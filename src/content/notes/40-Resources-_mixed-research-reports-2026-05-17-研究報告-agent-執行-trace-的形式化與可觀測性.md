---
_slug: 40-Resources-_mixed-research-reports-2026-05-17-研究報告-agent-執行-trace-的形式化與可觀測性
_vault_path: 40-Resources/_mixed/research/reports/2026-05-17-研究報告-agent-執行-trace-的形式化與可觀測性.md
tags:
- research
- knowledge
- ai-agent
created: '2026-05-17'
version: 1
source_report: 2026-05-18-agent-trace-observability-formalization.md
source_url: null
type: research
fingerprint: trace, agent, github, gen, opentelemetry, https, com, repo, schema, agent-replay
title: 研究報告：Agent 執行 Trace 的形式化與可觀測性
updated: '2026-06-15'
status: budding
---

# 研究報告：Agent 執行 Trace 的形式化與可觀測性

## Version 1 — 2026-05-17

### 核心觀念
**問題**：當 AI Agent 進入生產環境，開發者立刻面臨一個根本問題：**你看不到它在幹嘛**。LLM 的輸出是非確定性的，一個 agent 可能呼叫 30 次工具、穿越多個决策節點、最後給你一個錯的答案——而你唯一的除錯工具就是無盡的 JSON ログ。 這個問題在 2025-2026 年隨著 agent 系統複雜度暴增而尖銳化。現有方案分為兩派： - **商業平台**：LangSmith、AgentOps、Traceloop——功能強但要錢、資料出境 - **開源碎片**：十幾種工具各自定義自己的 trace 格式，互不相通 核心問題是：**沒有一個統一的 trace 格式標準**。每個框架說「我…

**洞見**：**對 AI agent 領域的影響：** 1. **Debugging 生產問題**：當 agent 在凌晨 3 點給了錯誤答案，你能用 time-travel 找到根本原因，而不是猜 2. **Prompt 版本控制**：每次 prompt 改動都能跟歷史 trace diff，避免 regression 3. **合規審計**：金融、醫療場景需要完整 lineage——什麼時間呼叫了什麼、回了什麼、誰批准了什麼 4. **成本控制**：追蹤 token 用量不只是省錢，還能發現异常的 agent 行为模式（比如無意義的迴圈呼叫） 5. **多框架統一可觀測性**：當 OpenTeleme…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 OpenTelemetry GenAI Semantic Conventions（格式標準）

這個是本領域目前最重要的基礎建設。OpenTelemetry 社群定義了 GenAI 操作的標準 span/event 格式，schema URL 是 `https://opentelemetry.io/schemas/gen-ai/1.42.0`。

**核心 spans：**
```yaml
# gen_ai.inference.client
# Span kind: CLIENT
# 捕獲 LLM 呼叫的完整上下文
attributes:
  - gen_ai.request.model          # 模型名
  - gen_ai.usage.input_tokens     # 輸入 token 數
  - gen_ai.usage.output_tokens    # 輸出 token 數
  - gen_ai.request.temperature
  - gen_ai.request.max_tokens
  - gen_ai.response.finish_reasons
  - gen_ai.conversation.id       # 對話 ID
  - gen_ai.agent.id / .name / .version  # Agent 身份
  - gen_ai.data_source.id         # 知識來源
```

**關鍵 events：**
- `gen_ai.client.inference.operation.details`：詳細的推論請求資訊（chat history + 參數）
- `gen_ai.evaluation.result`：品質評估結果（分數、解釋）
- `gen_ai.client.operation.exception`：API 錯誤、rate limit、timeout

這套 convention 的價值在於它是**供應商中立**的——OpenLIT、LangSmith、Traceloop 都採用這套 schema，理論上可以互通。

### 2.2 Trace 資料的層次結構

目前業界共識，一個完整的 agent trace 應該包含四層：

| 層次 | 內容 | 工具/標準 |
|------|------|-----------|
| **LLM 層** | prompt、response、token count、finish reason | OpenTelemetry gen_ai spans |
| **工具層** | tool name、arguments、result、latency | OpenTelemetry span events / 自訂 |
| **决策層** | agent 選擇哪個 action、為什麼 | 自訂 JSON（無標準） |
| **系統層** | 子程序、記憶體寫入、外部 API 呼叫 | OpenTelemetry general spans |

大多數工具只做第一層，agent-trace 這類工具號稱要做「工具層」——把 strace 的概念帶進來，捕獲每個 tool call 的輸入輸出。

### 2.3 Time-travel Debugging（時間軸回溯除錯）

agent-replay 這個工具最具啟發性的設計：用 SQLite 儲存完整執行 trace，提供時間軸回溯能力：
- **replay**：像倒帶一樣重看整個執行過程
- **fork**：在任意 step 切入，改 input，看會怎麼跑
- **diff**：兩個 run 並排比對，找出分歧點
- **eval**：自動 hallucination detection、safety audit、completeness check
- **guard**：即時 kill-switch，攔截危險 pattern

```bash
agent-replay list --status failed --since 7d
agent-replay show <trace-id>   # 逐步檢視
agent-replay replay <trace-id> # 動畫終端回放
agent-replay fork <trace-id> --step 5  # 從第 5 步分叉測試
```

### 2.4 即時視覺化（Live Visualization）

LangGraphics 的切入點很不一樣——它不是存 trace，而是**在執行時畫圖**。一行 code 就能把 LangGraph 的狀態圖轉成瀏覽器裡的即時動畫：

```python
from langgraph.graph import StateGraph, MessagesState
from langgraphics import watch

workflow = StateGraph(MessagesState)
workflow.add_node(...)
graph = watch(workflow.compile())
await graph.ainvoke({"messages": [...]})  # 瀏覽器裡即時看見執行路徑
```

完全本地、不需要 API key、不需要註冊。這是個被嚴重低估的路線——**在本地端做到 production 等級的可視化**。

### 2.5 MCP 作為 Trace Query Interface

OpenTelemetry MCP Server 把查詢 trace 變成一個 **MCP tool call**——你可以在 IDE 裡直接問 Claude：

> 「找出最近一小時有錯誤的 traces」
> 「比較 v1 和 v2 prompt 的 token 用量差異」

背後對接 Jaeger、Grafana Tempo、Traceloop 等後端。這個方向很有趣：讓 AI 本身變成 trace 的 query interface，而不是讓人手工過濾。

---

### 思考
## 4. Limitations / Honest Assessment

### 作者坦承的限制

- **OpenTelemetry GenAI conventions 目前是 `stability: development` 状态**：還在變，1.42.0 schema 還不是 stable，意味着今天 instrument 的代碼明年可能需要 migration
- **agent-replay 是 Node.js 工具**：如果你的 agent 是 Python 寫的，攔截 layer 要自己處理（JSON export 是唯一橋接方式）
- **LangGraphics 只支援 LangGraph**：其他框架（CrewAI、AutoGen、AG2）沒有類似的本地視覺化方案
- **Trace 資料量极大**：一個複雜的 agent session 可能產生幾百 MB 的 trace，SQLite 儲存和查詢都是瓶頸

### 我們的獨立評估

- **聲稱的突破大部分是行銷**：各工具號稱「AI observability revolution」，但底層都是 OpenTelemetry，差異只在包裝和 UX
- **真正的新東西不多**：`agent-replay` 的 time-travel 概念是 1970 年代 debugger 的老概念，只是應用在了 LLM agent
- **「完全本地」是偽命題**：OpenTelemetry SDK 預設還是往雲端後端送 trace，要真的完全本地需要另外架 Jaeger/Tempo，複雜度不低
- **沒有銀彈**：Trace 只能告訴你「發生了什麼」，不能告訴你「為什麼 LLM 選了這個 action」——那是 evaluation 的範疇

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 對 firn/managed-agents 的具體建議

#### A. 採用 OpenTelemetry GenAI Conventions（TRIVIAL to MODERATE）

**目標**：讓 firn 的執行 trace 可以被任何 OpenTelemetry 相容工具消費

**做法**：
- 在現有 logger 層加上一層 thin wrapper，輸出符合 `gen_ai.inference.client` schema 的 span
- 核心欄位：`gen_ai.request.model`、`gen_ai.usage.*`、`gen_ai.agent.id`、`gen_ai.conversation.id`
- 不需要完整 OTEL SDK，用 JSON 輸出再自己想辦法導出即可

**影響模組**：`hermes-gateway` 的 logger、每個 tool 的 wrapper

**難度**：MODERATE——JSON schema 是現成的，但需要規範所有 tool 輸出格式

**免費方案**：完全免費，純 JSON

#### B. 實作本地 time-travel debugger（MODERATE to HARD）

**目標**：用 SQLite 完整記錄每個 managed agent session，支援 replay/diff/fork

**做法**：
- 每個 agent session 結束後，寫入一個 SQLite 檔案（`.firn/traces/`）
- schema：`sessions(id, agent_id, step, timestamp, type, data_json)`
- 提供 CLI：`firn-trace list`、`firn-trace replay <id>`、`firn-trace diff <id1> <id2>`
- eval 和 guard 功能可以後期再補

**影響模組**：需要新的 `trace/` 子系統

**難度**：MODERATE——核心 record/replay 不難，但要做到 `fork`（在任意 step 重新執行）需要保存完整狀態快照，複雜度陡增

**免費方案**：SQLite 無成本

#### C. 加入 LangGraphics 類的 live graph 可視化（HARD）

**目標**：讓 operator 在瀏覽器裡即時看到 managed agents 的決策圖

**做法**：
- 這個更適合作為可選的 debug mode，不是標配
- 如果 managed-agents 的 workflow 有明確的 graph 結構（plan → execute → review），可以套用類似模式
- 一個 `firn watch <session-id>` 在瀏覽器開視覺化

**難度**：HARD——需要前端能力，目前團隊可能沒有

**免費方案**：可用 Python + Flask 自己做一個簡化版

#### D. 採用 OpenLIT 整合（HARD）

**目標**：用 OpenLIT 替 firn 加上 50+ LLM provider、vector DB、GPU 的可觀測性

**做法**：
- `pip install openlit` + 一行初始化
- 缺點：目前架構是 Python-first，hermes-agent 是 TypeScript/Node.js，需要包一個 thin Python wrapper

**難度**：HARD——架構 mismatch

**免費方案**：OpenLIT 開源版免費，但需要自架 ClickHouse + OTel Collector

---


### 來源

- 原始報告：2026-05-18-agent-trace-observability-formalization.md
- 類型：
- 連結：
