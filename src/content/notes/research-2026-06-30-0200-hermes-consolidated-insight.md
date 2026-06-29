---
_slug: research-2026-06-30-0200-hermes-consolidated-insight
_vault_path: research/2026-06-30-0200-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- agent-memory
- ws-035
source: multi
created: '2026-06-30'
confidence: high
title: 讀寫閉環 + 事件驅動失效：4 篇 agent memory 論文的隱性收斂
type: research
status: seedling
updated: '2026-06-30'
---

# 讀寫閉環 + 事件驅動失效：4 篇 agent memory 論文的隱性收斂

**消化筆記**:
- 2026-06-09-llm-agent-memory-governance-synthesis
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine

4 篇獨立探索都圍繞「LLM agent 的長期記憶怎麼管」這個題目。單看每一篇，hierarchy / recurrence / OS-style paging / graph self-evolution 各自是獨立設計；但把它們並排，會浮現兩個單篇看不到的共識——讀寫必須閉環、失效必須事件驅動。

> **與 02:00 cron 同步注意**：本次觸發時 4 篇已在 00:01 cron 被標記為 fed（見 `[[2026-06-30-0001-hermes-consolidated-insight]]`），該份 note 走的是 meta-observation 路線（飽和、state reset、建議互斥性）。本份走內容綜觀路線（4 篇共同的架構共識）。兩者不衝突、互補；`--mark-fed` 在本次無可標記筆記（已被前次消費），符合規則。

## Cross-Cutting Theme 1: Reader signal 必須回灌給 Writer，純 write-then-forget 已過時

**支援筆記**: hmem-recmem, memory-os, sage, governance-synthesis

4 篇從不同切入點收斂到同一個架構 pattern——記憶的 reader（檢索/查詢端）必須有訊號回灌給 writer（寫入/蒸餾端），形成閉環：

- **H-MEM**: user feedback 直接調整 memory weight——approval strengthen、rebuttal 觸發 decay。讀端（user）對記憶的評價是寫端的輸入。
- **RecMem**: 同一個 raw unit 被 query 多次（cosine similarity ≥ θsim 且 count ≥ θcount）才觸發 consolidation。讀端命中頻率是寫端升級的觸發條件。
- **MemoryOS**: heat = α·N_visit + β·L_interaction + γ·R_recency——N_visit（被檢索次數）是 heat score 的主成分。Segment 被讀越多越不容易被蒸發；LPM 升級後 L_interaction 重置讓熱度下降，避免舊 segment 永遠卡住。
- **SAGE**: 最明確的閉環——Reader 檢索失敗 → 反饋給 Writer「圖中缺少什麼結構」→ 下一輪 self-evolution 改進寫入策略。論文量化「two self-evolution rounds → multi-hop QA 最佳平均 rank」。

**單篇看不見的是**：這 4 個系統的設計動機雖然不同（H-MEM 為 efficiency、RecMem 為 token cost、MemoryOS 為 persona 演化、SAGE 為 graph completeness），但它們**各自獨立**都拒絕了「write-then-forget」的純粹 append-only 模型。這不是巧合，而是 2026 年 production-grade agent memory 的事實標準。

對 Hermes 的 `heartbeat_learning.py` 來說，目前的 distillate pipeline 本質上還是 write-then-forget——distillate 寫入後只能等 time-based decay，沒有 reader failure signal 回收機制。

**可行動下一步**: 在 `heartbeat_learning.py` 為每個 distillate 增加 `last_referenced_at` 與 `reference_count` 兩個欄位（schema migration），加上一個 `report_stale_distillates()` 函式：當某 distillate 連續 30 天 `reference_count == 0` 時，emit 一個 "potential staleness" 事件到 log/heartbeat，讓後續的蒸餾 trigger 可以決定是否重新覆蓋。預估工作量：1 個 PR，< 100 LOC，不需新依賴。

## Cross-Cutting Theme 2: 純時間 decay 在 2026 已被放棄，事件驅動失效是 consensus

**支援筆記**: hmem-recmem, memory-os, sage, governance-synthesis

governance-synthesis 那篇點出了一個關鍵洞察：「staleness ≠ decay」——Decay 是低關聯記憶平滑衰減（exponential recency），Staleness 是高關聯事實突然失效。論文引文：「knowledge that is outdated often fails without overt indication; although factually incorrect, such information may still exhibit significant relevance in its semantic representation」。

把這個洞察和另外 3 篇對齊，可以看到 5 個獨立系統都放棄了純時間 decay：

- **H-MEM**: memory weight 由 user feedback 動態調整，不是時間函數
- **RecMem**: θsim 過濾 + θcount 觸發，本質上是「事件觸發」（新 arrival 觸發 query）
- **MemoryOS**: heat score 三維（visit × interaction × recency），recency 只是其中一項
- **SAGE**: reader failure signal 是直接的事件——失敗就觸發 writer 改進，沒有時間等待
- **Governed Memory** (2603.17787): semantic conflict resolution 83.3% detection，但仍是 exponential recency 為 fallback——明確承認 production gap

**單篇看不見的是**：4 個系統給出的「事件」定義其實是**互補**的：
- H-MEM 的事件 = user explicit feedback
- RecMem 的事件 = recurrence of similar unit
- MemoryOS 的事件 = visit + interaction signal
- SAGE 的事件 = reader retrieval failure
- Governance synthesis 的事件 = semantic contradiction

這 5 種事件可以組合成一個完整的 staleness detector：**沒有任何單一事件足以標記 staleness，但任 2 種事件同時發生（例如 recurrence 下降 + reader failure 上升）就是高信心 staleness signal**。

**可行動下一步**: 在 `heartbeat_learning.py` 的 staleness 計算中，從 `exp(-Δt/μ)` 單一公式改成加權的 multi-event 評分。具體公式： `staleness_score = w1·(1 - normalized_visit_count) + w2·contradiction_event_count + w3·recency_decay + w4·reader_failure_signal`。初始權重全部 = 0.25，等收集 2 週的日誌後用 LoCoMo-style benchmark 回頭校準。預估工作量：1 個 PR + 1 個 calibration script（< 50 LOC）。

## Cross-Cutting Theme 3（bonus, medium confidence）: Token cost 與結構完整性是 trade-off，不是 trade-in

**支援筆記**: hmem-recmem, memory-os, governance-synthesis

這個 theme 只有 3 篇直接量化（RecMem 87% token 節省、MemoryOS 3874 vs 16977 tokens、Governed Memory progressive delivery 50% 節省），信心 medium 但 pattern 清楚：

| 系統 | Token cost | 結構完整性 |
|-----|-----------|-----------|
| RecMem | 最低（subconscious 不調 LLM）| 中（只 refined recurring patterns）|
| MemoryOS | 中（4.9 LLM calls）| 高（STM/MTM/LPM + User Traits 90 維）|
| Governed Memory | 中-高（full mode 2-55s）| 最高（schema-enforced + reflection-bounded）|
| H-MEM | 未直接量化 | 高（4 層 hierarchical routing）|

**洞察**: 沒有一個系統同時在兩個維度都是 top——RecMem 用放棄結構完整性換 token，Governed Memory 用放棄 latency 換結構。Hermes 要選的其實是「在 WS-035 的 38-day half-life 預算下，可以承受多少 token cost 換多少結構完整性」。

**可行動下一步**: 把這個 trade-off 表加進 `hermes-agent-feeding-report` 的「memory architecture 評估」段落，作為未來選擇 memory backend 框架的決策矩陣。不需寫 code，是個 1-paragraph doc update。
