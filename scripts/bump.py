#!/usr/bin/env python3
"""
content-bump: Rubric 升级
提案并执行 rubric 升级 —— 调整维度权重 / 桶边界
"""
import os, sys, json, re, argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state, save_state

def main():
    parser = argparse.ArgumentParser(description="Rubric升级")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--propose", help="升级提案描述")
    parser.add_argument("--bucket-only", action="store_true", help="只校准桶边界")
    parser.add_argument("--dry-run", action="store_true", help="仅预览不执行")
    parser.add_argument("--status", action="store_true", help="检查校准状态")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    state = load_state(project_dir)
    rubric_path = os.path.join(project_dir, "rubric_notes.md")
    benchmark_path = os.path.join(project_dir, "benchmark.md")

    if args.status:
        samples = state.get('calibration_samples', 0)
        rubric_exists = os.path.exists(rubric_path)
        rubric_version = state.get('rubric_version', 'v0')
        print(f"""
📐 Rubric 校准状态
====================
Rubric版本: {rubric_version}
校准样本: {samples}
Rubric文件: {"✅" if rubric_exists else "❌"} {'存在' if rubric_exists else '不存在'}
Benchmark: {"✅" if os.path.exists(benchmark_path) else "❌"} {'存在' if os.path.exists(benchmark_path) else '不存在'}
""")
        if samples >= 5:
            print("建议: 校准样本 ≥5，可以 bump")
        else:
            print(f"建议: 还需 {5 - samples} 个样本才够 bump")
        return

    if args.propose:
        print(f"""
📝 Rubric 升级提案
===================
提案: {args.propose}
模式: {"仅校准桶" if args.bucket_only else "完整升级"}
试运行: {"是" if args.dry_run else "否"}
""")
        if args.dry_run:
            print("（试运行模式，不实际修改）")
            print("当前 rubric 版本:", state.get('rubric_version', 'v0'))
            print("提案将通过 content-score-blind 子代理验证后执行")
        else:
            # Execute bump
            old_ver = state.get('rubric_version', 'v0')
            ver_num = int(re.search(r'v(\d+)', old_ver).group(1)) if re.search(r'v(\d+)', old_ver) else 0
            new_ver = f'v{ver_num + 1}'
            
            state['rubric_version'] = new_ver
            state['consecutive_directional_errors'] = []
            save_state(state, project_dir)
            print(f"✅ Rubric 已升级: {old_ver} → {new_ver}")
            
            # Add upgrade record
            if os.path.exists(rubric_path):
                with open(rubric_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n## 升级记录 ({datetime.now().strftime('%Y-%m-%d')})\n\n")
                    f.write(f"版本: {old_ver} → {new_ver}\n")
                    f.write(f"提案: {args.propose}\n\n")
        return

    print("请使用 --propose "升级描述" 来提案")
    print("可选: --bucket-only (仅校准桶), --dry-run (试运行)")

if __name__ == "__main__":
    main()
