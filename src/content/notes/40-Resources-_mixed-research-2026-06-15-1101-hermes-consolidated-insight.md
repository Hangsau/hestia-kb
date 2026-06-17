---
_slug: 40-Resources-_mixed-research-2026-06-15-1101-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-15-1101-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-governance
- drift-penalty
- ws-035
source: multi
created: '2026-06-15'
confidence: high
title: 記憶系統的「觸發信號」其實是同一個變數的 4 種測量
updated: '2026-06-15'
type: research
status: budding
---

# 記憶系統的「觸發信號」其實是同一個變數的 4 種測量

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 的 agent memory 探索各自看起來在講不同主題（階層 routing、recurrence 觸發、graph self-evolution、governance routing），但合併來看，WS-035 drift penalty 的設計其實被這四篇從四個方向「同時收斂」到同一個架構模式。

## Cross-Cutting Theme 1: 所有「eager vs triggered consolidation」的差異是 trigger 信號，不是寫入策略

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

四篇都否定「每個 incoming interaction 都 LLM consolidate」。表面差異：

| 系統 | Trigger 信號 | 寫入策略 |
|------|------------|---------|
| H-MEM | user feedback (rebuttal → decay) | 4 層 hierarchical routing |
| RecMem | recurrence count (θcount ≥ 5) | 3 層 subconscious→episodic→semantic |
| MemoryOS | heat score (α·N_visit + β·L_interaction + γ·R_recency) | 3 層 STM/MTM/LPM |
| SAGE | reader failure signal | Graph writer-reader loop |
| Governed Memory | governance routing (fast/full) + reflection-bounded | dual open-set + schema-enforced |

**實際上**：四種 trigger 信號都是「下游使用證據」（retrieval/use/feedback），而不是「寫入時的顯著性」（importance/recency/novelty）。Heat、recurrence、rebuttal、reader-failure 都是同一個潛變數的不同測量方式——**「這個記憶是否在為後續推理買單」**。

這對 Hermes 是 non-obvious 的：四篇筆記各自把這個變數取了不同名字（heat, weight, confidence, failure signal），讀起來像 4 個獨立設計。並排看才看出來——WS-035 drift penalty 不需要 4 個獨立信號通道，只需要 1 個 composite signal。

**可行動下一步**: 在 `heartbeat_learning.py` 的 drift penalty 模組新增 `distillate_value_signal.py` 介面，定義 4 個 adapter（heat_adapter, recurrence_adapter, feedback_adapter, failure_adapter），每個 adapter 輸出一個 `value ∈ [0, 1]` 標準化分數，drift penalty 用加權平均讀單一 composite signal。先用 MemoryOS 的 heat score（最容易從現有 `distillate_visit_log` 算）作 v0 實作，其他三個 adapter 之後再接。預期可消除目前「distillate staleness 判斷不一致」的 bug 群。

## Cross-Cutting Theme 2: Drift penalty 必須是閉環控制器，不是 time-based 衰減

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

Note 4（governance synthesis）明確指出統一時間衰減的失效模式：

> "knowledge that is outdated often fails without overt indication ... although factually incorrect, such information may still exhibit significant relevance in its semantic representation"

換句話說，staleness 與 decay 是不同的：decay 是低關聯平滑衰減，staleness 是高關聯突然失效。Time-based decay（half-life=38 days）解前者不解後者。

四篇筆記各自提出解方：
- **RecMem**：recurrence 是「使用中」的信號 → consolidate
- **MemoryOS**：heat score 的 N_visit = 0 長期 → cold → evict
- **SAGE**：reader failure signal → writer 的改進目標
- **Governed Memory**：reflection-bounded retrieval 的 query generation strategy 是 signal 來源

**共同點**：四者都把 memory 的「存活」繫於「使用」上，沒有任何一個用純時間決定。但目前 `heartbeat_learning.py` 的 drift penalty 是 open-loop：寫入時計算 staleness score，之後只靠 time decay 修正，沒有機制讓下游（task context matching）回報「這個 distillate 已經無用」。

**可行動下一步**: 把 `heartbeat_learning.py` 的 drift penalty 從「寫入時計算 + time decay」改為「read-time 觀測 + 滑動視窗衰減」。具體：
1. `Distillate` 加 `last_retrieved_at` 和 `retrieval_count_30d` 欄位（從 FTS5 查詢 log 推導）
2. drift penalty = `f(recency, retrieval_count, contradiction_events)`，沒有 retrieval 的 distillate 加速 decay（相當於 heat = 0）
3. 第一次失敗 retrieval 觸發 `stale_candidate` flag，第二次失敗才實際標 stale（避免單次 false negative 殺死好 distillate）

預期行為改變：高頻被引用的 distillate 不會被時間淘汰，零引用的 distillate 在 30 天內被自然淘汰，與新行為匹配。

## Cross-Cutting Theme 3: Token 成本是架構決策的因，不是果

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

四篇 papers 各自把「階層化」、「recurrence 觸發」、「graph 演化」、「governance routing」包裝成創新，但合併讀才看出：**這些結構都是 token/compute 約束的副產品**。

- H-MEM 的 4 層 routing：因為 flat retrieval 是 O(a·10^6·D) 在大規模記憶下 100ms+ latency，所以**必須**分層
- RecMem 的 recurrence trigger：因為 eager LLM consolidate 每個 interaction 太貴，所以**必須**等 pattern 重複
- MemoryOS 的 heat-based eviction：因為 MTM 容量固定（200 segments），所以**必須**蒸發
- SAGE 的 self-evolution loop：因為 writer 一次寫太貴，所以**必須**讓 reader feedback 指導 writer 改進
- Governed Memory 的 fast/full routing：因為 LLM classification 慢（2-55s），所以**必須**對簡單 case 跳過 LLM

**結構是約束的解，不是約束的源。**

這對 Hermes 的 non-obvious 啟示：目前 `heartbeat_learning.py` 的設計文件強調「consolidation quality」（架構選擇），但實際的設計 pressure 應該從「token cost budget」出發。先定義每月/每次 session 的 distillate token budget，反推允許的 LLM call 次數，再決定 consolidation 策略是 eager / recurrence-triggered / heat-driven。

**可行動下一步**: 在 `heartbeat_learning.py` 的 config 加 `monthly_distillate_token_budget` 參數（預設可從 cost_aggregator 推導），然後：
1. 把每個 distillate 的 LLM call token cost 計入 budget
2. 預算用完時自動切換到 recurrence-triggered mode（節流）
3. 月底 review：哪個 distillate 的 token 投入 vs retrieval count 比率最高/最低 → 下一季調整 trigger 閾值

這樣做可以把架構決策從「哪個 paper 聽起來好」變成「成本約束下的最優解」，避免每讀一篇新 paper 就重構一次 drift penalty。

---

**Meta-observation**: 這 4 篇都是 2026-06-09 同一天產出的探索筆記，3 篇明確標註「延續自」前一篇。從 hmem-recmem → memory-os → sage → governance-synthesis 是同一根思路的展開。**單日的密集探索讓 cross-cutting pattern 自然浮現**——這是 Hermes 自主探索模式的成功樣本。下次設計「單日多論文 digest」cron 時，優先排 4-5 篇相關主題的 paper，會比分散式單篇 fetch 更容易觸發此類綜合 insight。
