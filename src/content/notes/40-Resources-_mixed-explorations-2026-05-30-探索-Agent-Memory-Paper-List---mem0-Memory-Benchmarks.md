---
_slug: 40-Resources-_mixed-explorations-2026-05-30-探索-Agent-Memory-Paper-List---mem0-Memory-Benchmarks
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-探索-Agent-Memory-Paper-List---mem0-Memory-Benchmarks.md
title: 探索：Agent Memory Paper List + mem0 Memory Benchmarks
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- benchmarks
- contradiction
- distillate
- drift
- hermes
- mem
- memory
- resolution
- snapshot
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 探索：Agent Memory Paper List + mem0 Memory Benchmarks

**延續自**: [[2026-05-30-mem0-state-of-ai-agent-memory-2026.md]]

## Per-Source Insights

### 1. Shichun-Liu/Agent-Memory-Paper-List — Unified Taxonomy

Source: `https://github.com/Shichun-Liu/Agent-Memory-Paper-List` (2.1k stars)

**核心價值：統一的記憶分類框架**

這個 repo 支撐了 Hu et al. (2025) 的論文「Memory in the Age of AI Agents: A Survey」，提出三維 taxonomy：

- **Forms（什麼攜帶記憶）**: Token-level（explicit/discrete）、Parametric（implicit weights）、Latent（hidden states）
- **Functions（為何需要記憶）**: Factual（知識）、Experiential（洞見與技能）、Working Memory（主動上下文管理）
- **Dynamics（記憶如何演化）**: Formation（萃取）、Evolution（整合+遺忘）、Retrieval（存取策略）

這個分類直接比 Hermes 的架構更精細。Hermes 目前 implicit（即時對話）vs explicit（持久化）的區分，忽略了：
- Parametric memory（LLM 權重隱含的知識）vs Latent memory（hidden states like KV cache）的區分
- Experiential memory 的「技能」維度——不只是事實，還包括從經驗中萃取的 procedure

**對 Hermes 的啟發**：
- `heartbeat_learning.py` 的 distillate 層目前只處理「經驗洞見」（Factual/Experiential boundary），但沒有捕獲「技能」維度（如何做某件事的程序知識）
- 三層 Dynamics（Formation→Evolution→Retrieval）對應 heartbeat 的 snapshot→distillate→retrieve 管道，但目前的實現是 Formation 有（snapshot）、Evolution 有（distillate）、Retrieval 幾乎沒有（只有硬編碼的查詢）

### 2. mem0ai/memory-benchmarks — Evaluation Suite

Source: `https://github.com/mem0ai/memory-benchmarks` (36 stars, Apache 2.0)

**核心價值：可跑的量化基準**

三個 benchmark：
- **LOCOMO**: ~300 questions, 10 multi-session dialogues — factual recall, temporal reasoning, multi-hop inference
- **LongMemEval**: 500 questions, 6 types — long-term memory across extraction, temporal, multi-session reasoning
- **BEAM**: 100 conversations per bucket (100K–10M tokens), 2000+ questions — 10 memory ability types

**直接與 Hermes 相關的數字**：

| Benchmark | Score | 含義 |
|-----------|-------|------|
| BEAM 1M (Top 200) | 70.1% pass, 0.641 avg | 中等規模回憶能力 |
| BEAM 10M (Top 200) | 50.5% pass, 0.486 avg | Hermes 的實際 regime（長時運行累積記憶）|
| `contradiction_resolution` @ 1M | 0.357 avg score | **最難的記憶能力** |
| `contradiction_resolution` @ 10M | 0.325 avg score | 規模越大越難 |

**`contradiction_resolution` 是 drift 問題的核心指標**

當新證據與舊記憶衝突時的解析能力。這正是 `heartbeat_learning.py` 目前欠缺的：
- 沒有 explicit mechanism 偵測「新的 snapshot 與舊的 distillate 矛盾」
- 也沒有「衝突解決」策略（保留哪個、丟棄哪個）

這與 SSGM Theorem 1（bounded semantic drift via periodic reconciliation）完全吻合。

**可移植性**：
- 支援 Mem0 OSS self-hosted（Docker Compose），不需要 API key
- 可以對 Gemini/Ollama 等本地模型跑 extraction
- 結果有 web UI 可視化

## 跨文章 Synthesis

1. **分類學收斂**：Agent-Memory-Paper-List 的 Forms/Function/Dynamics 框架，與 YantrikDB 的五層索引（HSNW+graph+temporal+decay+KV）、Mem0 的 scope-tagged writes，趨同到同一個結論：「純嵌入檢索不夠，需要結構化的元資料層（時間、衰減、衝突標記）」

2. **量化缺口**：memory-benchmarks 提供了客觀的落後指標。BEAM 10M 的 48.6 分（`contradiction_resolution` 最低）是個參考點——如果我們能在 Hermes 的記憶系統上跑同樣的 benchmark，就能知道自己落後多少

3. **實作路徑**：memory-benchmarks 是 Python 套件，`pip install -r requirements.txt` 就能跑。LOCOMO 最快（~300 Qs），可以用來快速驗證。對於 WS-035 的「drift penalty」設計，BEAM 的 `contradiction_resolution` metric 是直接的量化目標。

## Hermes 啟發

1. **WS-035 drift penalty 設計方向明確化**：`contradiction_resolution` score 可以作為 heartbeat_learning drift penalty 的 evaluation target。設計 contract：`distillate` 產出時，必須能通過「若新 snapshot X 與 distillate D 衝突則標記 `conflict_flag`」的檢查。

2. **Experiential Memory → Procedural Memory**：目前的 distillate 偏向 Factual（知識陳述），缺少「技能」維度。可以探索：snapshot 中的 tool-call pattern 是否應該成為 distillate 的 secondary output？

3. **Evaluation before Implementation**：在實作 drift penalty 之前，先用 memory-benchmarks 建立 baseline（用 LOCOMO 快速跑），這樣日後的改進有量化對比。

## 未追蹤 Leads

- https://github.com/mem0ai/mem0 — Mem0 OSS core (not just benchmarks)
- https://arxiv.org/abs/2512.13564 — 原版 Survey 論文
- `benchmarks/locomo/run.py` — LOCOMO benchmark 實作，可參考如何隔離跑 evaluation

## ✅ 本次探索完成

