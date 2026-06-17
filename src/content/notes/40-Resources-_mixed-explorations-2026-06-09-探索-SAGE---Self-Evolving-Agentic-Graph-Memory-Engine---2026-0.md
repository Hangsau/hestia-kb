---
_slug: 40-Resources-_mixed-explorations-2026-06-09-探索-SAGE---Self-Evolving-Agentic-Graph-Memory-Engine---2026-0
_vault_path: 40-Resources/_mixed/explorations/2026-06-09-探索-SAGE---Self-Evolving-Agentic-Graph-Memory-Engine---2026-0.md
title: 探索：SAGE — Self-Evolving Agentic Graph-Memory Engine — 2026-06-09
date: 2026-06-09
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- distillate
- evolution
- graph
- heartbeat
- learning
- memory
- reader
- sage
- self
- writer
created: '2026-06-09'
updated: '2026-06-15'
status: budding
---

# 探索：SAGE — Self-Evolving Agentic Graph-Memory Engine — 2026-06-09

**延續自**: [[2026-06-09-memory-os-three-tier-hierarchical-memory]]
**日期**: 2026-06-09 | **來源**: SAGE (Wang et al., arxiv:2605.12061, NeurIPS 2026) | **類型**: Exploration

## 核心：Graph Memory 作為動態工作基底

SAGE 的核心洞察：**現有 GraphRAG 將圖結構當靜態檢索中介，SAGE 將圖記憶當動態長期記憶 substrate**。圖不僅在檢索前建構、檢索後搜尋——它是記憶書寫、讀取、更正、自我改進的工作基底。

**三個核心挑戰**：
1. **全局聯想閱讀**：從稀疏、部分、間接線索重建完整推理鏈（不是只檢索語意相似的文字片段）
2. **結構化使用學習**：圖結構不應只是固定索引——hubs 和 bridges 的角色需學習而非啟發式擴展
3. **記憶自我演化**：讀取失敗信號反饋給寫入，形成閉環——更好的閱讀暴露寫入缺陷，更好的寫入使未來閱讀更精準

---

## 架構解析

### Memory Writer — Policy-based Writing

將記憶寫入建模為序列決策 policy：
- **State**: `(q, D, G_{t-1}, D^{proc}_{t-1})` — 查詢、文檔、當前圖、已處理文檔
- **Action**: `(u, r, v, source)` —實體-關係-實體三元組 +來源錨點
- **Reward**: 來自下游記憶使用的反饋信號

### Memory Reader — Graph Foundation Model (GFM)

基於 Graph Foundation Model 的讀取器，執行：
- **Cognition-inspired Structured Query Planning**：從查詢中提取實體和關係規劃傳播起點
- **Soft Addressing + Pre-activation**：軟定位查詢相關實體
- **Synapse-inspired Structurally Conditioned Associative Propagation**：通過關係結構傳播證據信號，控制 hubs 的過度擴展
- **Target Graph Calibration**：根據 cross-graph structural priors 校正目標圖

### Writer-Reader Self-Evolution

閉環反饋機制：
- Reader 的檢索失敗信號 → Writer 的改進目標
- 更好的閱讀暴露寫入缺陷（哪些結構鏈路缺失）
- 更好的寫入使未來閱讀更精準（圖結構更完整）

**實驗結果**：two self-evolution rounds → multi-hop QA 最佳平均 rank；zero-shot NQ 達82.5/91.6 Recall@2/5

---

## Per-source Insight

1. **Graph as dynamic substrate, not static index**：這是 SAGE區別於所有現有 GraphRAG 的核心。Graphiti 的 bi-temporal model 只解決時間維度，SAGE 的 writer-reader loop 解決「記憶系統如何通過使用反饋自我改進」。這個模式對 heartbeat_learning.py 的 drift penalty 有直接實作價值——reader 的檢索失敗信號 = distillate 失效信號。

2. **Writer-Reader coupling 是 drift detection 的關鍵**：Reader失敗時，會反饋「圖中缺少什麼」。這正是 heartbeat_learning.py 目前缺少的——沒有機制讓 reader（task context matching）報告「這個 distillate 已經很久沒被引用，熱度為零」。SAGE 的 self-evolution loop 提供了一個 concrete機制。

3. **Structurally Conditioned Propagation解決 hub over-expansion**：GFM-based reader 學習何時控制 hubs（不能盲目擴展 GraphRAG），何時擴展 bridges（連接不同領域的關鍵節點）。這對應 drift penalty 中的「哪些 distillate該保留、哪些該標記為 stale」的判斷邏輯。

4. **Policy-based writing 解決「何時寫入」問題**：SAGE 的 writer 不是被動接收新資訊就寫入，而是 policy決定何時寫、如何寫、寫什麼結構。這對應 heartbeat_learning.py 的「何時蒸餾新 distillate」的觸發條件。

5. **Self-evolution rounds 量化收斂**：SAGE 用 two rounds達到 multi-hop QA 最佳，說明 self-evolution 有明確的收斂點。這對 drift penalty 的「何時停止 decay、認為系統穩定」有參考價值。

---

## 對 Hermes/Talos 的具體建議

### WS-035 Drift Penalty — SAGE Self-Evolution Pattern移植

heartbeat_learning.py缺少的是「reader → writer 的失效信號反饋」。SAGE 的模式可以直接移植：

```
Task Context (Reader) 
  →檢索 distillates 
  → 若某 distillate 熱度長期為 0 → 回饋給 distillation trigger
  → 標記為 potentially stale
  → 下次 self-evolution round考量是否蒸餾新的覆蓋版本
```

具體：
- `N_visit` → distillate 被 task context 引用的次數（SAGE 的 visit count）
- `L_interaction` → 該 distillate 關聯的 task 總數
- `R_recency` → 上次被引用的時間衰減（SAGE 的 recency decay）
- **Reader failure signal** → SAGE 獨有：當 reader 找不到足夠證據時，該信號直接反饋給 writer（distillation trigger），指示「哪類資訊在圖中缺失」

### Memory Graph for Talos Governance

SAGE 的 entity-relation triple graph 可以作為 Talos tool-call監控的參考架構：
- Node = tool / skill / proposal
- Edge = call dependency + temporal co-occurrence
- Writer = heartbeat_learning.py 的 distillate writer
- Reader = task context matching

---

## 未追蹤 Leads

- ~~SAGE arxiv:2605.12061~~ → 已fetch，本筆記
- SCM (Self-Controlled Memory, Wang et al. 2025) — dual buffers + memory controller，MemoryOS 的另一個比較對象，尚未fetch

## ✅ 本次探索完成

