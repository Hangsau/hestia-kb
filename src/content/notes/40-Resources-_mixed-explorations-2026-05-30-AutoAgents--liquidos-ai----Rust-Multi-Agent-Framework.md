---
_slug: 40-Resources-_mixed-explorations-2026-05-30-AutoAgents--liquidos-ai----Rust-Multi-Agent-Framework
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-AutoAgents--liquidos-ai----Rust-Multi-Agent-Framework.md
title: AutoAgents (liquidos-ai) — Rust Multi-Agent Framework
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- autoagents
- github
- guardrails
- https
- liquidos
- llmlayer
- pipeline
- sandbox
- tool
- wasm
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# AutoAgents (liquidos-ai) — Rust Multi-Agent Framework

**URL**: https://github.com/liquidos-ai/AutoAgents | **Stars**: 659 | **Date**: 2026-05-30

## Core Architecture

**Rust-first multi-agent framework** — type-safe agents, structured tool calling, WASM sandbox, typed pub/sub communication.

### Key Differentiators

| Feature | Details |
|---|---|
| **WASM sandbox** | Sandboxed tool execution — untrusted tools run in WASM runtime |
| **Typed pub/sub** | Compile-time type-safe message passing between agents, not raw strings |
| **Sliding window memory** | Configurable backends, not just a fixed strategy |
| **LLM Guardrails** | LLMLayer in pipeline (Block/Sanitize/Audit policies) |
| **LLM Optimization** | Cache + retry optimization passes built into pipeline |
| **MCP integration** | Native MCP server/client support in examples |

### Guardrails Architecture (Notable)

AutoAgents implements guardrails as an **LLMLayer** in the inference pipeline — input/output sanitization happens at the LLM layer, not at tool level. This is a different point of intervention compared to tool scoping.

```
Request → Guardrail (input) → LLM → Guardrail (output) → Response
```

Relevant to Talos governance: the LLMLayer concept gives a structured place to inject policy checks without modifying individual tools.

### WASM Tool Execution

The WASM sandbox allows running untrusted third-party tools without compromising the host. Example: `wasm_agent` example in the repo. This maps directly to the Guardian Sandboxing Gradient (L3 container) proposal.

### Python Bindings

`autoagents-py` on PyPI — can be installed with extras for llama.cpp, mistral-rs, guardrails, etc.

## Hermes Connections

1. **WS-035 memory**: Sliding window memory with extensible backends is similar to what heartbeat_learning.py does, but more structured. The `memory backend` abstraction is cleaner than current single-layer distillate.
2. **Talos governance**: WASM sandbox for tool execution directly addresses the Guardian Sandboxing Gradient proposal (L3). Typed pub/sub is a concrete implementation of the single-writer queue concept from the governance pipeline blueprint.
3. **LLMLayer guardrails**: The LLMLayer as a pipeline component (not tool-level) is a more composable architecture than current tool scoping — worth considering for `exploration-tool-scoping-gradient`.

##未追蹤 Leads
- https://github.com/liquidos-ai/AutoAgents-CLI — YAML-based workflow runner over HTTP
- https://liquidos-ai.github.io/AutoAgents/ — Full API docs
- https://github.com/liquidos-ai/AutoAgents-Experimental-Backends — Experimental providers (Burn, Onnx)

## ✅ 本次探索完成

