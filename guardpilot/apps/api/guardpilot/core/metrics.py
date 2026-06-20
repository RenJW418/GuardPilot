from __future__ import annotations

from statistics import mean, pstdev


def max_drawdown(equity_curve: list[dict]) -> float:
    peak = 0.0
    max_dd = 0.0
    for point in equity_curve:
        equity = float(point["equity"])
        peak = max(peak, equity)
        if peak:
            max_dd = max(max_dd, (peak - equity) / peak)
    return max_dd


def win_rate(trades: list[dict]) -> float:
    closed = [trade for trade in trades if trade.get("realized_pnl", 0) != 0]
    if not closed:
        return 0.0
    wins = [trade for trade in closed if trade.get("realized_pnl", 0) > 0]
    return len(wins) / len(closed)


def profit_factor(trades: list[dict]) -> float:
    gross_profit = sum(max(0, trade.get("realized_pnl", 0)) for trade in trades)
    gross_loss = abs(sum(min(0, trade.get("realized_pnl", 0)) for trade in trades))
    if gross_loss == 0:
        return gross_profit if gross_profit else 0.0
    return gross_profit / gross_loss


def sharpe_like(equity_curve: list[dict]) -> float:
    if len(equity_curve) < 3:
        return 0.0
    equities = [float(point["equity"]) for point in equity_curve]
    returns = [(equities[i] - equities[i - 1]) / equities[i - 1] for i in range(1, len(equities)) if equities[i - 1]]
    if len(returns) < 2:
        return 0.0
    vol = pstdev(returns)
    if vol == 0:
        return 0.0
    return mean(returns) / vol
