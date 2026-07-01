---
_slug: research-2026-07-01-1901-hermes-consolidated-insight
_vault_path: research/2026-07-01-1901-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- drift-penalty
source: multi
created: '2026-07-01'
confidence: high
title: 2026-06-09 Memory Architecture Cluster — Drift Penalty 的合成模式
type: research
status: seedling
updated: '2026-07-01'
---

# 2026-06-09 Memory Architecture Cluster — Drift Penalty 的合成模式

**消化筆記**:
- 2026-06-09-llm-agent-memory-governance-synthesis
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine

四篇 2026-06-09 同日產出的 LLM agent 記憶架構探索。把 4 篇並排後浮現 3 個單篇各自沒說清楚的 pattern，全部指向 WS-035 drift penalty 該怎麼落地。

## Cross-Cutting Theme 1: Drift Detection 至少需要 4 種信號的合成，單一機制都不夠

**支援筆記**: governance-synthesis, H-MEM/RecMem, MemoryOS, SAGE

每篇提出**不同**的 staleness detection 機制，且都承認自己那個機制是 partial：

| 來源 | 機制 | 失效場景 |
|------|------|----------|
| governance-synthesis（2605.06716） | event-driven invalidation（environment 事實改變觸發） | 沒事實改變但知識已過時怎麼辦？ |
| RecMem | recurrence count ≥ θcount | 第一次出現的 concept 永遠不會被 consolidate，會誤刪 |
| MemoryOS | heat score = α·N_visit + β·L_interaction + γ·R_recency | 冷啟動的新 distillate 熱度 = 0，直接被視為 stale |
| SAGE | reader-failure signal（找不到證據→回饋 writer） | 沒人查的 distillate 沒有 failure signal，安靜腐爛 |

**分析**：四篇的「when is memory stale?」答案**互補而非競爭**。把它們疊起來才是完整的：
- **Recurrence** 處理「重複出現 vs 從未出現」
- **Heat** 處理「被使用頻率」
- **Event-driven** 處理「外部事實改變」
- **Reader failure** 處理「查詢時找不到」（主動信號）

WS-035 目前只實現 time-based decay。drift penalty 必須是這 4 個維度的加權合成。

**可行動下一步**:
- 在 `heartbeat_learning.py` 的 distillate metadata 加上 4 個欄位：`recurrence_count`, `visit_heat`, `last_event_invalidation_ts`, `reader_failure_count`
- 寫一個 `compute_drift_score(distillate)` function：`score = w1·(1/recurrence) + w2·(1/heat) + w3·time_since_event + w4·failure_count`
- 從現有 4 個維度各自的 threshold 開始 tune（RecMem: θcount=5；MemoryOS: τ=5；SAGE: 2 self-evolution rounds = convergence）

---

## Cross-Cutting Theme 2: Architecture Separation 是 production-grade 的必要條件 — 但分離的「層數」沒有共識

**支援筆記**: governance-synthesis（OCL proposal/execution）、MemoryOS（STM/MTM/LPM 三層）、H-MEM（4 層 hierarchical routing）、SAGE（writer/reader）

四篇獨立收斂到同一個架構原則：**寫入與讀取（或提案與執行、或 STM 與 LPM）必須有明確的 architectural boundary**。但 boundary 切幾刀各家不同：

- OCL: 1 boundary（proposal ↔ execution）
- MemoryOS: 2 boundaries（STM↔MTM, MTM↔LPM）
- H-MEM: 3 boundaries（Domain↔Category↔MemoryTrace↔Episode，4 層 = 3 boundaries）
- SAGE: 1 boundary 但內部複雜（writer↔reader + self-evolution loop）

**分析**：boundary 數量對應到「consolidation trigger 的數量」。MemoryOS 有 2 個 trigger（FIFO + heat），H-MEM 有 3 個（user approval / rebuttal / implicit decay），SAGE 只有 1 個 trigger 但通過 self-evolution rounds 累積效果。

對 Hermes 的含意：Talos governance 的 `PolicyInterceptor` 不只是「在 tool call 前插一個 gate」（OCL 視角），而是**整個 distillation pipeline 需要 N 個明確的 trigger points**，每個 trigger 對應不同的 governance policy。

**可行動下一步**:
- 盤點 Hermes/Talos 目前有幾個「phase boundary」：LLM generation → tool call execution（OCL）、distillate 入庫 → retrieval（governance）、retrieval → context injection（governed memory）
- 給每個 boundary 寫一個 policy module（不是 scattered checks），至少 3 個：`gen_to_exec_policy.py`、`distillate_gate_policy.py`、`retrieval_filter_policy.py`
- MemoryOS 的 2-boundary 設計是最低可接受起點；OCL 的 1-boundary 不夠

---

## Cross-Cutting Theme 3: 4 篇 60%+ 篇幅在談「何時 consolidate」，不到 20% 在談「寫什麼」

**支援筆記**: 全部 4 篇

**分析**：這是 meta-observation。四篇 paper 的章節比重都偏向「trigger conditions」「eviction policies」「migration gates」，很少談 writing format 或 content representation。意謂在 memory architecture 領域，**trigger 是公認的難題，representation 是已解決的問題**。

但 Hermes 的 `heartbeat_learning.py` 反過來：花大量精力在 distillate 格式、metadata schema、embedding choice，trigger 只有簡單的「每次 heartbeat 就跑一次」。

WS-035 drift penalty 的設計重心應該是 trigger logic（何時標記 stale、何時 consolidate、何時蒸餾新版），不是 distillate format。

**可行動下一步**:
- 把 `heartbeat_learning.py` 的 trigger 區塊獨立成 `distillation_trigger.py` module
- 在新 module 內 implement 上面 Theme 1 的 4 維度 drift score
- distillate format 維持現狀（已解決的問題不值得再投資）
- 設 threshold：drift score > X → 觸發新的 distillation round（不是直接刪除，是**先標記、再等 recurrence 或 reader failure 確認**才刪）

---

## 共同未追蹤的 Lead（cross-cutting）

4 篇都提到但沒時間追：
- **SCM (Self-Controlled Memory, Wang et al. 2025)** — 出現在 MemoryOS 比較表 + SAGE leads，但 vault 無記錄
- **Zep Temporal Knowledge Graph** — RecMem taxonomy 提到，graph-based consolidation 的另一條路線
- **LongMemEval-S benchmark**（500 conversations, 115k avg tokens）— RecMem 用的第二個 benchmark，比 LoCoMo 更 stress test

**可行動下一步**: 排程一個 exploration 同時 cover 這 3 個（它們在 consolidation trigger 設計上屬於同一支線）。
