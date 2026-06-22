#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT/.venv"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3.11+ or set PYTHON_BIN=/path/to/python3.11."
  exit 1
fi

PYTHON_VERSION="$($PYTHON_BIN - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
if ! "$PYTHON_BIN" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
then
  echo "Python 3.11+ is required; $PYTHON_BIN is Python $PYTHON_VERSION."
  echo "Rerun with: PYTHON_BIN=/path/to/python3.11 npm run setup"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required. Install Node.js 20+ and rerun this script."
  exit 1
fi

echo "==> Creating local Python virtualenv at .venv"
"$PYTHON_BIN" -m venv "$VENV_DIR"
PY="$VENV_DIR/bin/python"

echo "==> Installing GuardPilot API dependencies"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -e guardpilot/apps/api
"$PY" -m pip install 'pytest>=8.0.0'

echo "==> Installing GuardPilot web dependencies"
npm install --prefix guardpilot/apps/web

echo "==> Regenerating replay evidence from committed Bitget public market snapshot"
npm run replay

echo "==> Verifying evidence manifest"
npm run evidence

echo "==> Generating Bitget official AI Agent dry-run evidence"
npm run bitget:trace

echo "==> Setup complete"
echo "Python venv: $VENV_DIR"
echo "Run the full demo with: npm run judge:demo"
echo "Or start API + dashboard with: npm run dev"
echo "Dashboard: http://localhost:5173"
echo "API docs:  http://localhost:8000/docs"
