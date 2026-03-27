#!/bin/bash
# Pre-Tool Execution Hook
#
# Claude Code passes tool context as JSON via stdin.
# Input JSON schema: { "tool_name": string, "tool_input": object }
#   - Edit/Write: tool_input.file_path
#   - Bash: tool_input.command
#
# Exit codes:
#   0 - Allow execution
#   2 - Block execution (stderr shown to Claude as reason)
#   1 - Non-blocking error (does NOT block)
#
# Features:
#   - Phase gate enforcement (advisory/tdd/strict modes)
#   - `any` type introduction detection for TypeScript
#   - Credential file blocking
#   - Dangerous command blocking
#   - Session metrics tracking

set +e

# Configuration — customize PROJECT_ROOT for your project
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_DIR="${PROJECT_ROOT}/.claude/hooks"
LOG_FILE="${HOOKS_DIR}/audit.log"
ENFORCEMENT_FILE="${HOOKS_DIR}/enforcement-mode.txt"
PHASE_FILE="${HOOKS_DIR}/phase-state.txt"
SESSION_METRICS="${PROJECT_ROOT}/.claude/memory/metrics.jsonl"

mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
mkdir -p "$(dirname "$SESSION_METRICS")" 2>/dev/null

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] PRE: $*" >> "$LOG_FILE" 2>/dev/null
}

# --- Parse JSON from stdin ---
if ! command -v jq &>/dev/null; then
    exit 0
fi

INPUT=$(cat /dev/stdin 2>/dev/null || echo '{}')

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if [[ -z "$TOOL_NAME" ]]; then
    exit 0
fi

log "Tool: $TOOL_NAME, File: $FILE_PATH, Command: ${COMMAND:0:100}"

# Track tool invocation for session metrics
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"tool_invoke\",\"tool\":\"$TOOL_NAME\",\"file\":\"$FILE_PATH\"}" >> "$SESSION_METRICS" 2>/dev/null || true

# Skip checks for read-only tools
case "$TOOL_NAME" in
    Read|Glob|Grep|LSP|WebFetch|WebSearch|Agent|ToolSearch)
        exit 0
        ;;
esac

# --- Phase Gate Enforcement ---
# Modes: off (default), advisory, tdd, strict
ENFORCEMENT_MODE="off"
if [[ -f "$ENFORCEMENT_FILE" ]]; then
    ENFORCEMENT_MODE=$(cat "$ENFORCEMENT_FILE" 2>/dev/null || echo "off")
fi

CURRENT_PHASE="IMPLEMENT"
if [[ -f "$PHASE_FILE" ]]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE" 2>/dev/null || echo "IMPLEMENT")
fi

if [[ "$ENFORCEMENT_MODE" != "off" ]]; then
    if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then
        case "$CURRENT_PHASE" in
            PLAN)
                if [[ "$ENFORCEMENT_MODE" == "strict" ]]; then
                    log "BLOCKED: Write during PLAN phase (strict mode): $FILE_PATH"
                    echo "Phase gate: PLAN phase - use Read/Glob/Grep only. Switch phase with /enforce phase GREEN" >&2
                    exit 2
                elif [[ "$ENFORCEMENT_MODE" != "off" ]]; then
                    echo "Advisory: Currently in PLAN phase - consider finishing planning before editing"
                fi
                ;;
            RED)
                if [[ ! "$FILE_PATH" =~ \.(test|spec)\.(ts|tsx|js|jsx|py)$ ]] && [[ ! "$FILE_PATH" =~ tests/ ]]; then
                    if [[ "$ENFORCEMENT_MODE" == "strict" || "$ENFORCEMENT_MODE" == "tdd" ]]; then
                        log "BLOCKED: Non-test write during RED phase: $FILE_PATH"
                        echo "Phase gate: RED phase - write tests first. Edit test files or switch to GREEN with /enforce phase GREEN" >&2
                        exit 2
                    elif [[ "$ENFORCEMENT_MODE" == "advisory" ]]; then
                        echo "Advisory: RED phase - consider writing tests before source code"
                    fi
                fi
                ;;
        esac
    fi
fi

# --- Write/Edit Operation Checks ---
if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then

    # Block writes to credential files
    if [[ "$FILE_PATH" =~ \.(pem|key|credentials)$ ]] || [[ "$FILE_PATH" =~ \.env$ ]] || [[ "$FILE_PATH" =~ \.env\.local$ ]]; then
        log "BLOCKED: Attempt to modify sensitive file: $FILE_PATH"
        echo "Blocked: Cannot modify credential/secret files directly ($FILE_PATH)" >&2
        exit 2
    fi

    # Warn about modifying core config (non-blocking)
    if [[ "$FILE_PATH" =~ (package\.json|tsconfig\.json|\.claude/settings\.json)$ ]]; then
        log "WARNING: Modifying core config: $FILE_PATH"
    fi

    # Capture pre-edit `any` type count for TypeScript files (for post-hook comparison)
    if [[ "$FILE_PATH" =~ \.(ts|tsx)$ ]] && [[ -f "$FILE_PATH" ]]; then
        ANY_COUNT=$(grep -c ': any\b\|: any;\|: any,\|: any)\|as any\b' "$FILE_PATH" 2>/dev/null || echo "0")
        FILE_HASH=$(echo "$FILE_PATH" | md5 2>/dev/null || echo "$FILE_PATH" | md5sum 2>/dev/null | cut -d' ' -f1)
        echo "$ANY_COUNT" > "/tmp/cct_any_count_${FILE_HASH}" 2>/dev/null || true
    fi
fi

# --- Bash Command Checks ---
if [[ "$TOOL_NAME" == "Bash" ]] && [[ -n "$COMMAND" ]]; then

    # Block dangerous commands
    if [[ "$COMMAND" =~ (rm[[:space:]]+-rf[[:space:]]+/|sudo|--force.*push|reset.*--hard) ]]; then
        log "BLOCKED: Dangerous command: $COMMAND"
        echo "Blocked: Dangerous command pattern detected: ${COMMAND:0:80}" >&2
        exit 2
    fi

    # Warn about production-impacting commands (non-blocking)
    if [[ "$COMMAND" =~ (npm[[:space:]]+publish|docker[[:space:]]+push|DROP[[:space:]]+TABLE|TRUNCATE) ]]; then
        log "WARNING: Production-impacting command: $COMMAND"
        echo "Warning: This command may affect production systems"
    fi
fi

exit 0
