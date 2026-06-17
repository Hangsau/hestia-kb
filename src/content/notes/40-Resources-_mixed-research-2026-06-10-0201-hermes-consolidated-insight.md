---
_slug: 40-Resources-_mixed-research-2026-06-10-0201-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-10-0201-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-10'
confidence: high
title: 2026 記憶系統四論文收斂：Event-Driven、Reader-Writer 閉環、結構化強制取代純 Embedding
updated: '2026-06-15'
type: research
status: budding
---

# 2026 記憶系統四論文收斂：Event-Driven、Reader-Writer 閉環、結構化強制取代純 Embedding

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇同一天（2026-06-09）產出的探索筆記，獨立來看是四個不同的記憶/治理系統設計；放在一起才看得出 2026 年的研究社群正在向三個共同方向收斂，且三個收斂點都直接命中 `heartbeat_learning.py` 與 `PolicyInterceptor` (WS-035) 的現存缺口。

## Cross-Cutting Theme 1: Event-Driven Invalidation 取代 Time-Based Decay

**支援筆記**: 全部 4 篇

四個系統用四種不同機制表達同一件事：「**記憶 staleness 不應該靠時間衰減偵測，應該靠事件信號**」。

- **H-MEM**: user approval/rebuttal 直接調整 memory weight（user feedback 是最強事件）
- **RecMem**: recurrence count ≥ θcount（重複出現才算存在，單次不算）
- **MemoryOS**: heat score = α·N_visit + β·L_interaction + γ·R_recency，**觸發蒸發的是 visit count 不是 time**（recency 只是 heat 的三個分量之一）
- **Governance synthesis（2605.06716 §3.2）**: 直接點名「uniform time decay 失效」——過時知識的 semantic representation 仍然看起來相關，無明顯跡象失效

**論文原文的明確認據**:
> "knowledge that is outdated often fails without overt indication... although factually incorrect, such information may still exhibit significant relevance in its semantic representation"
> — arXiv:2605.06716 Section 3.2

`heartbeat_learning.py` 目前用 `exponential recency decay (half-life=38d)` 做 stale detection——這正是四篇論文共同否定的模式。**缺口已從四個獨立來源被驗證**。

**可行動下一步**:
1. 開新 script `drift_event_detector.py`，定義三種 event signal：`user_rebuttal`（強）、`contradiction_with_new_distillate`（中）、`zero_heat_for_N_days`（弱）。
2. 把現有 `time_decay` 降級為 fallback：只在三個 event signal 都未觸發時使用。
3. 第一版實作只需 `user_rebuttal` 一個 signal——這是 4 篇論文中證據最強（OCL 205→0 violations + Governed Memory 100% adversarial compliance），且最容易從現有 `heartbeat_learning.py` 的 user feedback 機制擴展。

## Cross-Cutting Theme 2: Reader-Writer Feedback 閉環

**支援筆記**: SAGE、RecMem、Governed Memory（3 篇，high confidence）

三個系統的共同創新：**reader 的失敗不是終點，是 writer 改進的起點**。

- **SAGE**: 核心就是 writer-reader self-evolution loop。Reader 找不到足夠證據時，反饋「圖中缺少什麼結構」給 writer。
- **RecMem**: Semantic Refinement 機制。Episodic abstraction（LLM 摘要）會漏掉 fine-grained facts，system「回頭」去 raw interaction store 補回。**這是 reader-driven writer correction**。
- **Governed Memory**: Reflection-Bounded Retrieval。LLM judge evidence completeness → 若 incomplete 就 generate targeted follow-up queries（**query 是 reader 端的 writer**）。

**共同結構**:
```
Reader 失敗 → 失敗信號被結構化記錄 → Writer 據此改進 → 下次 Reader 表現提升
       ↑                                                      ↓
       └──────────────── 反饋閉環 ←─────────────────────────┘
```

這個模式在 `heartbeat_learning.py` **完全不存在**。目前的 distillate 流程是：寫入 → 等 decay → 被 reader 引用或不被引用。沒有「不被引用」反饋回 writer 的機制。

**可行動下一步**:
1. 在 `heartbeat_learning.py` 加入 `cold_distillate_detector`：每個 distillate 維護 `last_referenced_at` 和 `reference_count_30d`。當 `reference_count_30d == 0 AND heat_score < threshold`，標記為 `cold_candidate`。
2. `cold_candidate` 進入「待重蒸餾」佇列：下次有相關 trajectory 進來時，distillation trigger 優先考慮用新資訊覆蓋舊的 `cold_candidate`。
3. 量化目標（從 Governed Memory E2）：當某 concept 有 7 個 distillates 時達到 quality saturation，additional distillates yield diminishing returns。**超過 7 個 → 蒸發最舊最 cold 的**。

## Cross-Cutting Theme 3: 純 Embedding Similarity 已被結構化約束取代

**支援筆記**: 全部 4 篇

四個系統都用**結構化元素**補強或取代 pure vector similarity：

| 系統 | 取代/補強元素 | 機制 |
|------|--------------|------|
| H-MEM | discrete positional index | 「下一層子記憶的 pointer」是離散位置，不是語意相似度 |
| MemoryOS | cosine + Jaccard on keywords | 關鍵字集合強制 overlap，純 embedding 不夠 |
| SAGE | graph structural priors | hubs/bridges 角色學習，不是「找最近鄰」 |
| Governed Memory | schema-enforced typed properties | 結構化欄位，非自由 text |

**共同訊息**: 2026 年的記憶系統共識是 **「embedding 是必要但不足的」**。所有 production-grade 系統都加入了至少一個非-embedding 元素（position、keyword、structure、schema）。

**對 Hermes 的直接應用**: `heartbeat_learning.py` 目前的 distillate 匹配幾乎純靠 semantic similarity（task context embedding vs distillate embedding）。這與四個論文的收斂結論相違。

**可行動下一步**:
1. 給每個 distillate 加 `tags: [concept, domain, action_type]` 三維 metadata（schema-enforced）。檢索時除 similarity 還要求至少一個 tag 重疊（governed routing 的 fast path 概念）。
2. 短期：最低成本的 schema 就是 `domain`（從既有 `domain:` docstring 提取）——30 個無 domain skills（system-map 提到的問題）順便解決。
3. 中期：把 `tags` 變成 forced field，蒸餾時若 LLM 沒給出 tag 就 fallback 到 rule-based extraction（關鍵字 + 既有 skill taxonomy）。

---

## 額外觀察（信心：medium）：~7 的魔術數字

**支援筆記**: MemoryOS、Governed Memory（2 篇）

- MemoryOS STM: `max 7 pages` 固定長度
- Governed Memory: 「~7 governed memories per entity reaches near-peak personalization quality」

兩個獨立系統收斂到同一個 7。可能代表 working memory 的容量上限（Miller's law 的 7±2 在 2026 LLM context 仍適用）。**推測成分高**，但若屬實，這是 `heartbeat_learning.py` 設定 `max_distillates_per_concept` 的天然預設值。

**可行動下一步**: 把 `max_distillates_per_concept = 7` 設為 default，配合 Theme 2 的 cold_distillate_detector 形成自然蒸發機制——新 distillate 進入時，若該 concept 已 7 個，蒸發 heat 最低的。

---

## 三個 Theme 的交集：這是同一個東西的三個面向

若把三個 theme 放在一起看，會發現它們其實是**同一個新典範**的三個 facet：

```
         [Event-Driven]          [Reader-Writer]         [Structured Constraint]
              ↓                       ↓                           ↓
         「when」                  「who learns」              「what format」
         觸發時機                  誰改進誰                  結構如何表達
```

這個新典範可稱為 **「閉環、結構化、事件驅動的記憶系統」**——相對於 2024-2025 的「靜態、扁平、向量相似度」舊典範。

`heartbeat_learning.py` 目前完全在舊典範。三個 theme 的 next step 全部實作後，系統就從「寫入一次、被動等待 decay」升級為「事件觸發、reader 失敗反饋、schema 強制結構化」的閉環系統。
