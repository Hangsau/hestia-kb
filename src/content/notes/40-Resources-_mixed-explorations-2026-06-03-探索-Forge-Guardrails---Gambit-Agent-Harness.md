---
_slug: 40-Resources-_mixed-explorations-2026-06-03-探索-Forge-Guardrails---Gambit-Agent-Harness
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-探索-Forge-Guardrails---Gambit-Agent-Harness.md
title: 探索：Forge Guardrails + Gambit Agent Harness
date: 2026-06-03
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- calls
- forge
- gambit
- guardrails
- harness
- layer
- model
- tool
- tools
created: '2026-06-03'
updated: '2026-06-15'
status: budding
---

# 探索：Forge Guardrails + Gambit Agent Harness

**日期**: 2026-06-03 | **來源**: HN Algolia (Forge 687pts, Gambit 91pts) | **類型**: EXPLORATION

## Per-Source Insight

### Forge — Guardrails for 8B Models (687pts Show HN)

**URL**: https://github.com/antoinezambelli/forge

**Core claim**: "takes an 8B local model from single digits to 84%" on 26-scenario eval suite (v0.7.0).

**Architecture** — three ways to use:
1. **Proxy server** — drop-in OpenAI/Anthropic API proxy, sits between any client and local model server. forge applies guardrails transparently. Works with Claude Code, opencode, Continue, aider — no rewrite.
2. **WorkflowRunner** — define tools + pick backend, forge manages full lifecycle (system prompts, tool execution, context compaction, guardrails). `SlotWorker` for priority-queued GPU slot access in multi-agent architectures.
3. **Guardrails middleware** — composable middleware inside your own loop.

**Key mechanisms**:
- `ResponseValidator` — each tool call checked against tools array before response returns
- `Rescue parsing` — extracts malformed tool calls (Mistral `[TOOL_CALLS]`, Qwen `<tool_call>` XML, fenced JSON) and re-emits in canonical OpenAI `tool_calls` schema
- **Retry loop** — corrective tool-result message on canonical channel, not a malformed response returned
- **Synthetic respond tool** — injected when tools present; model calls it instead of bare text; stripped from outbound response → client sees normal `finish_reason: "stop"`. Essential for small models (~8B) that can't choose between text and tool calls
- `TieredCompact` context strategy — keeps recent N turns

**Backends**: Ollama, llama-server (llama.cpp), Llamafile, vLLM, Anthropic

**Paper**: IEEE published — "Forge: A Reliability Layer for Self-Hosted LLM Tool-Calling" (DOI: 10.1145/3786335.3813193)

---

### Gambit — Agent Harness Framework (91pts Show HN)

**URL**: https://github.com/bolt-foundry/gambit

**Core focus**: "Agent frameworks help you build agents. Gambit helps you create the evidence that they work."

**Positioning**: synthetic scenario + evaluation layer. Generate realistic scenarios → validate quality → run agents → grade behavior → capture trace evidence → turn failures into regression suites.

**Key workflows**:
- **Native Gambit path** — define agent in Gambit, run locally, attach graders, inspect traces in simulator, reuse in CI
- **Bring your own agent** — use Mastra/LangGraph/OpenAI to build agent, use Gambit to create/validate scenario suites
- **PR gate** — run scenarios on every PR, fail check when behavior drops

**Architecture**:
- `deck.md` — agent definition format (Markdown with `+++` frontmatter for modelParams, actions)
- `simulator` — Debug UI (build/test/grade/verify), runs at `localhost:8000`
- Graders defined as `deck.md` files
- Traces as JSONL (`--trace .gambit/chat/trace.jsonl`)
- `runtime-tools` — mock tool fixtures for reproducible testing
- Worker sandbox execution by default (can disable with `--no-worker-sandbox`)

**Observability**: transcript lanes + trace/tools feed + state persistence under `.gambit/`

---

## Hermes Notes

**Relevance to Talos governance (exploration-tool-scoping-gradient, WS-035)**:

Forge's guardrails stack directly addresses `exploration-tool-scoping-gradient` — it enforces tool call validity without requiring model fine-tuning. The `ResponseValidator` + `Rescue parsing` dual-layer is analogous to Hermes's sanitizer + Phase-Lock pattern.

Forge's **synthetic respond tool injection** is particularly relevant: small models (~8B) need explicit guidance to use tools vs text. This maps to the "structured output over free-form" principle in Talos governance — force the right behavior rather than trusting the model to self-regulate.

Gambit's **evidence-based agent verification** aligns with the `agent-observability-landscape` research: Gambit is a concrete implementation of "Task Eval" layer (grading behavior from transcripts/traces) + "Product Analytics" layer (scenario quality, coverage metrics).

**Forge + Gambit convergence**: Both are reliability layers for agents — Forge focuses on tool-calling fidelity, Gambit on behavioral verification. Together they form: Forge = L1 guardrails (enforce correct tool calls), Gambit = L2 eval harness (measure and regression-test agent behavior). This two-layer pattern (enforcement + measurement) is a concrete architecture for Talos governance.

**Not directly implementable as-is** — both are substantial Python/TypeScript frameworks. But the *pattern* (proxy guardrails + eval harness) is the right architecture for Talos governance pipeline.

---

## Untracked Leads
- https://github.com/flowersteam/lamorel — compute-efficient alternative to LlamaGym (from 2026-06-03 exploration)
- https://github.com/antoinezambelli/forge#model-guide — which model fits your hardware (potential lead for local model selection)
- Gambit `runtime-tools` mock fixture pattern — could inform Talos test harness design

## ✅ 本次探索完成
