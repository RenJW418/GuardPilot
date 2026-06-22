# Submission Checklist

## Final Submission Fields

- [x] Public GitHub repository: `https://github.com/RenJW418/GuardPilot`
- [ ] Demo video public URL: add after uploading `reports/guardpilot-demo.mov` or another public recording link
- [ ] Public dashboard deployment URL, optional: not required for local reproducible judging; add only if deployed
- [ ] X/Twitter development post URL with `#BitgetHackathon` and `@Bitget_AI`: optional post-submission promotion field
- [ ] Bitget registration UID confirmed: fill manually in the submission form if required; do not commit private UID if unnecessary
- [ ] Submission form completed: `https://forms.gle/GDQNx5TnCBvYuPin9`
- [ ] Final commit hash or release tag: fill after final push

## Required for Trading Infra

- [x] Public GitHub repository: `https://github.com/RenJW418/GuardPilot`
- [x] README includes installation steps.
- [x] README includes integration method: `POST /api/v1/intents`.
- [x] README documents Bitget dry-run boundary: `POST /api/v1/bitget/dry-run`.
- [x] Bitget-style dry-run trace is included: `samples/outputs/bitget_agenthub_dry_run_response.json`.
- [x] README includes usage examples and replay command.
- [x] Default replay uses Bitget public market snapshot, not generated synthetic candles.
- [x] Market provenance is included and hash-checked:
  - `samples/market/bitget_btcusdt_1m.csv`
  - `samples/market/bitget_btcusdt_1m.provenance.json`
- [x] Verifiable usage record is included:
  - `samples/outputs/sample_api_calls.jsonl`
  - `samples/outputs/sample_trade_log.jsonl`
  - `samples/outputs/sample_risk_events.jsonl`
  - `samples/outputs/sample_risk_report.json`
  - `samples/outputs/evidence_manifest.json`
- [x] Another developer can run the project from README.
- [x] Paper trading disclaimer is explicit; no live exchange funds are claimed.
- [x] No docs claim live trading or guaranteed profitability.

## Commands to Run Before Final Submission

```bash
npm run test
npm run build
npm run replay
npm run evidence
npm run bitget:trace
```

Expected proof points from `npm run evidence`:

- Market data source: Bitget public market API snapshot.
- 42 total paper-agent intents.
- 28 allowed / 0 warned / 14 blocked.
- Final simulated equity: 9976.93 USDT with GuardPilot vs 9828.07 USDT without guard.
- Max drawdown: 0.27% with GuardPilot vs 1.88% without guard.
- Relative drawdown reduction: 85.68%.
- 98 audit records generated.
- Evidence manifest hashes, CSV/JSONL row counts, and market provenance checks pass verification.

## Strongly Recommended

- [x] Architecture and data-flow diagram in README.
- [x] No secrets or real exchange credentials in repository.
- [x] Clear paper trading / dry-run disclaimer.
- [x] Dashboard displays real-data provenance and execution boundary.
- [ ] Public demo video URL added to final submission packet after upload.
- [ ] Public dashboard deployment if time allows.
- [ ] X/Twitter development post with `#BitgetHackathon` and `@Bitget_AI` if desired.
- [ ] Submission UID matches Bitget registration UID if the form asks for it.

## Suggested Submission Summary

GuardPilot is a pre-trade risk gateway, paper trading evaluation sandbox, and audit layer for autonomous trading agents. Instead of letting an Agent directly place orders, GuardPilot evaluates each trade intent with behavior-aware risk rules, returns `ALLOW`, `WARN`, or `BLOCK`, simulates safe intents in paper trading, and generates hash-verifiable audit logs and reports.

The default replay uses a recorded Bitget public market data snapshot with provenance metadata. Paper-agent intents are derived from that real market tape for reproducible risk-gateway evaluation. In the included replay, GuardPilot evaluates 42 intents, blocks 14 high-risk actions, reduces simulated max drawdown from 1.88% to 0.27%, improves final simulated equity by 148.86 USDT, and produces 98 audit records. The project is paper-trading/dry-run only and does not claim live exchange execution, financial advice, or profitability guarantees.

## Evidence Artifact Paths

- Demo video: `reports/guardpilot-demo.mov` if recorded locally
- HTML report: `reports/demo_report.html`
- Market snapshot: `samples/market/bitget_btcusdt_1m.csv`
- Market provenance: `samples/market/bitget_btcusdt_1m.provenance.json`
- Paper-agent inputs: `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl`
- Signal provenance: `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.provenance.json`
- Risk report: `samples/outputs/sample_risk_report.json`
- Evidence manifest: `samples/outputs/evidence_manifest.json`
- API logs: `samples/outputs/sample_api_calls.jsonl`
- Trade logs: `samples/outputs/sample_trade_log.jsonl`
- Risk events: `samples/outputs/sample_risk_events.jsonl`
- Bitget-style dry-run trace: `samples/outputs/bitget_agenthub_dry_run_response.json`
- Agent Hub / Playbook-style risky payload: `samples/agents/bitget_agenthub_payload.json`
- Agent Hub / Playbook-style safe payload: `samples/agents/bitget_agenthub_safe_payload.json`
