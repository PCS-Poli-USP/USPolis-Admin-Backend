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

if ! "${PYTHON_CMD[@]}" -m playwright --version >/dev/null 2>&1; then
  echo "[ERROR] Playwright Python package is not available in this environment." >&2
  echo "        Run: poetry install" >&2
  exit 1
fi

# Ask the currently installed playwright package which browser revisions it
# expects, then check for those *exact* install locations. Checking for any
# chromium-*/chromium_headless_shell-* folder (regardless of revision) would
# wrongly report a stale browser build as up to date after a playwright
# version bump.
expected_install_locations() {
  PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_PATH" "${PYTHON_CMD[@]}" -m playwright install --dry-run chromium 2>/dev/null \
    | sed -n 's/^\s*Install location:\s*//p'
}

has_expected_browsers() {
  local locations
  locations="$(expected_install_locations)"
  [[ -n "$locations" ]] || return 1
  while IFS= read -r dir; do
    [[ -n "$dir" ]] || continue
    [[ -f "$dir/INSTALLATION_COMPLETE" ]] || return 1
  done <<< "$locations"
  return 0
}

mkdir -p "$BROWSERS_PATH"

if has_expected_browsers; then
  echo "[SKIP] Playwright Chromium already installed in: $BROWSERS_PATH"
  exit 0
fi

echo "[INFO] Removing existing browsers in: $BROWSERS_PATH (frees disk before downloading new build)"
PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_PATH" "${PYTHON_CMD[@]}" -m playwright uninstall --all || true

echo "[INFO] Installing Playwright Chromium in: $BROWSERS_PATH"
PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_PATH" "${PYTHON_CMD[@]}" -m playwright install chromium

if has_expected_browsers; then
  echo "[OK] Playwright Chromium installed successfully."
else
  echo "[ERROR] Installation finished, but Chromium executable was not found." >&2
  exit 1
fi

echo "[INFO] Installed browsers are located in: $BROWSERS_PATH"
echo "[INFO] PLAYWRIGHT_BROWSERS_PATH=$BROWSERS_PATH"
