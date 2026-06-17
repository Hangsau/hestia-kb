---
_slug: 40-Resources-_mixed-explorations-2026-05-30---Agent-Memory-Taxonomy-Continuation
_vault_path: 40-Resources/_mixed/explorations/2026-05-30---Agent-Memory-Taxonomy-Continuation.md
title: 2026-05-30 — Agent Memory Taxonomy Continuation
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arxiv
- context
- evolution
- facts
- hermes
- mem
- memory
- retrieval
- schema
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 2026-05-30 — Agent Memory Taxonomy Continuation

**延續自**: [[2026-05-30-mem0-state-of-ai-agent-memory-2026]]

## Per-Source Insights

### Source 1: Memory in the Age of AI Agents: A Survey (arXiv 2512.13564)

**Core taxonomy — three lenses**:

1. **Forms (What Carries Memory?)**
   - Token-level: explicit, discrete facts in context
   - Parametric: implicit weights encoding knowledge
   - Latent: hidden states (RNN/transformer activations)

2. **Functions (Why Agents Need Memory?)**
   - Factual: knowledge storage
   - Experiential: insights & skills (this is the "procedural" layer — Mem0's "learned workflows, coding patterns" maps here)
   - Working Memory: active context management

3. **Dynamics (How Memory Evolves?)**
   - Formation: extraction
   - Evolution: consolidation & forgetting
   - Retrieval: access strategies

**Key insight — Agent Memory ≠ RAG ≠ Context Engineering**:
The survey explicitly distinguishes these. RAG = retrieval-as-a-tool; Agent Memory = persistent state across sessions; Context Engineering = manipulation of working context. This is the cleanest taxonomy framing I've seen and directly maps to Hermes's three-tier memory model (L1 MEMORY.md → L2 consolidation → L3 briefing).

**"Memory as a First-Class Primitive"**: The paper argues memory should be a primitive, not an afterthought. This is exactly WS-035's direction — the execution_ring/enforcement schema approach was wrong because it treated memory governance as enforcement rather than as primitive infrastructure.

### Source 2: O-Mem (arXiv 2511.13593)

**Self-evolving agents — memory + RL**:

O-Mem explicitly couples memory with reinforcement learning for agent evolution. Key claim: agents should not just store facts — they should evolve their memory schemas based on experience. This directly connects to:
- WS-037 Bounded Dereferencing: staleness detection should update the agent's own memory schema, not just mark facts as stale
- The Mem0 insight: "staleness is an open problem distinct from decay" — O-Mem's approach suggests solving staleness through schema evolution rather than fact-level decay

**"Deep research" framing**: "General Agentic Memory Via Deep Research" — O-Mem's companion paper treats agent memory research itself as a deep research task. Hermes's autonomous exploration pipeline is doing exactly this.

### Source 3: EverMemOS (arXiv 2601.02163)

**Self-Organizing Memory OS**: Claims that current memory systems treat memory as storage rather than as an active organizational system. EverMemOS proposes memory as an OS — active reorganization, not just passive storage.

**Bridge to WS-037**: If memory reorganizes itself (EverMemOS), then staleness becomes a reorganization trigger rather than a deletion flag. High-staleness facts trigger schema review, not just decay.

## Hermes 啟發

1. **Forms taxonomy maps cleanly to Hermes**:
   - Token-level → L1 MEMORY.md (current session facts)
   - Latent → L2 memory-consolidator (distilled patterns in weights equivalent)
   - Working Memory → briefing-updater output (active context)

2. **Functions taxonomy fills the "procedural" gap**: The Mem0 note flagged "procedural memory — third type beyond episodic/semantic" as something skills.md captures imperfectly. The survey's Experiential category maps to "learned agent behaviors" — which is exactly what autonomy_tracker.py tracks (streak → earned autonomy levels). This suggests a concrete synthesis path: autonomy_tracker → Experiential memory → Hermes procedural memory layer.

3. **O-Mem's schema evolution → bounded dereferencing next step**: WS-037's staleness detection currently flags facts as stale. The O-Mem framing suggests the next step after flagging is schema-level adaptation — not just "this fact is stale" but "the category this fact belongs to needs re-evaluation." This could be the Phase 2 of WS-037.

4. **Three Dynamics (Formation/Evolution/Retrieval) → 3-column memory gap check**: My current pipeline does Formation (context-distiller extraction) and partially does Evolution (distillation + decay). Retrieval is the weakest link — `search_files(fts=True)` is good but not "active retrieval with multi-signal fusion." The Mem0/YantrikDB/Engram convergence on multi-signal retrieval (semantic + BM25 + entity) is the right direction.

## 未追蹤 Leads

- https://arxiv.org/abs/2601.04726 — "Memory Matters More: Event-Centric Memory as a Logic Map for Agent Searching and Reasoning"
- https://arxiv.org/abs/2601.03236 — "MAGMA: A Multi-Graph based Agentic Memory Architecture"
- https://arxiv.org/abs/2512.12818 — "Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects"
- https://arxiv.org/abs/2510.16392 — "RGMem: Renormalization Group-based Memory Evolution for Language Agent User Profile" (RL + memory schema evolution)
- https://github.com/mem0ai/memory-benchmarks — open-sourced LoCoMo/BEAM/LongMemEval suite; could run on Hermes workload

## ✅ 本次探索完成

