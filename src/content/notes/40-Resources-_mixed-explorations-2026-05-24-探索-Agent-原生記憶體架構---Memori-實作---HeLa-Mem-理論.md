---
_slug: 40-Resources-_mixed-explorations-2026-05-24-探索-Agent-原生記憶體架構---Memori-實作---HeLa-Mem-理論
_vault_path: 40-Resources/_mixed/explorations/2026-05-24-探索-Agent-原生記憶體架構---Memori-實作---HeLa-Mem-理論.md
title: 探索：Agent 原生記憶體架構 — Memori 實作 + HeLa-Mem 理論
date: 2026-05-24
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- graph
- hebbian
- hela
- hermes
- mem
- memori
- pathway
- process
- semantic
created: '2026-05-24'
updated: '2026-06-15'
status: budding
---

# 探索：Agent 原生記憶體架構 — Memori 實作 + HeLa-Mem 理論

**延續自**:（無前期筆記）

## Phase 3 — Review

### Per-source insights

#### MarkTechPost — Memori 實作教程（2026-05-11）

**Core insight**：Memori 的價值主張是「LLM register」模式——所有 chat completion call 自動過記憶層，不需要手動呼叫 `mem.search()`。這是真正 non-invasive 的設計。

**Key patterns**：
1. `mem.attribution(entity_id="...", process_id="...")` — entity 可對應 user，process 可對應 agent role/persona。這和 Hermes 的 multi-agent 架構契合。
2. `mem.set_session(uuid)` / `mem.new_session()` — session 級團組相關對話，隔離不相關上下文（如專案决策 vs 個人瑣事）
3. `WRITE_DELAY = 6` — 這個 sleep delay 是關鍵：memori 的 write 是非同步延後寫入，不是同步完成後才回應。需要 6 秒確保 write 完成後再 query。這說明記憶寫入有 eventual consistency 特性。
4. 多租戶隔離：同一 entity_id 不同 process_id 的記憶完全隔離（Alice 的 fitness-coach 和 meal-planner不互串）
5. **BYODB 模式**：支援指向自己的 PostgreSQL——這讓 Memori 可以脫離 SaaS 跑在本地，符合 Hermes 的 self-hosted 偏好。

**對 Hermes 的啟發**：
- LLM register 模式比手動 mem.search() 更好——工具層 interception，agent 無感知
- process_id concept 可直接拿來做 Talos 的守護者視角隔離（不同 concerns 不同的 memory namespace）
- session grouping 解決「同一 user 的專案 context 和閒聊 context 混雜」問題

#### Papernotes — HeLa-Mem（ACL 2026）

**Core insight**：Hebbian learning 的核心不是「相似的記憶連在一起」，而是「一起被用過的記憶連在一起」。這是 associative linkage 而非 semantic similarity，是更深的維度。

**Architecture**：
1. **Hebbian Online Association**：graph nodes = dialogue turns，edge weight 根據 co-activation 更新。`w_{ij}^{(t+1)} = (1-λ)·w_{ij}^{(t)} + η·I(v_i, v_j in K_t)` — 這是真正的動態圖結構，不是 vector similarity。
2. **Reflective Consolidation**：hub node（高連接度）觸發蒸餾——將叢集蒸餾成 semantic knowledge（user profile、factual memories）。這模擬了人腦睡眠時的記憶鞏固過程。
3. **Dual-pathway retrieval**：base pathway = semantic similarity；flip pathway = Hebbian spreading activation（associatively close but semantically distant）。這解決了「標題和內容不符」的問題——可以找到 HN 文章實際在說什麼而不只是關鍵字重疊。

**Token efficiency 的關鍵**：HeLa-Mem 在 LoCoMo benchmark 上用的 tokens 最少但表現最好。原因是精確檢索（precision）比數量重要。

**對 Hermes 的啟發**：
- Hebbian graph 可用於記憶壓縮的優先級排序——高 co-activation 的記憶不該被壓縮，要保留 associative structure
- 蒸餾後的 semantic knowledge 比 episodic memory 更穩定——Hermes 的 memory-consolidator 應該區分這兩種
- dual-pathway 對複雜推理很重要——「標題不符實際」的 agent（如 Butter/behvisor）可以被 Hebbian path 抓到

### 跨文章 Synthesis

Memori（實作）和 HeLa-Mem（理論）形成互補：

- **Memori** 解決「如何實際接入」——LLM register、BYODB、多租戶隔離
- **HeLa-Mem** 解決「記憶結構如何演化」——Hebbian graph、consolidation、dual-pathway retrieval

共同啟示：記憶不該是靜態 vector store，而是動態成長的 graph。Memori 的 process_id 可對應 HeLa-Mem 的 node attributes；Memori 的 session 可對應 HeLa-Mem 的 retrieval set boundary。

對 Hermes 的 long-term memory 架構：
1. 從 append-only vector store 改為 Hebbian graph（edges = co-activation history）
2. 區分 episodic（對話節點）和 semantic（蒸餾後的結構化知識）
3. dual-pathway retrieval：semantic similarity base + Hebbian spreading activation supplement
4. write path 非同步（eventual consistency），需要 WRITE_DELAY 機制

### 未追蹤 leads

- https://github.com/Mem0rias/Memori（ Memori 官方 repo）
- https://arxiv.org/abs/2604.16839（HeLa-Mem 原始論文）
- Mem0 multi-signal retrieval（semantic + BM25 + entity）— 和 HeLa-Mem 的 dual-pathway 有相通之處
- A-MEM（NeurIPS 2025）— Zettelkasten-style，和 HeLa-Mem 的 graph approach 對比

## ✅ 本次探索完成（2026-05-24 02:50 CST）
