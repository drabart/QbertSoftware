#!/usr/bin/env bash
set -e

# Paths
TS_DIR="i18n"
UI_DIR="ui"
PY_FILES="main.py screens/*.py core/*.py"

# Update .ts files from source
# Note: pylupdate6 needs individual files, so we use find
pylupdate6 main.py $(find screens -name "*.py" 2>/dev/null || true) $(find core -name "*.py" 2>/dev/null || true) $(find ui -name "*.ui" 2>/dev/null || true) -ts $TS_DIR/*.ts

echo "Text extracted from Python files and UI files"
