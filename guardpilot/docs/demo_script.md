# GuardPilot Demo 视频讲解脚本

目标：3 分钟左右，面向 Bitget AI Base Camp Hackathon S1 · Trading Infra 评委，清楚说明项目背景、意义、核心功能、可复现证据和 Bitget 生态适配方式。

## 一句话定位

GuardPilot 不是交易机器人，而是自主交易 Agent 上线前必须经过的 **风控网关 + 纸交易评估沙盒 + 审计证据层**。

## 推荐录制准备

从仓库根目录运行：

```bash
npm run replay
npm run dev
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

> 大家好，这是 GuardPilot，一个为自主交易 Agent 设计的风险网关和纸交易评估沙盒。
> 现在越来越多 Agent 可以 24 小时读取市场信号并自动提交交易意图，但真正接入实盘前，团队必须先回答几个问题：这个 Agent 会不会过度交易？会不会亏损后加杠杆报复性交易？会不会在高波动行情里追涨杀跌？它的每一次决策是否可以复现和审计？

要点：

- 自主交易 Agent 有执行能力，但缺少上线前的安全评估层。
- 交易基础设施不只需要下单，还需要风控、回放、审计和可复现报告。

---

## 0:20 - 0:45 项目意义：为什么需要 GuardPilot

画面：展示 README 中架构图，或 Dashboard 顶部指标卡。

讲解：

> GuardPilot 的意义是把 Agent 的交易意图和真实执行层隔离开。
> Agent 不再直接下单，而是先把 trade intent 发送给 GuardPilot。GuardPilot 会根据行为风险规则进行评分，输出 ALLOW、WARN 或 BLOCK。安全的交易进入 paper trading 模拟执行，危险的交易会被拦截，同时所有 API 调用、交易记录和风控事件都会写入审计日志。

要点：

- GuardPilot 是 pre-trade guardrail。
- 适用于 Bitget Agent Hub / Playbook / MCP 风格的交易 Agent。
- 当前 MVP 使用 paper trading，评委无需真实交易所密钥即可复现。

---

## 0:45 - 1:20 核心功能展示：Run Replay

画面：Dashboard 点击 **Run Replay**，或终端运行：

```bash
npm run replay
```

讲解：

> 这里我运行一个确定性的 replay 场景：BTC momentum crash。
> 这个场景包含 42 个 demo Agent 交易意图，既有正常动量交易，也有刻意设计的高风险行为，比如连续亏损后提高杠杆、短时间过度交易、低置信度大仓位下单，以及在剧烈波动中追单。

点击 Run Replay 后讲解结果：

> 回放结果是 42 个意图中，16 个被允许，4 个被警告，22 个被阻止。
> 在这个场景里，GuardPilot 将最大回撤从无防护时的 2.60% 降低到 0.70%，最终权益也从 9930.81 USDT 提升到 9980.91 USDT。风险等级最终为 B。

关键数字：

| 指标 | 结果 |
|---|---:|
| Total intents | 42 |
| Allowed / Warned / Blocked | 16 / 4 / 22 |
| Final equity with GuardPilot | 9980.91 USDT |
| Final equity without GuardPilot | 9930.81 USDT |
| Max drawdown with GuardPilot | 0.70% |
| Max drawdown without GuardPilot | 2.60% |
| Risk grade | B |

---

## 1:20 - 2:05 Dashboard 功能展示

画面：依次滚动 Dashboard。

### 1. Risk Score / Equity / Blocked Intents

讲解：

> 顶部卡片展示当前风险分、账户权益、被拦截意图数量和审计事件数量，让评委快速看到 Agent 经过风控后的整体表现。

### 2. Equity Curve

讲解：

> 权益曲线用于对比有无 GuardPilot 的结果。这里可以看到风控网关不是为了阻止所有交易，而是在保留合理交易机会的同时，降低危险行为造成的回撤。

### 3. Trade Timeline

讲解：

> Trade Timeline 展示实际被 paper trading 执行的交易。WARN 交易仍然可以模拟执行，但会带有风险标记；BLOCK 交易不会进入执行层。

### 4. Risk Events

讲解：

> Risk Events 展示每个被警告或阻止的原因，例如 max leverage、overtrading、revenge trading、volatility risk 和 confidence mismatch。
> 这些不是黑盒判断，而是可解释、可审计的行为风控规则。

### 5. API Call Audit Log

讲解：

> API Call Audit Log 记录每一次接口调用、请求路径、状态和耗时。这满足 Trading Infra 对可验证使用记录的要求，也方便团队排查 Agent 行为。

---

## 2:05 - 2:35 API 集成方式展示

画面：打开 `http://localhost:8000/docs`，定位 `POST /api/v1/intents`。

讲解：

> GuardPilot 的核心接入点是 POST /api/v1/intents。任何交易 Agent 都可以把一个标准 JSON trade intent 发过来，包括 symbol、side、quantity、leverage、confidence 和 reason。
> GuardPilot 返回 intent_id、decision、risk_score、risk_level，以及是否生成 simulated_order_id。
> 这意味着它可以很自然地放在 Bitget Agent Hub、Playbook 或 MCP agent 和真实执行工具之间，作为上线前的风险关卡。

示例说明：

```json
{
  "agent_id": "demo_momentum_agent",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.08,
  "leverage": 8,
  "confidence": 0.61,
  "reason": "Trying to recover previous losses after breakout failure"
}
```

返回示例：

```json
{
  "decision": "BLOCK",
  "risk_score": 92,
  "risk_level": "critical",
  "simulated_order_id": null
}
```

---

## 2:35 - 2:50 可复现证据展示

画面：展示文件目录或 README 的 evidence 部分。

讲解：

> 为了方便评委复现，项目内置了样本输入、输出交易日志、API 调用日志和风险报告。只要运行同一个 replay 命令，就可以得到同样的结果。

展示文件：

- `samples/agents/demo_momentum_signals.jsonl`
- `samples/outputs/sample_api_calls.jsonl`
- `samples/outputs/sample_trade_log.jsonl`
- `samples/outputs/sample_risk_events.jsonl`
- `samples/outputs/sample_risk_report.json`
- `reports/demo_report.html`

---

## 2:50 - 3:00 结尾总结

画面：回到 Dashboard 或 README 标题。

讲解：

> 总结一下，GuardPilot 不是另一个交易 Bot，而是自主交易 Agent 上线前的安全评估和审计基础设施。它通过 pre-trade 风险评分、paper trading 模拟、可解释拦截和可复现日志，帮助团队判断一个 Agent 是否值得进入真实交易环境。
> 后续它可以扩展为 Bitget Agent Hub / Playbook 的前置风控层，也可以加入真实市场数据、Agent 排行榜和更多策略评估指标。谢谢大家。

---

## 录制时的展示顺序清单

1. 打开 Dashboard：`http://localhost:5173`
2. 简述背景：自主交易 Agent 需要上线前风控和审计。
3. 展示架构：Agent intent -> Risk Engine -> Paper Trading -> Audit logs -> Dashboard。
4. 点击 **Run Replay**。
5. 讲清楚关键数字：42 intents、16/4/22、回撤 2.60% -> 0.70%。
6. 展示 Dashboard：顶部卡片、权益曲线、交易时间线、风险事件、API logs。
7. 打开 API Docs：`POST /api/v1/intents`。
8. 展示样本证据文件和报告。
9. 总结：GuardPilot 是交易 Agent 的风控和审计层，不是交易 Bot。

## 如果只能录 60 秒

> GuardPilot is a pre-trade risk gateway and paper trading sandbox for autonomous trading agents. Instead of letting an Agent directly place orders, every trade intent goes through risk scoring first. GuardPilot returns ALLOW, WARN or BLOCK, simulates safe trades in paper trading, and records API logs, trade logs and risk events for audit. In the demo replay, 42 Agent intents are evaluated: 16 allowed, 4 warned and 22 blocked. GuardPilot reduces max drawdown from 2.60% to 0.70% in this deterministic scenario. The dashboard shows risk score, equity curve, trade timeline, risk events and API audit logs. The core integration is POST /api/v1/intents, so it can sit between Bitget Agent Hub or Playbook agents and the execution layer as a safety guardrail.
