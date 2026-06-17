---
_slug: 40-Resources-_mixed-explorations-2026-05-27-yantrikdb-cognitive-memory
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-yantrikdb-cognitive-memory.md
title: YantrikDB — Cognitive Memory Database for AI Agents
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# YantrikDB — Cognitive Memory Database for AI Agents

**Date**: 2026-05-27
**Source**: https://github.com/yantrikos/yantrikdb-server (147 ⭐)
**Type**: exploration

---

## TL;DR

A memory database that does more than store — it **forgets**, **consolidates**, and **detects contradictions**. Built on Tulving's memory taxonomy (semantic/episodic/procedural). Architecture: 5 indexes (vector HNSW + graph + temporal + decay heap + KV). Written in Rust, ships as library/MCP server/HTTP cluster.

---

## Core Differentiation vs. Existing Solutions

| Solution | What it does | What it lacks |
|----------|-------------|---------------|
| Vector DBs (Pinecone, Weaviate) | Nearest-neighbor lookup | No decay, no causality, no self-organization |
| Knowledge Graphs (Neo4j) | Structured relations | Poor for fuzzy memory, not adaptive |
| Memory Frameworks (LangChain, Mem0) | Retrieval wrappers | Not a memory architecture — just middleware |
| File-based (CLAUDE.md) | Dump everything into context | O(n) token cost, no relevance filtering |

**YantrikDB's claim**: At 5,000 memories, file-based exceeds 200K context; YantrikDB stays at ~70 tokens per recall. Precision *improves* with more data.

---

## Five Indexes, One Engine

```
Vector (HNSW)   — semantic similarity search
Graph           — entity relationships, profile aggregation, bridge detection
Temporal        — time-aware queries ("what happened Tuesday")
Decay Heap      — importance scores that degrade over time
Key-Value       — fast facts, session state, scoring weights
```

Combined into a multi-signal scoring: `recency × importance × similarity × graph_proximity`.

---

## Key Capabilities

### 1. Temporal Decay
```python
db.record("read the SLA doc by Friday", importance=0.4, half_life=86400)  # 1 day
# 24h later: relevance score has decayed
# 7 days later: stops surfacing unless explicitly queried
```

### 2. Consolidation (`think()`)
```python
for note in meeting_notes:
    db.record(note, namespace="standup-2026-04-12")
db.think()
# → {"consolidation_count": 5}  # collapsed 20 fragments into 5 canonical memories
```

`think()` runs: consolidation + conflict scan + pattern mining + trigger evaluation.

### 3. Contradiction Detection
```python
db.record("CEO is Alice")
db.record("CEO is Bob")  # added later in another conversation
db.think()
# → {"conflicts_found": 1, "conflicts": [{"type": "factual_contradiction"}]}
```

Conflict resolution is conversational — the AI asks naturally, not programmatically.

### 4. Procedural Memory
Strategies that worked before get recorded and reinforced. "Deploy with blue-green, not rolling update."

### 5. Proactive Triggers
System surfaces:
- Memory conflicts needing resolution
- Approaching deadlines
- Patterns detected across domains
- High-importance memories about to decay

---

## Tulving's Memory Taxonomy (built-in)

| Type | Stores | Example |
|------|--------|---------|
| Semantic | Facts, knowledge | "User is a software engineer at Meta" |
| Episodic | Events with context | "Had a rough day at work on Feb 20" |
| Procedural | Strategies, what worked | "Deploy with blue-green, not rolling update" |

---

## Research: "Skill as Memory, Not Document" (May 2026)

Sarkar, P. (2026). Zenodo.

On a 5,000-skill corpus:
- **Token cost**: full-catalog disclosure = 919,200 tokens (exceeds 200K window). YantrikDB indexed top-K = 369 tokens, constant in catalog size.
- **Latency**: p50 = 87.3ms, p95 = 106.3ms at 5,000-skill scale.
- **Invalid-skill admission**: YantrikDB rejects 70/70 adversarially-malformed skills (0%); document-only baseline admits 68/70 (97%).

**Core insight**: "skill catalogs for autonomous learning aren't documents; they're memory."

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   YantrikDB Engine                    │
│  ┌──────────┬──────────┬──────────┬──────────┐       │
│  │  Vector  │  Graph   │ Temporal │  Decay   │       │
│  │  (HNSW)  │(Entities)│ (Events) │  (Heap)  │       │
│  └──────────┴──────────┴──────────┴──────────┘       │
│  ┌──────────┐                                        │
│  │ Key-Value│  WAL + Replication Log (CRDT)          │
│  └──────────┘                                        │
└──────────────────────────────────────────────────────┘
```

---

## Hermes Relevance

1. **Contradiction detection for heartbeat_learning.py**: YantrikDB's `db.think()` conflict scan is exactly what the distillate drift problem needs. A periodic conflict scan between consecutive distillates could catch semantic reversals before they propagate.

2. **Procedural memory pattern**: `record_procedural()` / `surface_procedural()` mirrors what `heartbeat_learning.py` does — extracting stable patterns from episodic data. The difference: YantrikDB has explicit procedural memory type; Hermes uses distillation as implicit procedural capture.

3. **Tulving taxonomy mapping to Hermes**:
   - Semantic → `memory-consolidator` (persistent facts about workspace)
   - Episodic → session threads (events with context)
   - Procedural → `heartbeat_learning.py` distillates (stable strategies)

4. **Multi-signal scoring**: recency × importance × similarity × graph_proximity. Hermes currently lacks importance weighting and graph proximity in memory scoring.

5. **"Skill as Memory" paper**: The 5,000-skill corpus experiment is directly relevant to WS-035 (Policy Engine) and any skill catalog scaling work. Token cost stays constant (369 tokens) vs O(n) for file-based.

---

## 未追蹤 leads

- https://yantrikdb.com/papers/skill-substrate — "Skill as Memory, Not Document" companion blog post
- https://github.com/yantrikos/yantrikdb-server/blob/main/DESIGN.md — detailed design doc
- benchmarks/skill_recall/ — reproducible code + raw CSVs from the paper

## ✅ 本次探索完成
