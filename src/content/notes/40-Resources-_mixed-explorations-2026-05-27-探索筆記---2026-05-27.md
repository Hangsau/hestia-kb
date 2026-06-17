---
_slug: 40-Resources-_mixed-explorations-2026-05-27-探索筆記---2026-05-27
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-探索筆記---2026-05-27.md
title: 探索筆記 — 2026-05-27
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arcade
- blog
- catalog
- context
- dev
- llm
- mcp
- patterns
- tool
created: '2026-05-27'
updated: '2026-06-15'
status: budding
---

# 探索筆記 — 2026-05-27

**主題**: Arcade 52 Tool Patterns 全目錄（完整結構化 catalog）
**延續自**: [[2026-05-27-llm-agent-loop-tool-patterns]]

## Per-Source Insights

### Arcade.dev — 52 Patterns Full Catalog

**實際數量：52 patterns（blog 說 54，可能後來整合了）**，10 categories。與 blog post 相同的分類框架，但有完整 pattern name + 簡短定義。以下填補 blog post 未列出的完整 pattern list：

#### Tool (4)
- **Tool** — atomic callable unit
- **Query Tool** — read-only, no side effects
- **Command Tool** — performs actions with side effects
- **Discovery Tool** — reveals available operations/schema/capabilities

#### Tool Interface (7)
- **Tool Description** — optimized for LLM comprehension, not human reading
- **Constrained Input** — enums, ranges, validation to limit inputs
- **Smart Defaults** — reduce required parameters
- **Natural Identifier** — accept human-friendly identifiers, resolve internally
- **Mutual Exclusivity** — enforce 'exactly one of X or Y'
- **Performance Hint** — guide agents toward efficient usage
- **Parameter Coercion** — accept flexible input formats, normalize internally

#### Tool Discovery (5)
- **Tool Registry** — catalog of available tools with capabilities
- **Schema Explorer** — progressive revelation through layered discovery
- **Dependency Hint** — embed 'call X before Y' in descriptions
- **Capability Matching** — find by intent/capability, not just name
- **Health Check** — verify availability before relying on it

#### Tool Composition (6)
- **Abstraction Ladder** — multiple levels of granularity for same capability
- **Task Bundle** — combine multiple operations into single tool
- **Batch Operation** — process multiple items in one call
- **Operation Mode** — different modes for different access patterns
- **Tool Chain** — explicit sequences for complex workflows
- **Scatter-Gather Tool** — fan out, then combine results

#### Tool Execution (6)
- **Synchronous Execution** — immediate request-response
- **Async Job** — long-running with job IDs and polling
- **Idempotent Operation** — safe to retry, identical results
- **Transactional Boundary** — all-or-nothing for multi-step
- **Compensation Handler** — undo completed steps on failure
- **Timeout Boundary** — max execution time with graceful termination

#### Tool Output (6)
- **Response Shaper** — transform raw API → agent-friendly format
- **Token-Efficient Response** — minimize size, preserve essentials
- **Paginated Result** — cursor-based for large result sets
- **Progressive Detail** — summary by default, full detail on request
- **GUI URL** — links to view/edit results in web interface
- **Partial Success** — report mixed success/failure for batch

#### Tool Context (4) — MCP-native
- **Identity Anchor** — establish user identity/context at session start
- **Resource Reference** — point to external data by URI
- **Context Injection** — auto-inject relevant context agent didn't request
- **Context Boundary** — scope/boundaries of tool operations

#### Tool Resilience (6)
- **Recovery Guide** — actionable error messages telling agents how to fix
- **Error Classification** — distinguish retryable vs permanent failures
- **Confirmation Request** — request clarification on ambiguous input
- **Fuzzy Match Threshold** — auto-accept high-confidence, confirm uncertain
- **Graceful Degradation** — return partial results when full not possible
- **Fallback Tool** — alternative when primary unavailable

#### Tool Security (4)
- **Secret Injection** — inject credentials at runtime, never via LLM
- **Permission Gate** — enforce access control in code, not prompts
- **Scope Declaration** — declare required OAuth scopes per tool
- **Audit Trail** — log all invocations for security/debugging

#### Compositional (4)
- **Tool Gateway** — unified interface to multiple backends
- **Tool Adapter** — wrap legacy APIs as agent-friendly tools
- **Canonical Tool Model** — standard data models across ecosystem
- **Tool Versioning** — multiple versions coexisting

### LLM-Optimized Text endpoint

**URL**: `https://arcade.dev/patterns/llm.txt`

頁面有 `LLM-optimized text: https://arcade.dev/patterns/llm.txt` — 這是給 LLM 直接讀取的純文字版 catalog，結構化但無 HTML。用於：當 context 吃緊時，直接 fetch `llm.txt` 而非整頁 HTML。

## 跨文章 Synthesis

### 與 2026-05-27 note 的關聯

Blog post 提到「54 patterns」但只摘要了 cross-cutting concerns（Agent Experience / Security Boundaries / Error-Guided Recovery / Tool Composition）。完整 catalog 比 blog post 多了幾個關鍵類別：

1. **Tool Context (4)** — MCP-native category，明確區分於其他 generic patterns。這對應 WS-034（gateway）和 WS-035（policy engine）正在做的 MCP tool governance。

2. **Tool Discovery (5)** — 與 Herme s現有能力最有 gap 的類別。現有 `skills_list` / `skill_view` 是某種程度的手動 Discovery Tool，但：
   - 無 `Schema Explorer`（分層 reveal structure）
   - 無 `Capability Matching`（以意圖而非名稱找 tool）
   - `Health Check` pattern 對應 cron job aliveness 檢測，但尚未封裝成 tool 可被 LLM 查詢

3. **Tool Resilience** — Recovery Guide 和 Error Classification 正是 Hermes tool error messages 缺乏的。429 → "rate limited" 不夠；應該是 "rate limited, retry after 30s or reduce batch size to 50"。

4. **Tool Security** — Secret Injection pattern（credentials at runtime, never via LLM）是 HMAC proposal（WS-015）的技術基礎。

### 一致收斂點

1. **「working ≠ agent-usable」**：Tool Description pattern 直接命名這個問題（"optimized for LLM comprehension, not human reading"）。Constrained Input、Smart Defaults、Parameter Coercion 都是試圖解決這個落差的具體技術。

2. **Tool Composition 是 first-class concern**：Abstraction Ladder、Task Bundle、Batch Operation、Tool Chain、Scatter-Gather — 這 5 個 composition patterns 合計佔 6/52，是最大類別。Sketch.dev 的 "minimal tool set, maximum loop" 哲學與 Arcade 的 "rich composition" 哲學其實不矛盾——前者說 tool 要 capable，後者說 capable tools 要能組合。

3. **MCP 架構對應 Tool Context category**：Identity Anchor、Resource Reference、Context Injection、Context Boundary 這 4 個 patterns 幾乎是 MCP 协议的官方 design patterns 說明。Context Boundary（定義 tool 操作範圍）直接解釋了為何 MCP 的 `tools/list` 和 `tools/call` 需要分開。

## Untracked Leads

- https://arcade.dev/patterns/llm.txt （LLM-optimized text version）
- https://arcade.dev/patterns （可存檔，下次直接用 llm.txt）

## ✅ 本次探索完成

