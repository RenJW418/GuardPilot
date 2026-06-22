#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d guardpilot/apps/web/node_modules || ! -x .venv/bin/python ]]; then
  echo "==> First-time setup for GuardPilot sidecar"
  npm run setup
fi

echo "==> Generating official Bitget AI Agent dry-run contract trace"
npm run bitget:trace

OUT_DIR="$ROOT/guardpilot/reports"
mkdir -p "$OUT_DIR"

cat > "$OUT_DIR/bitget-agent-sidecar.env" <<'ENV'
# GuardPilot sidecar endpoint for Bitget Agent Hub / Playbook / MCP agents
GUARDPILOT_RISK_GATE_URL=http://localhost:8000/api/v1/bitget/dry-run
GUARDPILOT_DASHBOARD_URL=http://localhost:5173
GUARDPILOT_POLICY=ALLOW_WARN_DRY_RUN_BLOCK_STOP
# Keep live order forwarding disabled unless your own production deployment explicitly enables it.
GUARDPILOT_LIVE_FORWARDING=disabled
ENV

cat > "$OUT_DIR/bitget-agent-sidecar.json" <<'JSON'
{
  "name": "guardpilot-bitget-agent-sidecar",
  "riskGateUrl": "http://localhost:8000/api/v1/bitget/dry-run",
  "dashboardUrl": "http://localhost:5173",
  "policy": {
    "ALLOW": "use bitget_dry_run.execution_payload for dry-run or downstream review",
    "WARN": "use bitget_dry_run.execution_payload only after review or size reduction",
    "BLOCK": "do not call Bitget order-capable tools; bitget_dry_run is null"
  },
  "officialBitgetSurfaces": [
    "Agent Hub Tools",
    "Skill Hub signal context",
    "Bitget Playbook strategy output",
    "MCP Server order-tool boundary"
  ],
  "liveForwardingDefault": false
}
JSON

cat <<MSG
==> GuardPilot sidecar config written
- $OUT_DIR/bitget-agent-sidecar.env
- $OUT_DIR/bitget-agent-sidecar.json

Use this endpoint before any Bitget Agent Hub / Playbook / MCP order-capable call:
  POST http://localhost:8000/api/v1/bitget/dry-run

Dashboard:
  http://localhost:5173

Starting GuardPilot API + visualization dashboard now...
Press Ctrl+C to stop both servers.
MSG

exec npm run dev
