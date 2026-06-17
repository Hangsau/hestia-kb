---
_slug: 40-Resources-_mixed-explorations-2026-05-27-探索-Agent-記憶架構---MuninnDB---Synrix
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-探索-Agent-記憶架構---MuninnDB---Synrix.md
title: 探索：Agent 記憶架構 — MuninnDB × Synrix
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- decay
- distillate
- engine
- hebbian
- https
- learning
- memory
- muninndb
- prefix
- synrix
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 探索：Agent 記憶架構 — MuninnDB × Synrix

**日期**: 2026-05-27 | **來源**: HN Algolia (agent memory RAG, ≥10pts fallback to all results) | **類型**: 探索
**延續自**: [[2026-05-26-agent-memory-architecture-2026-05-26]]（memU、JARVIS-1、YantrikDB、Engram）

## Per-Source Insight

### 1. MuninnDB — Ebbinghaus Decay + Hebbian Learning Engine (297⭐, Go)

**URL**: https://github.com/scrypster/muninndb

**核心發現**：不是 vector store，不是 graph DB，不是 RAG wrapper——是「cognitive database」。Engine-native primitives：

- **Ebbinghaus decay**：記憶用進廢退，時間加權自動計算
- **Hebbian learning**：共同激活的記憶自動形成關聯，edges 隨 co-activation 加強
- **Bayesian confidence**：每個 engram 追蹤信心分數；矛盾降低，強化提升
- **6-phase ACTIVATE pipeline**（<20ms）：parallel full-text + vector search → fusion → Hebbian co-activation boosts → predictive candidates from sequential patterns → association graph traversal → ACT-R temporal weighting
- **Predictive activation**：追蹤 sequential patterns，Recall@10 +21%（workflow-oriented）
- **Semantic triggers**：subscribe to context，DB push when relevance changes（非 polling）

**MCP-native**：35 tools，auto-detect Claude Desktop/Copilot/Cursor/Windsurf/VSCode/OpenCode。`muninn init` 自動設定。

**架構數字**：
- Ports: 8474 MBP / 8475 REST / 8476 Web UI / 8477 gRPC / 8750 MCP
- LangChain integration：實質對話鏈每次 turn 都 store，每次 response 都 draw on relevant past
- BSL 1.1，2030-02-26 自動變 Apache 2.0

**對 Hermes 的啟發**：
- `heartbeat_learning.py` 目前沒有 explicit drift penalty（無 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`），MuninnDB 的 Bayesian confidence 可直接映射——當 distillate 與前期結論相悖時，confidence 應下降而非直接覆寫
- Ebbinghaus decay 可補足 YantrikDB 的「時間衰減」——Hermes 記憶目前沒有 decay 機制，只有 accumulation

### 2. Synrix — O(k) Prefix Queries, No Vectors, No Embeddings (88⭐, Python/C)

**URL**: https://github.com/RYJOX-Technologies/Synrix-Memory-Engine

**核心發現**：flat memory-mapped array of fixed-size nodes (1216 bytes, cache-aligned)。不是 general-purpose DB，是「purpose-built state infrastructure for agents that need to read/write structured state at frequencies no human will ever reach」。

- **O(1) lookup by ID**：ID × node size → arithmetic offset → mmap seek → read
- **O(k) prefix queries**：k = matching results，不依賴 dataset size。100K nodes 時 0.07ms
- **No embeddings**：Agents know what they're looking for；semantic search 是 human convenience
- **Enforced prefix namespace**：`TASK:stripe:attempt`、`PATTERN:retry` — 非 convention，engine 強制。杜絕 prefix explosion，保證 O(k)
- **WAL + fsync**：SIGKILL mid-write 零資料損失（500 nodes stress test 驗證）
- **Crash safety**：checkpoint every N writes，CRC detect corrupt，WAL replay

**Node types**：
```
PATTERN_  — learned behaviour with confidence + decay_rate
TASK_     — attempt records with outcome + parent reasoning chain
FAILURE_  — error type + retry count
FUNC_     — call signatures + success rates
ISA_      — ontological relationships
```

**parent_id on disk**：agents build reasoning chains，hierarchy persists across restarts。`get_children / get_subtree / get_ancestors` 三種遍歷。

**Latency**（real hardware, not synthetic）：
- Node lookup by ID: 192ns (hot cache) / 3.2μs (warm)
- Prefix query 100K nodes: 0.07ms（跟 10K 一樣快——O(k) 不是 O(n)）
- WAL write + fsync: ~1-5ms（磁碟依賴）
- In-place payload update: sub-microsecond（direct mmap write）

**對 Hermes 的啟發**：
- Synrix 的「namespace prefix 強制」vs MuninnDB 的「Hebbian auto-association」是兩種互補的結構化策略
- Synrix 的 reasoning chain（parent_id on disk）直接對應 `heartbeat_learning.py` 的 distillate lineage——每次 distill 是 child of prior distillation
- O(k) 的保證（跟 dataset size 無關）對 heartbeat 的 memory 操作有意義——distillate 讀取不應隨 vault 增長變慢

### 3. Mark Hendrickson post (404 — unreachable)

URL: https://markmhendrickson.com/posts/why-agent_memory-needs-more-than-rag/
Status: 404，頁面不存在。推測已被移除或改 URL。

## 跨文章 Synthesis

**主題收斂：結構化記憶 > 純嵌入檢索**

三個來源（加上前期的 memU、JARVIS-1、YantrikDB、Engram）全部收斂到同一個設計原則：

| 系統 | 結構化策略 | 關鍵數字 |
|------|-----------|---------|
| MuninnDB | Hebbian co-activation + temporal weighting | Recall@10 +21% |
| Synrix | Enforced prefix namespace + parent_id chain | O(k) lookup, 0.07ms/100K |
| YantrikDB | 5-layer index (HNSW+graph+temporal+decay+KV) | 矛盾偵測 |
| Engram | Transactional Forgetting + Memory Bus | 六原則 |

**對 heartbeat_learning.py drift penalty 的具體建議**：
1. 每次 distillate 寫入時，計算與前期所有 distillate 的 semantic overlap（可用 MuninnDB-style Hebbian edge weight 或 Synrix-style prefix 衝突偵測）
2. 若 overlap 高但結論相悖 → 降低 confidence，標記 drift 而非直接覆寫
3. 加入 Ebbinghaus-style decay：長時間未引用的 distillate 自動衰減 weight

## 未追蹤 Leads

- https://github.com/scrypster/muninndb (⭐297, Go) — 深入讀 recall.go / dream.go 的 ACT-R implementation
- https://github.com/RYJOX-Technologies/Synrix-Memory-Engine (⭐88) — python-sdk latency benchmark 實測

## ✅ 本次探索完成
