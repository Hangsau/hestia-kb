---
_slug: 40-Resources-_mixed-explorations-2026-05-22-2026-05-22---MemoryArena--Agent-Memory-Benchmark-Deep-Dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-2026-05-22---MemoryArena--Agent-Memory-Benchmark-Deep-Dive.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 32:\n    title: 2026-05-22 — MemoryArena: Agent Memory Benchmark Deep\
  \ Dive\n                                   ^"
_raw_fm: '

  title: 2026-05-22 — MemoryArena: Agent Memory Benchmark Deep Dive

  date: 2026-05-22

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, context, long, memgpt, memory, memoryarena, multi, session,
  sessions, tasks]

  created: 2026-05-22

  updated: 2026-06-15

  status: active

  '
title: '2026-05-22 — MemoryArena: Agent Memory Benchmark Deep Dive'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# 2026-05-22 — MemoryArena: Agent Memory Benchmark Deep Dive

**延續自**: [[2026-05-22-agent-memory-architecture-survey]]

## Source
- "Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks"
- arXiv:2602.16313, ICML 2026
- URL: https://arxiv.org/html/2602.16313

## Per-Source Insights

### The Core Problem: Existing Benchmarks Are QA Tests, Not Memory Tests

All prior benchmarks (LoCoMo, LongMemEval, MemoryBench, MemBench) test **post-hoc recall** — agent sees a long context, then answers a question. This doesn't measure whether memory guides **future actions**.

MemoryArena introduces **Memory-Agent-Environment Loop**: actions → feedback → memory update → future actions. Task success requires correctly using information from earlier sessions to constrain later ones.

### Key Taxonomy: What Makes a Memory Benchmark Hard

Table 1 comparison across 8 benchmarks:

| Benchmark | Memory | Actions | Env Feedback | Multi-Sess | Interdep |
|-----------|--------|---------|-------------|------------|----------|
| LoCoMo | ✓ | ✗ | ✗ | ✗ | N/A |
| LongMemEval | ✓ | ✗ | ✗ | ✗ | N/A |
| MemoryBench | ✓ | ✗ | ✗ | ✗ | N/A |
| WebArena | ✗ | ✓ | ✓ | ✗ | 13.3 |
| WebShop | ✗ | ✓ | ✓ | ✗ | 7.3 |
| MemoryArena | ✓ | ✓ | ✓ | ✓ | **57** |

57 avg action steps, 6.9 avg subtasks per task. No other benchmark combines all five.

### Four Evaluation Environments

**1. Bundled Web Shopping** — later purchases depend on recalling compatibility constraints from earlier sessions (e.g., TV size determines which stand fits). 150 tasks.

**2. Progressive Web Search** — each subquery introduces a new constraint; answer must satisfy ALL prior constraints. Causal ordering enforced by human annotation. 256 tasks.

**3. Group Travel Planning** — new travelers join an existing itinerary; their choices must respect prior travelers' selections (price relative to X, cuisine shared with Y). Multi-agent memory scenario.

**4. Sequential Formal Reasoning** — math/physics problems require building on previously proven lemmas. Average trace: 40k tokens.

### When External Memory Helps vs Hurts

Critical finding:
- **Long-context-only agents**: 80%→45% drop on interdependent multi-session tasks vs single-session
- **RAG systems**: can help but latency cost is significant (async writes critical)
- **Memory systems with learned retrieval** (ReasoningBank, Letta) outperform both long-context and basic RAG on multi-session tasks

### Memory System Comparison Results

Key results (GPT-5-mini across four environments):

**Web Shopping:**
- MemGPT (Letta): Best overall — precision in cross-session constraint recall
- Long Context: "Lost in the middle" — 20k+ context causes instruction drift
- Text Embedding RAG: Moderate, consistent

**Group Travel:**
- MemGPT: Best precision but can fail on base traveler (seed) info retrieval
- Long Context: bloated context (20k+ chars) loses the reference value within the noise
- Case study shows MemGPT correctly retrieves `Rebecca's lunch: $48, rating 2.9` → calculates `10% margin → $43.2-$52.8` → picks `The Krib: $45`. Long context picks Daawat-e-Kashmir at $19 (violates constraint).

**Progressive Web Search:**
- All systems struggle with subquery 2+ when it requires reasoning over info from subquery 1
- Mem0: semantic drift — memory context includes noise from unrelated searches (snooker player, dissertation, etc.)
- Long Context: XML-wrapped history has cross-document noise (Edmund Fitzgerald for Ghana doctor query)

**Formal Math Reasoning:**
- MemGPT: best at retrieving procedural memory (lemmas from prior sessions)
- Mirix (ReasoningBank): abstracts into `# Memory Item` with title + description, enabling flexible recombination
- Long Context: fails when 40k token trace has relevant lemma at token 20k-30k

### The "Lost in the Middle" Problem Quantified

Long context (20k+ chars) consistently fails when:
1. Reference value is buried in middle (no salience signal)
2. Constraints are relative (10% of X, higher than Y) not absolute
3. Cross-session dependencies require tracking relationships, not just facts

**Key insight**: Compression + selective retrieval > raw context length. MemGPT's approach of storing only high-density summaries (2,979 chars) vs Long Context's 20,042 chars — the former is actually more effective.

### Interdependent Subtask Difficulty

Table 2: avg trace length and complexity:
- Bundled Web Shopping: 6 subtasks, 41.5k tokens avg
- Group Travel: 5-9 subtasks, 40.6k tokens, 270 avg queries
- Progressive Web Search: 2-16 subtasks, 122.4k tokens, 256 tasks
- Math Reasoning: 2-16 subtasks, 18.1k tokens

## Hermes 啟發

### Gap Analysis: MemoryArena Findings vs Hermes System

| MemoryArena Finding | Hermes Equivalent | Gap |
|---------------------|-----------------|-----|
| Memory-Agent-Environment loop | heartbeat action → state change → snapshot | **Partial**: snapshot captures state but no feedback loop |
| Interdependent subtask constraint tracking | session tree phase navigation (WS-025) | **Addressed** by WS-025 proposal |
| Long-context "lost in the middle" | session_search on 40k+ token sessions | **Real risk**: flat JSONL forces full scan |
| Learned memory control vs heuristic | heartbeat scoring is heuristic | **Gap**: no RL-trained component |
| Multi-agent memory governance | DCG command-level governance | **Partial**: DCG handles writes, not cross-agent read scope |
| Memory operation observability | severity logging exists | **Gap**: no memory-diff between cycles |

### Actionable Directions

1. **WS-025 phase navigation addresses "interdependent subtask" gap** — the MemoryArena finding that constraint tracking across sessions is the hardest part validates WS-025's B+ tree approach. The key insight: we don't need to index everything, just the **decision-relevant moments** (where earlier session constraints affect later session choices).

2. **MemGPT-style high-density summarization > raw context** — `session_search` currently does full text search on raw JSONL. For long sessions, we should consider storing a summary layer alongside raw logs, similar to how MemGPT stores `EpisodicMemory` vs `ProceduralMemory`.

3. **MemoryArena observability principle** — the benchmark measures `memory diff` (what changed between sessions) as a key metric. Hermes should track: what was the most important new knowledge acquired this cycle? What's the confidence that it will be retrieved correctly next cycle?

4. **Group Travel = multi-agent memory scenario** — This is closest to the Hearth/Talos shared workspace problem. When multiple agents (Hestia, Talos) work on shared tasks, we need constraint tracking across agent boundaries, not just within a single agent's session.

### Relevant Existing Proposals

- **WS-025** (Session Tree Phase Navigation): Directly addresses "interdependent subtask" memory gap. MemoryArena provides empirical validation.
- **WS-017** (DCG Governance): Multi-agent write coordination — relevant to Group Travel multi-agent scenario.
- **heartbeat/snapshot.py**: Already captures episodic records, but lacks the Memory-Agent-Environment feedback loop.

## 未追蹤 Leads
- https://memoryarena.github.io/ — MemoryArena benchmark code + tasks
- https://arxiv.org/html/2601.01885 — Agentic Memory (RL-trained memory control, GRPO)
- https://arxiv.org/html/2506.21605 — MemBench evaluation framework

## ✅ 本次探索完成
