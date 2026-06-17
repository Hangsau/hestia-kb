---
_slug: 40-Resources-_mixed-research-2026-05-29-研究報告-code-agents-vs-tool-based-agents-2026-架構取捨
_vault_path: 40-Resources/_mixed/research/2026-05-29-研究報告-code-agents-vs-tool-based-agents-2026-架構取捨.md
tags:
- research
- knowledge
- ai-agent
created: '2026-05-29'
version: 1
source_report: 2026-05-29-code-agents-vs-tool-based-agents-2026.md
source_url: null
type: research
fingerprint: tool, mcp, llm, code, agents, agent, smolagents, firn, json, langchain
title: 研究報告：Code Agents vs Tool-Based Agents — 2026 架構取捨
updated: '2026-06-15'
status: budding
---

# 研究報告：Code Agents vs Tool-Based Agents — 2026 架構取捨

## Version 1 — 2026-05-29

### 核心觀念
**問題**：AI agent 的核心問題是：**LLM 如何選擇行動？如何執行？如何確保行動的正確性？** 2024-2025 年，主流做法是所謂的 **tool-based agent**：LLM 输出 JSON 格式的 tool call（例如 `{"name": "search", "args": {"query": "..."}}`），系統解析後執行。這是 ReAct、LangChain Agents、AutoGPT 的核心模式。 但 2025 年中旬起，另一种路线崛起：**Code Agents**（又稱  `"agents that think in code"`）。代表是 HuggingFa…

**洞見**：1. **可靠性更高**：當 tool call 是 JSON 時，parse error、escaping bug、格式錯誤是常見失敗點。Code 作為 action 的表示形式，對 LLM 而言更自然（它本來就受過大量程式碼訓練）。 2. **可組合性**：程式碼可以组合多個操作（`search(); if result: analyze(); else: fallback()`），不需要多輪 LLM→tool→LLM 的迴圈。 3. **除錯更容易**：LLM 產生的程式碼可以 print、inspect、version control。JSON tool call 只能看字串。 4. …

### 架構 / 機制
## 2. Core Mechanism

### Tool-Based Agents（JSON Tool Calls）

```
LLM → {"tool": "search", "args": {...}} → Parser → Execution → Result → LLM
```

典型流程：
1. LLM 輸出結構化的 tool call 區塊（function calling）
2. 系統解析 JSON、呼叫對應工具
3. 工具結果以文字形式加回 context
4. LLM 根據觀察結果決定下一步

**代表框架**：LangChain（⭐138K）、AutoGen（⭐58K）、CrewAI、OpenAI Agents SDK

**工具格式的關鍵問題**（Anthropic 觀點）：
- Diff format 需要事先知道改了幾行——對 LLM 困難
- JSON 內嵌程式碼需要 escaped newlines——容易出錯
- 建議：格式要接近網路上自然出現的文本；工具文件要像給 junior developer 寫的 docstring

### Code Agents（Actions in Code）

```
LLM → Python/JS code → Sandbox execution → Result → LLM
```

LLM 產生的不是 JSON，而是 **可執行程式碼**，在隔離環境（Docker、E2B、Blaxel）中執行。程式碼可以直接做搜尋、檔案操作、API 呼叫——而這些動作的語法就是普通的 Python/JS。

**代表框架**：smolagents（⭐27,581，核心邏輯僅 ~1,000 行）

smolagents 的設計原則：
```python
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel())
agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")
```

- **Model-agnostic**：可用 HF Inference、LiteLLM（100+ LLMs）、本地 ollama、transformers
- **Tool-agnostic**：支援 MCP servers、LangChain tools、Hub Spaces as tools
- **Sandboxing**：E2B/Blaxel/Modal/Docker 隔離執行，防止有害程式碼
- **Modality-agnostic**：支援 text、vision、video、audio 输入

### MCP（Model Context Protocol）

MCP 是 2025 年崛起的重要標準——試圖建立 tool calling 的通用協議。

**規模型**：官方 SDK（Go⭐4,617、C#⭐4,297）、社群伺服器 registry（⭐6,871）、大型延伸生態（Chrome MCP⭐11,748、XcodeBuildMCP⭐5,774、Playwright MCP⭐5,536）。

核心價值：
- **大一統介面**：不再需要每個 framework 各自定義 tool schema
- **Client-Server 架構**：MCP server 可單獨部署、版本控制、分享
- **生態快速成長**：從 IDE 延伸（Cursor、Windsurf）到生產基礎設施

### Orchestration 層的取捨

**Simple patterns beat complex frameworks**（Anthropic 建議）：
- Framework 會增加抽象層，隱藏 prompt 和 response，讓 debugging 變難
- 建議：先用 LLM API 直接實作，複雜度增加時再評估 framework
- 「many patterns can be implemented in a few lines of code」

**Agno 的觀點**（⭐非官方，但文件完整）：
- Build agents using any framework → Run with tracing/scheduling/RBAC → Manage from single control plane
- 支援 100+ 工具整合、Storage、Observability、Human approval、Multi-user/multi-tenant

---

### 思考
## 4. Limitations / Honest Assessment

### Code Agents 的限制

- **Sandbox 安全**：執行程式碼需要隔離環境，E2B/Blaxel 是額外依賴
- **並非所有模型都適合**：Code Agent 需要較強的 coding 能力（GPT-4、Claude 3.5+、等較好，小模型掙扎）
- **除錯複雜度**：當 LLM 產生的程式碼有語法錯誤或邏輯 bug 時，需要追蹤「是 model 能力問題還是 prompt 問題」

### Tool-Based 的限制

- **多輪效率低**：每個 tool call 都需要一個完整的 LLM call迴圈，貴且慢
- **格式脆弱**：一旦 API schema 改變，整個 agent 可能失效
- **Context window 消耗**：每次 tool result 都附加到 context，long horizon 任務很快就爆

### 框架 vs 直接 API

Anthropic 的警告值得記住：
> "These frameworks often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug. They can also make it tempting to add complexity when a simpler setup would suffice."

### 可複製性評估

| 方案 | 免費可行？ | 瓶頸 |
|------|-----------|------|
| smolagents + 本地 LLM (ollama) | ✅ 是 | 小模型 tool-use 能力差 |
| LangChain Agent | ✅ 是 | 複雜度直線上升 |
| Anthropic 官方 SDK | ⚠️ 需 API key | 生產環境成本 |
| MCP server 部署 | ✅ 是 | 文件品質參差不齊 |

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### FIRN 具體行動

1. **採用 Code Agent 模式**（MODERATE難度）
   - FIRN 的 `CodeExecutor` 方向對了——考慮讓更多的 tool 變成 in-code action
   - 不必完全拋棄 tool-based，但對複雜 workflow 優先考慮 code generation
   - 參考 smolagents 的 sandbox 設計（可用 Docker in Docker）

2. **支援 MCP 整合**（TRIVIAL）
   - FIRN 的 tool registry 可以接 MCP——HuggingFace smolagents 已經實作 `ToolCollection.from_mcp()`
   - 先讓 FIRN 能以 MCP client 身份呼叫現有 MCP servers（不用自己寫 server）
   - 評估 `firn-vault` 是否可以变成 MCP server 暴露知識庫查詢

3. **Tool 文件最佳化**（TRIVIAL）
   - Anthropic 的 ACI（Agent-Computer Interface）原則：每個 tool 的 description 要像 docstring 一樣寫
   - FIRN 的 tool schema 加上 example usage 和 edge cases
   - 測試：用不同表述方式餵同樣 tool，看 LLM 行為差異

4. **避免 framework 陷阱**
   - FIRN 不要過度封裝——保持每層可 trace
   - 如果日後需要 LangChain/MCP 等整合，確保底層 call 可見

---


### 來源

- 原始報告：2026-05-29-code-agents-vs-tool-based-agents-2026.md
- 類型：
- 連結：
