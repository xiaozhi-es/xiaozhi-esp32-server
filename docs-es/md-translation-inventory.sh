#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"
cd "$TARGET_DIR"

FILES="$(rg --files -g '*.md' || true)"

if [ -z "$FILES" ]; then
  echo "No se encontraron archivos .md en: $TARGET_DIR"
  exit 0
fi

echo "== Markdown files =="
printf '%s\n' "$FILES"
echo

echo "== Count =="
printf '%s\n' "$FILES" | wc -l | awk '{print $1 " files"}'
echo

echo "== Line counts =="
wc -l *.md
echo

echo "== Git status =="
git status --short -- *.md || true
