# GuardPilot Demo Recording Guide

## One-command recording

From the repository root:

```bash
npm run record:demo
```

This command will:

1. Start the GuardPilot API at `http://localhost:8000`.
2. Start the Dashboard at `http://localhost:5173`.
3. Run the Bitget public-snapshot replay once.
4. Open the Dashboard in your browser.
5. Record the screen for 180 seconds using macOS `screencapture`.
6. Save the video to `guardpilot/reports/guardpilot-demo.mov`.

If macOS asks for Screen Recording permission, grant it to Terminal / Claude / the app running this shell, then run the command again.

## Recommended 3-minute flow

### 0:00 - 0:20 Problem

Say:

> Autonomous trading agents can trade 24/7, but before letting them touch real execution, we need a safety and evaluation layer. GuardPilot is a pre-trade risk gateway and paper trading sandbox for Agentic Trading.

### 0:20 - 0:45 Data truthfulness

Show README or dashboard Data truthfulness card.

Say:

> The default demo uses a recorded Bitget public-market snapshot with provenance and SHA-256 hash. The agent intents are paper-agent decisions derived from that snapshot. Execution is paper trading and dry-run only: no private keys, no real funds, and no live orders.

### 0:45 - 1:20 Run Replay

Click **Run Snapshot Replay**.

Expected numbers:

- 42 total intents
- 28 allowed
- 0 warned
- 14 blocked
- Risk grade B

Say:

> This replay is reproducible. Judges can regenerate the same API logs, trade logs, market provenance, risk report and evidence manifest from the committed Bitget public snapshot.

### 1:20 - 2:15 Show evidence

Scroll through:

- Data Truthfulness
- Before / After GuardPilot
- Equity Curve
- Trade Timeline
- Risk Events
- API Call Audit Log

Mention:

> GuardPilot reduced max drawdown from 1.88% to 0.27% in this replay by blocking high-risk behavior like overtrading, leverage escalation and revenge trading.

### 2:15 - 2:40 Show API docs

Open `http://localhost:8000/docs`.

Say:

> The core integration point is POST /api/v1/intents. For Bitget Agent Hub or Playbook-style signals, POST /api/v1/bitget/dry-run returns a dry-run preview only if the risk decision is not BLOCK. Live forwarding is disabled in this submission.

### 2:40 - 3:00 Close

Say:

> GuardPilot is not another trading bot. It is the risk and audit layer every autonomous trading Agent should pass before deployment.

## Shorter test recording

For a quick 10-second test:

```bash
bash scripts/record-demo.sh 10
```

## Output

The recording is saved at:

```text
guardpilot/reports/guardpilot-demo.mov
```

Upload this file to YouTube, X/Twitter, Google Drive, or another public link accepted by the hackathon form.
