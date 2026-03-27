#!/bin/bash
# Claude Code Toolkit Uninstaller
#
# Usage:
#   ./uninstall.sh --global    # Remove from ~/.claude/
#   ./uninstall.sh --project   # Remove from ./.claude/
#   ./uninstall.sh             # Interactive mode

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }

TOOLKIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine mode
MODE=""
if [[ "${1:-}" == "--global" ]]; then
    MODE="global"
elif [[ "${1:-}" == "--project" ]]; then
    MODE="project"
else
    echo ""
    echo "Claude Code Toolkit Uninstaller"
    echo "================================"
    echo ""
    echo "Where would you like to uninstall from?"
    echo "  1) Global  (~/.claude/)"
    echo "  2) Project (./.claude/)"
    echo ""
    read -rp "Choose [1/2]: " choice
    case "$choice" in
        1) MODE="global" ;;
        2) MODE="project" ;;
        *) echo "Invalid choice."; exit 1 ;;
    esac
fi

if [[ "$MODE" == "global" ]]; then
    TARGET_DIR="${HOME}/.claude"
else
    PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    TARGET_DIR="${PROJECT_ROOT}/.claude"
fi

info "Uninstalling from ${TARGET_DIR}/"
echo ""

# Remove symlinks (only if they point to our toolkit)
remove_link() {
    local dest="$1"
    local name="$2"

    if [[ -L "$dest" ]]; then
        local target
        target=$(readlink "$dest")
        if [[ "$target" == "$TOOLKIT_DIR/"* ]]; then
            rm "$dest"
            ok "Removed $name symlink"

            # Restore backup if it exists
            local backup
            backup=$(ls -1t "${dest}.backup."* 2>/dev/null | head -1)
            if [[ -n "$backup" ]]; then
                mv "$backup" "$dest"
                ok "Restored $name from backup"
            fi
        else
            warn "$name symlink points elsewhere ($target) — skipping"
        fi
    else
        warn "$name is not a symlink — skipping (may have been customized)"
    fi
}

remove_link "$TARGET_DIR/agents"    "Agents"
remove_link "$TARGET_DIR/skills"    "Skills"
remove_link "$TARGET_DIR/workflows" "Workflows"
remove_link "$TARGET_DIR/hooks"     "Hooks"
remove_link "$TARGET_DIR/rules"     "Rules"
remove_link "$TARGET_DIR/docs"      "Docs"

# Check if settings.json references our hooks
if [[ -f "$TARGET_DIR/settings.json" ]]; then
    if grep -q "claude-code-toolkit" "$TARGET_DIR/settings.json" 2>/dev/null; then
        warn "settings.json references toolkit paths — you may want to update hook paths"
    fi
fi

echo ""
echo "================================"
echo -e "${GREEN}Uninstall complete.${NC}"
echo "================================"
echo ""
echo "Settings file preserved at: $TARGET_DIR/settings.json"
echo "Backups (if any) are in: $TARGET_DIR/*.backup.*"
echo ""
