#!/bin/bash
# Post-Tool Execution Hook
#
# Claude Code passes tool context as JSON via stdin.
# Input JSON schema: { "tool_name": string, "tool_input": object, "tool_output"?: string }
#
# This hook is informational — it cannot block (tool already executed).
# Stdout messages are shown to Claude as system messages.
# Always exit 0.
#
# Features:
#   - `any` type introduction detection (compares pre/post counts)
#   - Secret detection in modified files
#   - console.log / bare except detection
#   - Session metrics tracking

set +e

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LOG_FILE="${PROJECT_ROOT}/.claude/hooks/audit.log"
ERRORS_LOG="${PROJECT_ROOT}/.claude/memory/errors.jsonl"
METRICS_LOG="${PROJECT_ROOT}/.claude/memory/metrics.jsonl"

mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
mkdir -p "$(dirname "$ERRORS_LOG")" 2>/dev/null

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] POST: $*" >> "$LOG_FILE" 2>/dev/null
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

log "Tool: $TOOL_NAME, File: $FILE_PATH"

# Track completion
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"tool_complete\",\"tool\":\"$TOOL_NAME\",\"file\":\"$FILE_PATH\"}" >> "$METRICS_LOG" 2>/dev/null || true

# --- After file modifications, run quality checks ---
if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then

    if [[ -n "$FILE_PATH" ]] && [[ -f "$FILE_PATH" ]]; then
        # Check for accidentally committed secrets
        if grep -qiE "(api[_-]?key|password|secret|token)[[:space:]]*[=:][[:space:]]*['\"][^'\"]{20,}" "$FILE_PATH" 2>/dev/null; then
            log "WARNING: Possible secret detected in $FILE_PATH"
            echo "Warning: File may contain hardcoded secrets - please review"
        fi

        # Check for console.log in TypeScript (production code)
        if [[ "$FILE_PATH" =~ \.(ts|tsx)$ ]] && [[ ! "$FILE_PATH" =~ \.test\. ]]; then
            if grep -q "console\.log" "$FILE_PATH" 2>/dev/null; then
                log "WARNING: console.log detected in $FILE_PATH"
                echo "Note: console.log detected in $FILE_PATH - remove before commit"
            fi
        fi

        # Check for bare except in Python
        if [[ "$FILE_PATH" =~ \.py$ ]]; then
            if grep -qE "^[[:space:]]*except[[:space:]]*:" "$FILE_PATH" 2>/dev/null; then
                log "WARNING: Bare except: detected in $FILE_PATH"
                echo "Note: Bare 'except:' detected in $FILE_PATH - specify exception type"
            fi
        fi

        # --- `any` type introduction detection ---
        if [[ "$FILE_PATH" =~ \.(ts|tsx)$ ]]; then
            FILE_HASH=$(echo "$FILE_PATH" | md5 2>/dev/null || echo "$FILE_PATH" | md5sum 2>/dev/null | cut -d' ' -f1)
            PRE_COUNT_FILE="/tmp/cct_any_count_${FILE_HASH}"
            if [[ -f "$PRE_COUNT_FILE" ]]; then
                PRE_COUNT=$(cat "$PRE_COUNT_FILE")
                POST_COUNT=$(grep -c ': any\b\|: any;\|: any,\|: any)\|as any\b' "$FILE_PATH" 2>/dev/null || echo "0")
                rm -f "$PRE_COUNT_FILE"

                if [[ "$POST_COUNT" -gt "$PRE_COUNT" ]]; then
                    NEW_ANY=$((POST_COUNT - PRE_COUNT))
                    log "WARNING: $NEW_ANY new 'any' type(s) introduced in $FILE_PATH"
                    echo "Warning: $NEW_ANY new 'any' type(s) introduced in $FILE_PATH - use proper types (unknown, generics, interfaces)"
                    echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"type\":\"any_type_introduced\",\"file\":\"$FILE_PATH\",\"count\":$NEW_ANY}" >> "$ERRORS_LOG" 2>/dev/null || true
                fi
            fi
        fi
    fi

    # Track file modification for session summary
    MODIFIED_FILES_LOG="${PROJECT_ROOT}/.claude/hooks/session_modified.txt"
    echo "$FILE_PATH" >> "$MODIFIED_FILES_LOG" 2>/dev/null || true
fi

# --- After Bash operations, log relevant state ---
if [[ "$TOOL_NAME" == "Bash" ]] && [[ -n "$COMMAND" ]]; then
    if [[ "$COMMAND" =~ ^git[[:space:]]+(commit|push|merge|rebase) ]]; then
        log "Git operation: $COMMAND"
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"git_operation\",\"command\":\"${COMMAND:0:200}\"}" >> "$METRICS_LOG" 2>/dev/null || true
    fi

    if [[ "$COMMAND" =~ (npm[[:space:]]+run[[:space:]]+build|npm[[:space:]]+test|npm[[:space:]]+run[[:space:]]+typecheck) ]]; then
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"build_test\",\"command\":\"${COMMAND:0:200}\"}" >> "$METRICS_LOG" 2>/dev/null || true
    fi
fi

exit 0
