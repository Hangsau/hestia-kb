---
_slug: 40-Resources-_mixed-explorations-2026-05-30-探索-Mem0-v3---ADD-only-Memory---Multi-Signal-Retrieval
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-探索-Mem0-v3---ADD-only-Memory---Multi-Signal-Retrieval.md
title: 探索：Mem0 v3 — ADD-only Memory + Multi-Signal Retrieval
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- add
- entity
- fts
- hermes
- mem
- memory
- multi
- retrieval
- signal
- temporal
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

---
title: "探索：Mem0 v3 — ADD-only Memory + Multi-Signal Retrieval"
date: 2026-05-30
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [mem0, v3, add-only, multi-signal, bm25, entity-linking, temporal-reasoning]
---

# 探索：Mem0 v3 — ADD-only Memory + Multi-Signal Retrieval

**延續自**: [[2026-05-30-探索-Agent-Memory-Paper-List---mem0-Memory-Benchmarks.md]]

## 核心發現：Mem0 v3 (April 2026) Major Algorithm Update

### 數據對比

| Benchmark | Old (May 2026) | New (April 2026) | Delta |
|-----------|---------------|-----------------|-------|
| LoCoMo | 71.4 | **91.6** | +20.2 |
| LongMemEval | 67.8 | **94.8** | +27.0 |
| BEAM (1M) | 70.1 | **64.1** | -6.0 |
| BEAM (10M) | 50.5 | **48.6** | -1.9 |
| Tokens/context | ~7K | ~7K | — |

### 關鍵設計：ADD-only + Multi-Signal Retrieval

**ADD-only extraction（核心突破）**：
- Single-pass, one LLM call — no UPDATE/DELETE
- Memories accumulate; nothing is overwritten
- Agent-generated facts are stored with equal weight

這是完全不同的記憶管理哲學。傳統方法嘗試「衝突解決」（新記憶 vs 舊記憶 → 決定保留哪個），但這在實務上很難做對（需要完美判斷哪個 fact 更「正確」）。

Mem0 的解法：**不解決衝突，讓兩者都存在，用 temporal reasoning 決定哪個適用於當下 query**。

**Multi-signal retrieval**：
- Semantic（向量）
- BM25 keyword（精準匹配）
- Entity matching（跨記憶的 entity 連結）
- Fused in parallel, scored together

這完全吻合 FTS5 proposal 的方向（BM25 keyword search），但擴展成三路融合。FTS5 只能做 BM25一路，沒有 semantic/Entity維度。

**Temporal Reasoning**：
- Time-aware retrieval — ranks the right dated instance for queries about current state, past events, upcoming plans

這是 Hermes 目前最欠缺的維度。heartbeat_learning.py 的 staleness window 是「新於某 threshold 就 stale」，但沒有「time-aware retrieval」——根據 query 的時間上下文動態 ranking。

### 對 Hermes 的直接啟發

#### 1. FTS5 提案方向確認

Mem0 v3 確認 BM25 keyword search 是必要維度（不只靠 semantic）。FTS5 BM25 路線正確，但需要考慮：
- 純 BM25 → 可以升級成 BM25 + entity linking
- 實作路徑：`fts5_search.py` 加 entity extraction（用簡單的 NLP 或 just regex NER）

#### 2. WS-035 Bounded Dereferencing — ADD-only vs Conflict Resolution

Mem0 的 ADD-only 哲學 vs 傳統 conflict resolution：
- **Conflict resolution**: 遇到矛盾 → 決定保留哪個 → 困難（需要完美的 fact 真實性判断）
- **ADD-only + temporal ranking**: 遇到矛盾 → 兩個都保留 → query時根據時間上下文动态选哪个 → 簡單很多

具體啟發：bounded dereferencing 中的 `conflict_flag` 不需要触发「删除旧记忆」的操作，而是标记「此记忆有时间上下文依赖，query時評估」。这样 drift 就变成了一个 retrieval 策略问题，而不是一个 state management 问题。

#### 3. Multi-signal retrieval 融合架構

Mem0 三路融合（semantic + BM25 + entity）與 FTS5 BM25 的 gap：
- FTS5 只有 BM25（結構化文本檢索）
- 缺 semantic 向量維度（需要 embedding model）
- 缺 entity linking 維度（跨記憶的 entity 關聯）

可行的彌補路徑：
- 短期：BM25-only（FTS5 已實作）→ 足夠基本使用
- 中期：BM25 + simple entity extraction（用 spaCy 或正則表達式）+ explicit temporal metadata
- 長期：考慮 hybrid（BM25 + 輕量向量相似度）

#### 4. BEAM 1M 下降的警示

LoCoMo 和 LongMemEval 大幅提升，但 BEAM 1M 分數下降（70.1 → 64.1）。可能的解釋：
- ADD-only 累積了更多 memory，在超長上下文（1M token）時反而引入更多噪點
- 在 10M 等級差距變小（-1.9），表示1M區間的干擾最明顯

對 Hermes 的啟示：ADD-only 模式在短中期累積記憶時有好處，但長期（超長 session）需要某种衰變機制（distillation / decay）。這呼應了 WS-037 的 staleness window 設計。

## Per-Source Insights

### mem0ai/mem0 — README (raw GitHub)

**核心價值：v3 algorithm 完整說明**

Source: `https://raw.githubusercontent.com/mem0ai/mem0/main/README.md`

這個 README 直接揭示了 v3 的核心創新。April 2026 發布，距離上次調研（May 2026）只有幾週，但演算法已經經過重大更新。

關鍵技術細節：
1. **Single-pass ADD-only**: 從「extract → update → delete」變成「extract → always ADD」
2. **Entity linking**: 跨記憶的 entity 提取和嵌入，建立知識圖譜
3. **Multi-signal fusion**: 三路並行檢索，分數加總

**與 Hermes 的對應**：
- `heartbeat_learning.py` 的 distillate 層目前是「extract + overwrite」（當 staleness 超標就 invalidate）。可以考慮改成 ADD-only + temporal ranking
- FTS5 BM25 是 multi-signal retrieval 的 BM25 維度，需要與 semantic 向量維度融合

## 未追蹤 Leads

- https://docs.mem0.ai/migration/oss-v2-to-v3 — Mem0 v2 → v3 遷移指南（了解 ADD-only 的具體實作）
- https://mem0.ai/research — 完整論文（ Benchmarks 的詳細方法論）
- `benchmarks/locomo/run.py` — LOCOMO benchmark 實作（可以跑 Hermes 版本的 baseline）

## Hermes 啟發

1. **FTS5 → Multi-signal roadmap**: 短期鞏固 BM25（已實作），中期加上 entity extraction + temporal metadata，長期考虑輕量向量融合
2. **WS-035 drift handling**: 考慮 ADD-only + temporal ranking 而非 conflict resolution。标记住忆的时间上下文依赖，query時动态评估
3. **Memory benchmark baseline**: 儘快跑 LOCOMO 對 Hermes 記憶系統建立 baseline，量化落後幅度
4. **BEAM 1M 下降警示**: ADD-only 需要配合蒸餾/衰變機制，避免長期 session 記憶污染

## ✅ 本次探索完成
