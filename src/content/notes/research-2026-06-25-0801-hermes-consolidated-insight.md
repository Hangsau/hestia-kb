---
_slug: research-2026-06-25-0801-hermes-consolidated-insight
_vault_path: research/2026-06-25-0801-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- drift-penalty
- memory-architecture
- ws-035
source: multi
created: '2026-06-25'
confidence: high
title: Drift Penalty 不是單一信號：2026-06-09 四篇記憶架構探索的隱藏共識
type: research
status: seedling
updated: '2026-06-25'
---

# Drift Penalty 不是單一信號：2026-06-09 四篇記憶架構探索的隱藏共識

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 自主探索各自從不同 paper 角度（H-MEM、RecMem、MemoryOS、SAGE、Governed Memory、OCL、Storage→Reflection→Experience）切入 LLM agent 記憶架構，**但都收斂到同一個 WS-035 改造點**——heartbeat_learning.py 的 drift penalty 必須從「uniform time decay」升級為「多信號、閉環的事件驅動系統」。把四篇並列才看得出來，**各篇的「建議」其實是同一個架構的不同零件**。

## Cross-Cutting Theme 1: Drift Penalty 必須從「時間衰減」轉向「事件驅動的多信號融合」

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

四篇從不同命名空間描述同一個機制：

| 系統 | 信號名稱 | 觸發條件 | 對應的 drift 行為 |
|------|---------|---------|-------------------|
| H-MEM | user feedback (rebuttal) | approval → strengthen, rebuttal → decay | event-driven invalidation |
| RecMem | recurrence count (θcount) | 出現 ≥5 次相似才 consolidate | recurrence = 它值得存在 |
| MemoryOS | heat score (N_visit + L_interaction + R_recency) | heat > τ 才升級 LPM | 冷知識 = potentially stale |
| SAGE | reader failure signal | 讀不到證據 → 寫入端改進 | 讀取失敗 = 失效信號 |
| Storage→Reflection→Experience (2605.06716) | semantic contradiction | 新蒸餾與舊有衝突 | 高關聯事實突然失效 = staleness 而非 decay |

**這 5 個信號在本質上是同一個架構的 5 個視角**：
- **時間軸**：recency decay（MemoryOS 的 R_recency）
- **頻率軸**：recurrence count（RecMem）+ visit count（MemoryOS）
- **深度軸**：interaction length（MemoryOS）+ L_interaction
- **品質軸**：user feedback（H-MEM）+ semantic contradiction（Governed Memory）
- **閉環軸**：reader→writer failure signal（SAGE）

每一篇都批評了「uniform time decay」不足：2605.06716 Section 3.2 明確寫「outdated knowledge fails **without overt indication**; although factually incorrect, such information may still exhibit significant relevance in its semantic representation」——意即單看語意相似度抓不到 staleness，必須要 event signal 才能偵測。

**可行動下一步**:
- 在 `heartbeat_learning.py` 的 `DriftPenalty` class 加一個 `signal_aggregator` 子系統，定義 5 個 signal source（recency、recurrence、visit_count、feedback、contradiction），每個有 weight
- weight 預設值：contradiction 0.4（最強）、recurrence 0.25、feedback 0.2、recency 0.1、visit_count 0.05（最弱，因為 visit 容易受任務流行度偏差）
- 寫一個 `MultiSignalDriftCalculator`，input 是 (distillate_id, signal_vector)，output 是 (staleness_score, recommended_action ∈ {keep, decay, invalidate})，threshold 從 0.3/0.7 開始 ablation

**信心**: high（4 篇全部收斂，且 2605.06716 提供了 empirical anchor：contradiction_resolution 是 benchmark metric）

## Cross-Cutting Theme 2: Reader-Writer 閉環是所有記憶系統的隱藏骨架

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

第二個跨主題模式：四篇各自獨立提出「讀取端要回饋給寫入端」這個閉環概念：

- **SAGE**：最明確的 writer-reader self-evolution loop（reader 失敗 → writer 改進）
- **H-MEM**：user feedback 從 reader 端流向 writer 端（rebuttal → decay）
- **MemoryOS**：heat score 是 reader→writer 的回饋路徑（N_visit 從 retrieval counter 流回 LPM 升級）
- **Governed Memory (2603.17787)**：reflection-bounded retrieval 讓 LLM judge evidence completeness，incomplete 就 generate follow-up queries——這就是 in-loop 的 reader→writer feedback（query generator = 動態 writer）
- **OCL (2606.04306)**：constraint violation 觸發 deterministic replan——execution reader → proposal writer 閉環

**單篇筆記都沒意識到這是同一個 pattern**：每篇都把 reader→writer feedback 當作「該系統的特色」，但放在一起才看得出來——**這是 production-grade memory system 的必要條件，不是 nice-to-have**。缺了閉環，記憶系統就只是個 append-only log。

**對應到 WS-035**：目前的 heartbeat_learning.py 是 pure writer 模式（蒸餾 → 存），沒有 reader→writer 回饋。task context matching 是 reader，但它的失敗信號（distillate 沒被引用）沒有回流到 distillate 維護決策。

**可行動下一步**:
- 在 heartbeat_learning.py 加一個 `RetrievalFeedbackCollector`，每次 task context matching 結束時記錄 `(distillate_id, was_referenced, retrieval_usefulness_score)`
- `usefulness_score` 用 0/1 binary 起步（被引用 vs 沒被引用），未來可升級為 LLM judge
- 累積 N 次低 usefulness 的 distillate 觸發 Theme 1 的 staleness 計算
- 寫一個 weekly cron 跑 `drift_review.py`：列出上週 usefulness < 0.1 的 distillates，建議 archive 或 re-distill

**信心**: high（4 篇直接引證，且閉環是 control theory 與 RL 的基本原則，這個收斂不是巧合）

## Cross-Cutting Theme 3: Token cost 是真實瓶頸，但每篇只解一個變數——需要綜合預算

**支援筆記**: hmem-recmem, memory-os, llm-agent-memory-governance-synthesis（SAGE 沒量化）

四篇各自量化了記憶系統的某個 token cost 維度，但沒有一篇給出 unified budget model：

- **RecMem**：87% construction token 節省（via recurrence-triggered，避免 eager LLM call）
- **H-MEM**：retrieval 從 O(a·10^6·D) 降到 O((a+k·300)·D)，latency 從 100ms+ 降到 <100ms
- **MemoryOS**：3,874 tokens/query + 4.9 LLM calls（vs A-Mem 13.0 calls，68% 節省）
- **Governed Memory (2603.17787)**：tiered routing（fast 850ms vs full 2-55s）+ progressive context delivery（50% token reduction）

**單篇看不出的東西**：這些是不同的開銷來源（construction、retrieval、context delivery、tiered routing），且它們之間有 trade-off。RecMem 省 construction 但 retrieval 沒改；MemoryOS 在 MTM 段做 LLM summary 增加了 construction cost 但降低 retrieval 開銷；Governed Memory 的 fast path 省錢但犧牲 precision。

**WS-035 對應**：heartbeat_learning.py 目前的 distillate 流程是 unbounded LLM call，沒有 budget cap，也沒有 tiered routing。drift penalty 計算本身如果每次都跑 LLM judge，會消耗大量 token。

**可行動下一步**:
- 定義 `MemoryOperationBudget` schema：`max_construction_tokens_per_distillate`、`max_retrieval_tokens_per_query`、`max_drift_check_llm_calls_per_week`
- drift check 走 Governed Memory 的 tiered pattern：fast path 用 recency+visit_count（無 LLM call），full path 用 LLM contradiction check（只在 fast path 標記為 suspect 時觸發）
- 預期 token 預算：drift check 從 unbounded 降到 < 200 LLM calls/週（假設 100 個 distillates，每個 2 signals 都 fast path）

**信心**: medium（只有 3 篇量化，且 trade-off 整合是推論成分）

## 整合視角：WS-035 Drift Penalty 的 4 個 Component 來自 4 篇

把三個 theme 拼起來，WS-035 drift penalty 的完整設計其實已經在這 4 篇裡「散落」著——只是沒有單一筆記把它組裝起來：

1. **Signal sources**（Theme 1）— 從 5 個 paper 的 5 個信號抽取
2. **Feedback loop**（Theme 2）— 從 SAGE/Governed Memory/OCL 的閉環模式抽取
3. **Budget control**（Theme 3）— 從 MemoryOS/Governed Memory 的 tiered routing 抽取
4. **Output schema**（隱藏的第 4 個 component）— 從 2603.17787 的 schema-enforced memory 抽取：drift 決策應該是 structured output（`{action, reason, suggested_replacement_id}`），不只 text summary

**4 篇筆記各自給了 1-2 個 component 的靈感，但從未串接**。這就是 cross-cutting synthesis 的價值——把分散的零件拼成可實作的藍圖。

**可行動下一步**（integrated）:
- 開 `WS-035/SPEC.md`，列出 4 個 component 與其 paper 來源（H-MEM、RecMem、MemoryOS、SAGE、Governed Memory、OCL、Storage→Reflection→Experience）
- 第一個 PR：實作 Theme 2 的 RetrievalFeedbackCollector（最簡單，純 append-only log）
- 第二個 PR：實作 Theme 1 的 MultiSignalDriftCalculator，套用 Theme 3 的 tiered routing
- 第三個 PR：整合 Theme 4 的 structured output，下游 system-map 可直接消費
