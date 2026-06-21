import type { Trade } from '../lib/types';

function shortTime(timestamp: string) {
  return timestamp.includes('T') ? timestamp.slice(11, 19) : timestamp;
}

export function TradeTimeline({ trades }: { trades: Trade[] }) {
  return (
    <div className="card wide">
      <div className="section-title">Trade Timeline</div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Time</th><th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th><th>Decision</th><th>Risk</th></tr></thead>
          <tbody>
            {trades.slice(0, 12).map((trade, idx) => (
              <tr key={idx}>
                <td title={trade.timestamp}>{shortTime(trade.timestamp)}</td><td>{trade.symbol}</td><td>{trade.side}</td><td>{trade.quantity}</td><td>{trade.price.toFixed(2)}</td>
                <td><span className={`pill ${trade.decision.toLowerCase()}`}>{trade.decision}</span></td><td>{trade.risk_score}</td>
              </tr>
            ))}
            {!trades.length && (
              <tr><td colSpan={7} className="empty-state">Run replay to generate paper-trading decisions.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
