---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Agent-Memory---Grep-vs-RAG--2026-05-22
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Agent-Memory---Grep-vs-RAG--2026-05-22.md
title: Agent Memory — Grep vs RAG (2026-05-22)
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- context
- grep
- https
- memory
- rag
- results
- retrieval
- summaries
- tool
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# Agent Memory — Grep vs RAG (2026-05-22)

**延續自**: 無（第一篇探索）

---

## Ask HN — Are we close to figuring out LLM/Agent Memory?
- **URL**: https://news.ycombinator.com/item?id=47449389
- **Date**: March 26, 2026
- **Points**: 4 (low engagement Ask HN)

### Key Insights

**Community shift: RAG → grep/markdown**
- A few years ago everyone used RAG + embeddings + vector DBs
- Now models with local markdown + memory files (OpenClaw pattern) outperform those DBs with grep + UNIX tools
- Main bottleneck for adoption = memory/persistent long-term context, not model quality

**kageroumado's "lossless context management" (LCM)**
- DB stores every message; model accesses via simple search
- Tiered summarization: raw messages → level-0 summaries → level-1 summaries
- Full context stack: `[intro] + [lvl1 summaries] + [system prompt] + [recent lvl0 summaries] + [temporal context] + [recent msgs w/ tool results] + [recent msgs]`
- Tool results progressively stripped (useful only a few turns)
- Never compacts during active work; expandable on demand
- Reports outperforming all other solutions for personal assistant use case

**ramblurr's problem with LCM**: agent doesn't use retrieval tools enough → pattern exists but not triggered
- This is the "tool use gap" — even with good memory infra, agent needs explicit prompting/incentive to retrieve

**AndyNemmity**: no good metrics for this; everyone exploring different paths; full custom Claude Code setup solved it for their use case

### Hermes 啟發

1. **Memori should support expandable retrieval**: LCM's "expand each node" approach — agent retrieves on demand, not forced. Hermes could add a `memory_expand()` action that pulls more context for a given topic rather than always feeding everything.

2. **Tool results are ephemeral — strip aggressively**: kageroumado strips tool results after a few turns. Memori's compaction should aggressively compress tool call outputs (which is already happening via compaction, but maybe too slowly?).

3. **The retrieval incentive problem**: Even with good memory infra, agent won't use it without prompting. This maps to WS-008 "memory continuity" — the skill needs to include explicit retrieval cues, not just storage.

---

## Leads Not Retrieved
- **Expensively Quadratic** (`47000034`) — returned "Sorry."
- **Local memory for any LLM agent** (`47054436`) — returned "Sorry."

## 未追蹤
- https://news.ycombinator.com/item?id=47000034
- https://news.ycombinator.com/item?id=47054436

## ✅ 本次探索完成
