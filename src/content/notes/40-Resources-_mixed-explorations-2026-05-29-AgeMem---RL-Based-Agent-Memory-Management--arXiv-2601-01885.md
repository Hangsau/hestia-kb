---
_slug: 40-Resources-_mixed-explorations-2026-05-29-AgeMem---RL-Based-Agent-Memory-Management--arXiv-2601-01885
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-AgeMem---RL-Based-Agent-Memory-Management--arXiv-2601-01885.md
title: AgeMem — RL-Based Agent Memory Management (arXiv 2601.01885)
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- agent
- context
- delete
- facts
- ltm
- memory
- stm
- task
- training
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

# AgeMem — RL-Based Agent Memory Management (arXiv 2601.01885)

**日期**: 2026-05-29 | **來源**: arXiv 2601.01885 (Yu et al. 2026) | **類型**: Exploration

**延續自**: [[2026-05-29-llm-agent-memory-architecture]]

---

## Core Architecture — Three-Stage RL Training

AgeMem trains memory management as an RL problem, not a retrieval problem. Three progressive stages:

### Stage 1: LTM Supervision
- Train on HotpotQA QA pairs — structured contextual information naturally provides ground-truth "supporting facts" for memory consolidation
- Supervised learning: agent learns which facts are worth storing in long-term memory
- Result: a strong LTM consolidation policy before any RL

### Stage 2: DistractorGen-Based STM Management
- **DistractorGen**: dedicated module prompts an external LLM to generate short, user-style utterances conditioned on the target query while remaining semantically unrelated
- Distractors have three enforced properties:
  1. No shared entities or key concepts with target question
  2. Conversential plausibility (resemble natural dialogue turns)
  3. Topical diversity
- N=3–5 distractors are optimal; N=7 shows mild decline (Table 8)
- STM tools: `Filter_context` (remove distractors), `Summary_context` (compress), `Retrieve_memory` (pull from LTM)
- Key insight: **distractor-based training is essential** — without it, the agent cannot learn when to filter vs. absorb

### Stage 3: Full Pipeline + GRPO
- Joint training with all three components:
  - `Add_memory`, `Update_memory`, `Delete_memory` (LTM)
  - `Filter_context`, `Summary_context`, `Retrieve_memory` (STM)
- Step-wise GRPO: K=8 independent rollouts per task for group normalization
- KL divergence coefficient β = 0.1
- Convergence: 50-70 steps

---

## Key Results

**Overall performance (Qwen2.5-7B-Instruct)**:
| Method | ALFWorld | SciWorld | HotpotQA | Average |
|--------|----------|----------|----------|---------|
| No-Memory | 27.16 | 13.80 | 38.36 | 26.44 |
| LangMem | 38.27 | 28.29 | 37.43 | 34.66 |
| A-Mem | 34.68 | 28.06 | 43.95 | 35.56 |
| Mem0 | 37.49 | 26.99 | 46.66 | 37.05 |
| AgeMem | **41.07** | **35.55** | **54.44** | **43.69** |

**Token efficiency (HotpotQA)**:
- No-Memory: 3076 tokens/context
- AgeMem: 2105 tokens/context (31% reduction)
- Key: selective memory management prevents context bloat

**Memory Quality (MQ) — LLM judge evaluation**:
- MQ = LLM judge comparing stored memories vs ground-truth supporting facts
- Prompt template in Appendix C.2
- AgeMem MQ: 0.621 (vs A-Mem 0.541, Mem0 0.498)

**STM contribution (ablation)**:
- Adding STM management to LangMem: +41.56 avg (+6.9 over LangMem alone)
- STM alone provides 20-30% relative improvement on memory quality
- **Joint LTM+STM training is crucial** — they reinforce each other

---

## Three-Layer Memory Architecture

1. **LTM** (Long-Term Memory): `Add_memory`, `Update_memory`, `Delete_memory` — stores core facts with validity windows
2. **STM** (Short-Term Memory): `Filter_context`, `Summary_context` — manages current context under distraction
3. **WM** (Working Memory): active reasoning state

Plus: `Retrieve_memory` bridges LTM → WM when relevant facts are needed.

---

## Reward Design

Three-component reward (equal weight 1/3 each):

```
J = (1/3) × J_task + (1/3) × J_context + (1/3) × J_memory
```

- **J_task**: task completion (LLM judge on HotpotQA answer quality)
- **J_context**: context efficiency (penalize token overflow)
- **J_memory**: memory quality (MQ metric from LLM judge)

**All-Returns > Answer-Only**: Using all intermediate step returns in GRPO significantly outperforms only rewarding the final answer. Every memory operation has an immediate reward signal, not just the terminal task outcome.

---

## Critical Design Patterns for Hermes

### 1. DistractorGen as STM training signal
The DistractorGen approach is the key innovation. Without it, the agent cannot learn when to filter vs. absorb. For Hermes:
- The DistractorGen concept maps to the "noisy inbox" problem — hearth inbox messages, Telegram pings, background research are all distractors
- Training the agent to selectively filter hearth tasks (low priority, stale) vs. absorb (high priority, new) is analogous to AgeMem's STM training
- **Pattern to steal**: generate synthetic distraction scenarios for Hermes's STM training

### 2. Delete_memory as first-class operation
AgeMem has explicit `Delete_memory`. The paper shows this is crucial — agents must unlearn stale facts, not just add new ones. Hermes skills have `deprecated` frontmatter, but there's no active deletion/archival mechanism.
- **WS-037** already addresses staleness via `_compute_staleness()` + `check_distillation_freshness()` — but explicit `Delete_memory` (archive to cold storage) is the complement

### 3. LTM stability + STM flexibility
LTM (vault, autonomous_notes) is stable — writes are deliberate. STM (current session context) is flexible — agent can filter/summarize freely. This is the Pattern B vs Pattern C from the MLMF survey — AgeMem confirms Pattern B is the right starting point.

### 4. Memory quality as explicit metric
The MQ metric (LLM judge comparing stored memories against ground truth) gives AgeMem a trainable signal for memory quality, not just task performance. For Hermes:
- Could we define a similar MQ for heartbeat learnings?
- Ground truth = the actual errors/fixes that occurred in subsequent cycles
- This would close the loop on "did the agent correctly identify what was worth remembering?"

### 5. Token efficiency as a first-class signal
31% token reduction through selective memory management. Hermes has no such metric currently. `avg_tokens_per_session_start` was identified in the prior exploration note as a key metric — AgeMem validates this direction.

---

## Connection to WS-037 (Heartbeat Bounded Dereferencing)

WS-037 implemented `_compute_staleness()` in heartbeat_learning.py:
- **technical facts**: 99% → staleness triggered
- **domain knowledge**: 98% → staleness triggered
- Signal is correct per implementation

AgeMem adds the missing piece: **RL-based policy for when to delete vs. keep**. WS-037's staleness detection fires correctly, but the decision of *what to do with stale facts* (delete? downgrade? leave?) is still heuristic. AgeMem's framework suggests:
- If memory is stale AND task performance degrades → Delete
- If memory is stale but task still correct → Keep with lower retrieval priority
- The RL policy learns this distinction from environment feedback

**Next step**: Integrate AgeMem's reward structure into heartbeat_learning.py decision loop — not just detection, but action selection trained on downstream task performance.

---

## ✅ Exploration Complete

