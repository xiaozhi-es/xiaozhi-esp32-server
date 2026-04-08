#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"
cd "$TARGET_DIR"

echo "== git diff --check =="
git diff --check -- *.md || true
echo

echo "== Remaining CJK characters =="
rg -n --glob '*.md' '[一-龥]' || true
echo

echo "== Diff stat =="
git diff --stat -- *.md || true
echo

echo "Revision recomendada:"
echo "- Si quedan cadenas CJK, revisa si son labels exactos de UI, logs o ejemplos literales."
echo "- Si git diff --check no muestra nada, no hay problemas formales detectados."
