from __future__ import annotations

import csv
import hashlib
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


BITGET_SPOT_CANDLES_ENDPOINT = "https://api.bitget.com/api/v2/spot/market/candles"


@dataclass(frozen=True)
class Candle:
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_csv_row(self) -> dict[str, str]:
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "open": f"{self.open:.8f}".rstrip("0").rstrip("."),
            "high": f"{self.high:.8f}".rstrip("0").rstrip("."),
            "low": f"{self.low:.8f}".rstrip("0").rstrip("."),
            "close": f"{self.close:.8f}".rstrip("0").rstrip("."),
            "volume": f"{self.volume:.8f}".rstrip("0").rstrip("."),
        }


def fetch_spot_candles(symbol: str = "BTCUSDT", granularity: str = "1min", limit: int = 100) -> tuple[list[Candle], dict[str, Any]]:
    """Fetch public Bitget spot candles and normalize them for GuardPilot replay.

    This uses Bitget public market data only. It does not require API keys and it
    never touches private account or order endpoints.
    """
    normalized_symbol = symbol.upper().replace("-", "")
    params = {
        "symbol": normalized_symbol,
        "granularity": granularity,
        "limit": str(limit),
    }
    url = f"{BITGET_SPOT_CANDLES_ENDPOINT}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "GuardPilot/0.1 public-market-snapshot"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw_body = response.read().decode("utf-8")
    payload = json.loads(raw_body)
    if payload.get("code") not in {"00000", "0", 0, None}:
        raise ValueError(f"Bitget public market API returned error: {payload}")
    candles = parse_bitget_candles(payload.get("data", []), normalized_symbol)
    if not candles:
        raise ValueError("Bitget public market API returned no candle rows")
    metadata = {
        "source": "Bitget public market API",
        "endpoint": BITGET_SPOT_CANDLES_ENDPOINT,
        "request_url": url,
        "request_params": params,
        "symbol": normalized_symbol,
        "granularity": granularity,
        "rows": len(candles),
        "exchange_time_start": candles[0].timestamp,
        "exchange_time_end": candles[-1].timestamp,
        "response_code": payload.get("code"),
        "response_request_time": payload.get("requestTime"),
        "license_note": "Public market data fetched from Bitget. No private account data, API keys, real funds, or live orders are used.",
    }
    return candles, metadata


def parse_bitget_candles(rows: Iterable[Any], symbol: str) -> list[Candle]:
    candles: list[Candle] = []
    for row in rows:
        if isinstance(row, dict):
            timestamp_ms = row.get("ts") or row.get("timestamp") or row.get("time")
            open_price = row.get("open")
            high = row.get("high")
            low = row.get("low")
            close = row.get("close")
            volume = row.get("baseVolume") or row.get("volume") or row.get("baseVol") or row.get("vol")
        else:
            if len(row) < 6:
                continue
            timestamp_ms, open_price, high, low, close, volume = row[:6]
        candles.append(
            Candle(
                timestamp=_timestamp_ms_to_iso(timestamp_ms),
                symbol=symbol,
                open=float(open_price),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume),
            )
        )
    return sorted(candles, key=lambda candle: candle.timestamp)


def write_candles_csv(candles: list[Candle], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "symbol", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for candle in candles:
            writer.writerow(candle.to_csv_row())


def write_provenance(metadata: dict[str, Any], csv_path: Path, provenance_path: Path) -> dict[str, Any]:
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    enriched = {
        **metadata,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "csv_path": str(csv_path),
        "sha256": sha256(csv_path),
        "bytes": csv_path.stat().st_size,
        "schema": ["timestamp", "symbol", "open", "high", "low", "close", "volume"],
        "guardpilot_data_mode": "recorded_bitget_public_snapshot",
        "execution_mode": "paper_trading_only",
        "live_orders": False,
    }
    provenance_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return enriched


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _timestamp_ms_to_iso(value: Any) -> str:
    timestamp_ms = int(float(value))
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")
