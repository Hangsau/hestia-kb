---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-MemoryBank---Rust-多-Agent-共享記憶系統
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-MemoryBank---Rust-多-Agent-共享記憶系統.md
title: 探索：MemoryBank — Rust 多 Agent 共享記憶系統
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- capture
- hooks
- https
- mcp
- memory
- memorybank
- namespace
- path
- recall
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：MemoryBank — Rust 多 Agent 共享記憶系統

**日期**: 2026-05-22 | **來源**: [[2026-05-20-agent-memory-taxonomy-survey]]

## 資料來源

### MemoryBank — https://github.com/feelingsonice/MemoryBank

**核心定位**：本地 Rust 服務，跨 agent 共享長期記憶。

**Architecture 要點**：

1. **Capture path** — agent hooks/plugins/extensions 捕捉對話事件
   - Codex/Gemini CLI: hooks
   - Claude Code: hooks
   - OpenCode: plugin
   - OpenClaw: extension
   - `memory-bank-hook` 二進位制正規化事件 → 送至本地服務

2. **Recall path** — 統一 HTTP MCP 介面
   - `retrieve_memory` MCP tool
   - OpenClaw 用 stdio proxy → HTTP MCP
   - 所有 agent 走同一介面，**recall 是 agent-agnostic 的**

3. **Memory lifecycle**：
   - 事件捕捉 → 正規化 → 組装 finalized turn → LLM 分析（產生 memory note + keywords + tags）→ 存 SQLite + embedding → 未來可通過 MCP 檢索

4. **Namespace 隔離**：每個 namespace 獨立 SQLite DB（`~/.memory_bank/namespaces/<ns>/memory.db`），支援多專案/團隊隔離

5. **雙 provider 分离**：Agent 使用的 model 和 Memory Bank 內部的 analysis model 是分開的（可用不同 provider）

**與前期筆記的對應**：

| 前期筆記提出的需求 | MemoryBank 的實作 |
|---|---|
| 跨 agent 共享記憶 | ✅ capture 從各 agent hooks，recall 統一 MCP |
| 結構化知識圖譜 | ✅ memory notes + keywords + tags + linked memories |
| 本地優先 | ✅ SQLite + local embedding cache |
| Continual consolidation | ✅ turn 組装後自動分析 + 圖譜演化 |
| Learned forgetting | ❌ 未明確提到（但 SQLite 可配合 external TTL） |

**對 Hermes 的啟發**：

1. **Hermes 的 MCP recall path 是對的方向** — MemoryBank 證明 MCP 作為統一的 recall interface 可跨多 agent 工作
2. **Capture path 是真正的難題** — 每個 agent 需要各自的 hook/integration，這解釋了為何 Hermes 的 `sessions/` 目錄 capture 方案難以推廣
3. **Namespace 設計值得參考** — Herms 如果要做到 multi-agent 記憶隔離，namespace 概念很實用
4. **雙 provider 分离** — Memory Bank 用不同 model 做 analysis vs agent reasoning，這對 deep research agent 有價值（analysis model 可以用小模型）

**為何感興趣**：
- 前期筆記（Day 1-2）問「跨 agent 共享記憶的實際系統長什麼樣」— MemoryBank 是目前看到最完整的开源實作
- Rust + SQLite + MCP 是可行的 production stack
- 它的 namespace 設計解決「不同 task 用不同 memory context」的問題

## 跨文章 Synthesis

結合前期筆記：

- **Day 1**（Mnemora, Aegis, DPM）：append-only log、policy-learned、selective memory
- **Day 2**（arXiv survey）：write-manage-read loop、五大家族、continual consolidation
- **Day 3**（MemoryBank）：具體的多 agent 共享記憶實作架構 — capture/recall 分離、namespace 隔離

**核心收斂**：
前期筆記的「跨 agent 共享」問題，MemoryBank 證明可行，關鍵是：
1. Capture path 要適配每個 agent 的 hooks（客製化）
2. Recall path 必須統一（標準化）
3. 圖譜/標籤/namespace 是長期組織的關鍵

**與 Hermes 的差距**：
- Hermes 目前只有 session-level capture（sessions/），沒有跨 agent 的 capture 基礎設施
- Recall 只有 FTS5，沒有 semantic memory note 的生成
- 如果要實作 multi-agent memory，MemoryBank 的架構是最接近的參考

## 未追蹤 Leads

- https://github.com/feelingsonice/MemoryBank (本篇已讀)
- https://github.com/quantifylabs/aegis-memory (前期筆記 lead，尚未讀)
- https://arxiv.org/abs/2605.13486 (R²-Mem)
- https://github.com/mnemora-db/mnemora

## ✅ 本次探索完成
