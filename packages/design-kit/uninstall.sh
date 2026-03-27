#!/usr/bin/env bash
set -euo pipefail

# Claude Design Kit Uninstaller
# Convenience wrapper for install.sh --uninstall

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODE="project"
for arg in "$@"; do
    case $arg in
        --global|-g) MODE="global" ;;
    esac
done

if [ "$MODE" = "global" ]; then
    exec "$SCRIPT_DIR/install.sh" --global --uninstall
else
    exec "$SCRIPT_DIR/install.sh" --project --uninstall
fi
