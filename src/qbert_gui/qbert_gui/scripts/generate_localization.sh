#!/usr/bin/env bash
set -e

TS_DIR="i18n"

# Compile .ts -> .qm
lrelease $TS_DIR/*.ts

echo "Translations compiled"