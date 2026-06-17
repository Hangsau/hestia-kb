---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索-Mem0-v3-新演算法---2026-04-benchmark-突破
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索-Mem0-v3-新演算法---2026-04-benchmark-突破.md
title: 探索：Mem0 v3 新演算法 — 2026-04 benchmark 突破
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- add
- agent
- benchmark
- entity
- https
- list
- mem
- memory
- paper
- 新演算法
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# 探索：Mem0 v3 新演算法 — 2026-04 benchmark 突破

**日期**: 2026-05-31 | **來源**: [[2026-05-30-探索-Agent-Memory-Paper-List---mem0-Memory-Benchmarks]] | **類型**: SPIKE

**延續自**: [[2026-05-30-探索-Agent-Memory-Paper-List---mem0-Memory-Benchmarks]]

## Per-Source Insights

### mem0ai/mem0 — v3 新演算法（2026-04）

Source: `https://raw.githubusercontent.com/mem0ai/mem0/main/README.md`

**核心突破：Single-pass ADD-only extraction**

Mem0 v3 的核心設計轉變：
- **ADD-only**：記憶只追加，永不覆寫。新資訊覆蓋舊資訊時，會標記 conflict 但保留歷史
- **Agent-generated facts first-class**：當 agent 確認某個 action，該資訊現在和 user-provided facts 同等權重
- **Entity linking**：跨記憶的 entity 追蹤，增強檢索
- **Multi-signal retrieval**：semantic + BM25 keyword + entity matching 平行評分、RRF fusion
- **Temporal reasoning**：時間感知排序（「上個月的老鼠問題」優先於「昨天的」）

**Benchmark 對比**：

| Benchmark | Old v2 | New v3 | 改善幅度 |
|-----------|--------|--------|---------|
| LoCoMo | 71.4 | **91.6** | +20.2 pts |
| LongMemEval | 67.8 | **94.8** | +27.0 pts |
| BEAM (1M) | — | **64.1** | — |
| BEAM (10M) | — | **48.6** | — |

Token efficiency：~7K tokens/query（4.97% context footprint），latency p50 < 1.1s。

**對 Hermes 的直接相關性**：
- `contradiction_resolution` 在 1M 為 0.357、10M 為 0.325——仍是最低分的維度，但新演算法已有顯著改善
- ADD-only 的 conflict tracking 機制可直接對映 WS-035 的 drift penalty 設計

### 未追蹤 Leads

- https://docs.mem0.ai/migration/oss-v2-to-v3 — 從 v2 升級的路徑，看架構差異
- https://github.com/mem0ai/mem0/tree/main/mem0 — 原始碼，看 EntityExtractor 的 prompt engineering

## ✅ 本次探索完成
