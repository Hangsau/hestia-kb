---
_slug: 40-Resources-_mixed-explorations-2026-05-30-mem0-v3-architecture-synthesis
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-mem0-v3-architecture-synthesis.md
title: 2026-05-30-mem0-v3-architecture-synthesis
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- add
- enforcement
- entity
- extraction
- keyword
- mem
- memory
- ring
- semantic
- signal
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

**日期**: 2026-05-30
**延續自**: [[2026-05-30-探索-Mem0-v3---ADD-only-Memory---Multi-Signal-Retrieval]]

## Mem0 v3 架構核心解析

### 1. ADD-only 提取（Single-pass）

舊版：雙 LLM call（extract → decide ADD/UPDATE/DELETE）
新版：單 LLM call，只做 ADD

→ 記憶不覆蓋，新事实加在旁边，舊記憶保留
→ 衝突由檢索層處理（most relevant/current first），而非寫入層
→ LLM 容量全用於理解輸入，不再做狀態比對

### 2. Multi-signal 混合檢索

三訊號並行：
- **Semantic search**（向量相似度）
- **BM25 keyword**（正規化 term matching）
- **Entity matching**（實體圖譜 boost）

分數融合 → Top-K

BM25 是 boost signal，不是 recall expander。只有 semantic 結果才是候選，BM25/entity 只影響排名，不新增候選。

### 3. Entity linking 取代 Graph memory

Graph store removed (~4000 lines removed from SDK)
→ Entity extraction 自動運行，存進 `{collection}_entities`
→ Query 時 entity match → boost relevant memories
→ 無需外部 graph DB dependency

### 4. 效能數據

| Benchmark | v2 | v3 | 提升 |
|-----------|-----|-----|------|
| LoCoMo | 71.4 | 91.6 | +20pts |
| LongMemEval | 67.8 | 93.4 | +26pts |
| Extraction latency | 2x | 1x | -50% |

### 5. Graceful Degradation 設計

| 缺失 dependency | Impact | 檢索可用？ |
|-----------------|--------|----------|
| spaCy | 無 entity extraction，無 BM25 lemmatization | ✅ semantic-only |
| fastembed (Qdrant) | 無 BM25 keyword search | ✅ semantic + entity |
| Entity store unavailable | 無 entity boosting | ✅ semantic + BM25 |

**底層 guarantee**：永遠有 semantic search。上層功能按需分層。

## Hermes 啟發

### WS-035 ring enforcement → ADD-only + temporal ranking

Mem0 v3 的核心 insight：**寫入层不解决冲突，解决冲突的是检索层**。

現有 WS-035 `execution_ring` 只有 1 match（在 pairing store context），無 ring check enforcement。根本原因：Schema 存在（execution_ring field 存在）但 enforcement layer 缺失。

修復路徑：
1. Memory 寫入時加 timestamp + temporal context
2. Query 時動態評估（而非 static enforcement）
3. 對應 WS-035 的 `ring enforcement with temporal decay`

### Hermes 記憶系統升級方向

**短期（已實作）**：FTS5 BM25 鞏固
**中期**：Entity extraction + temporal metadata
**長期**：輕量向量融合（semantic + keyword）

Mem0 v3 的 multi-signal architecture 證明了：
- BM25 keyword 是必要信號（非可選）
- Entity matching 是 +20pts 的關鍵
- ADD-only 簡化了寫入邏輯，衝突自然被檢索層處理

### Consolidation 加速

`consolidate_memory.py` 的核心功能（cross-cutting insight 生成）在 ADD-only 模式下更容易：
- 記憶不覆蓋，跨 session 累積的 theme 更完整
- 新舊共存 → 可以觀察一段時間內的主題演變
- 不需要「compaction decision」（UPDATE/DELETE），只需要「ranking decision」（哪些在前）

## ✅ 本次探索完成

