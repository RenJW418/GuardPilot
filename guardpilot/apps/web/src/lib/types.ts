export type Trade = {
  id?: number;
  timestamp: string;
  agent_id: string;
  symbol: string;
  side: string;
  price: number;
  quantity: number;
  notional: number;
  fee: number;
  realized_pnl: number;
  balance_before: number;
  balance_after: number;
  equity_after: number;
  risk_score: number;
  decision: string;
  reason?: string;
};

export type ApiLog = {
  id?: number;
  timestamp: string;
  method: string;
  path: string;
  agent_id: string;
  status_code: number;
  latency_ms: number;
  decision: string;
  risk_score: number;
};

export type RiskCheck = {
  name: string;
  status: string;
  score: number;
  message: string;
};

export type RiskEvent = {
  id?: number;
  timestamp: string;
  agent_id: string;
  symbol: string;
  decision: string;
  risk_score: number;
  risk_level: string;
  message: string;
  checks?: RiskCheck[];
};

export type AgentSummary = {
  agent_id: string;
  trades: number;
  blocked: number;
  pnl: number;
  average_risk_score: number;
};

export type ReplayScenario = 'btc_momentum_crash';

export type ImpactMetrics = {
  equity_improvement_usdt: number;
  max_drawdown_reduction_points: number;
  max_drawdown_reduction_relative: number;
  blocked_intent_rate: number;
  audit_records_generated: number;
};

export type DataProvenance = {
  market_data_source?: string;
  market_data_file?: string;
  market_data_provenance_file?: string;
  agent_signal_source?: string;
  agent_signals_file?: string;
  agent_signals_provenance_file?: string;
  execution_mode?: string;
  live_orders?: boolean;
  market_source_endpoint?: string;
  market_symbol?: string;
  market_granularity?: string;
  market_rows?: number;
  market_sha256?: string;
  market_time_start?: string;
  market_time_end?: string;
};

export type RiskReport = {
  report_id: string;
  scenario_id: string;
  agent_id: string;
  initial_balance: number;
  final_equity_without_guard: number;
  final_equity_with_guard: number;
  max_drawdown_without_guard: number;
  max_drawdown_with_guard: number;
  total_intents: number;
  allowed: number;
  warned: number;
  blocked: number;
  risk_grade: string;
  average_risk_score: number;
  residual_risk_score_after_guard: number;
  impact_metrics: ImpactMetrics;
  data_provenance?: DataProvenance;
  win_rate?: number;
  profit_factor?: number;
  sharpe_like?: number;
  equity_curve?: Array<{ timestamp: string; equity: number }>;
  risk_events: RiskEvent[];
  top_risk_findings: string[];
  trade_log_path: string;
  api_call_log_path: string;
  risk_event_log_path: string;
  evidence_manifest_path: string;
};

export type ReplaySummary = {
  scenario_id: string;
  total_intents: number;
  allowed: number;
  warned: number;
  blocked: number;
  final_equity_with_guard: number;
  final_equity_without_guard: number;
  max_drawdown_with_guard: number;
  max_drawdown_without_guard: number;
  risk_grade: string;
  impact_metrics: ImpactMetrics;
  data_provenance?: DataProvenance;
  report_path: string;
  evidence_manifest_path: string;
  risk_report?: RiskReport;
  trades?: Trade[];
  api_calls?: ApiLog[];
  risk_events?: RiskEvent[];
};
