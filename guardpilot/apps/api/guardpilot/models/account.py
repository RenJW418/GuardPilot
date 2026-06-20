from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0

    @property
    def direction(self) -> str:
        if self.quantity > 0:
            return "LONG"
        if self.quantity < 0:
            return "SHORT"
        return "FLAT"


@dataclass
class Account:
    balance: float = 10000.0
    equity: float = 10000.0
    realized_pnl: float = 0.0
    peak_equity: float = 10000.0
    max_drawdown: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)
    equity_curve: list[dict] = field(default_factory=list)

    def position_for(self, symbol: str) -> Position:
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]

    def mark_equity(self, timestamp: str, prices: dict[str, float]) -> float:
        unrealized = 0.0
        for symbol, position in self.positions.items():
            price = prices.get(symbol, position.avg_price)
            unrealized += (price - position.avg_price) * position.quantity
        self.equity = self.balance + unrealized
        self.peak_equity = max(self.peak_equity, self.equity)
        if self.peak_equity:
            self.max_drawdown = max(self.max_drawdown, (self.peak_equity - self.equity) / self.peak_equity)
        self.equity_curve.append({"timestamp": timestamp, "equity": round(self.equity, 4)})
        return self.equity
