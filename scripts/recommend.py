#!/usr/bin/env python3
"""
Content Oracle - recommend
从选题池和趋势数据中推荐写作方向
"""

import os
import sys
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.state import find_project_root, load_state


TREND_WEIGHT = 0.4
CANDIDATE_WEIGHT = 0.6


def load_candidates(project_dir: str) -> list:
    """读取 candidates.md 中的候选选题"""
    path = Path(project_dir) / "candidates.md"
    if not path.exists():
        return []

    candidates = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("- ["):
                # parse: - [优先级] 标题 | 来源 | 理由
                parts = line[2:].split("|")
                priority = parts[0].strip("[] ") if len(parts) >= 1 else "中"
                title = parts[0].split("] ", 1)[-1] if "]" in parts[0] else parts[0]
                source = parts[1].strip() if len(parts) >= 2 else ""
                reason = parts[2].strip() if len(parts) >= 3 else ""
                candidates.append({
                    "title": title.strip(),
                    "priority": priority,
                    "source": source,
                    "reason": reason,
                    "type": "candidate",
                })
    return candidates


def load_latest_trends(project_dir: str) -> list:
    """读取最近一次趋势报告"""
    pred_dir = Path(project_dir) / "predictions"
    if not pred_dir.exists():
        return []

    trend_files = sorted(pred_dir.glob("trends_*.md"), reverse=True)
    if not trend_files:
        return []

    with open(trend_files[0]) as f:
        content = f.read()

    # 简单解析：取 GitHub/HN 的标题行作为候选
    items = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- [") and "](" in line:
            title = line.split("[", 1)[1].split("]", 1)[0]
            items.append({
                "title": title,
                "source": "trends",
                "priority": "高",
                "reason": "今日热点",
                "type": "trend",
            })
        elif line.startswith("- ") and not line.startswith("- [") and not line.startswith("- ❌"):
            # plain text items from trends
            title = line[2:]
            if title and len(title) < 200:
                items.append({
                    "title": title,
                    "source": "trends",
                    "priority": "中",
                    "reason": "趋势提及",
                    "type": "trend",
                })
    return items


def main():
    parser = argparse.ArgumentParser(description="推荐选题")
    parser.add_argument("--project-dir", help="内容项目目录（默认自动查找）")
    parser.add_argument("--count", type=int, default=5, help="推荐数量")
    parser.add_argument("--include-trends", action="store_true", default=True, help="包含趋势数据")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json，请先运行初始化")
        sys.exit(1)

    candidates = load_candidates(project_dir)
    trends = load_latest_trends(project_dir) if args.include_trends else []

    print(f"📋 选题池: {len(candidates)} 条")
    if trends:
        print(f"🔥 最新趋势: {len(trends)} 条")

    # 合并推荐
    all_items = []

    # 现有候选按优先级排序
    priority_map = {"高": 3, "中": 2, "低": 1}
    for c in candidates:
        c["score"] = priority_map.get(c["priority"], 2) * CANDIDATE_WEIGHT * 10
        all_items.append(c)

    # 趋势选题
    for t in trends:
        # 去重
        title_lower = t["title"].lower()
        if any(title_lower in c["title"].lower() or c["title"].lower() in title_lower for c in all_items):
            continue
        t["score"] = priority_map.get(t["priority"], 2) * TREND_WEIGHT * 10
        all_items.append(t)

    # 排序
    all_items.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n🎯 推荐选题（Top {min(args.count, len(all_items))}）：")
    print()
    for i, item in enumerate(all_items[:args.count], 1):
        tag = "🔥" if item.get("type") == "trend" else "📋"
        src = f" [{item.get('source', '')}]" if item.get("source") else ""
        score_bar = "█" * int(item["score"] / 3) + "░" * (10 - int(item["score"] / 3))
        print(f"  {i}. {tag} {item['title']}{src}")
        print(f"     评分 {score_bar} {item['score']:.0f}")
        if item.get("reason"):
            print(f"     理由: {item['reason']}")
        print()

    if not all_items:
        print("  暂无选题。说 '抓热点' 采集趋势，或编辑 candidates.md 添加选题。")
        print()
        print("candidates.md 格式：")
        print("  - [高] 你的选题 | 来源 | 为什么值得写")


if __name__ == "__main__":
    main()
