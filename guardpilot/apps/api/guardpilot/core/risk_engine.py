from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from guardpilot.core.scoring import clamp_score, decision_for, risk_level
from guardpilot.models.account import Account
from guardpilot.models.intent import TradeIntent
from guardpilot.models.risk import RiskCheck, RiskDecision


@dataclass
class RiskProfile:
    max_leverage: float = 5
    warn_leverage: float = 3
    max_single_notional_ratio: float = 0.35
    warn_single_notional_ratio: float = 0.22
    max_symbol_exposure_ratio: float = 0.55
    daily_loss_limit: float = 0.06
    max_consecutive_losses: int = 3
    max_trades_per_15m: int = 8
    volatility_warn: float = 0.018
    volatility_block: float = 0.035
    min_confidence: float = 0.35


@dataclass
class RiskContext:
    account: Account
    recent_trades: list[dict] = field(default_factory=list)
    current_price: float = 0.0
    recent_volatility: float = 0.0
    initial_balance: float = 10000.0


class RiskEngine:
    def __init__(self, profile: RiskProfile | None = None):
        self.profile = profile or RiskProfile()

    def evaluate(self, intent: TradeIntent, context: RiskContext) -> RiskDecision:
        checks = [
            self._check_leverage(intent),
            self._check_single_notional(intent, context),
            self._check_symbol_exposure(intent, context),
            self._check_daily_loss(intent, context),
            self._check_consecutive_losses(intent, context),
            self._check_overtrading(intent, context),
            self._check_revenge_trading(intent, context),
            self._check_volatility(intent, context),
            self._check_confidence_mismatch(intent, context),
        ]
        score = clamp_score(sum(check.score for check in checks))
        return RiskDecision(
            decision=decision_for(score),
            risk_score=score,
            risk_level=risk_level(score),
            checks=checks,
        )

    def _check_leverage(self, intent: TradeIntent) -> RiskCheck:
        if intent.leverage > self.profile.max_leverage:
            return RiskCheck(name="max_leverage", status="fail", score=28, message=f"Leverage {intent.leverage}x exceeds max {self.profile.max_leverage}x")
        if intent.leverage > self.profile.warn_leverage:
            return RiskCheck(name="max_leverage", status="warn", score=12, message=f"Leverage {intent.leverage}x is above recommended {self.profile.warn_leverage}x")
        return RiskCheck(name="max_leverage", status="pass", score=0, message="Leverage is within limit")

    def _check_single_notional(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        notional = intent.quantity * context.current_price * intent.leverage
        ratio = notional / max(context.account.equity, 1)
        if ratio > self.profile.max_single_notional_ratio:
            return RiskCheck(name="max_single_notional", status="fail", score=24, message=f"Single trade notional is {ratio:.1%} of equity")
        if ratio > self.profile.warn_single_notional_ratio:
            return RiskCheck(name="max_single_notional", status="warn", score=10, message=f"Single trade notional is elevated at {ratio:.1%} of equity")
        return RiskCheck(name="max_single_notional", status="pass", score=0, message="Single trade notional is acceptable")

    def _check_symbol_exposure(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        position = context.account.position_for(intent.symbol)
        current_exposure = abs(position.quantity * context.current_price)
        new_exposure = abs(intent.quantity * context.current_price * intent.leverage)
        ratio = (current_exposure + new_exposure) / max(context.account.equity, 1)
        if ratio > self.profile.max_symbol_exposure_ratio:
            return RiskCheck(name="symbol_exposure", status="fail", score=18, message=f"Projected {intent.symbol} exposure reaches {ratio:.1%} of equity")
        if ratio > self.profile.max_symbol_exposure_ratio * 0.75:
            return RiskCheck(name="symbol_exposure", status="warn", score=8, message=f"Projected {intent.symbol} exposure is concentrated at {ratio:.1%}")
        return RiskCheck(name="symbol_exposure", status="pass", score=0, message="Symbol exposure is diversified enough")

    def _check_daily_loss(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        loss_ratio = max(0.0, (context.initial_balance - context.account.equity) / context.initial_balance)
        if loss_ratio > self.profile.daily_loss_limit:
            return RiskCheck(name="daily_loss_limit", status="fail", score=26, message=f"Daily loss {loss_ratio:.1%} exceeds limit {self.profile.daily_loss_limit:.1%}")
        if loss_ratio > self.profile.daily_loss_limit * 0.65:
            return RiskCheck(name="daily_loss_limit", status="warn", score=10, message=f"Daily loss is approaching limit at {loss_ratio:.1%}")
        return RiskCheck(name="daily_loss_limit", status="pass", score=0, message="Daily loss is within limit")

    def _check_consecutive_losses(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        streak = self._loss_streak(context.recent_trades)
        if streak >= self.profile.max_consecutive_losses:
            return RiskCheck(name="consecutive_losses", status="fail", score=16, message=f"Agent has {streak} consecutive losing closes")
        if streak == self.profile.max_consecutive_losses - 1:
            return RiskCheck(name="consecutive_losses", status="warn", score=7, message=f"Agent has {streak} consecutive losses")
        return RiskCheck(name="consecutive_losses", status="pass", score=0, message="No dangerous loss streak detected")

    def _check_overtrading(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        window_start = intent.timestamp - timedelta(minutes=15)
        recent = [trade for trade in context.recent_trades if trade.get("agent_id") == intent.agent_id and trade.get("parsed_timestamp") and trade["parsed_timestamp"] >= window_start]
        if len(recent) >= self.profile.max_trades_per_15m:
            return RiskCheck(name="overtrading", status="fail", score=16, message=f"{len(recent)} trades in the last 15 minutes")
        if len(recent) >= max(1, self.profile.max_trades_per_15m - 2):
            return RiskCheck(name="overtrading", status="warn", score=7, message=f"Trading frequency is elevated: {len(recent)} trades in 15 minutes")
        return RiskCheck(name="overtrading", status="pass", score=0, message="Trading frequency is normal")

    def _check_revenge_trading(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        streak = self._loss_streak(context.recent_trades)
        recent_sizes = [trade.get("notional", 0) for trade in context.recent_trades[-5:] if trade.get("agent_id") == intent.agent_id]
        avg_recent = sum(recent_sizes) / len(recent_sizes) if recent_sizes else 0
        new_notional = intent.quantity * context.current_price * intent.leverage
        if streak >= 2 and avg_recent and new_notional > avg_recent * 1.6:
            return RiskCheck(name="revenge_trading_detector", status="fail", score=24, message="Position size increased sharply after consecutive losses")
        if streak >= 1 and avg_recent and new_notional > avg_recent * 1.35:
            return RiskCheck(name="revenge_trading_detector", status="warn", score=10, message="Possible loss-chasing behavior detected")
        return RiskCheck(name="revenge_trading_detector", status="pass", score=0, message="No revenge trading pattern detected")

    def _check_volatility(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        if context.recent_volatility >= self.profile.volatility_block:
            return RiskCheck(name="volatility_risk", status="fail", score=22, message=f"Recent volatility {context.recent_volatility:.2%} is extreme")
        if context.recent_volatility >= self.profile.volatility_warn:
            return RiskCheck(name="volatility_risk", status="warn", score=9, message=f"Recent volatility {context.recent_volatility:.2%} is elevated")
        return RiskCheck(name="volatility_risk", status="pass", score=0, message="Volatility is normal")

    def _check_confidence_mismatch(self, intent: TradeIntent, context: RiskContext) -> RiskCheck:
        notional_ratio = intent.quantity * context.current_price * intent.leverage / max(context.account.equity, 1)
        if intent.confidence < self.profile.min_confidence and notional_ratio > 0.15:
            return RiskCheck(name="confidence_mismatch", status="fail", score=14, message="Low-confidence intent has an oversized notional")
        if intent.confidence < 0.5 and notional_ratio > 0.2:
            return RiskCheck(name="confidence_mismatch", status="warn", score=7, message="Confidence is low relative to trade size")
        return RiskCheck(name="confidence_mismatch", status="pass", score=0, message="Confidence and trade size are aligned")

    @staticmethod
    def _loss_streak(trades: list[dict]) -> int:
        streak = 0
        for trade in reversed(trades):
            pnl = trade.get("realized_pnl", 0)
            if pnl < 0:
                streak += 1
            elif pnl > 0:
                break
        return streak
