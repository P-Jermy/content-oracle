#!/usr/bin/env python3
"""
content-shoot: 写稿助手
接收候选选题 → 问用户细节 → 输出完整草稿到 articles/<id>.md
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state, save_state

def list_candidates(project_dir):
    path = os.path.join(project_dir, "candidates.md")
    if not os.path.exists(path): return []
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    candidates = []
    for i, line in enumerate(lines):
        if line.startswith('- ['):
            cand = {"line": i+1, "raw": line.strip()[2:], "title": line.strip(), "priority": "?"}
            m = re.match(r'- \[(.)\]\s*(.+?)(?:\s*\|\s*(.+))?', line.strip())
            if m:
                cand["priority"] = m.group(1)
                cand["title"] = m.group(2).strip()
                cand["source"] = m.group(3).strip() if m.group(3) else ""
            candidates.append(cand)
    return candidates

def list_scripts(project_dir):
    scripts_dir = os.path.join(project_dir, "scripts")
    if not os.path.exists(scripts_dir): return []
    files = sorted(os.listdir(scripts_dir))
    return [f for f in files if f.endswith('.md')]

def generate_draft_id(title):
    safe = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '-', title.lower())[:40]
    safe = re.sub(r'-+', '-', safe).strip('-')
    date = datetime.now().strftime('%Y%m%d')
    return f'{date}_{safe}'

def main():
    parser = argparse.ArgumentParser(description="写稿助手")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--id", help="指定稿件ID（来自candidates或scripts）")
    parser.add_argument("--title", help="直接指定标题")
    parser.add_argument("--from-candidates", action="store_true", help="从candidates.md选择")
    parser.add_argument("--from-scripts", action="store_true", help="从scripts/选择")
    parser.add_argument("--output", help="输出路径（默认 articles/<id>.md）")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目，请先运行初始化")
        sys.exit(1)

    state = load_state(project_dir)
    title = args.title
    draft_id = None
    source_info = ""

    if args.from_candidates:
        cands = list_candidates(project_dir)
        if not cands:
            print("❌ candidates.md 为空，无法选择")
            sys.exit(1)
        print(f"可用候选（{len(cands)} 个）：")
        for i, c in enumerate(cands, 1):
            print(f"  {i}. [{c['priority']}] {c['title'][:60]}")
        print()
        # We'll output and let the user tell us which one
        print("请回复编号选择候选")
        sys.exit(0)
    
    if args.from_scripts:
        scripts = list_scripts(project_dir)
        if not scripts:
            print("❌ scripts/ 为空")
            sys.exit(1)
        print(f"可用草稿（{len(scripts)} 篇）：")
        for i, s in enumerate(scripts, 1):
            print(f"  {i}. {s}")
        print("请回复编号选择")
        sys.exit(0)

    if args.id:
        # Try to find it
        cands = list_candidates(project_dir)
        for c in cands:
            if args.id in c["title"] or args.id in c["raw"]:
                title = c["title"]
                source_info = f"来源: candidates.md 第{c['line']}行"
                break
        if not title:
            # Check scripts
            scripts = list_scripts(project_dir)
            for s in scripts:
                if args.id in s:
                    title = s.replace('.md','')
                    source_info = f"来源: scripts/{s}"
                    break
    
    if not title:
        print("❌ 未指定标题，请使用 --title 或 --id")
        sys.exit(1)

    draft_id = args.id or generate_draft_id(title)
    output_path = args.output or os.path.join(project_dir, "articles", f"{draft_id}.md")
    
    # If output exists, warn
    if os.path.exists(output_path):
        print(f"⚠️  稿件已存在: {output_path}")
        resp = input("覆盖? (y/N): ")
        if resp.lower() != 'y':
            print("已取消")
            sys.exit(0)
    
    # Output a writing prompt template
    print(f"""
📝 写稿准备就绪
================
标题: {title}
{source_info}
输出: {output_path}

请提供写稿信息：
- 核心观点（一句话）
- 目标读者
- 参考素材/链接
- 配图需求（几张）
- 特殊要求（语气/长度/结构）
================
写稿时我会自动：
1. 用 content-score 打分确认选题价值
2. 参考 rubric_notes.md 评分标准
3. 标注配图占位 [ILLUSTRATION: xxx]
4. 生成后记录到 state.shoots
""")
    
    # Record in state
    if "shoots" not in state: state["shoots"] = []
    state["shoots"].append({
        "id": draft_id,
        "title": title,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "writing",
        "source": source_info,
    })
    save_state(state, project_dir)

if __name__ == "__main__":
    main()
