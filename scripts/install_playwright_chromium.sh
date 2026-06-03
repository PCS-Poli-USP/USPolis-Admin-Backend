#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$REPO_ROOT/.playwright-browsers}"

if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_CMD=("$REPO_ROOT/.venv/bin/python")
elif command -v poetry >/dev/null 2>&1; then
  PYTHON_CMD=(poetry run python)
else
  echo "[ERROR] Could not find .venv python or poetry in PATH." >&2
  exit 1
fi

has_chromium() {
  find "$BROWSERS_PATH" -type f \
    \( -path "*/chromium-*/chrome-linux64/chrome" \
    -o -path "*/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium" \
    -o -path "*/chromium-*/chrome-win/chrome.exe" \
    -o -path "*/chromium-*/chrome-win64/chrome.exe" \) \
    -print -quit 2>/dev/null | grep -q .
}

has_headless_shell() {
  find "$BROWSERS_PATH" -type f \
    \( -path "*/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell" \
    -o -path "*/chromium_headless_shell-*/chrome-headless-shell-mac/chrome-headless-shell" \
    -o -path "*/chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe" \) \
    -print -quit 2>/dev/null | grep -q .
}

mkdir -p "$BROWSERS_PATH"

if has_chromium && has_headless_shell; then
  echo "[SKIP] Playwright Chromium already installed in: $BROWSERS_PATH"
  exit 0
fi

if ! "${PYTHON_CMD[@]}" -m playwright --version >/dev/null 2>&1; then
  echo "[ERROR] Playwright Python package is not available in this environment." >&2
  echo "        Run: poetry install" >&2
  exit 1
fi

echo "[INFO] Installing Playwright Chromium in: $BROWSERS_PATH"
PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_PATH" "${PYTHON_CMD[@]}" -m playwright install chromium

if has_chromium && has_headless_shell; then
  echo "[OK] Playwright Chromium installed successfully."
else
  echo "[ERROR] Installation finished, but Chromium executable was not found." >&2
  exit 1
fi

echo "[INFO] Installed browsers are located in: $BROWSERS_PATH"
echo "[INFO] PLAYWRIGHT_BROWSERS_PATH=$BROWSERS_PATH"
