#!/usr/bin/env bash
set -e

# Paths
TS_DIR="i18n"
UI_DIR="ui"
PY_FILES="main.py"

# Update .ts files from source
pylupdate6 $PY_FILES $UI_DIR/*.ui -ts $TS_DIR/*.ts

echo "Text extracted"
