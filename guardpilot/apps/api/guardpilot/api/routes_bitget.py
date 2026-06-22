from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, HTTPException

from guardpilot.config import settings
from guardpilot.core.market_context import MarketContextProvider
from guardpilot.core.risk_engine import RiskContext, RiskEngine
from guardpilot.integrations.agent_hub_adapter import AgentHubAdapter
from guardpilot.integrations.bitget_adapter import BitgetAdapter
from guardpilot.models.account import Account
from guardpilot.models.intent import TradeIntent
from guardpilot.storage.repositories import record_api_call, record_risk_event

router = APIRouter(prefix="/api/v1/bitget", tags=["bitget"])
_agent_hub_adapter = AgentHubAdapter()
_bitget_adapter = BitgetAdapter()
_risk_engine = RiskEngine()
_market_context = MarketContextProvider()
_demo_account = Account(balance=settings.initial_balance, equity=settings.initial_balance, peak_equity=settings.initial_balance)


@router.post("/dry-run")
def bitget_dry_run(payload: dict) -> dict:
    """Risk-check an Agent Hub / Playbook style signal before Bitget dry-run forwarding.

    This endpoint never places live orders. It makes the GuardPilot -> Bitget
    execution boundary explicit for hackathon review and safety testing.
    """
    start = perf_counter()
    intent_payload = _agent_hub_adapter.to_guardpilot_intent(payload)
    intent = TradeIntent(**intent_payload)
    try:
        market = _market_context.for_intent(intent.symbol, intent.timestamp, intent.price_hint)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    price = market.price
    context = RiskContext(
        account=_demo_account,
        recent_trades=[],
        current_price=price,
        recent_volatility=market.recent_volatility,
        initial_balance=settings.initial_balance,
    )
    risk = _risk_engine.evaluate(intent, context)
    bitget_payload = None
    forwarding_status = "BLOCKED_BY_GUARDPILOT"
    if risk.decision in {"ALLOW", "WARN"}:
        bitget_payload = _bitget_adapter.dry_run_forward_allowed_intent(intent.model_dump(mode="json"))
        forwarding_status = "DRY_RUN_READY_NO_LIVE_ORDER_PLACED"

    latency_ms = int((perf_counter() - start) * 1000)
    record_api_call(
        {
            "timestamp": intent.normalized_timestamp(),
            "method": "POST",
            "path": "/api/v1/bitget/dry-run",
            "agent_id": intent.agent_id,
            "status_code": 200,
            "latency_ms": latency_ms,
            "decision": risk.decision,
            "risk_score": risk.risk_score,
        }
    )
    if risk.decision in {"WARN", "BLOCK"}:
        record_risk_event(
            {
                "timestamp": intent.normalized_timestamp(),
                "agent_id": intent.agent_id,
                "symbol": intent.symbol,
                "decision": risk.decision,
                "risk_score": risk.risk_score,
                "risk_level": risk.risk_level,
                "message": _top_risk_message(risk.checks),
            }
        )

    return {
        "guardpilot_intent": intent.model_dump(mode="json"),
        "risk_decision": risk.decision,
        "risk_score": risk.risk_score,
        "risk_level": risk.risk_level,
        "checks": [check.model_dump() for check in risk.checks],
        "forwarding_status": forwarding_status,
        "bitget_dry_run": bitget_payload,
        "market_context": market.model_dump(),
        "execution_mode": "paper_trading_only",
        "live_forwarding": {
            "enabled": False,
            "reason": "Hackathon submission is paper-trading/dry-run only. No private keys, real funds, or live Bitget orders are used.",
        },
    }


def _top_risk_message(checks) -> str:
    failing = [check for check in checks if check.status == "fail"]
    warning = [check for check in checks if check.status == "warn"]
    chosen = failing or warning
    if not chosen:
        return "All risk checks passed"
    return max(chosen, key=lambda check: check.score).message
