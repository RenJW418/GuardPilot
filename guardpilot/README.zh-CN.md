# GuardPilot

[English](README.md) | [中文](README.zh-CN.md)

> Bitget AI Base Camp Hackathon S1 · Trading Infra 赛道项目
> 面向自主交易 Agent 的本地交易前风控 sidecar、纸交易沙盒和可视化审计面板。

GuardPilot 接在 Agent Hub / Playbook / MCP-style 下单工具之前，在任何 order-capable payload 被生成前先返回 `ALLOW`、`WARN` 或 `BLOCK`。提交版本默认 **paper-trading + dry-run only**，并使用 **Bitget 官方公开行情快照** 作为默认 replay 数据。

## 1. 一句话定位

GuardPilot 是给 Bitget AI Agent 用户使用的本地 **交易前风控 sidecar**。它把自主交易意图转化为风险决策、paper-trading 结果和 hash-verifiable 审计证据。

```text
Bitget 公开行情快照
        ↓
基于快照派生的 paper-agent intents
        ↓
GuardPilot 本地风险网关
        ↓
ALLOW / WARN -> paper execution + Bitget-compatible dry-run preview
BLOCK        -> 不生成 forwarding payload
        ↓
可视化 Dashboard + audit logs + replay evidence
```

默认不需要私有 Bitget API key，不使用真实资金，不启用 live forwarding。

## 2. 数据真实性

默认 replay 数据：

| 层 | 文件 |
|---|---|
| Market data | `samples/market/bitget_btcusdt_1m.csv` |
| Market provenance | `samples/market/bitget_btcusdt_1m.provenance.json` |
| Paper-agent intents | `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl` |
| Signal provenance | `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.provenance.json` |
| Evidence manifest | `samples/outputs/evidence_manifest.json` |

行情 provenance 记录 Bitget public endpoint、symbol、granularity、交易所时间范围、行数和 SHA-256。Agent intents 是基于真实行情快照派生的 paper-agent 决策，不声称为真实 AgentHub 导出或真实交易所成交记录。

## 3. 一键 sidecar 启动

从仓库根目录运行：

```bash
npm run bitget:sidecar
```

这个命令会安装依赖、重新生成 replay/evidence、写出 sidecar config、生成 Bitget-style dry-run trace，并启动 API + Dashboard。

打开：

- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Sidecar endpoint: `POST http://localhost:8000/api/v1/bitget/dry-run`

## 4. 评委快速运行

```bash
npm run setup
npm run judge:demo
```

完整验证：

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
| Audit records | 98 |

## 5. Bitget dry-run contract

在 Bitget Agent Hub / Playbook / MCP-style agent 调用任何订单工具前，先调用 GuardPilot：

```bash
curl -X POST http://localhost:8000/api/v1/bitget/dry-run \
  -H 'Content-Type: application/json' \
  --data @samples/agents/bitget_agenthub_payload.json
```

决策合同：

| GuardPilot decision | 含义 |
|---|---|
| `ALLOW` | 生成 Bitget-compatible dry-run preview |
| `WARN` | 生成 preview，但建议降仓位或人工确认 |
| `BLOCK` | 返回 `bitget_dry_run: null`，不要调用订单工具 |

提交版本中 `live_forwarding.enabled` 始终为 `false`。

可复查 trace：

```bash
npm run bitget:trace
```

生成：

- `samples/outputs/bitget_agenthub_dry_run_response.json`

其中包含一个被 BLOCK 的风险 payload，以及一个允许生成 dry-run preview 的保守 payload。

## 6. Dashboard 展示内容

Dashboard 是评委和开发者入口，展示：

- Bitget public snapshot provenance 数据真实性卡片
- risk cockpit 和 decision rail
- Before / After GuardPilot 对比
- Snapshot replay 控制
- decision mix、risk trend、rules、latency 等可视化分析
- audit trail：API logs、trade logs、risk events、evidence artifacts
- Bitget Agent Hub / Playbook-style dry-run boundary

## 7. 重要文件

- `apps/api/` — FastAPI 风控网关
- `apps/web/` — React/Vite 可视化 Dashboard
- `samples/market/bitget_btcusdt_1m.csv` — Bitget 公开行情快照
- `samples/market/bitget_btcusdt_1m.provenance.json` — 行情 provenance
- `samples/agents/paper_momentum_agent_signals_from_bitget_snapshot.jsonl` — 派生 paper-agent inputs
- `samples/outputs/evidence_manifest.json` — SHA-256 证据 manifest
- `samples/outputs/bitget_agenthub_dry_run_response.json` — dry-run contract trace
- `docs/bitget_integration_boundary.md` — Bitget 接入边界
- `docs/one_command_demo.md` — 一键安装/演示说明
- `docs/final_submission_packet.md` — 提交表单材料包

## 8. 真实性边界

- 真实行情数据来自 Bitget public market snapshot，不是私有账户数据。
- Agent intents 是基于快照派生的 paper-agent 信号，不是 live AgentHub export。
- 默认只做 paper trading 和 dry-run preview，不声称真实交易所成交记录。
- 默认不需要真实 Bitget API Key。
- `BLOCK` 决策永远不生成 Bitget forwarding payload。
- 未来实盘接入必须要求显式授权、严格风控 profile、密钥管理、监控、回滚和独立安全审查。
