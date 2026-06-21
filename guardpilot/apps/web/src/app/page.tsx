import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AgentTable } from '../components/AgentTable';
import { ApiLogTable } from '../components/ApiLogTable';
import { AuditCoverageCard, ApiLatencyPanel, DecisionBreakdown, ImpactComparison, RiskRuleBreakdown, RiskTrend } from '../components/DashboardInsights';
import { EquityCurve } from '../components/EquityCurve';
import { ReplayPanel } from '../components/ReplayPanel';
import { RiskScoreCard } from '../components/RiskScoreCard';
import { TradeTimeline } from '../components/TradeTimeline';
import { fetchJson, fetchLatestReport, runReplay } from '../lib/api';
import type { AgentSummary, ApiLog, ReplayScenario, ReplaySummary, RiskEvent, RiskReport, Trade } from '../lib/types';
import './styles.css';

function pct(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(2)}%`;
}

function money(value?: number, signed = false) {
  if (value === undefined || value === null) return '—';
  return `${signed && value >= 0 ? '+' : ''}${value.toFixed(2)} USDT`;
}

function shortTime(timestamp: string) {
  return timestamp.includes('T') ? timestamp.slice(11, 19) : timestamp;
}

const evidenceArtifacts = [
  ['Sample Agent inputs', 'samples/agents/demo_momentum_signals.jsonl'],
  ['API call log', 'samples/outputs/sample_api_calls.jsonl'],
  ['Paper trade log', 'samples/outputs/sample_trade_log.jsonl'],
  ['Risk events', 'samples/outputs/sample_risk_events.jsonl'],
  ['Risk report', 'samples/outputs/sample_risk_report.json'],
  ['Evidence manifest', 'samples/outputs/evidence_manifest.json'],
];

function App() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [apiLogs, setApiLogs] = useState<ApiLog[]>([]);
  const [riskEvents, setRiskEvents] = useState<RiskEvent[]>([]);
  const [summary, setSummary] = useState<ReplaySummary | null>(null);
  const [latestReport, setLatestReport] = useState<RiskReport | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<ReplayScenario>('btc_momentum_crash');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    try {
      const [nextTrades, nextAgents, nextLogs, nextEvents, report] = await Promise.all([
        fetchJson<Trade[]>('/api/v1/trades'),
        fetchJson<AgentSummary[]>('/api/v1/agents'),
        fetchJson<ApiLog[]>('/api/v1/api-logs'),
        fetchJson<RiskEvent[]>('/api/v1/risk-events'),
        fetchLatestReport().catch(() => null),
      ]);
      setTrades(nextTrades);
      setAgents(nextAgents);
      setApiLogs(nextLogs);
      setRiskEvents(nextEvents);
      setLatestReport(report);
      setError('');
    } catch (err) {
      setError('Backend is not ready. From repo root run: npm run dev. API-only fallback: npm run dev:api. Evidence fallback: npm run replay && npm run evidence.');
    }
  }

  useEffect(() => { load(); }, []);

  const activeReport = summary?.risk_report ?? latestReport;
  const impact = summary?.impact_metrics ?? activeReport?.impact_metrics;
  const latestEquity = trades[0]?.equity_after ?? activeReport?.final_equity_with_guard ?? 10000;
  const pnl = latestEquity - 10000;
  const avgRisk = useMemo(() => {
    if (trades.length) return trades.reduce((sum, trade) => sum + trade.risk_score, 0) / trades.length;
    return activeReport?.average_risk_score;
  }, [activeReport, trades]);
  const displayedRiskEvents: RiskEvent[] = summary?.risk_events ?? activeReport?.risk_events ?? riskEvents;
  const blocked = summary?.blocked ?? activeReport?.blocked ?? (displayedRiskEvents.filter((event) => event.decision === 'BLOCK').length || trades.filter((trade) => trade.decision === 'BLOCK').length);
  const topFindings = activeReport?.top_risk_findings ?? [];
  const hasEvidence = Boolean(summary || activeReport || trades.length || apiLogs.length || riskEvents.length);

  async function handleReplay() {
    setLoading(true);
    try {
      const result = await runReplay(selectedScenario);
      setSummary(result);
      setLatestReport(result.risk_report ?? null);
      await load();
    } catch (err) {
      setError('Replay failed. Start the backend first with npm run dev:api, or regenerate evidence from CLI with npm run replay && npm run evidence.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section className="hero">
        <div>
          <div className="eyebrow">Bitget AI Base Camp · Trading Infra</div>
          <h1>GuardPilot</h1>
          <p className="subtitle">A pre-trade risk gateway, paper trading sandbox, and reproducible audit layer between autonomous trading Agents and execution tools.</p>
          <div className="hero-tags">
            <span>Agent Hub / Playbook safety gate</span>
            <span>Paper trading only</span>
            <span>No live exchange orders</span>
          </div>
        </div>
        <div className="status">Auditable · Replayable · Bitget-ready dry run</div>
      </section>

      <section className="grid proof-grid">
        <div className="card proof-card"><span>Default scenario</span><strong>42 intents</strong><small>same Agent stream, same market tape</small></div>
        <div className="card proof-card"><span>Decisions</span><strong>16 / 4 / 22</strong><small>allowed / warned / blocked</small></div>
        <div className="card proof-card"><span>Max drawdown</span><strong>2.60% → 0.70%</strong><small>with GuardPilot enabled</small></div>
        <div className="card proof-card"><span>Audit trail</span><strong>110 records</strong><small>API + trade + risk events</small></div>
      </section>

      <section className="judge-flow card wide">
        <div className="section-title">Judge Demo Flow</div>
        <div className="flow-steps">
          <span>1. Run deterministic replay</span>
          <span>2. Confirm 42 Agent intents</span>
          <span>3. Verify 16 / 4 / 22 decisions</span>
          <span>4. Confirm 2.60% → 0.70% drawdown</span>
          <span>5. Inspect Risk Events + API Logs</span>
        </div>
      </section>

      {error && <div className="error">{error}</div>}

      <section className="grid metrics">
        <RiskScoreCard score={avgRisk} hasData={avgRisk !== undefined} />
        <div className="card metric"><div className="eyebrow">Current Equity</div><strong>{money(latestEquity)}</strong><span>{hasEvidence ? `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)} PnL` : 'initial paper balance'}</span></div>
        <div className="card metric"><div className="eyebrow">Blocked Intents</div><strong>{hasEvidence ? blocked : '—'}</strong><span>dangerous actions stopped before execution</span></div>
        <div className="card metric"><div className="eyebrow">Impact Evidence</div><strong>{impact ? `${pct(activeReport?.max_drawdown_without_guard ?? summary?.max_drawdown_without_guard)} → ${pct(activeReport?.max_drawdown_with_guard ?? summary?.max_drawdown_with_guard)}` : 'Run Replay'}</strong><span>{impact ? `+${impact.equity_improvement_usdt.toFixed(2)} USDT vs unguarded replay · ${pct(impact.max_drawdown_reduction_relative)} DD reduction` : 'drawdown reduction proof'}</span></div>
      </section>

      <section className="grid two">
        <ReplayPanel onReplay={handleReplay} loading={loading} summary={summary} scenario={selectedScenario} onScenarioChange={setSelectedScenario} />
        <AuditCoverageCard summary={summary} trades={trades} apiLogs={apiLogs} riskEvents={displayedRiskEvents} />
      </section>

      <section className="grid two">
        <DecisionBreakdown summary={summary} trades={trades} apiLogs={apiLogs} />
        <ImpactComparison summary={summary} report={activeReport} />
      </section>

      <RiskTrend trades={trades} apiLogs={apiLogs} />

      <section className="grid two">
        <RiskRuleBreakdown riskEvents={summary?.risk_events ?? activeReport?.risk_events ?? []} />
        <ApiLatencyPanel apiLogs={summary?.api_calls ?? apiLogs} />
      </section>

      <section className="grid two">
        <AgentTable agents={agents} />
        <div className="card">
          <div className="section-title">Evidence & Audit Pack</div>
          <p>Trading Infra requires verifiable usage records. GuardPilot regenerates sample inputs, outputs, logs, reports, and a hash manifest.</p>
          <div className="artifact-list">
            {evidenceArtifacts.map(([label, path]) => (
              <div key={path}><span>{label}</span><strong>{path}</strong></div>
            ))}
          </div>
          {impact && <p className="muted">Latest run generated {impact.audit_records_generated} audit records.</p>}
        </div>
        <div className="card">
          <div className="section-title">Top Risk Findings</div>
          {topFindings.length ? (
            <ul className="findings-list">
              {topFindings.slice(0, 5).map((finding) => <li key={finding}>{finding}</li>)}
            </ul>
          ) : (
            <div className="empty-panel">Run replay to surface overtrading, revenge trading, leverage, volatility, and confidence-mismatch findings.</div>
          )}
        </div>
      </section>

      <section className="card wide integration-card">
        <div>
          <div className="section-title">Bitget Integration Boundary</div>
          <p>GuardPilot is designed to sit before Bitget Agent Hub / Playbook / MCP-style order tools. The hackathon MVP returns a Bitget-ready dry-run payload only after `ALLOW` or `WARN`; `BLOCK` removes the forwarding payload entirely.</p>
        </div>
        <div className="integration-flow">
          <span>Agent signal</span><span>GuardPilot risk score</span><span>ALLOW / WARN / BLOCK</span><span>Dry-run payload or stop</span>
        </div>
      </section>

      <EquityCurve trades={trades} />
      <TradeTimeline trades={trades} />

      <section className="card wide">
        <div className="section-title">Risk Events</div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Time</th><th>Agent</th><th>Symbol</th><th>Decision</th><th>Risk</th><th>Message</th><th>Failed checks</th></tr></thead>
            <tbody>
              {displayedRiskEvents.slice(0, 10).map((event, idx) => (
                <tr key={idx}>
                  <td title={event.timestamp}>{shortTime(event.timestamp)}</td>
                  <td>{event.agent_id}</td>
                  <td>{event.symbol}</td>
                  <td><span className={`pill ${event.decision.toLowerCase()}`}>{event.decision}</span></td>
                  <td>{event.risk_score}</td>
                  <td>{event.message}</td>
                  <td>
                    <div className="check-list">
                      {(event.checks ?? []).slice(0, 4).map((check, checkIdx) => (
                        <span key={checkIdx} className={`check-chip ${check.status}`}>{check.name}: {check.status} (+{check.score})</span>
                      ))}
                      {!event.checks?.length && <span className="muted">Run replay or load latest report to view rule checks</span>}
                    </div>
                  </td>
                </tr>
              ))}
              {!displayedRiskEvents.length && (
                <tr><td colSpan={7} className="empty-state">Run replay to view WARN/BLOCK decisions and failed checks.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <ApiLogTable logs={apiLogs} />
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
