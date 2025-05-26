#!/bin/bash

SKIP_FOLDERS=(-path ./.venv -o -path ./build -o -path ./dist -o -path ./ruff_cache -o -path ./pytest_cache -o -name "*/__pycache__")

mapfile -t FILES < <(find . \( "${SKIP_FOLDERS[@]}" \) -prune -false -o -type f -name "*.py" -print)

LINES_COUNT=0
for file in "${FILES[@]}"; do
    lines_in_file=$(wc -l < "$file")  # importante: usar '<' para pegar só o número
    ((LINES_COUNT += lines_in_file))
done


echo "Total lines of code: $LINES_COUNT"