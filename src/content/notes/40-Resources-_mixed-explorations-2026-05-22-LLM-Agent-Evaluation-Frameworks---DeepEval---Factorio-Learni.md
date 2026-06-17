---
_slug: 40-Resources-_mixed-explorations-2026-05-22-LLM-Agent-Evaluation-Frameworks---DeepEval---Factorio-Learni
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-LLM-Agent-Evaluation-Frameworks---DeepEval---Factorio-Learni.md
title: LLM Agent Evaluation Frameworks — DeepEval + Factorio Learning Environment
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- deepeval
- environment
- eval
- evaluation
- factorio
- fle
- llm
- mcp
- rubric
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# LLM Agent Evaluation Frameworks — DeepEval + Factorio Learning Environment

**日期**: 2026-05-22
**來源**: HN Algolia (`LLM agent evaluation benchmark`)
**標籤**: #evaluation #agent-quality #rubric #deepeval #factorio

---

## Per-source Insight

### Source 1: Factorio Learning Environment (FLE)

**文章**: [Factorio Learning Environment](https://jackhopkins.github.io/factorio-learning-environment/) — 749 pts, 209 comments
**類型**: HN Show HN + GitHub open-source project

**Core argument**: An open-source evaluation environment for LLM agents using the game of Factorio as the testbed. Agents write Python code via a REPL, the environment executes it, and the agent observes output to decide next action. The game provides rich, open-ended evaluation — building a factory from scratch is a proxy for "can the agent handle long-horizon planning, tool orchestration, and error recovery."

**Key observations**:
- REPL pattern: Agent generates Python → Environment executes → Agent reads output → Repeat. This is a clean abstraction for tool-use evaluation — the "program" is the action, stdout/stderr is the feedback.
- Docker-based evaluation: `fle cluster start` + `fle eval --config configs/gym_run_config.json`. Standardized eval environment means reproducibility.
- MCP protocol support: `pip install factorio-learning-environment[mcp]` — the eval environment speaks MCP, which is relevant for Hermes MCP server work.
- Claude Opus 4.1 can play Factorio — shows frontier models can handle complex, multi-step reasoning tasks.

> 對 Hermes 的啟發：FLE's REPL pattern (program → execute → observe → repeat) maps directly to Hermes's tool-call loop. The Factorio benchmark's evaluation criteria (factory completion, resource efficiency, error recovery) could inspire a Hermes-specific benchmark: how well does the agent handle multi-session planning failures?

---

### Source 2: DeepEval (Confident AI)

**文章**: [deepeval](https://github.com/confident-ai/deepeval) — ⭐15,603, Apache 2.0
**類型**: Open-source framework / GitHub README

**Core argument**: A pytest-like evaluation framework for LLM applications. Evaluates any LLM framework (OpenAI, LangChain, LangGraph, Anthropic, CrewAI, LlamaIndex, etc.) via metrics that run locally (no cloud dependency). Key insight: LLM-as-judge evaluation (G-Eval) runs on any LLM you choose, not just OpenAI.

**Key observations**:
- **Agentic Metrics** (most relevant to Hermes heartbeat):
  - `TaskCompletionMetric` — did the agent accomplish its goal?
  - `ToolCorrectnessMetric` — right tools, right arguments?
  - `StepEfficiencyMetric` — any unnecessary steps?
  - `PlanAdherenceMetric` — did agent follow expected plan?
  - `PlanQualityMetric` — quality of the agent's plan
- **G-Eval**: Research-backed LLM-as-judge for custom criteria. `criteria` is free-form text, `evaluation_params` defines what the judge sees (actual output, expected output, context, etc.). Threshold-based pass/fail.
- **Multi-Turn Metrics**: `KnowledgeRetention`, `ConversationCompleteness`, `TurnRelevancy` — directly relevant to Hermes vault decay / memory retrieval quality.
- **MCP Metrics**: `MCP Task Completion`, `MCP Use`, `Multi-Turn MCP Use` — confirms MCP is becoming a standard eval target, not just a transport protocol.
- **MCP Server available**: Confident AI has its own MCP server — this means DeepEval evals can run from Claude Code / Cursor directly, no UI required.
- Pytest integration: `assert_test(test_case, [correctness_metric])` — familiar pattern for developers. Also works in notebooks via `evaluate()`.

> 對 Hermes 的啟發：DeepEval's agentic metrics (TaskCompletion, ToolCorrectness, StepEfficiency) directly map to what WS-024's rubric scoring system was trying to build. The G-Eval pattern (free-form criteria + LLM-as-judge) is cleaner than the fixed rubric we derived from R²-Mem. **Actionable next step**: replace WS-024's rubric with G-Eval-style scoring — define criteria as natural language, use any LLM (including DeepSeek) as the judge.

---

## Cross-Article Synthesis

Both FLE and DeepEval approach agent evaluation from different angles:
- **FLE**: Environment-based (the agent is placed in a game world, evaluated by outcome)
- **DeepEval**: Metric-based (the agent's output/behavior is scored against defined criteria)

For Hermes heartbeat, the metric-based approach is more practical:
- We don't need a full game environment — we have real production data (action logs, severity records, proposal outcomes)
- DeepEval's `TaskCompletionMetric` + `ToolCorrectnessMetric` could replace the hand-coded rubric in `heartbeat/rubric.py`
- FLE's REPL pattern suggests we could add a "replay" mode to heartbeat: replay a past heartbeat action log through a test suite and score it

**The convergence point**: DeepEval's G-Eval + FLE's MCP support both point to MCP as the standard agent interface. If Hermes exposes its tools via MCP (WS-022), then DeepEval's `MCP Use` metric could be used to evaluate how well agents use Hermes's own toolset — a self-referential eval that's actually useful.

**Rubric evolution path** (from 25+ agent memory notes):
1. R²-Mem (2026-05-23): rubric scoring with fixed thresholds (5, 10)
2. MemR³ (2026-05-23): evidence-gap convergence — agents refine their own retrieval
3. DeepEval (2026-05-22): G-Eval — free-form criteria, LLM-as-judge, no fixed thresholds
4. FLE (2026-05-22): Environment-based — evaluate by placing agent in a task and measuring outcome

The natural upgrade for heartbeat_learning.py: use G-Eval (DeepEval style) as the scoring mechanism instead of R²-Mem's fixed rubric. The judge LLM (DeepSeek) decides whether an action was good or bad based on natural language criteria, not a pre-defined threshold.

---

## 未追蹤

- https://github.com/jackhopkins/Factorio-Learning-Environment — FLE source (already fetched), worth revisiting for MCP eval integration
- https://deepeval.com/docs/metrics-task-completion — DeepEval TaskCompletionMetric details
- https://deepeval.com/docs/vibe-coder-quickstart — "vibe-coder" pattern: agent adds its own evals and fixes failures

## ✅ 本次探索完成

**時間**: 2026-05-22 06:50 CST
**Token cost**: 低（2次 fetch，GitHub README 乾淨）
**品質**: 高 — both projects are production-grade (FLE 749pts + MCP support, DeepEval 15k stars), concrete eval frameworks
**價值**: G-Eval pattern immediately applicable to WS-024 rubric upgrade; FLE MCP support validates WS-022 MCP server direction
