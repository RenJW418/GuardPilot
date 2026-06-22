# GuardPilot Final Submission Packet

## Track

Bitget AI Base Camp Hackathon S1 · Trading Infra

## One-line Pitch

GuardPilot is a pre-trade risk gateway, paper trading evaluation sandbox, and audit evidence layer for autonomous trading Agents.

## Project Summary

Autonomous trading Agents can read market signals and submit orders 24/7, but before they reach execution tools, teams need a way to detect overtrading, revenge trading, leverage escalation, confidence mismatch, high-volatility chasing, and drawdown-limit violations.

GuardPilot sits between the Agent and the execution layer. Every trade intent is scored by behavior-aware risk rules, then returned as `ALLOW`, `WARN`, or `BLOCK`. Safe or warned intents are simulated in paper trading, dangerous intents are stopped before execution, and every decision is recorded as API logs, trade logs, risk events, JSON/HTML reports, and a SHA-256 evidence manifest.

The submitted release uses a recorded Bitget public-market snapshot with provenance metadata. It is paper-trading and dry-run only so judges can reproduce the same evidence without private exchange credentials or real funds.

## Bitget Ecosystem Fit

Bitget Agent Hub / Playbook / MCP-style tools give Agents market and execution capabilities. GuardPilot adds the missing pre-trade safety layer before those Agents reach order tools.

| Bitget AI Agent surface | GuardPilot integration |
|---|---|
| Agent Hub Tools | gates order-capable API/tool calls before forwarding |
| Skill Hub | preserves macro/sentiment/technical/on-chain/news signal context in audit reasons |
| MCP Server | places ALLOW/WARN/BLOCK before Claude/Cursor/Codex can trigger order tools |
| Playbook | evaluates strategy-style outputs through paper trading before live deployment |

For Bitget, GuardPilot can become the pre-launch certification and audit layer for AI trading agents: safer agent onboarding, fewer unsafe automated orders, and reviewable evidence before any strategy touches live execution.

Current hackathon boundary:

```text
Recorded Bitget public market snapshot
        ↓
Agent Hub / Playbook-style or paper-agent signal
        ↓
GuardPilot intent normalization
        ↓
Risk Engine + Paper Trading Sandbox
        ↓
ALLOW / WARN / BLOCK
        ↓
Bitget-compatible dry-run preview only if not blocked
```

`POST /api/v1/bitget/dry-run` demonstrates this boundary. `BLOCK` responses do not generate a forwarding payload. Live order forwarding is intentionally disabled for the submission.

## Public Links / Submission-Time Fields

- GitHub repository: `https://github.com/RenJW418/GuardPilot`
- Demo video public URL: add after uploading the final recording
- Public dashboard URL, optional: local reproducible dashboard is supported; deployment is optional
- X/Twitter post URL, optional: add if publishing a `#BitgetHackathon @Bitget_AI` post
- Bitget registration UID: fill manually in the form if required; not committed here
- Submission form: `https://forms.gle/GDQNx5TnCBvYuPin9`
- Final commit hash or release tag: fill after final push

## Judge Quickstart

From the repository root:

```bash
npm run setup
npm run judge:demo
```

Manual equivalent:

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
| Market data source | Bitget public market API snapshot |
| Total paper-agent intents | 42 |
| Allowed / Warned / Blocked | 28 / 0 / 14 |
| Final equity with GuardPilot | 9976.93 USDT |
| Final equity without GuardPilot | 9828.07 USDT |
| Max drawdown with GuardPilot | 0.27% |
| Max drawdown without GuardPilot | 1.88% |
| Relative drawdown reduction | 85.68% |
| Audit records generated | 98 |
| Risk grade after guardrails | B |

## Evidence Artifacts

- Market snapshot: `guardpilot/samples/market/bitget_btcusdt_1m.csv`
- Market provenance: `guardpilot/samples/market/bitget_btcusdt_1m.provenance.json`
- Paper-agent inputs: `guardpilot/samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl`
- Signal provenance: `guardpilot/samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.provenance.json`
- API call log: `guardpilot/samples/outputs/sample_api_calls.jsonl`
- Paper trade log: `guardpilot/samples/outputs/sample_trade_log.jsonl`
- Risk event log: `guardpilot/samples/outputs/sample_risk_events.jsonl`
- Risk report JSON: `guardpilot/samples/outputs/sample_risk_report.json`
- Replay summary: `guardpilot/samples/outputs/sample_replay_summary.json`
- Evidence manifest: `guardpilot/samples/outputs/evidence_manifest.json`
- Bitget-style dry-run trace: `guardpilot/samples/outputs/bitget_agenthub_dry_run_response.json`
- Agent Hub / Playbook-style risky payload: `guardpilot/samples/agents/bitget_agenthub_payload.json`
- Agent Hub / Playbook-style safe payload: `guardpilot/samples/agents/bitget_agenthub_safe_payload.json`
- HTML report: `guardpilot/reports/demo_report.html`
- Demo video file, if recorded: `guardpilot/reports/guardpilot-demo.mov`

## Suggested Submission Description

GuardPilot is a Trading Infra project for autonomous trading Agents. It is not another trading bot; it is a pre-trade risk gateway, paper trading evaluation sandbox, and audit evidence layer that sits between an Agent and execution tools.

Every trade intent is scored with behavior-aware risk rules such as leverage escalation, overtrading, revenge trading, volatility chasing, and confidence mismatch. GuardPilot returns `ALLOW`, `WARN`, or `BLOCK`, simulates safe intents in paper trading, and writes API logs, trade logs, risk events, JSON/HTML reports, and a SHA-256 evidence manifest.

The default replay uses a recorded Bitget public-market snapshot with provenance metadata. Paper-agent intents are derived from that real market tape for reproducible risk-gateway evaluation. In the included replay, GuardPilot evaluates 42 intents, allows 28, blocks 14 high-risk actions, reduces simulated max drawdown from 1.88% to 0.27%, improves final simulated equity from 9828.07 USDT to 9976.93 USDT, and generates 98 audit records. The project is paper-trading/dry-run only and does not claim live exchange execution or financial advice.

GuardPilot is designed to fit the Bitget ecosystem as a safety layer before Bitget Agent Hub Tools, Skill Hub-informed signals, Playbook strategy agents, and MCP-powered order calls reach live execution tools. The repo includes a credential-free dry-run trace at `guardpilot/samples/outputs/bitget_agenthub_dry_run_response.json`: one risky Agent Hub / Playbook-style payload is blocked with no forwarding payload, and one conservative payload is allowed with a Bitget-compatible dry-run execution preview.

## Truthfulness / Limitations

- The submitted market data is a recorded Bitget public-market snapshot with hash provenance.
- Agent intents are paper-agent signals derived from that snapshot, not live AgentHub exports.
- The submitted evidence is paper trading, not live exchange execution.
- No private Bitget API keys, exchange funds, or live order forwarding are required by default.
- GuardPilot evaluates infrastructure safety and auditability, not trading alpha.
- Any future live execution should require explicit authorization, strict risk profiles, production-grade monitoring, and independent security review.
