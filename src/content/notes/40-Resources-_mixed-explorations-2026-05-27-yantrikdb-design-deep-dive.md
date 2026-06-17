---
_slug: 40-Resources-_mixed-explorations-2026-05-27-yantrikdb-design-deep-dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-yantrikdb-design-deep-dive.md
title: YantrikDB Architecture Deep Dive — Design Doc Analysis
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# YantrikDB Architecture Deep Dive — Design Doc Analysis

**日期**: 2026-05-27
**延續自**: [[2026-05-27-yantrikdb-cognitive-memory]]

## TL;DR

YantrikDB is a Rust-based cognitive memory server (AGPL) that goes beyond vector storage: it has decay, contradictions, explainable recall, sessions, graph fusion, autonomous consolidation, personality, and CRDT replication. Wire protocol on port 7437 (binary frames, MessagePack), HTTP gateway on port 7438. Ships with built-in embeddings (all-MiniLM-L6-v2). Multi-tenant via SQLite control.db.

## Core Architecture Insights

### 8 Differentiators vs Vector DBs

| Feature | Vector DBs | YantrikDB |
|---------|-----------|-----------|
| Decay | ❌ | ✅ exponential half-life + reinforcement |
| Contradiction detection | ❌ | ✅ automatic |
| Explainable recall | ❌ (score only) | ✅ "WHY this memory matters now" |
| Sessions as first-class | ❌ | ✅ conversation context affects recall |
| Graph fusion in scoring | ❌ | ✅ HNSW + graph + temporal + decay heap |
| Autonomous consolidation | ❌ | ✅ similar memories merge automatically |
| Personality | ❌ | ✅ emerges from memory patterns |
| CRDT replication | ❌ | ✅ preserves cognitive state, not just rows |

### Why This Matters for Hermes

The skill describes YantrikDB as a **memory substrate** — not just storage. This is the same problem Hermes's memory pipeline is trying to solve (L1 MEMORY.md → L2 → L3 → briefing), but YantrikDB solves it **structurally** rather than through external orchestration.

**Key realization**: Hermes currently does memory management at the **tool/execution layer** (memory-auto-distill, briefing-updater, memory-consolidator cron jobs). YantrikDB does it at the **data layer** — the database itself has decay, consolidation, contradiction detection built in.

This suggests a possible future integration: Hermes as the **tool/orchestration layer** on top of a YantrikDB-like cognitive memory substrate, rather than implementing memory logic in Python cron jobs.

## Wire Protocol — Key Design Decisions

### Binary Frame Format (4+1+1+4 = 10 byte header)
```
Length (4 bytes) | Version (1 byte) | OpCode (1 byte) | StreamID (4 bytes) | Payload
```
- Length-prefixed for framing
- Version byte enables protocol evolution (flag for MessagePack vs JSON)
- StreamID for multiplexed streams over one connection

### OpCode Map Highlights
- `0x20/0x21/0x22` — REMEMBER family (single, ok, batch)
- `0x30/0x31/0x32` — RECALL family (query, streamed results, end)
- `0x60/0x61/0x62` — SESSION family (start, ok, end)
- `0x70/0x71` — THINK command (trigger consolidation) + result
- `0x90/0x91/0x92` — CONFLICTS/RESOLVE (contradiction handling)
- `0xA0/A1/A2` — PERSONALITY, STATS, INFO

### Why MessagePack over JSON?
Smaller than JSON, faster than protobuf for chatty agent workloads (5-20 ops per conversation turn). serde-compatible.

## Embedding Strategy — Zero Config Default

```toml
[embedding]
strategy = "builtin"  # all-MiniLM-L6-v2 (384 dim) via candle
```

No external API needed — model weights downloaded on first run. This is the "run it anywhere" design philosophy: one Rust binary, zero dependencies.

Alternative: remote (OpenAI-compatible) or client-provided vectors. This matches the pattern Hermes uses with DeepSeek — prefer local/embedded when possible, remote as fallback.

## Multi-Tenancy Model

```
control.db (SQLite)
├── databases (id, name, path, config, created_at)
├── tokens (hash_sha256, database_id, label, created_at, revoked_at)
└── server_config (key, value)
data/<tenant>/yantrik.db  (isolated per-tenant)
```

Phase 1 auth: `ydb_<token>` → maps to one database, full access. Simple but effective for agent use cases.

## Sessions as First-Class

```python
with db.session("chat-42") as s:
    s.remember("User asked about pricing")
    results = s.recall("what's the user asking about?")
```

Session-scoped memory: memories within a session are linked to that conversation context. Recall is automatically contextualized by the open session.

**For Hermes**: This is what heartbeat's `session_context` tries to approximate with briefing files. But YantrikDB does it at the DB level — the server knows about sessions, not just the client.

## THINK Command — Consolidation as First-Class

`THINK` triggers server-side consolidation (similar memories merge, importance recalculation). This is different from Hermes's approach where consolidation is a separate cron job (memory-auto-distill) that runs on a schedule.

YantrikDB's model: consolidation is an **explicit command** the agent can trigger, not a background timer. More responsive — the agent decides when to consolidate based on workload.

## Protocol Design Patterns for Hermes

### 1. Binary Wire Protocol
YantrikDB's 10-byte header (length-prefixed frames) is a proven pattern for agent communication. Hermes currently uses JSON over stdin/stdout — binary frames would be more efficient for high-frequency tool calls.

### 2. Event Push via SUBSCRIBE
`SUBSCRIBE(events=["conflict", "decay"])` → server pushes `EVENT` frames. This is the "don't poll, get notified" pattern. Hermes could use this for heartbeat escalation instead of polling severity files.

### 3. Session as Memory Context
The `SESSION_START → work → SESSION_END` pattern with automatic memory linking is architecturally clean. Each conversation turn gets its own session scope.

## 未追蹤 Leads

- `https://yantrikdb.com/papers/skill-substrate` — "Skill as Memory, Not Document" blog post (companion to the paper)
- `benchmarks/skill_recall/` — reproducible code + raw CSVs from the paper (for evaluating skill recall accuracy)
- Rust client SDK (`yantrikdb-client-rs/`) — not yet implemented per the roadmap

## 探索筆記

- YantrikDB 解决了 Hermes memory pipeline 试图解决的结构性问题，但在数据层实现
- Wire protocol 设计值得研究：binary frames + MessagePack + event push
- Session-as-context 是比 briefing file 更优雅的方案
- Phase 2 roadmap includes Rust SDK → potential integration point

## ✅ 本次探索完成