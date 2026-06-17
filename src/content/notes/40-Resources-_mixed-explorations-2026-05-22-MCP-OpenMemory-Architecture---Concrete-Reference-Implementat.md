---
_slug: 40-Resources-_mixed-explorations-2026-05-22-MCP-OpenMemory-Architecture---Concrete-Reference-Implementat
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-MCP-OpenMemory-Architecture---Concrete-Reference-Implementat.md
title: MCP OpenMemory Architecture — Concrete Reference Implementation
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- abstract
- context
- last
- llm
- mcp
- memory
- messages
- openmemory
- source
- timestamp
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# MCP OpenMemory Architecture — Concrete Reference Implementation

**日期**: 2026-05-22
**來源**: GitHub (`baryhuang/mcp-openmemory`, ⭐73, JS)
**延續自**: [[2026-05-22-MCP-OpenMemory---Concrete-MCP-Memory-Server-Reference]]

---

## Per-Source Insight

### MCP OpenMemory — Concrete Implementation Analysis

**Article**: GitHub README + server source + memory service source
**Type**: Live MCP server source code

---

## Architecture Overview

```
MCP Client (Claude/Cursor)
    ↓ stdio
MCP OpenMemory Server (Node.js)
    ↓
SQLite (local file via MEMORY_DB_PATH env)
```

**Four tools** exposed:

| Tool | Purpose | Key params |
|------|---------|------------|
| `save_memory` | Store individual messages | speaker, message, context |
| `recall_memory_abstract` | Get processed summary | force_refresh (optional) |
| `update_memory_abstract` | Save new/updated summary | abstract, last_processed_timestamp |
| `get_recent_memories` | Get raw messages, last N days | max_days (default: 3) |

Plus: MCP **Resources** (`memory://schema`, `memory://stats`) and **Prompts** (`memory_summary`).

---

## Key Implementation Details

### Database Schema (via `database.js`)

SQLite with tables for:
- `memories` — raw messages (speaker, message, context/timestamp, sequence)
- `memory_abstracts` — summaries (abstract_content, last_processed_timestamp)
- Implicit stats tracking (phone numbers, agents)

### Soft Namespace via `context` Field

Rather than separate DB files, the system uses a `context` field on `save_memory` to segment:
```javascript
{ speaker: "user", message: "...", context: "project-x" }
```
This is soft namespace — all in one DB, but queryable by context. Similar to Hermes's scope tagging concept in Mem0 paper.

**Note**: Semantic search explicitly NOT supported ("Semantic search is not supported yet. Open a GitHub issue if needed.")

### Abstract Summarization — No LLM

This is the most important finding: the abstract summarization is **NOT LLM-powered**:

```javascript
// memory.js — combineAbstracts()
combineAbstracts(previousAbstract, newMessages) {
  const newContent = newMessages.slice(0, 10).join('\n');
  return `Previous Summary:\n${previousAbstract}\nRecent Activity:\n${newContent}\n...`;
}
```

Comments in source explicitly say:
> "For now, return the combined abstract without LLM processing"
> "In a real implementation, you would call an LLM API here"

**This means mcp-openmemory is a storage + retrieval system, NOT a summarization system.** The "abstract" is just a sliding window of recent messages concatenated. This is significantly simpler than Mem0's approach.

### Phase-aware Recall

`recallMemoryAbstract` tracks `last_processed_timestamp` per abstract. On subsequent calls:
1. Get existing abstract + last_processed_timestamp
2. Fetch only messages after that timestamp
3. Combine with previous abstract
4. Save new abstract with updated timestamp

This is similar to MemR³'s incremental update concept — processing only new messages, not reprocessing the entire history. But mcp-openmemory achieves it via a simple timestamp gate rather than a confidence-gap loop.

### MCP Resources + Prompts

MCP OpenMemory uses the full MCP capability surface:
- **Resources**: `memory://schema` (DB schema as JSON), `memory://stats` (aggregated stats)
- **Prompts**: `memory_summary` — returns a prompt template with memory content

The prompt feature is interesting: `GetPromptRequestSchema` returns a pre-filled prompt that the LLM can then process. This means the LLM decides when/how to ask for its own memory rather than the system proactively injecting it.

---

## Comparison with Hermes Memory Architecture

| Dimension | mcp-openmemory | Hermes (proposed) |
|-----------|----------------|-------------------|
| Storage | SQLite, single file | TBD (FTS5?) |
| Retrieval | Raw messages + simple abstract | MemR³ evidence-gap |
| Summarization | String concatenation (no LLM) | LLM-powered |
| Namespace | Soft (context field) | Hard (per-agent, per-session) |
| Semantic search | ❌ Not supported | ✅ (MemR³) |
| MCP surface | Full (tools+resources+prompts) | ✅ (WS-022) |
| Multi-user | Single-user design | Multi-agent (Hestia/Talos) |

---

## Synthesis with Prior Notes

**Mem0 paper** (ECAI 2025): Multi-signal retrieval (semantic + BM25 + entity), LLM-based entity linking, ADD-only memory model. Mem0 is sophisticated but complex.

**mcp-openmemory**: Simpler — pure storage with timestamp-gated incremental updates. No LLM summarization. No semantic search. But it's a real, working system.

**Gap this reveals**: Mem0 is too complex for Hermes's current needs; mcp-openmemory is too simple. The sweet spot might be:
- mcp-openmemory's **timestamp-gated incremental update pattern** (simple, no LLM needed)
- + Mem0's **multi-signal retrieval** (semantic, keyword, entity — but deferred, not blocking)
- + DeepEval's **G-Eval** for rubric scoring (WS-024 upgrade path)

**For session_tree_phase_navigation proposal (WS-025)**: The phase tree's `last_processed_timestamp` can gate retrieval similarly to mcp-openmemory's abstract refresh. Each phase has a timestamp; only phases updated since last query need re-examination.

---

## 未追蹤

- https://github.com/baryhuang/mcp-openmemory — source for memory.js + database.js (fetched above)
- `combineAbstracts` and `createSimpleSummary` are stubs — could fork + add DeepSeek LLM call for real summarization

---

## ✅ 本次探索完成

**時間**: 2026-05-22 07:10 CST
**Token cost**: 低（2次 fetch，JS source 乾淨）
**品質**: 高 — live production MCP server, full source available
**價值**: Confirmed timestamp-gated incremental update is a valid simple pattern; mcp-openmemory is a storage system, not a summarization system (key insight: the "abstract" is just concatenated messages)
