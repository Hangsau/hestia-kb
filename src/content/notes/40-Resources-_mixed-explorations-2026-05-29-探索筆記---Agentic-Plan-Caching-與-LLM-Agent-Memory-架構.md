---
_slug: 40-Resources-_mixed-explorations-2026-05-29-探索筆記---Agentic-Plan-Caching-與-LLM-Agent-Memory-架構
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-探索筆記---Agentic-Plan-Caching-與-LLM-Agent-Memory-架構.md
title: 探索筆記 — Agentic Plan Caching 與 LLM Agent Memory 架構
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- apc
- cache
- caching
- drift
- keyword
- memory
- penalty
- plan
- template
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

# 探索筆記 — Agentic Plan Caching 與 LLM Agent Memory 架構

**日期**: 2026-05-29
**延續自**: （非延續，隨機探索）
**主題**: LLM Agent Memory / Plan Caching 成本優化架構

---

## Source 1: Agentic Plan Caching (APC) — arxiv 2506.14852

**URL**: `https://arxiv.org/html/2506.14852v2`
**为什么要看**: Plan-Act agent 成本優化的具體演算法，直接回答「heartbeat learning drift penalty 需要什麼機制」

### 核心洞察

APC 解決的問題：傳統 caching（如 prompt caching、semantic caching）對 chatbot 有效，但對 agent無效——因為 agent 的輸出取決於外部資料和環境，相同 high-level intent 會產生不同具體計畫。

**解決方案輪廓**：

1. **Keyword Extraction** — 用小模型（GPT-4o-mini）從 query 萃取高層意圖關鍵字（與 query本身的語意相似度比較，這是關鍵 insight）
2. **Plan Template Cache** — 快取結構化 plan template，而非 (input, output) pair 或完整 execution log。 Template 包含「步驟序列 + 預期回應格式」，去除了 entity names、numeric values 等具體細節
3. **Lightweight Adaptation** — cache hit 時，用小模型（Llama-3.1-8B）將 template 調整為 task-specific plan，再用大模型執行
4. **Results**: 50.31% cost reduction，27.28% latency reduction，maintain 96.61% accuracy

**與 Hermes 的關聯**：

- **heartbeat_learning.py drift penalty**：APC 說明為何「直接快取 complete execution log」（= 把對話歷史當 in-context example）是無效的——需萃取「去除 context-specific detail 的 template」。這正是 drift penalty 需要的：stable insight extraction
- **`memory-consolidator` drift detection**：APC 的 keyword extraction 可用於辨識哪些 task pattern 已穩定（重複出現的 keyword = stable instruction pattern），哪些仍在實驗中
- **cost tracking`：APC 的 cache hit/miss metrics 直接可對映到 token 用量追蹤

**未追蹤 leads**：
- 網址：`https://github.com/qizhengzhang/agentic-plan-caching`（從 paper 作者領域抓，尚未驗證存在）
- 需要研究： APC 的 cache eviction strategy（paper 只提「cache size management」無具體 algorithm）

---

## Source 2: LLM Agent Memory — OpenReview Survey

**URL**: `https://openreview.net/forum?id=KPs1EgGKcT`
**为什么要看**: 統一的 taxonomy，覆蓋「natural language tokens / intermediate representations / parameters」三層 memory paradigm

### 核心洞察

三層 Paradigm：
1. **Natural Language Tokens** — 文字 history、summaries
2. **Intermediate Representations** — KV caches、embeddings、state representations
3. **Parameters** — Fine-tuned weights（最昂貴但最 hard）

**Management stages**（每層都有的三個 stage）：
- Memory Construction
- Memory Update
- Memory Query

三個 stage 的 decoupling 是關鍵設計原則——與 APC 的「extract keyword + adapt template」一致：construction（extract）、update（template adaptation）、query（keyword match）。

**與 Hermes 的對照**：

| Hermes Layer | OpenReview Paradigm |
|---|---|
| L1 MEMORY.md（原生文字）| Natural Language Tokens |
| L2 memory-consolidator（structured KB）| Intermediate Representations |
| L3 briefing-updater | ???（不屬於前兩層？）|

**未追蹤 leads**：
- MemAgents Workshop（`https://openreview.net/pdf?id=U51WxL382H`）— 需要 PDF，但 sanitizer 失敗。改找 HTML 版本
- Mem0 / Mem0 Pro 的實作細節（已有接觸，需要深入研究 actual API design）

---

## 跨 Source Synthesis

### 收斂點：結構化 template > 純嵌入或純文字

APC + OpenReview survey + 前期調研（Mem0、YantrikDB）全部收斂到同一個結論：

> **Memory abstraction 必須去除 context-specific details，才能實現 stable reuse**

具體：
- APC：去除 entity names、numeric values → plan template
- Mem0：scope-tagged writes，去除具體對話 context
- YantrikDB：程序記憶（procedural）vs 事實記憶（episodic）分層
- agentmemory（18.9k⭐）：Ebbinghaus decay + BM25+vector+graph RRF fusion

### 對 heartbeat_learning.py drift penalty 的直接回答

drift penalty 需要的新機制（從 APC 改良而來）：

1. **Semantic deduplication**：當 distillate 與前期 conclusion 語義重疊（而非字面重疊）時，不累積新的 triplet，而是標註「reinforced existing claim」
2. **Template stability score**：計算同一 claim 在 N 次 distillate cycle 中的出現頻率。低頻 claim（<3次）不納入 stable KB，只留在 working memory
3. **Keyword-triggered consolidation**：當某個 task keyword（如 `consolidation-step`、`memory-distill`）在 multiple cycles 重複出現，代表對應的 insight pattern 已穩定，觸發 explicit drift penalty approval

### 補充：從 APC 學到的 cost 按鈕

APC 對演算法層面的 cost 非常有價值：
- `keyword_extraction`（小模型）→ `adapt_template`（小模型）→ `execute_plan`（大模型按需）
- 這就是 Hermes `heartbeat_learning.py` 應該做的：infer distilled insight 時用小模型，validate drift penalty 時再用大一點的模型

---

## ✅ 本次探索完成

**時間戳**: 2026-05-29 14:46 CST
**驗證指令**: `python3 /root/.hermes/scripts/validate_note.py /tmp/explore_note_apc_2026-05-29.md`（未跑，筆記不在 autonomous_notes/，直接整合進本 note）

