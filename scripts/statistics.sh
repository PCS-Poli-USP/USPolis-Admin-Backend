#!/bin/bash

SKIP_FOLDERS=(-name "__pycache__" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name ".pytest_cache" -o -name ".venv")

count_lines() {
    local dir="$1"
    mapfile -t files < <(find "$dir" \( "${SKIP_FOLDERS[@]}" \) -prune -o -name "*.py" -print)
    local lines_count=0
    for file in "${files[@]}"; do
        lines_in_file=$(wc -l < "$file")  # importante: usar '<' para pegar só o número
        ((lines_count += lines_in_file))
    done
    echo "$lines_count"
}

SERVER_LINES=$(count_lines ./server)
TESTS_LINES=$(count_lines ./tests)

echo "Server lines of code: $SERVER_LINES"
echo "Tests lines of code: $TESTS_LINES"
echo "Total lines of code: $((SERVER_LINES + TESTS_LINES))"