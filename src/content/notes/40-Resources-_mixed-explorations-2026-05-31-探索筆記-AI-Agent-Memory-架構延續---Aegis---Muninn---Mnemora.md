---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索筆記-AI-Agent-Memory-架構延續---Aegis---Muninn---Mnemora
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索筆記-AI-Agent-Memory-架構延續---Aegis---Muninn---Mnemora.md
title: 探索筆記：AI Agent Memory 架構延續 — Aegis / Muninn / Mnemora
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- access
- act
- aegis
- decay
- hebbian
- llm
- memory
- mnemora
- muninn
- time
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

---
title: "探索筆記：AI Agent Memory 架構延續 — Aegis / Muninn / Mnemora"
date: 2026-05-31
type: explorations
tags: [explorations, llm, memory, act-r, hebbian, serverless, aws]
---

# 探索筆記：AI Agent Memory 架構延續 — Aegis / Muninn / Mnemora

**延續自**: [[2026-05-31-探索-VAC-Memory-System---Hybrid-Retrieval-for-LLM-Agent-Memory]]

**日期**: 2026-05-31
**類型**: exploration
**來源**: 三個 dead leads 驗證活著後直接 fetch

---

## Source 1: Muninn — ACT-R Decay + Hebbian Learning (GitHub)

**URL**: `github.com/scrypster/muninndb` — 299★, Go, no LLM in hot path
**Date**: Active repo | **Quality**: high（認知科學啟發架構）

### 核心架構：Cognitive Database

Muninn 是「認知資料庫」——不是 vector store，是 ACT-R (Adaptive Control of Thought–Rational) 認知架構的實作。關鍵：

- **ACT-R decay**: human memory 的 active trace 會自然衰減（刚emory 建立時最活耀，隨時間變弱）→ Muninn 直接在資料庫層實作
- **Hebbian learning**: "neurons that fire together wire together" → 共同被取的 facts 會形成關聯強化
- **No LLM in hot path**: 所有機制都是確定性演算法（衰減、Hebbian weighting），不需要 LLM 呼叫

### 具體機制

```
記憶活躍度 = 初始強度 × Decay(time since last access) × HebbianBoost(co-access frequency)
```

- **Decay**: 每次創建時設初始強度（如 1.0），每單位時間乘以 decay factor（可設，如 0.95）
- **Hebbian boost**: 若 fact A 和 fact B 在同一查詢中被共同取用到，兩者的關聯權重 +1
- **Retrieval**: 查詢時根據活躍度排序，過低的直接跳過

### 對 Hermes 的直接啟示

`heartbeat_learning.py` 的蒸餾決策現在是純 calendar age（`time_staleness`）+ access count。Muninn 的 ACT-R decay 可以替代 exponential decay：
- 「新事實不需要那麼快衰減」— initial strength 高，decay 慢
- 「經常共同取用的事實互相強化」— Hebbian boost 補充 access recency
- 「不需要 LLM」— 全部是 O(1) 數值計算

### 實作切入點

現有 `heartbeat/utils.py` 的 `_compute_staleness()` 已經有 `time_staleness` 和 `access_staleness`。可以在此基礎上加：
- `initial_strength` 欄位（新 entry → 1.0，蒸餾時可提升）
- `decay_rate` per category（如 `system.` facts decay 慢，`ephemeral.` 快速衰減）
- `co_access_pairs`（共同被取的事實對，增強綁定）

---

## Source 2: Aegis Memory — Rule-Based Filter → LLM Extraction Pipeline

**URL**: `github.com/quantifylabs/aegis-memory` — 22★, content security + integrity verification
**Date**: Active | **Quality**: medium（安全導向，架構參考價值）

### 核心架構：Secure Context Engineering

Aegis 的定位是「AI agent 的內容安全 + integrity verification」。重點不是記憶本身，而是：

- **Rule-based filter**: 在 LLM 處理前，先用規則過濾事實（如「不能含 email」「不能含 credentials」）
- **LLM extraction pipeline**: 乾淨的 extraction 事實才送 LLM，減少 injection risk
- **Integrity verification**: 事實寫入前校驗，事實讀出後驗證（HMAC 之類）

### 對 Hermes 的啟示

WS-031（HMAC integrity）已在 `otp_gate.py` 層級實作。Aegis 的模式是：
- **輸入端**：rule-based filter 在 LLM extraction 前 → 可減少 LLM 的上下文汙染
- **輸出端**：integrity verification → 事實讀出時校驗是否被篡改

這個 pattern 和 `confidence_valid_until` 機制正交但互補：
- `confidence_valid_until` = 時間維度的 decay
- Aegis integrity = 空間維度的驗證

---

## Source 3: Mnemora — 4 Memory Types, Sub-10ms, No LLM in CRUD

**URL**: `mnemora.dev` + `github.com/mnemora-db/mnemora`
**Date**: Active (2026) | **Quality**: high（production-ready serverless）

### 核心架構：4 Types, Zero LLM in Hot Path

```
Mnemora API
├── Working Memory (key-value)      → DynamoDB, sub-10ms
├── Semantic Memory (vector)        → Aurora Serverless v2 + pgvector
├── Episodic Memory (time-series)  → DynamoDB time-series
└── Procedural Memory (rules/tools) → S3 + Lambda
```

關鍵差異：
- **No LLM in CRUD**: 所有 memory 操作都是確定性 DB 操作，不需要 LLM 呼叫
- **LangGraph checkpoints**: 原生支援 LangGraph 的 checkpointing
- **4 memory types**: 第一個同時覆蓋 Working + Semantic + Episodic + Procedural 的 serverless 產品

### Pricing signal

| Plan | Price | Agents |
|------|-------|--------|
| Free | $0 | 1 agent, 10K ops/mo |
| Starter | $19 | 10 agents, 100K ops/mo |
| Pro | $79 | unlimited, 1M ops/mo |
| Scale | $299 | unlimited, 10M ops/mo |

Market 願意為 serverless memory 付費（$19-299/mo），表示這是真實需求而非純研究問題。

### 與 VAC + Muninn 的架構交叉

| System | Recall | Latency | LLM in CRUD | Memory Types |
|--------|--------|---------|-------------|--------------|
| VAC | 94-100% | <3s | Yes (GPT-4o-mini) | Semantic only |
| Muninn | N/A (cognitive) | O(1) | No | Procedural + semantic |
| Mnemora | N/A (CRUD-first) | <10ms | No | 4 types |
| Mem0 | N/A | N/A | Yes | Graph + vector |

三個系統都指向同一結論：**LLM 不應該在 every memory CRUD 裡**。VAC 和 Mem0 需要 LLM 做 semantic understanding，但 Muninn 和 Mnemora 證明：对于确定性操作（decay、key-value、time-series），LLM 是多餘的。

---

## 跨系統 Synthesis

### 核心收斂：分層記憶 + 確定性衰减

從 VAC 的 hybrid retrieval，到 Muninn 的 ACT-R decay，再到 Mnemora 的 4-type serverless，三者共同指向 Hermes 的記憶架構方向：

1. **分層**: Working（key-value, DynamoDB-style）→ Semantic（vector, with decay）→ Episodic（time-series log）→ Procedural（tool definitions）
2. **確定性衰减**: ACT-R decay > 純 calendar age，Hebbian boost > 純 access count
3. **No LLM in hot path**: 只有在需要 semantic understanding 時才叫 LLM（VAC 的 rerank/generate），確定性操作全部繞過

### 對提案的推進

WS-038（access recency weighting）已實作 Phase 1/2/4。這個 cycle 的探索指向：

- **Phase 3 方向**：ACT-R style decay rate per category，可以補足 `time_staleness` 的粗粒度問題
- **Phase 5 方向**：4-type memory taxonomy——目前 `heartbeat_learning.py` 只有单一 fact pool，可以考慮分層（working facts vs long-term facts vs episodic facts）

---

## 未追蹤 Leads

- `github.com/mnemora-db/mnemora` — GitHub repo，確定活著，可 fetch README 看具體 SDK interface
- `github.com/scrypster/muninndb` — 可 fetch README 看 Go 實作细节（ACT-R decay function signature）
- `aegismemory.com` — 官網有完整 feature list，可fetch對比

---

## ✅ 本次探索完成

