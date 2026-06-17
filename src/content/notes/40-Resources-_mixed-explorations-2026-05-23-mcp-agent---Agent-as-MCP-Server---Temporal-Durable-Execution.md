---
_slug: 40-Resources-_mixed-explorations-2026-05-23-mcp-agent---Agent-as-MCP-Server---Temporal-Durable-Execution
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-mcp-agent---Agent-as-MCP-Server---Temporal-Durable-Execution.md
title: mcp-agent — Agent-as-MCP-Server + Temporal Durable Execution 追加
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- asyncio
- durable
- execution
- hermes
- mcp
- server
- temporal
- tool
- workflow
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "mcp-agent — Agent-as-MCP-Server + Temporal Durable Execution 追加"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [agent, asyncio, decorator, durable, execution, mcp, mcp-agent, server, temporal, tool, workflow]
---

# mcp-agent — Agent-as-MCP-Server + Temporal Durable Execution 追加

**延續自**: [[2026-05-23-Moltis-vs-mcp-agent---Rust-Agent-Server---MCP-Pattern-比較]]

**日期**: 2026-05-23 | **來源**: GitHub raw README (lastmile-ai/mcp-agent) | **類型**: 主題延續

---

## Per-source Insight

### Source 1: MCP Agent Server — Agent-as-MCP-Server Pattern

**URL**: `examples/mcp_agent_server/README.md`
**類型**: Architecture pattern

**核心顛覆**：傳統 MCP 客戶端（Claude、Cursor、VS Code）消費 MCP server tools。mcp-agent 把這個方向翻轉——**把 agent workflow 包裝成 MCP server**，讓其他 client 都可以呼叫它。

**為何重要**：
- **Agent Composition**：多個 agent 可以互相呼叫，透過標準化 MCP 協議
- **Platform Independence**：any MCP-compatible client 都能用（Claude、VSCode、Cursor、MCP Inspector、自定義 app）
- **Multi-Agent Ecosystems**：不需要客製化整合，protocol 就是整合層

**實作方式（decorator-based，preferred）**：
```python
from mcp_agent.app import MCPApp
app = MCPApp(name="my_agent_server")

@app.tool
async def do_something(arg: str) -> str:
    ...
```

**兩種 execution mode**：
| Mode | 優點 | 適用場景 |
|------|------|----------|
| asyncio | 啟動快、無外部依賴 | 開發、測試、簡單 workflow |
| Temporal | pause/resume/retry/觀測 UI | 生產部署、複雜 workflow |

**Hermes 對應**：Hermes 目前 tool interface 是 flat list，沒有分層的 agent-as-tool 概念。`native-mcp` skill 可以考慮參考這個 pattern：把 Hestia/Talos 作為 MCP server expose 出來。

---

### Source 2: Temporal Workflow Examples — Durable Execution

**URL**: `examples/temporal/README.md`
**類型**: Orchestration backend

**核心價值**：durability = workflows can be long-running, paused, resumed, retried。

**與 asyncio 的差別**：
- asyncio 的 workflow 在記憶體中，process 重啟就 lost
- Temporal 的 workflow 持久化到 DB，重啟無感
- Temporal 提供 Web UI 監控 (`localhost:8233`)
- Task queue: `mcp-agent`，max concurrent activities: 10

**實作架構**：
1. `temporal server start-dev` 啟動 server（`localhost:7233`）
2. `run_worker.py` 啟動 worker，register 所有 workflows
3. workflow scripts (`basic.py`, `evaluator_optimizer.py`, `orchestrator.py`) 提交任務

**Hermes 對應**：Hermes 的 heartbeat action 是 stateless（每次跑完就結束），沒有 pause/resume。SAGA 論文的 durable execution 概念在 Temporal 這裡找到了具體實作參照。

---

## Cross-Source Synthesis

MCP Agent Server + Temporal = **可組合的持久化 agent 系統**：

```
MCP Client (Claude/any)
       ↓ MCP protocol
Agent Server (mcp-agent)
       ↓ asyncio or Temporal
  Workflow Logic (Python decorators)
```

三層分離：protocol / execution engine / business logic。這與 Hermes 的架構對比：

| 層 | Hermes | mcp-agent |
|----|--------|-----------|
| Protocol | Hermes CLI / tools | MCP |
| Execution | stateless heartbeat cycles | asyncio / Temporal |
| Logic | skill system | decorator-based workflows |

**值得偷的點**：
1. **Decorator-based tool definition**：比 skill frontmatter 更動態，agent 可以在 runtime 自己注册新 tool（Moltis 也走這條路）
2. **Execution engine abstraction**：asyncio ↔ Temporal 可以 swap，不需要改 workflow code

---

## 未追蹤 Leads

- https://github.com/lastmile-ai/mcp-agent/blob/main/examples/mcp_agent_server/asyncio/README.md — asyncio 實作細節
- https://github.com/lastmile-ai/mcp-agent/blob/main/examples/mcp_agent_server/temporal/README.md — Temporal 實作細節

---

## ✅ 本次探索完成
