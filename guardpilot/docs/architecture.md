# Architecture

GuardPilot is intentionally small and reproducible for hackathon judging.

```text
Demo Agent -> GuardPilot API -> Risk Engine
                         |-> Paper Trading Engine
                         |-> SQLite + JSONL audit logs
                         |-> Dashboard / Reports
```

## Components

- **Agent Gateway**: `POST /api/v1/intents` accepts an Agent's trade intent.
- **Risk Engine**: rules evaluate leverage, exposure, drawdown, volatility, overtrading and revenge trading.
- **Paper Engine**: simulates market fills, fees, slippage, positions, realized PnL and equity curve.
- **Replay Engine**: loads deterministic market CSV + signal JSONL and regenerates reports.
- **Dashboard**: React interface for PnL, risk score, equity curve, trade log and API audit log.

## Data Flow

1. Agent sends trade intent with `reason` and `confidence`.
2. GuardPilot builds risk context from account state and recent trades.
3. Risk Engine returns `ALLOW`, `WARN`, or `BLOCK`.
4. `ALLOW` / `WARN` intents are paper-traded; `BLOCK` intents are recorded but not executed.
5. Every step is written to JSONL logs and, when the API is running, SQLite.
6. Reports compare baseline paper trading vs guarded paper trading.
