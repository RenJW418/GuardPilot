from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from guardpilot.config import settings
from guardpilot.storage.database import Database
from guardpilot.storage.jsonl_logger import JsonlLogger


db = Database(settings.db_path)
logger = JsonlLogger(settings.log_dir)


def record_api_call(record: dict) -> None:
    db.insert("api_logs", record)
    logger.append("sample_api_calls.jsonl", record)


def reset_runtime_records() -> None:
    db.clear_runtime()


def replace_runtime_records(trades: list[dict], api_calls: list[dict], risk_events: list[dict]) -> None:
    db.clear_runtime()
    for trade in trades:
        db_record = {key: value for key, value in trade.items() if key in {
            "timestamp", "agent_id", "symbol", "side", "price", "quantity", "notional", "fee",
            "realized_pnl", "balance_before", "balance_after", "equity_after", "risk_score", "decision", "reason"
        }}
        db.insert("trades", db_record)
    for api_call in api_calls:
        db.insert("api_logs", api_call)
    for event in risk_events:
        db_record = {key: value for key, value in event.items() if key in {
            "timestamp", "agent_id", "symbol", "decision", "risk_score", "risk_level", "message"
        }}
        db.insert("risk_events", db_record)


def record_trade(record: dict) -> None:
    db_record = {key: value for key, value in record.items() if key in {
        "timestamp", "agent_id", "symbol", "side", "price", "quantity", "notional", "fee",
        "realized_pnl", "balance_before", "balance_after", "equity_after", "risk_score", "decision", "reason"
    }}
    db.insert("trades", db_record)
    logger.append("sample_trade_log.jsonl", record)


def record_risk_event(record: dict) -> None:
    db.insert("risk_events", record)
    logger.append("sample_risk_events.jsonl", record)


def list_api_logs(limit: int = 200) -> list[dict]:
    return db.list("api_logs", limit=limit)


def list_trades(limit: int = 200) -> list[dict]:
    return db.list("trades", limit=limit)


def list_risk_events(limit: int = 200) -> list[dict]:
    return db.list("risk_events", limit=limit)
