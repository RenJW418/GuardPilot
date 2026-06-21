function pct(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(2)}%`;
}

function money(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)} USDT`;
}

export function ReplayPanel({ onReplay, loading, summary }: { onReplay: () => void; loading: boolean; summary: any }) {
  const impact = summary?.impact_metrics;
  return (
    <div className="card">
      <div className="section-title">Deterministic Replay</div>
      <p>Replay sample market data and 42 Agent intents to regenerate auditable outputs for judges.</p>
      <button onClick={onReplay} disabled={loading}>{loading ? 'Running...' : 'Run Replay'}</button>
      {summary && (
        <div className="replay-summary">
          <div><span>Total</span><strong>{summary.total_intents}</strong></div>
          <div><span>Allowed / Warned / Blocked</span><strong>{summary.allowed} / {summary.warned} / {summary.blocked}</strong></div>
          <div><span>Risk grade</span><strong>{summary.risk_grade}</strong></div>
          <div><span>Blocked rate</span><strong>{pct(impact?.blocked_intent_rate)}</strong></div>
        </div>
      )}
      {impact && (
        <div className="impact-grid">
          <div><span>Equity improvement</span><strong>{money(impact.equity_improvement_usdt)}</strong></div>
          <div><span>Max drawdown</span><strong>{pct(summary.max_drawdown_without_guard)} → {pct(summary.max_drawdown_with_guard)}</strong></div>
          <div><span>Relative DD reduction</span><strong>{pct(impact.max_drawdown_reduction_relative)}</strong></div>
          <div><span>Audit records</span><strong>{impact.audit_records_generated}</strong></div>
        </div>
      )}
      {summary?.report_path && <p className="artifact-path">Report: {summary.report_path}</p>}
      {summary?.evidence_manifest_path && <p className="artifact-path">Evidence manifest: {summary.evidence_manifest_path}</p>}
    </div>
  );
}
