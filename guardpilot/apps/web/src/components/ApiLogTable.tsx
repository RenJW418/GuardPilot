import type { ApiLog } from '../lib/types';

function shortTime(timestamp: string) {
  return timestamp.includes('T') ? timestamp.slice(11, 19) : timestamp;
}

export function ApiLogTable({ logs }: { logs: ApiLog[] }) {
  return (
    <div className="card wide">
      <div className="section-title">API Call Audit Log</div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Time</th><th>Method</th><th>Path</th><th>Agent</th><th>Status</th><th>Latency</th><th>Decision</th></tr></thead>
          <tbody>
            {logs.slice(0, 10).map((log, idx) => (
              <tr key={idx}>
                <td title={log.timestamp}>{shortTime(log.timestamp)}</td><td>{log.method}</td><td>{log.path}</td><td>{log.agent_id}</td><td>{log.status_code}</td><td>{log.latency_ms}ms</td>
                <td><span className={`pill ${log.decision.toLowerCase()}`}>{log.decision}</span></td>
              </tr>
            ))}
            {!logs.length && (
              <tr><td colSpan={7} className="empty-state">Run replay to generate verifiable API call logs.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
