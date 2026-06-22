#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_LOG="$ROOT/guardpilot/.api-dev.log"
WEB_LOG="$ROOT/guardpilot/.web-dev.log"

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then kill "$API_PID" 2>/dev/null || true; fi
  if [[ -n "${WEB_PID:-}" ]]; then kill "$WEB_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

if lsof -ti:8000 >/dev/null 2>&1; then
  echo "Port 8000 is already in use. Stop the existing API process or run: lsof -ti:8000 | xargs kill"
  exit 1
fi

if lsof -ti:5173 >/dev/null 2>&1; then
  echo "Port 5173 is already in use. Stop the existing web process or run: lsof -ti:5173 | xargs kill"
  exit 1
fi

PYTHON_BIN="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON:-python3}"
fi

cd "$ROOT/guardpilot"
PYTHONPATH=apps/api "$PYTHON_BIN" -m uvicorn guardpilot.main:app --app-dir apps/api --reload --port 8000 > "$API_LOG" 2>&1 &
API_PID=$!

cd "$ROOT/guardpilot/apps/web"
npm run dev -- --host 0.0.0.0 > "$WEB_LOG" 2>&1 &
WEB_PID=$!

echo "GuardPilot dev servers starting..."
echo "API:       http://localhost:8000"
echo "Dashboard: http://localhost:5173"
echo "Logs:      guardpilot/.api-dev.log and guardpilot/.web-dev.log"
echo "Press Ctrl+C to stop both servers."

while true; do
  if ! kill -0 "$API_PID" 2>/dev/null; then
    echo "API server exited. See $API_LOG"
    exit 1
  fi
  if ! kill -0 "$WEB_PID" 2>/dev/null; then
    echo "Web server exited. See $WEB_LOG"
    exit 1
  fi
  sleep 1
done
