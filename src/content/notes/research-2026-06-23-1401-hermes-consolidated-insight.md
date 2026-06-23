---
_slug: research-2026-06-23-1401-hermes-consolidated-insight
_vault_path: research/2026-06-23-1401-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- governance
source: multi
created: '2026-06-23'
confidence: high
title: Reader-Writer 閉環 × Token 經濟學：2026-06-09 四篇記憶架構筆記的隱藏收斂
type: research
status: seedling
updated: '2026-06-23'
---

# Reader-Writer 閉環 × Token 經濟學：2026-06-09 四篇記憶架構筆記的隱藏收斂

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory.md
- 2026-06-09-memory-os-three-tier-hierarchical-memory.md
- 2026-06-09-sage-self-evolving-graph-memory-engine.md
- 2026-06-09-llm-agent-memory-governance-synthesis.md

四篇筆記表面都在談「AI agent 記憶架構」，但每一篇各自的結論都聚焦在細節設計（層數、trigger 條件、heat 公式）。把它們疊在一起才浮現兩個**跨論文**模式：reader-writer 反饋閉環是所有系統真正的 killer feature，而 token 成本才是推動架構選型的真正引擎。

## Cross-Cutting Theme 1: Reader-Writer 閉環是共同的 killer primitive

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

四篇筆記各自提出不同的「寫入條件」，但沒有一篇明確點出這些其實都是**同一個抽象模式的不同實例**：

| 系統 | Writer 觸發 | Reader 反饋信號 |
|------|------------|----------------|
| H-MEM | user approval/rebuttal | memory weight decay/grow |
| RecMem | recurrence count ≥ θcount | θsim cosine 過濾 |
| MemoryOS | heat score > τ | visit count + recency |
| SAGE | policy-based + reader failure | 圖結構補完信號（**顯式閉環**） |
| OCL | policy gate (πrole/πgate/πescalate/πaudit) | executed violations = 0 |
| Governed Memory | quality gate 通過 | LLM judge evidence completeness |

**非顯然觀察**：SAGE 是唯一把閉環**明確命名**為架構原語的系統（writer-reader self-evolution rounds）。但 OCL 的 `πaudit` log + `Valid Success Rate 12%→96%` 的躍升，本質就是 OCL 把「proposal 失敗率」當作 reader 反饋寫進下一輪 policy refinement。MemoryOS 的 heat score 衰退也是隱式的 reader→writer 信號。

換言之，**所有 2026 年提出的 production-grade 記憶系統都在悄悄實作同一件事：把讀取端的失效信號接回寫入端的決策**。Hermes 的 `heartbeat_learning.py` 目前**只寫不讀**——distillate 寫入後沒有任何機制把「這個 distillate 多久沒被引用、引用時 relevance score 多低」回饋給 distillation trigger。

**可行動下一步**:
1. 在 `heartbeat_learning.py` 新增 `read_signal_collector.py` 子模組：每次 task context matching 引用某 distillate 時，記錄 `(timestamp, relevance_score, query_topic)` 到 `distillate_usage.db`
2. 設定 7 天 rolling window：若某 distillate 的 `usage_count == 0` 且 `age > 30d`，標記為 `potentially_stale`，下次 heartbeat 觸發時**主動蒸餾替代版本**（對齊 SAGE 的 self-evolution round）
3. 借鑒 OCL 的 `πaudit`：每次 drift penalty 決策寫進 `governance_audit.log`，未來可以用 H-MEM 式的 user approval/rebuttal 動態調整 heat 公式的權重（而非 hard-code α/β/γ）
4. **量化目標**：對齊 BEAM benchmark 的 `contradiction_resolution` metric，下一輪 heartbeat 後跑一次 `distillate_recall_at_30d` 測量 stale 比例

## Cross-Cutting Theme 2: Token 經濟學才是架構選型的真正 driver

**支援筆記**: 全部四篇

四篇筆記都列出 LoCoMo 上的 F1 數字，但 F1 差異其實是**次要訊號**——真正決定 production 採用與否的是**單位 query 的 token/compute 成本**：

- **H-MEM**: flat retrieval O(a·10^6·D) 100ms+ vs hierarchical O((a+k·300)·D) <100ms——贏在**檢索成本線性化**
- **RecMem**: 87% token 節省 vs Mem0/A-Mem/MemoryOS——贏在**避免 eager LLM consolidation**
- **MemoryOS**: 4.9 LLM calls/query vs A-Mem* 13.0（68% 節省）——贏在**保守的 STM 設計（7 pages）**
- **Governed Memory**: 50% token 削減 via progressive context delivery——贏在**delta-only injection**
- **OCL**: 38.75s → 18.51s avg latency——贏在**early termination via deterministic replanning**

**非顯然觀察**：F1 最高的系統不一定是 cost-adjusted 最佳者。MemoryOS 4.9 calls 拿 36.23 F1，換算 ~7.4 F1 per call；A-Mem* 13.0 calls 拿 26.55 F1，換算 ~2.0 F1 per call。**MemoryOS 的單位成本效益是 A-Mem* 的 3.7 倍**。但這個 ratio 在論文中從未被明確計算。

對 Hermes 的直接含意：每次設計決策（要不要加新的 LLM call？要不要做 reflection？要不要蒸餾新 distillate？）都應該以**token/$** 而非 F1 為度量單位評估。Hermes 目前沒有 token 預算的概念——每次 heartbeat 不論 distillate 數量都跑完整 LLM pass。

**可行動下一步**:
1. 為 `heartbeat_learning.py` 加 `token_budget.py` config：預設每輪 heartbeat 限制 50K tokens，啟發式：`(num_distillates_to_refresh) × (avg_summarization_cost)` ≤ budget，超過就採 MemoryOS 式**分頁批次處理**（只 refresh 熱度最高的 N 個，其餘延後）
2. 對齊 RecMem 的 `subconscious store` 概念：新增 `raw_interaction_buffer.py`，所有 incoming task context 先存 raw embedding **不** 觸發 LLM consolidation，等到 recurrence ≥ 3 次才升級到 distillate 層
3. 對齊 Governed Memory 的 progressive delivery：task context matching 改為 delta-only，只 inject「自上次 reference 以來新增的 distillate」，不重發整個 knowledge base
4. 建立 `cost_efficiency_dashboard.md`，每月記錄 `(f1_per_token, latency_per_query, calls_per_query)` 三個 metric，追蹤 Hermes 自身的「單位成本效益」是否隨時間改善

## Meta-Insight：四篇筆記的「建議」其實互相覆寫

**支援筆記**: hmem-recmem, memory-os, sage（三篇都對 WS-035 drift penalty 提出建議）

hmem-recmem 建議加 `recurrence check`、memory-os 建議加 `heat score`、sage 建議加 `reader failure signal`——但**三者本質是同一個函數的三個 feature**：

```
distillate_score(distillate, now) =
    α · recency_decay(now, last_referenced)
  + β · usage_count(t_30d)
  + γ · mean_relevance_score(t_30d)
  + δ · contradiction_penalty(conflicts)
```

當前 `heartbeat_learning.py` 的 drift penalty 是純時間衰減（只 `α` 項）。**三篇筆記實際上已經把 `β` `γ` `δ` 的設計藍圖各自給了一份**——缺的是把它們拼成單一 score 函數，並量化每個權重的 ablation 結果。

**可行動下一步**:
1. 把三個筆記的 heat 公式整理成 `drift_penalty_unified.md` 提案，明確標出哪些權重來自哪篇
2. 在 Hermes vault 開一個 `99-Projects/ws-035-drift-penalty/` 資料夾，把這四篇筆記的 per-source insight + 三方 heat 公式 + 統一公式作為 RFC-001 草稿
3. 排程下一次 heartbeat 跑 ablation：固定其他權重，逐一 sweep α/β/γ/δ，測量 LoCoMo-style task 表現
