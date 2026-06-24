---
_slug: research-2026-06-25-0601-hermes-consolidated-insight
_vault_path: research/2026-06-25-0601-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-governance
- ws-035
- drift-penalty
source: multi
created: '2026-06-25'
confidence: high
title: 記憶生命週期缺少 Reader→Writer 反饋迴路；Hermes 必須以多訊號 staleness + 分層 router 統一處理
type: research
status: seedling
updated: '2026-06-25'
---

# 記憶生命週期缺少 Reader→Writer 反饋迴路；Hermes 必須以多訊號 staleness + 分層 router 統一處理

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 的探索各自觸及記憶系統設計的一個面向（H-MEM/RecMem 的觸發條件、MemoryOS 的熱度驅動、SAGE 的 self-evolution、Governance 的 schema 與 pre-execution gate）。它們合在一起顯露一個共同結構性盲點：**記憶/動作生命週期缺乏 reader→writer 的反饋閉環**，且每一篇都各自選了不同訊號當作唯一觸發器——而 Hermes 的 WS-035 正面對這個問題。

## Cross-Cutting Theme 1: 多訊號 staleness 函數是唯一出路（不是「選一個最佳觸發器」）

**支援筆記**: hmem-recmem, memory-os, sage, memory-governance-synthesis

四篇論文在「何時標記記憶為 stale / 何時 consolidation / 何時蒸餾」這個問題上各自提出不同的觸發訊號：

| 來源 | 主張的觸發器 | 形式 |
|------|------------|------|
| H-MEM | user feedback（approval/rebuttal） | event-driven weight |
| RecMem | recurrence count（θcount≥5, θsim≥0.7） | frequency-driven |
| MemoryOS | heat score（α·N_visit + β·L_interaction + γ·R_recency） | composite |
| SAGE | reader failure signal（圖中找不到證據） | failure-driven |
| Storage→Experience survey | event-driven invalidation（條件性失效） | semantic-driven |

**單篇看不出來的模式**：這些訊號**互補**而非互斥——H-MEM 自己承認單靠 user feedback 在 single-hop QA 上只贏 +1.7 F1；RecMem 的 recurrence 對低頻但高價值資訊（用戶偏好）會誤判；MemoryOS 的 heat score 對「從未被檢索但被 reader 直接詢問」的記憶會蒸發掉；SAGE 的 reader failure signal 無法處理「reader 找到舊版但新版本已存在」的情況。

Hermes 的 heartbeat_learning.py 目前是純時間衰減（half-life=38d），這是所有觸發器中**最弱**的一個——四篇論文的 implicit 共識是 time decay 必須被取代，但不能被**任一單一**訊號取代。

**可行動下一步**：
1. 在 `heartbeat_learning.py` 的 distillate metadata 中加四個獨立計數欄：`recurrence_count`、`visit_count`、`user_feedback_score`、`contradiction_count`（先不動行為，只收集）
2. 寫一個 `drift_score(distillate) = w1·(1-recurrence_norm) + w2·(1-visit_norm) + w3·contradiction_count + w4·time_decay` 的 prototype function
3. 兩週後看真實分佈決定 w 值

**信心**: high（四篇獨立交叉驗證）

## Cross-Cutting Theme 2: Reader→Writer 反饋迴路是治理基礎設施，而非優化項

**支援筆記**: memory-governance-synthesis (Governed Memory "Silent quality degradation without feedback loops"), sage (writer-reader self-evolution loop), memory-os (heat score 本身就是 reader→writer signal), hmem-recmem (H-MEM 的 user feedback 與 RecMem 的 recurrence 都是 reader→writer signal)

Governed Memory 論文直接點名：「**Silent quality degradation without feedback loops**」是五大 structural challenges 之一。SAGE 量化了閉環的價值：two self-evolution rounds 達到 multi-hop QA 最佳。MemoryOS 的 heat score 表面是「被動計數」，本質是 reader（檢索）告訴 writer（distillation）什麼值得保留。H-MEM 的 user rebuttal → memory decay 是同一回事。

**單篇看不出來的模式**：Hermes 已經在**三個獨立位置**缺少這個迴路：
1. **distillate 層**：`heartbeat_learning.py` 的 writer（distillation）沒有 reader（task context）回報「找不到證據」的信號
2. **skill 路由層**：技能被觸發/不被觸發的訊號沒有回流到技能歸類器
3. **tool governance 層**（OCL 對應）：proposal→execution 中間沒有 reader（policy engine）回報「這個 action 在過往失敗率太高」

這三層本質上是**同一個閉環的三個投影**。

**可行動下一步**：
1. 定義一個 `feedback_signal` 的標準 schema（`{source, target, signal_type, timestamp, weight}`），先在 distillate 層實作
2. 觀察兩週後，把 skill 路由的「未觸發」事件也寫入同一個 schema
3. 最終目標是 `audit_cron.py` 能用這個 schema 跨層追蹤「reader 失敗率」

**信心**: high（三篇直接命名 + 一篇 implicit 支援）

## Cross-Cutting Theme 3: Token 成本是 binding constraint，每個 LLM call 需要 router

**支援筆記**: hmem-recmem (87% reduction vs Mem0/A-Mem/MemoryOS), memory-os (3,874 tokens/query vs MemGPT 16,977), memory-governance-synthesis (Governed Memory 50% via progressive delivery, OCL 38.75s→18.51s)

四篇都量化了 token/latency 成本：
- RecMem：eager consolidation → triggered consolidation，**87% reduction**
- MemoryOS：MemGPT 16,977 → MemoryOS 3,874 tokens/query（**77% reduction**），13.0 → 4.9 LLM calls（**62% reduction**）
- Governed Memory：Progressive Context Delivery 砍 50% context token
- OCL：5.36 → 2.58 rounds，38.75s → 18.51s latency（**52% reduction**）

**單篇看不出來的模式**：所有削減來自**同一個機制**——在 LLM call 之前加一道 cheap 的 pre-filter。RecMem 用 cosine+threshold、MemoryOS 用 heat score、Governed Memory 用 embedding similarity、OCL 用 deterministic rules。這是 tiered routing 的具體實例。

Hermes 的 `heartbeat_learning.py` 每次 distillation 都是「無條件 LLM call」——這正是四篇論文共同的「naive baseline」。

**可行動下一步**：
1. 在 distillation 之前加一道 cosine similarity gate：如果新 trajectory 與既有 distillate 的 max similarity > 0.85，跳過 LLM distillation（直接 increment recurrence count）
2. 預期削減：根據 RecMem 數據保守估計 30-50% LLM call reduction
3. 同步在 `cost_aggregator.py` 加 metric 追蹤，避免削減以品質為代價

**信心**: high（四篇全部量化驗證）

---

## 反直覺發現

四篇論文**一致**指向「MemoryOS 的 heat score 是當前最完整的 staleness 函數原型」——它已經把 recurrence（N_visit 涵蓋）、recency（R_recency 顯式）、participation（L_interaction）三個維度組合起來。Hermes 與其從零設計 WS-035 drift penalty 的多訊號公式，不如**直接用 MemoryOS 的 heat score 公式**作為 baseline，然後加 H-MEM 的 user feedback 維度與 SAGE 的 reader failure 維度。這比從頭設計更穩健——MemoryOS 已在 LoCoMo 達到 SOTA（Single-Hop 35.27, Multi-Hop 41.15, Temporal 20.02）。

## 觀察限制

- 這四篇都是 2026-06-09 當天連續探索的（chain of `延續自` links），可能有 selection bias：hermes 那天選定 memory governance 主題後就連續 fetch 該主題相關論文
- 沒有 cross-domain 驗證（例如 hardware 控制系統的 staleness 函數、傳統 DB 的 vacuum 策略是否同形）
- MemoryOS 的 heat score 公式有 α/β/γ/τ 四個超參數，論文中是 LoCoMo-tuned，移植到 Hermes 的 session/learning 語境需要重新 sweep
