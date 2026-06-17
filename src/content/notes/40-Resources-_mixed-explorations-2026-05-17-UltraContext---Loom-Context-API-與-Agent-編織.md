---
_slug: 40-Resources-_mixed-explorations-2026-05-17-UltraContext---Loom-Context-API-與-Agent-編織
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-UltraContext---Loom-Context-API-與-Agent-編織.md
title: UltraContext + Loom：Context API 與 Agent 編織
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- api
- compaction
- context
- git
- hermes
- loom
- proxy
- server
- ultracontext
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# UltraContext + Loom：Context API 與 Agent 編織

**延續自**: [[2026-05-17-agentkit-multi-agent-typescript]], [[2026-05-17-everything-is-a-ralph-loop]]

**來源**:
- https://ultracontext.ai/ (21 pts HN) — Context API with auto-versioning
- https://github.com/ghuntley/loom (1,311 ⭐, Rust) — Huntley 的 AI coding agent

---

## Per-source Insight

### UltraContext：Git-like Context Primitives

UltraContext 不是又一個 agent framework——它是 **context infrastructure**。核心命題：不同 agent（Claude Code、Codex、Cursor）各有各的 session，彼此不知道對方在做什麼。UltraContext 做的是統一 context layer。

**API 設計**：五個 primitive，模仿 Git：
- `create()` — 建立 context（可從現有 fork）
- `append()` — 追加 message（不產生新版本）
- `update()` — 修改 message → 自動版本號 +1
- `delete()` — 刪除 message → 自動版本號 +1
- `get(id, { version: N })` — time-travel 到任一版本

版本模型細節：
- Append 不產生版本（可透過 index 做 time-travel）
- Update/delete 才 bump version
- Fork 是從現有 context 分支（像 git branch）
- Schema-free：message 是任意 JSON object

**架構**：daemon 捕獲 agent session → MCP server 分享 context → CLI 查詢

**Context Engineering Framework**（文件中定義的五種技術）：
1. **Compaction**（可逆）— 剝離可從外部狀態重建的資訊。例：file write → 保留 path，丟棄 content。零資訊損失。
2. **Summarization**（不可逆）— 結構化 schema prompt（非自由格式），保留最後幾步 tool call 完整細節。
3. **Offloading** — 把 context 搬出 window，存檔 → on-demand grep。
4. **Isolation** — 兩種 subagent 模式：by communicating（只給指令只收結果）vs by sharing context（看到完整歷史但不同 system prompt）
5. **Caching** — 穩定 prefix → KV cache reuse。動態 tool injection 會破壞 cache。固定 atomic tools，extensibility 走 sandbox/code execution。

### ghuntley/loom：The Weaving Loom 的實體

Huntley 的「weaving loom」不是比喻——是真的有 code。Rust 寫的 AI coding agent，30+ crates。

**值得注意的組件**：

| 組件 | 說明 |
|------|------|
| **Core Agent** | State machine for conversation flow + tool orchestration |
| **LLM Proxy** | Server-side proxy — API keys 永遠不離開 server，client 透過 `/proxy/{provider}` 呼叫 |
| **Weaver** | Remote execution via K8s pods — 這就是「sending down ladders」的實作：agent 把 work 派到遠端執行環境 |
| **Thread System** | Conversation persistence + FTS5 full-text search |
| **Analytics** | PostHog-style with identity resolution（agent 行為追蹤 + 使用者識別） |
| **Auth** | OAuth + magic links + ABAC |

**License**：Proprietary。"if your name is not Geoffrey Huntley then do not use" — 這是 Huntley 的個人研究專案，不是 open source 產品。

---

## Hermes 啟發

### UltraContext 的 pull model vs Hermes 的 push model

| | Hermes | UltraContext |
|---|---|---|
| Context 供應 | Push：briefing 預先建好，注入 system prompt | Pull：agent CLI 查詢 MCP server |
| 跨 agent 共享 | 共用 vault + git repo | 統一 context API + daemon |
| Versioning | Git history（檔案層級） | Message-level auto-versioning |
| Context 大小控制 | 手動 summarization | 五種技術框架 |

UltraContext 的 pull model 好處是 context window 永遠 lean——agent 只拿到它問的東西。代價是 agent 必須知道要問什麼（需要 metacognition）。Hermes 的 push model 保證 agent 有完整背景，但 briefing 越長越吃 window。

**可能的混合模式**：Hermes briefing 保持 push（確保 agent 不忘核心 context），但增加 MCP tool 讓 agent 可以 pull 額外 context on demand。這已經部分實現（obsidian-cli、session_search），但不像 UltraContext 有統一的 context API layer。

### Context Engineering Framework 直接適用

五種技術中，Hermes 目前用了：
- ✅ **Summarization** — memory-consolidator、briefing-updater
- ✅ **Offloading** — vault 存筆記，obsidian-cli 檢索
- ❌ **Compaction** — 未實作。Hermes 的 HEARTBEAT_MAP.md 寫「不要自動 summarization，讓 agent 自己決定」，但 compaction 和 summarization 不同——compaction 是可逆的、零資訊損失的。
- ✅ **Isolation** — delegate_task subagent（by communicating pattern）
- ⚠️ **Caching** — DeepSeek KV cache 有在用，但未結構化（`references/provider-caching-behavior.md` 有分析）

**Compaction 是低風險改進**：在寫入 briefing 前，對 tool call 結果做 compaction——保留路徑/查詢參數，丟棄可重建的輸出。不需要改 prompt，只需要一個 post-processing step。

### Loom 的 Weaver 模式

Weaver（遠端執行 via K8s pods）是 agent sandboxing 的 production-grade 實現。Hermes 的 worktree-subagent-isolation 是 filesystem-level，Weaver 是 pod-level——更強的隔離但更重的 infra。

對 Hermes 的啟發：如果未來需要在容器內跑不可信 code（如 user-submitted script），Loom 的 server-side proxy + Weaver 是 reference architecture。

### Loom 的 Server-side Proxy 架構

```
cli → /proxy/{provider} → server → actual LLM API
```

API key 只存在 server 端。Hermes 目前 API key 在 config.yaml，agent 直接呼叫 provider。如果未來要 run multiple agents with different trust levels，proxy 架構是標準解法（Docker AI Governance 也是這個模式）。

---

## 未追蹤

- UltraContext 的 `compaction` 指南細節（https://ultracontext.ai/docs/guides 的 "Store & Retrieve Contexts" 節）
- Loom 的 `specs/` 目錄（設計文檔清單，https://github.com/ghuntley/loom/tree/trunk/specs）

---

## ✅ 本次探索完成

