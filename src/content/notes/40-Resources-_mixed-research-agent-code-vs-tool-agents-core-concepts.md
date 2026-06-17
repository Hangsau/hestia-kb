---
_slug: 40-Resources-_mixed-research-agent-code-vs-tool-agents-core-concepts
_vault_path: 40-Resources/_mixed/research/agent/code-vs-tool-agents-core-concepts.md
tags:
- knowledge
- ai-agent
- core-concepts
- code-agent
- tool-based
- architecture
created: '2026-06-08'
version: 1
status: seedling
sources:
- 2026-05-29-研究報告-code-agents-vs-tool-based-agents-2026-架構取捨.md
type: core-concepts
fingerprint: code-agent, tool-based, smolagents, json-tool-call, mcp, sandbox, aci
title: Code Agents vs Tool-Based Agents — 核心概念整合
updated: '2026-06-15'
---

# Code Agents vs Tool-Based Agents — 核心概念整合

> LLM 如何選擇行動？如何執行？2024-2025 主流是 JSON tool call，2025 年中起另一條路線崛起：「agents that think in code」。

## 兩條路線的對比

```
Tool-Based：LLM → {"tool": "search", "args": {...}} → Parser → Execution → Result → LLM
Code-Based：LLM → Python/JS code → Sandbox execution → Result → LLM
```

| 維度 | Tool-Based (JSON) | Code Agents |
|------|-------------------|-------------|
| **動作表示** | 結構化 JSON | 可執行程式碼 |
| **代表框架** | LangChain (138K)、AutoGen (58K)、CrewAI、OpenAI Agents SDK | smolagents (27.5K) |
| **可靠性** | parse error、escaping bug、格式錯誤常見 | **對 LLM 更自然**（它本就受過大量 code 訓練） |
| **可組合性** | 一輪 LLM→tool→LLM | **可一次組合多個操作**：`search(); if result: analyze(); else: fallback()` |
| **除錯** | 只能看字串 | **可 print、inspect、version control** |
| **多輪效率** | 低（每 call 一次 LLM 迴圈） | 高（單次程式碼可做多步） |
| **Context 消耗** | 高（每次 tool result 加進 context） | 低（結果可變數） |
| **模型要求** | 中（小模型可） | 高（**需較強 coding 能力**，小模型掙扎）|
| **Sandbox** | 不需要 | 必須（E2B/Blaxel/Modal/Docker） |

---

## Tool-Based 的關鍵設計教訓（Anthropic ACI 原則）

**ACI = Agent-Computer Interface**。tool 格式設計要像給 junior developer 寫的 docstring：

- **Diff format 需要事先知道改了幾行** — 對 LLM 困難
- **JSON 內嵌程式碼需要 escaped newlines** — 容易出錯
- **格式要接近網路上自然出現的文本**
- **工具文件要像 docstring**（example、edge cases、典型使用情境）

---

## Code Agents：smolagents 設計解析

```python
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel())
agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")
```

**核心設計原則**：
- **Model-agnostic** — HF Inference、LiteLLM (100+ LLMs)、本地 ollama、transformers
- **Tool-agnostic** — 支援 MCP servers、LangChain tools、Hub Spaces as tools
- **Sandboxing** — E2B/Blaxel/Modal/Docker 隔離執行
- **Modality-agnostic** — text、vision、video、audio 輸入
- **核心邏輯僅 ~1,000 行** — 輕量、可讀、可改

---

## MCP（Model Context Protocol）

**2025 年崛起的 tool calling 通用協議**：

- **官方 SDK**（Go 4.6K、C# 4.3K）
- **社群伺服器 registry**（6.9K）
- **大型延伸生態**：Chrome MCP (11.7K)、XcodeBuildMCP (5.8K)、Playwright MCP (5.5K)

**核心價值**：
- **大一統介面** — 不再每個 framework 各自定義 tool schema
- **Client-Server 架構** — MCP server 可單獨部署、版本控制、分享
- **生態快速成長** — 從 IDE 延伸（Cursor、Windsurf）到生產基礎設施

---

## Orchestration 層的取捨

### Anthropic 的警告

> "These frameworks often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug. They can also make it tempting to add complexity when a simpler setup would suffice."

**Simple patterns beat complex frameworks**：
- Framework 會增加抽象層，隱藏 prompt 和 response
- **建議：先用 LLM API 直接實作，複雜度增加時再評估 framework**
- 「many patterns can be implemented in a few lines of code」

### Agno 的對應策略

- **Build agents using any framework**
- **Run with tracing/scheduling/RBAC**
- **Manage from single control plane**
- 支援 100+ 工具整合、Storage、Observability、Human approval、Multi-user/multi-tenant

---

## 可複製性評估

| 方案 | 免費可行？ | 瓶頸 |
|------|-----------|------|
| smolagents + 本地 LLM (ollama) | ✅ | 小模型 tool-use 能力差 |
| LangChain Agent | ✅ | 複雜度直線上升 |
| Anthropic 官方 SDK | ⚠️ 需 API key | 生產成本 |
| MCP server 部署 | ✅ | 文件品質參差不齊 |

---

## 給我們自己的 Actionable

| 方向 | 難度 | 具體做法 |
|------|------|----------|
| **採用 Code Agent 模式** | MODERATE | firn `CodeExecutor` 方向對了 — 對複雜 workflow 優先 code generation |
| **支援 MCP 整合** | TRIVIAL | smolagents 已實作 `ToolCollection.from_mcp()` — 先以 MCP client 身份呼叫現有 servers |
| **Tool 文件最佳化** | TRIVIAL | 每個 tool description 加上 example usage 和 edge cases（Anthropic ACI） |
| **避免 framework 陷阱** | — | 保持每層可 trace，底層 call 可見 |

---

## 參考資料

- **2026-05-29** — Code Agents vs Tool-Based Agents 2026 架構取捨
- smolagents（27.5K stars, 1k 行核心邏輯）
- Anthropic ACI 原則、Agno framework
- MCP 官方 SDK + 社群 registry
