#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

if [[ ! -d guardpilot/apps/web/node_modules ]]; then
  echo "Web dependencies are missing. Running npm run setup first..."
  npm run setup
fi

if ! PYTHONPATH=guardpilot/apps/api "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import fastapi, uvicorn, pydantic
PY
then
  echo "API dependencies are missing. Running npm run setup first..."
  npm run setup
fi

echo "==> Refreshing Bitget snapshot replay evidence before the judge demo"
npm run replay
npm run evidence
npm run bitget:trace

echo "==> Launching GuardPilot API + dashboard"
echo "Dashboard: http://localhost:5173"
echo "API docs:  http://localhost:8000/docs"
echo "Python:    $PYTHON_BIN"
echo "Bitget dry-run endpoint: POST http://localhost:8000/api/v1/bitget/dry-run"
echo "Sample Agent Hub payload: guardpilot/samples/agents/bitget_agenthub_payload.json"
exec npm run dev
