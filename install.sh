#!/usr/bin/env bash
# Claude Dev Tools — Master Installer
#
# Usage:
#   ./install.sh --all                        # Install everything
#   ./install.sh --toolkit                    # Install toolkit only
#   ./install.sh --design-kit                 # Install design-kit only
#   ./install.sh --prompt-engine              # Install prompt-engine only
#   ./install.sh --toolkit --prompt-engine    # Install specific packages
#
# Target:
#   --global    Install to ~/.claude/ (all projects)
#   --project   Install to ./.claude/ (current project only)
#
# Idempotent: safe to run multiple times.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d%H%M%S)"

# Colors (bash 3.2+ compatible)
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

# --- Parse arguments ---
MODE=""
INSTALL_ALL=false
INSTALL_TOOLKIT=false
INSTALL_DESIGN_KIT=false
INSTALL_PROMPT_ENGINE=false
ANY_PACKAGE=false

for arg in "$@"; do
    case "$arg" in
        --global|-g)        MODE="global" ;;
        --project|-p)       MODE="project" ;;
        --all|-a)           INSTALL_ALL=true; ANY_PACKAGE=true ;;
        --toolkit)          INSTALL_TOOLKIT=true; ANY_PACKAGE=true ;;
        --design-kit)       INSTALL_DESIGN_KIT=true; ANY_PACKAGE=true ;;
        --prompt-engine)    INSTALL_PROMPT_ENGINE=true; ANY_PACKAGE=true ;;
        --help|-h)
            echo ""
            echo "Claude Dev Tools — Master Installer"
            echo ""
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Packages (select one or more):"
            echo "  --all              Install all packages"
            echo "  --toolkit          Install core engineering toolkit"
            echo "  --design-kit       Install design intelligence kit"
            echo "  --prompt-engine    Install prompt optimization engine"
            echo ""
            echo "Target (select one):"
            echo "  --global, -g       Install to ~/.claude/ (all projects)"
            echo "  --project, -p      Install to ./.claude/ (current project)"
            echo ""
            echo "Examples:"
            echo "  ./install.sh --all --global"
            echo "  ./install.sh --toolkit --project"
            echo "  ./install.sh --toolkit --prompt-engine --global"
            echo ""
            exit 0
            ;;
        *) err "Unknown option: $arg. Run ./install.sh --help"; exit 1 ;;
    esac
done

# --- Interactive prompts for missing selections ---

if [ -z "$MODE" ]; then
    echo ""
    echo -e "${BOLD}Claude Dev Tools${NC}"
    echo -e "Battle-tested Claude Code configuration"
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

if [ "$ANY_PACKAGE" = false ]; then
    echo ""
    echo "Which packages would you like to install?"
    echo "  1) All (toolkit + design-kit + prompt-engine)"
    echo "  2) Toolkit only (agents, workflows, hooks, rules)"
    echo "  3) Design Kit only (UI/UX skills, palettes, typography)"
    echo "  4) Prompt Engine only (meta-prompts, autopilot, ultrawork)"
    echo ""
    read -rp "Choose [1/2/3/4]: " pkg_choice
    case "$pkg_choice" in
        1) INSTALL_ALL=true ;;
        2) INSTALL_TOOLKIT=true ;;
        3) INSTALL_DESIGN_KIT=true ;;
        4) INSTALL_PROMPT_ENGINE=true ;;
        *) err "Invalid choice."; exit 1 ;;
    esac
fi

if [ "$INSTALL_ALL" = true ]; then
    INSTALL_TOOLKIT=true
    INSTALL_DESIGN_KIT=true
    INSTALL_PROMPT_ENGINE=true
fi

# --- Set target directory ---

if [ "$MODE" = "global" ]; then
    TARGET_DIR="$HOME/.claude"
    info "Installing globally to $TARGET_DIR/"
else
    PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    TARGET_DIR="$PROJECT_ROOT/.claude"
    info "Installing to project at $TARGET_DIR/"
fi

mkdir -p "$TARGET_DIR"

# --- Helper: symlink a directory ---
link_dir() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [ -L "$dest" ]; then
        local existing_target
        existing_target=$(readlink "$dest")
        if [ "$existing_target" = "$src" ]; then
            ok "$name already linked (up to date)"
            return
        else
            warn "$name symlink points elsewhere — relinking"
            rm "$dest"
        fi
    elif [ -d "$dest" ]; then
        warn "$name directory exists — backing up to ${dest}${BACKUP_SUFFIX}"
        mv "$dest" "${dest}${BACKUP_SUFFIX}"
    fi

    ln -s "$src" "$dest"
    ok "$name linked: $dest -> $src"
}

# --- Helper: symlink a skill directory ---
link_skill() {
    local skill_file="$1"
    local target_skills_dir="$2"
    local skill_name
    skill_name="$(basename "$skill_file" .md)"

    local skill_dir="$target_skills_dir/$skill_name"
    mkdir -p "$skill_dir"

    if [ -L "$skill_dir/SKILL.md" ] || [ -f "$skill_dir/SKILL.md" ]; then
        rm "$skill_dir/SKILL.md"
    fi
    ln -sf "$skill_file" "$skill_dir/SKILL.md"
}

# --- Helper: merge settings.json ---
merge_settings() {
    local example_settings="$1"
    local settings_file="$TARGET_DIR/settings.json"

    if [ ! -f "$example_settings" ]; then
        return
    fi

    if [ -f "$settings_file" ]; then
        if command -v jq &>/dev/null; then
            warn "settings.json exists — merging new commands (existing settings preserved)"

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
            ' "$settings_file" "$example_settings" 2>/dev/null || true)

            if [ -n "$MERGED" ]; then
                cp "$settings_file" "${settings_file}${BACKUP_SUFFIX}"
                echo "$MERGED" > "$settings_file"
                ok "settings.json merged (backup at ${settings_file}${BACKUP_SUFFIX})"
            else
                warn "jq merge failed — copying example as reference"
                cp "$example_settings" "${settings_file}.example"
            fi
        else
            warn "jq not installed — cannot merge settings. Copying example as reference."
            cp "$example_settings" "${settings_file}.example"
        fi
    else
        if command -v jq &>/dev/null; then
            local hooks_dir="$SCRIPT_DIR/packages/toolkit/hooks"
            jq --arg hooks "$hooks_dir" '
                .hooks.PreToolUse[0].hooks[0].command = ($hooks + "/pre-tool.sh") |
                .hooks.PostToolUse[0].hooks[0].command = ($hooks + "/post-tool.sh") |
                .hooks.Stop[0].hooks[0].command = ($hooks + "/memory-check.sh")
            ' "$example_settings" > "$settings_file" 2>/dev/null || cp "$example_settings" "$settings_file"
            ok "settings.json created with hook paths"
        else
            cp "$example_settings" "$settings_file"
            warn "settings.json copied (update hook paths manually — jq not available)"
        fi
    fi
}

# ============================================================
#  Install packages
# ============================================================

echo ""

# --- TOOLKIT ---
if [ "$INSTALL_TOOLKIT" = true ]; then
    info "Installing Toolkit (core engineering)..."
    echo ""

    TOOLKIT_DIR="$SCRIPT_DIR/packages/toolkit"

    link_dir "$TOOLKIT_DIR/agents"    "$TARGET_DIR/agents"    "Agents"
    link_dir "$TOOLKIT_DIR/skills"    "$TARGET_DIR/skills"    "Skills (toolkit)"
    link_dir "$TOOLKIT_DIR/workflows" "$TARGET_DIR/workflows" "Workflows"
    link_dir "$TOOLKIT_DIR/hooks"     "$TARGET_DIR/hooks"     "Hooks"
    link_dir "$TOOLKIT_DIR/rules"     "$TARGET_DIR/rules"     "Rules"
    link_dir "$TOOLKIT_DIR/docs"      "$TARGET_DIR/docs"      "Docs (toolkit)"

    # Make hooks executable
    chmod +x "$TOOLKIT_DIR/hooks/"*.sh 2>/dev/null || true

    # Merge settings
    merge_settings "$TOOLKIT_DIR/settings/settings.example.json"

    echo ""
fi

# --- DESIGN KIT ---
if [ "$INSTALL_DESIGN_KIT" = true ]; then
    info "Installing Design Kit (UI/UX intelligence)..."
    echo ""

    DESIGN_KIT_DIR="$SCRIPT_DIR/packages/design-kit"
    SKILLS_TARGET="$TARGET_DIR/skills"
    mkdir -p "$SKILLS_TARGET"

    # Link the full kit
    if [ -L "$SKILLS_TARGET/claude-design-kit" ]; then
        rm "$SKILLS_TARGET/claude-design-kit"
    fi
    ln -sf "$DESIGN_KIT_DIR/skills" "$SKILLS_TARGET/claude-design-kit"
    ok "Linked design-kit skills"

    # Link ui-ux-pro-max as top-level
    if [ -L "$SKILLS_TARGET/ui-ux-pro-max" ]; then
        rm "$SKILLS_TARGET/ui-ux-pro-max"
    fi
    ln -sf "$DESIGN_KIT_DIR/skills/ui-ux-pro-max" "$SKILLS_TARGET/ui-ux-pro-max"
    ok "Linked ui-ux-pro-max"

    # Link frontend-design reference
    if [ -L "$SKILLS_TARGET/frontend-design" ]; then
        rm "$SKILLS_TARGET/frontend-design"
    fi
    mkdir -p "$SKILLS_TARGET/frontend-design"
    ln -sf "$DESIGN_KIT_DIR/skills/frontend-design.md" "$SKILLS_TARGET/frontend-design/SKILL.md"
    if [ -d "$DESIGN_KIT_DIR/skills/frontend-design-reference" ]; then
        ln -sf "$DESIGN_KIT_DIR/skills/frontend-design-reference" "$SKILLS_TARGET/frontend-design/reference"
    fi
    ok "Linked frontend-design with references"

    # Link individual design skills
    SKILL_COUNT=0
    for skill_file in "$DESIGN_KIT_DIR/skills"/*.md; do
        skill_name="$(basename "$skill_file" .md)"
        if [ "$skill_name" = "SKILLS_INDEX" ] || [ "$skill_name" = "frontend-design" ]; then
            continue
        fi
        link_skill "$skill_file" "$SKILLS_TARGET"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    done
    ok "Linked $SKILL_COUNT individual design skills"

    # Link design agents if agents directory exists
    if [ -d "$TARGET_DIR/agents" ] || [ -L "$TARGET_DIR/agents" ]; then
        local_agents_dir="$TARGET_DIR/agents"
        if [ -L "$local_agents_dir" ]; then
            # agents is a symlink (from toolkit), link into the source
            actual_agents=$(readlink "$local_agents_dir")
            for agent_file in "$DESIGN_KIT_DIR/agents"/*.md; do
                agent_name="$(basename "$agent_file")"
                ln -sf "$agent_file" "$actual_agents/$agent_name" 2>/dev/null || true
            done
        fi
    fi

    echo ""
fi

# --- PROMPT ENGINE ---
if [ "$INSTALL_PROMPT_ENGINE" = true ]; then
    info "Installing Prompt Engine (meta-intelligence)..."
    echo ""

    PROMPT_ENGINE_DIR="$SCRIPT_DIR/packages/prompt-engine"
    SKILLS_TARGET="$TARGET_DIR/skills"
    mkdir -p "$SKILLS_TARGET"

    # Link each prompt-engine skill
    PE_COUNT=0
    for skill_file in "$PROMPT_ENGINE_DIR/skills"/*.md; do
        link_skill "$skill_file" "$SKILLS_TARGET"
        PE_COUNT=$((PE_COUNT + 1))
    done
    ok "Linked $PE_COUNT prompt-engine skills"

    echo ""
fi

# ============================================================
#  Summary
# ============================================================

echo "=============================="
echo -e "${GREEN}${BOLD}Installation complete!${NC}"
echo "=============================="
echo ""
echo "Installed to: $TARGET_DIR/"
echo ""

if [ "$INSTALL_TOOLKIT" = true ]; then
    echo "Toolkit:"
    echo "  - 35 specialist agents"
    echo "  - 5 skills (/plan, /tdd, /deslop, /session, /learner)"
    echo "  - 4 workflow pipelines"
    echo "  - 3 hooks (pre-tool, post-tool, memory-check)"
    echo "  - 4 rules (typescript, python, testing, migrations)"
    echo ""
fi

if [ "$INSTALL_DESIGN_KIT" = true ]; then
    echo "Design Kit:"
    echo "  - 24 design skills (/polish, /bolder, /animate, /typeset, ...)"
    echo "  - UI/UX Pro Max design system generator"
    echo "  - 67 styles, 96 palettes, 57 font pairings"
    echo "  - 2 design agents"
    echo ""
fi

if [ "$INSTALL_PROMPT_ENGINE" = true ]; then
    echo "Prompt Engine:"
    echo "  - /meta (master prompt optimizer)"
    echo "  - /meta-lite (fast prompt enhancer)"
    echo "  - /meta-engineering (backend-focused optimizer)"
    echo "  - /meta-design (frontend-focused optimizer)"
    echo "  - /deep-interview (Socratic requirements gathering)"
    echo "  - /autopilot (zero-intervention pipeline)"
    echo "  - /ultrawork (maximum parallelism engine)"
    echo ""
fi

echo "Next steps:"
echo "  1. Start a Claude Code session"
if [ "$INSTALL_TOOLKIT" = true ]; then
    echo "  2. Try: /plan, /tdd, /deslop, /session"
fi
if [ "$INSTALL_DESIGN_KIT" = true ]; then
    echo "  2. Try: /teach-impeccable, /polish, /bolder, /audit"
fi
if [ "$INSTALL_PROMPT_ENGINE" = true ]; then
    echo "  2. Try: /meta, /autopilot, /ultrawork"
fi
echo ""
