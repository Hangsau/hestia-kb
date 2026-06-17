---
_slug: 40-Resources-_mixed-explorations-2026-06-05-探索-Agent-Memory-Flat-File-Hybrid-Search-Architecture
_vault_path: 40-Resources/_mixed/explorations/2026-06-05-探索-Agent-Memory-Flat-File-Hybrid-Search-Architecture.md
title: 探索：Agent Memory — Flat-File + Hybrid Search Architecture
created: '2026-06-05'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：Agent Memory — Flat-File + Hybrid Search Architecture

**延續自**: [[2026-06-05-state-of-agent-memory-2026]]

**日期**: 2026-06-05
**來源**: https://agent-memory.bruegs.com/

## Per-Source Insight

### Agent Memory Architecture — Nick Brueggeman (March 2026)

**Core architecture: flat-file + hybrid search**

- **74% LoCoMo** with file-only memory — competitive with vector DB and graph store approaches
- **Hybrid search weights**: 0.6 vector / 0.4 BM25 — consistently outperforms either alone
- **Local embeddings**: Qwen3 Embedding 0.6B via LM Studio — 1024 dims, free, fast, competitive with commercial APIs
- **sqlite-vec** — single-file vector DB, no server process, sub-millisecond lookups
- **Zero external API dependencies** — fully self-hosted

**Two automated pipelines**:

1. **Daily extraction** (~15-30s): scan session JSONL → embed chunks (Qwen3) → cosine sim < 0.60 = novel → send to Opus for fact extraction → write to `memory/YYYY-MM-DD.md`
2. **Weekly consolidation**: load all embeddings → pairwise similarity matrix → cluster near-duplicates (cos > 0.85) → LLM merge + contradiction resolution → promote to MEMORY.md

**Key insight — hybrid (embeddings + LLM)**:
- Pure embeddings can't distinguish "loves React" from "hates React"
- Pure LLM is too expensive for large corpus scanning
- Hybrid: embeddings do SELECTION (fast, free, deterministic), LLM does UNDERSTANDING (smart, accurate)

**Temporal decay: disable on small corpora** — negligible improvement under ~500 files. This directly contradicts the time-based decay approach currently in heartbeat_learning.py.

**Claude Memory Tool**: CRUD calls against storage backend (files/DB/S3). Agent owns the storage. Context Editing + Memory Tool together: +39% performance improvement in complex multi-turn sessions.

**Anti-patterns confirmed**:
- Don't add graph DB for single-user systems — flat files + hybrid search cover the same ground
- Don't enable temporal decay early — only helps at ~500+ files
- Don't load entire memory files — search first, read targeted snippets

**Infrastructure comparison**: This architecture (flat files + sqlite-vec) has ZERO external API dependencies vs Mem0 (vector DB + graph + API), Letta (server + API), ChatGPT (cloud-only). The 74% LoCoMo result validates the "structure > pure embedding" thesis from the Mem0 survey.

## Hermes 啟發

- `heartbeat_learning.py` currently implements **time-based decay** — agent-memory.bruegs.com confirms this is counterproductive on small corpora. Should switch to cosine-similarity-based novelty detection instead.
- The hybrid pipeline (embeddings SELECT, LLM UNDERSTAND) directly maps to what heartbeat_learning.py distillate + consolidate cycle is trying to do — but with wrong mechanism (time decay vs similarity threshold)
- **Pre-compaction flush** pattern: reminds agent to save durable memories before context compaction. Relevant to WS-035 structured memory lifecycle management.
- **Session transcript indexing** for cross-session recall — Hermes has `sessions/archive/` which could serve this purpose with the right indexing layer.

## 未追蹤 leads

- https://github.com/.../simplemem — SimpleMem paper: +64% vs Claude-Mem on LoCoMo (mentioned in source, no direct link found)
- sqlite-vec GitHub repo — for local vector acceleration without API dependency
- Qwen3 Embedding 0.6B via LM Studio — for zero-cost local embeddings

## ✅ 本次探索完成
