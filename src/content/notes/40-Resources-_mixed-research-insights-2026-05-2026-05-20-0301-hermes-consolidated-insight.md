---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-20-0301-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-20-0301-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-20'
confidence: medium
title: Aegis Memory 啟發：ACE Loop 閉環 + Contradiction Graph 取代靜態 ISSUES.md
updated: '2026-06-15'
type: research
status: budding
---

# Aegis Memory 啟發：ACE Loop 閉環 + Contradiction Graph 取代靜態 ISSUES.md

**消化筆記**: 2026-05-20-aegis-memory-deep-dive, 2026-05-20-agent-memory-taxonomy-survey

（本篇是單一筆記的深度分析，但有另一篇 `agent-memory-taxonomy-survey` 提供了 broader context。Aegis 的 three non-obvious 設計與 Hermes 現有架構的 gap 有明確的 cross-session 呼應。）

## Cross-Cutting Theme 1: ACE Loop 閉環是 Hermes heartbeat_learning 的缺失環節

**支援筆記**: 2026-05-20-aegis-memory-deep-dive, heartbeat_learning.py

**分析**:

Aegis 的 ACE loop (`Generation → Execution → Reflection → Curation`) 中，**Execution 層**是 Hermes 完全沒有的一環：

```
成功時: 所有被使用的 memories → auto-vote helpful
失敗時: 所有被使用的 memories → vote harmful + 建立 reflection memory（含 error context）
```

Hermes 的 `heartbeat_learning.py` 只做 pattern extraction，不追蹤「這些 memories 有沒有真的解決問題」。結果是：

- 成功案例的 context 永遠不被 reinforce
- 失敗案例的 error context 散落在 logs 但不成為可查詢的 memory

**非顯然之處**：failure-triggered reflection memory 不是「錯誤筆記」，而是攜帶 error context 的 typed memory，可被未來查詢召回。相當於每次失敗都自動寫了一次 structured pre-mortem，並與用到爛的 memory 連結。這讓記憶系統從「被動儲存」變成「主動從後果學習」。

**可行動下一步**: 
1. 在 `heartbeat_learning.py` 加入 `task_outcome` 參數（`success` / `failure`）
2. 失敗時：query 最近 N 個相關 memory IDs → 對每個 vote `not_helpful` + 建立新的 `reflection` type memory，含 `error_type`、`context`、`task_id`
3. 成功時：對所有被召回的 memories auto-vote `helpful`（需要先實作 memory recall logging）

---

## Cross-Cutting Theme 2: Typed Contradiction Edge 讓 ISSUES.md 從靜態清單變成可稽核的 Graph

**支援筆記**: 2026-05-20-aegis-memory-deep-dive, ISSUES.md

**分析**:

Hermes 的 ISSUES.md 是靜態文字檔，沒有結構化的矛盾檢測。當新的變更引入時：
- 新 issue 可能與舊 root cause 分析衝突
- 沒有人會系統性地比對
- 兩個人解決同一個 bug 可能用完全不同的 root cause 假設

Aegis 的 typed contradiction edge 設計：
```
Memory A (root cause: network timeout)
  ↕ contradicts (confidence: 0.7, rationale: "latency < 50ms, not network")
Memory B (root cause: DB lock contention)
```

好處：
- 矛盾是可查詢的 graph，不是散落在 comment 裡
- confidence 分數讓系統知道哪些矛盾是高可信的、值得優先 resolve
- 解決 contradiction 時留下 audit trail（哪些假設被修正了）

**非顯然之處**：這不只是 ISSUES.md 的格式問題，而是「假設的版本控制」。每次 root cause 分析都是一個 versioned assumption，矛盾 = 同一個假設的兩個版本打架。

**可行動下一步**:
1. 審計現有 ISSUES.md，找出兩條以上 entry 的 root cause 互相排斥的情況 → 建立 contradiction pairs
2. 建立簡單的 JSON/graph 結構 (`~/.hermes/knowledge/assumption_contradictions.json`) 儲存這些 pairs
3. 設計一個 `check_contradiction(new_issue, existing_issues)` 工具，在新的 known issue 被寫入前呼叫

---

## Cross-Cutting Theme 3（Low-confidence）: RRF Retrieval 是 Hermes FTS5 的 Missing Piece

**支援筆記**: 2026-05-20-aegis-memory-deep-dive

**分析**:

Aegis 使用 `pgvector + tsvector + RRF` 混合檢索。RRF（Reciprocal Rank Fusion）是一個 zero-parameter 的 rank aggregation：

```
RRF_score(d) = Σ 1/(k + rank_i(d))
```

Hermes 已有 FTS5（sparse），如果多加了 vector search（dense），RRF 可以融合兩者，特別是對 entity + keyword 混合查詢（如「找 skills/ 下處理 async 錯誤的程式碼」）有效。

**非顯然之處**：RRF 比單純串接 BM25 + vector 的效果好，且實作只有 10 行。這個不是「新系統」，是對現有 FTS5 的微幅升級。

**可行動下一步**:
1. 實驗：對同一個 query，分別跑 FTS5 排名和一個 mock vector rank，用 RRF 公式合併結果
2. 如果效果明確，在 `fts5_index.py` 加入 RRF 模式開關
