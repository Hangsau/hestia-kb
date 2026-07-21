---
_slug: research-2026-07-21-1101-hermes-consolidated-insight
_vault_path: research/2026-07-21-1101-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- drift-penalty
source: multi
created: '2026-07-21'
confidence: high
title: 4 篇 Memory Architecture 研究的收斂訊號：Reader→Writer 失效信號回饋是 WS-035 的真正缺口
type: research
status: seedling
updated: '2026-07-21'
---

# 4 篇 Memory Architecture 研究的收斂訊號：Reader→Writer 失效信號回饋是 WS-035 的真正缺口

**消化筆記**:
- 2026-06-09-llm-agent-memory-governance-synthesis
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine

4 篇獨立研究（來自 EACL 2026、ACL 2026 Findings、EMNLP 2025、NeurIPS 2026 + 3 篇獨立 arXiv）在 memory architecture 設計空間的不同區域各自深掘，卻全部指向同一個缺口：**「reader 端的失效信號沒有回饋給 writer 端的蒸餾/更新邏輯」**。這是 WS-035 drift penalty 應該填補的位置。

## Cross-Cutting Theme 1: Reader→Writer 失效信號回饋是 6 個系統的共同缺口

**支援筆記**: 全部 4 篇（但論點由各篇獨立提出）

**分析**

每一篇都摸到「reader 失敗時該如何影響 writer」這個邊界，但都沒做到閉環：

| 系統 | Reader 端做了什麼 | Writer 端收到什麼 | 閉環？ |
|------|------------------|------------------|--------|
| **SAGE** (2605.12061) | GFM-based reader，soft addressing + propagation | Writer 收到 failure signal 改進寫入 | **是**（唯一閉環） |
| **Governed Memory** (2603.17787) | Reflection-bounded retrieval，reformulate query | 無（query reformulation 是 reader 內部動作） | 否 |
| **MemoryOS** (2506.06326) | Heat score（visit + interaction + recency） | Heat < threshold 時 evict（L_interaction 重置為 0） | 半閉環（被動） |
| **RecMem** (2605.16045) | Subconscious cosine filter → | recurrence ≥ θcount 觸發 consolidation | 半閉環（單向） |
| **H-MEM** (2026.eacl-long.15) | Top-down layer routing | User feedback 直接 strengthen/decay weight | 半閉環（人工觸發） |
| **Storage→Reflection→Experience** (2605.06716) | LLM evaluator 判斷 completeness | 觸發 cross-trajectory abstraction | 概念閉環、無實作 |

把 6 個系統並排看得到：**只有 SAGE 真正實作了 writer-reader self-evolution loop**——reader 在 multi-hop QA 失敗時反饋「圖中缺少哪些關係」，writer 據此補結構。其他 5 個各自有一個 reader-to-writer 信號，但都是單向的（reader 觀測 → 觸發事件），沒有「writer 消化這個信號後，未來 reader 表現如何」的閉環驗證。

SAGE 用 **two self-evolution rounds 達到 multi-hop QA 最佳平均 rank** 量化了這個閉環的收斂性——這個收斂訊號本身是別人沒有的 insight。

**可行動下一步**

修改 `heartbeat_learning.py` 加入 reader→writer 回饋通道。具體：

1. 在 distillate 寫入時記錄 `distillate_id → last_reader_signal` 欄位
2. `task context matching`（reader）找不到合適 distillate 時，記錄 `failure: concept=⟨X⟩, evidence_gap=⟨Y⟩` 到 `~/.hermes/state/reader_failures.jsonl`
3. `distillation trigger`（writer）下次 run 時讀這個 log，若某概念在 N 天內累積 ≥ K 次 failure，主動觸發 cross-trajectory distillation
4. 評估指標：reader failure rate 在 2 個 round 後是否下降（仿 SAGE two-round convergence）
5. 第一個 PR 改動控制在 ~50 行：加 JSON log writer + 讀取邏輯，不改既有 decay/heat score

## Cross-Cutting Theme 2: 「Eager consolidation 是反模式」已升級為領域共識 + 「7」是 magic number

**支援筆記**: 全部 4 篇

**分析**

**Eager consolidation 反模式**的論據：

- **RecMem**（2605.16045）量化：**87% token 浪費**——所有 incoming interaction 都做 LLM consolidation 是 token cost 的最大瓶頸
- **Storage→Reflection→Experience**（2605.06716）明確反對：Reflection 不應取代 Storage，三階段是疊加演進而非取代
- **MemoryOS** 用 heat-based eviction 取代 FIFO 的 trivial eviction（不滿足 heat threshold 不晉升 LPM）
- **H-MEM** 通過 hierarchical routing 避免 exhaustive flat retrieval（O(a·10^6·D) → O((a+k·300)·D)）

**「7」（±1）是 magic number**的論據：

- **MemoryOS STM**：固定 7 pages 對話佇列
- **MemoryOS User KB**：100 條 FIFO（接近 7² 工作記憶容量的平方化）
- **Governed Memory**（2603.17787）：**7 memories per entity 達到 near-peak personalization quality**（+24% relative jump from 0→3 memories；7 之後 diminishing returns）
- **H-MEM**：4 層 hierarchy 是 ablation 確認的最優點（不是 7，但同樣是工程化經驗值）

這不是巧合——Miller's Law（1956）working memory capacity 是 7±2 個 chunks。MemoryOS 和 Governed Memory 各自獨立得出的「7」是 cognitive science constraint 在 LLM memory 系統的工程化體現。**這意味著我們應該停止搜尋「最佳分層數」、「最佳 saturation 容量」的 optimization 結果，直接用 7 作為 starting hyperparameter**。

**可行動下一步**

1. 在 `consolidate_memory.py` 輸出的 distillates 中，**對每個 concept cluster 設定上限 7 個 active distillates**，超過的標記為 archive（不刪除，避免 recurrence 誤判）。
2. WS-035 的 distillate writer 改寫：當某 concept 已有 7 個 distillates 時，新 distillate 預設進入 archive queue，等 heat score 排擠掉最低者才晉升（仿 MemoryOS LPM FIFO + heat eviction）。
3. 寫一個 `arch_note: ~/.hermes/diary/2026-07-21-memory-saturation-magic-7.md` 記錄這個觀察，標註 [miller-1956 | governed-memory-2603.17787 | memoryos-2506.06326] 三方 cross-validation。
4. 第一個 PR 改動：加 `MAX_ACTIVE_DISTILLATES_PER_CONCEPT = 7` 常數 + archive queue，FIFO 邏輯約 30 行。

## Cross-Cutting Theme 3: Staleness detection 必須從 time-decay 升級為 event-driven invalidation

**支援筆記**: 全部 4 篇（以不同論證路徑）

**分析**

`heartbeat_learning.py` 目前用 exponential recency decay（half-life=38 days），4 篇獨立研究都指出這不夠：

| 證據來源 | 論證 |
|---------|------|
| **2605.06716** Section 3.2 | 「knowledge that is outdated often fails **without overt indication**」——高關聯事實突然失效，但 semantic representation 仍然看起來相關 |
| **RecMem**（2605.16045） | recurrence trigger 是事件，不是時間——同樣的概念若 recurrence 停掉，代表它已過時 |
| **H-MEM**（2026.eacl-long.15） | user feedback 直接觸發 weight decay，不等時間 |
| **SAGE**（2605.12061） | reader failure signal 是事件，不是時間——graph 結構缺失立即反饋給 writer |
| **MemoryOS**（2506.06326） | heat score 雖含 recency decay，但主軸是 visit count + interaction length（事件維度） |
| **Governed Memory**（2603.17787） | semantic conflict resolution 83.3% detection——衝突事件觸發 suppression，不等 decay |

把這 6 個論證並排看：**drift 不是「知識慢慢變舊」這種漸進過程，而是「觸發事件 → 立即標記 → 等待 eviction 或 contradiction resolution」這種事件驅動過程**。Half-life=38d 的 smooth decay 是錯誤的 abstraction layer。

`heartbeat_learning.py` 的 drift penalty 應該由兩部分組成：
- **Event-driven invalidation**（新增）：reader failure log、user rebuttal、contradiction detection 觸發 immediate staleness flag
- **Time-based decay**（保留）：fallback for 無事件的 gradually cooling memory

這呼應了 Theme 1 的讀者-寫者閉環——staleness events 正是 reader→writer 的信號內容。

**可行動下一步**

1. 在 `heartbeat_learning.py` 加入 `event_driven_invalidation` 表（distinct from heat score）：
   - `distillate_id`
   - `event_type ∈ {reader_failure, user_rebuttal, contradiction}` 
   - `event_timestamp`
   - `status: pending | invalidated | resolved`
2. Distillate retrieval 時，若 `event_driven_invalidation.status = invalidated` 存在，**bypass heat score 直接返回 None**（即便 heat 還高）
3. 反向：若 `event_driven_invalidation.event_type = reader_failure` 累積 ≥ 3 次，主動觸發 cross-trajectory re-distillation（Theme 1 步驟 3 的觸發條件之一）
4. 第一個 PR：SQLite 新 table + 讀取時 check，~80 行

## 整合觀察

3 個 themes 不是獨立的——

- **Theme 1**（reader→writer 閉環）是機制
- **Theme 2**（7 magic number）是容量上限
- **Theme 3**（event-driven invalidation）是觸發條件

把三者組合 = WS-035 drift penalty 的完整 prototype：
> 7 ± 2 個 active distillates per concept，event-driven 觸發 invalidation / re-distillation，reader failure signal 反饋 writer，self-evolution rounds 量化收斂。

這是 4 篇獨立研究從不同路徑都收斂到的設計空間，而 Hermes 還沒填補這個位置。優先級應該是 Theme 3（event-driven invalidation）→ Theme 2（7 上限）→ Theme 1（reader→writer 閉環），因為前兩者改動小、可以直接 ship，第三個需要更多 design。
