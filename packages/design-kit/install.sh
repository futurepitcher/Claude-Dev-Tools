#!/usr/bin/env bash
set -euo pipefail

# Claude Design Kit Installer
# Install design intelligence skills for Claude Code
#
# Usage:
#   ./install.sh              # Install to current project (.claude/skills/)
#   ./install.sh --global     # Install to ~/.claude/skills/
#   ./install.sh --project    # Same as default (explicit project mode)
#   ./install.sh --uninstall  # Remove symlinks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_NAME="claude-design-kit"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}Claude Design Kit${NC}"
    echo -e "${BLUE}AI-powered design intelligence for Claude Code${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}[ok]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[--]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[!!]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERR]${NC} $1"
}

# Parse arguments
MODE="project"
UNINSTALL=false

for arg in "$@"; do
    case $arg in
        --global|-g)
            MODE="global"
            ;;
        --project|-p)
            MODE="project"
            ;;
        --uninstall|-u)
            UNINSTALL=true
            ;;
        --help|-h)
            print_header
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --project, -p    Install to current project .claude/skills/ (default)"
            echo "  --global, -g     Install to ~/.claude/skills/"
            echo "  --uninstall, -u  Remove installed symlinks"
            echo "  --help, -h       Show this help"
            echo ""
            echo "Project mode makes skills available in the current project only."
            echo "Global mode makes skills available in all projects."
            exit 0
            ;;
        *)
            print_error "Unknown option: $arg"
            echo "Run ./install.sh --help for usage"
            exit 1
            ;;
    esac
done

# Determine target directory
if [ "$MODE" = "global" ]; then
    TARGET_DIR="$HOME/.claude/skills"
else
    TARGET_DIR=".claude/skills"
fi

print_header

if [ "$UNINSTALL" = true ]; then
    print_info "Uninstalling from $TARGET_DIR..."

    # Remove symlinks
    LINKS=(
        "$TARGET_DIR/$KIT_NAME"
        "$TARGET_DIR/ui-ux-pro-max"
        "$TARGET_DIR/frontend-design"
    )

    # Also remove individual skill symlinks
    for skill in adapt animate arrange audit bolder clarify colorize critique delight distill extract harden normalize onboard optimize overdrive polish quieter remotion-best-practices teach-impeccable typeset; do
        LINKS+=("$TARGET_DIR/$skill")
    done

    removed=0
    for link in "${LINKS[@]}"; do
        if [ -L "$link" ]; then
            rm "$link"
            print_success "Removed $link"
            ((removed++))
        fi
    done

    if [ $removed -eq 0 ]; then
        print_warn "No symlinks found to remove"
    else
        print_success "Removed $removed symlinks"
    fi

    echo ""
    print_success "Uninstall complete"
    exit 0
fi

# Create target directory
print_info "Installing to $TARGET_DIR ($MODE mode)..."
mkdir -p "$TARGET_DIR"

# Create main kit symlink
SKILLS_SRC="$SCRIPT_DIR/skills"

# Symlink the full kit directory
if [ -L "$TARGET_DIR/$KIT_NAME" ]; then
    rm "$TARGET_DIR/$KIT_NAME"
fi
ln -sf "$SKILLS_SRC" "$TARGET_DIR/$KIT_NAME"
print_success "Linked skills/ -> $TARGET_DIR/$KIT_NAME"

# Symlink ui-ux-pro-max as top-level for direct invocation
if [ -L "$TARGET_DIR/ui-ux-pro-max" ]; then
    rm "$TARGET_DIR/ui-ux-pro-max"
fi
ln -sf "$SKILLS_SRC/ui-ux-pro-max" "$TARGET_DIR/ui-ux-pro-max"
print_success "Linked ui-ux-pro-max"

# Symlink frontend-design reference
if [ -L "$TARGET_DIR/frontend-design" ]; then
    rm "$TARGET_DIR/frontend-design"
fi
mkdir -p "$TARGET_DIR/frontend-design"
# Create a SKILL.md that points to the actual skill
ln -sf "$SKILLS_SRC/frontend-design.md" "$TARGET_DIR/frontend-design/SKILL.md"
# Link reference files
if [ -d "$SCRIPT_DIR/skills/frontend-design-reference" ]; then
    ln -sf "$SCRIPT_DIR/skills/frontend-design-reference" "$TARGET_DIR/frontend-design/reference"
fi
print_success "Linked frontend-design with references"

# Symlink individual skills for direct /skill invocation
SKILL_COUNT=0
for skill_file in "$SKILLS_SRC"/*.md; do
    skill_name="$(basename "$skill_file" .md)"

    # Skip index files
    if [ "$skill_name" = "SKILLS_INDEX" ] || [ "$skill_name" = "frontend-design" ]; then
        continue
    fi

    skill_dir="$TARGET_DIR/$skill_name"

    # Create skill directory with SKILL.md (Claude Code convention)
    mkdir -p "$skill_dir"
    if [ -L "$skill_dir/SKILL.md" ] || [ -f "$skill_dir/SKILL.md" ]; then
        rm "$skill_dir/SKILL.md"
    fi
    ln -sf "$skill_file" "$skill_dir/SKILL.md"
    ((SKILL_COUNT++))
done
print_success "Linked $SKILL_COUNT individual skills"

# Copy agents if target has agents directory
if [ "$MODE" = "project" ] && [ -d ".claude/agents" ]; then
    for agent_file in "$SCRIPT_DIR/agents"/*.md; do
        agent_name="$(basename "$agent_file")"
        if [ -L ".claude/agents/$agent_name" ]; then
            rm ".claude/agents/$agent_name"
        fi
        ln -sf "$agent_file" ".claude/agents/$agent_name"
    done
    print_success "Linked agents to .claude/agents/"
fi

# Summary
echo ""
echo -e "${BOLD}${GREEN}Installation complete!${NC}"
echo ""
echo "Installed to: $TARGET_DIR"
echo ""
echo -e "${BOLD}Quick start:${NC}"
echo "  /teach-impeccable    Set up design context for your project"
echo "  /ui-ux-pro-max       Generate a complete design system"
echo "  /frontend-design     Build distinctive UI components"
echo "  /polish              Final quality pass before shipping"
echo "  /audit               Comprehensive design quality audit"
echo ""
echo -e "${BOLD}All skills:${NC}"
echo "  /adapt /animate /arrange /audit /bolder /clarify /colorize"
echo "  /critique /delight /distill /extract /harden /normalize"
echo "  /onboard /optimize /overdrive /polish /quieter /typeset"
echo ""
echo "See skills/SKILLS_INDEX.md for the full catalog."
