# GuardPilot

GuardPilot is a risk gateway and paper trading evaluation sandbox for autonomous trading agents.

It is built for the **Bitget AI Base Camp Hackathon S1 · Trading Infra** track. Instead of letting an Agent directly place orders, GuardPilot evaluates each trade intent with behavior-aware risk rules, simulates execution in a paper trading environment, records auditable logs, and generates reproducible risk reports.

> Paper trading only. This project is for hackathon evaluation and does not provide financial advice.
>
> **Data note:** the included evidence uses deterministic sample market data, sample Agent intents, and paper-trading simulation. It is not a live exchange execution record. The value is demonstrated through a reproducible A/B comparison between the same Agent stream without guardrails and with GuardPilot enabled.

## Judge Packet

| Item | Value |
|---|---|
| Track | Bitget AI Base Camp Hackathon S1 · Trading Infra |
| One-line pitch | Pre-trade risk gateway, paper trading evaluation sandbox, and audit evidence layer for autonomous trading Agents |
| Bitget ecosystem fit | Designed to sit before Bitget Agent Hub / Playbook / MCP-style order tools as a safety gate |
| Runtime boundary | Paper trading + Bitget-ready dry-run payloads only; no live exchange order forwarding by default |
| Verifiable record | API logs, trade logs, risk events, JSON/HTML report, and SHA-256 evidence manifest |

Expected default proof:

- 42 Agent intents evaluated.
- 16 allowed / 4 warned / 22 blocked.
- Final simulated equity: 9980.91 USDT with GuardPilot vs 9930.81 USDT without guard.
- Max drawdown: 0.70% with GuardPilot vs 2.60% without guard.
- 110 audit records generated.

## Judge Quickstart

If you are reviewing from the repository root (`20260620_bitget`), install dependencies once:

```bash
pip install -e guardpilot/apps/api
npm install --prefix guardpilot/apps/web
```

Then run:

```bash
npm run replay
npm run evidence
npm run dev
```

Then open:

- Dashboard: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Expected replay result for the default scenario:

| Metric | Result |
|---|---:|
| Total Agent intents | 42 |
| Allowed / Warned / Blocked | 16 / 4 / 22 |
| Final equity with GuardPilot | 9980.91 USDT |
| Final equity without GuardPilot | 9930.81 USDT |
| Max drawdown with GuardPilot | 0.70% |
| Max drawdown without GuardPilot | 2.60% |
| Risk grade after guardrails | B |

`POST /api/v1/replay` also writes the replayed trades, API calls, risk events, and `samples/outputs/evidence_manifest.json` so reviewers can verify SHA-256 hashes, JSONL row counts, and the full 42-intent audit trail after clicking **Run Replay**.

## Why GuardPilot

Autonomous trading agents can read signals and submit orders, but before deployment teams still need to answer:

- Is the agent overtrading?
- Is it increasing leverage after losses?
- Is it chasing volatile moves?
- Does it respect drawdown and exposure limits?
- Can its behavior be reproduced and audited?

GuardPilot provides the safety and evaluation layer every trading agent should pass before going live.

## Key Features

- **Risk gateway** for agent trade intents: `ALLOW`, `WARN`, or `BLOCK`.
- **Behavior-aware scoring**: leverage escalation, revenge trading, overtrading, confidence mismatch, volatility risk.
- **Paper trading engine**: market fills, fees, slippage, simplified long/short positions, PnL, equity curve, max drawdown.
- **Replayable scenarios**: deterministic sample market data + agent signals.
- **Auditable logs**: API call logs, trade logs, risk events, JSON reports.
- **Dashboard**: risk score, PnL, equity curve, trades, risk events, API logs.
- **Bitget ecosystem fit**: designed as a pre-trade guardrail for Agent Hub / Playbook / MCP powered agents.

## Architecture

```text
+--------------------+
| Demo Trading Agent |
+---------+----------+
          | trade intent JSON
          v
+---------+----------+
| GuardPilot API     |
+---------+----------+
          | 
          +------------------------------+
          |                              |
          v                              v
+---------+----------+        +----------+---------+
| Risk Engine        |        | Paper Trading      |
| rules + score      |        | fills + PnL        |
+---------+----------+        +----------+---------+
          |                              |
          +---------------+--------------+
                          v
+-------------------------+-------------------------+
| SQLite / JSONL logs / reports                     |
+-------------------------+-------------------------+
                          v
+-------------------------+-------------------------+
| Web Dashboard                                     |
+---------------------------------------------------+
```

## Quick Start

### 1. Run a deterministic replay

No external API key is required.

```bash
cd guardpilot
python3 scripts/replay.py --scenario samples/scenarios/btc_momentum_crash.json
```

Expected output includes:

```text
Replay completed
Total intents: 42
Allowed: ...
Warned: ...
Blocked: ...
Report: reports/demo_report.json
```

Generated files:

- `samples/outputs/sample_trade_log.jsonl`
- `samples/outputs/sample_api_calls.jsonl`
- `samples/outputs/sample_risk_report.json`
- `samples/outputs/sample_replay_summary.json`
- `reports/demo_report.json`
- `reports/demo_report.html`

### 2. Run backend API

```bash
cd guardpilot
python3 -m venv .venv
source .venv/bin/activate
pip install -e apps/api
uvicorn guardpilot.main:app --app-dir apps/api --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

### 3. Submit an agent trade intent

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H 'Content-Type: application/json' \
  -d '{
    "timestamp":"2026-06-20T10:08:00Z",
    "agent_id":"demo_momentum_agent",
    "symbol":"BTCUSDT",
    "side":"BUY",
    "order_type":"MARKET",
    "quantity":0.08,
    "leverage":8,
    "confidence":0.61,
    "reason":"Trying to recover previous losses after breakout failure"
  }'
```

Response example:

```json
{
  "intent_id": "int_000001",
  "decision": "BLOCK",
  "risk_score": 92,
  "risk_level": "critical",
  "simulated_order_id": null,
  "account_equity_after": 9954.13
}
```

### 4. Run web dashboard

```bash
cd guardpilot/apps/web
npm install
npm run dev
```

Open `http://localhost:5173`.

The frontend reads the API from `VITE_API_BASE_URL` and defaults to `http://localhost:8000`.

## Replay Scenario

The main scenario is `samples/scenarios/btc_momentum_crash.json`:

- 42 demo trade intents.
- Includes normal momentum trades and deliberately risky behavior.
- GuardPilot should allow safe trades, warn on elevated risk, and block dangerous trades.
- The report compares **without guard** vs **with GuardPilot**.

## Risk Scoring

Each trade intent is evaluated by configurable rule families:

| Rule | Purpose |
|---|---|
| Max leverage | Prevents high leverage orders. |
| Max notional | Prevents oversized single trades. |
| Symbol exposure | Limits concentration in one symbol. |
| Daily loss | Blocks when drawdown exceeds limit. |
| Consecutive losses | Detects unstable trading periods. |
| Overtrading | Detects too many trades in a short window. |
| Revenge trading | Detects increased size/leverage after losses. |
| Volatility risk | Blocks chasing extreme candles. |
| Confidence mismatch | Flags low-confidence oversized trades. |

Scores map to decisions:

- `0-60`: `ALLOW`
- `61-80`: `WARN` and still paper-trade
- `81-100`: `BLOCK` and do not trade

## API Reference

Core endpoints:

- `GET /health`
- `POST /api/v1/intents`
- `GET /api/v1/agents`
- `GET /api/v1/agents/{agent_id}`
- `GET /api/v1/trades`
- `GET /api/v1/risk-events`
- `POST /api/v1/replay`
- `GET /api/v1/reports/{report_id}`
- `GET /api/v1/api-logs`

See `docs/api_reference.md` for details.

## Reproducible Evidence for Submission

Trading Infra requires verifiable usage records. GuardPilot provides:

- API call log: `samples/outputs/sample_api_calls.jsonl`
- Sample input signals: `samples/agents/demo_momentum_signals.jsonl`
- Sample output trade log: `samples/outputs/sample_trade_log.jsonl`
- Sample risk report: `samples/outputs/sample_risk_report.json`
- Replay summary: `samples/outputs/sample_replay_summary.json`

## Bitget Ecosystem Fit

GuardPilot can sit between any Bitget Agent Hub / Playbook / MCP powered agent and the execution layer:

1. Agent generates trade intent.
2. GuardPilot scores risk and produces an audit trail.
3. Safe intents can be forwarded to Bitget Agent Hub tools or Playbook deployment.
4. Dangerous intents are blocked before reaching real trading APIs.

The current MVP uses deterministic paper trading so judges can run it without exchange credentials.

### Bitget Agent Hub / Playbook style payload

A sample Agent Hub / Playbook-style signal is included at:

- `samples/agents/bitget_agenthub_payload.json`

Submit it through GuardPilot before real execution:

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H 'Content-Type: application/json' \
  --data @samples/agents/bitget_agenthub_payload.json
```

In a live Bitget setup, GuardPilot acts as the pre-trade gate. The dry-run endpoint now evaluates risk first; only `ALLOW` or `WARN` returns a Bitget-ready dry-run payload, while `BLOCK` returns `bitget_dry_run: null` and no forwarding payload.

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @samples/agents/bitget_agenthub_payload.json
```

```text
Agent Hub / Playbook signal -> GuardPilot risk score -> ALLOW/WARN/BLOCK -> optional Bitget order tool forwarding
```

For hackathon reproducibility, live order forwarding is intentionally opt-in and the submitted evidence uses paper trading. The included `BitgetAdapter` still produces a Bitget-ready dry-run execution payload so the execution boundary is explicit and reviewable.

## Demo Video Script

See `docs/demo_script.md` for a 3-minute video outline.

Submission helpers:

- `docs/final_submission_packet.md` — one-page packet for the hackathon submission form.
- `docs/bitget_integration_boundary.md` — Bitget Agent Hub / Playbook dry-run safety boundary.
- `docs/submission_checklist.md` — final checklist for public links, UID, evidence, and commands.

To record locally on macOS from the repository root:

```bash
npm run record:demo
```

Detailed recording instructions are in `docs/recording_guide.md`.

## Roadmap

- Live Bitget market data adapter.
- Optional forwarding to Bitget Agent Hub order tools.
- Multi-agent leaderboard.
- LLM-based natural language risk explanation.
- Web-hosted demo with preloaded replay results.

## License

MIT
