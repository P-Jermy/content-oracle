#!/usr/bin/env python3
"""
Content Oracle - publish / retro / status
发布登记、复盘、状态看板
"""

import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.state import find_project_root, load_state, save_state


def cmd_publish(args):
    """登记发布"""
    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json")
        sys.exit(1)

    prediction_path = os.path.abspath(args.prediction_path)
    if not os.path.exists(prediction_path):
        print(f"❌ 预测文件不存在: {prediction_path}")
        sys.exit(1)

    state = load_state(project_dir)
    now = datetime.now(timezone.utc).isoformat()
    state["last_published_at"] = now
    state["last_published_file"] = prediction_path

    # 添加到 shoots 队列等待复盘
    if "shoots" not in state:
        state["shoots"] = []
    state["shoots"].append({
        "file": prediction_path,
        "published_at": now,
    })
    state["pending_retros"].append(prediction_path)

    # 添加发布信息到预测文件
    with open(prediction_path, "a", encoding="utf-8") as f:
        f.write(f"\n## 发布记录\n\n")
        f.write(f"- **发布时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")
        f.write(f"- **平台**: {args.platform or '未记录'}\n")
        f.write(f"- **链接**: {args.url or '未记录'}\n\n")

    save_state(state, project_dir)
    print(f"✅ 已登记发布: {os.path.basename(prediction_path)}")
    print(f"   等待 {args.retro_days or 3} 天后复盘")


def cmd_retro(args):
    """复盘"""
    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json")
        sys.exit(1)

    prediction_path = os.path.abspath(args.prediction_path)
    if not os.path.exists(prediction_path):
        print(f"❌ 预测文件不存在: {prediction_path}")
        sys.exit(1)

    with open(prediction_path) as f:
        content = f.read()

    if "## 复盘" in content and "<!--" in content.split("## 复盘")[-1]:
        print("📝 复盘段已存在。请提供实际数据：")
    else:
        print("📝 预测文件已打开，请在 ## 复盘 段填入实际数据。")

    # 从 state 移除 pending
    state = load_state(project_dir)
    if prediction_path in state.get("pending_retros", []):
        state["pending_retros"].remove(prediction_path)
    save_state(state, project_dir)

    print(f"\n📄 {os.path.basename(prediction_path)}")
    print(f"   等待你提供实际表现数据")


def cmd_status(args):
    """状态看板"""
    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到 .content-state.json")
        print("   在当前目录运行 '初始化'")
        sys.exit(1)

    state = load_state(project_dir)

    print("📊 Content Oracle 状态")
    print("=" * 40)
    print(f"   项目: {project_dir}")
    print(f"   内容形态: {state.get('content_form', '未设置')}")
    print(f"   版本: v{state.get('skill_version', '?')}")

    # 待复盘
    pending = len(state.get("pending_retros", []))
    pred_count = len(list(Path(project_dir).glob("predictions/*.md")))

    print()
    print(f"   预测总数: {pred_count}")
    print(f"   待复盘: {pending}")
    print(f"   已发布: {len(state.get('shoots', []))}")

    # 上次趋势
    last_trends = state.get("last_trends_run_at", "")
    if last_trends:
        try:
            dt = datetime.fromisoformat(last_trends)
            print(f"   上次抓热点: {dt.strftime('%m-%d %H:%M')}")
        except:
            pass

    # 校准池
    cal_samples = state.get("calibration_samples", 0)
    print(f"   校准样本: {cal_samples}")

    print()
    if state.get("pending_retros"):
        print("⏳ 待复盘:")
        for p in state["pending_retros"]:
            print(f"   - {os.path.basename(p)}")
    else:
        print("✅ 没有待复盘项")


def main():
    parser = argparse.ArgumentParser(description="内容发布与复盘管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # publish
    p_pub = subparsers.add_parser("publish", help="登记发布")
    p_pub.add_argument("prediction_path", help="预测文件路径")
    p_pub.add_argument("--platform", help="发布平台")
    p_pub.add_argument("--url", help="发布链接")
    p_pub.add_argument("--retro-days", type=int, default=3, help="几天后复盘")
    p_pub.add_argument("--project-dir", help="项目目录")

    # retro
    p_retro = subparsers.add_parser("retro", help="复盘")
    p_retro.add_argument("prediction_path", help="预测文件路径")
    p_retro.add_argument("--project-dir", help="项目目录")

    # status
    p_stat = subparsers.add_parser("status", help="状态看板")
    p_stat.add_argument("--project-dir", help="项目目录")

    args = parser.parse_args()

    if args.command == "publish":
        cmd_publish(args)
    elif args.command == "retro":
        cmd_retro(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
