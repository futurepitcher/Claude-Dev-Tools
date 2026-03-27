#!/bin/bash
# Claude Code Toolkit Installer
#
# Usage:
#   ./install.sh --global    # Install to ~/.claude/ (applies to all projects)
#   ./install.sh --project   # Install to ./.claude/ (current project only)
#   ./install.sh             # Interactive mode (asks which)
#
# Idempotent: safe to run multiple times.

set -euo pipefail

TOOLKIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d%H%M%S)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Determine install mode
MODE=""
if [[ "${1:-}" == "--global" ]]; then
    MODE="global"
elif [[ "${1:-}" == "--project" ]]; then
    MODE="project"
else
    echo ""
    echo "Claude Code Toolkit Installer"
    echo "=============================="
    echo ""
    echo "Where would you like to install?"
    echo "  1) Global  (~/.claude/ — applies to all projects)"
    echo "  2) Project (./.claude/ — current project only)"
    echo ""
    read -rp "Choose [1/2]: " choice
    case "$choice" in
        1) MODE="global" ;;
        2) MODE="project" ;;
        *) err "Invalid choice. Use --global or --project."; exit 1 ;;
    esac
fi

# Set target directory
if [[ "$MODE" == "global" ]]; then
    TARGET_DIR="${HOME}/.claude"
    info "Installing globally to ${TARGET_DIR}/"
else
    # Find git root or use current directory
    PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    TARGET_DIR="${PROJECT_ROOT}/.claude"
    info "Installing to project at ${TARGET_DIR}/"
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# --- Symlink a directory ---
# If target exists and is not already our symlink, back it up
link_dir() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [[ -L "$dest" ]]; then
        local existing_target
        existing_target=$(readlink "$dest")
        if [[ "$existing_target" == "$src" ]]; then
            ok "$name already linked (up to date)"
            return
        else
            warn "$name symlink points elsewhere — relinking"
            rm "$dest"
        fi
    elif [[ -d "$dest" ]]; then
        warn "$name directory exists — backing up to ${dest}${BACKUP_SUFFIX}"
        mv "$dest" "${dest}${BACKUP_SUFFIX}"
    fi

    ln -s "$src" "$dest"
    ok "$name linked: $dest -> $src"
}

# --- Copy a file (don't overwrite if exists, unless it's ours) ---
copy_file() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [[ -f "$dest" ]]; then
        # Check if file is identical
        if diff -q "$src" "$dest" &>/dev/null; then
            ok "$name already up to date"
            return
        else
            warn "$name exists and differs — backing up to ${dest}${BACKUP_SUFFIX}"
            cp "$dest" "${dest}${BACKUP_SUFFIX}"
        fi
    fi

    cp "$src" "$dest"
    ok "$name installed"
}

echo ""
info "Installing components..."
echo ""

# --- Link directories ---
link_dir "$TOOLKIT_DIR/agents"    "$TARGET_DIR/agents"    "Agents"
link_dir "$TOOLKIT_DIR/skills"    "$TARGET_DIR/skills"    "Skills"
link_dir "$TOOLKIT_DIR/workflows" "$TARGET_DIR/workflows" "Workflows"
link_dir "$TOOLKIT_DIR/hooks"     "$TARGET_DIR/hooks"     "Hooks"
link_dir "$TOOLKIT_DIR/rules"     "$TARGET_DIR/rules"     "Rules"
link_dir "$TOOLKIT_DIR/docs"      "$TARGET_DIR/docs"      "Docs"

# --- Make hooks executable ---
chmod +x "$TOOLKIT_DIR/hooks/"*.sh 2>/dev/null || true

# --- Merge settings.json ---
echo ""
info "Configuring settings..."

SETTINGS_FILE="$TARGET_DIR/settings.json"
EXAMPLE_SETTINGS="$TOOLKIT_DIR/settings/settings.example.json"

if [[ -f "$SETTINGS_FILE" ]]; then
    if command -v jq &>/dev/null; then
        # Merge: add missing commands and permissions from example
        warn "settings.json exists — merging new commands (existing settings preserved)"

        # Create merged version
        MERGED=$(jq -s '
            .[0] as $existing |
            .[1] as $new |
            $existing * {
                commands: ($new.commands // {} | to_entries | map(select(.key as $k | $existing.commands[$k] == null)) | from_entries) + ($existing.commands // {}),
                permissions: {
                    allow: (($existing.permissions.allow // []) + ($new.permissions.allow // []) | unique),
                    deny: (($existing.permissions.deny // []) + ($new.permissions.deny // []) | unique)
                }
            }
        ' "$SETTINGS_FILE" "$EXAMPLE_SETTINGS" 2>/dev/null)

        if [[ -n "$MERGED" ]]; then
            cp "$SETTINGS_FILE" "${SETTINGS_FILE}${BACKUP_SUFFIX}"
            echo "$MERGED" > "$SETTINGS_FILE"
            ok "settings.json merged (backup at ${SETTINGS_FILE}${BACKUP_SUFFIX})"
        else
            warn "jq merge failed — copying example as reference"
            copy_file "$EXAMPLE_SETTINGS" "${SETTINGS_FILE}.example" "settings.example.json"
        fi
    else
        warn "jq not installed — cannot merge settings. Copying example as reference."
        copy_file "$EXAMPLE_SETTINGS" "${SETTINGS_FILE}.example" "settings.example.json"
    fi
else
    # Update hook paths in settings to point to toolkit
    if command -v jq &>/dev/null; then
        HOOKS_DIR="$TOOLKIT_DIR/hooks"
        jq --arg hooks "$HOOKS_DIR" '
            .hooks.PreToolUse[0].hooks[0].command = ($hooks + "/pre-tool.sh") |
            .hooks.PostToolUse[0].hooks[0].command = ($hooks + "/post-tool.sh") |
            .hooks.Stop[0].hooks[0].command = ($hooks + "/memory-check.sh")
        ' "$EXAMPLE_SETTINGS" > "$SETTINGS_FILE"
        ok "settings.json created with correct hook paths"
    else
        cp "$EXAMPLE_SETTINGS" "$SETTINGS_FILE"
        warn "settings.json copied (update hook paths manually — jq not available)"
    fi
fi

# --- Summary ---
echo ""
echo "=============================="
echo -e "${GREEN}Installation complete!${NC}"
echo "=============================="
echo ""
echo "Installed to: $TARGET_DIR/"
echo ""
echo "Components:"
echo "  - 35 specialist agents"
echo "  - 5 skills (/plan, /tdd, /deslop, /session, /learner)"
echo "  - 4 workflow pipelines"
echo "  - 3 hooks (pre-tool, post-tool, memory-check)"
echo "  - 4 rules (typescript, python, testing, database-migrations)"
echo "  - 3 documentation guides"
echo ""
echo "Next steps:"
echo "  1. Review settings: $SETTINGS_FILE"
echo "  2. Copy the CLAUDE.md template: cp $TOOLKIT_DIR/templates/CLAUDE.md.template ./CLAUDE.md"
echo "  3. Start a Claude Code session and try: /plan, /help"
echo ""
