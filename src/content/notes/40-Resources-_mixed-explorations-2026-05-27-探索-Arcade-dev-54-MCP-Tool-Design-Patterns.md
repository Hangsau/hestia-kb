---
_slug: 40-Resources-_mixed-explorations-2026-05-27-探索-Arcade-dev-54-MCP-Tool-Design-Patterns
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-探索-Arcade-dev-54-MCP-Tool-Design-Patterns.md
title: 探索：Arcade.dev 54 MCP Tool Design Patterns
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arcade
- context
- design
- dev
- mcp
- pattern
- patterns
- talos
- tool
created: '2026-05-27'
updated: '2026-06-15'
status: budding
---

# 探索：Arcade.dev 54 MCP Tool Design Patterns

**日期**: 2026-05-27 | **來源**: web search + arcade.dev blog

## 核心洞察

Arcade.dev 從 8000+ 工具、100+ 整合的生產經驗萃取出 54 個 MCP tool design patterns。

### 最重要的核心發現

**"Working" ≠ "Agent-usable"** — 一個工具可以回傳正確資料但仍然失敗，因為 agent 無法判断何时该调用它。

### 三軸分類框架

每個工具存在於三個維度的交點：

| 維度 | 選項 |
|------|------|
| Maturity（複雜度） | Atomic（單一操作）→ Orchestrated（多操作協調） |
| Integration（連接類型） | API / Database / File System / System |
| Access Pattern（執行模式） | Sync / Async / Streaming / Event-driven |

### 四個 Cross-Cutting Concerns

1. **Agent Experience**：工具描述、參數名稱、錯誤訊息都為 LLM 優化，不是為人類
2. **Security Boundaries**：Prompt 表達意圖，程式碼強制規則。授權和密鑰必須在 server-side 處理
3. **Error-Guided Recovery**：錯誤要教 agent 如何恢復，不是只失敗。429 → 「rate limited, retry after 30s or reduce batch to 50」
4. **Tool Composition**：工具應該像 Unix pipe 一樣組合，不是 command chain。回應形狀一致、支援 batch、多個抽象層

### 54 Patterns，10 Categories

| Category | 核心問題 |
|----------|----------|
| Tool Types | Query, Command, or Discovery? |
| Tool Interface | How will agents understand and call it? |
| Tool Discovery | How do agents find the right tool? |
| Tool Composition | Should it bundle operations? |
| Tool Execution | Sync, async, or transactional? |
| Tool Response | What should results look like? |
| Tool Context | How is identity and state managed? |
| Tool Resilience | How does it recover from failures? |
| Tool Security | How is access controlled? |
| Integration | How does it connect to external systems? |

### 具體 Pattern 範例

**Parameter Coercion**：agent 可能傳「2024-01-15」、「January 15」、或「yesterday」，工具全部接受並內部正規化。

**Idempotent Operation**：資料庫工具必備 because agents retry on timeout，工具必須優雅處理重複呼叫。

**Async Job**：報告生成工具 blocking 45 秒會 timeout。解法：agent 呼叫 `generate_report()` → 收到 job ID → 輪詢 `check_status(job_id)` 直到完成。

**Context Injection**：使用者身份、權限、憑證透過 server-side context object 傳遞，絕不通過 LLM prompt。

### 對 Talos 的啟發

1. **Tool interface design**：Talos 的 governance pipeline 工具（comms reader、memory distill、snapshot）都應該用「agent-optimized」描述，不是工程師視角
2. **Error-guided recovery**：heartbeat 的 error sensor 輸出可以改進——提供恢復指引而非只是「failed」
3. **Tool composition**：未來的 Talos 工具應該支援 batch 模式和一致回應形狀
4. **Security boundary**：context injection pattern 呼應了 Hestia/Talos 雙 agent 的 auth design

## 未追蹤 Leads
- https://www.arcade.dev/patterns — 完整 54 patterns 目錄
- https://www.arcade.dev/blog/mcp-runtime-gateway — MCP gateway 架構

## ✅ 本次探索完成
