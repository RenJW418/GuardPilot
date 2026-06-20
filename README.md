# GuardPilot

> Bitget AI Base Camp Hackathon S1 · Trading Infra 赛道项目
> Risk gateway, paper trading evaluation sandbox, and audit layer for autonomous trading agents.

GuardPilot 是一个面向自主交易 Agent 的 **交易前风控网关 + 纸交易评估沙盒 + 可复现审计系统**。它不是另一个交易机器人，而是放在 Agent 和真实交易执行层之间的安全基础设施：每一个交易意图都必须先经过风险评分、行为规则检查和纸交易模拟，然后生成可审计的 API 日志、交易日志、风控事件和风险报告。

GuardPilot is a **pre-trade risk gateway, paper trading sandbox, and reproducible audit layer** for autonomous trading agents. It is not another trading bot. Instead, it sits between an Agent and the execution layer, evaluates each trade intent, returns `ALLOW`, `WARN`, or `BLOCK`, simulates safe orders, and records verifiable evidence for review.

---

## 中文说明

### 1. 项目背景

随着 LLM Agent、交易 Agent、策略自动化工具的发展，越来越多系统能够 24 小时读取市场信号、生成交易决策并调用交易接口。但是在真正接入实盘之前，团队必须回答几个关键问题：

- Agent 会不会在亏损后加杠杆、扩大仓位，出现“复仇交易”？
- Agent 会不会在短时间内过度交易，快速消耗手续费和风险预算？
- Agent 会不会在高波动行情中追涨杀跌？
- Agent 是否遵守仓位、杠杆、回撤和风险敞口限制？
- 每一次交易意图、风控判断和模拟执行结果是否可以复现、审计和提交给评委/团队复核？

GuardPilot 解决的是 **Agentic Trading 上线前最后一道安全闸门**。它让 Agent 不再直接触达真实交易执行，而是先通过可解释的风险网关和 paper trading 环境完成评估。

### 2. 项目意义

在 Trading Infra 场景中，真正有价值的不只是“能下单”，而是：

1. **上线前安全评估**：在真实资金暴露之前发现危险 Agent 行为。
2. **行为级风控**：不仅检查单笔订单参数，还检查连续亏损、过度交易、杠杆升级、置信度不匹配等行为模式。
3. **可复现实验**：同一个 replay 场景可以稳定生成同样的结果，方便评委和开发者验证。
4. **审计证据链**：输出 API 调用日志、交易日志、风控事件、JSON/HTML 报告，满足基础设施项目对可验证记录的要求。
5. **Bitget 生态适配**：可以作为 Bitget Agent Hub / Playbook / MCP 交易 Agent 和真实执行工具之间的前置风控层。

### 3. 核心功能

- **Trade Intent 风控网关**：通过 `POST /api/v1/intents` 接收 Agent 交易意图。
- **风险决策输出**：返回 `ALLOW`、`WARN` 或 `BLOCK`。
- **行为风险评分**：检测高杠杆、超额名义价值、过度交易、复仇交易、连续亏损、波动风险、低置信度大仓位等。
- **Paper Trading 引擎**：模拟成交、手续费、滑点、持仓、PnL、权益曲线和最大回撤。
- **确定性 Replay**：内置 BTC momentum crash 场景，方便一键复现。
- **审计日志与报告**：生成 API logs、trade logs、risk events、risk report。
- **Web Dashboard**：展示风险分、账户权益、权益曲线、交易时间线、风控事件和 API 调用日志。
- **Bitget-ready Adapter**：包含 Bitget 风格 dry-run execution payload，明确未来接入真实执行工具的边界。

### 4. 架构

```text
+--------------------+
| Demo Trading Agent |
+---------+----------+
          | trade intent JSON
          v
+---------+----------+
| GuardPilot API     |
+---------+----------+
          |
          +------------------------------+
          |                              |
          v                              v
+---------+----------+        +----------+---------+
| Risk Engine        |        | Paper Trading      |
| rules + score      |        | fills + PnL        |
+---------+----------+        +----------+---------+
          |                              |
          +---------------+--------------+
                          v
+-------------------------+-------------------------+
| SQLite / JSONL logs / reports                     |
+-------------------------+-------------------------+
                          v
+-------------------------+-------------------------+
| Web Dashboard                                     |
+---------------------------------------------------+
```

### 5. Demo 结果

默认 replay 场景：`guardpilot/samples/scenarios/btc_momentum_crash.json`

| 指标 | 结果 |
|---|---:|
| Total Agent intents | 42 |
| Allowed / Warned / Blocked | 16 / 4 / 22 |
| Final equity with GuardPilot | 9980.91 USDT |
| Final equity without GuardPilot | 9930.81 USDT |
| Max drawdown with GuardPilot | 0.70% |
| Max drawdown without GuardPilot | 2.60% |
| Risk grade after guardrails | B |

这个结果说明：GuardPilot 并不是阻止所有交易，而是在保留合理交易机会的同时，拦截高风险行为，将最大回撤从 `2.60%` 降低到 `0.70%`。

### 6. 快速运行

从仓库根目录运行：

```bash
npm run replay
npm run dev
```

打开：

- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

常用命令：

```bash
npm run replay      # 复现样本交易审计记录
npm run dev         # 启动 API + Dashboard
npm run test        # 运行后端测试
npm run build       # 构建前端 Dashboard
npm run record:demo # 录制 Demo 视频
```

### 7. API 接入示例

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H 'Content-Type: application/json' \
  -d '{
    "timestamp": "2026-06-20T10:08:00Z",
    "agent_id": "demo_momentum_agent",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 0.08,
    "leverage": 8,
    "confidence": 0.61,
    "reason": "Trying to recover previous losses after breakout failure"
  }'
```

示例返回：

```json
{
  "intent_id": "int_000001",
  "decision": "BLOCK",
  "risk_score": 92,
  "risk_level": "critical",
  "simulated_order_id": null,
  "account_equity_after": 9954.13
}
```

### 8. 可复现证据文件

项目内置了提交和评审可用的证据文件：

- `guardpilot/samples/agents/demo_momentum_signals.jsonl`：样本 Agent 输入信号
- `guardpilot/samples/outputs/sample_api_calls.jsonl`：API 调用日志
- `guardpilot/samples/outputs/sample_trade_log.jsonl`：交易日志
- `guardpilot/samples/outputs/sample_risk_events.jsonl`：风控事件
- `guardpilot/samples/outputs/sample_risk_report.json`：风险报告
- `guardpilot/reports/demo_report.html`：HTML 报告
- `guardpilot/reports/guardpilot-demo.mov`：Demo 视频

### 9. 项目结构

```text
.
├── README.md                         # 双语项目介绍
├── package.json                      # 根目录快捷命令
├── scripts/                          # 本地启动和录屏脚本
└── guardpilot/
    ├── apps/api/                     # FastAPI 后端
    ├── apps/web/                     # React + Vite Dashboard
    ├── configs/risk_profiles/        # 风控配置
    ├── docs/                         # API、架构、Demo、录制说明
    ├── reports/                      # Demo 报告和视频
    ├── samples/                      # 样本 Agent、行情、场景和输出
    └── scripts/                      # replay / export / seed 脚本
```

### 10. 风险提示

本项目仅用于 Hackathon 展示、paper trading 和工程评估，不提供任何投资建议，也不会默认连接真实交易执行。真实交易所接入应在明确授权、充分测试和严格风控配置后进行。

---

## English Version

### 1. Background

Autonomous trading agents can read market signals, generate trade decisions, and call execution tools around the clock. However, before connecting them to live trading, teams need to answer critical safety and infrastructure questions:

- Does the Agent overtrade during unstable periods?
- Does it increase leverage or position size after losses?
- Does it chase volatile candles?
- Does it respect exposure, leverage, drawdown, and risk limits?
- Can every trade intent, risk decision, and simulated execution be reproduced and audited?

GuardPilot provides the missing **pre-deployment safety layer** for agentic trading systems. Instead of allowing an Agent to directly place orders, every trade intent must pass through GuardPilot first.

### 2. Why GuardPilot Matters

For Trading Infra, the key challenge is not only order execution. A production-ready agentic trading stack also needs safety, evaluation, and evidence:

1. **Pre-live safety evaluation** before real funds are exposed.
2. **Behavior-aware risk control**, including overtrading, revenge trading, leverage escalation, and confidence mismatch.
3. **Deterministic replay** so judges and developers can reproduce the same results.
4. **Auditable evidence** including API logs, trade logs, risk events, and JSON/HTML reports.
5. **Bitget ecosystem fit** as a pre-trade guardrail between Agent Hub / Playbook / MCP agents and execution tools.

### 3. Core Features

- **Trade intent gateway** via `POST /api/v1/intents`.
- **Risk decisions**: `ALLOW`, `WARN`, or `BLOCK`.
- **Behavior-aware scoring** for leverage, notional size, exposure, daily loss, consecutive losses, overtrading, revenge trading, volatility, and confidence mismatch.
- **Paper trading engine** with fills, fees, slippage, positions, PnL, equity curve, and max drawdown.
- **Replayable scenarios** with deterministic sample market data and agent signals.
- **Audit logs and reports** for reproducible evaluation.
- **Dashboard** for risk score, PnL, equity curve, trades, risk events, and API logs.
- **Bitget-ready dry-run adapter** to make the future execution boundary explicit.

### 4. Architecture

```text
Demo Trading Agent
        |
        | trade intent JSON
        v
GuardPilot API
        |
        +--> Risk Engine: rules + score + ALLOW/WARN/BLOCK
        |
        +--> Paper Trading: simulated fills + PnL + drawdown
        |
        v
SQLite / JSONL logs / reports
        |
        v
Web Dashboard
```

### 5. Demo Results

Default scenario: `guardpilot/samples/scenarios/btc_momentum_crash.json`

| Metric | Result |
|---|---:|
| Total Agent intents | 42 |
| Allowed / Warned / Blocked | 16 / 4 / 22 |
| Final equity with GuardPilot | 9980.91 USDT |
| Final equity without GuardPilot | 9930.81 USDT |
| Max drawdown with GuardPilot | 0.70% |
| Max drawdown without GuardPilot | 2.60% |
| Risk grade after guardrails | B |

In this deterministic replay, GuardPilot reduces max drawdown from `2.60%` to `0.70%` by blocking high-risk behavior while preserving reasonable trading opportunities.

### 6. Quick Start

From the repository root:

```bash
npm run replay
npm run dev
```

Open:

- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Useful commands:

```bash
npm run replay      # reproduce sample trading audit records
npm run dev         # start API + dashboard
npm run test        # run backend tests
npm run build       # build web dashboard
npm run record:demo # record demo video on macOS
```

### 7. API Example

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H 'Content-Type: application/json' \
  -d '{
    "timestamp": "2026-06-20T10:08:00Z",
    "agent_id": "demo_momentum_agent",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 0.08,
    "leverage": 8,
    "confidence": 0.61,
    "reason": "Trying to recover previous losses after breakout failure"
  }'
```

Example response:

```json
{
  "intent_id": "int_000001",
  "decision": "BLOCK",
  "risk_score": 92,
  "risk_level": "critical",
  "simulated_order_id": null,
  "account_equity_after": 9954.13
}
```

### 8. Reproducible Evidence

The repository includes review-ready evidence files:

- `guardpilot/samples/agents/demo_momentum_signals.jsonl` — sample Agent input signals
- `guardpilot/samples/outputs/sample_api_calls.jsonl` — API call log
- `guardpilot/samples/outputs/sample_trade_log.jsonl` — trade log
- `guardpilot/samples/outputs/sample_risk_events.jsonl` — risk events
- `guardpilot/samples/outputs/sample_risk_report.json` — risk report
- `guardpilot/reports/demo_report.html` — HTML report
- `guardpilot/reports/guardpilot-demo.mov` — demo video

### 9. Repository Layout

```text
.
├── README.md                         # bilingual project introduction
├── package.json                      # root workspace commands
├── scripts/                          # local dev and recording scripts
└── guardpilot/
    ├── apps/api/                     # FastAPI backend
    ├── apps/web/                     # React + Vite dashboard
    ├── configs/risk_profiles/        # risk profiles
    ├── docs/                         # API, architecture, demo and recording docs
    ├── reports/                      # demo report and video
    ├── samples/                      # sample agents, market data, scenarios and outputs
    └── scripts/                      # replay / export / seed scripts
```

### 10. Disclaimer

This project is for hackathon demonstration, paper trading, and engineering evaluation only. It does not provide financial advice and does not connect to live exchange execution by default. Any live trading integration should be enabled only with explicit authorization, thorough testing, and strict risk controls.

---

## License

MIT — see `guardpilot/LICENSE`.
