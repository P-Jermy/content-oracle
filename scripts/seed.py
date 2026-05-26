#!/usr/bin/env python3
"""
content-seed: 种子选题
根据用户兴趣/趋势生成选题，添加到 candidates.md
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state

def main():
    parser = argparse.ArgumentParser(description="种子选题")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--batch", type=int, help="批量生成N个选题")
    parser.add_argument("--from-trends", action="store_true", help="从最近趋势生成")
    parser.add_argument("--interest", help="用户兴趣方向（如 AI/Agent/生产力）")
    parser.add_argument("--add", help="直接添加选题到 candidates.md")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    state = load_state(project_dir)

    # Direct add
    if args.add:
        cand_path = os.path.join(project_dir, "candidates.md")
        if not os.path.exists(cand_path):
            with open(cand_path, 'w', encoding='utf-8') as f:
                f.write("# 选题池\n\n")
        with open(cand_path, 'a', encoding='utf-8') as f:
            f.write(f"- [ ] {args.add} | 手动添加 | {datetime.now().strftime('%Y-%m-%d')}\n")
        print(f"✅ 已添加: {args.add}")
        return

    # Load recent trends for inspiration
    recent_trends = []
    cache_path = os.path.join(project_dir, ".content-cache", "trends-history.jsonl")
    if args.from_trends and os.path.exists(cache_path):
        with open(cache_path, encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    recent_trends.append(item)
                except: pass
        recent_trends = recent_trends[-20:]

    if args.json:
        info = {
            "batch": args.batch or 1,
            "interest": args.interest or state.get("content_form", "long-essay"),
            "recent_trends_count": len(recent_trends),
            "sample_trends": [t.get("title","")[:50] for t in recent_trends[-3:]],
        }
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    # Print context for user to choose
    print(f"""
🌱 种子选题
===========
方向: {args.interest or state.get('content_form', 'long-essay')}
批量: {args.batch or 1}
""")
    if recent_trends:
        print("近期热点（供参考）:")
        for t in recent_trends[-5:]:
            print(f"  • {t.get('title','')[:60]}")
    print()
    print("请告诉我你的选题意向，我会: ")
    print("  1. 聊天引导找到切入点")
    print("  2. 生成选题添加到 candidates.md")
    print("  3. 如果指定 --batch N 则批量生成 N 个")

if __name__ == "__main__":
    main()
