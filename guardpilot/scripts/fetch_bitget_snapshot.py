from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_SRC = ROOT / "apps" / "api"
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from guardpilot.integrations.bitget_market_data import fetch_spot_candles, write_candles_csv, write_provenance


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch a credential-free Bitget public market data snapshot for GuardPilot replay.")
    parser.add_argument("--symbol", default="BTCUSDT", help="Bitget spot symbol, e.g. BTCUSDT")
    parser.add_argument("--granularity", default="1min", help="Bitget candle granularity, e.g. 1min")
    parser.add_argument("--limit", type=int, default=100, help="Number of candles to request")
    parser.add_argument("--output", default="samples/market/bitget_btcusdt_1m.csv", help="Output CSV path under guardpilot/")
    parser.add_argument(
        "--provenance",
        default="samples/market/bitget_btcusdt_1m.provenance.json",
        help="Output provenance JSON path under guardpilot/",
    )
    args = parser.parse_args()

    output = (ROOT / args.output).resolve()
    provenance = (ROOT / args.provenance).resolve()
    if ROOT.resolve() not in output.parents or ROOT.resolve() not in provenance.parents:
        raise SystemExit("Output paths must stay inside the guardpilot project directory")

    candles, metadata = fetch_spot_candles(args.symbol, args.granularity, args.limit)
    write_candles_csv(candles, output)
    csv_for_metadata = output.relative_to(ROOT)
    enriched = write_provenance(metadata, csv_for_metadata, provenance)

    print("GuardPilot Bitget public market snapshot")
    print("========================================")
    print(f"Source:      {enriched['source']}")
    print(f"Symbol:      {enriched['symbol']}")
    print(f"Granularity: {enriched['granularity']}")
    print(f"Rows:        {enriched['rows']}")
    print(f"Time range:  {enriched['exchange_time_start']} -> {enriched['exchange_time_end']}")
    print(f"CSV:         {output.relative_to(ROOT)}")
    print(f"Provenance:  {provenance.relative_to(ROOT)}")
    print(f"SHA-256:     {enriched['sha256']}")
    print("Safety:      public market data only; no API keys, private account data, real funds, or live orders")


if __name__ == "__main__":
    main()
