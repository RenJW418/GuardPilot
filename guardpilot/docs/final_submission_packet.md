# GuardPilot Final Submission Packet

## Track

Bitget AI Base Camp Hackathon S1 · Trading Infra

## One-line Pitch

GuardPilot is a pre-trade risk gateway, paper trading evaluation sandbox, and audit evidence layer for autonomous trading Agents.

## Project Summary

Autonomous trading Agents can read market signals and submit orders 24/7, but before they reach execution tools, teams need a way to detect overtrading, revenge trading, leverage escalation, confidence mismatch, high-volatility chasing, and drawdown-limit violations.

GuardPilot sits between the Agent and the execution layer. Every trade intent is scored by behavior-aware risk rules, then returned as `ALLOW`, `WARN`, or `BLOCK`. Safe or warned intents are simulated in paper trading, dangerous intents are stopped before execution, and every decision is recorded as API logs, trade logs, risk events, JSON/HTML reports, and a SHA-256 evidence manifest.

This is a Trading Infra project, not a trading bot and not an alpha strategy. The submitted MVP is deterministic and paper-trading only so judges can reproduce the same evidence without exchange credentials.

## Bitget Ecosystem Fit

Bitget Agent Hub / Playbook / MCP-style tools give Agents market and execution capabilities. GuardPilot adds the missing pre-trade safety layer before those Agents reach order tools.

Current hackathon boundary:

```text
Agent Hub / Playbook signal
        ↓
GuardPilot intent normalization
        ↓
Risk Engine + Paper Trading Sandbox
        ↓
ALLOW / WARN / BLOCK
        ↓
Bitget-ready dry-run payload only if not blocked
```

`POST /api/v1/bitget/dry-run` demonstrates this boundary. `BLOCK` responses do not generate a forwarding payload. Live order forwarding is intentionally disabled for the submission.

## Public Links to Fill Before Submission

- GitHub repository: `https://github.com/RenJW418/GuardPilot`
- Demo video public URL: `TODO: add public video link`
- Public dashboard URL, optional: `TODO: add deployment link if available`
- X/Twitter post URL, optional: `TODO: add #BitgetHackathon @Bitget_AI post link`
- Bitget registration UID: `TODO: confirm the UID used during registration`
- Submission form: `https://forms.gle/GDQNx5TnCBvYuPin9`

## Judge Quickstart

From the repository root:

```bash
pip install -e guardpilot/apps/api
npm install --prefix guardpilot/apps/web
npm run replay
npm run evidence
npm run dev
```

Open:

- Dashboard: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## Expected Demo Proof

Default scenario: `guardpilot/samples/scenarios/btc_momentum_crash.json`

| Metric | Result |
|---|---:|
| Total Agent intents | 42 |
| Allowed / Warned / Blocked | 16 / 4 / 22 |
| Final equity with GuardPilot | 9980.91 USDT |
| Final equity without GuardPilot | 9930.81 USDT |
| Max drawdown with GuardPilot | 0.70% |
| Max drawdown without GuardPilot | 2.60% |
| Relative drawdown reduction | 73.11% |
| Audit records generated | 110 |
| Risk grade after guardrails | B |

## Evidence Artifacts

- Sample Agent inputs: `guardpilot/samples/agents/demo_momentum_signals.jsonl`
- API call log: `guardpilot/samples/outputs/sample_api_calls.jsonl`
- Paper trade log: `guardpilot/samples/outputs/sample_trade_log.jsonl`
- Risk event log: `guardpilot/samples/outputs/sample_risk_events.jsonl`
- Risk report JSON: `guardpilot/samples/outputs/sample_risk_report.json`
- Replay summary: `guardpilot/samples/outputs/sample_replay_summary.json`
- Evidence manifest: `guardpilot/samples/outputs/evidence_manifest.json`
- HTML report: `guardpilot/reports/demo_report.html`
- Demo video file: `guardpilot/reports/guardpilot-demo.mov`

## Suggested Submission Description

GuardPilot is a Trading Infra project for autonomous trading Agents. It is not another trading bot; it is a pre-trade risk gateway, paper trading evaluation sandbox, and audit evidence layer that sits between an Agent and execution tools.

Every trade intent is scored with behavior-aware risk rules such as leverage escalation, overtrading, revenge trading, volatility chasing, and confidence mismatch. GuardPilot returns `ALLOW`, `WARN`, or `BLOCK`, simulates safe intents in paper trading, and writes API logs, trade logs, risk events, JSON/HTML reports, and a SHA-256 evidence manifest.

In the deterministic demo replay, GuardPilot evaluates 42 Agent intents, allows 16, warns 4, blocks 22 high-risk actions, reduces simulated max drawdown from 2.60% to 0.70%, improves final simulated equity from 9930.81 USDT to 9980.91 USDT, and generates 110 audit records. The project is paper-trading only for hackathon reproducibility and does not claim live exchange execution or financial advice.

GuardPilot is designed to fit the Bitget ecosystem as a safety layer before Bitget Agent Hub / Playbook / MCP-powered Agents reach live execution tools.

## Truthfulness / Limitations

- The submitted evidence is deterministic paper trading, not live exchange execution.
- No real Bitget API keys, exchange funds, or live order forwarding are required by default.
- GuardPilot evaluates infrastructure safety and auditability, not trading alpha.
- Any future live execution should require explicit authorization, strict risk profiles, and production-grade monitoring.
