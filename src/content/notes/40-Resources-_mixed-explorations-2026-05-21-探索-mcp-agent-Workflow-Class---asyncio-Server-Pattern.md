---
_slug: 40-Resources-_mixed-explorations-2026-05-21-探索-mcp-agent-Workflow-Class---asyncio-Server-Pattern
_vault_path: 40-Resources/_mixed/explorations/2026-05-21-探索-mcp-agent-Workflow-Class---asyncio-Server-Pattern.md
title: 探索：mcp-agent Workflow Class + asyncio Server Pattern
date: 2026-05-21
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- app
- async
- mcp
- run
- self
- server
- value
- workflow
- workflowresult
created: '2026-05-19'
updated: '2026-06-15'
status: budding
---

# 探索：mcp-agent Workflow Class + asyncio Server Pattern

**延續自**: [[2026-05-20-mcp-agent-agent-as-mcp-server-deep-dive]]

## Per-Source Insight

### 1. Workflow Class — 結構化多步 agent 的正確 abstraction

**核心發現**: `@app.workflow` + `@app.workflow_run` 是比 `@app.async_tool` 更高層的 abstraction，專為 stateful multi-step flows 設計。

**Decorator hierarchy**:
- `@app.tool` — sync，立即回結果（stateless）
- `@app.async_tool` — async，回 `workflow_id` 供 polling（long-running）
- `@app.workflow` — class decorator（stateful multi-step）
- `@app.workflow_run` — method decorator，entry point

**WorkflowResult** 回傳格式:
```python
return WorkflowResult(value=summary)  # 成功
return WorkflowResult(value=None, error=str(e))  # 失敗
```

**Stateful example**:
```python
@app.workflow
class StatefulWorkflow(Workflow[dict]):
    def __init__(self):
        super().__init__()
        self.state = {}  # 跨執行保留

    @app.workflow_run
    async def run(self, action: dict) -> WorkflowResult[dict]:
        action_type = action.get("type")
        if action_type == "set":
            self.state[action["key"]] = action["value"]
            return WorkflowResult(value={"status": "set"})
        elif action_type == "get":
            value = self.state.get(action["key"])
            return WorkflowResult(value={"value": value})
        elif action_type == "clear":
            self.state.clear()
            return WorkflowResult(value={"status": "cleared"})
        return WorkflowResult(value=self.state)
```

### 2. Workflow Composition Pattern — 巢狀 workflow

```python
@app.workflow
class CompositeWorkflow(Workflow[dict]):
    @app.workflow_run
    async def run(self, request: dict) -> WorkflowResult[dict]:
        step1 = DataFetchWorkflow()
        data = await step1.run(request["source"])
        step2 = DataProcessWorkflow()
        processed = await step2.run(data.value)
        step3 = ReportGenerationWorkflow()
        report = await step3.run(processed.value)
        return WorkflowResult(value={
            "data": data.value,
            "processed": processed.value,
            "report": report.value
        })
```

→ **直接對應 WS-020 的 coordinator → workers → aggregator 模式**

### 3. Workflow + Agent Integration

```python
@app.workflow
class AgentWorkflow(Workflow[str]):
    @app.workflow_run
    async def run(self, task: str) -> WorkflowResult[str]:
        agent = Agent(
            name="researcher",
            instruction="Research thoroughly and provide detailed analysis.",
            server_names=["fetch", "filesystem"]
        )
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            result = await llm.generate_str(task)
            return WorkflowResult(value=result)
```

→ **Hermes 自己的 tools 可以封裝成 Agent，直接在 Workflow 裡呼叫**

### 4. Parallel Workflow Execution

```python
import asyncio

@app.workflow
class ParallelWorkflow(Workflow[dict]):
    @app.workflow_run
    async def run(self, tasks: List[str]) -> WorkflowResult[dict]:
        workflows = [TaskWorkflow() for _ in tasks]
        results = await asyncio.gather(*[w.run(task) for w, task in zip(workflows, tasks)])
        combined = {f"task_{i}": r.value for i, r in enumerate(results)}
        return WorkflowResult(value=combined)
```

→ **asyncio.gather = Hermes multi-agent fan-out 的自然語意**

### 5. Temporal Integration — Durable execution

```python
app = MCPApp(
    name="temporal_agent",
    settings=Settings(
        execution_engine="temporal",
        temporal=TemporalSettings(
            host="localhost",
            port=7233,
            namespace="default",
            task_queue="mcp-agent"
        )
    )
)

@app.workflow
class DurableWorkflow(Workflow[str]):
    @app.workflow_run
    async def run(self, task: str) -> WorkflowResult[str]:
        await app.context.executor.signal_bus.wait_for_signal(
            Signal(name="approve", workflow_id=self.id)
        )
        result = await self.process_with_approval(task)
        return WorkflowResult(value=result)
```

→ **Signal-based human-in-the-loop = OTP gate 的 native 實作方式**

### 6. asyncio Server Pattern (from `examples/mcp_agent_server/asyncio/main.py`)

**正確的 stdio server pattern**:
```python
from mcp.server.fastmcp import FastMCP
from mcp_agent.server.app_server import create_mcp_server_for_app

mcp = FastMCP(name="hermes_server", instructions="...")
app = MCPApp(name="basic_agent_server", mcp=mcp, ...)

# Workflow + tools definitions...

async def main():
    async with app.run():
        mcp_server = create_mcp_server_for_app(app)
        await mcp_server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
```

**關鍵發現**:
- `mcp` 參數是 optional — 不給的話 `MCPApp` 會自動建立預設 `FastMCP`
- `create_mcp_server_for_app(app)` 在 `app.run()` async context 內呼叫
- `run_stdio_async()` 是正確的方法名（不是 `run_stdio()`）

**gen_client pattern**（nested MCP server）:
```python
from mcp_agent.mcp.gen_client import gen_client

async with gen_client(
    server_name, context.server_registry, context=context
) as client:
    result = await client.call_tool("tool_name", args)
```

→ **Hermes 可以用 gen_client 呼叫外部 MCP servers（如 semblent）**

### 7. MCP Sampling + Elicitation Pattern

`sampling_demo` tool 展示了 MCP Sampling API 的 nested server 實作：
- 無 upstream client → local sampling（console prompt）
- 有 upstream client → proxy 到上游（MCP protocol）

→ **Hermes 的 OTP gate 可以用 sampling proxy 實作**

## 跨文章 Synthesis

mcp-agent 的 decorator + Workflow class 提供了一個完整的 agent 系統抽象：

| 抽象層 | mcp-agent 工具 | Hermes 對應 |
|--------|---------------|-------------|
| Stateless tool | `@app.tool` | 現有 Hermes tools |
| Long-running task | `@app.async_tool` | WS-020 write queue |
| Stateful flow | `@app.workflow` | WS-020 orchestration |
| Human-in-loop | Temporal signals | OTP gate 提案 |
| Nested server | `gen_client` | native-mcp skill |

**關鍵洞察**：mcp-agent 的 `@app.async_tool` → 返回 `workflow_id` 的 pattern 已經是個原生 queue。不需要自己寫 queue 機制。`WorkflowResult(value=..., error=...)` 的格式讓錯誤處理也標準化了。

## Hermes 啟發

1. **WS-020 整合路徑更清晰**：
   - Step 1: 把 `heartbeat_v2.py --action=EVOLVE` 封裝成 `@app.workflow`
   - Step 2: 用 `gen_client` 呼叫外部 MCP servers（sembl、fetch）
   - Step 3: 用 `asyncio.gather` 實作 parallel fan-out
   - Step 4: 用 Temporal signals 實作 OTP gate

2. **Hermes tools → Agent workflow**：
   Hermes 的 `read_file`、`patch`、`terminal` 等底層工具可以用 `Agent(server_names=[...])` 包裝，在 workflow 裡以結構化方式呼叫，不再是 naked function calls。

3. **OTP gate 的 mcp-agent native 實作**：
   不需要自己寫 OTP flow。用 Temporal `signal_bus.wait_for_signal(Signal(name="approve", ...))` 即可實現「agent 等待 human approval」的 blocking pattern。這比 Telegram OTP 更乾淨（因為是同步的，不依赖外部訊息系統）。

## 未追蹤 Leads

- `https://docs.mcp-agent.com/examples/mcp_agent_server/temporal` — Temporal deployment example（已從 `examples/` 目錄確認存在）
- `https://api.github.com/repos/lastmile-ai/mcp-agent/contents/examples/workflows` — pre-built patterns: router, parallel fan-out, orchestrator, evaluator/optimizer

## ✅ 本次探索完成

**時間**: 2026-05-21T15:20 CST
**Token cost**: 低（1次 doc fetch + 1次 GitHub API + 1次 raw source fetch）
**品質**: 高 — 完整理解 Workflow class 生態、asyncio pattern、Temporal integration
**價值**: 直接服務 mcp-agent-hermes-integration 提案的實作階段（WS-019）
