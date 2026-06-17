---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-Voice-Agent-自動化測試---Hamming--YC-S24
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-Voice-Agent-自動化測試---Hamming--YC-S24.md
title: 探索：Voice Agent 自動化測試 — Hamming (YC S24)
date: 2026-05-25
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agents
- hamming
- heartbeat
- judges
- llm
- rubric
- scoring
- testing
- voice
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：Voice Agent 自動化測試 — Hamming (YC S24)

**延續自**: (standalone exploration, no prior notes)

**日期**: 2026-05-25
**来源**: Hacker News — Launch HN #41257369, 129 pts

---

## Per-Source Insights

### Hamming — Automated Testing for Voice Agents (129 pts)

**What it is**: Hamming (YC S24) is a platform for automated voice agent testing. Their core insight: "It's a catch-22 — making current voice agents reliable is incredibly time-consuming, which keeps teams from pushing them into production."

**Architecture (4-step pipeline)**:
1. **Persona + scenario generation** — diverse but realistic user personas; "Getting LLMs to create diverse scenarios even with high temperatures is surprisingly tricky"
2. **Agent-to-agent calls** — their agents call your agent, playing difficult users; or test just the LLM/logic layer via API hook
3. **LLM judging** — deterministic checks (fallback) + LLM judges tailored to the domain (e.g., order accuracy). LLM judge reviews full transcript + function calls + traces against success criteria. "Building LLM judges that consistently align with human preferences is challenging"
4. **Production scoring** — reuse the same checks/judges on live traffic → track quality metrics over time

**What surprised me**: The eval loop for voice agents is structurally identical to what heartbeat_learning.py tries to do for agent actions — but Hamming's version has:
- Explicit persona simulation (the "difficult end user")
- Multi-turn adversarial coverage
- LLM judges that explain their scoring reasoning
- Production traffic integration for online evals

**Their inspiration**: "Simulations were key to testing autonomous systems before deployment" — Tesla (autonomous vehicles) + Anduril. This is exactly the mental model heartbeat_learning.py is trying to build.

**Future direction (resembles DSPy)**: "We're considering building a voice agent optimizer (like DSPy) that uses scenarios from testing that failed to generate a new set of prompts or function call definitions to make the scenario pass. We find the potential of self-play and self-improvement here super exciting."

---

## Hermes 啟發

### 1. Evals > Systems (the hard truth)
> "It seems just as challenging to figure out all the ways your system can go wrong, as it is to build the system in the first place." — HN commenter

This maps directly to heartbeat_learning.py's rubric scoring (WS-024). The rubric is the eval. Getting good evals IS the work.

### 2. LLM judge with deterministic fallback
Hamming uses dual-mode scoring: deterministic checks (fast, certain) + LLM judge (nuanced, expensive). heartbeat_learning.py's rubric.py could adopt this pattern — deterministic rules for obvious failures (syntax error, wrong tool, timeout), rubric score for nuanced quality assessment.

### 3. Production traffic for online evals
Hamming's step 4 — scoring live traffic with the same judges used in testing. heartbeat's action log IS production traffic. The existing `heartbeat_action_log.jsonl` could be fed through rubric scoring as a continuous online eval, not just manual review.

### 4. Failed evals → self-improvement (DSPy-style)
Hamming's aspirational direction: use failing scenarios to auto-generate better prompts. For heartbeat, this would be: rubric scores that fail → adjust `heartbeat/scoring.py` weights or action selection thresholds. The gap is clear: heartbeat has scoring but no feedback loop back to the scoring weights.

### 5. Hamming distance naming
Named after Richard Hamming ("You and Your Research"). Their product measures "distance between current LLM output vs. desired LLM output." This is structurally similar to heartbeat's severity scoring — distance from expected state.

---

## 未追蹤 Leads

- https://github.com/pipecat-ai/pipecat — open source voice orchestration (mentioned in comments, integration opportunity?)
- https://github.com/bolna-ai/bolna — open source voice agent (mentioned in comments, mentioned by Sumanyu they were reaching out to integrate)
- https://www.hamming.ai/voice-demo — interactive demo (requires web access, couldn't fetch through terminal)
- Hamming's GitHub presence? — no direct mention in HN thread, their product is proprietary SaaS

---

## Cross-Article Synthesis

Hamming's eval framework and MemR³'s evidence-gap tracking (from prior notes) share a structural pattern: both define a target state (desired outcome / evidence gap), measure distance from target, and iterate. Hamming does it with voice agents + LLM judges; MemR³ does it with memory retrieval + cosine similarity. The generic form: **Define target → Generate candidates → Score gap → Update → Repeat**.

heartbeat_learning.py has the target (rubric thresholds) and generation (action log ingestion) but lacks the closed loop back to weight adjustment. This is the "upgrade path" for WS-024.

---

## ✅ 本次探索完成
