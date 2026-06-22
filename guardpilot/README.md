# GuardPilot

[English](README.md) | [中文](README.zh-CN.md)

> Bitget AI Base Camp Hackathon S1 · Trading Infra
> Local pre-trade risk sidecar, paper-trading sandbox, and visualization dashboard for autonomous trading agents.

GuardPilot sits before Agent Hub / Playbook / MCP-style order tools and returns `ALLOW`, `WARN`, or `BLOCK` before any order-capable payload is produced. The submitted release is **paper-trading and dry-run only** and uses a **recorded Bitget public market snapshot** for the default replay.

## 1. One-line pitch

GuardPilot is a local **pre-trade risk sidecar** for Bitget AI Agent users. It turns autonomous trading intents into risk-scored decisions, paper-trading outcomes, and hash-verifiable audit evidence.

```text
Bitget public market snapshot
        ↓
Paper-agent intents derived from the snapshot
        ↓
GuardPilot local risk sidecar
        ↓
ALLOW / WARN -> paper execution + Bitget-compatible dry-run preview
BLOCK        -> no forwarding payload
        ↓
Visualization dashboard + audit logs + replay evidence
```

No private Bitget API key, real exchange funds, or live order forwarding is required by default.

## 2. Data truthfulness

Default replay data:

| Layer | Artifact |
|---|---|
| Market data | `samples/market/bitget_btcusdt_1m.csv` |
| Market provenance | `samples/market/bitget_btcusdt_1m.provenance.json` |
| Paper-agent intents | `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl` |
| Signal provenance | `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.provenance.json` |
| Evidence manifest | `samples/outputs/evidence_manifest.json` |

The market snapshot provenance records the Bitget public endpoint, symbol, granularity, exchange time range, row count, and SHA-256 hash. Agent intents are deterministic paper-agent decisions derived from that real market snapshot; they are not claimed as a real AgentHub export or live exchange record.

## 3. One-command sidecar setup

From the repository root:

```bash
npm run bitget:sidecar
```

This command installs dependencies if needed, regenerates replay/evidence, writes sidecar config files, generates the Bitget-style dry-run trace, and starts the API + dashboard.

Open:

- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Sidecar endpoint: `POST http://localhost:8000/api/v1/bitget/dry-run`

## 4. Judge quickstart

```bash
npm run setup
npm run judge:demo
```

Verification:

```bash
npm run test
npm run build
npm run replay
npm run evidence
npm run bitget:trace
```

Default replay proof:

| Metric | Result |
|---|---:|
| Market data source | Bitget public market API snapshot |
| Total paper-agent intents | 42 |
| Allowed / Warned / Blocked | 28 / 0 / 14 |
| Final equity with GuardPilot | 9976.93 USDT |
| Final equity without GuardPilot | 9828.07 USDT |
| Max drawdown with GuardPilot | 0.27% |
| Max drawdown without GuardPilot | 1.88% |
| Audit records | 98 |

## 5. Bitget dry-run contract

Before your Bitget Agent Hub / Playbook / MCP-style agent calls any order-capable tool, call GuardPilot first:

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

Decision contract:

| GuardPilot decision | Meaning |
|---|---|
| `ALLOW` | Produces a Bitget-compatible dry-run preview |
| `WARN` | Produces a preview but should be reviewed or size-reduced |
| `BLOCK` | Returns `bitget_dry_run: null`; do not call order tools |

`live_forwarding.enabled` is always `false` for the hackathon submission.

Credential-free trace:

```bash
npm run bitget:trace
```

Generated artifact:

- `guardpilot/samples/outputs/bitget_agenthub_dry_run_response.json`

It includes a risky payload that is blocked and a conservative payload that receives a dry-run preview.

## 6. Visualization dashboard

The dashboard shows:

- Data truthfulness card for Bitget public snapshot provenance
- Risk cockpit and decision rail
- Before/after GuardPilot replay comparison
- Snapshot replay controls
- Visual analytics for decision mix, risk trend, rules, and latency
- Audit trail: API logs, trade logs, risk events, evidence artifacts
- Bitget Agent Hub / Playbook-style dry-run boundary

## 7. Important files

- `apps/api/` — FastAPI risk gateway
- `apps/web/` — React/Vite visualization dashboard
- `samples/market/bitget_btcusdt_1m.csv` — recorded Bitget public market snapshot
- `samples/market/bitget_btcusdt_1m.provenance.json` — market data provenance
- `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl` — derived paper-agent inputs
- `samples/outputs/evidence_manifest.json` — SHA-256 evidence manifest
- `samples/outputs/bitget_agenthub_dry_run_response.json` — dry-run contract trace
- `docs/bitget_integration_boundary.md` — Bitget integration boundary
- `docs/one_command_demo.md` — setup and demo guide
- `docs/final_submission_packet.md` — submission packet

## 8. Truthfulness and limits

- Real market data is a recorded Bitget public market snapshot, not private account data.
- Agent intents are paper-agent signals derived from the snapshot, not a live AgentHub export.
- Paper trading and dry-run previews only; no live exchange execution records are claimed.
- No real Bitget API key is required by default.
- A `BLOCK` decision never produces a Bitget forwarding payload.
- Future live integration must require explicit authorization, strict risk profiles, secret management, monitoring, rollback controls, and independent security review.
