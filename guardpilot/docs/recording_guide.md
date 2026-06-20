# GuardPilot Demo Recording Guide

## One-command recording

From the repository root:

```bash
npm run record:demo
```

This command will:

1. Start the GuardPilot API at `http://localhost:8000`.
2. Start the Dashboard at `http://localhost:5173`.
3. Run the deterministic replay once.
4. Open the Dashboard in your browser.
5. Record the screen for 180 seconds using macOS `screencapture`.
6. Save the video to `guardpilot/reports/guardpilot-demo.mov`.

If macOS asks for Screen Recording permission, grant it to Terminal / Claude / the app running this shell, then run the command again.

## Recommended 3-minute flow

### 0:00 - 0:20 Problem

Say:

> Autonomous trading agents can trade 24/7, but before letting them touch real execution, we need a safety and evaluation layer. GuardPilot is a pre-trade risk gateway and paper trading sandbox for Agentic Trading.

### 0:20 - 0:45 What GuardPilot does

Show Dashboard top cards:

- Risk score
- Current equity
- Blocked intents
- Audit events

Say:

> Every Agent intent is scored before execution. Safe intents are paper-traded; risky intents are warned or blocked and written to audit logs.

### 0:45 - 1:20 Run Replay

Click **Run Replay**.

Expected numbers:

- 42 total intents
- 16 allowed
- 4 warned
- 22 blocked
- Risk grade B

Say:

> This replay is deterministic. Judges can reproduce the same API logs, trade logs and risk report from the sample input files.

### 1:20 - 2:15 Show evidence

Scroll through:

- Equity Curve
- Trade Timeline
- Risk Events
- API Call Audit Log

Mention:

> GuardPilot reduced max drawdown from 2.60% to 0.70% in this scenario by blocking high-risk behavior like overtrading, leverage escalation and revenge trading.

### 2:15 - 2:40 Show API docs

Open `http://localhost:8000/docs`.

Say:

> The core integration point is POST /api/v1/intents. Any Agent Hub or Playbook style signal can pass through GuardPilot before execution.

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
