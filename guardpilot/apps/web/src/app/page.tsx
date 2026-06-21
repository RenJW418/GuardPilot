import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AgentTable } from '../components/AgentTable';
import { ApiLogTable } from '../components/ApiLogTable';
import { EquityCurve } from '../components/EquityCurve';
import { ReplayPanel } from '../components/ReplayPanel';
import { RiskScoreCard } from '../components/RiskScoreCard';
import { TradeTimeline } from '../components/TradeTimeline';
import { fetchJson, runReplay } from '../lib/api';
import type { AgentSummary, ApiLog, RiskEvent, Trade } from '../lib/types';
import './styles.css';

function pct(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(2)}%`;
}

function App() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [apiLogs, setApiLogs] = useState<ApiLog[]>([]);
  const [riskEvents, setRiskEvents] = useState<RiskEvent[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    try {
      const [nextTrades, nextAgents, nextLogs, nextEvents] = await Promise.all([
        fetchJson<Trade[]>('/api/v1/trades'),
        fetchJson<AgentSummary[]>('/api/v1/agents'),
        fetchJson<ApiLog[]>('/api/v1/api-logs'),
        fetchJson<RiskEvent[]>('/api/v1/risk-events'),
      ]);
      setTrades(nextTrades);
      setAgents(nextAgents);
      setApiLogs(nextLogs);
      setRiskEvents(nextEvents);
      setError('');
    } catch (err) {
      setError('Backend is not ready. From repo root run: npm run dev. API-only fallback: npm run dev:api. Evidence fallback: npm run replay && npm run evidence.');
    }
  }

  useEffect(() => { load(); }, []);

  const latestEquity = trades[0]?.equity_after ?? 10000;
  const pnl = latestEquity - 10000;
  const avgRisk = useMemo(() => trades.length ? trades.reduce((sum, trade) => sum + trade.risk_score, 0) / trades.length : 0, [trades]);
  const displayedRiskEvents: RiskEvent[] = summary?.risk_events ?? riskEvents;
  const blocked = displayedRiskEvents.filter((event) => event.decision === 'BLOCK').length || trades.filter((trade) => trade.decision === 'BLOCK').length;
  const impact = summary?.impact_metrics;

  async function handleReplay() {
    setLoading(true);
    try {
      const result = await runReplay();
      setSummary(result);
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
          <p className="subtitle">Risk gateway and paper trading evaluation sandbox for autonomous trading agents.</p>
        </div>
        <div className="status">Paper Trading · Auditable · Replayable</div>
      </section>

      <section className="judge-flow card wide">
        <div className="section-title">Judge Demo Flow</div>
        <div className="flow-steps">
          <span>1. Click Run Replay</span>
          <span>2. Verify 42 intents</span>
          <span>3. Check 16 / 4 / 22</span>
          <span>4. Confirm drawdown reduction</span>
          <span>5. Inspect Risk Events + API Logs</span>
        </div>
      </section>

      {error && <div className="error">{error}</div>}

      <section className="grid metrics">
        <RiskScoreCard score={avgRisk} />
        <div className="card metric"><div className="eyebrow">Current Equity</div><strong>{latestEquity.toFixed(2)} USDT</strong><span>{pnl >= 0 ? '+' : ''}{pnl.toFixed(2)} PnL</span></div>
        <div className="card metric"><div className="eyebrow">Blocked Intents</div><strong>{blocked}</strong><span>dangerous actions stopped</span></div>
        <div className="card metric"><div className="eyebrow">Impact Evidence</div><strong>{impact ? `${pct(summary.max_drawdown_without_guard)} → ${pct(summary.max_drawdown_with_guard)}` : 'Run Replay'}</strong><span>{impact ? `+${impact.equity_improvement_usdt.toFixed(2)} USDT protected` : 'drawdown reduction proof'}</span></div>
      </section>

      <section className="grid two">
        <ReplayPanel onReplay={handleReplay} loading={loading} summary={summary} />
        <AgentTable agents={agents} />
      </section>

      <EquityCurve trades={trades} />
      <TradeTimeline trades={trades} />

      <section className="card wide">
        <div className="section-title">Risk Events</div>
        <table>
          <thead><tr><th>Time</th><th>Agent</th><th>Symbol</th><th>Decision</th><th>Risk</th><th>Message</th><th>Failed checks</th></tr></thead>
          <tbody>
            {displayedRiskEvents.slice(0, 10).map((event, idx) => (
              <tr key={idx}>
                <td>{event.timestamp}</td>
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
                    {!event.checks?.length && <span className="muted">Run replay to view rule checks</span>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <ApiLogTable logs={apiLogs} />
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
