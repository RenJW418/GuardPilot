type Props = {
  score?: number;
  hasData: boolean;
};

export function RiskScoreCard({ score, hasData }: Props) {
  const value = score ?? 0;
  const level = value > 80 ? 'Critical' : value > 60 ? 'High' : value > 30 ? 'Medium' : 'Low';
  const color = value > 80 ? '#ef4444' : value > 60 ? '#f59e0b' : value > 30 ? '#38bdf8' : '#22c55e';
  return (
    <div className="card hero-card">
      <div className="eyebrow">Agent Risk Score</div>
      <div className="risk-score" style={{ color: hasData ? color : '#64748b' }}>{hasData ? value.toFixed(0) : '—'}</div>
      <div className="risk-level">{hasData ? level : 'Run replay to compute'}</div>
      <p>Behavior-aware score computed from leverage, exposure, drawdown, volatility and Agent behavior rules.</p>
    </div>
  );
}
