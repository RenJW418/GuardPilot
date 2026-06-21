# API Reference

Base URL: `http://localhost:8000`

GuardPilot is paper-trading only by default. The API never places live exchange orders unless a future deployment explicitly adds and enables a live execution adapter.

## `GET /health`

Returns service health.

## `POST /api/v1/intents`

Submit an Agent trade intent for pre-trade risk evaluation.

### Request fields

| Field | Required | Description |
|---|---:|---|
| `timestamp` | yes | ISO timestamp for the Agent decision. |
| `agent_id` | yes | Stable Agent identifier. |
| `symbol` | yes | Trading pair, e.g. `BTCUSDT`. |
| `side` | yes | `BUY` or `SELL`. |
| `order_type` | yes | Current demo supports `MARKET`. |
| `quantity` | yes | Positive order quantity. |
| `leverage` | no | Leverage multiplier, defaults to `1`. |
| `confidence` | no | Agent confidence from `0` to `1`. |
| `reason` | no | Natural-language Agent rationale. |
| `price_hint` | no | Optional price used by the demo risk context. |

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

### Response

```json
{
  "intent_id": "int_000001",
  "decision": "BLOCK",
  "risk_score": 92,
  "risk_level": "critical",
  "simulated_order_id": null,
  "account_equity_after": 9954.13,
  "checks": [
    {
      "name": "max_leverage",
      "status": "fail",
      "score": 28,
      "message": "Leverage 8.0x exceeds max 5x"
    }
  ],
  "bitget_dry_run_payload": null
}
```

Use the decision as a pre-trade gate:

- `ALLOW`: safe enough for paper trading / optional downstream forwarding.
- `WARN`: simulated and logged, but should be reviewed or size-reduced before live use.
- `BLOCK`: do not forward to execution.

## `POST /api/v1/bitget/dry-run`

Risk-check an Agent Hub / Playbook style payload and, only when allowed or warned, convert it into a Bitget-ready dry-run payload. This endpoint never places live orders.

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @samples/agents/bitget_agenthub_payload.json
```

Response fields:

| Field | Description |
|---|---|
| `guardpilot_intent` | Normalized GuardPilot trade intent. |
| `risk_decision` | `ALLOW`, `WARN`, or `BLOCK`. |
| `risk_score` | 0-100 risk score. |
| `risk_level` | Human-readable level. |
| `checks` | Per-rule explainability results. |
| `forwarding_status` | `DRY_RUN_READY_NO_LIVE_ORDER_PLACED` or `BLOCKED_BY_GUARDPILOT`. |
| `bitget_dry_run` | Bitget-ready dry-run payload, or `null` when blocked. |

Mapping:

| Agent Hub / Playbook field | GuardPilot intent | Bitget dry-run payload |
|---|---|---|
| `symbol` | `symbol` | `symbol` |
| `side` | `side` | `side` |
| `order_type` | `order_type` | `orderType` |
| `quantity` | `quantity` | `size` |
| `leverage` | `leverage` | `leverage` |
| `confidence` | `confidence` | audit metadata |
| `reason` | `reason` | `auditReason` |
| `agent_id` | `agent_id` | `clientTag` |

Blocked response shape:

```json
{
  "risk_decision": "BLOCK",
  "risk_score": 100,
  "forwarding_status": "BLOCKED_BY_GUARDPILOT",
  "bitget_dry_run": null,
  "live_forwarding": "opt_in_disabled_for_hackathon_submission"
}
```

## `POST /api/v1/replay`

Runs a deterministic replay scenario. The HTTP endpoint accepts only bundled scenario IDs to prevent arbitrary path access.

```bash
curl -X POST http://localhost:8000/api/v1/replay
curl -X POST "http://localhost:8000/api/v1/replay?scenario=eth_overtrade"
```

Allowed values:

- `btc_momentum_crash`
- `eth_overtrade`

Invalid paths, absolute paths, or unknown scenarios return `400`.

## `GET /api/v1/reports/latest`

Returns the latest replay report.

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
