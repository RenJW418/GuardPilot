# GuardPilot

[English](README.md) | [中文](README.zh-CN.md)

> Bitget AI Base Camp Hackathon S1 · Trading Infra
> Pre-trade risk gateway, paper-trading sandbox, and audit evidence layer for autonomous trading agents.

GuardPilot is **not a trading bot**. It sits between an autonomous trading Agent and any order-capable tool, evaluates every trade intent, and returns `ALLOW`, `WARN`, or `BLOCK` before execution. The final hackathon demo uses a **recorded Bitget public market data snapshot** with SHA-256 provenance, then runs paper-agent intents derived from that snapshot through paper trading and risk controls.

```text
Recorded Bitget public market snapshot
        ↓
Paper-agent intents derived from the snapshot
        ↓
GuardPilot risk gateway
        ↓
ALLOW / WARN -> paper execution + Bitget-compatible dry-run preview
BLOCK        -> no forwarding payload
        ↓
Dashboard + JSONL logs + JSON/HTML report + SHA-256 evidence manifest
```

## Data truthfulness and safety

- **Market data:** recorded from Bitget public market API, committed at `guardpilot/samples/market/bitget_btcusdt_1m.csv`.
- **Provenance:** `guardpilot/samples/market/bitget_btcusdt_1m.provenance.json` records endpoint, symbol, granularity, time range, row count, and SHA-256 hash.
- **Agent intents:** paper-agent signals derived from that real market snapshot, committed at `guardpilot/samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl`.
- **Execution:** paper trading and dry-run previews only. No private Bitget API key, no real funds, and no live exchange orders are used.
- **Claim boundary:** GuardPilot demonstrates risk infrastructure and auditability, not trading alpha or live profitability.

## Judge quickstart

From the repository root:

```bash
npm run setup
npm run judge:demo
```

Open:

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

`npm run setup` installs backend/frontend dependencies, regenerates replay evidence from the committed Bitget public snapshot, verifies the evidence manifest, and generates the Bitget-style dry-run trace. `npm run judge:demo` refreshes evidence and starts the API + dashboard.

## Verification commands

```bash
npm run test
npm run build
npm run replay
npm run evidence
npm run bitget:trace
```

Expected default replay proof:

| Metric | Result |
|---|---:|
| Market data source | Bitget public market API snapshot |
| Total paper-agent intents | 42 |
| Allowed / Warned / Blocked | 28 / 0 / 14 |
| Final equity with GuardPilot | 9976.93 USDT |
| Final equity without GuardPilot | 9828.07 USDT |
| Max drawdown with GuardPilot | 0.27% |
| Max drawdown without GuardPilot | 1.88% |
| Relative drawdown reduction | 85.68% |
| Audit records generated | 98 |

## Optional: refresh the public market snapshot

The default judge flow is offline/reproducible because the Bitget snapshot is committed. To refresh it before rerunning evidence:

```bash
npm run fetch:market
npm run build:signals
npm run replay
npm run evidence
```

If your network blocks direct access to Bitget, use the local proxy required by the project environment:

```bash
HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 npm run fetch:market
```

## API integration

### Generic Agent intent

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H 'Content-Type: application/json' \
  -d '{
    "timestamp":"2026-06-22T16:10:00Z",
    "agent_id":"paper_agent",
    "symbol":"BTCUSDT",
    "side":"BUY",
    "order_type":"MARKET",
    "quantity":0.005,
    "leverage":1,
    "confidence":0.82,
    "reason":"small paper order"
  }'
```

### Bitget Agent Hub / Playbook-style dry-run boundary

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

Decision contract:

| GuardPilot decision | Meaning |
|---|---|
| `ALLOW` | Generates a Bitget-compatible dry-run preview and paper/audit records |
| `WARN` | Generates a dry-run preview but should be reviewed or size-reduced |
| `BLOCK` | Returns `bitget_dry_run: null`; no order payload is forwarded |

`live_forwarding.enabled` is always `false` in this submission.

## Bitget ecosystem fit

| Bitget AI Agent surface | What it gives an Agent | Where GuardPilot fits |
|---|---|---|
| Agent Hub Tools | Spot, futures, account, and order-capable APIs | Pre-trade gate before order-like payloads |
| Skill Hub | Macro, sentiment, technical, on-chain, and news context | Preserves context in audit reasons and scores behavior risk |
| MCP Server | Claude / Cursor / Codex can call Bitget tools | Inserts `ALLOW` / `WARN` / `BLOCK` before order calls |
| Playbook | Natural-language strategy generation/backtesting/deployment | Paper-trading certification before live deployment |

GuardPilot is the **safety contract** before autonomous trading agents approach real execution.

## Important files

- `guardpilot/apps/api/` — FastAPI risk gateway and paper-trading engine
- `guardpilot/apps/web/` — React/Vite judge dashboard
- `guardpilot/samples/market/bitget_btcusdt_1m.csv` — recorded Bitget public market snapshot
- `guardpilot/samples/market/bitget_btcusdt_1m.provenance.json` — snapshot provenance and SHA-256
- `guardpilot/samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl` — derived paper-agent intent stream
- `guardpilot/samples/outputs/evidence_manifest.json` — replay evidence hashes and row counts
- `guardpilot/samples/outputs/sample_risk_report.json` — replay report
- `guardpilot/reports/demo_report.html` — HTML report
- `guardpilot/docs/demo_script.md` — final presentation script
- `guardpilot/docs/final_submission_packet.md` — submission packet

## License / limits

This repository is a hackathon prototype. It is paper-trading only by default, does not include private Bitget credentials, and must not be treated as financial advice. Any future live execution adapter should require explicit authorization, strict caps, symbol allowlists, monitoring, rollback controls, and independent security review.
