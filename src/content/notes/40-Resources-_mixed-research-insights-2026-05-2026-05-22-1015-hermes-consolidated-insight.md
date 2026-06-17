---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-1015-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-1015-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory
- retrieval
- heartbeat
source: multi
created: '2026-05-25'
confidence: medium
title: 評分迴路斷裂：rubric 打了分卻沒人去讀
updated: '2026-06-15'
type: research
status: budding
---

# 評分迴路斷裂：rubric 打了分卻沒人去讀

**消化筆記**: 2026-05-21-pageindex-chatindex-in-context-index, 2026-05-23-memr3-reflective-reasoning-for-memory-retrieval, 2026-05-23-exploration-memori-retrieval, 2026-05-20-探索-R²-Mem---Reflective-Experience-for-Memory-Search

（摘要）三個獨立的 retrieval/learning 系統揭示同一個実装缺口：分數被算出來了，但觸發閾值迴路沒接上。rubric scoring 和 evidence-gap tracking 是兩個名字不同、但解決同一類問題的設計——都試圖回答「什麼時候才算夠好，可以 advance 到下一層」。Hermes 兩者都有，但都沒關起來。

---

## Cross-Cutting Theme 1: 評分結果沒有人 consumption——rubric 打了分，action layer 完全沒在看

**支援筆記**: 2026-05-20-探索-R²-Mem---Reflective-Experience-for-Memory-Search, 2026-05-23-memr3-reflective-reasoning-for-memory-retrieval, 2026-05-21-pageindex-chatindex-in-context-index

### 分析

三篇筆記各自描述了一個「評估 → 決策」的 closed loop：

| 系統 | 評估層 | 決策層 | 迴路封閉？ |
|------|--------|--------|-----------|
| **R²-Mem** | Rubric-guided Evaluator（8維評分，0-3）| `K_high` → 蒸餾成 good experience；`K_low` → 蒸餾成 bad experience | ✅ 直接寫 experience bank |
| **MemR³** | Evidence-Gap Tracker（維護 E=已知, G=缺口集合） | `G=∅` 才允許 answer，否則 continue retrieve/reflect | ✅ Router 吃 E/G 狀態做決策 |
| **PageIndex** | LLM 推論「這個 section 有沒有答案」| YES → return summary；NO → 再選一個 section | ✅ LLM 自己根據推理結果 navigate |
| **Hermes heartbeat** | `score_actions_batch()`（8維評分）| ？？？ | ❌ 結果只進 log，不驅動任何 action |

`heartbeat_learning.py` 的 R²-Mem rubric 章節（line 293-317）已經實作：每個 heartbeat cycle 的 planning/reflection 各維度分數都算出來了，`low_q_count` 統計了低品質訊號，priority 也用 reflection score 調整過。但這些數字只寫進 `heartbeat_patterns.json`，沒有任何消費端。

### 非顯然的連結

R²-Mem 的 IF-THEN experience pairs 和 MemR³ 的 evidence-gap tracker 本質上是同一個問題的兩個名字：**什麼信號觸發 advance 行為？** R²-Mem 回答「評分 > 某閾值 → 蒸餾」，MemR³ 回答「缺口集合空了 → answer」。兩者都不是簡單的「達到 N 筆就觸發」，而是「到達某種內部狀態」才行動。Hermes 的 heartbeat rubric 分數正好是這個內部狀態——但迴路在這裡斷了，評分結果只是被存起來，沒有任何東西根據它做决策。

### 可行動下一步

在 `heartbeat_v2.py` 的 action loop 或 `memory/consolidation/` 裡新增一個 rubric-consumer：在每個 heartbeat cycle 結尾讀取 `heartbeat_patterns.json` 的 rubric summary，根據分數驅動具體 action：

1. 若 `avg_planning < 1.5`（rolling 7-day window）→ 抑制 proactive research schedule，下個 cycle 只做 minimum viable heartbeat
2. 若 `avg_reflection < 1.5` → 降低 ISSUES.md suppression aggressiveness（讓更多 issue 浮上來，強迫 explicit resolution 而非 implicit suppression）
3. 若 `low_q_count > 3` 且持續 3 個 cycle → 觸發 `memory-consolidator` 的 proactive extraction（不等 cron，強迫馬上 distill）

這三條把「評分」變成「行為門閥」，而不是純統計數字。

---

## Cross-Cutting Theme 2: Retrieval 沒有雙層排序——semantic match + re-rank 該綁在一起

**支援筆記**: 2026-05-23-exploration-memori-retrieval, 2026-05-21-pageindex-chatindex-in-context-index, 2026-05-23-memr3-reflective-reasoning-for-memory-retrieval

### 分析

三篇筆記合起來揭示了 Hermes vault retrieval 的一個具體缺口：

**PageIndex 的 claim**：「semantic similarity 抓不到時序相關性和引用關係」。Vector RAG 的 cosine similarity 只衡量「語意像不像」，不衡量「這是不是我需要的時序上下文」。Fed 年報案例：主 section 報增量，Appendix G 報總值——兩者語意都不近「deferred assets 總值」這個 query，但引用關係（77頁說「see Appendix G」）才是正確答案的真正線索。

**Memori 的實作細節**：「fetch → cosine similarity → BM25 re-rank → RankedFact」。這個 pipeline 在 Memori Labs 是 production 的，意思是：向量相似度只是候選集生成，真正決定順序的是 BM25 re-rank 層。`dynamic_candidate_limit` 確保候選池足夠大（10x floor 50）再 re-rank，避免「候選太少導致 recall 崩潰」的問題。

**MemR³ 的 closed-loop 概念**：「每次 retrieve 不是獨立的，是在前一次 retrieval 的基礎上問『還缺什麼』」。這讓 retrieval 變成一個引導式的探索，而不是一次性的 similarity search。

三個加起来：Hermes vault 的 `/lookup` 目前只有第一層（向量相似度），缺少後兩層。

### 非顯然的連結

PageIndex 和 Memori 描述的問題相同但切入角度不同：PageIndex 說「LLM reasoning 可以繞過 similarity limitation」（在 context 內推理），Memori 說「BM25 re-rank 可以繞過 similarity limitation」（在 retrieval 層修復）。兩者並不互斥——最好的架構是：BM25 re-rank 確保 recall，PageIndex-style in-context tree 確保 routing 精確。Hermes 目前兩者都沒有，vault lookup 是啞的 cosine similarity。

### 可行動下一步

在 vault lookup pipeline（`hermes-fts5-doc-index` 或其後續）加入兩階段：

1. **BM25 re-rank step**：用 `rank_bm25` library（Python）对 FTS5 initial result 再做一次 keyword-level re-rank。具體：initial query 結果取 10x candidate（floor=50），餵給 BM25，取最終 top-K
2. **MemR³-style sub-query tracking**：在 vault lookup response 加入 `evidence_gaps[]` 欄位——每次 lookup 不只返回結果，還附帶「哪些 query aspect 還沒被滿足」的診斷，供上層（consolidation 或 briefing）決定是否需要 follow-up query

第一步是純工程增量，無需 LLM call。第二步需要修改 vault lookup 的 prompt/template，是medium cost 的變更。