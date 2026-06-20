#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT/guardpilot/reports"
OUT_FILE="$OUT_DIR/guardpilot-demo.mov"
API_LOG="$ROOT/guardpilot/.api-demo.log"
WEB_LOG="$ROOT/guardpilot/.web-demo.log"
DURATION="${1:-180}"

mkdir -p "$OUT_DIR"

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then kill "$API_PID" 2>/dev/null || true; fi
  if [[ -n "${WEB_PID:-}" ]]; then kill "$WEB_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

if lsof -ti:8000 >/dev/null 2>&1; then
  echo "Port 8000 is already in use. Stop it first: lsof -ti:8000 | xargs kill"
  exit 1
fi
if lsof -ti:5173 >/dev/null 2>&1; then
  echo "Port 5173 is already in use. Stop it first: lsof -ti:5173 | xargs kill"
  exit 1
fi

cd "$ROOT/guardpilot"
PYTHONPATH=apps/api python3 -m uvicorn guardpilot.main:app --app-dir apps/api --reload --port 8000 > "$API_LOG" 2>&1 &
API_PID=$!

cd "$ROOT/guardpilot/apps/web"
npm run dev -- --host 0.0.0.0 > "$WEB_LOG" 2>&1 &
WEB_PID=$!

for i in $(seq 1 40); do
  if curl -sf http://localhost:8000/health >/dev/null && curl -sf -I http://localhost:5173/ >/dev/null; then
    break
  fi
  sleep 0.5
  if [[ "$i" == "40" ]]; then
    echo "Dev servers did not become ready. Check $API_LOG and $WEB_LOG"
    exit 1
  fi
done

cd "$ROOT"
npm run replay >/tmp/guardpilot-demo-replay.log
open "http://localhost:5173"
sleep 2

cat <<MSG
Recording GuardPilot demo for ${DURATION}s...
Output: $OUT_FILE
Suggested flow while recording:
1. Show Dashboard metric cards.
2. Click Run Replay.
3. Scroll through Equity Curve, Trade Timeline, Risk Events, API Call Audit Log.
4. Open http://localhost:8000/docs if time allows.
MSG

rm -f "$OUT_FILE"
screencapture -v -V "$DURATION" -C -k -x "$OUT_FILE"
ls -lh "$OUT_FILE"
echo "Demo recording saved: $OUT_FILE"
