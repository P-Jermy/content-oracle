#!/usr/bin/env bash
# content-oracle / install.sh
# Install content-oracle to Hermes Agent
#
# Usage:
#   bash install.sh                     # install local dir (symlink)
#   bash install.sh --copy              # install local dir (copy)
#   bash install.sh --remote            # clone from GitHub then install
#   bash install.sh --remote --copy     # clone + copy
#
# For end users: the simplest way is:
#   git clone https://github.com/P-Jermy/content-oracle.git
#   cd content-oracle && bash install.sh

set -euo pipefail

REPO_URL="https://github.com/P-Jermy/content-oracle.git"
HERMES_SKILLS_DIR="${HOME}/.hermes/skills"
TARGET_NAME="content-oracle"
MODE="link"
REMOTE=false

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --link) MODE="link" ;;
    --remote) REMOTE=true ;;
    --help|-h)
      echo "Content Oracle 安装脚本"
      echo ""
      echo "用法:"
      echo "  bash install.sh                     # 本地安装（symlink）"
      echo "  bash install.sh --copy              # 本地安装（copy）"
      echo "  bash install.sh --remote            # 从 GitHub 克隆后安装"
      echo "  bash install.sh --remote --copy     # 克隆+copy"
      echo ""
      echo "新手最简安装:"
      echo "  git clone $REPO_URL"
      echo "  cd content-oracle && bash install.sh"
      exit 0
      ;;
  esac
done

# ── Remote mode: clone from GitHub ──
if [[ "$REMOTE" == true ]]; then
  CLONE_DIR="/tmp/content-oracle-install-$$"
  echo "📦 从 GitHub 克隆..."
  git clone --depth 1 "$REPO_URL" "$CLONE_DIR"
  cd "$CLONE_DIR"
  echo "✓ 克隆完成"
fi

# Detect the script's directory
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# ── Install to Hermes ──
mkdir -p "$HERMES_SKILLS_DIR"
TARGET="$HERMES_SKILLS_DIR/$TARGET_NAME"

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  echo "⚠️  $TARGET 已存在"
  read -p "   覆盖？(y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
  fi
  rm -rf "$TARGET"
fi

if [[ "$MODE" == "link" ]]; then
  ln -s "$SCRIPT_DIR" "$TARGET"
  echo "✓ Symlink: $SCRIPT_DIR → $TARGET"
else
  cp -R "$SCRIPT_DIR" "$TARGET"
  rm -rf "$TARGET/.git"
  echo "✓ Copied: $SCRIPT_DIR → $TARGET"
fi

# ── Cleanup ──
if [[ "$REMOTE" == true ]]; then
  rm -rf "/tmp/content-oracle-install-$$"
fi

echo ""
echo "✅ content-oracle 安装完成！"
echo ""
echo "现在在你的内容项目目录中对 Hermes 说："
echo ""
echo "  初始化    创建内容项目"
echo "  抓热点    采集今日趋势"
echo "  推荐选题  选题推荐"
echo "  写稿      开始写稿"
echo "  状态      查看看板"
echo ""
echo "安装路径: $TARGET"
echo "项目地址: $REPO_URL"
