---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-23'
confidence: high
title: 記憶系統收斂：容量工程 + 失敗優先學習
updated: '2026-06-15'
type: research
status: budding
---

# 記憶系統收斂：容量工程 + 失敗優先學習

**消化筆記**: 2026-05-21-memori-atlas-long-term-memory-deep-dive, 2026-05-22-agent-memory-rubric-scoring-memori-r2mem, 2026-05-23-r2-mem-rubric-thresholds-deep-dive

三篇同時期的 memory/learning 研究，各自研究不同系統（Memori、R²-Mem、ATLAS），但交叉比對後收斂到兩個一致的工程方向。

---

## Cross-Cutting Theme 1: 失敗案例比成功案例更有學習價值

**支援筆記**: 2026-05-23-r2-mem-rubric-thresholds-deep-dive, 2026-05-21-memori-atlas-long-term-memory-deep-dive, 2026-05-22-agent-memory-rubric-scoring-memori-r2mem

### 分析

R²-Mem 論文有直接的實驗數據：**只用 low-quality experience > 只用 high-quality experience**。失敗案例提供更正信號（corrective signal），成功案例只是確認現有行為。

Memori 的 benchmark 數據從另一個角度印證同一件事：Memori 在 **Temporal（80.37%）和 Open-domain（63.54%）表現最差**——這兩個類別恰好是「需要從失敗中學習」的場景（temporal 需要追踪錯誤假設，open-domain 需要處理異常邊界）。Memori 的 triple+summary 結構善於處理「常見事實」，但不善於處理「罕見錯誤」。

R²-Mem 的最佳閾值 (K_low=5, K_high=10) 隱含一個設計原則：**不要蒸餾灰色地帶（5-10分）的 experience，只蒸餾黑白分明的**。灰色地帶浪費蒸餾 token 但對學習貢獻低。

### 可行動下一步

修改 `heartbeat_learning.py` 的 experience distillation 邏輯：

1. 加入失敗導向的 special track：當 action 的 Reflection score < 5（低充分性判斷）時，把完整失敗鏈（trigger condition → wrong decision → outcome）存入 `bad_experiences/` 子目錄
2. 在 `_detect_recurring_errors()` 中增加 `bad_experience_weight=2.0`——bad experience 檢索權重為 good experience 的兩倍
3. 確保 distillation prompt 只蒸餾 score < 5 或 score > 10 的 steps，中間範圍 skip

---

## Cross-Cutting Theme 2: 記憶容量是工程參數，不是意外結果

**支援筆記**: 2026-05-21-memori-atlas-long-term-memory-deep-dive, 2026-05-22-agent-memory-rubric-scoring-memori-r2mem, 2026-05-23-r2-mem-rubric-thresholds-deep-dive

### 分析

三個數據點各自從不同角度討論容量問題：

| 系統 | 容量表示 | 實測效率 |
|------|----------|----------|
| Memori | Semantic triples + summaries 雙層結構 | 1,294 tokens = 5% full context |
| ATLAS | Polynomial feature map: O(d_k^p) | 10M context BABILong +80% over Titans |
| vault_decay (Hermes) | `count / (age^0.5)` scoring | 未知，無 benchmark |

Memori 的 1,294 tokens 不是魔法數字——它是一個**目標約束**：從一開始就設定「我要把 context 壓到 X%」，然後往回工程化架構。ATLAS 的 O(d_k^p) 給了理論基礎——簡單的線性映射容量受限，需要 nonlinear feature mapping 才能擴展。

R²-Mem 的 experience format `{condition, situation, experience}` 提供了具體的 storage schema——這不是 free-form text，是**有意義壓縮的結構化表示**。每個 field 都有用途，不是自然語言的冗余表達。

**非顯然的連結**：Memori 的「破壞性 distill」（原文丟）和 ATLAS 的「architecture-level capacity」（無額外 token）在 token 效率和召回能力之間做了不同取捨——但兩者都同意一點：**raw text 不適合直接當記憶**。Memori 用 structured extraction，ATLAS 用 nonlinear feature mapping，目標都是把「高維原始資料」壓成「低維高資訊密度表示」。

### 可行動下一步

為 vault pipeline 的每個 stage 設定明確的容量預算（backward engineering from target）：

1. **Distill stage**: 輸出上限 = 原始對話長度的 10%，用 `len(distill_output) / len(raw_conversation) <= 0.10` 作為 quality gate
2. **Consolidate stage**: 輸出上限 = distill 輸出的 5%
3. **Experience JSON**: 每筆 experience 上限 500 tokens，超過則截断 low-importance fields（保留 `condition` 和 `experience`，裁 `situation`）
4. 在 `consolidate_memory.py` 加入容量 report：每次 consolidation 輸出「total tokens in / tokens compressed / compression ratio」，累積成 capacity trend chart

---

## 對現有 WS 提案的映照

| WS 提案 | 本次 insight 具體影響 |
|---------|----------------------|
| WS-004（consolidate）| 容量預算 + 失敗案例優先蒸餾 |
| heartbeat_learning rubric | R²-Mem (5,10) 閾值 + Planning/Reflection 8維度 |
| vault_decay | 從「隨時間衰減」升級為「基於 quality score 的容量管理」 |