# Submission Checklist

## Required for Trading Infra

- [ ] Public GitHub repository.
- [ ] README includes installation steps.
- [ ] README includes integration method: `POST /api/v1/intents`.
- [ ] README includes usage examples and replay command.
- [ ] Verifiable usage record is included:
  - `samples/outputs/sample_api_calls.jsonl`
  - `samples/outputs/sample_trade_log.jsonl`
  - `samples/outputs/sample_risk_report.json`
- [ ] Another developer can run the project from README.

## Strongly Recommended

- [ ] Public demo video, under 3 minutes.
- [ ] Public dashboard deployment if time allows.
- [ ] X/Twitter development post with `#BitgetHackathon` and `@Bitget_AI`.
- [ ] Architecture diagram in README.
- [ ] No secrets or real exchange credentials in repository.
- [ ] Clear paper trading disclaimer.
- [ ] Submission UID matches Bitget registration UID.

## Suggested Submission Summary

GuardPilot is a risk gateway and paper trading evaluation sandbox for autonomous trading agents. It evaluates each Agent trade intent with behavior-aware risk rules, blocks dangerous actions, simulates safe orders in a paper trading engine, and generates reproducible audit logs and reports for deployment review.
