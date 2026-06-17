---
_slug: 40-Resources-_mixed-explorations-2026-05-30---LLM-Agent-Memory-Architecture---Survey---2026-B
_vault_path: 40-Resources/_mixed/explorations/2026-05-30---LLM-Agent-Memory-Architecture---Survey---2026-B.md
title: 2026-05-30 | LLM Agent Memory Architecture — Survey + 2026 Benchmarks
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- architecture
- context
- control
- entity
- mem
- memory
- multi
- retrieval
- survey
- three
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 2026-05-30 | LLM Agent Memory Architecture — Survey + 2026 Benchmarks

**延續自**: 無（全新探索）

## Per-Source Insights

### 1. arXiv:2603.07670v1 — "Memory for Autonomous LLM Agents" (March 2026)

Survey from Hong Kong Research Institute, covering 2022–early 2026. Three-axis taxonomy:

**Taxonomy dimensions:**
- **Temporal scope**: Working / Episodic / Semantic / Procedural — mirrors Tulving's human memory model; most agents blend ≥2 layers
- **Representational substrate**: Context-resident text / Vector indexes / Structured stores (SQL, KG) / Executable repos — hybrid is norm
- **Control policy**: Heuristic → Prompted self-control (MemGPT) → Learned control (Agentic Memory/Yu 2026 via RL)

**Five mechanism families:**
1. Context-resident compression (summarize, scratchpad, CoT)
2. Retrieval-augmented stores (RAG → memory)
3. Reflective self-improvement (Reflexion verbal self-critique)
4. Hierarchical virtual context (MemGPT tiered: main memory + recall + archive)
5. Policy-learned management (Agentic Memory, RL end-to-end)

**POMDP formulation** — memory as belief state:
- `a_t = πθ(x_t, R(M_t, x_t), g_t)` — policy reads from memory
- `M_{t+1} = U(M_t, x_t, a_t, o_t, r_t)` — write path does summarization/dedup/conflict resolution, not just append

**Key empirical results:**
- Generative Agents: removing reflection → degenerate to repetitive within 48 sim hours
- Voyager: without skill library → 15.3× slower tech-tree milestones
- MemoryArena: swap active memory for long-context-only → 80% → 45% on multi-session tasks

**Engineering patterns (three clusters):**
- Pattern A: Monolithic context (cap-limited, zero infra)
- Pattern B: Context + retrieval store (workhorse, most production agents)
- Pattern C: Tiered memory + learned control (MemGPT, AgeMem — highest headroom, most engineering cost)

**Seven engineering realities**: write-path filtering, contradiction handling, staleness management, latency budgets, privacy/compliance/deletion, three architecture patterns, observability/debugging.

**Open challenges (10)**:
1. Principled consolidation (hippocampal replay analogy, dual-buffer probation)
2. Causally grounded retrieval (not just similarity — "what caused this?")
3. Trustworthy reflection (avoid entrenching mistakes via confirmation bias)
4. Learning to forget (selective forgetting under safety constraints)
5. Multimodal embodied memory
6. Multi-agent memory governance
7. Memory-efficient architectures
8. Deeper neuroscience integration (spreading activation, reconsolidation theory)
9. Foundation models for memory management
10. Standardized evaluation (GLUE-style shared leaderboard)

**Key quote**: "Memory deserves the same level of engineering investment as the LLM itself. Model selection gets months of careful benchmarking; memory architecture often gets an afternoon."

---

### 2. Mem0 Blog — "State of AI Agent Memory 2026"

Production-focused benchmark landscape:

**Three benchmarks now standard:**
- **LoCoMo**: 1,540 questions, multi-session recall (single/multi-hop, open-domain, temporal)
- **LongMemEval**: 500 questions, knowledge update + multi-session
- **BEAM**: 1M and 10M token scales — cannot be solved by expanding context window alone

**Evaluation dimensions**: BLEU / F1 / LLM judge / token consumption / latency — prevents single-axis optimization

**Mem0 2026 results**:
| Benchmark | Score | Tokens/query |
|-----------|-------|-------------|
| LoCoMo | 92.5 | 6,956 |
| LongMemEval | 94.4 | 6,787 |
| BEAM 1M | 64.1 | 6,719 |
| BEAM 10M | 48.6 | 6,914 |

Biggest gains: +29.6 on temporal reasoning, +23.1 on multi-hop. Driven by:
- **Single-pass ADD-only extraction**: agent confirmations stored with equal weight to user-stated facts
- **Multi-signal retrieval**: semantic similarity + BM25 keyword matching + entity matching, fused into one score

**Architecture evolution**:
- Replaced external graph store support → built-in entity linking during `add()`, parallel `{collection}_entities` collection, entity matches boost final score
- Tradeoff: no longer queryable graph interface (no direct traversal), but entity-aware retrieval without Neo4j overhead

**Multi-scope memory model**: user_id / agent_id / run_id / session_id / app_id compose at retrieval time — ranked merge (user > session > raw history)

**Open problems confirmed**:
- **Memory staleness**: high-relevance memories become confidently wrong (user changes jobs, facts about products). Decay handles low-relevance; staleness in high-relevance is harder — no product solution yet
- **Cross-session identity resolution**: anonymous sessions, multi-device, mixed auth break stable user_id assumption
- **Temporal abstraction**: BEAM 1M→10M drop (64.1→48.6) = ~25% loss at 10× context scale, headroom remains significant

---

## Cross-Article Synthesis

**Convergence point**: Both sources agree on three-layer temporal memory (episodic/semantic/procedural) and the inadequacy of pure vector similarity. The survey formalizes the mechanism taxonomy; the Mem0 blog provides benchmarked evidence that multi-signal retrieval (semantic + keyword + entity) outperforms single-signal semantic alone.

**Distinct contribution**: The survey (2603.07670) is the theoretical framework — POMDP formulation, ten open challenges, principled consolidation via dual-buffer probation. The Mem0 blog is the empirical production data — benchmarks with numbers, 21 framework integrations, vector store proliferation landscape.

**For Hermes heartbeat_learning.py**: The staleness problem (both sources flag it as unsolved) directly explains the drift behavior observed in heartbeat distillates. The survey's "recursive dependence" framing — bad writes pollute downstream — is the correct mental model for why drift compounds. The Mem0 2026 algorithm's entity linking approach (entity extraction at write time → parallel entity collection → fused score at read time) is a concrete architecture pattern that could inform the drift penalty design.

**Design convergence**: Both sources independently point to "structured > pure embedding" — the survey via knowledge graphs and structured stores, Mem0 via entity linking replacing external graph stores. This strengthens the WS-035 direction: structured extraction with confidence + Ebbinghaus decay + Hebbian edges is the right architecture, not pure vector similarity.

---

## Untracked Leads

- Agentic Memory (Yu et al. 2026, arXiv:2601.01885) — RL-trained memory management, three-stage GRPO pipeline. Referenced in survey as exemplar of learned control. Not yet fetched.
- MemBench (Tan et al. 2025) — referenced in survey, 1,540 questions across 4 categories. GitHub: mem0ai/memory-benchmarks
- MemoryArena (He et al. 2026, arXiv:2602.16313) — benchmark at 1M/10M token scale. Full benchmark suite for production-scale evaluation.
- LoCoMo benchmark dataset — open sourced, available for local evaluation
- AgeMem — mentioned in survey's Pattern C as tiered memory + learned control exemplar. Not fetched.

---

## ✅ 本次探索完成
