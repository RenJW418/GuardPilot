import type { ApiLog } from '../lib/types';

export function ApiLogTable({ logs }: { logs: ApiLog[] }) {
  return (
    <div className="card wide">
      <div className="section-title">API Call Audit Log</div>
      <table>
        <thead><tr><th>Time</th><th>Method</th><th>Path</th><th>Agent</th><th>Status</th><th>Latency</th><th>Decision</th></tr></thead>
        <tbody>
          {logs.slice(0, 10).map((log, idx) => (
            <tr key={idx}><td>{log.timestamp}</td><td>{log.method}</td><td>{log.path}</td><td>{log.agent_id}</td><td>{log.status_code}</td><td>{log.latency_ms}ms</td><td>{log.decision}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
