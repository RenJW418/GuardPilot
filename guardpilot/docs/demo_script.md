# 3-Minute Demo Script

## 0:00 - 0:20 Problem

Autonomous trading agents can submit orders 24/7, but before allowing live execution we need to know whether the Agent is safe. GuardPilot is a risk gateway and paper trading evaluation sandbox for trading agents.

## 0:20 - 0:45 Architecture

Show the diagram: Agent intent -> Risk Engine -> Paper Trading -> Audit logs -> Dashboard.

## 0:45 - 1:25 Replay

Run:

```bash
python3 scripts/replay.py --scenario samples/scenarios/btc_momentum_crash.json
```

Point out total intents, ALLOW/WARN/BLOCK counts, final equity and max drawdown comparison.

## 1:25 - 2:10 Dashboard

Open the dashboard and show:

- Risk score
- Current equity
- Blocked intents
- Equity curve
- Trade timeline
- Risk events

## 2:10 - 2:40 Audit Evidence

Open:

- `samples/outputs/sample_api_calls.jsonl`
- `samples/outputs/sample_trade_log.jsonl`
- `samples/outputs/sample_risk_report.json`

Explain that these satisfy the Trading Infra requirement for verifiable usage records.

## 2:40 - 3:00 Closing

GuardPilot is not another trading bot. It is the safety and evaluation layer every autonomous trading Agent should pass before deployment, and it can be extended to Bitget Agent Hub or Playbook.
