---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-21-0800-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-21-0800-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-21'
confidence: high
title: 記憶系統設計的兩個核心對立：失敗重於成功、LLM 應退出 CRUD
updated: '2026-06-15'
type: research
status: budding
---

# 記憶系統設計的兩個核心對立：失敗重於成功、LLM 應退出 CRUD

**消化筆記**: 2026-05-19-agent-memory-architecture, 2026-05-20-agent-memory-taxonomy-survey, 2026-05-20-aegis-memory-deep-dive, 2026-05-20-llm-agent-memory-biological-decay, 2026-05-20-r2-mem-reflective-experience-memory-search

（摘要）五篇記憶系統研究筆記揭示兩個 cross-cutting pattern：一是多系統independently收敛到「失敗案例比成功案例更有訓練價值」；二是「critical path 上應移除 LLM」的架構共識。

---

## Cross-Cutting Theme 1: 失敗重於成功 — 低質量經驗的反直覺收斂

**支援筆記**: 2026-05-20-llm-agent-memory-biological-decay, 2026-05-20-aegis-memory-deep-dive, 2026-05-20-r2-mem-reflective-experience-memory-search

### 獨立來源的收斂

三個系統用完全不同切入點，卻同時指向同一結論：

1. **YourMemory (decay)**: category-specific half-life 中，`failure` ~11天是所有類別中最短——失敗經驗會快速衰減，除非被主动强化。這等於是「失敗需要更多recency才能被記住」，暗示失敗本身是稀有信號。

2. **Aegis (ACE loop)**: completion 回傳 `success=True` → 自動在所有用過的 memories 上 vote `helpful`；失敗 → vote `harmful` + 建立 reflection memory（含 error context）。失敗時主動建立 reflection memory，等於失敗是 reflection 的觸發器、成功不是。

3. **R²-Mem (ablation study)**: Table 4 發現「只用低質量經驗 > 只用高質量經驗」。作者的解釋：高質量行為本來就有效，不需要引導；低質量行為才是需要被糾正的。**這是 end-to-end ablation 驗證，不是 conjecture。**

### Hermes 的映照

Hermes 的 `heartbeat_learning.py` 目前是中性統計——記錄所有 pattern，沒有區分成功/失敗維度。ISSUES.md 也是被動的（問題出現後才 suppress），而不是主動驅動 reflection。

### 可行動下一步

在 `heartbeat_learning.py` 加入第一層 failure-weighted scoring：每個 extracted pattern 附帶 `failure_weight`（從 `heartbeat_state.json` 的 severity 軌跡計算），failure-weight 高的 pattern 在 consolidation 時優先轉為反思筆記，而不是均勻對待。

---

## Cross-Cutting Theme 2: LLM 應退出 CRUD — No-LLM in hot path 的架構共識

**支援筆記**: 2026-05-20-llm-agent-memory-biological-decay, 2026-05-19-agent-memory-architecture

### 兩個獨立的 LLM-free 宣言

1. **Mnemora (2026-05-19)**: 「no LLM in CRUD path」——明確宣稱建立/讀取/更新/刪除記憶時不經過 LLM。用簡單 DB query 回答「你上次處理過這個專案嗎？」這類問題。

2. **YourMemory (2026-05-20)**: 「No-LLM ask」——trivial factual query 直接回答，零 token cost、零延遲、零隱私風險。把 trivial 和 complex 分離，LRU path 完全不碰 LLM。

### Hermes 的現況

目前的 `memory-consolidator` pipeline：extract（LLM）→ distill（LLM）→ brief（LLM）。三步都在 LLM hot path 上。即使是「簡單查詢上次心跳時間」也要走完整個 chain。

### 可行動下一步

在 `memory-consolidator` 的 README 或架構文件中識別「LLM-free query」的介面：定義哪些查詢（最近 session 狀態、已知錯誤指紋查詢、某路徑的最近修改時間）可以繞過 consolidation pipeline，直接從 `heartbeat_state.json` 或 FTS5 返回。

---

## 附：兩個 theme 的交匯點

失敗案例 + No-LLM CRUD 的交匯點是 **ISSUES.md 的查詢效率**：當 Talos 需要知道「這個錯誤指紋是否已知」，目前要走 LLM context（或手動翻 ISSUES.md）。如果把 ISSUES.md 轉為結構化 DB query（error_fingerprint → status + suppression_count），就能在 constant time 內完成 failure lookup，同時讓 failure pattern 在查詢時自然積累 access count，驅動 learned forgetting。

這條線把 Theme 1（failure-weighted scoring）和 Theme 2（LLM-free query）串成一個具體的實作方向。