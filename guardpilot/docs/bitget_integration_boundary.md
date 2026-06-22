# Bitget Integration Boundary

GuardPilot is designed as a pre-trade safety layer before the Bitget AI Agent surfaces described in the hackathon requirements: **Agent Hub Tools**, **Skill Hub**, **MCP Server**, and **Bitget Playbook**.

The submitted release intentionally uses a recorded Bitget public-market snapshot, paper trading, and dry-run previews only. This keeps the demo reproducible for judges and avoids requiring private exchange credentials or real funds.

## Why this matches the Bitget AI Agent toolkit

The competition brief asks builders to start from Bitget Agent Hub or Bitget Playbook. GuardPilot does not replace those tools; it adds the missing safety contract between autonomous agent reasoning and order-capable tooling:

| Bitget AI Agent surface | What it gives an Agent | GuardPilot role |
|---|---|---|
| Agent Hub Tools | Trading APIs for spot, futures, accounts, and order actions | Gate every order-like intent before a payload is produced |
| Skill Hub | Macro, sentiment, technical, on-chain, and news context | Preserve signal context in audit reasons and score behavior risk |
| MCP Server | Claude/Cursor/Codex can call Bitget tools directly | Insert a risk decision before any MCP order call is allowed |
| Playbook | Natural-language strategy generation, backtesting, and deployment | Evaluate strategy signals in paper trading before live execution |

For Bitget, this can become a pre-launch certification and audit layer for AI trading agents: safer agent onboarding, fewer unsafe automated orders, and reviewable evidence before any strategy touches live execution.

## Current Hackathon Flow

```text
Recorded Bitget public market snapshot
        |
        v
Paper-agent / Agent Hub / Playbook-style signal
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
        +-- WARN  -> write audit trail, return Bitget-compatible dry-run preview
        |
        +-- ALLOW -> write audit trail, return Bitget-compatible dry-run preview
```

## Data and execution boundary

- Market context comes from `samples/market/bitget_btcusdt_1m.csv`, a recorded Bitget public API snapshot.
- Snapshot provenance lives at `samples/market/bitget_btcusdt_1m.provenance.json`.
- Agent signals in the default replay are paper-agent signals derived from that snapshot.
- `/api/v1/bitget/dry-run` returns a dry-run preview only; it is not an official Bitget order API client.
- `live_forwarding.enabled` is false in the submitted release.

## Agent Hub / Playbook-style payload contract

A reviewable sample payload lives at:

- `samples/agents/bitget_agenthub_payload.json`

It includes:

- `source`: Agent Hub / Playbook style signal
- `agent_surface`: Agent Hub Tools + Skill Hub + Playbook + MCP Server
- `skill_context`: analysis context produced by Skill Hub-style modules
- standard order fields: `symbol`, `side`, `order_type`, `quantity`, `leverage`, `confidence`, `reason`

GuardPilot maps this signal into a normalized `TradeIntent`, runs behavior-aware risk checks, and returns a dry-run preview only when the decision is `ALLOW` or `WARN`.

## Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

## Credential-free trace

For judges who do not have a Bitget Playbook API key or Agent Hub MCP credentials, the repository includes a reproducible dry-run trace that models the Agent Hub / Playbook contract without placing orders:

```bash
npm run bitget:trace
```

Generated output:

- `samples/outputs/bitget_agenthub_dry_run_response.json`

It contains two cases:

1. `agenthub_style_blocked_risky_payload` — a risky Playbook-style payload is `BLOCK`ed and returns `bitget_dry_run: null`.
2. `agenthub_style_allowed_safe_payload` — a conservative Agent-style payload is `ALLOW`ed and returns a Bitget-compatible dry-run execution preview.

This is not a live Bitget order and does not require credentials. It is a reviewable contract trace showing where GuardPilot sits relative to Agent Hub Tools, Skill Hub context, MCP Server order calls, and Playbook strategy output.

## Safety Contract

- `BLOCK` means GuardPilot does **not** generate a forwarding payload.
- `WARN` and `ALLOW` may generate a dry-run preview.
- `live_forwarding.enabled` remains false for the hackathon submission.
- No real exchange order is placed by default.
- Every decision is recorded in API logs and risk events for audit.

## Why This Matters for Trading Infra

Bitget Agent Hub and Playbook can give Agents powerful market and execution capabilities. GuardPilot adds the missing safety layer between autonomous reasoning and order execution:

1. **Pre-trade risk scoring** before any order tool is reached.
2. **Behavior-aware guardrails** for overtrading, revenge trading, leverage escalation, volatility chasing, and confidence mismatch.
3. **Paper trading evaluation** so teams can inspect fills, PnL, equity, and drawdown without real funds.
4. **Reproducible audit evidence** through public-market provenance, API logs, trade logs, risk events, reports, and SHA-256 manifests.

## Future Live Integration

A production deployment could place GuardPilot in front of live Bitget order tools:

```text
Agent signal -> GuardPilot risk score -> policy decision -> optional Bitget order tool
```

Live forwarding should only be enabled with explicit authorization, strict risk profiles, secret management, monitoring, alerting, rollback controls, and independent security review.
