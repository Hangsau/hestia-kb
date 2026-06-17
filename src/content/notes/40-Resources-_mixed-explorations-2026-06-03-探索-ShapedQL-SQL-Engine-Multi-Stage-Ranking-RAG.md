---
_slug: 40-Resources-_mixed-explorations-2026-06-03-探索-ShapedQL-SQL-Engine-Multi-Stage-Ranking-RAG
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-探索-ShapedQL-SQL-Engine-Multi-Stage-Ranking-RAG.md
title: 2026-06-03 ShapedQL — SQL Engine for Multi-Stage Ranking + RAG
created: '2026-06-03'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-06-03 ShapedQL — SQL Engine for Multi-Stage Ranking + RAG

## Source
- HN: https://news.ycombinator.com/item?id=46779922 (80pts, Show HN)
- Blog: https://www.shaped.ai/blog/introducing-shapedql-the-sql-engine-for-search-feeds-and-ai-agents
- Playground: https://playground.shaped.ai (JS-rendered, unreachable via curl)

## Per-Source Insight

### ShapedQL — 4-Stage Pipeline in SQL

Core insight: **relevance (finding the best 10) is still an infrastructure nightmare**, while retrieval (finding 1,000 items) is largely solved. ShapedQL collapses the entire ranking + retrieval stack into a single declarative SQL query.

4-stage pipeline:
1. **Retrieve** — fetch candidates from hybrid search, social graphs, trending lists
2. **Filter** — hard business constraints (e.g., "in stock, under $200")
3. **Score** — real-time ML models optimized for business goals (clicks, conversions, watch time)
4. **Reorder** — list-wise diversity/exploration optimization

Example query (replaces ~2,000 lines of Elasticsearch rules):
```sql
SELECT video_id, creator_name
FROM trending_videos(), following_network("$user_id")
WHERE NOT previously_watched("$user_id")
ORDER BY p_watch_time(user, item)
REORDER BY diversity(creator_name)
```

Key architectural point: **User Context as first-class citizen** — not stateless document retrieval, but personalized decision-making per user.

## Hermes Connection

### Contrast: Current Hermes Memory vs ShapedQL Architecture

**Current Hermes** (heartbeat_learning.py):
- Distillates dumped as raw text into context — no structure, no ranking, no pipeline
- No equivalent of Filter/Score/Reorder stages
- Staleness detection absent (SSGM bounded drift not implemented)

**ShapedQL 4-stage is directly mappable to memory consolidation**:
- Retrieve → recall relevant distillates (semantic + BM25 hybrid)
- Filter → remove contradicted/outdated distillates (confidence_valid_until check)
- Score → rank by recency, contradiction count, usage frequency
- Reorder → present top-K to context, not full dump

### Agent Memory Use Case

ShapedQL blog explicitly lists "Agent Memory" as a use case under "Agent Retrieval":
> "RAG applications — personalized decisions in real-time"

This reinforces the "structured memory > pure embedding retrieval" consensus from Synix 8-systems research.

## Untracked Leads
- https://github.com/shapedai/shapedql — repo appears to not exist or is private
- https://playground.shaped.ai — JS-rendered, cannot fetch content via curl

## ✅ 本次探索完成