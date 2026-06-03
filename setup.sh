#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] Running setup steps..."
bash "$SCRIPT_DIR/scripts/install_playwright_chromium.sh"
echo "[OK] Setup finished."
