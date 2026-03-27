#!/usr/bin/env bash
# Claude Dev Tools — Master Uninstaller
#
# Usage:
#   ./uninstall.sh --global              # Remove from ~/.claude/
#   ./uninstall.sh --project             # Remove from ./.claude/
#   ./uninstall.sh --global --toolkit    # Remove only toolkit
#   ./uninstall.sh --global --design-kit # Remove only design-kit
#   ./uninstall.sh --global --prompt-engine  # Remove only prompt-engine

set -euo pipefail

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

MODE=""
TOOLKIT=false
DESIGN_KIT=false
PROMPT_ENGINE=false
ANY_PACKAGE=false

for arg in "$@"; do
    case "$arg" in
        --global|-g)    MODE="global" ;;
        --project|-p)   MODE="project" ;;
        --toolkit)      TOOLKIT=true; ANY_PACKAGE=true ;;
        --design-kit)   DESIGN_KIT=true; ANY_PACKAGE=true ;;
        --prompt-engine) PROMPT_ENGINE=true; ANY_PACKAGE=true ;;
        --help|-h)
            echo "Usage: ./uninstall.sh [--global|--project] [--toolkit] [--design-kit] [--prompt-engine]"
            exit 0
            ;;
        *) err "Unknown option: $arg"; exit 1 ;;
    esac
done

if [ -z "$MODE" ]; then
    echo ""
    echo "Claude Dev Tools Uninstaller"
    echo "============================"
    echo ""
    echo "Remove from:"
    echo "  1) Global  (~/.claude/)"
    echo "  2) Project (./.claude/)"
    echo ""
    read -rp "Choose [1/2]: " choice
    case "$choice" in
        1) MODE="global" ;;
        2) MODE="project" ;;
        *) err "Invalid choice."; exit 1 ;;
    esac
fi

if [ "$MODE" = "global" ]; then
    TARGET_DIR="$HOME/.claude"
else
    PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    TARGET_DIR="$PROJECT_ROOT/.claude"
fi

# If no specific package selected, remove all
if [ "$ANY_PACKAGE" = false ]; then
    TOOLKIT=true
    DESIGN_KIT=true
    PROMPT_ENGINE=true
fi

removed=0

remove_link() {
    local path="$1"
    local label="$2"
    if [ -L "$path" ]; then
        rm "$path"
        ok "Removed $label"
        removed=$((removed + 1))
    elif [ -d "$path" ] || [ -f "$path" ]; then
        warn "$label exists but is not a symlink -- skipping (remove manually if desired)"
    fi
}

echo ""
info "Uninstalling from $TARGET_DIR..."
echo ""

if [ "$TOOLKIT" = true ]; then
    remove_link "$TARGET_DIR/agents"    "agents"
    remove_link "$TARGET_DIR/skills"    "skills (toolkit)"
    remove_link "$TARGET_DIR/workflows" "workflows"
    remove_link "$TARGET_DIR/hooks"     "hooks"
    remove_link "$TARGET_DIR/rules"     "rules"
    remove_link "$TARGET_DIR/docs"      "docs (toolkit)"
fi

if [ "$DESIGN_KIT" = true ]; then
    remove_link "$TARGET_DIR/skills/claude-design-kit" "claude-design-kit"
    remove_link "$TARGET_DIR/skills/ui-ux-pro-max"     "ui-ux-pro-max"
    remove_link "$TARGET_DIR/skills/frontend-design"   "frontend-design"
    for skill in adapt animate arrange audit bolder clarify colorize critique delight distill extract harden normalize onboard optimize overdrive polish quieter remotion-best-practices teach-impeccable typeset; do
        remove_link "$TARGET_DIR/skills/$skill" "$skill"
    done
fi

if [ "$PROMPT_ENGINE" = true ]; then
    for skill in meta meta-lite meta-engineering meta-design deep-interview autopilot ultrawork; do
        remove_link "$TARGET_DIR/skills/$skill" "$skill (prompt-engine)"
    done
fi

echo ""
if [ $removed -eq 0 ]; then
    warn "No symlinks found to remove."
else
    ok "Removed $removed symlinks."
fi
echo ""
