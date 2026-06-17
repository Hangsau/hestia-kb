---
_slug: 40-Resources-_mixed-explorations-2026-06-06-Cq---Stack-Overflow-for-AI-Agents
_vault_path: 40-Resources/_mixed/explorations/2026-06-06-Cq---Stack-Overflow-for-AI-Agents.md
title: Cq — Stack Overflow for AI Agents
date: 2026-06-06
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agents
- hermes
- knowledge
- mcp
- mozilla
- overflow
- server
- stack
- trust
created: '2026-06-06'
updated: '2026-06-15'
status: budding
---

# Cq — Stack Overflow for AI Agents

**Source**: Mozilla AI (225 pts, Show HN) — https://blog.mozilla.ai/cq-stack-overflow-for-agents/

## Per-Source Insight

**What it is**: A shared knowledge commons where AI coding agents query past learnings before tackling unfamiliar tasks, contribute discoveries back, and build collective knowledge that earns trust through use rather than authority.

**Core mechanic**:
- Agent queries cq commons before unfamiliar work (API integration, CI/CD config, framework)
- If another agent already learned "Stripe returns 200 with error body for rate-limited requests" → your agent knows it upfront
- Agent discovers something novel → proposes knowledge back → other agents confirm or flag stale
- Knowledge trust = function of use + cross-agent confirmation, not static documentation

**Architecture (PoC)**:
- Plugin for Claude Code + OpenCode
- MCP server managing local knowledge store
- Team API for org-wide sharing
- UI for human-in-the-loop review
- Containers to spin up whole system

**Key insight — "knowledge earns trust through use"**:
- 84% of developers use AI tools, but 46% don't trust accuracy (up from 31% year prior)
- Single model best-guess vs multi-agent confirmed knowledge: the latter carries more weight
- Mozilla's framing: "The more agents share the knowledge they gain, the better all our agents get"

**Comparison to existing approaches**:
- Current (rejected by Mozilla): `.md` files in repos, hoping for adherence — static, no trust signal
- Cq: dynamic, earns trust over time through use + confirmation

## Hermes Relevance

**Directly relevant to WS-035 (heartbeat_learning.py drift + memory)**:
- Cq's "knowledge trust through use" = same direction as heartbeat_learning.py's distillate confidence
- Both solve: single agent learns something, other agents can't benefit from it
- Cq's MCP server for local knowledge store → analogous to Hermes's vault/notes ingestion pipeline
- Human-in-the-loop review in Cq = Hermes's own review workflow

**Complements existing work**:
- Mem0/Letta/Cogene/Graphiti/Hindsight — all solve single-agent memory, not cross-agent knowledge sharing
- Cq addresses the *collective* dimension: how do agents share learnings without central authority?
- For Hermes: could be the "Talos → Hestia knowledge transfer" pattern formalised as a cq-like exchange

**Architecture note**: Cq's MCP server is a local knowledge store (no cloud dependency). Hermes could run a similar MCP server for vault query + write.

## Untracked Leads
- https://github.com/mozilla/cq — the actual repo (not explicitly linked in blog post, repo name inferred from "open source and building in the open")
- "cq exchange: Agents without Borders" (May 21 post) — https://blog.mozilla.ai/cq-exchange-agents-without-borders/
- Andrew Ng's "Stack Overflow for AI coding agents" post that inspired this (referenced but not linked)

## ✅ 本次探索完成
