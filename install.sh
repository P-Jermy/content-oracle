#!/usr/bin/env bash
# content-oracle / install.sh
# 安装 content-oracle 到 Hermes Agent
# Usage: bash install.sh [--link|--copy]

set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
HERMES_SKILLS_DIR="${HOME}/.hermes/skills"
TARGET_NAME="content-oracle"
MODE="link"  # default: symlink for live development

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --link) MODE="link" ;;
    --help|-h)
      echo "Usage: bash install.sh [--link|--copy]"
      echo "  --link  (default) symlink for live edits"
      echo "  --copy  copy files (frozen version)"
      exit 0
      ;;
  esac
done

# Create Hermes skills dir if needed
mkdir -p "$HERMES_SKILLS_DIR"

# Check existing install
TARGET="$HERMES_SKILLS_DIR/$TARGET_NAME"
if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  echo "⚠️  $TARGET already exists"
  read -p "   Overwrite? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
  rm -rf "$TARGET"
fi

if [[ "$MODE" == "link" ]]; then
  ln -s "$SCRIPT_DIR" "$TARGET"
  echo "✓ Symlinked: $SCRIPT_DIR → $TARGET"
else
  cp -R "$SCRIPT_DIR" "$TARGET"
  rm -rf "$TARGET/.git"
  echo "✓ Copied: $SCRIPT_DIR → $TARGET"
fi

echo ""
echo "✅ content-oracle installed!"
echo ""
echo "Now say in Hermes:"
echo "  初始化   → 创建内容项目"
echo "  抓热点   → 采集趋势"
echo "  推荐选题 → 选题推荐"
echo "  状态     → 看板"
echo ""
echo "Install location: $TARGET"
