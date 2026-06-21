import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { ApiLog, ReplaySummary, RiskEvent, RiskReport, Trade } from '../lib/types';

const COLORS = {
  allow: '#22c55e',
  warn: '#f59e0b',
  block: '#ef4444',
  info: '#38bdf8',
  muted: '#64748b',
  guarded: '#22c55e',
  unguarded: '#ef4444',
};

const tooltipStyle = {
  background: '#111827',
  border: '1px solid #334155',
  color: '#e2e8f0',
  borderRadius: 12,
};

function pct(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(2)}%`;
}

function pctFromPoints(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${value.toFixed(2)}%`;
}

function money(value?: number, signed = false) {
  if (value === undefined || value === null) return '—';
  return `${signed && value >= 0 ? '+' : ''}${value.toFixed(2)} USDT`;
}

function shortTime(timestamp: string) {
  return timestamp.includes('T') ? timestamp.slice(11, 16) : timestamp;
}

function EmptyChart({ children }: { children: string }) {
  return <div className="chart-empty">{children}</div>;
}

function decisionCounts(summary: ReplaySummary | null, trades: Trade[], apiLogs: ApiLog[]) {
  if (summary) {
    return { ALLOW: summary.allowed, WARN: summary.warned, BLOCK: summary.blocked };
  }
  const source = trades.length ? trades : apiLogs;
  return source.reduce((counts, item) => {
    const decision = item.decision as 'ALLOW' | 'WARN' | 'BLOCK';
    if (decision in counts) counts[decision] += 1;
    return counts;
  }, { ALLOW: 0, WARN: 0, BLOCK: 0 });
}

export function DecisionBreakdown({ summary, trades, apiLogs }: { summary: ReplaySummary | null; trades: Trade[]; apiLogs: ApiLog[] }) {
  const counts = decisionCounts(summary, trades, apiLogs);
  const data = [
    { name: 'ALLOW', value: counts.ALLOW, color: COLORS.allow },
    { name: 'WARN', value: counts.WARN, color: COLORS.warn },
    { name: 'BLOCK', value: counts.BLOCK, color: COLORS.block },
  ].filter((item) => item.value > 0);
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const blockedRate = total ? counts.BLOCK / total : 0;

  return (
    <div className="card chart-card">
      <div className="section-title">Decision Breakdown</div>
      <p className="chart-subtitle">Replay intent outcomes across ALLOW / WARN / BLOCK.</p>
      {total ? (
        <>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={88} paddingAngle={3}>
                {data.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          <div className="mini-metrics">
            <div className="metric-tile"><span>Total</span><strong>{total}</strong></div>
            <div className="metric-tile"><span>Blocked rate</span><strong>{pct(blockedRate)}</strong></div>
            <div className="metric-tile"><span>Mix</span><strong>{counts.ALLOW} / {counts.WARN} / {counts.BLOCK}</strong></div>
          </div>
        </>
      ) : (
        <EmptyChart>Run replay to populate the decision distribution.</EmptyChart>
      )}
    </div>
  );
}

export function ImpactComparison({ summary, report }: { summary: ReplaySummary | null; report: RiskReport | null }) {
  const withGuardEquity = summary?.final_equity_with_guard ?? report?.final_equity_with_guard;
  const withoutGuardEquity = summary?.final_equity_without_guard ?? report?.final_equity_without_guard;
  const withGuardDd = summary?.max_drawdown_with_guard ?? report?.max_drawdown_with_guard;
  const withoutGuardDd = summary?.max_drawdown_without_guard ?? report?.max_drawdown_without_guard;
  const impact = summary?.impact_metrics ?? report?.impact_metrics;
  const hasData = [withGuardEquity, withoutGuardEquity, withGuardDd, withoutGuardDd].every((value) => value !== undefined);
  const equityData = [{ metric: 'Final equity', withoutGuard: withoutGuardEquity, withGuard: withGuardEquity }];
  const drawdownData = [{ metric: 'Max drawdown', withoutGuard: (withoutGuardDd ?? 0) * 100, withGuard: (withGuardDd ?? 0) * 100 }];

  return (
    <div className="card chart-card">
      <div className="section-title">Replay Impact Comparison</div>
      <p className="chart-subtitle">Counterfactual replay metrics; not a live exchange baseline curve.</p>
      {hasData ? (
        <>
          <div className="split-charts">
            <div>
              <div className="threshold-note">Final equity · higher is better</div>
              <ResponsiveContainer width="100%" height={150}>
                <BarChart data={equityData}>
                  <CartesianGrid stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="metric" stroke={COLORS.muted} />
                  <YAxis stroke={COLORS.muted} domain={['dataMin - 10', 'dataMax + 10']} />
                  <Tooltip contentStyle={tooltipStyle} formatter={(value) => money(Number(value), false)} />
                  <Bar dataKey="withoutGuard" name="Without guard" fill={COLORS.unguarded} radius={[8, 8, 0, 0]} />
                  <Bar dataKey="withGuard" name="With GuardPilot" fill={COLORS.guarded} radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <div className="threshold-note">Max drawdown · lower is better</div>
              <ResponsiveContainer width="100%" height={150}>
                <BarChart data={drawdownData}>
                  <CartesianGrid stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="metric" stroke={COLORS.muted} />
                  <YAxis stroke={COLORS.muted} />
                  <Tooltip contentStyle={tooltipStyle} formatter={(value) => pctFromPoints(Number(value))} />
                  <Bar dataKey="withoutGuard" name="Without guard" fill={COLORS.unguarded} radius={[8, 8, 0, 0]} />
                  <Bar dataKey="withGuard" name="With GuardPilot" fill={COLORS.guarded} radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mini-metrics">
            <div className="metric-tile"><span>Equity delta</span><strong>{money(impact?.equity_improvement_usdt, true)}</strong></div>
            <div className="metric-tile"><span>DD reduction</span><strong>{pct(impact?.max_drawdown_reduction_relative)}</strong></div>
          </div>
        </>
      ) : (
        <EmptyChart>Run replay to generate with/without GuardPilot comparison metrics.</EmptyChart>
      )}
    </div>
  );
}

export function RiskTrend({ trades, apiLogs }: { trades: Trade[]; apiLogs: ApiLog[] }) {
  const data = (trades.length ? trades : apiLogs)
    .slice()
    .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
    .slice(-50)
    .map((item, index) => ({
      index: index + 1,
      time: shortTime(item.timestamp),
      fullTime: item.timestamp,
      risk_score: item.risk_score,
      decision: item.decision,
      agent_id: item.agent_id,
      symbol: 'symbol' in item ? item.symbol : item.path,
    }));

  return (
    <div className="card chart-card wide">
      <div className="section-title">Replay Risk Trend</div>
      <p className="chart-subtitle">Risk scores from replay/audit records with high and critical guardrail thresholds.</p>
      {data.length ? (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid stroke="#1f2937" vertical={false} />
            <XAxis dataKey="time" stroke={COLORS.muted} />
            <YAxis stroke={COLORS.muted} domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} labelFormatter={(_, payload) => payload?.[0]?.payload?.fullTime ?? ''} />
            <ReferenceLine y={60} stroke={COLORS.warn} strokeDasharray="4 4" label={{ value: 'High', fill: COLORS.warn, position: 'insideTopRight' }} />
            <ReferenceLine y={80} stroke={COLORS.block} strokeDasharray="4 4" label={{ value: 'Critical', fill: COLORS.block, position: 'insideTopRight' }} />
            <Line type="monotone" dataKey="risk_score" name="Risk score" stroke={COLORS.info} strokeWidth={3} dot={{ r: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <EmptyChart>Run replay to draw risk score trend.</EmptyChart>
      )}
    </div>
  );
}

export function RiskRuleBreakdown({ riskEvents }: { riskEvents: RiskEvent[] }) {
  const map = new Map<string, { rule: string; warn: number; fail: number; score: number }>();
  for (const event of riskEvents) {
    for (const check of event.checks ?? []) {
      if (check.status !== 'warn' && check.status !== 'fail') continue;
      const next = map.get(check.name) ?? { rule: check.name, warn: 0, fail: 0, score: 0 };
      if (check.status === 'warn') next.warn += 1;
      if (check.status === 'fail') next.fail += 1;
      next.score += check.score;
      map.set(check.name, next);
    }
  }
  const data = Array.from(map.values())
    .sort((a, b) => (b.fail + b.warn) - (a.fail + a.warn) || b.score - a.score)
    .slice(0, 7);

  return (
    <div className="card chart-card">
      <div className="section-title">Risk Rule Breakdown</div>
      <p className="chart-subtitle">Rule-level evidence from replay response checks.</p>
      {data.length ? (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} layout="vertical" margin={{ left: 18 }}>
            <CartesianGrid stroke="#1f2937" horizontal={false} />
            <XAxis type="number" stroke={COLORS.muted} />
            <YAxis type="category" dataKey="rule" stroke={COLORS.muted} width={150} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Bar dataKey="fail" name="Fail" stackId="a" fill={COLORS.block} radius={[0, 8, 8, 0]} />
            <Bar dataKey="warn" name="Warn" stackId="a" fill={COLORS.warn} radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <EmptyChart>Run replay to view rule-level checks. Persisted risk events may omit checks.</EmptyChart>
      )}
    </div>
  );
}

export function AuditCoverageCard({ summary, trades, apiLogs, riskEvents }: { summary: ReplaySummary | null; trades: Trade[]; apiLogs: ApiLog[]; riskEvents: RiskEvent[] }) {
  const tradeRows = summary?.trades?.length ?? trades.length;
  const apiRows = summary?.api_calls?.length ?? apiLogs.length;
  const riskRows = summary?.risk_events?.length ?? riskEvents.length;
  const ruleChecks = (summary?.risk_events ?? riskEvents).reduce((sum, event) => sum + (event.checks?.length ?? 0), 0);
  const artifacts = [summary?.report_path, summary?.evidence_manifest_path, summary?.risk_report?.trade_log_path, summary?.risk_report?.api_call_log_path, summary?.risk_report?.risk_event_log_path].filter(Boolean).length;
  const auditRecords = summary?.impact_metrics.audit_records_generated ?? tradeRows + apiRows + riskRows;
  const totalIntents = summary?.total_intents ?? tradeRows;

  return (
    <div className="card chart-card">
      <div className="section-title">Audit Coverage</div>
      <p className="chart-subtitle">Replay evidence generated for judge inspection.</p>
      <div className="mini-metrics coverage-grid">
        <div className="metric-tile"><span>Intents</span><strong>{totalIntents || '—'}</strong></div>
        <div className="metric-tile"><span>Trade rows</span><strong>{tradeRows || '—'}</strong></div>
        <div className="metric-tile"><span>API rows</span><strong>{apiRows || '—'}</strong></div>
        <div className="metric-tile"><span>Risk events</span><strong>{riskRows || '—'}</strong></div>
        <div className="metric-tile"><span>Rule checks</span><strong>{ruleChecks || '—'}</strong></div>
        <div className="metric-tile"><span>Artifacts</span><strong>{artifacts || '—'}</strong></div>
      </div>
      <div className="audit-total"><span>Audit records generated</span><strong>{auditRecords || '—'}</strong></div>
    </div>
  );
}

function percentile(values: number[], p: number) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.min(sorted.length - 1, Math.ceil(sorted.length * p) - 1);
  return sorted[index];
}

export function ApiLatencyPanel({ apiLogs }: { apiLogs: ApiLog[] }) {
  const latencies = apiLogs.map((log) => log.latency_ms).filter((value) => Number.isFinite(value));
  const avg = latencies.length ? latencies.reduce((sum, value) => sum + value, 0) / latencies.length : 0;
  const p50 = percentile(latencies, 0.5);
  const p95 = percentile(latencies, 0.95);
  const max = latencies.length ? Math.max(...latencies) : 0;
  const ok = apiLogs.filter((log) => log.status_code >= 200 && log.status_code < 300).length;

  return (
    <div className="card chart-card">
      <div className="section-title">Replay API Audit Latency</div>
      <p className="chart-subtitle">Measured during deterministic replay; not production SLA.</p>
      {latencies.length ? (
        <div className="mini-metrics coverage-grid">
          <div className="metric-tile"><span>Avg</span><strong>{avg.toFixed(1)}ms</strong></div>
          <div className="metric-tile"><span>P50</span><strong>{p50}ms</strong></div>
          <div className="metric-tile"><span>P95</span><strong>{p95}ms</strong></div>
          <div className="metric-tile"><span>Max</span><strong>{max}ms</strong></div>
          <div className="metric-tile"><span>2xx rows</span><strong>{ok}</strong></div>
          <div className="metric-tile"><span>Total rows</span><strong>{apiLogs.length}</strong></div>
        </div>
      ) : (
        <EmptyChart>Run replay to generate API audit latency rows.</EmptyChart>
      )}
    </div>
  );
}
