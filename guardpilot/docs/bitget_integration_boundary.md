# Bitget Integration Boundary

GuardPilot is designed as a pre-trade safety layer before Bitget Agent Hub / Playbook / MCP-style execution tools.

The hackathon MVP intentionally uses deterministic paper trading and dry-run payloads only. This keeps the demo reproducible for judges and avoids requiring exchange credentials or real funds.

## Current Hackathon Flow

```text
Bitget Agent Hub / Playbook style signal
        |
        v
GuardPilot /api/v1/bitget/dry-run
        |
        v
Normalize to GuardPilot trade intent
        |
        v
Risk Engine + Paper Trading Sandbox
        |
        +-- BLOCK -> stop, write risk event, return no forwarding payload
        |
        +-- WARN  -> write audit trail, return Bitget-ready dry-run payload
        |
        +-- ALLOW -> write audit trail, return Bitget-ready dry-run payload
```

## Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

## Safety Contract

- `BLOCK` means GuardPilot does **not** generate a Bitget forwarding payload.
- `WARN` and `ALLOW` may generate a Bitget-ready dry-run payload.
- `live_forwarding` remains opt-in and disabled for the hackathon submission.
- No real exchange order is placed by default.
- Every decision is recorded in API logs and risk events for audit.

## Why This Matters for Trading Infra

Bitget Agent Hub and Playbook can give Agents powerful market and execution capabilities. GuardPilot adds the missing safety layer between autonomous reasoning and order execution:

1. **Pre-trade risk scoring** before any order tool is reached.
2. **Behavior-aware guardrails** for overtrading, revenge trading, leverage escalation, volatility chasing, and confidence mismatch.
3. **Paper trading evaluation** so teams can inspect fills, PnL, equity, and drawdown without real funds.
4. **Reproducible audit evidence** through API logs, trade logs, risk events, reports, and SHA-256 manifests.

## Future Live Integration

A production deployment could place GuardPilot in front of live Bitget order tools:

```text
Agent signal -> GuardPilot risk score -> policy decision -> optional Bitget order tool
```

Live forwarding should only be enabled with explicit authorization, strict risk profiles, secret management, monitoring, alerting, and rollback controls.
