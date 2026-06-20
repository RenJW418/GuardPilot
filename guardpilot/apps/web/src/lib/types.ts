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

export type RiskEvent = {
  id?: number;
  timestamp: string;
  agent_id: string;
  symbol: string;
  decision: string;
  risk_score: number;
  risk_level: string;
  message: string;
};

export type AgentSummary = {
  agent_id: string;
  trades: number;
  blocked: number;
  pnl: number;
  average_risk_score: number;
};
