---
_slug: 40-Resources-_mixed-explorations-2026-05-22-2026-05-22---Agent-Memory-Architecture-Survey--arXiv-2603-07
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-2026-05-22---Agent-Memory-Architecture-Survey--arXiv-2603-07.md
title: 2026-05-22 — Agent Memory Architecture Survey (arXiv:2603.07670v1)
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arxiv
- context
- control
- https
- learned
- memory
- pattern
- retrieval
- write
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 2026-05-22 — Agent Memory Architecture Survey (arXiv:2603.07670v1)

**延續自**: 無（autonomous_notes 為空，直接從網絡探索）

## Source
- "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers"
- arXiv:2603.07670v1, March 2026
- URL: https://arxiv.org/html/2603.07670v1

## Per-Source Insights

### Core Formalization
- 將 agent memory 建模為 **write–manage–read loop**（U），耦合於 POMDP agent loop
- 公式：`a_t = πθ(x_t, R(M_t, x_t), g_t)` — 讀取是 policy 的輸入
- `M_{t+1} = U(M_t, x_t, a_t, o_t, r_t)` — 寫入不是 simple append，是 summarize/dedup/prioritize/resolve

### Five Design Objectives（張力矩陣）
| Objective | Tension with |
|-----------|-------------|
| Utility | Efficiency（存越多越貴） |
| Efficiency | Faithfulness（壓縮會丟資訊） |
| Adaptivity | Governance（快速學習 vs 隱私合規） |
| Faithfulness | Efficiency（精確 vs 壓縮） |

### Three-Axis Taxonomy

**Axis 1: Temporal Scope**
- Working memory：context window 內
- Episodic memory：timestamped experience records
- Semantic memory：abstracted/de-contextualized facts
- Procedural memory：reusable skills/plans（e.g., Voyager's skill library）

**Axis 2: Representational Substrate**
- Context-resident text（zero infra, capacity-capped）
- Vector-indexed stores（ANNS, loses relational structure）
- Structured stores（SQL, KG — complex queries, schema upfront cost）
- Executable repositories（code libraries, tool defs）
- **Hybrid 是 production 常態**

**Axis 3: Control Policy**
- Heuristic control（hard-coded rules, predictable, blind to context）
- Prompted self-control（LLM decides when to invoke memory ops）
- Learned control（RL-trained memory operations — Agentic Memory, AgeMem）

### Five Mechanism Families
1. **Context-resident compression** — summarization, chain-of-thought
2. **Retrieval-augmented stores** — RAG-style, vector + structured
3. **Reflective self-improving** — Generative Agents observation–reflection–planning
4. **Hierarchical virtual context** — MemGPT OS-inspired paging（main/RAM vs recall/SSD vs archival/cold）
5. **Policy-learned management** — end-to-end RL for store/retrieve/summarize/forget

### Three Architecture Patterns
- **Pattern A: Monolithic context** — all in prompt, zero infra, capacity-capped
- **Pattern B: Context + retrieval store** — working memory in window, long-term in external store（**workhorse pattern, most production agents**）
- **Pattern C: Tiered memory + learned control** — MemGPT, AgeMem; most capable but highest complexity

**Recommendation from paper**: Start with Pattern B, instrument thoroughly, graduate to Pattern C only when data shows meaningful improvement.

### Engineering Realities（Section 7）
- **Write-path filtering**: importance scoring, deduplication, staleness detection
- **Contradiction handling**: temporal versioning（prefer newest）, source attribution（user statement >> agent inference）
- **Latency budgets**: async writes, progressive retrieval, dynamic routing（skip retrieval for simple queries）
- **Privacy/deletion**: encryption at rest/in transit, per-user scoping, PII redaction, configurable retention, auditable deletion. Machine unlearning when memories leak into weights.
- **Observability**: memory operation logging, memory diff between turns, regression test suites for retrieval quality

### Key Empirical Results
- Voyager without skill library: 15.3× slower tech-tree milestone
- MemoryArena: swapping active memory → long-context-only drops task completion 80%→45% on interdependent multi-session tasks
- Generative Agents: removing reflection → coherent multi-day → repetitive context-free within 48 simulated hours

### Open Challenges（Section 9）
1. Principled consolidation — dual-buffer probation period for new memories
2. Causally grounded retrieval — retrieve by cause, not semantic similarity
3. Trustworthy reflection — external validation, uncertainty quantification, adversarial probing
4. Learning to forget — selective forgetting under safety/compliance constraints
5. Multimodal/embodied memory — spatial, cross-modal retrieval
6. **Multi-agent memory governance** — access control over shared stores, concurrent write consensus, per-agent cache hierarchy
7. Memory-efficient architectures — sparse retrieval, memory-native transformers
8. Foundation models for memory management（foundation model for write/retrieve/summarize/forget）
9. Standardized evaluation — GLUE-style shared leaderboard for agent memory

## Hermes 啟發

### 現有系統對應
| Hermes 元件 | Paper 分類 |
|------------|-----------|
| `session_search` | Pattern B retrieval store（vector-indexed, but Hermes is text search not ANNS） |
| `memory-consolidator` | Write path — summarization + dedup |
| `heartbeat/snapshot.py` session review | Episodic record capture |
| `validate_note` / `sanitize_fetch` | Write-path filtering（importance/quality gate） |
| DCG governance | Multi-agent memory governance（access control） |
| `heartbeat_learning.py` | Policy-learned pattern extraction（learned control萌芽） |

### Gap 分析
1. **No Pattern C tiered memory** — Hermes lacks hierarchical paging（main/recall/archive）; consolidator is flat summarization not tiered
2. **No reflective self-improvement loop** — `heartbeat_learning.py` extracts patterns but no closed-loop verification against actual agent behavior
3. **No learned control** — heartbeat scoring is heuristic, not RL-trained
4. **Observability gap** — memory operation logging exists（severity logs）but no "memory diff" between cycles
5. **Multi-agent memory governance** — DCG provides command-level governance but no shared memory store with per-agent access scoping

### 可行動的方向
- **WS-020（Write Queue）+ DCG**：Pattern B 的 shared write coordination，減少 concurrent write corruption
- **heartbeat/snapshot.py phase detection**：可以用 Paper 的 episodic→semantic consolidation 框架強化（when does a session phase "graduate" to cross-session fact?）
- **Memory observability**：參考 Section 7.7，在 snapshot pipeline加 memory-diff 報告

## 未追蹤 Leads
- https://arxiv.org/html/2601.01885 — Agentic Memory（learned memory control, RL GRPO training）
- https://arxiv.org/html/2602.16313 — MemoryArena benchmark
- https://arxiv.org/html/2506.21605 — MemBench
- https://mem0.ai/blog/state-of-ai-agent-memory-2026 — Mem0 2026 survey（State of AI Agent Memory）
- https://atlan.com/know/best-ai-agent-memory-frameworks-2026/ — Atlan framework comparison

## ✅ 本次探索完成
