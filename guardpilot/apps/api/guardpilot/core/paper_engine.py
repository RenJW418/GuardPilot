from __future__ import annotations

from itertools import count

from guardpilot.config import settings
from guardpilot.models.account import Account
from guardpilot.models.intent import Side, TradeIntent
from guardpilot.models.order import OrderFill


_order_counter = count(1)


def reset_order_counter() -> None:
    global _order_counter
    _order_counter = count(1)


class PaperTradingEngine:
    def __init__(self, fee_rate: float | None = None, slippage_bps: float | None = None):
        self.fee_rate = settings.fee_rate if fee_rate is None else fee_rate
        self.slippage_bps = settings.slippage_bps if slippage_bps is None else slippage_bps

    def execute(
        self,
        intent: TradeIntent,
        account: Account,
        price: float,
        risk_score: int,
        decision: str,
    ) -> OrderFill:
        timestamp = intent.normalized_timestamp()
        balance_before = account.balance
        fill_price = self._fill_price(price, intent.side)
        signed_qty = intent.quantity if intent.side == Side.BUY else -intent.quantity
        notional = abs(fill_price * intent.quantity * intent.leverage)
        fee = notional * self.fee_rate
        realized_pnl = self._update_position(account, intent.symbol, signed_qty, fill_price)
        account.balance += realized_pnl - fee
        account.realized_pnl += realized_pnl - fee
        account.mark_equity(timestamp, {intent.symbol: fill_price})
        order_id = f"ord_{next(_order_counter):06d}"
        return OrderFill(
            order_id=order_id,
            timestamp=timestamp,
            agent_id=intent.agent_id,
            symbol=intent.symbol,
            side=intent.side.value,
            price=round(fill_price, 4),
            quantity=intent.quantity,
            notional=round(notional, 4),
            fee=round(fee, 4),
            realized_pnl=round(realized_pnl - fee, 4),
            balance_before=round(balance_before, 4),
            balance_after=round(account.balance, 4),
            equity_after=round(account.equity, 4),
            risk_score=risk_score,
            decision=decision,
            reason=intent.reason,
        )

    def mark_only(self, intent: TradeIntent, account: Account, price: float, risk_score: int, decision: str, reason: str) -> dict:
        timestamp = intent.normalized_timestamp()
        account.mark_equity(timestamp, {intent.symbol: price})
        return {
            "timestamp": timestamp,
            "agent_id": intent.agent_id,
            "symbol": intent.symbol,
            "side": intent.side.value,
            "price": round(price, 4),
            "quantity": intent.quantity,
            "notional": round(price * intent.quantity * intent.leverage, 4),
            "fee": 0.0,
            "realized_pnl": 0.0,
            "balance_before": round(account.balance, 4),
            "balance_after": round(account.balance, 4),
            "equity_after": round(account.equity, 4),
            "risk_score": risk_score,
            "decision": decision,
            "reason": reason,
        }

    def _fill_price(self, price: float, side: Side) -> float:
        slippage = self.slippage_bps / 10000
        if side == Side.BUY:
            return price * (1 + slippage)
        return price * (1 - slippage)

    @staticmethod
    def _update_position(account: Account, symbol: str, signed_qty: float, price: float) -> float:
        position = account.position_for(symbol)
        if position.quantity == 0 or position.quantity * signed_qty > 0:
            total_qty = position.quantity + signed_qty
            if total_qty != 0:
                position.avg_price = (
                    abs(position.quantity) * position.avg_price + abs(signed_qty) * price
                ) / abs(total_qty)
            position.quantity = total_qty
            return 0.0

        closing_qty = min(abs(position.quantity), abs(signed_qty))
        realized = (price - position.avg_price) * closing_qty
        if position.quantity < 0:
            realized *= -1

        remaining_existing = abs(position.quantity) - closing_qty
        remaining_new = abs(signed_qty) - closing_qty

        if remaining_existing > 0:
            position.quantity = (1 if position.quantity > 0 else -1) * remaining_existing
        elif remaining_new > 0:
            position.quantity = (1 if signed_qty > 0 else -1) * remaining_new
            position.avg_price = price
        else:
            position.quantity = 0.0
            position.avg_price = 0.0
        return realized
