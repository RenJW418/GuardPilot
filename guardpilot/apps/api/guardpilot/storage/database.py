from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS api_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  method TEXT NOT NULL,
  path TEXT NOT NULL,
  agent_id TEXT,
  status_code INTEGER NOT NULL,
  latency_ms INTEGER NOT NULL,
  decision TEXT,
  risk_score INTEGER
);

CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL,
  price REAL NOT NULL,
  quantity REAL NOT NULL,
  notional REAL NOT NULL,
  fee REAL NOT NULL,
  realized_pnl REAL NOT NULL,
  balance_before REAL NOT NULL,
  balance_after REAL NOT NULL,
  equity_after REAL NOT NULL,
  risk_score INTEGER NOT NULL,
  decision TEXT NOT NULL,
  reason TEXT
);

CREATE TABLE IF NOT EXISTS risk_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  decision TEXT NOT NULL,
  risk_score INTEGER NOT NULL,
  risk_level TEXT NOT NULL,
  message TEXT NOT NULL
);
"""


class Database:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def insert(self, table: str, record: dict[str, Any]) -> None:
        keys = list(record.keys())
        placeholders = ", ".join(["?"] * len(keys))
        columns = ", ".join(keys)
        values = [record[key] for key in keys]
        with self.connect() as conn:
            conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)

    def list(self, table: str, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    def clear_runtime(self) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM api_logs")
            conn.execute("DELETE FROM trades")
            conn.execute("DELETE FROM risk_events")
