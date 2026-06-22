# GuardPilot Demo 视频讲解脚本

目标：3 分钟左右，面向 Bitget AI Base Camp Hackathon S1 · Trading Infra 评委，清楚说明项目背景、真实数据来源、核心功能、可复现证据和 Bitget 生态适配方式。

## 一句话定位

GuardPilot 不是交易机器人，而是自主交易 Agent 上线前必须经过的 **风控网关 + 纸交易评估沙盒 + 审计证据层**。

## 推荐录制准备

从仓库根目录运行：

```bash
npm run setup
npm run judge:demo
```

打开：

- Dashboard: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs`

如果需要一键录屏：

```bash
npm run record:demo
```

---

## 0:00 - 0:20 开场：项目背景和痛点

画面：打开 Dashboard 或 README 标题页。

讲解：

> GuardPilot 是一个 Bitget AI Base Camp Trading Infra 项目，解决一个问题：自主交易 Agent 触达执行工具之前，我们如何判断它是否安全、可复现、可审计？
> 它不是交易 Bot，而是 pre-trade safety gate。每个交易意图会先经过行为风控、paper trading 模拟和审计记录，再决定 ALLOW、WARN 或 BLOCK。
> 当前提交版本默认使用 Bitget 官方公开行情快照，不需要真实交易所密钥，不触碰真实资金，也不会真实下单。

要点：

- 自主交易 Agent 有执行能力，但缺少上线前的安全评估层。
- 交易基础设施不只需要下单，还需要风控、回放、审计和可复现报告。
- 本演示使用真实公开行情数据 + paper execution，安全且可复现。

---

## 0:20 - 0:45 数据真实性和安全边界

画面：展示 README 的 Data truthfulness，或 Dashboard 的 Data truthfulness 卡片。

讲解：

> 默认 replay 使用 `samples/market/bitget_btcusdt_1m.csv`，这是从 Bitget public market API 记录下来的 BTCUSDT 1 分钟 K 线快照。
> 来源证明在 `samples/market/bitget_btcusdt_1m.provenance.json`，里面有 endpoint、symbol、granularity、时间范围、行数和 SHA-256 hash。
> Agent intents 不是实盘订单，而是基于这段真实行情派生的 paper-agent 信号；执行层是 paper trading 和 dry-run preview，`live_forwarding.enabled` 始终是 false。

要点：

- 真实数据：Bitget public market snapshot。
- 安全边界：paper trading only，no live funds，no private keys。
- 可验证：provenance + evidence manifest。

---

## 0:45 - 1:20 从安装到启动

画面：终端展示命令。

```bash
npm run setup
npm run judge:demo
```

讲解：

> `npm run setup` 会安装 API 和前端依赖，基于已提交的 Bitget public snapshot 重新生成 replay evidence，验证 SHA-256 evidence manifest，并生成 Bitget-style dry-run trace。
> `npm run judge:demo` 会刷新证据并启动 API 和 Dashboard。评委打开 `localhost:5173` 看 dashboard，打开 `localhost:8000/docs` 看 API。

如果要刷新行情快照，可展示：

```bash
npm run fetch:market
npm run build:signals
npm run replay
npm run evidence
```

---

## 1:20 - 1:55 核心功能展示：Run Snapshot Replay

画面：Dashboard 点击 **Run Snapshot Replay**，或终端运行：

```bash
npm run replay
npm run evidence
```

讲解：

> 这里运行默认 `btc_momentum_crash` replay。它包含 42 个 paper-agent 交易意图，这些意图基于 Bitget 公开行情快照派生，包含正常动量交易，也包含高风险行为，例如过度交易、亏损后提高杠杆、低置信度大仓位下单。
> Replay 会同时比较“没有 GuardPilot”和“启用 GuardPilot”的结果，隔离出风控网关的价值。

关键数字：

| 指标 | 结果 |
|---|---:|
| Total intents | 42 |
| Allowed / Warned / Blocked | 28 / 0 / 14 |
| Final equity with GuardPilot | 9976.93 USDT |
| Final equity without GuardPilot | 9828.07 USDT |
| Max drawdown with GuardPilot | 0.27% |
| Max drawdown without GuardPilot | 1.88% |
| Relative drawdown reduction | 85.68% |
| Audit records | 98 |

讲解：

> 在这段真实公开行情回放中，GuardPilot 阻止了 14 个高风险意图，将最大回撤从 1.88% 降到 0.27%，同时生成 98 条审计记录。这里展示的是风控基础设施效果，不是收益承诺或实盘盈利证明。

---

## 1:55 - 2:30 Dashboard 功能展示

画面：依次展示 Dashboard。

### 1. Risk Cockpit / Decision Rail

> 顶部卡片展示 replay intents、blocked unsafe、drawdown cut、audit rows，让评委快速看到安全门的整体效果。

### 2. Data Truthfulness

> 这里展示 market source、market file、provenance file、execution mode 和 live orders disabled，避免评委误解为实盘交易。

### 3. Before / After GuardPilot

> 同一组 paper-agent 输入和同一段 Bitget market tape，对比无防护和启用 GuardPilot 的最终权益与最大回撤。

### 4. Risk Events / Trade Timeline / API Logs

> Risk Events 解释每个被阻止的原因，例如 max leverage、overtrading、revenge trading、volatility risk 和 confidence mismatch。Trade Timeline 展示 paper execution。API logs 记录每次调用、耗时、decision 和 risk score。

---

## 2:30 - 2:50 API 集成方式展示

画面：打开 `http://localhost:8000/docs`，定位 `POST /api/v1/bitget/dry-run`，或展示 Dashboard 的 Integration tab。

讲解：

> 这里是 GuardPilot 和 Bitget Agent Hub / Playbook / MCP-style 工具的结合点。Agent 先把 signal 发给 GuardPilot，GuardPilot 标准化为 trade intent，然后做风险决策。
> 只有 ALLOW 或 WARN 才生成 Bitget-compatible dry-run preview；如果是 BLOCK，`bitget_dry_run` 是 null，不会把执行 payload 交给任何订单工具。提交版本里 live forwarding 显式禁用。

示例命令：

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

---

## 2:50 - 3:00 可复现证据和结尾

画面：展示 `samples/outputs/evidence_manifest.json`、`samples/outputs/sample_risk_report.json`、`reports/demo_report.html`。

讲解：

> Evidence manifest 会记录 scenario、market data、provenance、agent signals、API logs、trade logs、risk events report 的 SHA-256 hash 与行数。评委运行 `npm run evidence` 就能验证这些文件没有被篡改。
> 总结一下，GuardPilot 不是另一个交易 Bot，而是自主交易 Agent 上线前的安全评估和审计基础设施。它让团队在靠近真实执行之前，先看到风险、回撤、拦截原因和完整证据。

---

## 录制时的展示顺序清单

1. 展示 README / Dashboard 标题：pre-trade risk gateway，不是交易 Bot。
2. 展示 Data Truthfulness：Bitget public snapshot + provenance + paper trading only。
3. 运行或展示 `npm run setup` → `npm run judge:demo`。
4. 点击 **Run Snapshot Replay**。
5. 讲清楚关键数字：42 intents、28/0/14、回撤 1.88% -> 0.27%、98 audit records。
6. 展示 Dashboard：风险驾驶舱、数据来源卡、Before/After、风险事件、交易时间线、API logs。
7. 打开 API Docs：`POST /api/v1/intents` 和 `POST /api/v1/bitget/dry-run`。
8. 展示证据文件和 manifest。
9. 总结：GuardPilot 是交易 Agent 的风控和审计层，不是实盘交易系统。

## 如果只能录 60 秒

> GuardPilot is a pre-trade risk gateway and paper-trading audit layer for autonomous trading agents. The default demo uses a recorded Bitget public-market snapshot with provenance, then derives 42 paper-agent intents from that real market data. Every intent goes through risk scoring before execution. GuardPilot returns ALLOW, WARN or BLOCK, simulates safe trades in paper trading, and records API logs, trade logs, risk events and SHA-256 evidence. In the default replay, 14 risky intents are blocked, max drawdown drops from 1.88% to 0.27%, and 98 audit records are generated. The Bitget dry-run endpoint creates a dry-run preview only when the intent is not blocked; live forwarding is disabled.
