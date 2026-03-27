#!/bin/bash
# Memory Refresh Reminder Hook
#
# Checks if CLAUDE.md files need review based on last modification date.
# Runs on Stop event to remind about memory maintenance.
#
# Exit codes:
#   0 - No reminder needed
#   0 - (with stdout) Shows reminder

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CLAUDE_MD="${PROJECT_ROOT}/CLAUDE.md"
GLOBAL_CLAUDE_MD="${HOME}/.claude/CLAUDE.md"
REMINDER_INTERVAL_DAYS=90  # Quarterly review
LAST_REMINDER_FILE="${PROJECT_ROOT}/.claude/hooks/.last_memory_reminder"

NOW=$(date +%s)

# Check if we've shown a reminder recently (within 7 days)
if [[ -f "$LAST_REMINDER_FILE" ]]; then
    LAST_REMINDER=$(cat "$LAST_REMINDER_FILE")
    DAYS_SINCE_REMINDER=$(( (NOW - LAST_REMINDER) / 86400 ))
    if [[ $DAYS_SINCE_REMINDER -lt 7 ]]; then
        exit 0
    fi
fi

check_file_age() {
    local file="$1"
    local name="$2"

    if [[ ! -f "$file" ]]; then
        return
    fi

    if [[ "$(uname)" == "Darwin" ]]; then
        FILE_MTIME=$(stat -f %m "$file")
    else
        FILE_MTIME=$(stat -c %Y "$file")
    fi

    DAYS_OLD=$(( (NOW - FILE_MTIME) / 86400 ))

    if [[ $DAYS_OLD -gt $REMINDER_INTERVAL_DAYS ]]; then
        echo "reminder:$name:$DAYS_OLD"
    fi
}

PROJECT_CHECK=$(check_file_age "$CLAUDE_MD" "Project CLAUDE.md")
GLOBAL_CHECK=$(check_file_age "$GLOBAL_CLAUDE_MD" "Global CLAUDE.md")

if [[ -n "$PROJECT_CHECK" || -n "$GLOBAL_CHECK" ]]; then
    echo ""
    echo "======================================"
    echo "  MEMORY MAINTENANCE REMINDER"
    echo "======================================"

    if [[ -n "$PROJECT_CHECK" ]]; then
        DAYS=$(echo "$PROJECT_CHECK" | cut -d: -f3)
        echo "Project CLAUDE.md hasn't been updated in $DAYS days."
    fi

    if [[ -n "$GLOBAL_CHECK" ]]; then
        DAYS=$(echo "$GLOBAL_CHECK" | cut -d: -f3)
        echo "Global CLAUDE.md hasn't been updated in $DAYS days."
    fi

    echo ""
    echo "Consider reviewing and updating your CLAUDE.md files."
    echo "======================================"
    echo ""

    echo "$NOW" > "$LAST_REMINDER_FILE"
fi

exit 0
