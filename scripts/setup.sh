#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Automated Setup: AGY Thesis Starter Kit (PKN STAN) ==="

if command -v python3 >/dev/null 2>&1; then
  PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PY_CMD="python"
else
  echo "[ERROR] Python 3.10+ is not installed or not in PATH."
  exit 1
fi

echo "1. Installing required Python packages from requirements.txt..."
"$PY_CMD" -m pip install --upgrade pip
"$PY_CMD" -m pip install -r "$ROOT_DIR/requirements.txt"

if [ ! -f "$ROOT_DIR/thesis_config.json" ]; then
  cp "$ROOT_DIR/thesis_config.example.json" "$ROOT_DIR/thesis_config.json"
  echo "2. Created starter thesis_config.json from template."
else
  echo "2. thesis_config.json already exists (skipped)."
fi

echo "3. Running final readiness verification..."
"$PY_CMD" "$ROOT_DIR/scripts/setup_check.py"
