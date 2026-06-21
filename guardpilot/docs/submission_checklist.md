# Submission Checklist

## Final Submission Fields

- [x] Public GitHub repository: `https://github.com/RenJW418/GuardPilot`
- [ ] Demo video public URL: `TODO: upload reports/guardpilot-demo.mov or publish a public video link`
- [ ] Public dashboard deployment URL, optional: `TODO: add if deployed`
- [ ] X/Twitter development post URL with `#BitgetHackathon` and `@Bitget_AI`: `TODO`
- [ ] Bitget registration UID confirmed: `TODO: confirm same UID as registration`
- [ ] Submission form completed: `https://forms.gle/GDQNx5TnCBvYuPin9`
- [ ] Final commit hash or release tag: `TODO`

## Required for Trading Infra

- [x] Public GitHub repository: `https://github.com/RenJW418/GuardPilot`
- [x] README includes installation steps.
- [x] README includes integration method: `POST /api/v1/intents`.
- [x] README documents Bitget dry-run boundary: `POST /api/v1/bitget/dry-run`.
- [x] README includes usage examples and replay command.
- [x] Verifiable usage record is included:
  - `samples/outputs/sample_api_calls.jsonl`
  - `samples/outputs/sample_trade_log.jsonl`
  - `samples/outputs/sample_risk_events.jsonl`
  - `samples/outputs/sample_risk_report.json`
  - `samples/outputs/evidence_manifest.json`
- [x] Another developer can run the project from README.
- [x] Paper trading disclaimer is explicit; no live exchange funds are claimed.

## Commands to Run Before Final Submission

```bash
npm run test
npm run replay
npm run evidence
npm run build
```

Expected proof points from `npm run evidence`:

- 42 total Agent intents.
- 16 allowed / 4 warned / 22 blocked.
- Final simulated equity: 9980.91 USDT with GuardPilot vs 9930.81 USDT without guard.
- Max drawdown: 0.70% with GuardPilot vs 2.60% without guard.
- Relative drawdown reduction: 73.11%.
- 110 audit records generated.
- Evidence manifest hashes and JSONL row counts pass verification.

## Strongly Recommended

- [x] Public demo video file prepared: `reports/guardpilot-demo.mov`.
- [ ] Public demo video URL added to final submission packet.
- [ ] Public dashboard deployment if time allows.
- [ ] X/Twitter development post with `#BitgetHackathon` and `@Bitget_AI`.
- [x] Architecture diagram in README.
- [x] No secrets or real exchange credentials in repository.
- [x] Clear paper trading disclaimer.
- [ ] Submission UID matches Bitget registration UID.

## Suggested Submission Summary

GuardPilot is a pre-trade risk gateway, paper trading evaluation sandbox, and audit layer for autonomous trading agents. Instead of letting an Agent directly place orders, GuardPilot evaluates each trade intent with behavior-aware risk rules, returns `ALLOW`, `WARN`, or `BLOCK`, simulates safe intents in paper trading, and generates hash-verifiable audit logs and reports.

In the included deterministic replay, GuardPilot evaluates 42 Agent intents, blocks 22 high-risk actions, reduces simulated max drawdown from 2.60% to 0.70%, improves final simulated equity by 50.10 USDT, and produces 110 audit records. The project is paper-trading only and does not claim live exchange execution or financial advice.

## Evidence Artifact Paths

- Demo video: `reports/guardpilot-demo.mov`
- HTML report: `reports/demo_report.html`
- Risk report: `samples/outputs/sample_risk_report.json`
- Evidence manifest: `samples/outputs/evidence_manifest.json`
- API logs: `samples/outputs/sample_api_calls.jsonl`
- Trade logs: `samples/outputs/sample_trade_log.jsonl`
- Risk events: `samples/outputs/sample_risk_events.jsonl`
- API reference: `docs/api_reference.md`
- Evidence explanation: `docs/evidence.md`
