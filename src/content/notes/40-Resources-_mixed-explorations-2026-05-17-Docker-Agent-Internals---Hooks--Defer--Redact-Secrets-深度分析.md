---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-Agent-Internals---Hooks--Defer--Redact-Secrets-深度分析
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-Agent-Internals---Hooks--Defer--Redact-Secrets-深度分析.md
title: Docker Agent Internals — Hooks, Defer, Redact Secrets 深度分析
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- defer
- docker
- hook
- hooks
- portcullis
- pre
- redact
- talos
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker Agent Internals — Hooks, Defer, Redact Secrets 深度分析

**日期**: 2026-05-17 | **來源**: [[2026-05-17-docker-agent-yaml-schema-policy-enforcement]] 未追蹤 leads
**標籤**: #talos #governance #hooks #defer #secret-detection #portcullis #tool-governance
**延續自**: [[2026-05-17-docker-agent-yaml-schema-policy-enforcement]]

## Per-Source Insights

### 1. Hooks — Lifecycle Hook Architecture（`pkg/hooks/`）

Docker Agent 的 hook 系統是 production-grade 的 lifecycle enforcement framework。20+ event types，三種 hook 類型，concurrent dispatch。

**Event Type 分類**：

| 類別 | Event | 角色 |
|---|---|---|
| **Pre-execution gates** | `pre_tool_use`, `permission_request`, `before_llm_call`, `user_prompt_submit` | 閘控：允許/拒絕/修改 |
| **Post-execution** | `post_tool_use`, `after_llm_call`, `turn_end`, `stop`, `notification` | 觀測：記錄、metrics、審計 |
| **Lifecycle** | `session_start`, `session_end`, `subagent_stop`, `on_agent_switch`, `on_session_resume` | 生命週期管理 |
| **Error/Limit** | `on_error`, `on_max_iterations` | 異常處理 |
| **Compaction** | `pre_compact`, `before_compaction`, `after_compaction` | Context 管理 |
| **Transformation** | `tool_response_transform` | 輸出改寫 |

**Hook 類型**：
- `command` — shell command，stdin 收 JSON input，stdout 回 JSON output
- `builtin` — in-process Go function，透過 `Registry.RegisterBuiltin()` 註冊
- `model` — LLM-as-judge（runtime 層註冊，依賴 model provider stack）

**架構亮點**：
1. **Fail-closed for gates, fail-open for observation** — `pre_tool_use` 預設 deny，`post_tool_use` 不 block
2. **Concurrent dispatch** — 同 event 內 hooks 並行跑（goroutine + WaitGroup），用 `aggregate()` 合併 verdict
3. **Matcher system** — `MatcherConfig` 含 tool-name regex，`compileMatchers()` 預編譯。`""` 和 `"*"` 都 compile 為 nil（match all）
4. **Dedup** — `hooksFor()` 用 `(type, command, args)` 做 dedup，防止 YAML explicit hook 和 runtime auto-inject 重疊
5. **Registry pattern** — `Registry` 是 `map[HookType]HandlerFactory`，embedder 可以註冊自訂類型（HTTP webhook 等）而不改 executor

**Decision protocol**（`pre_tool_use` / `permission_request`）：
- Exit code 2 = `continue=false` = block
- Exit code 0 + stdout JSON → parse `{decision, reason, updated_input}`
- Exit code 0 + stdout plain text → treated as `{decision: "allow", reason: <text>}`
- `permission_request` 有獨立的 `PermissionAllowed` flag（因為 allow 是 explicit auto-approve，和 `pre_tool_use` 的 implicit allow 不同）

### 2. Defer — Lazy Tool Loading（`pkg/tools/builtin/deferred/`）

極簡但有效的 lazy loading 設計：

```
DeferredToolset wraps regular toolset
  → exposes only search_tool + add_tool initially
    → agent uses search_tool("git") to find relevant tools
      → add_tool("git_commit") to activate
        → tool now visible in agent's tool list
```

**核心結構**：
```go
type Toolset struct {
    deferredTools  map[string]deferredToolEntry  // 未啟用
    activatedTools map[string]tools.Tool           // 已啟用
    sources        []deferredSource                // 延遲來源
}
```

**`AddSource(toolset, deferAll, toolNames)`** — 三個控制維度：
- `deferAll=true` — 整個 toolset 延遲
- `deferAll=false` + `toolNames=["x","y"]` — 只延遲特定 tools

**Design decisions**：
- 搜尋用 case-insensitive substring match（非 semantic），簡單可控
- 啟用後永久有效（session lifetime）
- `search_tool` 和 `add_tool` 標為 `ReadOnlyHint: true`
- instructions 直接提示 agent：「Use search_tool to discover additional tools」

### 3. Redact Secrets — Portcullis Integration（`pkg/hooks/builtins/redact_secrets.go`）

**三腿防禦**：

| 攔截點 | Hook Event | 改寫目標 | 回傳欄位 |
|---|---|---|---|
| Tool 參數 | `pre_tool_use` | `ToolInput` (recursive) | `UpdatedInput` |
| 外送訊息 | `before_llm_call` | `Messages.Content` + `ReasoningContent` | `UpdatedMessages` |
| Tool 輸出 | `tool_response_transform` | `ToolResponse` (string) | `UpdatedToolResponse` |

**底層引擎**：`github.com/docker/portcullis` — 獨立 Go package，`portcullis.Redact(string) string`。

**Recursive redaction**：`redactAny()` 遞迴走 `map[string]any` / `[]any`，確保 JSON payload 內的 secret 也被抓到。非 string 型別直接 pass through。

**優化**：
- 回傳 nil 表示 nothing changed → executor 走 cheap path
- `UpdatedInput` 只含真正被改寫的 key（避免 concurrent hook 互相覆蓋）
- `UpdatedMessages` 傳完整 slice（不是 delta），因為 runtime swap in entire slice

## Hermes 啟發

### 1. Hook Architecture → Talos Phase 2-3 Blueprint

Docker Agent 的 hook 系統給 Talos 的 enforcement hook 設計提供了 concrete reference：

- **Talos Phase 2**（Policy definition）→ 對標 `HooksConfig` YAML schema。Talos 的 `guardian_policy.yaml` 可以借鑑 Docker 的 event type taxonomy + matcher system。
- **Talos Phase 3**（Enforcement）→ `pre_tool_use` hook 就是 Talos 需要做的：每次 tool call 前檢查 policy。Matcher system 讓不同 policy rule 只對應特定 tools（如：探索模式不給 terminal、不給 write_file）。

**可直接借鑑的設計**：
- Fail-closed for security gates（`pre_tool_use` 預設 deny）
- Concurrent dispatch（多個 policy check 平行跑，不增加 latency）
- Dedup（避免 runtime auto-inject 和 explicit config 重疊）

### 2. Defer → Hermes Tool Loading 優化

Hermes 目前有 128 skills，但 tool 層沒有 lazy loading。Docker 的 defer pattern 給了一個低成本方案：
- Hermes 探索模式只給 `web_search, web_extract, read_file, search_files` 四個 tools
- 如果探索 agent 需要 `terminal`（如跑 sanitizer），它用類 `search_tool` 找到 → `add_tool` 啟用
- 這比靜態 tool scoping 更靈活，同時保持最小權限原則

**和 skill_view() 的差異**：skill_view 是 knowledge lazy loading（LLM 決定讀不讀），defer 是 capability lazy loading（tool 本身不存在於 agent 的 tool list 中）。兩者互補。

### 3. Redact Secrets → secret-leak-prevention 升級路徑

Hermes 的 `secret-leak-prevention` skill 目前用 regex scan。Docker 的三腿方案更全面：

| | Hermes 現狀 | Docker 方案 |
|---|---|---|
| Tool 參數 | ❌ 不掃 | `pre_tool_use` → recursive redact |
| 外送訊息 | ❌ 不掃 | `before_llm_call` → redact content |
| Tool 輸出 | ✅ regex scan | `tool_response_transform` → portcullis engine |

**可行的升級**：(1) 把 `secret-leak-prevention` skill 從 post-hoc scan 改為 hook-based（三個攔截點）；(2) 評估 portcullis 的 Go package 是否可透過 Python binding 或 subprocess 整合；(3) 短期至少加 `pre_tool_use` 等級的參數掃描。

## Governance Stack 收斂

三個機制的組合形成完整的 governance stack：

```
hooks →  提供 hook point（何時執行治理）
defer →  減少攻擊面（只載入需要的 tools）
redact → 保護資料面（防止 credential 外洩）
```

對 Talos 的意義：Docker Agent 不是抽象治理框架，而是 **production code 中三層治理已經協同運作**。Talos 的 governance 設計不需要從零開始，可以逐層對標：
1. Hook points（Phase 2）→ 對標 Docker hooks event types
2. Tool scoping（WS-009）→ 對標 Docker defer
3. Secret protection（現有）→ 對標 Docker redact_secrets/portcullis

## ⏳ 未追蹤

- Docker Agent `snapshot_hooks.yaml` / `hooks.yaml` examples — 了解實際 hook 配置範例（`examples/` 目錄有 `redact_secrets_hooks.yaml`）
- Docker Agent `cache` 機制（`CacheConfig`）— response cache：相同問題 replay 不用 call model
- `model_handler.go` — hook type "model"（LLM-as-judge）的實作細節
- portcullis 獨立 package（`github.com/docker/portcullis`）的 detection ruleset 定義 — 了解它支援哪些 secret pattern

## ✅ 本次探索完成

