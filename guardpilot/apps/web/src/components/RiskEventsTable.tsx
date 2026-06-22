import type { RiskEvent } from '../lib/types';

function shortTime(timestamp: string) {
  return timestamp.includes('T') ? timestamp.slice(11, 19) : timestamp;
}

type Props = {
  events: RiskEvent[];
  sourceLabel: string;
  limit?: number;
};

export function RiskEventsTable({ events, sourceLabel, limit = 10 }: Props) {
  const visible = events.slice(0, limit);
  return (
    <section className="card wide">
      <div className="section-header">
        <div>
          <div className="section-title">Risk Events</div>
          <p>WARN/BLOCK decisions returned by replay/report or the risk-events API.</p>
        </div>
        <span className="source-badge">{sourceLabel}</span>
      </div>
      <div className="muted">Showing latest {visible.length} of {events.length} risk events.</div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Time</th><th>Agent</th><th>Symbol</th><th>Decision</th><th>Risk</th><th>Level</th><th>Message</th><th>Rule checks</th></tr></thead>
          <tbody>
            {visible.map((event, idx) => (
              <tr key={idx}>
                <td title={event.timestamp}>{shortTime(event.timestamp)}</td>
                <td>{event.agent_id}</td>
                <td>{event.symbol}</td>
                <td><span className={`pill ${event.decision.toLowerCase()}`}>{event.decision}</span></td>
                <td>{event.risk_score}</td>
                <td>{event.risk_level}</td>
                <td>{event.message}</td>
                <td>
                  <div className="check-list">
                    {(event.checks ?? []).slice(0, 4).map((check, checkIdx) => (
                      <span key={checkIdx} className={`check-chip ${check.status}`}>{check.name}: {check.status} (+{check.score})</span>
                    ))}
                    {!event.checks?.length && <span className="muted">No rule checks included in this source.</span>}
                  </div>
                </td>
              </tr>
            ))}
            {!events.length && (
              <tr><td colSpan={8} className="empty-state">No risk events returned by replay/report/API yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
