import type { ReplayScenario, ReplaySummary, RiskReport } from './types';

const configuredApiBase = import.meta.env.VITE_API_BASE_URL;
const API_BASE = configuredApiBase === undefined ? 'http://localhost:8000' : configuredApiBase;

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export async function runReplay(scenario: ReplayScenario = 'btc_momentum_crash'): Promise<ReplaySummary> {
  const response = await fetch(`${API_BASE}/api/v1/replay?scenario=${encodeURIComponent(scenario)}`, { method: 'POST' });
  if (!response.ok) {
    throw new Error(`Replay failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchLatestReport(): Promise<RiskReport | null> {
  const response = await fetch(`${API_BASE}/api/v1/reports/latest`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Report failed: ${response.status}`);
  }
  return response.json();
}
