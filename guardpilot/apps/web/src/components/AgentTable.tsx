import type { AgentSummary } from '../lib/types';

export function AgentTable({ agents }: { agents: AgentSummary[] }) {
  return (
    <div className="card">
      <div className="section-title">Agent Leaderboard</div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Agent</th><th>Trades</th><th>Blocked</th><th>PnL</th><th>Avg Risk</th></tr></thead>
          <tbody>
            {agents.map((agent) => (
              <tr key={agent.agent_id}><td>{agent.agent_id}</td><td>{agent.trades}</td><td>{agent.blocked}</td><td>{agent.pnl.toFixed(2)}</td><td>{agent.average_risk_score}</td></tr>
            ))}
            {!agents.length && (
              <tr><td colSpan={5} className="empty-state">Run replay to populate the agent leaderboard.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
