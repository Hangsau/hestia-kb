---
_slug: 40-Resources-_mixed-explorations-2026-05-29-AgeMem--Agentic-Memory-via-GRPO---arXiv-2601-01885
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-AgeMem--Agentic-Memory-via-GRPO---arXiv-2601-01885.md
title: 'AgeMem: Agentic Memory via GRPO — arXiv 2601.01885'
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- baseline
- context
- ltm
- memory
- reward
- skill
- stage
- tool
- update
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

# AgeMem: Agentic Memory via GRPO — arXiv 2601.01885

**日期**: 2026-05-29 | **來源**: arXiv 2601.01885 | **類型**: Exploration

**延續自**: [[2026-05-29-llm-agent-memory-architecture]]

---

## Core Contribution

AgeMem = **Three-stage RL training** (GRPO) to teach an LLM agent to manage its own memory — both long-term (LTM) and short-term (STM) — as first-class learnable skills.

### Three Memory Tool Types

| Tool | What it does | When used |
|------|-------------|-----------|
| `Add_memory` | Store fact to LTM with metadata | New important information discovered |
| `Update_memory` | Modify existing LTM entry | Information becomes outdated/incorrect |
| `Delete_memory` | Remove LTM entry | Fact no longer relevant or historical |
| `Retrieve_memory` | Query LTM by semantic similarity | Need past information to inform current task |
| `Filter_context` | Remove distracting content from short-term context | Irrelevant info diluting focus |
| `Summary_context` | Summarize accumulated context | Context growing too large |

### Three-Stage Training

**Stage 1 (LTM Foundation)**: Supervised fine-tuning on HotpotQA with annotated supporting facts. Teaches `Add_memory` — what facts to store and with what metadata.

**Stage 2 (STM Control under Distraction)**: RL fine-tuning with `DistractorGen` — generates fake user utterances on unrelated topics mixed into context. Teaches `Filter_context` and `Summary_context` — how to recognize and remove distractors.

**Stage 3 (Integrated Memory Coordination)**: Combined LTM + STM RL training. Teaches coordinated use: retrieve → add → update → delete based on task phase.

### Key Quantitative Results

- HotpotQA: 54.44 vs baseline 38.36 (+16 pts) with full AgeMem
- ALFWorld: 41.07 vs baseline 27.16 (+14 pts)
- SciWorld: 35.55 vs baseline 13.80 (+22 pts)
- Memory Quality (MQ) on HotpotQA: 0.657 with All-Returns reward vs 0.415 with Answer-Only reward
- **All-Returns reward** (reward every tool call) >> Answer-Only reward (only reward final answer) — because intermediate memory actions have delayed downstream effects

---

## Why This Matters for Hermes

**1. The "memory as learnable skill" insight**

Mem0 / Zep / Letta all treat memory management as **engineered infrastructure** — hand-coded rules for when to store, when to evict. AgeMem shows memory management is actually a **learnable policy**. This aligns with the MLMF survey's Pattern C (tiered memory + learned controller).

For Hermes: the `heartbeat_learning.py` staleness mechanism (WS-037) could benefit from RL-based eviction policy rather than fixed Ebbinghaus curves.

**2. All-Returns reward = correct**

The paper shows that rewarding only the final answer is insufficient — memory tool calls have delayed downstream effects that only pay off after many steps. This validates the heartbeat rubric's `followup_quality` dimension: measuring whether subsequent sessions show evidence of prior learning.

**3. `Filter_context` as a concrete primitive**

The distractor examples (quantum computing, blockchain, robotics mixed into ML course request) are directly relevant to Hearth's inbox filtering problem. The agent learns to recognize topical mismatch and filter — this is structurally similar to inbox message routing.

**4. Three-tool coordination cycle**

```
Retrieve_memory → Add_memory → Update_memory → Delete_memory
```

This is a memory lifecycle. Hermes skills have a parallel: `skill_create` → `skill_update` → `skill_deprecate`. The AgeMem pattern could inform a more principled skill lifecycle management.

---

## Contrast with WS-037 Bounded Dereferencing

WS-037 (heartbeat_learning.py staleness) implements **passive staleness detection** — decay based on time windows.

AgeMem's RL approach is **active policy learning** — the agent decides when to store/update/delete based on downstream utility.

The gap: WS-037's staleness mechanism could be enhanced with a lightweight policy that decides "is this fact still useful right now?" rather than just "has enough time passed?" — essentially bounded dereferencing as a learned retrieval decision.

---

## 未追蹤 Leads

- https://arxiv.org/abs/2601.01885 — (this paper, primary source)
- Trinity RL framework (Pan et al., 2025a) — the underlying GRPO optimizer used for AgeMem training
- https://github.com/WujiangXu/A-mem-sys/ — A-Mem baseline implementation
- https://langchain-ai.github.io/langmem/ — LangMem baseline

---

## ✅ Exploration Complete

