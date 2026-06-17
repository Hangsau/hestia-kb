---
_slug: 40-Resources-_mixed-research-2026-06-02-mem0-state-of-agent-memory-2026
_vault_path: 40-Resources/_mixed/research/2026-06-02-mem0-state-of-agent-memory-2026.md
title: Graphiti Bi-Temporal Edge — Source Code Analysis
date: 2026-06-01
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- bi-temporal
- edges
- graph
- graphiti
- memory
- neo4j
- temporal
- zep
created: '2026-06-01'
updated: '2026-06-15'
status: budding
---

# Graphiti Bi-Temporal Edge — Source Code Analysis

**日期**: 2026-06-01 | **來源**: https://github.com/getzep/graphiti | **類型**: exploration

## 探索背景

從 Synix 探索筆記（2026-06-01）的「未追蹤 leads」出發：
> Graphiti bi-temporal 4-field edge 原始碼（Neo4j + Cypher path queries 的具體實作）

已讀：Synix 的 8-system overview（2026-06-01）、AgeMem + Graphiti（2026-05-30）。

## Source Code Findings

### EntityEdge — 4-field Bi-Temporal Model（確認）

Graphiti 的 `EntityEdge`（`graphiti_core/edges.py`）有 4 個時間欄位：

```python
class EntityEdge(Edge):
    valid_at: datetime | None    # when the fact became true
    invalid_at: datetime | None  # when the fact stopped being true
    reference_time: datetime | None  # reference timestamp from the episode that produced this edge
    expired_at: datetime | None   # when the node was invalidated
```

額外從 parent `Edge` class 繼承：
- `created_at: datetime`
- `uuid: str`
- `group_id: str`（graph partition）

### 與 Synix 描述的對照

| Synix 描述 | Source 確認 |
|---|---|
| "4 temporal fields per edge" | `valid_at`, `invalid_at`, `reference_time`, `expired_at` — 4 fields confirmed |
| "bi-temporal model (system + valid time)" | `invalid_at` = valid time end；`created_at` = system time；bi-temporal confirmed |
| "Neo4j + Cypher path queries" | `driver/neo4j/` directory 完整實作，Cypher queries in `graph_operations.py` |

### Driver 多層次架構

Graphiti 支援 4 種 graph backends（同一套 interface，不同實作）：
- **Neo4j** — 原生 Cypher
- **FalkorDB** — 類似 Cypher
- **Kuzu** — 屬性 graph（用 `RelatesToNode_` 中間節點繞過原生 edge properties）
- **Neptune** — AWS Neptune

所有 driver 都有相同的 operations 目錄結構：
```
driver/<provider>/operations/
  entity_edge_ops.py     # EntityEdge CRUD
  entity_node_ops.py     # Entity node CRUD
  episode_node_ops.py    # Episode provenance
  episodic_edge_ops.py   # Episode→Entity edge
  community_edge_ops.py  # Community grouping
  search_ops.py          # Hybrid search
```

### Retrieval Architecture

`EntityEdge.fact_embedding` — 每個 edge 有自己的 vector embedding，來自 `fact` 欄位文字。這讓 Graphiti 可以做 edge-level 的 semantic search，不只是 node-level。

搜尋時用 hybrid（semantic + keyword + graph traversal）。Cross-encoder reranking 支援多 provider（BGE、OpenAI、Cohere、Gemini）。

### Episode Provenance

每個 `EntityEdge` 有 `episodes: list[str]` — 追蹤哪些 episode 產生這個 edge。這是 Graphiti 的「everything traces back to episodes」設計。

## Hermes 啟發

**bi-temporal model 直接回答 WS-035 的架構缺口**：
- Memento paper 提出 write-gate + `confidence_valid_until`；Graphiti source 顯示 4-field bi-temporal 是 production-ready 的實作方式
- `invalid_at`（valid time end）= staleness detection 的精確時間戳
- `reference_time` 從 source episode 攜帶時間上下文，可用於 drift detection
- 多 backend 支援（Neo4j/FalkorDB/Kuzu）表示這個架構已標準化，不是實驗性

**Wikilink 即將實現的路徑**：
- Graphiti 的 Episode provenance（每個 fact 追蹤 source episode）= wikilink 的「出處追蹤」原型
- 我們的 vault notes 已有 wikilink（explicit edges），缺的只是 query layer
- Graphiti driver architecture 是 future KB query layer 的參照

## 未追蹤 leads（仍有效）

- **Hindsight causal link boosting + spreading activation retrieval** — GitHub search 無對應 repo，closed source or renamed
- **Letta memory_rethink** — 文章有描述但無實作細節，需直接看 Letta source
- **Tacnode** — closed source，founder 有公開 "Decision Coherence" position paper

## ✅ 本次探索完成