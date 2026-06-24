# GuardPilot

[English](README.md) | [中文](README.zh-CN.md)

> Bitget AI Base Camp Hackathon S1 · Trading Infra 赛道项目
> 面向自主交易 Agent 的交易前风控网关、纸交易沙盒和审计证据层。

## 项目信息

| 字段 | 内容 |
|---|---|
| 作品名 | **GuardPilot** |
| 作者 | **添财交易员** |
| 学校 | **北京大学 Peking University** |
| 赛道 | Bitget AI Base Camp Hackathon S1 · Trading Infra |

GuardPilot 用来保护自主交易 Agent 在接触 order-capable tools 之前的关键边界。它把 AI Agent 提出的交易意图转换成可度量的策略决策，并记录市场数据、风险检查、dry-run 响应和可复现 evidence，方便评委和开发者审计。

## 为什么适合 Bitget AI Agent 生态

Bitget Agent Hub、MCP Server 和 Playbook-style 策略生成，让 AI Agent 更容易读取市场上下文并调用交易工具。但这也带来一个安全边界问题：Agent 生成交易意图的速度，可能快于人工检查速度。

GuardPilot 正是为这个边界设计的。它可以接在 Bitget AI Agent workflow 和 order-capable tools 之间，在任何下游订单 payload 生成之前返回 `ALLOW`、`WARN` 或 `BLOCK`。

GuardPilot **不是交易机器人**。它接在自主交易 Agent 和任何 order-capable 工具之间，对每个交易意图进行风险评分，并在执行前返回 `ALLOW`、`WARN` 或 `BLOCK`。最终提交版本默认使用 **Bitget 官方公开行情快照**，并提供 SHA-256 provenance；Agent intents 是基于该真实行情快照派生的 paper-agent 信号。

```text
Bitget 公开行情快照
        ↓
基于快照派生的 paper-agent intents
        ↓
GuardPilot 风控网关
        ↓
ALLOW / WARN -> paper execution + Bitget-compatible dry-run preview
BLOCK        -> 不生成 forwarding payload
        ↓
Dashboard + JSONL logs + JSON/HTML report + SHA-256 evidence manifest
```

## 数据真实性和安全边界

- **行情数据：** 来自 Bitget public market API，提交在 `guardpilot/samples/market/bitget_btcusdt_1m.csv`。
- **来源证明：** `guardpilot/samples/market/bitget_btcusdt_1m.provenance.json` 记录 endpoint、symbol、granularity、时间范围、行数和 SHA-256。
- **Agent intents：** 基于真实行情快照派生的 paper-agent 信号，提交在 `guardpilot/samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl`。
- **执行方式：** paper trading 和 dry-run preview only；不需要私有 Bitget API key，不使用真实资金，不真实下单。
- **声明边界：** GuardPilot 展示的是交易基础设施风控和审计能力，不是收益承诺或实盘盈利证明。

## 评委快速运行

从仓库根目录运行：

```bash
npm run setup
npm run judge:demo
```

打开：

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 完整验证命令

```bash
npm run test
npm run build
npm run replay
npm run evidence
npm run bitget:trace
```

默认 replay 结果：

| 指标 | 结果 |
|---|---:|
| Market data source | Bitget public market API snapshot |
| Total paper-agent intents | 42 |
| Allowed / Warned / Blocked | 28 / 0 / 14 |
| Final equity with GuardPilot | 9976.93 USDT |
| Final equity without GuardPilot | 9828.07 USDT |
| Max drawdown with GuardPilot | 0.27% |
| Max drawdown without GuardPilot | 1.88% |
| Relative drawdown reduction | 85.68% |
| Audit records generated | 98 |

## 可选：刷新 Bitget 公开行情快照

默认评审流程离线可复现，因为 Bitget 快照已提交。如果要刷新：

```bash
npm run fetch:market
npm run build:signals
npm run replay
npm run evidence
```

如果网络无法直连 Bitget，可使用本地代理：

```bash
HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 npm run fetch:market
```

## API 集成

### 通用 Agent intent

```bash
curl -X POST http://localhost:8000/api/v1/intents \
  -H 'Content-Type: application/json' \
  -d '{
    "timestamp":"2026-06-22T16:10:00Z",
    "agent_id":"paper_agent",
    "symbol":"BTCUSDT",
    "side":"BUY",
    "order_type":"MARKET",
    "quantity":0.005,
    "leverage":1,
    "confidence":0.82,
    "reason":"small paper order"
  }'
```

### Bitget Agent Hub / Playbook-style dry-run boundary

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @guardpilot/samples/agents/bitget_agenthub_payload.json
```

决策合同：

| GuardPilot decision | 含义 |
|---|---|
| `ALLOW` | 生成 Bitget-compatible dry-run preview 和审计记录 |
| `WARN` | 生成 dry-run preview，但建议降仓位或人工复核 |
| `BLOCK` | 返回 `bitget_dry_run: null`，不转发订单 payload |

提交版本中 `live_forwarding.enabled` 始终为 `false`。

## 重要文件

- `guardpilot/apps/api/` — FastAPI 风控网关和 paper trading engine
- `guardpilot/apps/web/` — React/Vite 评委 Dashboard
- `guardpilot/samples/market/bitget_btcusdt_1m.csv` — Bitget 公开行情快照
- `guardpilot/samples/market/bitget_btcusdt_1m.provenance.json` — 行情来源证明和 SHA-256
- `guardpilot/samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl` — 派生 paper-agent intents
- `guardpilot/samples/outputs/evidence_manifest.json` — replay 证据 hash 和行数
- `guardpilot/samples/outputs/sample_risk_report.json` — replay 风险报告
- `guardpilot/reports/demo_report.html` — HTML 报告
- `guardpilot/docs/demo_script.md` — 最终展示脚本
- `guardpilot/docs/final_submission_packet.md` — 提交材料包

## 真实性限制

本项目是 Hackathon prototype，默认只做 paper trading 和 dry-run preview，不包含私有 Bitget 凭证，不构成金融建议。任何未来 live execution adapter 都必须要求显式授权、仓位上限、symbol allowlist、监控、回滚机制和独立安全审查。
