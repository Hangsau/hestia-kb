---
_slug: 40-Resources-_mixed-explorations-2026-05-28-探索-Agent-記憶架構---Metamind---Entelgia---結構化收斂
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-探索-Agent-記憶架構---Metamind---Entelgia---結構化收斂.md
title: 探索：Agent 記憶架構 — Metamind + Entelgia + 結構化收斂
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- based
- decay
- entelgia
- layer
- llm
- memory
- metamind
- observer
- pattern
- time
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 探索：Agent 記憶架構 — Metamind + Entelgia + 結構化收斂

**日期**: 2026-05-28 | **來源**: HN Algolia (LLM agent memory architecture) | **類型**: Exploration

---

## Metamind — Cognitive architecture for LLM agents

**Source**: HN Show HN (bikidev, 2025-12-22) | points: low (1 pt, early-stage)

### Architecture
- Triple-layer memory: **episodic** (conversations) + **semantic** (KG) + **vector** (HNSW similarity)
- Single Rust binary, single-file DB (no Postgres/Redis/vector DB)
- Multi-user with data isolation
- **HNSW for O(log n) vector search** (not naive brute force)
- Cognitive processes: **salience-based decay, memory consolidation, pattern detection**

### Key insight
> "Every conversation starts from scratch, and existing memory solutions felt like overkill for what should be a simple problem."

Direct CRUD path: LLM only at **write time** to generate embedding. All reads = pure DB queries.

### Rejected pattern (per author)
- Mem0/Zep/Letta route ALL reads/writes through LLM → 200-500ms latency + token costs on memory layer
- Metamind: direct database CRUD, semantic search uses pgvector + Bedrock Titan embeddings, LLM only at write time

### Memory types
1. **Working memory**: key-value state (sub-10ms reads)
2. **Semantic memory**: vector-searchable facts (pgvector)
3. **Episodic memory**: time-stamped event logs (S3 + DynamoDB)
4. **Procedural memory**: rules and tool definitions (coming v0.2)

---

## Entelgia — consciousness-inspired multi-agent with persistent memory

**Source**: HN Show HN (sivanhavkin, 2026-02-09) | points: very low (1 pt) — but architecture is rich

### Architecture
- Three agents: **Socrates** (investigator), **Athena** (strategic synthesizer), **Fixy** (meta-cognitive observer)
- **Persistent memory**: short-term (JSON LRU) + long-term (SQLite + STM)
- **id/ego/superego dynamics** — internal conflict drives memory promotion
- **Memory promotion through error, repetition, and affect**
- Bounded short-term memory (LRU)
- **Observer-based correction loops** (meta-cognitive layer)
- **Energy-based regulation** — dream cycle consolidation, hallucination-risk detection
- Emotion tracking + importance scoring
- PII redaction, memory poisoning protection
- 2460 tests across 42 suites

### Observer correction loop (key pattern)
Fixy (observer agent) identifies contradictions and reasoning gaps → emits soft signals → consumed by IntegrationCore → regulates behavior. This is a **closed-loop self-correction** mechanism.

### Dream cycle consolidation
Energy-based regulation triggers "dream cycles" where memory consolidation happens off-line. Detects hallucination-risk states and triggers consolidation.

---

## 跨文章 Synthesis

### 收斂點 1: 結構化 > 純嵌入
所有三個系統（Metamind, Entelgia, prior art MuninnDB/YantrikDB）都收斂到「結構化記憶 > 純嵌入檢索」：
- Metamind: 4 memory types (working/semantic/episodic/procedural), LLM只在write time
- Entelgia: triple-layer + affect + drive + observer loop
- MuninnDB: Ebbinghaus decay + Hebbian learning
- YantrikDB: 5-layer index (HNSW+graph+temporal+decay+KV)

**Pattern**: Production-grade memory systems need **typed memory tiers** (not flat vector store) + **explicit consolidation policy** (not just retrieval).

### 收斂點 2: Bounded memory + decay
- Entelgia: **bounded LRU** short-term, salience-based promotion
- Metamind: salience-based decay + pattern detection
- MuninnDB: Ebbinghaus decay curve
- YantrikDB: temporal decay

**Pattern**: Unbounded memory growth is the #1 failure mode. Every system enforces hard bounds (LRU, time-based decay, salience threshold).

### 收斂點 3: Observer / meta-cognitive layer
- Entelgia: Fixy (observer) → IntegrationCore → behavior regulation
- YantrikDB: contradiction detection layer
- AGT: Hypervisor guardrails (privilege rings)
- WS-028: 4-layer enforcement (deny-always-wins policy engine)

**Pattern**: Production multi-agent systems need a **separate monitoring layer** that watches the main agent from outside its execution path. This is distinct from tool-scoping (which is L1) — observer loops operate at the **dialogue/decision layer**.

### 收斂點 4: LLM位置 — write-time only
- Metamind: LLM only at write time (embedding generation), reads = pure DB
- Mnemora: same pattern, DynamoDB sub-10ms reads
- Mem0 (criticized): LLM in both read and write path → 200-500ms + token costs

**Pattern**: The "LLM in CRUD path" is an anti-pattern for production memory. Embedding generation (write time) is the right LLM touchpoint; retrieval should be pure DB/vector ops.

### Gap: heartbeat_learning.py drift penalty
None of these systems have an **explicit semantic drift penalty** in their consolidation logic:
- Metamind: salience-based decay, pattern detection
- Entelgia: affect + repetition triggers promotion
- MuninnDB: Ebbinghaus curve
- **None** explicitly penalize **semantic contradiction** with prior distilled conclusions

This validates WS-035 / heartbeat_learning.py upgrade direction: explicit **contradiction detection** (Beads/Structure-Before-Content pattern) should gate distillation, not just salience.

### Gap: Hermes governance
Entelgia's id/ego/superego + Observer loop is architecturally similar to what WS-028 (Talos governance pipeline) is building:
- Observer = policy enforcement layer (reads-only, doesn't execute)
- Fixy = drift detection sensor
- IntegrationCore = enforcement action selector
- **But Entelgia is dialogue-governed; Talos needs decision-governed**

WS-028's 4-experiment COMPLETED status suggests the enforcement architecture is mature enough to benefit from Entelgia's Observer pattern transplant.

---

## ✅ 本次探索完成

### 未追蹤 Leads
- https://github.com/quantifylabs/aegis-memory (Aegis Memory v1.2, 70% cost reduction via rule-based pre-filter)
- https://github.com/mnemora-db/mnemora (Mnemora, serverless, no LLM in CRUD path)
- Entelgia whitepaper: https://doi.org/10.5281/zenodo.18754895 (full ablation study)
- Entelgia attractors paper: https://doi.org/10.5281/zenodo.18774720
- Metamind repo URL not found ( HN story had no external URL, just HN discussion page — unreachable without JS)
