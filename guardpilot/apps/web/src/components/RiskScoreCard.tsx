type Props = {
  score: number;
};

export function RiskScoreCard({ score }: Props) {
  const level = score > 80 ? 'Critical' : score > 60 ? 'High' : score > 30 ? 'Medium' : 'Low';
  const color = score > 80 ? '#ef4444' : score > 60 ? '#f59e0b' : score > 30 ? '#38bdf8' : '#22c55e';
  return (
    <div className="card hero-card">
      <div className="eyebrow">Agent Risk Score</div>
      <div className="risk-score" style={{ color }}>{score.toFixed(0)}</div>
      <div className="risk-level">{level}</div>
      <p>Behavior-aware score computed from leverage, exposure, drawdown, volatility and Agent behavior rules.</p>
    </div>
  );
}
