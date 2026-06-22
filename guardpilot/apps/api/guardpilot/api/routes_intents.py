from __future__ import annotations

from itertools import count
from time import perf_counter

from fastapi import APIRouter, HTTPException

from guardpilot.config import settings
from guardpilot.core.market_context import MarketContextProvider
from guardpilot.core.paper_engine import PaperTradingEngine
from guardpilot.core.risk_engine import RiskContext, RiskEngine
from guardpilot.integrations.bitget_adapter import BitgetAdapter
from guardpilot.models.account import Account
from guardpilot.models.intent import IntentResponse, TradeIntent
from guardpilot.storage.repositories import record_api_call, record_risk_event, record_trade

router = APIRouter(prefix="/api/v1", tags=["intents"])
_intent_counter = count(1)
_account = Account(balance=settings.initial_balance, equity=settings.initial_balance, peak_equity=settings.initial_balance)
_recent_trades: list[dict] = []
_risk_engine = RiskEngine()
_paper_engine = PaperTradingEngine()
_bitget_adapter = BitgetAdapter()
_market_context = MarketContextProvider()


@router.post("/intents", response_model=IntentResponse)
def submit_intent(intent: TradeIntent) -> IntentResponse:
    start = perf_counter()
    try:
        market = _market_context.for_intent(intent.symbol, intent.timestamp, intent.price_hint)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    price = market.price
    context = RiskContext(
        account=_account,
        recent_trades=_recent_trades,
        current_price=price,
        recent_volatility=market.recent_volatility,
        initial_balance=settings.initial_balance,
    )
    risk = _risk_engine.evaluate(intent, context)
    intent_id = f"int_{next(_intent_counter):06d}"
    simulated_order_id = None

    if risk.decision == "BLOCK":
        trade = _paper_engine.mark_only(intent, _account, price, risk.risk_score, risk.decision, _top_risk_message(risk.checks))
    else:
        fill = _paper_engine.execute(intent, _account, price, risk.risk_score, risk.decision)
        simulated_order_id = fill.order_id
        trade = fill.model_dump()

    _recent_trades.append({**trade, "parsed_timestamp": intent.timestamp})
    record_trade({key: value for key, value in trade.items() if key != "parsed_timestamp"})

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

    latency_ms = int((perf_counter() - start) * 1000)
    bitget_dry_run_payload = None
    if risk.decision in {"ALLOW", "WARN"}:
        bitget_dry_run_payload = _bitget_adapter.dry_run_forward_allowed_intent(intent.model_dump(mode="json"))
    record_api_call(
        {
            "timestamp": intent.normalized_timestamp(),
            "method": "POST",
            "path": "/api/v1/intents",
            "agent_id": intent.agent_id,
            "status_code": 200,
            "latency_ms": latency_ms,
            "decision": risk.decision,
            "risk_score": risk.risk_score,
        }
    )
    return IntentResponse(
        intent_id=intent_id,
        decision=risk.decision,
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        simulated_order_id=simulated_order_id,
        account_equity_after=round(_account.equity, 4),
        checks=[check.model_dump() for check in risk.checks],
        bitget_dry_run_payload=bitget_dry_run_payload,
        market_context=market.model_dump(),
        execution_mode="paper_trading_only",
    )


def _top_risk_message(checks) -> str:
    failing = [check for check in checks if check.status == "fail"]
    warning = [check for check in checks if check.status == "warn"]
    chosen = failing or warning
    if not chosen:
        return "All risk checks passed"
    return max(chosen, key=lambda check: check.score).message
