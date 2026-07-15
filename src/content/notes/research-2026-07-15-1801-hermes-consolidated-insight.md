---
_slug: research-2026-07-15-1801-hermes-consolidated-insight
_vault_path: research/2026-07-15-1801-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-07-15'
confidence: high
title: 2026-06 LLM Agent Memory Architecture 收斂：閉環 + Token-budgeted + Pre-execution
  Gate
type: research
status: seedling
updated: '2026-07-15'
---

# 2026-06 LLM Agent Memory Architecture 收斂：閉環 + Token-budgeted + Pre-execution Gate

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06 探索筆記表面上在討論「不同」的記憶系統（H-MEM、RecMem、MemoryOS、SAGE、Governed Memory、OCL），但 cross-reading 後浮現三個**跨系統的強收斂點**——它們不是單一論文的 novelty，是這個領域在同一個月獨立得出的共識。

## Cross-Cutting Theme 1: Memory 必須是閉環，write-then-forget 已經過時

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance

四篇從不同切入點收斂到同一個 architectural principle：**記憶系統必須在 reader 端產生可觀測信號，回灌到 writer 端的更新決策**。

- **SAGE** 最明確：writer-reader self-evolution loop，reader 檢索失敗 → 反饋 writer 補結構
- **H-MEM**：user feedback（approval/rebuttal）直接 drive memory weight dynamic adjustment
- **MemoryOS**：heat score 的 `N_visit`（reader 端的檢索計數）自動觸發 MTM→LPM 遷移與 eviction
- **Governed Memory**：reflection-bounded retrieval——LLM judge evidence completeness，incomplete 就 generate follow-up queries（reader 失敗 → 改變 query strategy）
- **OCL**：audit log 把所有 proposed decisions、constraint checks、outcomes 記下，**這些 log 本身就是下一輪的 reader-writer 介面**

單看任何一篇，這是「這篇論文的設計」。**放在一起才看出**：2026-06 的整個 LLM agent memory 領域，正在從「靜態結構設計」轉向「動態回饋系統設計」。Flat retrieval 之所以輸給 H-MEM，不是因為 H-MEM 結構更優雅，而是因為 H-MEM 結構本身承載了 feedback channel（user rebuttal → weight decay）。

**可行動下一步**:
打開 `heartbeat_learning.py`，檢查目前是否有「reader 端的引用/失敗信號回灌到 distillate writer」的機制。如果沒有，**在 distillate schema 加上 `last_referenced_at` 和 `reference_count` 兩個欄位**，並在 retrieval path 寫入這些計數（不需要新增 cron job，retrieval 本身就是 reader 端）。`drift_penalty` 從純時間衰改成 `time_since_last_reference`，這是 RecMem/MemoryOS/SAGE 三條路徑的交集點。

## Cross-Cutting Theme 2: Token cost 是架構決策的第一階 driver，不是 afterthought

**支援筆記**: hmem-recmem, memory-os, llm-agent-memory-governance

四篇都把 token 數量化為表格中的 headline metric，並以此推導架構選擇：

- **RecMem**：87% token reduction 是論文的賣點——這個數字直接驅動了「subconscious store + recurrence trigger」的設計（因為 eager consolidation 在 token 帳上是不可接受的）
- **MemoryOS**：3,874 vs MemGPT 16,977 tokens/query（77% 節省）——這個差距解釋了為什麼它選 STM=7 pages 的保守設定
- **Governed Memory**：progressive context delivery 省 50% tokens，是 routing tier 設計的 explicit 理由
- **H-MEM**：flat retrieval O(a·10^6·D) vs hierarchical O((a+k·300)·D)——把計算成本拉到 scalability 主軸

**模式**：所有新架構都在拒絕「eager/flat」設計，理由不是「eager 品質差」（事實上 A-Mem eager 也不差），而是「**eager 在 token 維度上不可持續**」。Token budget 是一階約束，記憶品質是二階約束。

這對 Hermes 的直接含義：**任何「每次互動都做完整蒸餾」的設計都需要被 token-budget 重新審視**。

**可行動下一步**:
盤點 `heartbeat_learning.py` 目前每次 heartbeat 觸發的 token 成本（LLM call 次數 × 平均 input/output tokens）。如果超過 2,000 tokens/cycle，套用 RecMem 的 recurrence threshold pattern——先在 subconscious buffer 累積 N 個 distillate candidates，**只有當 candidate 的 embedding cluster density 超過閾值時才呼叫 LLM 做 consolidation**。具體實作：在 `distillate_candidates/` 加一個 staging dir，候選先進 staging，cron 每天 batch 處理一次，cosine similarity ≥ 0.7 且 count ≥ 5 才觸發 summarization call。

## Cross-Cutting Theme 3: 「Proposal → Execution」之間需要顯式 governance gate

**支援筆記**: llm-agent-memory-governance (OCL + Governed Memory), 隱含於 hmem-recmem, memory-os

OCL 論文最直白：94% task success 隱藏 88% unsafe rate，proposal 與 execution 之間必須有 `πgate`/`πescalate`/`πaudit` 介入。**但這個模式在記憶系統內部也成立**：

- **H-MEM**：consolidation 是對 raw episode 的「proposal」，H-MEM 的 hierarchical routing 就是 gate（只讓 top-down 通過的記憶進 higher layer）
- **RecMem**：recurrence threshold θcount/θsim 就是 gate（不達標不允許進入 episodic layer）
- **MemoryOS**：heat > τ 才是 gate，控制 MTM→LPM 遷移
- **SAGE**：writer policy 的 reward signal 就是 gate——不該寫入的結構不會被寫
- **Governed Memory**：schema enforcement 是 gate的另一種形式，atomic facts 必須通過 coreference/self-containment/temporal anchoring 三個 quality gate

**模式**：所有系統在「資訊要進入某個層/結構/動作」之前都插了一個或多個 gate。**沒有 gate 的記憶系統在 2026-06 的文獻中已經不可見**。這是從「設計」轉向「治理」的訊號。

對應到 Hermes：`PolicyInterceptor` 在 OCL 層面（tool call pre-execution）已有雛形，**但 distillate pre-storage 沒有對應的 gate**。目前 distillate 是「LLM 蒸餾出來就寫入」——沒有 quality gate 沒有 schema enforcement。

**可行動下一步**:
在 `heartbeat_learning.py` 的 distillate write path 加三個 gate（直接挪用 Governed Memory 的 quality gate vocabulary）：
1. **Coreference gate**：新 distillate 中的代詞（它/這/那個）是否解析到具體 entity？沒解析的不寫入
2. **Self-containment gate**：distillate 獨立閱讀時是否語意完整？依賴外部 context 才能理解的（如「那個東西」）不寫入
3. **Temporal anchoring gate**：陳述是否標明時間（absolute 或 relative）？無時間標記的 universal claim 降級為「需驗證」flag，不直接寫入

這三個 gate 加起來估計 100 行 Python，且完全 deterministic（不需 LLM call），可作為 `PolicyInterceptor` 的 `πgate` component 對應到記憶層的版本。

## 總結：三個 theme 的交集

把三個 theme 疊起來：

| Theme | 針對的問題 | 在 Hermes 的對應位置 |
|-------|-----------|------------------|
| 1. 閉環 | distillate stale 沒人發現 | heartbeat_learning.py retrieval path |
| 2. Token budget | 每次 heartbeat 太貴 | heartbeat_learning.py trigger 條件 |
| 3. Pre-storage gate | distillate 品質無下限 | heartbeat_learning.py write path |

**共同點**：三個 theme 都在 `heartbeat_learning.py` 內，且都是「加 gate / 加 feedback / 加 batch」而非「換底層模型」。換言之，下一步不需要引入新架構——現有架構加 governance layer 即可。**WS-035 的 drift penalty 不該是新系統，應該是 heartbeat_learning.py 的三個 patch**。
