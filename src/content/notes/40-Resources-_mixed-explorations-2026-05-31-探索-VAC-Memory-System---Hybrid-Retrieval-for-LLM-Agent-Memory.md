---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索-VAC-Memory-System---Hybrid-Retrieval-for-LLM-Agent-Memory
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索-VAC-Memory-System---Hybrid-Retrieval-for-LLM-Agent-Memory.md
title: 探索：VAC Memory System — Hybrid Retrieval for LLM Agent Memory
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- coverage
- github
- llm
- locomo
- mca
- memory
- stage
- system
- union
- vac
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# 探索：VAC Memory System — Hybrid Retrieval for LLM Agent Memory

**日期**: 2026-05-31
**延續自**: [[2026-05-28-探索-LLM-Agent-Memory-Architectures-2026]]（MEMO 論文 + 其他架構）

---

## Source: VAC Memory System (GitHub)

GitHub: `vac-architector/VAC-Memory-System` — 80.1% on LoCoMo benchmark (open-weights, no external DB)

### 核心架構：6-stage pipeline

```
Query → Preprocess → MCA Gate → [FAISS + BM25] → Union → Cross-encoder rerank → GPT-4o-mini
```

**Stage 1 — Dense retrieval**: BGE-large-en-v1.5 (1024d) + FAISS IndexFlatIP

**Stage 2 — Sparse retrieval**: BM25 via classic inverted index（補足低 embedding-recall + keyword-heavy 查詢）

**Stage 3 — MCA (Multi-Component Aggregation) gate**: 第一層過濾
- Gravitational-style score combining: keyword coverage + token importance + local frequency signal
- Threshold: coverage ≥ 0.1 → keep top-30
- 目的：stabilize early recall、catch exact-match questions

**Stage 4 — Union strategy**: 不在 reranking 前 aggressive reduction，直接把 112-135 docs 送進 reranker
- 實踐證明這樣更穩定，避免丢失 rare but crucial documents

**Stage 5 — Cross-Encoder reranking**: bge-reranker-v2-m3，處理完整 union set

**Stage 6 — Answer generation**: GPT-4o-mini only，用於最終 synthesis

### Why it worked（三個關鍵）

1. **MCA-first filter** stabilizes early recall
2. **Not discarding union before re-ranking** — 保留更多 candidate
3. **Proper dense embedding instruction** — `Represent this sentence for searching relevant passages` 大幅影響 BGE performance

### 效能數據

- Speed: <3 seconds per query on single RTX 4090
- Cost: <$0.10 per million tokens
- Recall: 94-100% ground truth coverage
- Reproducible: temperature 0, deterministic

### LoCoMo Leaderboard (GPT-4o-mini judge)

| Rank | System | Accuracy |
|------|--------|----------|
| 🥇 | MemMachine | 84.87% |
| 🥈 | **VAC** | **80.1%** |
| 🥉 | Letta (MemGPT) | 74.0% |
| 4 | Mem0 (Graph) | 68.5% |
| 5 | Memobase | 75.78% |
| 6 | Zep | 75.14% |

---

## Hermes 啟發

### 1. MCA-style first-pass filter

VAC 的 MCA 是 keyword/coverage-based filter，適用於 Hermes 的 `heartbeat_learning.py` staleness 分類——可以把 `_compute_staleness()` 想像成一種「topic coverage gate」，決定哪些 facts 要 promote/skip。

### 2. Union-before-rerank pattern

Hermes 的 `memory_prefix_index.py` 目前是純 prefix match，沒有 cross-encoder reranking 層。可以考慮：
- 先 broad fetch（prefix + fuzzy），收集候選集
- 送進 lightweight cross-encoder rerank（而非直接吃第一輪結果）
- 這與 WS-038 的 access recency staleness 機制互補

### 3. LoCoMo as evaluation benchmark

LoCoMo (5,880 multi-hop, temporal, negation-rich QA pairs) 是比 Hermes 目前任何 internal evaluation 都更嚴格的標準。建議日後用 LoCoMo 驗證 `heartbeat_learning.py` 的蒸餾決策 quality。

---

## 未追蹤 Leads

- `github.com/scrypster/muninndb` — ACT-R decay + Hebbian learning, Go binary, no LLM in hot path
- `github.com/quantifylabs/aegis-memory` — rule-based filter → LLM extraction pipeline, 70% cost saving
- mnemora.dev — 4 memory types, no LLM in CRUD path, sub-10ms DynamoDB reads

