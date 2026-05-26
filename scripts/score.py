#!/usr/bin/env python3
"""
Content Oracle - score
按 rubric 对草稿进行打分
"""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.state import find_project_root, load_state


RUBRIC_DIMENSIONS = [
    "选题价值 — 话题是否有时效性/争议性/共鸣感",
    "标题冲击 — 标题是否能激发点击欲",
    "结构逻辑 — 是什么→为什么→怎么用 层次清晰",
    "信息密度 — 有没有独家信息/深度洞察",
    "表达力 — 语言是否生动、有记忆点",
    "受众匹配 — 内容是否精准触达目标读者",
    "行动驱动 — 是否有明确的互动/转发/关注引导",
]


def read_rubric(project_dir: str) -> str:
    """读取 rubric_notes.md"""
    path = Path(project_dir) / "rubric_notes.md"
    if path.exists():
        with open(path) as f:
            return f.read()
    return None


def init_rubric(project_dir: str):
    """如果不存在则创建默认 rubric"""
    path = Path(project_dir) / "rubric_notes.md"
    if not path.exists():
        content = """# 评分记录（Rubric Notes）

## 评分维度
"""
        for i, dim in enumerate(RUBRIC_DIMENSIONS, 1):
            name = dim.split(" — ")[0]
            desc = dim.split(" — ")[1] if " — " in dim else ""
            content += f"\n### {i}. {name}\n{desc}\n"
        content += """
## 评分标准
- 1-3: 需要大幅改进
- 4-6: 合格水平
- 7-8: 良好
- 9-10: 优秀

## 观察笔记
<!-- 每次复盘后记录校准发现 -->
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return content
    return None


def score_draft(draft_path: str, rubric: str = None) -> dict:
    """读取草稿并返回元数据"""
    with open(draft_path) as f:
        content = f.read()

    return {
        "path": draft_path,
        "filename": os.path.basename(draft_path),
        "word_count": len(content),
        "content_preview": content[:500] if len(content) > 500 else content,
    }


def main():
    parser = argparse.ArgumentParser(description="打分这篇草稿")
    parser.add_argument("draft_path", nargs="?", help="草稿文件路径")
    parser.add_argument("--project-dir", help="内容项目目录（默认自动查找）")
    parser.add_argument("--show-rubric", action="store_true", help="显示当前 rubric")
    parser.add_argument("--init-rubric", action="store_true", help="初始化 rubric_notes.md")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir and (args.init_rubric or args.show_rubric):
        print("❌ 未找到 .content-state.json")
        sys.exit(1)

    if args.show_rubric:
        rubric = read_rubric(project_dir)
        if rubric:
            print(rubric)
        else:
            print("⚠️  rubric_notes.md 不存在")
        return

    if args.init_rubric:
        rubric = init_rubric(project_dir)
        if rubric:
            print("✅ rubric_notes.md 已创建")
        else:
            print("✅ rubric_notes.md 已存在")
        return

    if not args.draft_path:
        parser.print_help()
        sys.exit(1)

    draft_info = score_draft(args.draft_path)
    print(f"📄 草稿: {draft_info['filename']}")
    print(f"   字数: {draft_info['word_count']}")
    print()
    print("请根据 rubric 对以下维度打分（1-10）：")
    for dim in RUBRIC_DIMENSIONS:
        print(f"  - {dim}")


if __name__ == "__main__":
    main()
