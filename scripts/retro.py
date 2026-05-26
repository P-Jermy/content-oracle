#!/usr/bin/env python3
"""
content-retro: T+N 复盘
对比预测 vs 实际数据，写入新观察到 rubric_notes.md
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state, save_state

def list_predictions(project_dir):
    pred_dir = os.path.join(project_dir, "predictions")
    if not os.path.exists(pred_dir): return []
    return sorted([f for f in os.listdir(pred_dir) if f.endswith('.md')])

def main():
    parser = argparse.ArgumentParser(description="复盘")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--id", help="预测文件名或ID")
    parser.add_argument("--list", action="store_true", help="列出可复盘的预测")
    parser.add_argument("--days", type=int, default=3, help="T+N 天数窗口（默认3）")
    parser.add_argument("--add-observation", help="手动添加观察到 rubric_notes.md")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    state = load_state(project_dir)
    predictions = list_predictions(project_dir)

    if args.list:
        pred_dir = os.path.join(project_dir, "predictions")
        print(f"可用预测（{len(predictions)} 个）：")
        for p in predictions:
            fpath = os.path.join(pred_dir, p)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            print(f"  {p}  ({mtime.strftime('%m-%d %H:%M')})")
        return

    if args.add_observation:
        rubric_path = os.path.join(project_dir, "rubric_notes.md")
        if not os.path.exists(rubric_path):
            with open(rubric_path, 'w', encoding='utf-8') as f:
                f.write(f"# Rubric Notes\n\n初始化于 {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        with open(rubric_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## 观察 ({datetime.now().strftime('%Y-%m-%d')})\n\n")
            f.write(f"{args.add_observation}\n\n")
        print("✅ 观察已添加到 rubric_notes.md")
        return

    if not args.id:
        print("❌ 请指定预测文件 (--id)，或 --list 查看")
        sys.exit(1)

    # Find matching prediction file
    pred_file = None
    pred_dir = os.path.join(project_dir, "predictions")
    for p in predictions:
        if args.id in p:
            pred_file = p
            break
    if not pred_file:
        print(f"❌ 未找到匹配: {args.id}")
        sys.exit(1)

    pred_path = os.path.join(pred_dir, pred_file)
    with open(pred_path, encoding='utf-8') as f:
        pred_content = f.read()

    print(f"""
📋 复盘: {pred_file}
======================

原始预测内容（前500字）:
{pred_content[:500]}

请回答以下问题来完成复盘：
1. 实际数据 vs 预测差距多大？
2. 哪些假设被验证了？哪些错了？
3. 学到什么可以更新到 rubric？
======================

复盘后将自动追加观察到 rubric_notes.md
""")
    
    # Record in state
    if "pending_retros" not in state: state["pending_retros"] = []
    state["pending_retros"] = [r for r in state["pending_retros"] if r != pred_file]
    save_state(state, project_dir)

if __name__ == "__main__":
    main()
