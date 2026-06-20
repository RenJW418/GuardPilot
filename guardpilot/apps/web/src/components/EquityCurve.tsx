import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { Trade } from '../lib/types';

export function EquityCurve({ trades }: { trades: Trade[] }) {
  const data = [...trades].reverse().map((trade) => ({ timestamp: trade.timestamp.slice(11, 16), equity: trade.equity_after }));
  return (
    <div className="card wide">
      <div className="section-title">Equity Curve</div>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <XAxis dataKey="timestamp" stroke="#64748b" />
          <YAxis stroke="#64748b" domain={['auto', 'auto']} />
          <Tooltip contentStyle={{ background: '#111827', border: '1px solid #334155', color: '#e2e8f0' }} />
          <Line type="monotone" dataKey="equity" stroke="#22c55e" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
