# API Reference

Base URL: `http://localhost:8000`

## `GET /health`

Returns service health.

## `POST /api/v1/intents`

Submit an Agent trade intent.

```json
{
  "timestamp": "2026-06-20T10:08:00Z",
  "agent_id": "demo_momentum_agent",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 0.08,
  "leverage": 8,
  "confidence": 0.61,
  "reason": "Trying to recover previous losses after breakout failure"
}
```

Response:

```json
{
  "intent_id": "int_000001",
  "decision": "BLOCK",
  "risk_score": 92,
  "risk_level": "critical",
  "simulated_order_id": null,
  "account_equity_after": 9954.13,
  "checks": []
}
```

## `GET /api/v1/agents`

Returns Agent summary table.

## `GET /api/v1/agents/{agent_id}`

Returns trades and risk events for one Agent.

## `GET /api/v1/trades`

Returns paper trading audit log.

## `GET /api/v1/risk-events`

Returns WARN / BLOCK events.

## `GET /api/v1/api-logs`

Returns API call records for Infra track submission evidence.

## `POST /api/v1/replay`

Runs deterministic scenario replay.

## `GET /api/v1/reports/latest`

Returns the latest replay report.
