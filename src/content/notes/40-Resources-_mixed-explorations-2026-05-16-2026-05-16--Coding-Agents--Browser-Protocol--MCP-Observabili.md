---
_slug: 40-Resources-_mixed-explorations-2026-05-16-2026-05-16--Coding-Agents--Browser-Protocol--MCP-Observabili
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-2026-05-16--Coding-Agents--Browser-Protocol--MCP-Observabili.md
title: '2026-05-16: Coding Agents, Browser Protocol, MCP Observability'
date: 2026-05-16
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- abp
- agent
- browser
- context
- hermes
- mcp
- opencode
- otel
- server
- session
created: '2026-05-16'
updated: '2026-06-15'
status: budding
---

# 2026-05-16: Coding Agents, Browser Protocol, MCP Observability

**來源**: HN 隨意探索 | **主題**: agent 工具鏈

---

## Per-Source Insights

### 1. OpenCode — 開源 AI coding agent 的兩面性

- **URL**: https://opencode.ai/
- **HN**: 1274pts

OpenCode 有兩個面孔：
1. **原始開源專案**（`opencode-ai/opencode`）— Go + Bubble Tea TUI，已歸檔並遷移到 Charmbracelet 的 [Crush](https://github.com/charmbracelet/crush)
2. **商業化版本**（opencode.ai）— 160K GitHub stars、900 contributors、7.5M 月活開發者，提供 terminal/desktop/IDE 三種介面

**技術細節**：
- Go-based CLI + Bubble Tea TUI（Charmbracelet 生態系）
- 多 session 並行：同一專案可開多個 agent 同時工作
- LSP 整合：自動載入對應語言的 LSP 給 LLM 用
- MCP server 支援（stdio type）
- SQLite 持久化 sessions
- **Auto-compact**：當對話接近 context window 95% 時自動摘要、開新 session 接續
- Non-interactive mode：`opencode -p "prompt"` 跑單次、支援 JSON output
- 75+ LLM providers via Models.dev + GitHub Copilot 帳號整合
- Zen：curated models，OpenCode 自己 benchmark 過確保 coding agent 品質

**對 Hermes 的啟發**：
- OpenCode 的 **multi-session** 架構是 Hermes `delegate_task` 沒有的：Hermes 每個 delegate 是獨立 subprocess，但 OpenCode 讓多個 agent 在同一個 project context 中並行。這和 `worktree-subagent-isolation` skill 互補——worktree 給隔離，OpenCode-style multi-session 給協作。
- **Auto-compact** 的設計值得注意：不是等 context window overflow 才處理，而是在 95% 主動 trigger summary→new session。Hermes 目前沒有等效機制（reliance on model's native context caching）。
- 但 `opencode` skill 現狀只是把它當作 delegate 選項之一（像 Claude Code / Codex 的替代品），沒有深入利用 OpenCode 特有的 multi-session 或 LSP 整合。目前 Hermes 使用 OpenCode 的場景太少，不足以驅動深入整合。

### 2. Agent Browser Protocol — Chromium fork with MCP baked in

- **URL**: https://github.com/theredsix/agent-browser-protocol
- **HN**: 155pts

ABP 是一個 Chromium fork，把 MCP + REST 直接嵌入瀏覽器引擎。核心設計哲學：

> "Web browsing is continuous and async. Agents think in tools and steps."

**關鍵數字**：
- 90.53% on Online Mind2Web
- 2x lower token usage / 2x faster / 2x lower tool calls vs Playwright MCP
- ~100ms overhead per action（含 screenshot）

**架構契約**：one request = one completed step
```
POST /click (x=450, y=320)
→ inject real input event
→ wait for page to settle
→ capture compositor screenshot
→ collect events
→ pause JavaScript + virtual time
→ 200 OK: screenshot + events
→ unpause for next step
```

**設計優勢**：
- No WebSocket, no CDP session management — just HTTP
- Pages freeze between steps → agent 永遠不會 race the browser
- MCP + REST dual interface（`npx -y agent-browser-protocol --mcp` 啟動 MCP server；`curl localhost:8222/api/v1/tabs` 走 REST）
- 直接支援 Claude Code / Codex / OpenCode 的 MCP config

**對 Hermes 的啟發**：
- ABP 的 "settled state" 模型是對 agent↔browser 互動的重新思考：與其讓 agent 處理 async browser events（Playwright 模型），不如讓 browser 主動 freeze→capture→return。這降低了 agent 需要理解的 browser 狀態複雜度。
- Hermes 目前沒有 browser automation tool（web scraping 走 `curl` + `sanitize_fetch.py`）。如果未來需要 interactive browsing（登入、填表單、點擊），ABP 比 Playwright MCP 更適合 agent 心智模型。
- 但 ABP 需要實際跑 Chromium（fork），資源成本比 curl 高很多。對 Hermes 的輕量搜尋場景，curl+sanitizer 足夠；對需要 JavaScript rendering 的頁面才需要 ABP。

### 3. OpenTelemetry for MCP — 雙路徑遙測架構

- **URL**: https://glama.ai/blog/2025-11-29-open-telemetry-for-model-context-protocol-mcp-analytics-and-agent-observability
- **HN**: 14pts

Glama 的文章剖析了如何用 OpenTelemetry 標準化 MCP agent 的可觀測性。

**雙路徑架構**：

| 路徑 | 位置 | 收集什麼 | 方法 |
|------|------|---------|------|
| **Path 1** — Server-side | MCP server 端 | tool latency, error rate, usage breakdown | OTel SDK 直接 instrument server |
| **Path 2** — Client-side | Proxy/gateway（agent ↔ LLM 之間） | token usage, context efficiency, model consumption | 攔截 LLM API call |

**Distributed Tracing 挑戰**：要把 Path 2 的 LLM call trace 連到 Path 1 的 tool execution trace，需要 W3C Trace Context propagation across MCP boundaries。目前缺少標準化的 semantic conventions（`mcp.tool_name`、`agent.session_id`、`llm.cached_tokens` 等都還沒定）。

**實作方案**：Shinzo Labs 的 `@shinzolabs/instrumentation-mcp` TypeScript package，提供 `instrumentServer()` wrapper 自動產生 OTel traces。

**對 Hermes 的啟發**：
- Hermes 的 heartbeat v2 已經做了 **Path 2 的部分**——provider health、cost tracking（`cost_24h` in state file）、token 統計。但 MCP 層完全空白。
- 現有 MCP gateway（`~/.hermes/scripts/mcp_gateway.py`）是天然的 interception point：它已經在 agent ↔ MCP server 之間。加上 OTel spans 是加 instrumentation，不是重構。
- **不需要**走 Shinzo Labs 的 TypeScript 方案——Hermes 是 Python，可以直接用 `opentelemetry-api` + `opentelemetry-sdk`。成本：裝一個 package、在 gateway 的 tool call handler 加 span。
- 但價值有限：Hermes 只有一個 MCP server（native-mcp），distributed tracing 的 "distributed" 部分不存在。OTel 對 Hermes 的邊際價值低於對多 server MCP 生態的價值。

---

## 跨文章 Synthesis

三篇文章看似分散，但有一個共同線索：**agent 工具鏈正在從「能跑就好」進化到「標準化契約」**。

1. **OpenCode** 代表的趨勢：coding agent 不再只是 CLI wrapper，而是 multi-session、LSP-aware、auto-compact 的完整工作環境。契約從 "run this command" 升級到 "manage my development session"。
2. **ABP** 代表的趨勢：browser automation 從 async event-driven（Playwright）轉向 synchronous request-response（HTTP + settled state）。契約從 "here's a browser, deal with it" 變成 "one request = one deterministic result"。
3. **OTel for MCP** 代表的趨勢：observability 從 ad-hoc logging 轉向標準化 distributed tracing。契約從 "maybe log something" 變成 "every span is traceable across boundaries"。

三者的共通語言是 **減少 agent 需要處理的不確定性**：OpenCode 用 auto-compact 減少 context overflow 的意外、ABP 用 freeze-and-capture 消除 race condition、OTel 用 structured traces 取代 guessing where time went。

對 Hermes 的意義：Hermes 已經走在這個方向上（heartbeat 是 structured health、sanitize_fetch 是 deterministic scraping），但在 coding agent 整合（multi-session）和 MCP observability 上還有空間。

---

## 未追蹤 Leads

- OpenCode 的商業化版本 vs Crush（Charmbracelet）— 同源分裂，哪個更有未來？
- `github.com/charmbracelet/crush` — OpenCode 的精神繼承者
- Playwright MCP vs ABP 的 benchmark 方法論 — 聲稱 2x faster，值得驗證
- Shinzo Labs MCP Analytics 平台 — `https://api.app.shinzo.ai`
- OTel Semantic Conventions for GenAI — 標準化進度追蹤
- `@shinzolabs/instrumentation-mcp` — npm package，值得看 source

## ✅ 本次探索完成

