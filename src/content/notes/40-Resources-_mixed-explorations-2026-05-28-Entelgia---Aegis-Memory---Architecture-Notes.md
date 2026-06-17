---
_slug: 40-Resources-_mixed-explorations-2026-05-28-Entelgia---Aegis-Memory---Architecture-Notes
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-Entelgia---Aegis-Memory---Architecture-Notes.md
title: Entelgia + Aegis Memory — Architecture Notes
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aegis
- agent
- based
- bounded
- entelgia
- filter
- hermes
- llm
- memory
- owasp
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# Entelgia + Aegis Memory — Architecture Notes
**日期**: 2026-05-28 | **來源**: HN exploration | **類型**: survey
**Tags**: multi-agent-memory, bounded-growth, OWASP, ACE-loop

---

## Entelgia — Bounded Memory + Multi-Agent Dialogue

**URL**: https://github.com/sivanhavkin/Entelgia

### Core Architecture

```
LLM + Persistent Memory + Psychological Drives + Observer Regulation → Dialogue-governed agents
```

Multi-agent system with two primary agents in continuous dialogue, backed by:
- **SQLite + STM** (Software Transactional Memory) for shared persistent memory
- **Bounded short-term memory** (LRU)
- **Memory promotion through error, repetition, affect**
- **Observer-based correction loops** (meta-cognitive layer)

Key design choices:
1. **Deterministic system behavior** — bounded memory growth, structured logging
2. **Privacy/PII redaction** — built-in
3. **Testability and long-running stability** — production rewrite focus
4. **No external dependencies** — single Rust binary option available

### Bounded Memory Pattern (Critical for Hermes)

Entelgia's bounded memory model is the most relevant for heartbeat_learning.py:
- **LRU for short-term** — bounded working memory
- **Memory promotion** — only memories that survive error/repetition/affect get promoted to long-term
- **Decay mechanism** — salience-based forgetting

This directly maps to WS-035's "earned autonomy" concept — memory persistence should require demonstrated stability, not just recency.

### Observer Correction Loop

```
Observer agent → detects behavioral drift → corrective signal → memory update
```

This is analogous to the "Guardian" role in Hermes governance. The observer doesn't control directly — it detects and corrects through the memory layer.

### Hermes Relevance

- **heartbeat_learning.py drift penalty**: The Ebbinghaus decay + Hebbian edges from YantrikDB/MuninnDB notes are reinforced by Entelgia's "memory promotion through error" — errors should create stronger memory traces, not just decay over time.
- **WS-028 Agent Lifecycle Governance**: The observer correction loop maps directly to Phase 3 earned autonomy — agents earn wider scope through demonstrated stability, not time-based promotion.
- **Multi-agent write queue**: Entelgia's STM-based shared memory suggests structured conflict resolution through transactional semantics rather than locking.

---

## Aegis Memory v1.2 — OWASP-Native Context Hub

**URL**: https://github.com/quantifylabs/aegis-memory

### Two-Stage Worth-Recording Filter (70% Cost Saving)

Stage 1: **Rule-based noise filter** — catches greetings, "thanks", obvious noise
Stage 2: **LLM extraction** — only when filter passes

This is the most immediately applicable pattern for Hermes:
- heartbeat_learning.py currently runs LLM distillation on every session summary
- A rule-based pre-filter could skip ~70% of distillations (greetings, simple queries, one-off commands)
- Only sessions with actual behavioral complexity trigger full LLM extraction

### Security Features (OWASP-Native)

Aegis is the only OSS memory layer implementing full OWASP AI Agent Security recommendations:

| Feature | mem0 | Zep | Letta | Aegis |
|---|---|---|---|---|
| Content injection detection | — | — | — | ✅ 4-stage |
| HMAC integrity | — | — | — | ✅ |
| Trust hierarchy | — | — | — | ✅ 4-tier OWASP |
| Per-agent rate limiting | — | — | — | ✅ sliding window |
| Security audit trail | — | — | — | ✅ immutable |

### ACE Loop (Generation → Reflection → Curation)

Stanford/SambaNova research pattern — fully implemented in Aegis:
1. **Generation**: Query playbook for strategies
2. **Reflection**: Auto-vote on used memories, auto-reflect on failures
3. **Curation**: Promote effective patterns, consolidate duplicates

### Hybrid Retrieval

Dense (pgvector cosine) + Sparse (PostgreSQL tsvector) — Reciprocal Rank Fusion. Catches exact-match cases (entity names, error codes, tool names, file paths) that pure embedding similarity misses.

### Contradiction Detection

When two memories contradict → `contradicts` edge with confidence + rationale. Explicit resolution API. This is the "drift detection" pattern for memory itself.

### Hermes Relevance

- **Heartbeat learning cost**: Two-stage filter directly applicable to `heartbeat_learning.py` — rule-based pre-filter before LLM distillation
- **Sanitizer complement**: Aegis's 4-stage content security pipeline is complementary to Hermes's `sanitize_fetch.py` — Aegis for memory writes, Hermes for exploration fetches
- **WS-035 Policy Engine**: The OWASP 4-tier trust hierarchy (untrusted/internal/privileged/system) maps directly to the AGT Hypervisor rings — consistent with the governance architecture already explored

---

## 跨文章 Synthesis

### Convergence Point: Structured > Embedding

Entelgia (consciousness-inspired), Aegis (OWASP-native), YantrikDB (cognitive DB), MuninnDB (Rust) — all converge on structured memory over pure vector search. The exact-match retrieval needs (error codes, file paths, tool names) cannot be reliably handled by embedding similarity.

**Action for Hermes**: Continue WS-035/WS-028 exploration of structured memory patterns. The FTS5 doc index (WS-008) is a step in this direction but scoped to documentation.

### Convergence Point: Bounded Growth via Explicit Pruning

Entelgia (LRU + promotion), Aegis (consolidation with deprecation), YantrikDB (Ebbinghaus decay + transactional forgetting), MuninnDB (prefix-based TTL) — all have explicit memory boundedness.

**Action for Hermes**: heartbeat_learning.py distillate has no boundedness mechanism. Consider adding max_entries + Ebbinghaus-style decay to prevent unbounded growth.

### Cost Optimization: Pre-filter Before LLM

Aegis's 70% cost saving from rule-based pre-filtering is the most immediately actionable finding for Hermes. The current `heartbeat_learning.py` runs LLM distillation on every session — adding a cheap rule-based filter first could dramatically reduce token costs without losing behavioral tracking quality.

## ✅ 本次探索完成

### 未追蹤 Leads

- https://github.com/sivanhavkin/Entelgia (raw README fetched, architecture clear)
- https://github.com/quantifylabs/aegis-memory (raw README fetched, architecture clear)
- https://vinithavn.medium.com/advancing-agentic-memory — deprioritized, likely overlaps with vault notes
