#!/usr/bin/env python3
"""
Content Oracle - trends
多源热点趋势采集，写入 predictions/ 目录
"""

import os
import sys
import json
import urllib.request
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.state import find_project_root, load_state, save_state


def fetch_github_trending():
    """GitHub AI/LLM 热门仓库"""
    try:
        url = "https://api.github.com/search/repositories?q=topic:ai+topic:llm&sort=stars&order=desc&per_page=10"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        repos = []
        for r in data.get("items", [])[:10]:
            repos.append({
                "title": r["full_name"],
                "url": r["html_url"],
                "description": r.get("description", "")[:100],
                "stars": r["stargazers_count"],
                "source": "github-trending",
                "language": r.get("language"),
            })
        return repos
    except Exception as e:
        return [{"title": f"github 采集失败: {e}", "source": "github-trending", "error": True}]


def fetch_hacker_news():
    """Hacker News 热门（逐条超时保护，减少数量）"""
    try:
        ids = json.loads(urllib.request.urlopen(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8).read())[:8]
        items = []
        for i in ids:
            try:
                item = json.loads(urllib.request.urlopen(
                    f"https://hacker-news.firebaseio.com/v0/item/{i}.json", timeout=5).read())
                items.append({
                    "title": item.get("title", "")[:120],
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={i}"),
                    "points": item.get("score", 0),
                    "source": "hacker-news",
                })
            except Exception:
                continue  # 跳过单条超时/失败
        return items if items else [{"title": "HN 单条全部超时", "source": "hacker-news", "error": True}]
    except Exception as e:
        return [{"title": f"HN 采集失败: {e}", "source": "hacker-news", "error": True}]


def generate_trends_markdown(all_items: list) -> str:
    """生成 trends 报告 markdown"""
    lines = [
        f"# 热点趋势 {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"> Content Oracle 自动采集 | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    # Group by source
    sources = {}
    for item in all_items:
        src = item.get("source", "unknown")
        if src not in sources:
            sources[src] = []
        sources[src].append(item)

    for source, items in sources.items():
        label = {"github-trending": "GitHub AI Trending", "hacker-news": "Hacker News"}.get(source, source)
        lines.append(f"## {label}")
        lines.append("")
        for item in items:
            if item.get("error"):
                lines.append(f"- ❌ {item['title']}")
            else:
                title = item.get("title", "")
                url = item.get("url", "")
                stars = item.get("stars")
                points = item.get("points")
                desc = item.get("description", "")
                tag = f"⭐{stars}" if stars else (f"{points}pts" if points else "")
                if url:
                    lines.append(f"- [{title}]({url}) {tag}")
                    if desc:
                        lines.append(f"  — {desc}")
                else:
                    lines.append(f"- {title} {tag}")
            lines.append("")

    # 写作方向建议
    lines.append("## 写作方向建议")
    lines.append("")
    lines.append("基于当前趋势，建议聚焦：")
    lines.append("")
    lines.append("1. **AI 工具最新进展与实际应用** — 工具链变化快，实操指南永远稀缺")
    lines.append("2. **技术趋势解读** — 把学术/业界动态转译成可理解的语言")
    lines.append("3. **开发者经验分享** — 避坑指南、效率提升、工作流分享")
    lines.append("4. **行业分析** — AI 对具体领域的影响与机会")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="抓取热点趋势")
    parser.add_argument("--project-dir", help="内容项目目录（默认自动查找）")
    parser.add_argument("--output", help="输出文件路径（默认 predictions/trends_<date>.md）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    # 确定项目目录
    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json，请先运行初始化")
        sys.exit(1)

    print("🔍 采集热点趋势...")

    # 串行采集（WSL 网络环境避免并发 HTTP 卡死）
    sources = [
        ("github-trending", fetch_github_trending),
        ("hacker-news", fetch_hacker_news),
    ]

    all_items = []
    for name, fn in sources:
        try:
            items = fn()
            if not items or items[0].get("error"):
                print(f"  ⚠️ {name}: 采集异常")
            else:
                print(f"  ✓ {name}: {len(items)} 条")
            all_items.extend(items)
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    # 更新 state
    state = load_state(project_dir)
    now = datetime.now(timezone.utc).isoformat()
    state["last_trends_run_at"] = now
    state["last_trends_added_count"] = len([i for i in all_items if not i.get("error")])
    save_state(state, project_dir)

    # 输出
    report = generate_trends_markdown(all_items)

    if args.json:
        print(json.dumps(all_items, ensure_ascii=False, indent=2))
        return

    output_path = args.output
    if not output_path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        pred_dir = os.path.join(project_dir, "predictions")
        os.makedirs(pred_dir, exist_ok=True)
        output_path = os.path.join(pred_dir, f"trends_{date_str}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 趋势报告已保存: {output_path}")
    print(f"   来源: {len(all_items)} 条 / 错误: {sum(1 for i in all_items if i.get('error'))}")


if __name__ == "__main__":
    main()
