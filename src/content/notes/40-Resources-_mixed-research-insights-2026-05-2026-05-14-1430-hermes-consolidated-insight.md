---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-14-1430-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-14-1430-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- mcp
- architecture
- hermes-internal
source: multi
created: '2026-05-14'
confidence: high
title: MCP 工具鏈分裂成輸入/輸出兩軸，Hermes 是天然統一點
updated: '2026-06-15'
type: research
status: budding
---

# MCP 工具鏈分裂成輸入/輸出兩軸，Hermes 是天然統一點

**消化筆記**: contextforge-spike, hermes-gateway-anatomy, context-mode-mcp, post-vector-agent-memory, lazy-tool-mcp-bloat, axe-unix-agents

MCP 生態正在快速分化成兩個獨立的優化方向（input schema bloat vs output data bloat），解法各自為政。同時，四個獨立專案在半年內不約而同選了同一套技術棧（SQLite FTS + 單一二進位 + 宣告式設定），形成一個尚未被明確指認的產業共識。Hermes gateway 的架構恰好坐在這兩個趨勢的交會點。

---

## Cross-Cutting Theme 1: MCP 工具鏈分裂成「輸入端」與「輸出端」兩個戰場，解法正在碎片化

**支援筆記**: lazy-tool-mcp-bloat, context-mode-mcp, contextforge-spike, hermes-gateway-anatomy

### 分析

MCP 生態正在圍繞**同一個根本問題的兩個側面**各自發展解法，但沒有人把它們視為同一層的問題：

| 側面 | 問題 | 代表工具 | 手法 |
|------|------|---------|------|
| **輸入端** | tool schema 太多，佔滿 prompt | lazy-tool | search-before-invoke，5 個 meta-tool 取代 N 個 tool schema |
| **輸出端** | tool 回傳太多 raw data | Context Mode | subprocess sandbox，只讓 stdout 回 context（-98%） |
| **輸出端** | tool 回傳太多 raw data | ContextForge | MCP reverse proxy，中間層過濾/轉換 |

lazy-tool 的筆記自己點出了這個 split（「lazy-tool 處理 input side，ContextForge 處理 output side」），但它只比較了 lazy-tool 和 ContextForge。把 Context Mode 也拉進來看，問題更清楚：**輸出端現在有兩個獨立的解法在碎片化**，而輸入端只有一個。更關鍵的是，沒有人在做統一層——一個同時處理 input schema bloat 和 output data bloat 的 MCP proxy。

Hermes gateway 的六層架構（hermes-gateway-anatomy）完全沒有 MCP 層的概念——gateway 不知道 MCP 的存在，MCP connection 是 per-session 透過 native-mcp skill 直接 stdio 建立的。這意味著：**Hermes gateway 要加這一層的位置是空的，沒有需要拆除的既有實作。**

### 可行動下一步

在 Hermes gateway 的 message handling loop（Layer 5）和 MCP tool execution 之間，插入一個「Context Filter」middleware 原型：攔截 tool call request（過濾/搜尋 schema）和 tool response（sandbox/summarize output）。先用 Context Mode 的 subprocess sandbox 模式做 output filtering（因為 MIT license，可直接參考），input filtering 留 stub。一週內可出 MVP。

---

## Cross-Cutting Theme 2: SQLite FTS + 單一二進位 + 檔案即真相——2026 Agent 工具鏈的沉默共識

**支援筆記**: lazy-tool-mcp-bloat, context-mode-mcp, axe-unix-agents, post-vector-agent-memory

### 分析

四個獨立專案，四個不同問題域，半年內做出高度一致的技術選擇：

| 專案 | 問題域 | 語言/部署 | 儲存層 | 設定格式 |
|------|--------|----------|--------|---------|
| lazy-tool | MCP schema bloat | Go single binary | SQLite FTS | YAML |
| Context Mode | MCP output bloat | npx package | SQLite FTS5 + BM25 | MCP config |
| Axe | Agent runner | Go single binary (12MB) | Markdown files | TOML |
| Google Always On / memU / SQLite Memory | Agent memory | Python / local | SQLite / filesystem | Markdown |

共同模式：**不要 vector DB、不要 cloud dependency、不要 daemon。** SQLite 是萬用後端（FTS 搜尋 + structured storage），檔案系統是 truth source，單一二進位或輕量 package 是部署單位。

這不是巧合。這是產業在 2025-2026 學到的教訓的集體反映：vector DB 對 agent tooling 過重（維運成本、延遲、語意雜訊），FTS 對結構化/半結構化內容（tool schema、markdown notes、code blocks）的檢索品質更好，而且不需要 embedding API。

Hermes 已經是這個共識的一部分（file-based skills、SQLite session store、autonomous_notes），但**尚未採用 SQLite FTS 做 runtime search**——目前的 session_search 依賴外部 embedding API。這個選擇跟產業方向相反。

### 可行動下一步

將 Hermes 的 session_search 加上 local FTS5 fallback/primary path。具體做法：在 session storage 層加一個 FTS5 virtual table，對 session transcript、autonomous_notes、proposals 做 index。搜尋時先走 FTS5（零延遲、零 API cost），只在語意搜尋必要時才 fallback 到 embedding。目標：80% 的 recall 場景用 FTS5 解決，省掉 embedding API 成本。

---

## Cross-Cutting Theme 3: Hermes 缺的不是一個功能，是整個「資訊消化層」——從記憶到 MCP 工具輸出的統一缺口

**支援筆記**: hermes-gateway-anatomy, context-mode-mcp, post-vector-agent-memory, contextforge-spike

### 分析

之前的 consolidation synthesis 指出 Hermes 缺 Consolidation Step（記憶消化）。這批筆記揭示了同一個缺口在另一個維度的表現：

```
                ┌─ 記憶層 ─────────────┐  ┌─ MCP 工具層 ──────────┐
                │                       │  │                       │
輸入            │ autonomous_notes      │  │ tool schema (N 個)     │
                │ session transcripts   │  │ tool results (raw)     │
                │ ↓                     │  │ ↓                      │
現狀            │ ❌ 無消化              │  │ ❌ 無過濾              │
                │ ↓                     │  │ ↓                      │
需要的          │ ConsolidateAgent      │  │ Context Filter         │
                │ (Google Always On)    │  │ (Context Mode/lazy-tool)│
                │ ↓                     │  │ ↓                      │
輸出            │ cross-cutting insight │  │ 精簡 schema + 結果     │
```

兩個缺口是同一個問題的兩種表現：**Hermes 沒有「在資訊進入 agent context window 之前先處理它」的機制。** 記憶是「歷史資訊的消化」，MCP 工具是「即時資訊的過濾」。產業正在分別解決這兩個問題，但 Hermes 可以把它們統一成一層。

更關鍵的是：Hermes gateway 的架構（hermes-gateway-anatomy）已經有完美的插入點——Layer 4（Background Subsystems）的 heartbeat 可以負責記憶消化（非即時），Layer 5（Message Handling Loop）可以插入 MCP 工具過濾（即時）。不需要新架構，只需要填兩個空位。

### 可行動下一步

定義一個 `DigestionLayer` 的介面規範（abstract base 或 protocol），包含兩個方法：`consolidate_memory()`（非即時，heartbeat 觸發）和 `filter_tool_context()`（即時，per-tool-call 觸發）。然後分兩路實作：(1) consolidate_memory 用現有的 `consolidate_memory.py`，補上 Google Always On 式的 cross-topic insight generation；(2) filter_tool_context 先做 output filtering（參考 Context Mode 的 subprocess sandbox），再做 input filtering（參考 lazy-tool 的 search-before-invoke）。兩個實作獨立進行，但共用同一個 DigestPolicy 設定（閾值、策略、allowlist）。

---

## 品質自我評估

| 標準 | 自評 | 證據 |
|------|:----:|------|
| 包含非顯然的跨主題連結 | ✅ | Theme 1（lazy-tool 只比較了 ContextForge，沒注意到 Context Mode 也在做同一側）；Theme 3（記憶消化 + MCP 過濾是同一個缺口） |
| 包含可行動的 next step | ✅ | Theme 1: Context Filter middleware MVP；Theme 2: FTS5 fallback for session_search；Theme 3: DigestionLayer 介面規範 |
| 不只是 summary | ✅ | Theme 3 把兩個看似無關的缺口（記憶 consolidation 和 MCP 過濾）識別為同一層問題 |
| 有引註 | ✅ | 每 theme 明確標記支援筆記 |

**Confidence: high** — Theme 1 有 4 篇筆記交叉驗證，Theme 2 有 4 篇獨立專案收斂，Theme 3 有 4 篇筆記從不同角度指向同一缺口。

---

## 關鍵詞

`mcp-proxy` `input-output-split` `sqlite-fts-consensus` `digestion-layer` `single-binary-pattern` `context-filter` `architecture-gap`
