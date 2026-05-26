#!/usr/bin/env python3
"""
content-migrate: Schema 版本迁移
将 .content-state.json 从旧 schema 迁移到最新
"""
import os, sys, json, re, argparse, shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.state import find_project_root, load_state, save_state, STATE_SCHEMA_VERSION

MIGRATIONS = {
    # version: (from_version, handler_func)
    # (none yet, but framework ready)
}

def main():
    parser = argparse.ArgumentParser(description="Schema迁移")
    parser.add_argument("--project-dir", help="项目目录")
    parser.add_argument("--dry-run", action="store_true", help="试运行")
    parser.add_argument("--force", action="store_true", help="强制迁移")
    parser.add_argument("--status", action="store_true", help="检查schema版本")
    parser.add_argument("--to", default=STATE_SCHEMA_VERSION, help="目标版本")
    args = parser.parse_args()

    project_dir = args.project_dir or find_project_root()
    if not project_dir:
        print("❌ 未找到项目")
        sys.exit(1)

    state = load_state(project_dir)
    current_ver = state.get('schema_version', '0.0.0')

    if args.status:
        print(f"""
📋 Schema 版本
===============
当前: {current_ver}
最新: {STATE_SCHEMA_VERSION}
状态: {"✅ 最新" if current_ver == STATE_SCHEMA_VERSION else "⚠️ 需要迁移"}
""")
        return

    if current_ver == STATE_SCHEMA_VERSION and not args.force:
        print(f"✅ Schema 已是最新 ({current_ver})")
        return

    print(f"迁移: {current_ver} → {args.to}")
    if args.dry_run:
        print("（试运行模式，不实际修改）")
        return

    # Backup
    backup_path = os.path.join(project_dir, ".content-state.json.bak")
    shutil.copy2(os.path.join(project_dir, ".content-state.json"), backup_path)
    print(f"✅ 已备份: .content-state.json.bak")

    # Update version
    state['schema_version'] = args.to
    state['migrated_at'] = datetime.utcnow().isoformat() + "Z"
    save_state(state, project_dir)
    print(f"✅ 迁移完成: {current_ver} → {args.to}")

if __name__ == "__main__":
    main()
