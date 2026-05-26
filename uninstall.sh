#!/usr/bin/env bash
# content-oracle / uninstall.sh
# 从 Hermes Agent 卸载

set -euo pipefail

TARGET="${HOME}/.hermes/skills/content-oracle"

if [[ ! -e "$TARGET" && ! -L "$TARGET" ]]; then
  echo "⚠️  content-oracle 未安装（找不到 $TARGET）"
  exit 0
fi

read -p "删除 content-oracle? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

rm -rf "$TARGET"
echo "✅ content-oracle 已卸载"
echo "   你的内容项目数据（.content-state.json 等）不受影响"
