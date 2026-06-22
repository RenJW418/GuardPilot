# API Reference

Base URL: `http://localhost:8000`

GuardPilot is paper-trading and dry-run only by default. It uses a recorded Bitget public-market snapshot for market context and never places live exchange orders in this submission.

## `GET /health`

Returns service health.

## `POST /api/v1/intents`

Submit an Agent trade intent for pre-trade risk evaluation.

### Market context

If `price_hint` is omitted, GuardPilot uses the nearest/latest close from the committed Bitget public snapshot: `samples/market/bitget_btcusdt_1m.csv`. If `price_hint` is provided, the response labels it as an agent-provided price while still using snapshot volatility context. Unsupported symbols fail with `400`; GuardPilot does not fall back to fake prices.

### Request fields

| Field | Required | Description |
|---|---:|---|
| `timestamp` | yes | ISO timestamp for the Agent decision. |
| `agent_id` | yes | Stable Agent identifier. |
| `symbol` | yes | Trading pair, e.g. `BTCUSDT`. Must exist in the market snapshot unless `price_hint` is explicitly used for supported workflows. |
| `side` | yes | `BUY` or `SELL`. |
| `order_type` | yes | Current demo supports `MARKET`. |
| `quantity` | yes | Positive order quantity. |
| `leverage` | no | Leverage multiplier, defaults to `1`. |
| `confidence` | no | Agent confidence from `0` to `1`. |
| `reason` | no | Natural-language Agent rationale. |
| `price_hint` | no | Optional agent-provided price; otherwise snapshot close is used. |

```json
{
  "timestamp": "2026-06-22T16:10:00Z",
  "agent_id": "paper_agent",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 0.005,
  "leverage": 1,
  "confidence": 0.82,
  "reason": "Small paper order"
}
```

### Response

```json
{
  "intent_id": "int_000001",
  "decision": "ALLOW",
  "risk_score": 12,
  "risk_level": "low",
  "simulated_order_id": "paper_000001",
  "account_equity_after": 9999.34,
  "checks": [],
  "bitget_dry_run_payload": {
    "status": "DRY_RUN_READY",
    "execution_payload": {
      "symbol": "BTCUSDT",
      "size": 0.005,
      "guardpilotPolicy": "ALLOW_OR_WARN_ONLY_DRY_RUN_NO_LIVE_ORDER"
    }
  },
  "market_context": {
    "source": "Bitget public market API snapshot",
    "price_source": "bitget_public_snapshot_close",
    "snapshot_path": "samples/market/bitget_btcusdt_1m.csv"
  },
  "execution_mode": "paper_trading_only"
}
```

Decision contract:

- `ALLOW`: safe enough for paper trading / optional dry-run preview.
- `WARN`: simulated and logged, but should be reviewed or size-reduced before live use.
- `BLOCK`: do not forward to execution; no dry-run payload is generated.

## `POST /api/v1/bitget/dry-run`

Risk-check an Agent Hub / Playbook-style payload and, only when allowed or warned, convert it into a Bitget-compatible dry-run preview. This endpoint never places live orders and does not require private Bitget credentials.

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
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
| `bitget_dry_run` | Bitget-compatible dry-run preview, or `null` when blocked. |
| `market_context` | Bitget public snapshot price/volatility context. |
| `execution_mode` | Always `paper_trading_only` in this submission. |
| `live_forwarding` | Object with `enabled: false` and safety reason. |

Mapping:

| Agent Hub / Playbook field | GuardPilot intent | Dry-run preview payload |
|---|---|---|
| `symbol` | `symbol` | `symbol` |
| `side` | `side` | `side` |
| `order_type` | `order_type` | `orderType` |
| `quantity` | `quantity` | `quantity` and `size` |
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
  "execution_mode": "paper_trading_only",
  "live_forwarding": {
    "enabled": false,
    "reason": "Hackathon submission is paper-trading/dry-run only. No private keys, real funds, or live Bitget orders are used."
  }
}
```

## `POST /api/v1/replay`

Runs a replay scenario. The default scenario uses the committed Bitget public-market snapshot and paper-agent signals derived from it. The HTTP endpoint accepts only bundled scenario IDs to prevent arbitrary path access.

```bash
curl -X POST http://localhost:8000/api/v1/replay
curl -X POST "http://localhost:8000/api/v1/replay?scenario=btc_momentum_crash"
```

Allowed values:

- `btc_momentum_crash`

Invalid paths, absolute paths, or unknown scenarios return `400`.

## Other read endpoints

- `GET /api/v1/reports/latest` — latest replay report.
- `GET /api/v1/agents` — Agent summary table.
- `GET /api/v1/agents/{agent_id}` — trades and risk events for one Agent.
- `GET /api/v1/trades` — paper trading audit log.
- `GET /api/v1/risk-events` — WARN / BLOCK events.
- `GET /api/v1/api-logs` — API call records for Infra track evidence.
