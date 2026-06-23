---
_slug: 40-Resources-_mixed-explorations-2026-05-31---GITM--Text-Based-Memory-for-LLM-Agents
_vault_path: 40-Resources/_mixed/explorations/2026-05-31---GITM--Text-Based-Memory-for-LLM-Agents.md
title: '2026-05-31 — GITM: Text-Based Memory for LLM Agents'
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- action
- based
- behavioral
- exact
- gitm
- llm
- mem
- memory
- successful
- text
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# 2026-05-31 — GITM: Text-Based Memory for LLM Agents

## Source
- https://github.com/OpenGVLab/GITM (640 ⭐)
- arxiv: https://arxiv.org/abs/2305.17144

## Per-Source Insight

**GITM Architecture (Ghost in the Minecraft)**

GITM solves the long-horizon task decomposition problem in Minecraft using three LLM-based modules:
1. **LLM Decomposer** — decomposes goal into sub-goals using Internet text knowledge
2. **LLM Planner** — plans structured actions per sub-goal; **records and summarizes successful action lists into text-based memory** to enhance future planning
3. **LLM Interface** — executes structured actions, processes keyboard/mouse I/O

Key memory insight: "LLM Planner also records and summarizes successful action lists into a text-based memory to enhance future planning."

**This is a pure text summarization approach — no embeddings, no vector search.** The agent learns successful action sequences and summarizes them as text for future reuse. This is architecturally similar to the "procedural memory" layer in YantrikDB/Mem0 frameworks — learning successful behavioral patterns as structured text rather than storing raw episodes.

**Quantitative results:**
- 100% of Minecraft Overworld technology tree items achievable (vs 30% combined for all prior agents)
- 67.5% success rate on "Obtain Diamond" (+47.5% over OpenAI VPT)
- Zero GPU required — runs on 32-core CPU node in 2 days

## Hermes 啟發

**WS-035 直接迴響**：GITM's text-based summarization memory for action sequences is exactly the pattern that `muscle-mem` (764⭐) also implements — storing successful tool-call trajectories as reusable behavioral templates. The distinction from vector-based memory: GITM doesn't retrieve by semantic similarity; it retrieves by action-list match (exact or near-exact). This is the "procedure memory" layer — what you do, not what you know.

**架構收斂**：mem0 (semantic layer) + muscle-mem (behavioral cache) + GITM (action summarization) all point to the same conclusion: **multi-tier memory where different tiers use different retrieval mechanisms.** Vector similarity for knowledge recall, exact-match for behavioral patterns, temporal decay for both.

## 跨文章 Synthesis

Three independent systems (mem0, muscle-mem, GITM) all converge on the same principle: **behavioral/action-pattern memory should be stored as structured text or action sequences, not raw embeddings.** The retrieval mechanism for behavioral patterns is exact/near-exact match (GITM's action lists, muscle-mem's tool-call trajectories), not semantic similarity.

This is the "procedural memory" tier — distinct from episodic (what happened) and semantic (what I know) memory in Tulving's classification. The retrieval is by **pattern match**, not by similarity search.

## 未追蹤 Leads
- https://github.com/chisasaw/redcache-ai (182⭐) — "A memory framework for LLMs and Agents" — vault 已有 dead-link note，但 GitHub 本身有內容可 fetch
- https://arxiv.org/abs/2305.17144 (GITM paper) — 三層架構的詳細實驗數據
- JARVIS-1 paper — vault 已有 note 但無 details

## ✅ 本次探索完成
