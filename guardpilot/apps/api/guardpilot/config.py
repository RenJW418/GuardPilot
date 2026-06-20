from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = ROOT_DIR / "guardpilot.db"
DEFAULT_LOG_DIR = ROOT_DIR / "samples" / "outputs"


class Settings:
    app_name: str = "GuardPilot"
    db_path: Path = Path(os.getenv("GUARDPILOT_DB_PATH", DEFAULT_DB_PATH))
    log_dir: Path = Path(os.getenv("GUARDPILOT_LOG_DIR", DEFAULT_LOG_DIR))
    initial_balance: float = float(os.getenv("GUARDPILOT_INITIAL_BALANCE", "10000"))
    fee_rate: float = float(os.getenv("GUARDPILOT_FEE_RATE", "0.0006"))
    slippage_bps: float = float(os.getenv("GUARDPILOT_SLIPPAGE_BPS", "2"))


settings = Settings()
