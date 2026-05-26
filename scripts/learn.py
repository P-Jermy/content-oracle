#!/usr/bin/env python3
"""
content-learn: 对标学习
分析行业/竞品样本，提取模式和信号
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state

def main():
    parser = argparse.ArgumentParser(description="对标学习")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--source", help="样本来源（账号名/URL）")
    parser.add_argument("--from-samples", action="store_true", help="从 samples/ 目录分析")
    parser.add_argument("--list", action="store_true", help="列出 samples/ 内容")
    parser.add_argument("--script", help="分析单个脚本文件")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    samples_dir = os.path.join(project_dir, "samples")

    if args.list:
        if not os.path.exists(samples_dir):
            print("samples/ 目录不存在")
            return
        for root, dirs, files in os.walk(samples_dir):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), samples_dir)
                print(f"  {rel}")
        return

    if args.from_samples:
        if not os.path.exists(samples_dir):
            print("❌ samples/ 为空，请先放入样本")
            return
        print("""
📊 对标分析
============
分析的样本:
""")
        for root, dirs, files in os.walk(samples_dir):
            for f in files:
                if f.endswith('.md'):
                    print(f"  {os.path.relpath(os.path.join(root, f), samples_dir)}")
        print()
        print("分析完成后将生成:")
        print("  • script_patterns.md - 写作模式")
        print("  • benchmark.md - 对标基准")
        print("  • rubric_notes.md - 更新评分信号")
        return

    if args.script:
        if not os.path.exists(args.script):
            print(f"❌ 文件不存在: {args.script}")
            return
        print(f"📄 分析脚本: {args.script}")
        print("请提供对这个样本的分析要点：")
        print("  1. 值得学习的模式")
        print("  2. 避免的问题")
        print("  3. 可提取到 rubric 的信号")
        return

    print("用法: --from-samples (分析samples/) | --script <路径> (分析单个文件) | --list (查看样本)")

if __name__ == "__main__":
    main()
