---
_slug: 40-Resources-_mixed-explorations-2026-05-28-探索-LLM-Agent-Memory-Architectures-2026
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-探索-LLM-Agent-Memory-Architectures-2026.md
title: 探索：LLM Agent Memory Architectures 2026
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- context
- facts
- graph
- mem
- memory
- multi
- open
- semantic
- temporal
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 2 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 2 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 3 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 4 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 5 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 6 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 7 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 8 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 9 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 10 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 11 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 12 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 13 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 14 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 15 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 16 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 17 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 18 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 19 — 2026-05-28

# 探索：LLM Agent Memory Architectures 2026

**日期**: 2026-05-28 | **來源**: Mem0 blog, Atlan guide | **主題**: agent memory 架構演進、生產 benchmark、開放問題

---

## Per-Source Insights

### 1. Mem0 — State of AI Agent Memory 2026 (2026-05-19 update)

**核心數據**:
- 三大 benchmark：LoCoMo (1,540 Q), LongMemEval (500 Q), BEAM (1M/10M token scale)
- 新演算法（April 2026）：LoCoMo 92.5 @ 6,956 tokens/query；LongMemEval 94.4 @ 6,787 tokens
- vs full-context：~26,031 tokens/conversation（2025 paper）；新演算法 90% reduction
- 最大進步：temporal reasoning +29.6 pts、multi-hop +23.1 pts

**架構變化**:
1. **Single-pass ADD-only extraction**：agent 生成的 facts（含 agent confirmations/recommendations）與 user facts 同等存儲，閉合了一個長期 gap
2. **Multi-signal retrieval**：semantic similarity + BM25 keyword matching + entity matching，三路並行打分融合
3. **Built-in entity linking**（取代 external graph store）：entity 存在 parallel `{collection}_entities` collection，boost relevant memories 的最終排名
   - Tradeoff：不再是 queryable graph interface，relations field 廢除，entity 只能影響 ranking 不能 traverse

**Mem0 的四 scope 模型**:
- `user_id`：跨 session 的 user facts
- `agent_id`：特定 agent instance facts
- `run_id / session_id`：單次對話 facts
- `app_id / org_id`：共享組織 context

**Procedural memory**：第三種 memory type（episodic + semantic之外的缺口）。存「如何做」：workflows、coding patterns、tool-use habits、review conventions。**實作落後於概念** — Mem0 支援但 tooling 仍是 early-stage。

**Open Problems**:
1. **Temporal abstraction**：BEAM 1M→10M drop（64.1→48.6），context 10x 但 performance -25%
2. **Cross-session structure**：user 搬遷（NY→SF），memory 應該理解為 evolution 而非 replacement
3. **Cross-session identity**：stable `user_id` 假設在 anonymous/multi-device/mixed auth 環境崩壞
4. **Memory staleness**：高相關性 memory 的 staleness 比 decay 更難——low-relevance 用 decay；**high-relevance stale facts 是 open problem**（例：用戶換工作但 memory 仍說他在舊公司）
5. **Application-level evaluation**：LoCoMo 91.6 不等於你的醫療/法律 workload 表現

**OpenMemory MCP**：隱私優先分支，本地 MCP memory server，Claude Desktop/Cursor/Windsurf/VS Code 適用。

---

### 2. Atlan — Agent Memory Architectures: 5 Patterns (2026-04-24)

**5 Patterns 對照**:

| Pattern | 準確率 | p95延遲 | Token/對話 | Governance | Multi-agent |
|---------|--------|---------|-----------|------------|-------------|
| P1: In-process | 72.9% | 17.12s | ~26K | 無 | 差 |
| P2: Flat vector | 66.9% | 1.44s | ~1.7K | 無 | 中（無 actor attribution） |
| P3: Tiered | 未单独 benchmark | 中 | 低-中 | 低-中 | 中 |
| P4: Graph+vector | 68.4% | 2.59s | 低-中 | 中 | **好（actor tags）** |
| P5: Enterprise context | 3x SQL uplift | <50ms direct | 低 | **高** | **優秀** |

**Pattern 3（MemGPT/Letta tiered）關鍵**：agents **主動管理**自己的 memory tier（explicit function calls 決定 retain/summarize/archive），不是被動接收 injected context。

**Pattern 4（Knowledge Graph + Vector）**：
- Temporal knowledge graphs（Zep/Graphiti）：time-aware edges，"what was true when" queries
- Actor-aware：每個 memory tag source agent，防止 multi-agent poisoning
- Graph-enhanced memory：68.4% @ 2.59s（vs flat vector 66.9% @ 1.44s）

**Pattern 5（Enterprise Context Layer）**：
- 不是從頭建立 bespoke memory system，而是把組織現有 governed metadata catalog 直接作為 agent memory
- 五個 components：semantic authority、active ontology、governance enforcement、provenance/lineage、decision memory
- 與 P1-P4 的根本差異：P1-P4 處理 **agent experienced**；P5 處理 **organization knows**（governed + certified）
- 生產案例：Mastercard（100M+ assets）、CME Group（18M assets, 1,300+ glossary terms）

**架構 composition（共識）**：
> Most common production combination in 2026: Pattern 2/3 (experiential) + Pattern 5 (organizational semantic authority)
> The patterns are layers, not alternatives

完整分層模型（most immediate → most persistent）：
1. Working memory（P1）— currently processing
2. Episodic/experiential（P2/P3）— what agent/user experienced
3. Semantic/relational（P4）— entity relationships + temporal facts
4. Organizational（P5）— what org formally defined + governed

---

## Hermes / Talos 啟發

### 1. heartbeat_learning.py 的 drift 問題 → 架構對應

**觀察**：heartbeat_learning distillate 有 semantic drift（結論與前期矛盾），原因：
- 缺乏 **Ebbinghaus decay**（不重要的 low-relevance memory 沒有自動衰減）
- 缺乏 **retention stability penalty**（MLMF 的 `Lret = Σt ‖E(Mt(s)) - E(Mt-1(s))‖²`，懲罰 semantic mutation）
- 缺乏 **temporal validity layer**（沒有「what was true when」機制，staleness 無法被偵測）

**對應 solution**：
- 短期：加 drift penalty 到 distillate algorithm（懲罰與前期結論相悖的 semantic jumps）
- 中期：引入 Ebbinghaus decay formula 到 memory consolidation
- 長期：Pattern 4/5 的 actor-aware + temporal graph 追蹤每條 synthesized conclusion 的 valid period

**相關研究**：
- YantrikDB（2026-05-27 notes）：Bayesian confidence + Ebbinghaus decay + Hebbian edges 直接對應這個方向
- Mem0 的 staleness open problem 印證這是 production-level challenge，不是理論問題

### 2. Talos guardian role 的 memory 含義

Talos 作為守護者，agent memory 需求對應：
- **P3 tiered** 適合 session coherence + long-horizon continuity（Talos 的守護視角需要「記得上次看到什麼」）
- **Actor-aware** 對 multi-agent 環境關鍵：區分「Hestia 說的」vs「Talos 自己觀察的」
- **Procedural memory**：Talos 的「系統性」風格意味著 learned workflows（如何做 health check、如何診斷 drift）值得 explicit storage

### 3. Token efficiency 的實務意涵

Mem0 新演算法 6,956 tokens/query vs 26,031 full-context：
- Hermes 的 heartbeat_learning.py 如果每次 distillate 都重新讀歷史 thread，成本是 26K vs 7K 的差距
- **Practical implication**：對於 Talos 这种 guardian agent，每月 distillation 的 token budget 差 3.7x

---

## 跨文章 Synthesis

兩個 source 收斂到同一個核心張力：

**「結構化 > 純嵌入」共識**：Mem0 從純 vector → multi-signal（含 entity linking、BM25）；Atlan 的 P4 graph+vector hybrid 取代純 vector 成为 production standard；YantrikDB 的 5-tier index（HNSW+graph+temporal+decay+KV）再次印證。

**「記憶問題 ≠ 檢索問題」**：Atlan P5 指出 enterprise memory 的核心不是 retrieval，是 semantic authority（組織已定義、governed、certified 的共識）。Mem0 的 staleness open problem 呼應——當一條 high-relevance fact 過時但 retrieval score 仍高時，問題不在 recall，是 **validity signal 缺席**。

**「Temporal 是最難的」**：BEAM 1M→10M -25%、Mem0 +29.6 pts 但 staleness 仍是 open、Atlan 的 "cross-session structure" 仍是 open。實務上 2026 的进展是：**量化了問題邊界**，但核心还没解决。

---

## 未追蹤 Leads

- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — eight frameworks compared (Letta, Zep, Mem0, etc.)
- https://mem0.ai/blog/state-of-ai-agent-memory-2026#open-problems — Mem0 staleness 問題的深入討論
- github.com/mem0ai/memory-benchmarks — LoCoMo/LongMemEval/BEAM 開源 benchmark framework
- https://arxiv.org/abs/2310.08560 — MemGPT/Letta 原始 paper
- https://arxiv.org/abs/2603.10062 — Multi-Agent Memory from a Computer Architecture Perspective

---

## ✅ 本次探索完成



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025 paper: the original token-efficient memory algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- ~~https://arxiv.org/abs/2504.19414~~ — ❌ WRONG ID (points to unrelated ViT paper), removed 2026-05-30
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- ~~https://arxiv.org/abs/2504.19414~~ — ❌ WRONG ID (points to unrelated ViT paper), removed 2026-05-30
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete



## Version 20 — 2026-05-29

# LLM Agent Memory Architecture — 2026 Survey & Benchmark Synthesis

**日期**: 2026-05-29 | **來源**: Mem0 blog (2026-04-01) + arXiv 2603.07670v1 MLMF Survey + Atlan comparison (2026-04-02) | **類型**: Exploration

---

## Source 1 — Mem0 Blog: "State of AI Agent Memory 2026"

**Core claims:**
- Three benchmarks now standard: LoCoMo (1,540 Q, 4 cat), LongMemEval (500 Q, 6 cat), BEAM (1M/10M token scale)
- Mem0 2026 algorithm: 92.5 LoCoMo, 94.4 LongMemEval, ~6,956 tokens/query (1/4 of full-context)
- Two architectural changes driving gains:
  1. Single-pass ADD-only extraction (agent-generated facts stored with equal weight to user facts)
  2. Multi-signal retrieval: semantic + BM25 + entity matching, all three fused
- Biggest gains: temporal reasoning (+29.6 pts) and multi-hop (+23.1 pts)
- 21 framework integrations, 20 vector stores
- Hardest open problems: cross-session identity, temporal abstraction at scale, memory staleness
- "Staleness in high-relevance memories is a harder, open problem" — this directly validates the gap identified in previous heartbeat_learning.py design discussions

**Key frame for Hermes:**
- 6,956 tokens/query vs ~26,000 full-context = 4× token efficiency gain
- Multi-signal retrieval (semantic + BM25 + entity) is the fusion approach that outperforms any single signal
- The benchmark suite (LoCoMo/LongMemEval/BEAM) gives us a concrete way to evaluate memory architectures before committing

---

## Source 2 — arXiv 2603.07670v1: MLMF Survey

**Core taxonomy (three dimensions):**
1. **Temporal scope**: working / episodic / semantic / procedural
2. **Representational substrate**: context-resident / vector-indexed / structured / executable
3. **Control policy**: heuristic / prompted self-control / learned control

**Five design objectives and their tensions:**
- Utility ↔ Efficiency (max utility tempts hoarding)
- Faithfulness (stale/hallucinated recall can be worse than no recall)
- Governance

**Three architecture patterns (practical recommendation):**
- Pattern A: Monolithic context (everything in prompt) — prototyping only
- Pattern B: Context + retrieval store — **recommended starting point**
- Pattern C: Tiered memory + learned controller — for when data shows it's needed

**Key findings:**
- Ablation: Voyager without skill library → 15.3× slower tech-tree milestones; MemoryArena swap → 80%→45% completion
- "The gap between 'has memory' and 'does not have memory' is often larger than the gap between different LLM backbones"
- Consolidation is the underserved problem — episodic→semantic transition requires either explicit developer rules or fragile LLM summarization
- MemGPT/Mem0 use prompted self-control; Agentic Memory (Yu et al. 2026) uses learned control via RL
- POMDP formulation clarifies: memory = belief state; the write/read loop is a feedback system where bad writes pollute downstream

**Open challenges (directly relevant to heartbeat_learning.py drift):**
- Principled consolidation: dual-buffer consolidation (hot buffer during probation → promote after quality checks) mirrors hippocampal-to-neocortical transfer
- Causally grounded retrieval: semantic similarity ≠ causal relation; root-cause analysis needs temporal/causal metadata layer
- Trustworthy reflection: agent falsely concluding "approach A always fails" → confirmation bias trap
- **Learning to forget**: hard problem; essential for robustness, privacy, efficiency
- Staleness vs decay distinction (from Mem0 blog): decay = low-relevance smoothing; staleness = high-confidence fact suddenly wrong — heartbeat_learning.py addresses decay but not yet staleness

**Three benchmarks:**
- LoCoMo: 1,540 Q, 4 cat (single/multi-hop, open-domain, temporal)
- LongMemEval: 500 Q, 6 cat (knowledge update, temporal reasoning, multi-session)
- BEAM: 1M/10M token scale; BEAM 1M→10M drop (64.1→48.6) is the hard ceiling for temporal abstraction at scale

---

## Source 3 — Atlan: "Best AI Agent Memory Frameworks 2026"

**Independent benchmark (from vectorize.io, arXiv 2501.13956):**
- Zep: 63.8% LongMemEval vs Mem0: 49.0% — 15-point gap, driven by temporal knowledge graph (validity windows)
- Architecturally: Zep stores fact validity windows; Mem0 stores timestamped snapshots — same data, different model

**Framework comparison (8 systems):**
- Mem0: self-editing memory (no duplicates), 48K stars, graph paywalled at Pro tier, no validity windows
- Zep/Graphiti: temporal KG, 300ms P95, no LLM at query time, SOC 2 + HIPAA
- Letta: OS-inspired tiered (core/archival/recall), agents actively curate own memory
- LangMem: procedural memory (agent rewrites own instructions), framework-locked
- Supermemory: explicit forgetting mechanism (first-class, not edge case), MCP-native
- Redis Agent Memory Server: infrastructure only (no management logic), sub-ms latency

**Important observation from Atlan:**
- ALL 8 frameworks lack enterprise governance: no glossary, lineage, entity resolution, or policy enforcement
- This is a fundamental gap in the memory framework market — not relevant to Hermes today but important for long-term architecture planning

---

## Cross-Article Synthesis

**Convergence point — structured > pure embedding:**
- Mem0: multi-signal retrieval (semantic + BM25 + entity)
- MLMF: "Forgetting is not a bug; it is a feature" — procedural memory stores *how*, not just *what*
- Atlan: Zep's temporal KG outperforms flat vector by 15 pts on temporal tasks
- Hermes skills.md philosophy: "Skill as Memory" — aligns with procedural memory emphasis
- agentmemory exploration (2026-05-28): same convergence to 4-tier (Working/Episodic/Semantic/Procedural) + Ebbinghaus decay + BM25+vector+graph RRF fusion

**Architecture decision implied:**
- Start with Pattern B (context + retrieval store), instrument thoroughly, graduate to Pattern C only when data justifies
- Hermes already has context-resident memory (skills, session context) + retrieval-augmented store (obsidian vault)
- Missing: temporal fact modeling (validity windows), explicit forgetting mechanism, entity resolution

**Drift penalty gap confirmed:**
- heartbeat_learning.py addresses *decay* (low-relevance memories) but NOT *staleness* (high-relevance facts suddenly wrong)
- MLMF open challenge: "causally grounded retrieval" + "trustworthy reflection" — directly maps to the semantic drift problem

**Tokens-per-query as a Hermes metric:**
- Mem0: 6,956 tokens/query vs 26,000 full-context — 4× efficiency
- Hermes should track a similar metric: `avg_tokens_per_session_start` to detect context bloat
- BEAM benchmark is the production stress test; 10M scale (48.6%) is the hard ceiling

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — Agentic Memory (Yu et al. 2026): learned memory management via GRPO (3-stage RL pipeline)
- ~~https://arxiv.org/abs/2504.19414~~ — ❌ WRONG ID (points to unrelated ViT paper), removed 2026-05-30
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper (vectorize.io source cited by Atlan)
- https://mem0.ai/docs — Mem0 docs; check if multi-signal retrieval pattern can be replicated without the managed service
- https://github.com/mem0ai/memory-benchmarks — benchmark evaluation framework, open-sourced

---

## Hermes 啟發

1. **heartbeat_learning.py needs a staleness mechanism**: a `confidence_valid_until` field alongside the decay curve, for high-impact facts (e.g., a skill's `version` field going stale after the tool itself updates). This complements decay; they're separate mechanisms for separate failure modes.

2. **BEAM benchmark is the right stress test for Herme's memory**: 10M token scale (48.6%) is the ceiling. If heartbeat_learning.py ever has to manage multi-session agent memory for Hestia, BEAM is the reference.

3. **The 3-architecture-pattern recommendation aligns with Herme's current design**: Pattern A = session context (already exists), Pattern B = vault + autonomous_notes (already exists), Pattern C = learned controller for memory consolidation (not yet, but we know when to add it — when metrics show retrieval quality is the bottleneck).

4. **Explicit forgetting as a first-class operation**: Supermemory is the only framework that treats forgetting as a design primitive, not an edge case. Hermes skills have version slots and `deprecated` frontmatter — this is already a partial implementation of forgetting as a first-class command.

## ✅ Exploration Complete

