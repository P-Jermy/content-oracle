#!/usr/bin/env python3
"""
Content Oracle - init
初始化一个内容项目：创建目录结构、.content-state.json、rubric_notes.md
"""

import os
import sys
import argparse

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.state import init_project


def main():
    parser = argparse.ArgumentParser(description="初始化内容项目")
    parser.add_argument("project_dir", nargs="?", default=".", help="项目目录")
    parser.add_argument("--form", default="long-essay", choices=["long-essay", "video", "podcast", "thread", "short-video"],
                        help="内容形态")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)

    # 检查是否已初始化
    if os.path.exists(os.path.join(project_dir, ".content-state.json")):
        print(f"⚠️  {project_dir} 已初始化。如需重新初始化请先删除 .content-state.json")
        sys.exit(1)

    state = init_project(project_dir, content_form=args.form)
    print(f"✅ Content Oracle 已初始化: {project_dir}")
    print(f"   内容形态: {args.form}")
    print(f"   predictions/: predictions/ 目录")
    print(f"   scripts/:    草稿目录")
    print(f"   candidates.md: 选题池（编辑后说'推荐选题'）")
    print()
    print("下一步：")
    print("  说 '抓热点' → 采集趋势补充选题池")
    print("  说 '推荐选题' → 选题推荐")
    print("  说 '状态' → 查看看板")


if __name__ == "__main__":
    main()
