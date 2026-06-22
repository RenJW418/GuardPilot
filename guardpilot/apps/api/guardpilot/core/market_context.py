from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from guardpilot.config import ROOT_DIR

DEFAULT_SNAPSHOT_PATH = ROOT_DIR / "samples" / "market" / "bitget_btcusdt_1m.csv"
DEFAULT_PROVENANCE_PATH = ROOT_DIR / "samples" / "market" / "bitget_btcusdt_1m.provenance.json"


@dataclass(frozen=True)
class MarketContext:
    symbol: str
    price: float
    recent_volatility: float
    source: str
    market_timestamp: str
    snapshot_path: str
    price_source: str

    def model_dump(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "recent_volatility": self.recent_volatility,
            "source": self.source,
            "market_timestamp": self.market_timestamp,
            "snapshot_path": self.snapshot_path,
            "price_source": self.price_source,
        }


class MarketContextProvider:
    def __init__(self, snapshot_path: Path | None = None, root_dir: Path | None = None):
        self.root_dir = root_dir or ROOT_DIR
        self.snapshot_path = snapshot_path or DEFAULT_SNAPSHOT_PATH
        self._rows: list[dict[str, str]] | None = None

    def for_intent(self, symbol: str, timestamp: datetime | None = None, price_hint: float | None = None) -> MarketContext:
        rows = self._load_rows()
        normalized_symbol = symbol.upper().replace("-", "")
        symbol_rows = [row for row in rows if row.get("symbol", "").upper().replace("-", "") == normalized_symbol]
        if not symbol_rows:
            raise ValueError(
                f"No Bitget public market snapshot rows for {normalized_symbol}. "
                f"Refresh or add a snapshot before evaluating this symbol."
            )
        market_row = self._nearest_row(symbol_rows, timestamp)
        snapshot_rel = self.snapshot_path.relative_to(self.root_dir)
        if price_hint is not None:
            price = float(price_hint)
            price_source = "agent_price_hint_with_bitget_snapshot_volatility"
        else:
            price = float(market_row["close"])
            price_source = "bitget_public_snapshot_close"
        return MarketContext(
            symbol=normalized_symbol,
            price=price,
            recent_volatility=self._recent_volatility(symbol_rows, market_row["timestamp"]),
            source="Bitget public market API snapshot",
            market_timestamp=market_row["timestamp"],
            snapshot_path=str(snapshot_rel),
            price_source=price_source,
        )

    def _load_rows(self) -> list[dict[str, str]]:
        if self._rows is not None:
            return self._rows
        if not self.snapshot_path.exists():
            raise FileNotFoundError(
                f"Missing Bitget public market snapshot: {self.snapshot_path.relative_to(self.root_dir)}. "
                "Run `python3 scripts/fetch_bitget_snapshot.py` from guardpilot/ or use the committed snapshot."
            )
        with self.snapshot_path.open("r", encoding="utf-8") as handle:
            self._rows = list(csv.DictReader(handle))
        if not self._rows:
            raise ValueError(f"Bitget public market snapshot has no rows: {self.snapshot_path.relative_to(self.root_dir)}")
        return self._rows

    @staticmethod
    def _nearest_row(rows: list[dict[str, str]], timestamp: datetime | None) -> dict[str, str]:
        if timestamp is None:
            return rows[-1]
        normalized = timestamp
        if normalized.tzinfo is None:
            normalized = normalized.replace(tzinfo=timezone.utc)
        target = normalized.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        first_timestamp = rows[0]["timestamp"]
        last_timestamp = rows[-1]["timestamp"]
        if target < first_timestamp or target > last_timestamp:
            raise ValueError(
                f"Intent timestamp {target} is outside the Bitget public market snapshot range "
                f"{first_timestamp} -> {last_timestamp}. Refresh the snapshot or use an in-range timestamp."
            )
        for row in rows:
            if row["timestamp"] >= target:
                return row
        return rows[-1]

    @staticmethod
    def _recent_volatility(rows: list[dict[str, str]], timestamp: str, lookback: int = 5) -> float:
        index = next((i for i, row in enumerate(rows) if row["timestamp"] == timestamp), len(rows) - 1)
        window = rows[max(0, index - lookback + 1): index + 1]
        if not window:
            return 0.0
        values = [(float(row["high"]) - float(row["low"])) / float(row["close"]) for row in window]
        return max(values)
