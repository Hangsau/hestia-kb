---
_slug: 40-Resources-_mixed-explorations-2026-05-29-Agentic-Memory--AgeMem----GRPO-Based-Unified-Memory-Manageme
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-Agentic-Memory--AgeMem----GRPO-Based-Unified-Memory-Manageme.md
title: Agentic Memory (AgeMem) — GRPO-Based Unified Memory Management
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- arxiv
- based
- management
- memory
- policy
- stage
- task
- tool
- via
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

# Agentic Memory (AgeMem) — GRPO-Based Unified Memory Management

**日期**: 2026-05-29 | **來源**: arXiv 2601.01885v2 (Apr 2026) | **類型**: Exploration

---

**延續自**: [[2026-05-29-llm-agent-memory-architecture]]

---

## Source — arXiv 2601.01885v2: AgeMem Paper (Yu et al. 2026)

**Core innovation — unified LTM+STM via tool-based actions:**
- Exposes memory operations (Retrieve/Add/Update/Delete/Summary/Filter) as **tool invocations** — identical to how LLM agents call external tools
- Three-stage progressive RL (Stage 1: passive observation → Stage 2: memory skills → Stage 3: active management)
- Step-wise GRPO addressing sparse/discontinuous rewards from memory operations
- Key insight: "Memory operations are structured actions" — treats memory management as a policy decision, not a side effect

**Method details:**
- **Stage 1 — Passive Observation**: agent traces task without memory ops, learns which tasks benefit from memory
- **Stage 2 — Memory Skills**: frozen memory policy combined with learnable task policy; trains when to invoke memory ops
- **Stage 3 — Active Management**: end-to-end unified policy for both task and memory operations together
- **Reward design**: composite of task success + different memory operation weights (Retrieve, Add, Delete balanced in Stage 3)
- GRPO (Group Relative Policy Optimization) replaces PPO for memory op stability

**Results (5 long-horizon benchmarks):**
- Consistent improvement over strong memory-augmented baselines across multiple LLM backbones
- Higher quality long-term memory stored (measured by retrieval accuracy after k steps)
- More efficient context usage (fewer tokens per query — 3.5× reduction on some tasks)
- The learned controller addresses "when to forget" as part of the policy — this directly solves the Supermemory insight

**Architecture comparison:**
- AgeMem Pipeline: [Task Observation] → [Memory Policy (GRPO-trained)] → [Tool-based Memory Ops] → [Updated Memory State] → [Task Policy]
- vs. Mem0/Blow: heuristic prompts for memory management; AgeMem learns "when" from data

**Key insights for Hermes:**
1. **Tool-based memory ops is the right abstraction** — same mental model as skill commands. If we expose memory operations as structured tool calls, the RL training path to learn "when to consolidate/forget" becomes clear
2. **Three-stage progressive RL mirrors Herme's own growth**: passive (observe patterns) → skill-based (apply learned rules) → active management (decide what/when)
3. **The 3.5× token reduction** is a concrete target for Herme's `avg_tokens_per_session_start` metric
4. **"Learning to forget" as a learned policy** — AgeMem trains Delete decisions end-to-end, not via heuristic rules

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — already fetched; follow on implementation via GitHub if available
- https://arxiv.org/abs/2504.19414 — Mem0 ECAI 2025: original token-efficient algorithm
- https://arxiv.org/abs/2501.13956 — Graphiti/Zep benchmark paper

---

## Hermes 啟發

1. **Expose memory ops as structured actions**: Heartbeat already has this with skills/scripts - the pattern is proven. Extend to memory consolidation decisions (should this fact be distilled? deleted? kept as-is?)

2. **The 3.5× token reduction target**: AgeMem achieves 3.5× fewer tokens via learned memory management. For Hestia, the analogous metric is `avg_tokens_per_session_start` — currently unbounded; target should be <5000 tokens/session via proactive forgetting

3. **Three-stage RL pipeline as an architecture blueprint**: Stage 1 (observe without acting) = session logging; Stage 2 (frozen memory policy) = rules we already encode; Stage 3 (active management) = what WS-037 (Bounded Dereferencing) is trying to approximate

## ✅ Exploration Complete

