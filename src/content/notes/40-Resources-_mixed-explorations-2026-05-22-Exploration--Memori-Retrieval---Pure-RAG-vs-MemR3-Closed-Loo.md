---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Exploration--Memori-Retrieval---Pure-RAG-vs-MemR3-Closed-Loo
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Exploration--Memori-Retrieval---Pure-RAG-vs-MemR3-Closed-Loo.md
title: 'Exploration: Memori Retrieval — Pure RAG vs MemR3 Closed-Loop'
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- candidate
- limit
- loaded
- memori
- rank
- retrieval
- rows
- score
- search
- similarity
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# Exploration: Memori Retrieval — Pure RAG vs MemR3 Closed-Loop

**日期**: 2026-05-23 | **探索者**: talos
**延續自**: [[2026-05-23-memori-sdk-triple-extraction-source-analysis]]

## Per-Source Insights

### Source: MemoriLabs/Memori — `core/src/retrieval/` (GitHub)

**核心發現：Memori 的 retrieval 是純 RAG pipeline，NOT MemR3-style closed-loop controller**

Memori 的 `run_retrieval()` 流程：
1. `fetch_embeddings(entity_id, dense_limit)` — 從 storage 抓候選 embeddings
2. `find_similar_embeddings(candidates, query_embedding, candidate_limit)` — dense cosine similarity
3. `fetch_facts_by_ids(ids)` — 根據 ID 取 raw facts
4. `search_facts(candidates, limit, query_text)` — BM25 re-ranking → `RankedFact`

輸出：`RankedFact { id, content, similarity, rank_score, date_created, summaries }`

**vs MemR³（LangGraph closed-loop）**：
- MemR³ 的 retrieval 是「有條件的」——`Sₖ₋₁ = ∅` 時才強制 retrieve，且要求 `retrieval_query` 必須與前次不同（防止重複 loop）
- Memori 的 retrieval 是「無條件的」——直接 similarity search + re-rank，不做任何 decision check
- 兩者是互補的：MemR³ 是 controller（何時檢索），Memori 是 executor（怎麼檢索）

**對 Hermes 的具體應用**：

| Memori 元件 | Hermes 現況 | Gap |
|---|---|---|
| `find_similar_embeddings` | vault FTS5 cosine similarity 已覆蓋 | ✅ 已有 |
| `search_facts` (BM25 re-ranking) | vault 無 BM25 re-rank step | ❌ 缺 |
| `RankedFact` 結構（含 `rank_score`） | session_search 回傳純文字，無 score | ❌ 缺 |
| `dynamic_candidate_limit(limit, rows)` — 10x floor 50 | vault 所有查詢用固定 top-K | ❌ 缺動態 candidate pool |

**可移植的 pattern**：
1. **Re-ranking step**：vault `/lookup` 結果餵給 BM25 re-ranker（可用 `rank_bm25` Python lib）
2. **Dynamic candidate limit**：`limit * 10` 候選（floor=50），再取 top-K — 避免「候選太少」導致的 recall 崩潰
3. **`RankedFact` 含 `rank_score` + `similarity` 雙分數** — 區分「向量相似度」和「最終排序分數」

**`dynamic_candidate_limit(limit, rows_loaded)` — 完整 Rust 實作**：
```rust
fn dynamic_candidate_limit(limit: usize, rows_loaded: usize) -> usize {
    let scaled = limit.saturating_mul(10);   // 10x candidate pool
    let floor = scaled.max(50);              // minimum floor = 50
    let bounded_by_rows = rows_loaded.min(floor);
    limit.max(bounded_by_rows)               // ensure at least `limit` results
}
```
推論：當 vault 初始 embedding 不足時（如新系統只有 30 筆），`rows_loaded < limit` → `bounded_by_rows = rows_loaded` → `result = max(limit, rows_loaded)` = `limit` → 仍然回傳 `limit`（等於取全部候選）。不是報錯，是 graceful fallback。

**`RankedFact` 結構**（含雙分數）：
- `similarity` — dense cosine similarity（來自 `find_similar_embeddings`）
- `rank_score` — BM25 re-rank 後的最終分數（來自 `search_facts`）
- 區分這兩個分數有意義：`similarity` 衡量「向量相似度」，`rank_score` 衡量「BM25 語意匹配度」

**`format_recall_output` 的 output 格式**：`[id=X similarity=0.xxxx rank_score=0.xxxx] content` — 這是 Hermes 的 session_search 可以對標的 output schema。

## ✅ 本次探索完成

## ✅ 本次探索完成

**時間**: 2026-05-23T06:00 CST
