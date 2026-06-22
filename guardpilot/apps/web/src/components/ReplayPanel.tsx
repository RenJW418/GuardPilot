import type { ReplayScenario, ReplaySummary } from '../lib/types';

function pct(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(2)}%`;
}

function money(value?: number, signed = true) {
  if (value === undefined || value === null) return '—';
  return `${signed && value >= 0 ? '+' : ''}${value.toFixed(2)} USDT`;
}

type Props = {
  onReplay: () => void;
  loading: boolean;
  summary: ReplaySummary | null;
  scenario: ReplayScenario;
  onScenarioChange: (scenario: ReplayScenario) => void;
};

const SCENARIOS: Array<{ value: ReplayScenario; label: string; hint: string }> = [
  { value: 'btc_momentum_crash', label: 'BTC Bitget snapshot replay', hint: 'recommended judge demo' },
];

export function ReplayPanel({ onReplay, loading, summary, scenario, onScenarioChange }: Props) {
  const impact = summary?.impact_metrics;
  return (
    <div className="card">
      <div className="section-title">Reproducible Bitget Snapshot Replay</div>
      <p>Run backend replay over the committed Bitget public-market snapshot to regenerate the latest risk report, audit records, and evidence manifest.</p>
      <label className="field-label" htmlFor="scenario">Replay scenario</label>
      <select
        id="scenario"
        value={scenario}
        onChange={(event) => onScenarioChange(event.target.value as ReplayScenario)}
        disabled={loading}
      >
        {SCENARIOS.map((item) => (
          <option key={item.value} value={item.value}>{item.label} · {item.hint}</option>
        ))}
      </select>
      <button onClick={onReplay} disabled={loading}>{loading ? 'Running replay...' : 'Run Replay'}</button>
      {summary && (
        <div className="success-note">Replay completed · {summary.scenario_id} · evidence regenerated</div>
      )}
      {summary && (
        <div className="replay-summary">
          <div><span>Total intents</span><strong>{summary.total_intents}</strong></div>
          <div><span>Allowed / Warned / Blocked</span><strong>{summary.allowed} / {summary.warned} / {summary.blocked}</strong></div>
          <div><span>Risk grade</span><strong>{summary.risk_grade}</strong></div>
          <div><span>Blocked rate</span><strong>{pct(impact?.blocked_intent_rate)}</strong></div>
        </div>
      )}
      {impact && (
        <div className="impact-grid">
          <div><span>Final equity</span><strong>{money(summary.final_equity_without_guard, false)} → {money(summary.final_equity_with_guard, false)}</strong></div>
          <div><span>Equity improvement</span><strong>{money(impact.equity_improvement_usdt)}</strong></div>
          <div><span>Max drawdown</span><strong>{pct(summary.max_drawdown_without_guard)} → {pct(summary.max_drawdown_with_guard)}</strong></div>
          <div><span>Relative DD reduction</span><strong>{pct(impact.max_drawdown_reduction_relative)}</strong></div>
          <div><span>Audit records</span><strong>{impact.audit_records_generated}</strong></div>
          <div><span>Report</span><strong>{summary.report_path}</strong></div>
        </div>
      )}
      {!summary && <p className="muted">No replay summary loaded yet. Run replay to evaluate paper-agent intents derived from the Bitget public snapshot.</p>}
      {summary?.evidence_manifest_path && <p className="artifact-path">Evidence manifest: {summary.evidence_manifest_path}</p>}
    </div>
  );
}
