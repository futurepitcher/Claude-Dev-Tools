#!/usr/bin/env bash
# Prosthetic Cover Design System — Installer
#
# Usage:
#   ./install.sh --global    Install to ~/.claude/ (all projects)
#   ./install.sh --project   Install to ./.claude/ (current project only)
#
# Installs:
#   - Claude Code skill (/prosthetic-cover)
#   - Python engine dependencies

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

MODE="${1:---global}"

case "$MODE" in
    --global|-g)
        TARGET_DIR="$HOME/.claude"
        info "Installing globally to $TARGET_DIR/"
        ;;
    --project|-p)
        PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
        TARGET_DIR="$PROJECT_ROOT/.claude"
        info "Installing to project at $TARGET_DIR/"
        ;;
    *)
        err "Usage: ./install.sh [--global|--project]"
        exit 1
        ;;
esac

SKILLS_TARGET="$TARGET_DIR/skills"
mkdir -p "$SKILLS_TARGET"

# Link the prosthetic-cover skill
SKILL_DIR="$SKILLS_TARGET/prosthetic-cover"
mkdir -p "$SKILL_DIR"

if [ -L "$SKILL_DIR/SKILL.md" ] || [ -f "$SKILL_DIR/SKILL.md" ]; then
    rm "$SKILL_DIR/SKILL.md"
fi
ln -sf "$SCRIPT_DIR/skills/prosthetic-cover/SKILL.md" "$SKILL_DIR/SKILL.md"
ok "Linked prosthetic-cover skill"

# Install Python dependencies
if command -v pip &>/dev/null; then
    info "Installing Python engine dependencies..."
    pip install -e "$SCRIPT_DIR" 2>/dev/null && ok "Python engine installed" || warn "pip install failed — install manually: pip install -e $SCRIPT_DIR"
elif command -v pip3 &>/dev/null; then
    info "Installing Python engine dependencies..."
    pip3 install -e "$SCRIPT_DIR" 2>/dev/null && ok "Python engine installed" || warn "pip3 install failed — install manually: pip3 install -e $SCRIPT_DIR"
else
    warn "pip not found — install Python dependencies manually: pip install -e $SCRIPT_DIR"
fi

echo ""
echo "=============================="
echo -e "${GREEN}${BOLD}Prosthetic Cover skill installed!${NC}"
echo "=============================="
echo ""
echo "Usage:"
echo "  /prosthetic-cover new --scan_path ./scan.stl"
echo "  /prosthetic-cover configure"
echo "  /prosthetic-cover validate"
echo "  /prosthetic-cover export"
echo ""
