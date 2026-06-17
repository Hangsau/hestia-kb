---
_slug: 40-Resources-_mixed-explorations-2026-06-03-探索-alexzhang13-rlm-官方-Codebase
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-探索-alexzhang13-rlm-官方-Codebase.md
title: 探索：alexzhang13/rlm 官方 Codebase
date: 2026-06-03
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- alexzhang
- com
- core
- github
- https
- isolation
- metadata
- model
- prime
- rlm
created: '2026-06-03'
updated: '2026-06-15'
status: budding
---

# 探索：alexzhang13/rlm 官方 Codebase

**日期**: 2026-06-03 | **來源**: [[2026-06-02-rlm-paper-reinforcement-codeRLM]]（未追蹤 leads）| **類型**: EXPLORATION
**URLs**:
- https://github.com/alexzhang13/rlm — official codebase (4.4k stars)

---

## Source Insight — alexzhang13/rlm Codebase

### Repository Structure

```
rlm/
  clients/     — OpenAI, Anthropic, OpenRouter, Portkey API clients
  core/        — RLM engine core
  environments/ — REPL environments (local, ipython, docker, modal, prime, daytona, e2b)
  logger/      — trajectory logging + visualizer
  utils/
  __init__.py
  training/    — RL training harness (prime-rl based)
  examples/
  docs/
  visualizer/  — Node.js + shadcn/ui trajectory visualizer
```

### Core API Pattern

```python
from rlm import RLM
rlm = RLM(backend="openai", backend_kwargs={"model_name": "gpt-5-nano"})
result = rlm.completion("Print me the first 100 powers of two")
print(result.response)
```

Key design: `rlm.completion(prompt, model)` replaces `llm.completion(prompt, model)` — the RLM acts as the "language model" interface, offloading context as a variable in the REPL.

### Environment Isolation Levels

Three tiers (directly relevant to Talos governance):
1. **Non-isolated** (local exec) — default, same process, shares venv
2. **Semi-isolated** (IPython subprocess) — hard cell_timeout, namespace isolation
3. **Fully isolated** (cloud sandboxes: modal/prime/daytona/e2b) — separate machine, sub-calls as network requests

### Metadata-Only Trajectory Logging

The `RLMLogger` only appends **constant-size metadata** about each iteration, not the full prompt or context:
```python
logger = RLMLogger(log_dir="./logs")
rlm = RLM(..., logger=logger)  # each completion writes .jsonl
# Visualizer at localhost:3001
```

This is exactly the pattern noted in the RLM paper — the trajectory file is small because only metadata (not raw text) is logged at each step. This maps to heartbeat_learning.py: distillates should be compressed representations, not raw exploration notes.

### Training Harness

`training/` folder uses Prime Intellect's prime-rl with `rlm.RLM` as the verifiers Environment. OOLONG benchmark long-context QA as example environment.

---

## Hermes 啟發

### 1. RLM Environment Gradient Matches Talos Governance Gradient

The three-tier isolation (local → ipython → cloud sandbox) is the production-grade version of the guardian sandboxing gradient proposal (L1 tool scoping / L2 gateway mediation / L3 container). Key difference: RLM's environments are **first-class** (not wrappers) — the REPL is a first-class citizen with typed interfaces.

### 2. Metadata-Only Logging Validates Distillate Compression Approach

heartbeat_learning.py should store:
- Distillate as compressed metadata (not raw note text)
- Timestamp + contradiction count + usage frequency as search-indexable fields
- Full raw note accessible but not loaded into context

This matches RLM's constant-size metadata per iteration → bounded memory growth.

### 3. Multiple Sandbox Providers = Tool Isolation Pattern

e2b, Daytona, Modal, Prime — 4 cloud sandbox providers supported. This mirrors the MCP tool isolation design: not one-solution-fits-all, but a provider abstraction layer with multiple backends.

---

## 未追蹤 Leads

- https://github.com/alexzhang13/rlm/tree/main/rlm/core — core engine (to understand REPL loop internals)
- https://github.com/alexzhang13/rlm/blob/main/README.md#rlms-in-the-wild — DSPy.RLM, Ax, HALO examples (production use cases)
- https://github.com/antoinezambelli/forge#model-guide — from forge-gambit exploration, hardware model selection

---

## ✅ 本次探索完成


## Version 2 — 2026-06-03

# 探索：alexzhang13/rlm 官方 Codebase

**日期**: 2026-06-03 | **來源**: [[2026-06-02-rlm-paper-reinforcement-codeRLM]]（未追蹤 leads）| **類型**: EXPLORATION
**URLs**:
- https://github.com/alexzhang13/rlm — official codebase (4.4k stars)

---

## Source Insight — alexzhang13/rlm Codebase

### Repository Structure

```
rlm/
  clients/     — OpenAI, Anthropic, OpenRouter, Portkey API clients
  core/        — RLM engine core
  environments/ — REPL environments (local, ipython, docker, modal, prime, daytona, e2b)
  logger/      — trajectory logging + visualizer
  utils/
  __init__.py
  training/    — RL training harness (prime-rl based)
  examples/
  docs/
  visualizer/  — Node.js + shadcn/ui trajectory visualizer
```

### Core API Pattern

```python
from rlm import RLM
rlm = RLM(backend="openai", backend_kwargs={"model_name": "gpt-5-nano"})
result = rlm.completion("Print me the first 100 powers of two")
print(result.response)
```

Key design: `rlm.completion(prompt, model)` replaces `llm.completion(prompt, model)` — the RLM acts as the "language model" interface, offloading context as a variable in the REPL.

### Environment Isolation Levels

Three tiers (directly relevant to Talos governance):
1. **Non-isolated** (local exec) — default, same process, shares venv
2. **Semi-isolated** (IPython subprocess) — hard cell_timeout, namespace isolation
3. **Fully isolated** (cloud sandboxes: modal/prime/daytona/e2b) — separate machine, sub-calls as network requests

### Metadata-Only Trajectory Logging

The `RLMLogger` only appends **constant-size metadata** about each iteration, not the full prompt or context:
```python
logger = RLMLogger(log_dir="./logs")
rlm = RLM(..., logger=logger)  # each completion writes .jsonl
# Visualizer at localhost:3001
```

This is exactly the pattern noted in the RLM paper — the trajectory file is small because only metadata (not raw text) is logged at each step. This maps to heartbeat_learning.py: distillates should be compressed representations, not raw exploration notes.

### Training Harness

`training/` folder uses Prime Intellect's prime-rl with `rlm.RLM` as the verifiers Environment. OOLONG benchmark long-context QA as example environment.

---

## Hermes 啟發

### 1. RLM Environment Gradient Matches Talos Governance Gradient

The three-tier isolation (local → ipython → cloud sandbox) is the production-grade version of the guardian sandboxing gradient proposal (L1 tool scoping / L2 gateway mediation / L3 container). Key difference: RLM's environments are **first-class** (not wrappers) — the REPL is a first-class citizen with typed interfaces.

### 2. Metadata-Only Logging Validates Distillate Compression Approach

heartbeat_learning.py should store:
- Distillate as compressed metadata (not raw note text)
- Timestamp + contradiction count + usage frequency as search-indexable fields
- Full raw note accessible but not loaded into context

This matches RLM's constant-size metadata per iteration → bounded memory growth.

### 3. Multiple Sandbox Providers = Tool Isolation Pattern

e2b, Daytona, Modal, Prime — 4 cloud sandbox providers supported. This mirrors the MCP tool isolation design: not one-solution-fits-all, but a provider abstraction layer with multiple backends.

---

## 未追蹤 Leads

- https://github.com/alexzhang13/rlm/tree/main/rlm/core — core engine (to understand REPL loop internals)
- https://github.com/alexzhang13/rlm/blob/main/README.md#rlms-in-the-wild — DSPy.RLM, Ax, HALO examples (production use cases)
- https://github.com/antoinezambelli/forge#model-guide — from forge-gambit exploration, hardware model selection

---

## ✅ 本次探索完成


## Version 3 — 2026-06-03

# 探索：alexzhang13/rlm 官方 Codebase

**日期**: 2026-06-03 | **來源**: [[2026-06-02-rlm-paper-reinforcement-codeRLM]]（未追蹤 leads）| **類型**: EXPLORATION
**URLs**:
- https://github.com/alexzhang13/rlm — official codebase (4.4k stars)

---

## Source Insight — alexzhang13/rlm Codebase

### Repository Structure

```
rlm/
  clients/     — OpenAI, Anthropic, OpenRouter, Portkey API clients
  core/        — RLM engine core
  environments/ — REPL environments (local, ipython, docker, modal, prime, daytona, e2b)
  logger/      — trajectory logging + visualizer
  utils/
  __init__.py
  training/    — RL training harness (prime-rl based)
  examples/
  docs/
  visualizer/  — Node.js + shadcn/ui trajectory visualizer
```

### Core API Pattern

```python
from rlm import RLM
rlm = RLM(backend="openai", backend_kwargs={"model_name": "gpt-5-nano"})
result = rlm.completion("Print me the first 100 powers of two")
print(result.response)
```

Key design: `rlm.completion(prompt, model)` replaces `llm.completion(prompt, model)` — the RLM acts as the "language model" interface, offloading context as a variable in the REPL.

### Environment Isolation Levels

Three tiers (directly relevant to Talos governance):
1. **Non-isolated** (local exec) — default, same process, shares venv
2. **Semi-isolated** (IPython subprocess) — hard cell_timeout, namespace isolation
3. **Fully isolated** (cloud sandboxes: modal/prime/daytona/e2b) — separate machine, sub-calls as network requests

### Metadata-Only Trajectory Logging

The `RLMLogger` only appends **constant-size metadata** about each iteration, not the full prompt or context:
```python
logger = RLMLogger(log_dir="./logs")
rlm = RLM(..., logger=logger)  # each completion writes .jsonl
# Visualizer at localhost:3001
```

This is exactly the pattern noted in the RLM paper — the trajectory file is small because only metadata (not raw text) is logged at each step. This maps to heartbeat_learning.py: distillates should be compressed representations, not raw exploration notes.

### Training Harness

`training/` folder uses Prime Intellect's prime-rl with `rlm.RLM` as the verifiers Environment. OOLONG benchmark long-context QA as example environment.

---

## Hermes 啟發

### 1. RLM Environment Gradient Matches Talos Governance Gradient

The three-tier isolation (local → ipython → cloud sandbox) is the production-grade version of the guardian sandboxing gradient proposal (L1 tool scoping / L2 gateway mediation / L3 container). Key difference: RLM's environments are **first-class** (not wrappers) — the REPL is a first-class citizen with typed interfaces.

### 2. Metadata-Only Logging Validates Distillate Compression Approach

heartbeat_learning.py should store:
- Distillate as compressed metadata (not raw note text)
- Timestamp + contradiction count + usage frequency as search-indexable fields
- Full raw note accessible but not loaded into context

This matches RLM's constant-size metadata per iteration → bounded memory growth.

### 3. Multiple Sandbox Providers = Tool Isolation Pattern

e2b, Daytona, Modal, Prime — 4 cloud sandbox providers supported. This mirrors the MCP tool isolation design: not one-solution-fits-all, but a provider abstraction layer with multiple backends.

---

## 未追蹤 Leads

- https://github.com/alexzhang13/rlm/tree/main/rlm/core — core engine (to understand REPL loop internals)
- https://github.com/alexzhang13/rlm/blob/main/README.md#rlms-in-the-wild — DSPy.RLM, Ax, HALO examples (production use cases)
- https://github.com/antoinezambelli/forge#model-guide — from forge-gambit exploration, hardware model selection

---

## ✅ 本次探索完成
