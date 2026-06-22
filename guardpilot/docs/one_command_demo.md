# GuardPilot One-Command Demo

This repository is optimized for Bitget AI Base Camp judges and developers who want the fastest possible local setup.

## Option A — local judge flow

From the repository root:

```bash
npm run setup
npm run judge:demo
```

What `npm run setup` does:

1. Installs the FastAPI backend in editable mode.
2. Installs pytest for local verification.
3. Installs the React/Vite dashboard dependencies.
4. Regenerates replay evidence from the committed Bitget public-market snapshot.
5. Verifies the SHA-256 evidence manifest, market provenance, and JSONL/CSV row counts.
6. Generates `samples/outputs/bitget_agenthub_dry_run_response.json`, a credential-free Agent Hub / Playbook-style dry-run contract trace.

What `npm run judge:demo` does:

1. Refreshes the Bitget snapshot replay.
2. Re-verifies evidence.
3. Regenerates the Bitget-style dry-run trace.
4. Starts both the API and dashboard.
5. Prints the review URLs and Bitget dry-run endpoint.

Open:

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Option B — Docker Compose

If Docker is available, run:

```bash
npm run docker:demo
```

This starts:

- `api`: FastAPI on port 8000
- `web`: Vite dashboard on port 5173

Docker is launch-focused; the strongest judge path remains `npm run setup && npm run judge:demo` because it regenerates and verifies the evidence first.

## Optional: refresh Bitget public market data

The default replay is offline/reproducible because the Bitget public snapshot is committed. If you want a fresh public snapshot before judging:

```bash
npm run fetch:market
npm run build:signals
npm run replay
npm run evidence
```

If direct network access to Bitget is blocked, use the local proxy:

```bash
HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 npm run fetch:market
```

## Bitget Agent Hub / Playbook dry-run check

After starting the API, run:

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

Expected behavior:

- GuardPilot normalizes the Agent Hub / Playbook-style signal.
- Market context comes from the recorded Bitget public snapshot.
- The risk engine returns `ALLOW`, `WARN`, or `BLOCK`.
- `BLOCK` returns no `bitget_dry_run` forwarding payload.
- `ALLOW` or `WARN` returns a Bitget-compatible dry-run preview.
- `live_forwarding.enabled` is false; no live exchange order is placed.

## Verification commands

```bash
npm run replay
npm run evidence
npm run bitget:trace
npm run test
npm run build
```

Recommended final pre-submission order:

```bash
npm run test
npm run build
npm run replay
npm run evidence
npm run bitget:trace
```

Run replay/evidence last so the committed demo artifacts and manifest remain canonical. `npm run bitget:trace` writes a separate dry-run evidence file and does not mutate the replay manifest.
