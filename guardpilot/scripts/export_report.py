from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
report = ROOT / "reports" / "demo_report.json"
if not report.exists():
    raise SystemExit("Run scripts/replay.py first")
print(json.dumps(json.loads(report.read_text(encoding="utf-8")), indent=2, ensure_ascii=False))
