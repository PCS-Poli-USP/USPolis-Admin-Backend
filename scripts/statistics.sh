#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SKIP_FOLDERS=(
    -path "$REPO_ROOT/.playwright-browsers" -o
    -path "$REPO_ROOT/.pytest_cache" -o
    -path "$REPO_ROOT/.ruff_cache" -o
    -path "$REPO_ROOT/.venv" -o
    -path "$REPO_ROOT/build" -o
    -path "$REPO_ROOT/dist" -o
    -path "$REPO_ROOT/.mypy_cache" -o
    -path "$REPO_ROOT/.pylint_cache" -o
    -name "__pycache__"
)

mapfile -t FILES < <(find "$REPO_ROOT" \( "${SKIP_FOLDERS[@]}" \) -prune -false -o -type f -name "*.py" -print)

LINES_COUNT=0
for file in "${FILES[@]}"; do
    lines_in_file=$(wc -l < "$file")  # importante: usar '<' para pegar só o número
    ((LINES_COUNT += lines_in_file))
done


echo "Total lines of code: $LINES_COUNT"