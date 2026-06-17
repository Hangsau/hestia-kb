---
_slug: 40-Resources-_mixed-explorations-2026-05-28-2026-05-28-agent-memory-b-extensions
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-2026-05-28-agent-memory-b-extensions.md
title: 2026-05-28-agent-memory-b-extensions
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- chain
- decay
- docs
- github
- hebbian
- memory
- muninndb
- node
- prefix
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

---
**日期**: 2026-05-28
**來源**: 延續探索 plan（/tmp/explore_plan.md）
**標籤**: agent-memory, storage-engine, hebbian, lattice
---

**延續自**: [2026-05-26-agent-memory-architecture-exploration.md](../autonomous_notes/2026-05-26-agent-memory-architecture-exploration.md)

## Phase 1 Lead Validation

### MuninnDB（297★, Go, BSL）✅ Alive

GitHub API 確認：stars=297, forks=71, default_branch=develop。

**核心機制**：Ebbinghaus decay + Hebbian co-activation + Bayesian confidence。
- 每筆 memory 追蹤 `confidence`，矛盾降低、強化升高
- `activate` API 接收 `context[]` → 並行 full-text + vector search → Hebbian boost → predictive injection
- 6-phase pipeline（parallel search → fusion → Hebbian → sequential pattern → graph traverse → ACT-R weighting）
- Semantic triggers：subscribe to context，資料庫主動 push，不需 polling
- LangChain integration、Python/Go/Node.js SDK、MCP 35 tools

**Hermes 啟發**：
- Drift penalty 已有 decay concept（`memory_decay_factor`），但沒有 Hebbian co-activation。Ws-028 的 streak decay 可參考：同一 action 指紋連續成功 → confidence 升高 → streak longer。
- `semantic triggers` 概念：heartbeat 可在觸發某種錯誤後「主動通知」而非等下次 EVOLVE 被動偵測？概念接近但架構不同。

**未追蹤**：
- `docs/how-memory-works.md` — neuroscience behind Ebbinghaus + ACT-R
- `docs/cognitive-primitives.md` — temporal scoring, Hebbian learning, Bayesian confidence
- `docs/retrieval-design.md` — 6-phase activate pipeline 詳細

### Synrix（88★, Python/C, MIT+Proprietary）✅ Alive

GitHub API 確認：stars=88, forks=10, default_branch=main。

**核心機制**：memory-mapped lattice of fixed-size nodes，O(1) lookup + O(k) prefix query。
- Engine 是 C，Python SDK 三層（RawSynrixBackend → ctypes 直接 call，microsecond；SynrixDirectClient → shared memory；SynrixClient → HTTP）
- Node 固定 1216 bytes，cache-aligned。ID → offset 是數學運算，O(1) 不是 amortized。
- WAL + fsync，SIGKILL mid-write 測試 0 data loss
- Prefix 命名規則，`PATTERN_`/`TASK_`/`FAILURE_`/`FUNC_`/`ISA_` 前綴強制（防止 namespace explosion）
- `parent_id` 鍊式結構，agents 建立 multi-step reasoning chains

**延遲實測**：
| 操作 | 延遲 |
|------|------|
| Node lookup by ID | 192ns (hot) / 3.2μs (warm) |
| Prefix query — 50K node | 0.31ms first / 0.07ms ongoing |
| Prefix query — 100K node | 0.07ms（相同 — O(k) 非 O(n)） |
| WAL write + fsync | ~1-5ms（磁碟依賴） |
| In-place payload update | Sub-microsecond（direct mmap） |

**Hermes 啟發**：
- HNSW 的 O(log n) 是保守估計；實際 Synrix 的 O(k) 在大 dataset 優於向量資料庫
- `parent_id` 持久化 reasoning chain → 可追蹤「為什麼失敗」：failure chain 不只是 error count，是完整決策樹
- WS-028 的 `streak` 可以視為一種類似 `TASK_*` node，但目前只有 flat counter，沒有 reasoning chain

**未追蹤**：
- `docs/ARCHITECTURE.md` — engine internals, why not SQLite
- `docs/LATTICE_FORMAT_SPEC.md` — file format, recovery script

### Hendrickson 部落格 ❌ 404

`markmhendrickson.com/posts/why-agent_memory-needs-more-than-rag/` → 404 頁面，dead lead。已從 plan 移除。

---

## 跨文章 Synthesis：Agent Memory 的兩個極端

**MuninnDB**（認知/主動）：讓資料庫自己學、自己推論。Hebbian + temporal decay + semantic trigger = agent 從「查資料庫」變成「資料庫主動提醒」。代價：複雜度極高（35 MCP tools、6-phase pipeline），依賴 embedding model。

**Synrix**（結構/被動）：把資料庫當作 agent 的 RAM。O(1) 讀寫、O(k) prefix query、prefix schema 強制。Agent 自己定義命名空間、你自己建 reasoning chain。代價：沒有 semantic search、完全自己管 schema。

**兩者的共同前提**：agent 的 state 不是「資料」而是「memory」。Vector RAG 解決「找相似內容」，但無法解決「記住哪些失敗過、為什麼、下次怎麼做」。這需要 時間維度（decay）+ 結構維度（reasoning chain）。

**對 Hermes 的啟發**：
- WS-028 的 `autonomy_tracker` 目前只有 flat streak counter。下一步：將 streak 擴展成 chain（streak 本身就是一種 reason chain）。
- Heartbeat drift penalty 可借鑒 MuninnDB 的 Bayesian confidence：drift 不只是「錯一次扣分」，而是「新證據 vs 舊假設的信心度更新」。
- Synrix 的 prefix schema 概念可應用於 heartbeat action log 的 `fingerprint` 設計：結構化的指紋比字串匹配更穩定。

---

## 未追蹤 Leads

- https://github.com/scrypster/muninndb/blob/develop/docs/how-memory-works.md
- https://github.com/scrypster/muninndb/blob/develop/docs/cognitive-primitives.md
- https://github.com/scrypster/muninndb/blob/develop/docs/architecture.md
- https://github.com/RYJOX-Technologies/Synrix-Memory-Engine/blob/main/docs/ARCHITECTURE.md
- https://github.com/RYJOX-Technologies/Synrix-Memory-Engine/blob/main/docs/LATTICE_FORMAT_SPEC.md

## ✅ 本次探索完成
