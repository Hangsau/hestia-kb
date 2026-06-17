---
_slug: 40-Resources-_mixed-explorations-2026-06-04-2026-06-04---Rust-Agent-Memory-Primitives
_vault_path: 40-Resources/_mixed/explorations/2026-06-04-2026-06-04---Rust-Agent-Memory-Primitives.md
title: 2026-06-04 — Rust Agent Memory Primitives
date: 2026-06-04
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- based
- decay
- forget
- mattbusel
- memory
- multi
- rust
- tokio
- working
created: '2026-06-04'
updated: '2026-06-15'
status: budding
---

# 2026-06-04 — Rust Agent Memory Primitives

**延續自**: 無（autonomous_notes 為空，首次探索）

## Sources

### tokio-agent-memory (Mattbusel/rust-crates)

Tokio-native agent memory system. GitHub API → README.md (raw, no sanitize needed).

**Architecture — 8 modules**:

| Module | Description |
|--------|-------------|
| `episodic` | Timestamped event log with causal chain linking, temporal recall, forget |
| `semantic` | Concept graph with typed assertions, BFS relation traversal, retraction |
| `working` | Priority-slotted working memory with LRU eviction, capacity control |
| `decay` | `DecayScheduler` with exponential and linear policies; configurable forget thresholds |
| `retrieval` | Multi-strategy: exact, fuzzy, temporal, tag-based, confidence-filtered |
| `persistence` | `InMemoryStore` + `FileStore` behind `MemoryStore` trait |
| `shared` | `SharedMemoryBus` — broadcast pub/sub with lease-based exclusive access |
| `consolidation` | `Consolidator` — promotes working→episodic/semantic based on importance |

**Key patterns**:
- DecayScheduler supports both exponential and linear decay — directly addresses the Ebbinghaus decay curve referenced in YantrikDB/MuninnDB explorations
- SharedMemoryBus uses lease-based exclusive access for multi-agent coordination — concrete implementation of guardian-sandboxing-gradient L3 (container-level isolation)
- MemoryStore trait abstraction enables pluggable backends (Redis, SQLite, S3) — aligns with WS-035's portable memory design
- Consolidation pipeline with importance-based promotion — similar to agentmemory's 4-tier consolidation (Working→Episodic→Semantic→Procedural)
- 120+ tests across unit/integration/multi-module pipeline suites

**Used in**: `tokio-prompt-orchestrator` — running 24 simultaneous Claude Code agents in production.

### tokio-memory (Mattbusel/rust-crates)

Simpler/higher-level version of tokio-agent-memory. `MemorySystem` facade with same tier model.

**Quick start** shows `memory.remember()` / `memory.recall_by_tag()` async API pattern:
```rust
memory.remember("user asked about Paris", &["geography", "user"]).await;
let results = memory.recall_by_tag("geography").await;
```

**DecayScheduler** same design as tokio-agent-memory: configurable linear/exponential decay + forget thresholds.

### localmind (nevenkordic/localmind)

5 stars, SQLite-backed hybrid memory for local LLM via Ollama. CLI agent with persistent context.

## Hermes Insights

1. **Consolidation pipeline is the missing piece**: Both Rust crates implement `Consolidator` that moves working→episodic/semantic based on importance scores. This directly answers the staleness-detection gap in `heartbeat_learning.py` — instead of time-based decay alone, a consolidation step would evaluate importance and promote/retain accordingly.

2. **DecayScheduler (exponential + linear) + forget thresholds**: This is the concrete Ebbinghaus implementation referenced in past explorations (MuninnDB, YantrikDB). Configurable forget thresholds per memory tier — high-importance items survive longer. Directly applicable to `heartbeat_learning.py` distillate confidence tracking.

3. **SharedMemoryBus for multi-agent coordination**: Typed pub/sub with lease-based exclusive access prevents write conflicts across agents. Concrete pattern for Talos governance pipeline's single-writer queue design.

4. **MemoryStore trait for portability**: Plug in Redis/SQLite/S3 by implementing one trait. WS-035 could adopt same pattern for Hermes memory backend abstraction.

5. **120+ tests on tokio-agent-memory**: Production-tested with multi-agent orchestration (24 Claude Code agents). Architecture credibility reinforced by actual deployment scale.

## Untracked Leads

- https://github.com/Mattbusel/tokio-prompt-orchestrator — production orchestrator running 24 agents, may have more architecture details
- https://github.com/Mattbusel/llm-budget — hard budget enforcement, per-model/agent/fleet accounting, relevant to Hermes cost governance
- https://github.com/Mattbusel/llm-sync — CRDT + vector clock for distributed agent state sync

## ✅ 本次探索完成
