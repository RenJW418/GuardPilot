import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AgentTable } from '../components/AgentTable';
import { ApiLogTable } from '../components/ApiLogTable';
import { AuditCoverageCard, ApiLatencyPanel, DecisionBreakdown, ImpactComparison, RiskRuleBreakdown, RiskTrend } from '../components/DashboardInsights';
import { EquityCurve } from '../components/EquityCurve';
import { ReplayPanel } from '../components/ReplayPanel';
import { RiskEventsTable } from '../components/RiskEventsTable';
import { RiskScoreCard } from '../components/RiskScoreCard';
import { TradeTimeline } from '../components/TradeTimeline';
import { fetchJson, fetchLatestReport, runReplay } from '../lib/api';
import type { AgentSummary, ApiLog, DataProvenance, ReplayScenario, ReplaySummary, RiskEvent, RiskReport, Trade } from '../lib/types';
import sampleReportData from '../../../../samples/outputs/sample_risk_report.json';
import sampleApiLogRaw from '../../../../samples/outputs/sample_api_calls.jsonl?raw';
import sampleTradeLogRaw from '../../../../samples/outputs/sample_trade_log.jsonl?raw';
import './styles.css';

function pct(value?: number) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(2)}%`;
}

function money(value?: number, signed = false) {
  if (value === undefined || value === null) return '—';
  return `${signed && value >= 0 ? '+' : ''}${value.toFixed(2)} USDT`;
}

const evidenceArtifacts = [
  ['Bitget public market snapshot', 'samples/market/bitget_btcusdt_1m.csv'],
  ['Market provenance', 'samples/market/bitget_btcusdt_1m.provenance.json'],
  ['Paper-agent inputs', 'samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl'],
  ['Signal provenance', 'samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.provenance.json'],
  ['API call log', 'samples/outputs/sample_api_calls.jsonl'],
  ['Paper trade log', 'samples/outputs/sample_trade_log.jsonl'],
  ['Risk events', 'samples/outputs/sample_risk_events.jsonl'],
  ['Risk report', 'samples/outputs/sample_risk_report.json'],
  ['Evidence manifest', 'samples/outputs/evidence_manifest.json'],
];

const sampleReport = sampleReportData as RiskReport;

function parseJsonl<T>(raw: string): T[] {
  return raw
    .trim()
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line) as T);
}

const sampleTrades = parseJsonl<Trade>(sampleTradeLogRaw);
const sampleApiLogs = parseJsonl<ApiLog>(sampleApiLogRaw);

type TabKey = 'overview' | 'visual' | 'audit' | 'integration';

type HighlightTile = {
  label: string;
  value: string;
  caption: string;
  tone: 'safe' | 'warn' | 'danger' | 'info';
};

type ProofMetric = {
  label: string;
  value?: string | number;
  detail: string;
  source: string;
};

function SourceBadge({ children }: { children: React.ReactNode }) {
  return <span className="source-badge">{children}</span>;
}

function ProofMetricCard({ metric }: { metric: ProofMetric }) {
  return (
    <div className="card proof-card proof-metric">
      <span>{metric.label}</span>
      <strong>{metric.value ?? '—'}</strong>
      <small>{metric.detail}</small>
      <SourceBadge>{metric.source}</SourceBadge>
    </div>
  );
}

function DashboardTabs({ activeTab, onTabChange }: { activeTab: TabKey; onTabChange: (tab: TabKey) => void }) {
  const tabs: Array<{ key: TabKey; label: string }> = [
    { key: 'overview', label: 'Overview' },
    { key: 'visual', label: 'Visual Analytics' },
    { key: 'audit', label: 'Audit Trail' },
    { key: 'integration', label: 'Integration' },
  ];
  return (
    <nav className="dashboard-tabs" aria-label="Dashboard views">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`dashboard-tab ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => onTabChange(tab.key)}
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}

function HeroStatRail({ stats }: { stats: HighlightTile[] }) {
  return (
    <div className="hero-stat-rail" aria-label="GuardPilot proof metrics">
      {stats.map((stat) => (
        <div key={stat.label} className={`hero-stat ${stat.tone}`}>
          <span>{stat.label}</span>
          <strong>{stat.value}</strong>
          <small>{stat.caption}</small>
        </div>
      ))}
    </div>
  );
}

function DecisionRail({ allow, warn, block }: { allow: number; warn: number; block: number }) {
  const total = allow + warn + block;
  const segments = [
    { key: 'allow', label: 'ALLOW', value: allow },
    { key: 'warn', label: 'WARN', value: warn },
    { key: 'block', label: 'BLOCK', value: block },
  ];

  return (
    <div className="decision-rail">
      <div className="decision-rail-bar" aria-label="Decision gate mix">
        {segments.map((segment) => (
          <span
            key={segment.key}
            className={segment.key}
            style={{ width: total ? `${Math.max(7, (segment.value / total) * 100)}%` : '33.33%' }}
            title={`${segment.label}: ${segment.value}`}
          />
        ))}
      </div>
      <div className="decision-rail-legend">
        {segments.map((segment) => <span key={segment.key} className={segment.key}>{segment.label} · {segment.value || '—'}</span>)}
      </div>
    </div>
  );
}

function GuardrailConstellation({ hasManifest }: { hasManifest: boolean }) {
  const nodes = ['Replay', 'Score', 'Policy', 'Audit'];
  return (
    <div className="constellation" aria-label="GuardPilot guardrail stages">
      <div className="orbit orbit-one" />
      <div className="orbit orbit-two" />
      <div className="constellation-core">
        <span>{hasManifest ? 'Verified' : 'Ready'}</span>
        <strong>GuardPilot</strong>
      </div>
      {nodes.map((node, index) => <span key={node} className={`constellation-node node-${index + 1}`}>{node}</span>)}
    </div>
  );
}

function JudgeNarrativeStrip({ activeTab, onTabChange }: { activeTab: TabKey; onTabChange: (tab: TabKey) => void }) {
  const items: Array<{ tab: TabKey; label: string; title: string; detail: string }> = [
    { tab: 'visual', label: '01', title: 'Impact first', detail: 'with/without guard comparison for fast judge comprehension' },
    { tab: 'audit', label: '02', title: 'Evidence-backed', detail: 'Bitget public snapshot provenance, hashes, API logs, trade logs, and risk events' },
    { tab: 'integration', label: '03', title: 'Safe Bitget boundary', detail: 'Agent Hub / Playbook-style signals become dry-run previews only after risk review' },
  ];
  return (
    <section className="judge-narrative card wide">
      {items.map((item) => (
        <button
          key={item.tab}
          className={`narrative-step ${activeTab === item.tab ? 'active' : ''}`}
          onClick={() => onTabChange(item.tab)}
          type="button"
        >
          <span>{item.label}</span>
          <strong>{item.title}</strong>
          <small>{item.detail}</small>
        </button>
      ))}
    </section>
  );
}

function BeforeAfterGuard({ summary, report }: { summary: ReplaySummary | null; report: RiskReport | null }) {
  const withGuardEquity = summary?.final_equity_with_guard ?? report?.final_equity_with_guard;
  const withoutGuardEquity = summary?.final_equity_without_guard ?? report?.final_equity_without_guard;
  const withGuardDd = summary?.max_drawdown_with_guard ?? report?.max_drawdown_with_guard;
  const withoutGuardDd = summary?.max_drawdown_without_guard ?? report?.max_drawdown_without_guard;
  const impact = summary?.impact_metrics ?? report?.impact_metrics;
  const total = summary?.total_intents ?? report?.total_intents;
  const blocked = summary?.blocked ?? report?.blocked;
  const auditRecords = impact?.audit_records_generated;
  const hasData = withGuardEquity !== undefined || withoutGuardEquity !== undefined || impact !== undefined;

  return (
    <section className="before-after-card card wide">
      <div className="section-header">
        <div>
          <div className="section-title">Before / After GuardPilot</div>
          <p>One glance impact story for judges: the same deterministic replay, with and without the pre-trade risk gate.</p>
        </div>
        <SourceBadge>{summary ? 'Replay response' : report ? 'Latest report' : 'Awaiting replay'}</SourceBadge>
      </div>
      <div className="before-after-grid">
        <div className="comparison-pane without">
          <span>Without GuardPilot</span>
          <strong>{money(withoutGuardEquity, false)}</strong>
          <small>Unsafe intents can hit the simulated exchange path; max drawdown {pct(withoutGuardDd)}.</small>
        </div>
        <div className="comparison-arrow">→</div>
        <div className="comparison-pane with">
          <span>With GuardPilot</span>
          <strong>{money(withGuardEquity, false)}</strong>
          <small>{blocked ?? '—'} unsafe intents stopped from {total ?? '—'} total; max drawdown {pct(withGuardDd)}.</small>
        </div>
        <div className="comparison-pane proof">
          <span>Proof generated</span>
          <strong>{auditRecords ?? '—'} rows</strong>
          <small>{impact ? `${money(impact.equity_improvement_usdt, true)} protected · ${pct(impact.max_drawdown_reduction_relative)} relative DD reduction` : 'Run replay to generate report, risk events, API logs, and manifest.'}</small>
        </div>
      </div>
      {!hasData && <div className="empty-panel">Run deterministic replay to populate the before/after impact story.</div>}
    </section>
  );
}

function DemoScriptCard() {
  const steps = [
    ['0-10s', 'Show data provenance: recorded Bitget public-market snapshot, paper trading only'],
    ['10-25s', 'Run snapshot replay; GuardPilot scores leverage, exposure, drawdown, overtrading, and behavior risk'],
    ['25-40s', 'Decision gate allows, warns, or blocks before paper-order execution'],
    ['40-60s', 'Evidence pack proves every decision with replay report, JSONL logs, and SHA-256 manifest'],
  ];
  return (
    <section className="card demo-script-card">
      <div className="section-title">60-second judge demo script</div>
      <div className="demo-script-list">
        {steps.map(([time, text]) => <div key={time}><span>{time}</span><strong>{text}</strong></div>)}
      </div>
    </section>
  );
}

function WhyWinsCard() {
  const items = [
    ['AI-native safety', 'Built for autonomous trading agents, not a manual trader dashboard.'],
    ['Real market replay', 'Default evidence uses a recorded Bitget public-market snapshot with provenance.'],
    ['Audit-ready proof', 'Risk events, API logs, trade logs, reports, provenance files, and manifest align to one evidence pack.'],
    ['Safe Bitget bridge', 'Designed as the dry-run safety contract before Agent Hub, Playbook, or MCP-style order calls.'],
  ];
  return (
    <section className="card why-wins-card">
      <div className="section-title">Why this can win</div>
      <div className="why-wins-list">
        {items.map(([title, detail]) => <div key={title}><strong>{title}</strong><span>{detail}</span></div>)}
      </div>
    </section>
  );
}

function BitgetOfficialAgentCard() {
  const modules = [
    ['Agent Hub Tools', '58 exchange APIs for spot, futures, account and order actions'],
    ['Skill Hub signals', 'macro, sentiment, technical, on-chain and news context before intent generation'],
    ['Playbook output', 'natural-language strategy becomes a deployable trading agent signal'],
    ['MCP order tools', 'Claude/Cursor/Codex can call Bitget tools, with GuardPilot as the pre-trade gate'],
  ];
  return (
    <section className="card bitget-agent-card">
      <div className="section-header">
        <div>
          <div className="section-title">Bitget AI Agent safety boundary</div>
          <p>GuardPilot fits before order-capable Agent Hub / Playbook / MCP-style tools: it normalizes the signal, checks risk, and returns a dry-run preview only when the intent is not blocked.</p>
        </div>
        <SourceBadge>Agent Hub / Playbook style</SourceBadge>
      </div>
      <div className="official-agent-grid">
        {modules.map(([title, detail]) => <div key={title}><strong>{title}</strong><span>{detail}</span></div>)}
      </div>
    </section>
  );
}

function IntegrationContractCard() {
  const contract = [
    ['Input', 'Agent Hub / Playbook-style JSON signal'],
    ['Normalize', 'Map symbol, side, order type, size, leverage, confidence, reason'],
    ['Gate', 'Risk Engine returns ALLOW / WARN / BLOCK with explainable rule checks'],
    ['Forward', 'Only ALLOW/WARN produce a Bitget-compatible dry-run preview; BLOCK returns null and no live order is placed'],
  ];
  return (
    <section className="card integration-contract-card">
      <div className="section-title">GuardPilot ↔ Bitget dry-run contract</div>
      <div className="contract-list">
        {contract.map(([label, detail]) => <div key={label}><span>{label}</span><strong>{detail}</strong></div>)}
      </div>
      <div className="code-card">
        <span>Judge command</span>
        <code>curl -X POST http://localhost:8000/api/v1/bitget/dry-run --data @guardpilot/samples/agents/bitget_agenthub_payload.json</code>
      </div>
    </section>
  );
}

function DataSourceCard({ provenance }: { provenance?: DataProvenance }) {
  const items = [
    ['Market source', provenance?.market_data_source ?? 'Bitget public market API snapshot'],
    ['Market file', provenance?.market_data_file ?? 'samples/market/bitget_btcusdt_1m.csv'],
    ['Provenance', provenance?.market_data_provenance_file ?? 'samples/market/bitget_btcusdt_1m.provenance.json'],
    ['Execution', provenance?.execution_mode ?? 'paper_trading_only'],
    ['Live orders', provenance?.live_orders === false ? 'disabled' : 'not enabled'],
    ['Snapshot range', provenance?.market_time_start && provenance?.market_time_end ? `${provenance.market_time_start} → ${provenance.market_time_end}` : 'recorded in provenance JSON'],
  ];
  return (
    <section className="card data-source-card">
      <div className="section-header">
        <div>
          <div className="section-title">Data truthfulness</div>
          <p>Default evidence uses a recorded Bitget public-market snapshot with hash provenance. Agent intents are paper-agent decisions derived from that snapshot; execution stays paper-only.</p>
        </div>
        <SourceBadge>Real market data · no live funds</SourceBadge>
      </div>
      <div className="artifact-list">
        {items.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
      </div>
    </section>
  );
}

function InstallExperienceCard() {
  return (
    <section className="card install-card">
      <div className="section-header">
        <div>
          <div className="section-title">One-command judge experience</div>
          <p>Designed for reviewers to install, regenerate evidence, and launch the visualization dashboard with minimal setup.</p>
        </div>
        <SourceBadge>npm run setup → judge:demo</SourceBadge>
      </div>
      <div className="install-steps">
        <div><span>1</span><strong>npm run setup</strong><small>Installs API + web dependencies, runs replay, verifies evidence.</small></div>
        <div><span>2</span><strong>npm run judge:demo</strong><small>Refreshes evidence and starts API + dashboard.</small></div>
        <div><span>3</span><strong>npm run docker:demo</strong><small>Optional Docker Compose path for packaged local demo.</small></div>
      </div>
    </section>
  );
}

function App() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [apiLogs, setApiLogs] = useState<ApiLog[]>([]);
  const [riskEvents, setRiskEvents] = useState<RiskEvent[]>([]);
  const [summary, setSummary] = useState<ReplaySummary | null>(null);
  const [latestReport, setLatestReport] = useState<RiskReport | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<ReplayScenario>('btc_momentum_crash');
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    try {
      const [nextTrades, nextAgents, nextLogs, nextEvents, report] = await Promise.all([
        fetchJson<Trade[]>('/api/v1/trades'),
        fetchJson<AgentSummary[]>('/api/v1/agents'),
        fetchJson<ApiLog[]>('/api/v1/api-logs'),
        fetchJson<RiskEvent[]>('/api/v1/risk-events'),
        fetchLatestReport().catch(() => null),
      ]);
      setTrades(nextTrades);
      setAgents(nextAgents);
      setApiLogs(nextLogs);
      setRiskEvents(nextEvents);
      setLatestReport(report);
      setError('');
    } catch (err) {
      setError('Backend is not ready. From repo root run: npm run dev. API-only fallback: npm run dev:api. Evidence fallback: npm run replay && npm run evidence.');
    }
  }

  useEffect(() => { load(); }, []);

  const activeReport = summary?.risk_report ?? latestReport ?? sampleReport;
  const isSampleMode = !summary && !latestReport;
  const evidenceSummary: ReplaySummary | null = summary ?? (isSampleMode ? {
    scenario_id: activeReport.scenario_id,
    total_intents: activeReport.total_intents,
    allowed: activeReport.allowed,
    warned: activeReport.warned,
    blocked: activeReport.blocked,
    final_equity_with_guard: activeReport.final_equity_with_guard,
    final_equity_without_guard: activeReport.final_equity_without_guard,
    max_drawdown_with_guard: activeReport.max_drawdown_with_guard,
    max_drawdown_without_guard: activeReport.max_drawdown_without_guard,
    risk_grade: activeReport.risk_grade,
    impact_metrics: activeReport.impact_metrics,
    report_path: 'samples/outputs/sample_risk_report.json',
    evidence_manifest_path: activeReport.evidence_manifest_path,
    risk_report: activeReport,
    trades: sampleTrades,
    api_calls: sampleApiLogs,
    risk_events: activeReport.risk_events,
  } : null);
  const impact = summary?.impact_metrics ?? activeReport?.impact_metrics;
  const dataProvenance = summary?.data_provenance ?? activeReport?.data_provenance;
  const displayedTrades = summary?.trades ?? (trades.length ? trades : isSampleMode ? sampleTrades : trades);
  const displayedApiLogs = summary?.api_calls ?? (apiLogs.length ? apiLogs : isSampleMode ? sampleApiLogs : apiLogs);
  const sortedTrades = useMemo(() => [...displayedTrades].sort((a, b) => a.timestamp.localeCompare(b.timestamp)), [displayedTrades]);
  const earliestTrade = sortedTrades[0];
  const latestTrade = sortedTrades[sortedTrades.length - 1];
  const initialEquity = earliestTrade?.balance_before ?? activeReport?.initial_balance;
  const latestEquity = latestTrade?.equity_after ?? activeReport?.final_equity_with_guard;
  const pnl = latestEquity !== undefined && initialEquity !== undefined ? latestEquity - initialEquity : undefined;
  const avgRisk = useMemo(() => {
    if (displayedTrades.length) return displayedTrades.reduce((sum, trade) => sum + trade.risk_score, 0) / displayedTrades.length;
    return activeReport?.average_risk_score;
  }, [activeReport, displayedTrades]);
  const displayedRiskEvents: RiskEvent[] = summary?.risk_events ?? activeReport?.risk_events ?? riskEvents;
  const blocked = summary?.blocked ?? activeReport?.blocked ?? (displayedRiskEvents.length || displayedTrades.length ? (displayedRiskEvents.filter((event) => event.decision === 'BLOCK').length || displayedTrades.filter((trade) => trade.decision === 'BLOCK').length) : undefined);
  const topFindings = activeReport?.top_risk_findings ?? [];
  const riskEventSource = summary?.risk_events ? 'Replay: /api/v1/replay' : isSampleMode ? 'Sample report: bundled evidence' : activeReport?.risk_events ? 'Report: latest risk report' : 'API: /api/v1/risk-events';

  const proofMetrics: ProofMetric[] = [
    {
      label: 'Replay Coverage',
      value: summary?.total_intents ?? activeReport?.total_intents,
      detail: summary || activeReport ? 'backend-generated scenario count' : 'Run replay or load report to populate',
      source: summary ? 'Replay summary' : isSampleMode ? 'Sample report' : activeReport ? 'Latest report' : 'No source loaded',
    },
    {
      label: 'Decision Gate',
      value: summary || activeReport ? `${summary?.allowed ?? activeReport?.allowed} / ${summary?.warned ?? activeReport?.warned} / ${summary?.blocked ?? activeReport?.blocked}` : undefined,
      detail: 'allowed / warned / blocked',
      source: summary ? 'Replay summary' : isSampleMode ? 'Sample report' : activeReport ? 'Latest report' : 'No source loaded',
    },
    {
      label: 'Replay Impact',
      value: summary || activeReport ? `${pct(summary?.max_drawdown_without_guard ?? activeReport?.max_drawdown_without_guard)} → ${pct(summary?.max_drawdown_with_guard ?? activeReport?.max_drawdown_with_guard)}` : undefined,
      detail: 'without guard → with GuardPilot',
      source: summary ? 'Replay summary' : isSampleMode ? 'Sample report' : activeReport ? 'Latest report' : 'No source loaded',
    },
    {
      label: 'Audit Evidence',
      value: impact?.audit_records_generated,
      detail: 'API + trade + risk-event rows',
      source: impact ? (summary ? 'Replay summary' : isSampleMode ? 'Sample report' : 'Latest report') : 'No source loaded',
    },
  ];

  const runtimeDecisionCounts = [...displayedTrades, ...displayedApiLogs].reduce((counts, item) => {
    const decision = item.decision as 'ALLOW' | 'WARN' | 'BLOCK';
    if (decision === 'ALLOW') counts.allow += 1;
    if (decision === 'WARN') counts.warn += 1;
    if (decision === 'BLOCK') counts.block += 1;
    return counts;
  }, { allow: 0, warn: 0, block: 0 });
  const cockpitDecisionMix = summary || activeReport
    ? `${summary?.allowed ?? activeReport?.allowed} / ${summary?.warned ?? activeReport?.warned} / ${summary?.blocked ?? activeReport?.blocked}`
    : runtimeDecisionCounts.allow + runtimeDecisionCounts.warn + runtimeDecisionCounts.block
      ? `${runtimeDecisionCounts.allow} / ${runtimeDecisionCounts.warn} / ${runtimeDecisionCounts.block}`
      : '—';
  const cockpitSource = summary ? 'Replay summary' : activeReport ? 'Latest report' : runtimeDecisionCounts.allow + runtimeDecisionCounts.warn + runtimeDecisionCounts.block ? 'Runtime APIs' : 'No source loaded';
  const cockpitRisk = summary?.risk_grade ?? activeReport?.risk_grade ?? (avgRisk !== undefined ? avgRisk.toFixed(0) : '—');
  const cockpitManifest = summary?.evidence_manifest_path ?? activeReport?.evidence_manifest_path;
  const replayTotal = summary?.total_intents ?? activeReport?.total_intents ?? displayedTrades.length;
  const allowCount = summary?.allowed ?? activeReport?.allowed ?? runtimeDecisionCounts.allow;
  const warnCount = summary?.warned ?? activeReport?.warned ?? runtimeDecisionCounts.warn;
  const blockCount = summary?.blocked ?? activeReport?.blocked ?? runtimeDecisionCounts.block;
  const relativeDdReduction = impact?.max_drawdown_reduction_relative;
  const heroHighlights: HighlightTile[] = [
    {
      label: 'Replay intents',
      value: replayTotal ? String(replayTotal) : '—',
      caption: evidenceSummary || activeReport ? 'Bitget snapshot replay rows' : 'load backend replay',
      tone: 'info',
    },
    {
      label: 'Blocked unsafe',
      value: blockCount ? String(blockCount) : '—',
      caption: blockCount ? 'pre-trade stops before execution' : 'waiting for decisions',
      tone: 'danger',
    },
    {
      label: 'Drawdown cut',
      value: relativeDdReduction !== undefined ? pct(relativeDdReduction) : '—',
      caption: 'counterfactual replay impact',
      tone: 'safe',
    },
    {
      label: 'Audit rows',
      value: impact?.audit_records_generated !== undefined ? String(impact.audit_records_generated) : '—',
      caption: cockpitManifest ? 'manifest-backed evidence' : 'generated after replay',
      tone: 'warn',
    },
  ];

  async function handleReplay() {
    setLoading(true);
    try {
      const result = await runReplay(selectedScenario);
      setSummary(result);
      setLatestReport(result.risk_report ?? null);
      await load();
    } catch (err) {
      setError('Replay failed. Start the backend first with npm run dev:api, or regenerate evidence from CLI with npm run replay && npm run evidence.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section className="hero hero-shell">
        <div className="hero-copy">
          <div className="eyebrow hero-eyebrow">Bitget AI Base Camp · Trading Infra · Real public market snapshot {isSampleMode ? '· Bundled evidence loaded' : ''}</div>
          <h1>Stop unsafe trading agents before they reach execution tools.</h1>
          <p className="subtitle">GuardPilot replays paper-agent intents derived from a Bitget public-market snapshot, scores every order, blocks dangerous behavior, and exports judge-verifiable evidence without API keys or live funds.</p>
          <HeroStatRail stats={heroHighlights} />
          {isSampleMode && <div className="sample-mode-note">Showing bundled evidence from a recorded Bitget public-market snapshot · click Run Snapshot Replay to regenerate backend evidence.</div>}
          <div className="hero-actions">
            <button onClick={handleReplay} disabled={loading}>{loading ? 'Running replay...' : 'Run Snapshot Replay'}</button>
            <button className="secondary-button" type="button" onClick={() => setActiveTab('visual')}>View Visual Analytics</button>
            <button className="secondary-button" type="button" onClick={() => setActiveTab('audit')}>Inspect Evidence</button>
          </div>
          <div className="hero-tags">
            <span>Paper trading only</span>
            <span>Bitget public snapshot</span>
            <span>Behavior risk rules</span>
            <span>SHA-256 evidence manifest</span>
          </div>
        </div>
        <div className="cockpit-card">
          <div className="cockpit-topline">
            <div className="section-header">
              <div>
                <div className="eyebrow">Risk cockpit</div>
                <div className="cockpit-title">{summary ? 'Replay evidence generated' : activeReport ? 'Latest report loaded' : 'Ready for backend replay'}</div>
              </div>
              <SourceBadge>{cockpitSource}</SourceBadge>
            </div>
            <GuardrailConstellation hasManifest={Boolean(cockpitManifest)} />
          </div>
          <div className="cockpit-grid">
            <div><span>Risk grade / score</span><strong>{cockpitRisk}</strong></div>
            <div><span>Decision gate</span><strong>{cockpitDecisionMix}</strong></div>
            <div><span>Equity saved</span><strong>{impact ? money(impact.equity_improvement_usdt, true) : '—'}</strong></div>
            <div><span>Manifest</span><strong>{cockpitManifest ? 'Generated' : '—'}</strong></div>
          </div>
          <DecisionRail allow={allowCount} warn={warnCount} block={blockCount} />
          <div className="pipeline">
              <span>Paper-agent intent</span><span>Snapshot market context</span><span>Risk engine</span><span>Evidence</span>
          </div>
          {cockpitManifest && <p className="artifact-path">{cockpitManifest}</p>}
        </div>
      </section>

      {error && <div className="error"><strong>Sample evidence mode:</strong> {error} The dashboard remains populated from the bundled deterministic report so judges can inspect the demo without a running backend.</div>}
      <JudgeNarrativeStrip activeTab={activeTab} onTabChange={setActiveTab} />
      <DashboardTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'overview' && (
        <section className="tab-panel">
          <section className="grid proof-grid">
            {proofMetrics.map((metric) => <ProofMetricCard key={metric.label} metric={metric} />)}
          </section>

          <BeforeAfterGuard summary={summary} report={activeReport} />

          <section className="grid two">
            <DataSourceCard provenance={dataProvenance} />
            <DemoScriptCard />
          </section>

          <section className="grid two">
            <WhyWinsCard />
            <BitgetOfficialAgentCard />
          </section>

          <section className="grid two">
            <InstallExperienceCard />
            <IntegrationContractCard />
          </section>

          <section className="judge-flow card wide">
            <div className="section-title">GuardPilot Evidence Pipeline</div>
            <div className="pipeline pipeline-large">
              <span>Bitget public snapshot</span>
              <span>Paper-agent intent</span>
              <span>Risk engine</span>
              <span>ALLOW / WARN / BLOCK</span>
              <span>Paper trade or stop</span>
              <span>Evidence manifest</span>
            </div>
          </section>

          <section className="grid metrics">
            <RiskScoreCard score={avgRisk} hasData={avgRisk !== undefined} />
            <div className="card metric"><div className="eyebrow">Current Equity</div><strong>{money(latestEquity)}</strong><span>{pnl !== undefined ? `${money(pnl, true)} PnL · derived from API trades/report` : 'No equity data from API/report yet'}</span></div>
            <div className="card metric"><div className="eyebrow">Blocked Intents</div><strong>{blocked ?? '—'}</strong><span>{blocked !== undefined ? 'blocked by backend policy/report' : 'No decision data loaded'}</span></div>
            <div className="card metric"><div className="eyebrow">Replay Impact Evidence</div><strong>{impact ? `${pct(activeReport?.max_drawdown_without_guard ?? summary?.max_drawdown_without_guard)} → ${pct(activeReport?.max_drawdown_with_guard ?? summary?.max_drawdown_with_guard)}` : '—'}</strong><span>{impact ? `${money(impact.equity_improvement_usdt, true)} vs unguarded replay · ${pct(impact.max_drawdown_reduction_relative)} DD reduction` : 'No replay impact loaded'}</span></div>
          </section>

          <section className="grid two">
            <ReplayPanel onReplay={handleReplay} loading={loading} summary={evidenceSummary} scenario={selectedScenario} onScenarioChange={setSelectedScenario} />
            <DecisionBreakdown summary={evidenceSummary} trades={displayedTrades} apiLogs={displayedApiLogs} />
          </section>

          <ImpactComparison summary={evidenceSummary} report={activeReport} />
        </section>
      )}

      {activeTab === 'visual' && (
        <section className="tab-panel">
          <section className="grid two">
            <ImpactComparison summary={evidenceSummary} report={activeReport} />
            <DecisionBreakdown summary={evidenceSummary} trades={displayedTrades} apiLogs={displayedApiLogs} />
          </section>
          <EquityCurve trades={displayedTrades} />
          <RiskTrend trades={displayedTrades} apiLogs={displayedApiLogs} />
          <section className="grid two">
            <RiskRuleBreakdown riskEvents={summary?.risk_events ?? activeReport?.risk_events ?? []} />
            <AuditCoverageCard summary={evidenceSummary} trades={displayedTrades} apiLogs={displayedApiLogs} riskEvents={displayedRiskEvents} />
          </section>
          <ApiLatencyPanel apiLogs={displayedApiLogs} />
        </section>
      )}

      {activeTab === 'audit' && (
        <section className="tab-panel">
          <section className="grid two">
            <div className="card">
              <div className="section-header">
                <div>
                  <div className="section-title">Evidence & Audit Pack</div>
                  <p>Verifiable usage records generated by backend replay over the recorded Bitget public-market snapshot.</p>
                </div>
                <SourceBadge>Repository artifacts</SourceBadge>
              </div>
              <div className="artifact-list">
                {evidenceArtifacts.map(([label, path]) => (
                  <div key={path}><span>{label}</span><strong>{path}</strong></div>
                ))}
              </div>
              {impact && <p className="muted">Latest report/replay generated {impact.audit_records_generated} audit records.</p>}
            </div>
            <div className="card">
              <div className="section-header">
                <div>
                  <div className="section-title">Top Risk Findings</div>
                  <p>Backend report findings from the latest replay/report.</p>
                </div>
                <SourceBadge>{activeReport ? 'Latest report' : 'No report loaded'}</SourceBadge>
              </div>
              {topFindings.length ? (
                <ul className="findings-list">
                  {topFindings.slice(0, 5).map((finding) => <li key={finding}>{finding}</li>)}
                </ul>
              ) : (
                <div className="empty-panel">Run replay or load a report to surface risk findings.</div>
              )}
            </div>
          </section>
          <RiskEventsTable events={displayedRiskEvents} sourceLabel={riskEventSource} />
          <TradeTimeline trades={displayedTrades} />
          <ApiLogTable logs={displayedApiLogs} />
        </section>
      )}

      {activeTab === 'integration' && (
        <section className="tab-panel">
          <section className="card wide integration-card">
            <div>
              <div className="section-header">
                <div>
                  <div className="section-title">Bitget AI Agent Dry-run Boundary</div>
                  <p>GuardPilot is the pre-trade safety contract before Agent Hub / Playbook / MCP-style order tools. It creates a dry-run preview only after risk review and keeps live forwarding disabled in this submission.</p>
                </div>
                <SourceBadge>Dry-run only · no live orders</SourceBadge>
              </div>
            </div>
            <div className="integration-flow">
              <span>Skill Hub / Playbook-style signal</span><span>Recorded Bitget market context</span><span>GuardPilot risk gate</span><span>ALLOW/WARN dry-run or BLOCK</span>
            </div>
          </section>
          <section className="grid two">
            <BitgetOfficialAgentCard />
            <IntegrationContractCard />
          </section>
          <section className="grid two">
            <AgentTable agents={agents} />
            <ApiLatencyPanel apiLogs={displayedApiLogs} />
          </section>
          <section className="card wide">
            <div className="section-title">Report Metadata</div>
            <div className="artifact-list">
              <div><span>Replay scenario</span><strong>{summary?.scenario_id ?? activeReport?.scenario_id ?? '—'}</strong></div>
              <div><span>Risk report</span><strong>{summary?.report_path ?? 'Run replay to generate report path'}</strong></div>
              <div><span>Evidence manifest</span><strong>{summary?.evidence_manifest_path ?? activeReport?.evidence_manifest_path ?? 'Run replay to generate manifest path'}</strong></div>
            </div>
          </section>
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
