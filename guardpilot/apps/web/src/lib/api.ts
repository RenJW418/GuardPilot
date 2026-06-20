const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export async function runReplay() {
  const response = await fetch(`${API_BASE}/api/v1/replay`, { method: 'POST' });
  if (!response.ok) {
    throw new Error(`Replay failed: ${response.status}`);
  }
  return response.json();
}
