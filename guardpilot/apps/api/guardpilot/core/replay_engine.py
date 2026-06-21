from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from guardpilot.config import ROOT_DIR, settings
from guardpilot.core.metrics import max_drawdown, profit_factor, sharpe_like, win_rate
from guardpilot.core.paper_engine import PaperTradingEngine
from guardpilot.core.risk_engine import RiskContext, RiskEngine, RiskProfile
from guardpilot.core.scoring import grade_for
from guardpilot.demo_agents.momentum_agent import generate_market_csv, generate_signal_jsonl
from guardpilot.models.account import Account
from guardpilot.models.intent import TradeIntent
from guardpilot.storage.jsonl_logger import JsonlLogger
from guardpilot.storage.repositories import replace_runtime_records


class ReplayEngine:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = root_dir or ROOT_DIR
        self.paper_engine = PaperTradingEngine()

    def run(self, scenario_path: str | Path) -> dict[str, Any]:
        scenario_file = self._resolve(scenario_path)
        scenario = json.loads(scenario_file.read_text(encoding="utf-8"))
        self._ensure_sample_inputs(scenario)
        market_rows = self._load_market(self._resolve(scenario["market_data"]))
        signals = self._load_signals(self._resolve(scenario["agent_signals"]))
        profile = self._load_profile(self._resolve(scenario["risk_profile"]))

        output_paths = {key: self._resolve(path) for key, path in scenario["outputs"].items()}
        for path in output_paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()

        log_dir = output_paths["trade_log"].parent
        logger = JsonlLogger(log_dir)

        guarded_account = Account(
            balance=float(scenario["initial_balance"]),
            equity=float(scenario["initial_balance"]),
            peak_equity=float(scenario["initial_balance"]),
        )
        baseline_account = Account(
            balance=float(scenario["initial_balance"]),
            equity=float(scenario["initial_balance"]),
            peak_equity=float(scenario["initial_balance"]),
        )
        risk_engine = RiskEngine(profile)
        guarded_trades: list[dict[str, Any]] = []
        api_calls: list[dict[str, Any]] = []
        risk_events: list[dict[str, Any]] = []
        decisions = {"ALLOW": 0, "WARN": 0, "BLOCK": 0}

        prices = {row["timestamp"]: float(row["close"]) for row in market_rows}

        for index, signal in enumerate(signals, start=1):
            intent = TradeIntent(**signal)
            timestamp = intent.normalized_timestamp()
            market = self._nearest_market_row(market_rows, timestamp)
            price = float(market["close"])
            volatility = self._recent_volatility(market_rows, market["timestamp"])

            baseline_decision = "ALLOW"
            self.paper_engine.execute(intent, baseline_account, price, 0, baseline_decision)

            context = RiskContext(
                account=guarded_account,
                recent_trades=guarded_trades,
                current_price=price,
                recent_volatility=volatility,
                initial_balance=float(scenario["initial_balance"]),
            )
            risk = risk_engine.evaluate(intent, context)
            decisions[risk.decision] += 1

            simulated_order_id = None
            if risk.decision == "BLOCK":
                trade_record = self.paper_engine.mark_only(
                    intent,
                    guarded_account,
                    price,
                    risk.risk_score,
                    risk.decision,
                    self._top_risk_message(risk.checks),
                )
            else:
                fill = self.paper_engine.execute(intent, guarded_account, price, risk.risk_score, risk.decision)
                simulated_order_id = fill.order_id
                trade_record = fill.model_dump()

            trade_record["parsed_timestamp"] = intent.timestamp
            guarded_trades.append(trade_record)
            serializable_trade = {key: value for key, value in trade_record.items() if key != "parsed_timestamp"}
            logger.append(output_paths["trade_log"].name, serializable_trade)

            api_record = {
                "timestamp": timestamp,
                "method": "POST",
                "path": "/api/v1/intents",
                "agent_id": intent.agent_id,
                "status_code": 200,
                "latency_ms": 12 + index % 11,
                "decision": risk.decision,
                "risk_score": risk.risk_score,
            }
            api_calls.append(api_record)
            logger.append(output_paths["api_calls"].name, api_record)

            if risk.decision in {"WARN", "BLOCK"}:
                risk_event = {
                    "timestamp": timestamp,
                    "agent_id": intent.agent_id,
                    "symbol": intent.symbol,
                    "decision": risk.decision,
                    "risk_score": risk.risk_score,
                    "risk_level": risk.risk_level,
                    "message": self._top_risk_message(risk.checks),
                    "checks": [check.model_dump() for check in risk.checks if check.status != "pass"],
                }
                risk_events.append(risk_event)
                logger.append(output_paths.get("risk_events", log_dir / "sample_risk_events.jsonl").name, risk_event)

            guarded_account.mark_equity(timestamp, {intent.symbol: price})
            baseline_account.mark_equity(timestamp, {intent.symbol: price})

        clean_guarded_trades = [{key: value for key, value in trade.items() if key != "parsed_timestamp"} for trade in guarded_trades]
        average_risk_score = sum(trade["risk_score"] for trade in guarded_trades) / max(len(guarded_trades), 1)
        blocked_ratio = decisions["BLOCK"] / max(len(signals), 1)
        residual_risk_score = max(10, average_risk_score - blocked_ratio * 60)
        baseline_drawdown = max_drawdown(baseline_account.equity_curve)
        guarded_drawdown = max_drawdown(guarded_account.equity_curve)
        equity_improvement = guarded_account.equity - baseline_account.equity
        drawdown_reduction = baseline_drawdown - guarded_drawdown
        impact_metrics = {
            "equity_improvement_usdt": round(equity_improvement, 4),
            "max_drawdown_reduction_points": round(drawdown_reduction * 100, 4),
            "max_drawdown_reduction_relative": round(drawdown_reduction / baseline_drawdown, 4) if baseline_drawdown else 0,
            "blocked_intent_rate": round(blocked_ratio, 4),
            "audit_records_generated": len(clean_guarded_trades) + len(api_calls) + len(risk_events),
        }
        report = {
            "report_id": f"rep_{scenario['scenario_id']}_001",
            "scenario_id": scenario["scenario_id"],
            "agent_id": signals[0]["agent_id"] if signals else "unknown",
            "initial_balance": scenario["initial_balance"],
            "final_equity_without_guard": round(baseline_account.equity, 4),
            "final_equity_with_guard": round(guarded_account.equity, 4),
            "max_drawdown_without_guard": round(baseline_drawdown, 6),
            "max_drawdown_with_guard": round(guarded_drawdown, 6),
            "total_intents": len(signals),
            "allowed": decisions["ALLOW"],
            "warned": decisions["WARN"],
            "blocked": decisions["BLOCK"],
            "risk_grade": grade_for(residual_risk_score),
            "average_risk_score": round(average_risk_score, 2),
            "residual_risk_score_after_guard": round(residual_risk_score, 2),
            "impact_metrics": impact_metrics,
            "win_rate": round(win_rate(clean_guarded_trades), 4),
            "profit_factor": round(profit_factor(clean_guarded_trades), 4),
            "sharpe_like": round(sharpe_like(guarded_account.equity_curve), 4),
            "equity_curve": guarded_account.equity_curve,
            "risk_events": risk_events,
            "top_risk_findings": self._top_findings(risk_events, decisions),
            "trade_log_path": str(output_paths["trade_log"].relative_to(self.root_dir)),
            "api_call_log_path": str(output_paths["api_calls"].relative_to(self.root_dir)),
            "risk_event_log_path": str(output_paths.get("risk_events", log_dir / "sample_risk_events.jsonl").relative_to(self.root_dir)),
        }

        manifest_path = output_paths["summary"].parent / "evidence_manifest.json"
        report["evidence_manifest_path"] = str(manifest_path.relative_to(self.root_dir))
        output_paths["risk_report"].write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        summary = {
            "scenario_id": scenario["scenario_id"],
            "total_intents": len(signals),
            "allowed": decisions["ALLOW"],
            "warned": decisions["WARN"],
            "blocked": decisions["BLOCK"],
            "final_equity_with_guard": report["final_equity_with_guard"],
            "final_equity_without_guard": report["final_equity_without_guard"],
            "max_drawdown_with_guard": report["max_drawdown_with_guard"],
            "max_drawdown_without_guard": report["max_drawdown_without_guard"],
            "risk_grade": report["risk_grade"],
            "impact_metrics": impact_metrics,
            "report_path": str(output_paths["risk_report"].relative_to(self.root_dir)),
            "evidence_manifest_path": str(manifest_path.relative_to(self.root_dir)),
        }
        output_paths["summary"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        manifest = self._build_evidence_manifest(
            scenario=scenario,
            scenario_file=scenario_file,
            market_file=self._resolve(scenario["market_data"]),
            signals_file=self._resolve(scenario["agent_signals"]),
            profile_file=self._resolve(scenario["risk_profile"]),
            output_paths=output_paths,
            report=report,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        reports_dir = self.root_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / "demo_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (reports_dir / "demo_report.html").write_text(self._render_html_report(report), encoding="utf-8")
        replace_runtime_records(clean_guarded_trades, api_calls, risk_events)
        return {**summary, "risk_report": report, "trades": clean_guarded_trades, "api_calls": api_calls, "risk_events": risk_events}

    def _resolve(self, path: str | Path) -> Path:
        path = Path(path)
        if path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed in replay scenarios: {path}")
        resolved = (self.root_dir / path).resolve()
        root = self.root_dir.resolve()
        if resolved != root and root not in resolved.parents:
            raise ValueError(f"Replay path escapes project root: {path}")
        return resolved

    def _build_evidence_manifest(
        self,
        *,
        scenario: dict[str, Any],
        scenario_file: Path,
        market_file: Path,
        signals_file: Path,
        profile_file: Path,
        output_paths: dict[str, Path],
        report: dict[str, Any],
    ) -> dict[str, Any]:
        evidence_files = {
            "scenario": scenario_file,
            "market_data": market_file,
            "agent_signals": signals_file,
            "risk_profile": profile_file,
            "trade_log": output_paths["trade_log"],
            "api_calls": output_paths["api_calls"],
            "risk_events": output_paths.get("risk_events", output_paths["trade_log"].parent / "sample_risk_events.jsonl"),
            "risk_report": output_paths["risk_report"],
            "summary": output_paths["summary"],
        }
        files = {}
        for key, path in evidence_files.items():
            files[key] = {
                "path": str(path.relative_to(self.root_dir)),
                "sha256": self._sha256(path),
                "bytes": path.stat().st_size,
            }
            if path.suffix == ".jsonl":
                files[key]["rows"] = self._count_nonempty_lines(path)
            elif path.suffix == ".csv":
                files[key]["rows"] = self._count_csv_rows(path)

        return {
            "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "scenario_id": scenario["scenario_id"],
            "initial_balance": scenario["initial_balance"],
            "totals": {
                "total_intents": report["total_intents"],
                "allowed": report["allowed"],
                "warned": report["warned"],
                "blocked": report["blocked"],
                "risk_events": len(report["risk_events"]),
                "audit_records_generated": report["impact_metrics"]["audit_records_generated"],
            },
            "impact_metrics": report["impact_metrics"],
            "files": files,
        }

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _count_nonempty_lines(path: Path) -> int:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())

    @staticmethod
    def _count_csv_rows(path: Path) -> int:
        with path.open("r", encoding="utf-8") as handle:
            return max(sum(1 for _ in handle) - 1, 0)

    def _ensure_sample_inputs(self, scenario: dict[str, Any]) -> None:
        market_path = self._resolve(scenario["market_data"])
        signal_path = self._resolve(scenario["agent_signals"])
        if not market_path.exists():
            symbol = "ETHUSDT" if "eth" in market_path.name.lower() else "BTCUSDT"
            start_price = 3500 if symbol == "ETHUSDT" else 65000
            generate_market_csv(market_path, symbol=symbol, start_price=start_price)
        if not signal_path.exists():
            generate_signal_jsonl(signal_path)
            if "risky" in signal_path.name:
                shutil.copyfile(self.root_dir / "samples" / "agents" / "demo_momentum_signals.jsonl", signal_path)

    @staticmethod
    def _load_market(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _load_signals(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    @staticmethod
    def _load_profile(path: Path) -> RiskProfile:
        data: dict[str, Any] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "profile":
                continue
            try:
                if "." in value:
                    data[key] = float(value)
                else:
                    data[key] = int(value)
            except ValueError:
                data[key] = value
        return RiskProfile(**data)

    @staticmethod
    def _nearest_market_row(rows: list[dict[str, str]], timestamp: str) -> dict[str, str]:
        for row in rows:
            if row["timestamp"] >= timestamp:
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

    @staticmethod
    def _top_risk_message(checks) -> str:
        failing = [check for check in checks if check.status == "fail"]
        warning = [check for check in checks if check.status == "warn"]
        chosen = failing or warning
        if not chosen:
            return "All risk checks passed"
        return max(chosen, key=lambda check: check.score).message

    @staticmethod
    def _top_findings(risk_events: list[dict[str, Any]], decisions: dict[str, int]) -> list[str]:
        findings = []
        if decisions["BLOCK"]:
            findings.append(f"Blocked {decisions['BLOCK']} high-risk intents before simulated execution")
        if decisions["WARN"]:
            findings.append(f"Flagged {decisions['WARN']} elevated-risk intents for audit")
        messages = []
        for event in risk_events:
            if event["message"] not in messages:
                messages.append(event["message"])
        findings.extend(messages[:3])
        return findings or ["No elevated-risk behavior detected in this scenario"]

    @staticmethod
    def _render_html_report(report: dict[str, Any]) -> str:
        impact = report["impact_metrics"]
        return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>GuardPilot Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; background: #0f172a; color: #e2e8f0; }}
    .card {{ background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 20px; margin: 16px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
    .metric {{ background: #1e293b; padding: 16px; border-radius: 12px; }}
    .label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 8px; }}
    .positive {{ color: #86efac; }}
  </style>
</head>
<body>
  <h1>GuardPilot Replay Report</h1>
  <p>Scenario: {report['scenario_id']} · Agent: {report['agent_id']}</p>
  <div class=\"grid\">
    <div class=\"metric\"><div class=\"label\">Equity Improvement</div><div class=\"value positive\">+{impact['equity_improvement_usdt']} USDT</div></div>
    <div class=\"metric\"><div class=\"label\">Drawdown Reduction</div><div class=\"value positive\">{impact['max_drawdown_reduction_points']} pts</div></div>
    <div class=\"metric\"><div class=\"label\">Blocked Intent Rate</div><div class=\"value\">{impact['blocked_intent_rate']:.1%}</div></div>
    <div class=\"metric\"><div class=\"label\">Audit Records</div><div class=\"value\">{impact['audit_records_generated']}</div></div>
  </div>
  <div class=\"grid\">
    <div class=\"metric\"><div class=\"label\">Final Equity With Guard</div><div class=\"value\">{report['final_equity_with_guard']}</div></div>
    <div class=\"metric\"><div class=\"label\">Final Equity Without Guard</div><div class=\"value\">{report['final_equity_without_guard']}</div></div>
    <div class=\"metric\"><div class=\"label\">Blocked</div><div class=\"value\">{report['blocked']}</div></div>
    <div class=\"metric\"><div class=\"label\">Risk Grade</div><div class=\"value\">{report['risk_grade']}</div></div>
  </div>
  <div class=\"card\">
    <h2>Why GuardPilot Helped</h2>
    <p>In this deterministic scenario, GuardPilot reduced max drawdown from {report['max_drawdown_without_guard']:.2%} to {report['max_drawdown_with_guard']:.2%} while generating a complete trade/API/risk-event audit trail.</p>
  </div>
  <div class=\"card\">
    <h2>Top Risk Findings</h2>
    <ul>{''.join(f'<li>{finding}</li>' for finding in report['top_risk_findings'])}</ul>
  </div>
  <div class=\"card\">
    <h2>Audit Evidence</h2>
    <p>Trade log: {report['trade_log_path']}</p>
    <p>API call log: {report['api_call_log_path']}</p>
  </div>
</body>
</html>
"""
