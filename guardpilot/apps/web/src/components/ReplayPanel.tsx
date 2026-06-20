export function ReplayPanel({ onReplay, loading, summary }: { onReplay: () => void; loading: boolean; summary: any }) {
  return (
    <div className="card">
      <div className="section-title">Deterministic Replay</div>
      <p>Replay sample market data and 42 Agent intents to regenerate auditable outputs for judges.</p>
      <button onClick={onReplay} disabled={loading}>{loading ? 'Running...' : 'Run Replay'}</button>
      {summary && (
        <div className="replay-summary">
          <div>Total: {summary.total_intents}</div>
          <div>Allowed: {summary.allowed}</div>
          <div>Warned: {summary.warned}</div>
          <div>Blocked: {summary.blocked}</div>
          <div>Risk grade: {summary.risk_grade}</div>
        </div>
      )}
    </div>
  );
}
