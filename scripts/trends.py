#!/usr/bin/env python3
"""
Content Oracle - trends
多源热点趋势采集，匹配原版 cheat-on-content 架构

Phases:
  0. 读 .content-state.json 拿启用 adapters
  1. 对每个 adapter 调 fetch
  2. normalize 到统一 schema
  3. 去重（SHA256 hash vs candidates/predictions/trends-history）
  4. 粗打分（内联 rubric）
  5. 排序输出 → 用户选择加入 candidates.md
  6. 写入 trends-history.jsonl 缓存
"""

import os
import sys
import json
import hashlib
import urllib.request
import xml.etree.ElementTree as ET
import argparse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state, save_state


# ──────────── Constants ────────────

LOOKBACK_HOURS = 24
MAX_PER_SOURCE = 15
MIN_COMPOSITE_TO_SUGGEST = 5.0
DEDUPE_REJECT_WINDOW_DAYS = 180  # 用户拒绝后 N 天内不再推


# ──────────── Phase 1-2: Adapters ────────────

def fetch_hackernews():
    """HN Algolia API（无需 key）"""
    try:
        resp = urllib.request.urlopen(
            "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=20", timeout=10)
        data = json.loads(resp.read())
        items = []
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            items.append({
                "title": title[:120],
                "url": url,
                "source": "trend:hackernews",
                "snapshot_text": (hit.get("title", "") + " — " + (hit.get("url", "")))[:500],
                "points": hit.get("points", 0),
            })
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        return [{"title": f"hackernews 采集失败: {e}", "source": "trend:hackernews", "error": True}]


def fetch_github_trending():
    """GitHub AI/LLM 热门仓库（Search API）"""
    try:
        req = urllib.request.Request(
            "https://api.github.com/search/repositories?q=topic:ai+topic:llm&sort=stars&order=desc&per_page=10",
            headers={"Accept": "application/vnd.github.v3+json"})
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        items = []
        for r in data.get("items", [])[:10]:
            items.append({
                "title": r["full_name"],
                "url": r["html_url"],
                "source": "trend:github-ai",
                "snapshot_text": f"{r['full_name']}: {r.get('description', '')[:200]}",
                "stars": r["stargazers_count"],
            })
        return items
    except Exception as e:
        return [{"title": f"github 采集失败: {e}", "source": "trend:github-ai", "error": True}]


def fetch_36kr():
    """36氪 RSS"""
    try:
        resp = urllib.request.urlopen("https://36kr.com/feed", timeout=15)
        root = ET.fromstring(resp.read())
        items = []
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item"):
                title = item.find("title")
                link = item.find("link")
                desc = item.find("description")
                if title is not None and link is not None and title.text:
                    snapshot = title.text.strip()
                    if desc is not None and desc.text:
                        snapshot += " " + desc.text.strip()[:200]
                    items.append({
                        "title": title.text.strip(),
                        "url": (link.text or "").strip(),
                        "source": "trend:36kr",
                        "snapshot_text": snapshot[:500],
                    })
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        return [{"title": f"36kr 采集失败: {e}", "source": "trend:36kr", "error": True}]


def fetch_reddit():
    """Reddit 热门（r/all/rising JSON）"""
    try:
        req = urllib.request.Request(
            "https://www.reddit.com/r/all/rising.json?limit=15",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HermesAgent/1.0"}
        )
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        items = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            title = d.get("title", "")
            if not title:
                continue
            items.append({
                "title": title[:120],
                "url": f"https://www.reddit.com{d.get('permalink', '')}",
                "source": "trend:reddit",
                "snapshot_text": title[:500],
                "ups": d.get("ups", 0),
                "subreddit": d.get("subreddit", ""),
            })
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        return [{"title": f"reddit 采集失败: {e}", "source": "trend:reddit", "error": True}]


def fetch_bilibili():
    """B站热门（公开 API）"""
    try:
        resp = urllib.request.urlopen(
            "https://api.bilibili.com/x/web-interface/popular?pn=1&ps=10", timeout=10)
        data = json.loads(resp.read())
        items = []
        for v in data.get("data", {}).get("list", []):
            items.append({
                "title": v.get("title", "").strip()[:80],
                "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
                "source": "trend:bilibili",
                "snapshot_text": v.get("title", "")[:200],
                "play": v.get("stat", {}).get("view", 0),
            })
        return items
    except Exception as e:
        return [{"title": f"B站 采集失败: {e}", "source": "trend:bilibili", "error": True}]


# ──────────── Phase 3: Dedup ────────────

def gen_item_id(source: str, title: str, url: str) -> str:
    """生成 SHA256[:12] 唯一 ID"""
    raw = f"{source}||{title.strip().lower()}||{url.split('?')[0].rstrip('/')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def load_trends_history(project_dir: str) -> dict:
    """加载 trends-history.jsonl → dict {id: entry}"""
    path = os.path.join(project_dir, ".content-cache", "trends-history.jsonl")
    history = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        history[entry["id"]] = entry
                    except:
                        pass
    return history


def save_trends_history(project_dir: str, entries: list):
    """追加到 trends-history.jsonl"""
    path = os.path.join(project_dir, ".content-cache", "trends-history.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_existing_ids(project_dir: str) -> set:
    """从 candidates.md 和 predictions/ 收集已有 ID"""
    existing = set()

    # Check candidates.md
    cand_path = os.path.join(project_dir, "candidates.md")
    if os.path.exists(cand_path):
        with open(cand_path) as f:
            content = f.read()
        for m in __import__("re").finditer(r'id:(\w{12})', content):
            existing.add(m.group(1))

    # Check predictions/
    pred_dir = os.path.join(project_dir, "predictions")
    if os.path.exists(pred_dir):
        for fn in os.listdir(pred_dir):
            if fn.endswith(".md"):
                with open(os.path.join(pred_dir, fn)) as f:
                    content = f.read()
                for m in __import__("re").finditer(r'id:(\w{12})', content):
                    existing.add(m.group(1))

    return existing


def deduplicate(all_items: list, project_dir: str, history: dict) -> (list, list):
    """
    去重：返回 (new_items, skipped_count)
    检查三重：candidates.md / predictions/ / trends-history.jsonl
    """
    existing_ids = load_existing_ids(project_dir)
    now = datetime.now(timezone.utc)

    new_items = []
    skipped = 0
    for item in all_items:
        if item.get("error"):
            continue
        item_id = gen_item_id(item["source"], item["title"], item.get("url", ""))
        item["id"] = item_id

        # Check candidates/predictions
        if item_id in existing_ids:
            skipped += 1
            continue

        # Check history: already fetched and not rejected
        if item_id in history:
            entry = history[item_id]
            # If rejected within window, skip
            if entry.get("rejected_at"):
                try:
                    rejected_at = datetime.fromisoformat(entry["rejected_at"].replace("Z", "+00:00"))
                    if (now - rejected_at).days < DEDUPE_REJECT_WINDOW_DAYS:
                        skipped += 1
                        continue
                except:
                    pass
            else:
                # Already fetched and not rejected, skip
                skipped += 1
                continue

        new_items.append(item)

    return new_items, skipped


# ──────────── Phase 4: Rough Scoring ────────────

def rough_score(item: dict) -> dict:
    """
    粗打分：7 维 rubric，内联打分
    基于标题 + snapshot_text 给出粗略 composite
    """
    text = (item.get("title", "") + " " + item.get("snapshot_text", "")).lower()

    # Simple heuristic scoring (will improve as rubric evolves)
    score_map = {
        "选题价值": 0, "标题冲击": 0, "结构逻辑": 0,
        "信息密度": 0, "表达力": 0, "受众匹配": 0, "行动驱动": 0,
    }

    # Keyword-based heuristic
    ai_keywords = ["ai", "llm", "agent", "gpt", "claude", "deepseek", "智能", "模型", "大模型"]
    tech_keywords = ["github", "代码", "编程", "开发", "技术", "开源", "python", "js"]
    hot_keywords = ["重磅", "新", "发布", "突破", "创新", "趋势"]

    ai_count = sum(1 for k in ai_keywords if k in text)
    tech_count = sum(1 for k in tech_keywords if k in text)
    hot_count = sum(1 for k in hot_keywords if k in text)

    score_map["选题价值"] = min(8, 5 + ai_count + tech_count)
    score_map["标题冲击"] = min(8, 4 + hot_count)
    score_map["结构逻辑"] = 6  # default
    score_map["信息密度"] = min(8, 5 + ai_count)
    score_map["表达力"] = 6
    score_map["受众匹配"] = min(9, 6 + ai_count)
    score_map["行动驱动"] = 5

    composite = round(sum(score_map.values()) / len(score_map), 1)

    # Brief rationale
    if ai_count >= 3:
        rationale = "AI 相关性强，选题价值高"
    elif tech_count >= 2:
        rationale = "技术话题，开发者关注"
    elif hot_count >= 2:
        rationale = "有热度，时效性好"
    else:
        rationale = "普通选题"

    return {
        "dimension_scores": score_map,
        "composite": composite,
        "rationale": rationale,
    }


# ──────────── Phase 5-6: Output ────────────

def generate_report(all_items: list, source_results: dict, new_count: int, skipped: int) -> str:
    """生成输出报告"""
    now = datetime.now(timezone.utc)
    lines = [
        f"# 热点趋势 {now.strftime('%Y-%m-%d')}",
        f"> Content Oracle 自动采集 | {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## 采集统计",
        "",
    ]

    for name, (ok, count) in source_results.items():
        icon = "✓" if ok else ("⚠️" if count == 0 else "✓")
        label = {"hackernews": "Hacker News", "github": "GitHub AI Trending", "36kr": "36氪",
                 "reddit": "Reddit 热门", "bilibili": "B站热门"}.get(name, name)
        if not ok:
            lines.append(f"- {icon} {label}: 采集失败")
        else:
            lines.append(f"- {icon} {label}: {count} 条")

    lines.extend([
        "",
        f"**去重**: {skipped} 条已存在 / **新候选**: {new_count} 条",
        "",
    ])

    if not all_items:
        lines.append("本次没有新的候选选题。")
        return "\n".join(lines)

    lines.append("## 新候选选题（按评分排序）")
    lines.append("")
    lines.append("| # | 评分 | 标题 | 来源 | 理由 |")
    lines.append("|---|---|---|---|---|")

    for i, item in enumerate(all_items, 1):
        score = item.get("_score", {})
        composite = score.get("composite", 0)
        rationale = score.get("rationale", "")
        src_short = item["source"].replace("trend:", "")
        title = item["title"][:60]
        lines.append(f"| {i} | **{composite}** | {title} | {src_short} | {rationale} |")

    return "\n".join(lines)


def update_content_state(project_dir: str, state: dict, new_count: int):
    """更新 .content-state.json"""
    now = datetime.now(timezone.utc).isoformat()
    state["last_trends_run_at"] = now
    state["last_trends_added_count"] = new_count
    save_state(state, project_dir)


# ──────────── Main ────────────

def main():
    parser = argparse.ArgumentParser(description="抓取热点趋势")
    parser.add_argument("--project-dir", help="内容项目目录（默认自动查找）")
    parser.add_argument("--sources", help="指定源，逗号分隔（默认全部）")
    parser.add_argument("--output", help="输出报告路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出新候选")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json，请先运行初始化")
        sys.exit(1)

    state = load_state(project_dir)

    # Phase 0: Determine enabled adapters
    enabled = state.get("enabled_trend_sources", ["hackernews", "github-ai", "36kr"])
    if args.sources:
        enabled = [s.strip() for s in args.sources.split(",")]

    adapter_map = {
        "hackernews": fetch_hackernews,
        "github-ai": fetch_github_trending,
        "36kr": fetch_36kr,
        "reddit": fetch_reddit,
        "bilibili": fetch_bilibili,
    }

    print("🔍 采集热点趋势...")
    print(f"   启用源: {', '.join(enabled)}")
    print()

    # Phase 1-2: Fetch + normalize
    all_raw = []
    source_results = {}
    for name in enabled:
        fn = adapter_map.get(name)
        if not fn:
            print(f"  ⚠️ {name}: 未知 adapter")
            source_results[name] = (False, 0)
            continue
        try:
            items = fn()
            if not items or items[0].get("error"):
                source_results[name] = (False, 0)
                print(f"  ⚠️ {name}: 采集失败")
                if items and items[0].get("error"):
                    print(f"     原因: {items[0]['title']}")
            else:
                source_results[name] = (True, len(items))
                print(f"  ✓ {name}: {len(items)} 条")
                all_raw.extend(items)
        except Exception as e:
            source_results[name] = (False, 0)
            print(f"  ✗ {name}: {e}")

    # Phase 3: Deduplicate
    history = load_trends_history(project_dir)
    new_items, skipped = deduplicate(all_raw, project_dir, history)
    print(f"\n  去重: 原始 {len(all_raw)} 条 → 新 {len(new_items)} 条 (跳过 {skipped} 条已有)")

    # Phase 4: Rough scoring (filter low quality)
    for item in new_items:
        score = rough_score(item)
        item["_score"] = score

    new_items = [i for i in new_items if i["_score"]["composite"] >= MIN_COMPOSITE_TO_SUGGEST]
    new_items.sort(key=lambda x: x["_score"]["composite"], reverse=True)

    # Save to trends-history.jsonl (all fetched items, even rejected)
    history_entries = []
    for item in all_raw:
        if not item.get("error") and item.get("id"):
            history_entries.append({
                "id": item["id"],
                "title": item["title"][:80],
                "source": item["source"],
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "rejected_at": None,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
    if history_entries:
        save_trends_history(project_dir, history_entries)
        print(f"  缓存已更新: {len(history_entries)} 条写入 trends-history.jsonl")

    # Update state
    update_content_state(project_dir, state, len(new_items))

    # Output
    report = generate_report(new_items, source_results, len(new_items), skipped)

    if args.json:
        output_data = []
        for item in new_items:
            output_data.append({
                "id": item["id"],
                "title": item["title"],
                "url": item.get("url", ""),
                "source": item["source"],
                "composite": item["_score"]["composite"],
                "rationale": item["_score"]["rationale"],
            })
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
        return

    output_path = args.output
    if not output_path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        pred_dir = os.path.join(project_dir, "predictions")
        os.makedirs(pred_dir, exist_ok=True)
        output_path = os.path.join(pred_dir, f"trends_{date_str}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 报告已保存: {output_path}")

    # Show top candidates
    if new_items:
        print(f"\n🎯 Top 5 候选（composite ≥ {MIN_COMPOSITE_TO_SUGGEST}）:")
        for i, item in enumerate(new_items[:5], 1):
            s = item["_score"]
            print(f"  {i}. [{s['composite']}] {item['title'][:50]}")
            print(f"     {s['rationale']}  |  {item['source']}")

        print(f"\n还有 {len(new_items)-5} 个候选（共 {len(new_items)} 个）")
        print("想加哪些到 candidates.md？回复编号（如 1,3,5）或 'all' 或 'none'")
    else:
        print("\n本次没有达到评分门槛的新候选。")


if __name__ == "__main__":
    main()
