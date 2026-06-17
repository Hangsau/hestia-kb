---
_slug: 40-Resources-_mixed-explorations-2026-05-30-AgeMem---Zep-Graphiti---GRPO-Memory-Management---Temporal-Kn
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-AgeMem---Zep-Graphiti---GRPO-Memory-Management---Temporal-Kn.md
title: AgeMem + Zep/Graphiti — GRPO Memory Management & Temporal Knowledge Graph
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- architecture
- arxiv
- graph
- graphiti
- grpo
- memory
- policy
- temporal
- zep
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# AgeMem + Zep/Graphiti — GRPO Memory Management & Temporal Knowledge Graph

**日期**: 2026-05-30 | **來源**: arXiv 2601.01885 + arXiv 2501.13956 | **類型**: Exploration
**延續自**: [[2026-05-29-llm-agent-memory-architecture.md]]

---

## Source 1 — AgeMem: Agentic Memory via GRPO (arXiv 2601.01885v2)

**Core architecture:**
- Unified LTM (long-term) + STM (short-term) management integrated into agent policy
- Key innovation: memory operations exposed as **tool-based actions** → LLM agent autonomously decides what/when to store, retrieve, update, summarize, discard
- Training: **3-stage progressive reinforcement learning** — GRPO (Group Relative Policy Optimization) addresses sparse/discontinuous rewards from memory operations
- Five long-horizon benchmarks — AgeMem consistently outperforms MemGPT-style baselines

**Three-stage GRPO pipeline:**
1. Memory operation policy bootstrap
2. Progressive reward shaping
3. End-to-end memory management optimization

**Why this is distinct from Mem0:**
- Mem0 = extraction-only ADD with heuristic retrieval signals (BM25 + semantic + entity)
- AgeMem = learned controller → memory operations are policy decisions, not rules
- This directly speaks to the WS-035 / heartbeat_learning.py design gap: we have decay, but no learned operation selection

**Key framing for Hermes:**
- "Memory operations as tool-based actions" is exactly what a future `memory_controller` skill would implement — but AgeMem shows you need RL training to get the policy right, not just rules
- The 3-stage progressive training suggests a deployment path: start with rules (current heartbeat_learning.py), then graduate to learned controller when metrics show hit quality is the bottleneck

---

## Source 2 — Zep + Graphiti: Temporal Knowledge Graph (arXiv 2501.13956)

**Core architecture:**
- Graphiti = temporally-aware knowledge graph engine that synthesizes conversational data + structured business data while maintaining historical relationships
- Zep = memory layer service built on Graphiti
- DMR (Deep Memory Retrieval) benchmark: Zep 94.8% vs MemGPT 93.4%
- LongMemEval benchmark: up to 18.5% accuracy improvement + 90% latency reduction vs baseline

**What makes Graphiti different from vector RAG:**
- Temporal edges — explicitly models "when" facts occurred and their causal ordering
- KG traversal vs flat similarity search — multi-hop queries don't degrades as badly as pure embedding approaches
- Cross-session synthesis is a first-class query type, not an afterthought

**Key framing for Hermes:**
- The `vault + autonomous_notes` pattern already gives us Graphiti-like raw material (structured notes with timestamps), but we don't yet have a temporal graph query layer
- Zep/Graphiti's 90% latency improvement over naive RAG speaks to the retrieval efficiency gap we identified (Mem0: 6,956 tokens/query vs 26,000 full-context)

---

## Hermes 啟發

1. **AgeMem's "memory as tool actions" framing resolves our design debate**: We used to ask "should forgetting be a first-class operation?" — AgeMem answers YES, as an actionable policy decision, not just an edge case in decay. This aligns with the existing `deprecated` frontmatter pattern in skills.

2. **Three distinct memory architecture learning paradigms now confirmed**:
   - AgeMem (learned controller): RL-trained memory operation policy
   - Zep/Graphiti (temporal knowledge graph): explicit KG + temporal reasoning
   - Mem0 (multi-signal retrieval): extraction + fused BM25/semantic/entity
   - All three outperform naive full-context — validates our path away from pure context stuffing

3. **heartbeat_learning.py gap confirmed — still no learned controller**: Decay (Ebbinghaus) addresses low-relevance gradual forgetting; AgeMem's GRPO pipeline addresses high-value memory operation selection. We have the former; the latter requires RL-style training signal we don't yet have. This is a WS-035 roadmap item.

4. **Temporal graph query ≠ vector similarity**: Graphiti's multi-hop advantage over flat embedding similarity search maps to our vault's wikilink structure — wikilinks are already our "explicit edges," just not yet queryable via KG traversal. Future KB query layer could exploit this.

---

## 未追蹤 Leads

- https://github.com/.../agemem — AgeMem code repo (URL in paper abstract, not fetched)
- https://arxiv.org/abs/2408.17736 — Graphiti associated paper (search)
- https://www.getzep.com — Zep cloud service (managed offering, architecture reference)

---

## ✅ Exploration Complete

