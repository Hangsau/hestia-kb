---
_slug: 40-Resources-_mixed-research-2026-06-14-1901-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-14-1901-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-14'
confidence: high
title: 2026-06-14 19:01 — Trigger Condition 為缺失原語：四篇 LLM 記憶架構論文對 Hermes heartbeat_learning.py
  的整合啟示
updated: '2026-06-15'
type: research
status: budding
---

# 2026-06-14 19:01 — Trigger Condition 為缺失原語：四篇 LLM 記憶架構論文對 Hermes heartbeat_learning.py 的整合啟示

**消化筆記**:
- 2026-06-09-llm-agent-memory-governance-synthesis
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine

四篇筆記各自看起來是不同記憶系統的獨立探索；放在一起才看見它們其實在回答**同一個被 Hermes 跳過的問題**：在一個分層 / 圖結構的長期記憶裡，**什麼時候該把資料從 A 層搬到 B 層**。Hermes 的 `heartbeat_learning.py` 目前只有「蒸餾寫入」與「時間衰減」兩個端點，沒有中間的 trigger 機制——這正是 2026 這批記憶系統論文集體補上的拼圖。

## Cross-Cutting Theme 1: 「Consolidation Trigger」是所有現代記憶系統的設計原語，而 Hermes 沒有

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

四篇論文雖然架構不同（H-MEM 四層 index、RecMem subconscious/episodic/semantic、MemoryOS STM/MTM/LPM、SAGE writer-reader graph），但**都把 trigger 條件作為一級公民設計**：

| 系統 | Trigger 種類 | 觸發變量 |
|------|------------|---------|
| H-MEM | user-feedback-driven | approval → strengthen weight、rebuttal → decay |
| RecMem | recurrence-driven | θcount ≥ 5 且 cos ≥ θsim |
| MemoryOS | heat-driven | N_visit + L_interaction + R_recency > τ |
| SAGE | reader-failure-driven | reader 找不到證據 → 回饋 writer |

而 `heartbeat_learning.py` 目前的路徑是 `distillate → (no staleness check) → retrieval`，中間的 trigger 完全缺位（hmem-recmem 筆記已明確指出此缺口）。Governed Memory 論文（arXiv:2603.17787）的「exponential recency decay」半衰期 38 天是 fallback，不是 trigger。

**非顯然之處**: 單看任一篇會以為 trigger 只是「壓低成本」(RecMem 87% token 節省)；四篇合看才發現 trigger 同時解決三件事：① 降低寫入 token、② 控制記憶密度（Governed Memory: ~7 memories/entity 飽和點）、③ 提供 staleness 信號（高熱 ≠ stale，低熱 ≠ 過時，需要 trigger 觸發語意衝突檢查）。

**可行動下一步**: 在 `heartbeat_learning.py` 新增 `consolidation_trigger.py` 模組，採用**複合 trigger**（不抄單一論文）：

```python
trigger_distillate_promotion(distillate) =
    recurrence_signal(distillate, window=30d)        # RecMem: 出現頻率
  OR heat_signal(distillate, half_life=38d)          # MemoryOS: 引用熱度
  AND NOT user_rebuttal_signal(distillate)            # H-MEM: 反駁衰減
```

三個信號並列 OR，任一觸發就升入結構化層；AND 條件確保用戶明確反駁的 distillate 不會被熱度誤升。實作入口：`consolidate_memory.py` 排程前先跑 `consolidation_trigger.scan_candidates()`，輸出 promotion list 給下游。

## Cross-Cutting Theme 2: Reader → Writer 反饋迴路是「Self-Evolving」與「Eager」的真正分水嶺

**支援筆記**: sage, hmem-recmem, memory-os, llm-agent-memory-governance-synthesis

SAGE 的核心創新是 **writer-reader self-evolution**：reader 檢索失敗 → 反饋 writer 修正圖結構。對比其他三篇：
- RecMem、MemoryOS、H-MEM 都是 **寫入端單向**（eager 或 trigger 寫入，無 reader 回饋）
- 只有 SAGE 顯式建模閉環

但把四篇合看會發現：**governance-synthesis 筆記提出的「event-driven invalidation」其實就是同一個閉環的另一面**——當環境事實改變（CTO 更換、vendor 評估出爐），reader 端觀察到「找不到符合 constraint 的 evidence」，這個失敗信號就是 trigger 該 distillation 失效的依據。MemoryOS 的 heat-based eviction 表面是「時間衰減」，實際上是**用 reader 引用次數當作隱性 reader feedback**——N_visit=0 持續 N 天的 segment 會被蒸發，本質就是 reader 「沉默地表達不需要」。

**非顯然之處**: 「Reader failure signal」這個概念在 SAGE 論文是 reader→writer 反饋；移植到 Hermes 應該是 **task context matching failure → distillation trigger failure**——當某個 distillate 連續 K 次 task context 檢索都沒被採用，不是該被標 stale，而是該被反饋給「未來是否還要蒸餾同類概念」的 writer 決策。這把 staleness detection 從被動的「時間到了就衰減」升級為主動的「系統承認這個 distillate 沒人需要」。

**可行動下一步**: 在 `consolidation_trigger.py`（承 Theme 1）之外，新增 `distillate_signal_collector.py`，記錄每個 distillate 的：
- `retrieval_attempt_count`（被 task context 嘗試匹配的次數）
- `retrieval_success_count`（真的被採用到 response 的次數）
- `staleness_candidate = (attempt > 10) AND (success == 0) AND (age > 14d)`

將 `staleness_candidate` 餵回 `consolidation_trigger.py` 作為**反向 trigger**——不只是「熱的升級」，也要「冷的降級」。這個反向 trigger 目前任何一篇論文都沒明說，但從 SAGE 閉環 + MemoryOS 熱度 + Governed Memory event-driven invalidation 三方交集可推導出。

## Cross-Cutting Theme 3: 「結構 vs 時機」是 orthogonal axis，但 Hermes 把它們綁在同一個決策點

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

從 governance-synthesis 筆記的對照表（hmem-recmem §跨論文 Synthesis）可看到一個清晰分工：

| 軸 | 系統 | 處理方式 |
|----|------|---------|
| 結構（資料放哪裡） | H-MEM positional index / MemoryOS segment-page / SAGE entity-relation graph | 一次性設計，後續微調 |
| 時機（何時搬遷） | RecMem recurrence / MemoryOS heat / H-MEM user feedback / SAGE reader failure | 動態 trigger |

Hermes 目前 `heartbeat_learning.py` 把這兩件事混在 `distillate` 物件的 `confidence_score` 單一欄位裡——結構（是否升入 structure）和時機（何時升）共用一個數字，且這個數字還是手設的「half-life=38d」時間衰減，沒有任何 trigger 條件。

**非顯然之處**: 結構選 H-MEM 的四層 position index（domain→category→trace→episode）已經在 `hmem-recmem` 筆記中提議移植到 Hermes skills（trigger condition→action→verification 對應四層）；時機選 MemoryOS heat + RecMem recurrence 的**聯集 trigger**（Theme 1）——兩者結合 = 「何時」觸發「在四層的哪一層」寫入。但目前沒有任何一篇論文做這個組合；四篇都是各自處理一軸。

**可行動下一步**: 開一個 `ws-035-memory-architecture-design.md` design doc（不是實作，是設計），把 axis 拆成兩個獨立子決策：

1. **Structure axis**: 採用 H-MEM 的 4-tier position index（domain/category/trace/episode），直接套用 `hmem-recmem` 筆記 §H-MEM 的 Position Index 可以移植到 Hermes Skills 段落
2. **Timing axis**: 採用 Theme 1 的複合 trigger + Theme 2 的反向 signal
3. 兩個 axis 的接合點定義為：`trigger_signal(type) → which_tier(type)` 的純函數

此 design doc 應該引用這四篇筆記的所有 trigger 公式，作為決策依據。實作順序：先 timing（影響小、風險低），後 structure（要動到 `distillate` 物件 schema，影響大）。

---

## 信心評估

- **Theme 1 (high)**: 四篇筆記都明確寫出 trigger 機制，且 H-MEM + RecMem + MemoryOS + SAGE 四套 trigger 互補，沒有矛盾。
- **Theme 2 (medium)**: SAGE 閉環 vs MemoryOS 熱度的等價性是推導出來的（兩篇未直接互引），Governed Memory event-driven invalidation 是 governance-synthesis 筆記的二手詮釋。需實證：若實作後發現「沉默 reader」信號比「顯式 reader failure」更常見，Theme 2 的優先級會再升。
- **Theme 3 (medium)**: orthogonal axis 拆解在四篇都未明說，是從 governance-synthesis 對照表反推的結構性觀察。可在實作時驗證：若 timing trigger 實作後發現「不知道該寫入哪一層」是主要痛點，Theme 3 就是正確的。

## 共同未追蹤項（給下次探索）

- **MemoryOS 開源 repo** (BAI-LAB/MemoryOS) — heat score 的實際超參數 (α, β, γ, τ) sweep 結果，可直接參考
- **Zep Temporal Knowledge Graph** — hmem-recmem 筆記列為待追蹤，可能是 trigger 設計的另一個對照點
- **LongMemEval-S benchmark** (500 conversations, 115k avg tokens) — 可作為 trigger 機制的 evaluation framework
- **SCM (Self-Controlled Memory, Wang et al. 2025)** — memory-os 與 sage 都列為比較對象，dual buffer + memory controller 模式可能補完 Theme 2 的 reader signal 設計
