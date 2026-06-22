from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from guardpilot.config import settings  # noqa: E402
from guardpilot.core.market_context import MarketContextProvider  # noqa: E402
from guardpilot.core.risk_engine import RiskContext, RiskEngine  # noqa: E402
from guardpilot.integrations.agent_hub_adapter import AgentHubAdapter  # noqa: E402
from guardpilot.integrations.bitget_adapter import BitgetAdapter  # noqa: E402
from guardpilot.models.account import Account  # noqa: E402
from guardpilot.models.intent import TradeIntent  # noqa: E402


CASES = [
    {
        "case_id": "agenthub_style_blocked_risky_payload",
        "input_path": ROOT / "samples" / "agents" / "bitget_agenthub_payload.json",
        "expected_gate": "BLOCK",
    },
    {
        "case_id": "agenthub_style_allowed_safe_payload",
        "input_path": ROOT / "samples" / "agents" / "bitget_agenthub_safe_payload.json",
        "expected_gate": "ALLOW_OR_WARN_WITH_DRY_RUN_PAYLOAD",
    },
]


def evaluate_case(case: dict) -> dict:
    payload = json.loads(case["input_path"].read_text(encoding="utf-8"))
    adapter = AgentHubAdapter()
    bitget = BitgetAdapter()
    risk_engine = RiskEngine()
    market_provider = MarketContextProvider()
    start = perf_counter()

    intent = TradeIntent(**adapter.to_guardpilot_intent(payload))
    market = market_provider.for_intent(intent.symbol, intent.timestamp, intent.price_hint)
    context = RiskContext(
        account=Account(balance=settings.initial_balance, equity=settings.initial_balance, peak_equity=settings.initial_balance),
        recent_trades=[],
        current_price=market.price,
        recent_volatility=market.recent_volatility,
        initial_balance=settings.initial_balance,
    )
    risk = risk_engine.evaluate(intent, context)
    bitget_dry_run = None
    forwarding_status = "BLOCKED_BY_GUARDPILOT"
    if risk.decision in {"ALLOW", "WARN"}:
        bitget_dry_run = bitget.dry_run_forward_allowed_intent(intent.model_dump(mode="json"))
        forwarding_status = "DRY_RUN_READY_NO_LIVE_ORDER_PLACED"

    return {
        "case_id": case["case_id"],
        "expected_gate": case["expected_gate"],
        "source_payload": str(case["input_path"].relative_to(ROOT)),
        "agent_surface": payload.get("agent_surface"),
        "skill_context": payload.get("skill_context"),
        "guardpilot_intent": intent.model_dump(mode="json"),
        "risk_decision": risk.decision,
        "risk_score": risk.risk_score,
        "risk_level": risk.risk_level,
        "checks": [check.model_dump() for check in risk.checks],
        "forwarding_status": forwarding_status,
        "bitget_dry_run": bitget_dry_run,
        "market_context": market.model_dump(),
        "execution_mode": "paper_trading_only",
        "live_forwarding": {
            "enabled": False,
            "reason": "Hackathon evidence is dry-run/paper-only; no private keys, real funds, or live orders are used.",
        },
        "latency_ms": int((perf_counter() - start) * 1000),
    }


def main() -> None:
    output = {
        "title": "GuardPilot Bitget AI Agent-style dry-run contract evidence",
        "description": "Credential-free evidence that Agent Hub / Playbook / Skill Hub / MCP-style signals are normalized, risk-gated, and only forwarded as Bitget-compatible dry-run previews when not blocked.",
        "agent_surfaces_covered": [
            "Agent Hub Tools",
            "Skill Hub signal context",
            "Bitget Playbook strategy output",
            "MCP Server order-tool boundary",
        ],
        "live_exchange_orders": False,
        "cases": [evaluate_case(case) for case in CASES],
    }
    output_path = ROOT / "samples" / "outputs" / "bitget_agenthub_dry_run_response.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}")
    for case in output["cases"]:
        payload_state = "payload" if case["bitget_dry_run"] else "no payload"
        print(f"{case['case_id']}: {case['risk_decision']} -> {payload_state}")


if __name__ == "__main__":
    main()
