---
_slug: 40-Resources-_mixed-explorations-2026-06-02-探索-RLM-Paper---Reinforcement-CodeRLM-產品
_vault_path: 40-Resources/_mixed/explorations/2026-06-02-探索-RLM-Paper---Reinforcement-CodeRLM-產品.md
title: 探索：RLM Paper + Reinforcement/CodeRLM 產品
date: 2026-06-02
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- code
- coderlm
- context
- drift
- https
- llm
- paper
- rlm
- state
- sub
created: '2026-06-02'
updated: '2026-06-15'
status: budding
---

# 探索：RLM Paper + Reinforcement/CodeRLM 產品

**日期**: 2026-06-02 | **來源**: CodeRLM vault note 延伸（未追蹤 leads）| **類型**: EXPLORATION
**URLs**:
- https://arxiv.org/abs/2512.24601（RLM paper v3, 2026-05-11）
- https://getreinforcement.com/（CodeRLM 產品/公司官網）

---

## Source Insight — RLM Paper (arXiv:2512.24601v3)

### Core Thesis
Recursive Language Models (RLMs) treat long prompts as part of an external environment — not as context to dump into the LLM, but as a symbolic object the LLM can programmatically examine, decompose, and recursively invoke itself over snippets of.

### Key Distinction: RLM vs. Naive Sub-call Scaffold

RLM (correct):
- Prompt stored as **variable in REPL**, not in LLM context
- LLM generates **code** to inspect/decompose the prompt variable
- Sub-calls are **programmatic** — can be inside loops, Ω(|P|) or Ω(|P|²) processes

Naive scaffold (Algorithm 2, flawed):
- Prompt loaded directly into **LLM context** → inherits context window limits
- Finish action produces output directly → bounded by context window
- Sub-calls are **verbalized**, not programmatic — can't loop over arbitrary slices

### Concrete Algorithm
```
state ← InitREPL(prompt=P)
state ← AddFunction(state, sub_RLM)
hist ← [Metadata(state)]
while True:
  code ← LLM(hist)
  (state, stdout) ← REPL(state, code)
  hist ← hist ∥ code ∥ Metadata(stdout)
  if state[Final] is set:
    return state[Final]
```
- Only **constant-size metadata** about stdout is appended to LLM history each iteration
- Forces model to rely on **variables and sub-calls** to manage long strings, not context

### Performance Results (GPT-5)
- On OOLONG-Pairs (quadratic complexity): +130% vs CodeAct with sub-calls
- On S-NIAH (constant complexity): comparable
- 10M+ token scale: maintains performance, others degrade steeply
- Cost: comparable at 50th percentile, tail can be high (Qwen3-Coder makes thousands of sub-calls on simple tasks)

### Three Design Requirements for Expressive Power
1. **Symbolic handle to prompt** — LLM gets a variable, not the text itself
2. **No direct output** — model doesn't verbalize output, builds Final variable
3. **Symbolic recursion** — code inside REPL can invoke LLM on programmatically constructed slices

---

## Source Insight — Reinforcement/CodeRLM 官網

### Product Positioning
- **Problem**: "Agents read code they don't need. Then miss the code they do." — glob/grep/read loop is high-noise
- **Solution**: Real-time symbol index as JSON API — exact symbols, callers, implementations

### CodeRLM Architecture
```
coderlm init .  →  session with files_indexed, symbols count
coderlm search "authenticate"  →  [{name, kind, file}]
coderlm callers authenticate_user --file src/auth.py  →  [file:line, ...]
```
- No glob. No scan. No guess. Signal-to-noise order-of-magnitude better.

### Studio (early preview)
- Managed workspace built on CodeRLM
- Teams link repos (schema, API, frontend, IaC) and author specs alongside
- **Bidirectional symbol ↔ spec references** — detects when code drifts from spec
- Drift detection: `CodeRLM · 3h Drifts: verify_token() now takes a device_id`

---

## Hermes 啟發

### 1. RLM Pattern is the Theoretical Grounding for WS-035 Drift Penalty

The RLM paper's core insight — treating external data as recursively-examinable structures rather than context dumps — maps directly to the heartbeat_learning.py staleness problem.

**Current gap**: heartbeat_learning.py uses time-based decay only. When a new distillate contradicts an earlier one, there's no mechanism to invalidate the old distillate's confidence.

**RLM solution for drift penalty**: Build a **concept relationship graph** where:
- Nodes = distillates (timestamped insights)
- Edges = mentions/contradictions/supersedes relationships between distillates
- When a new distillate creates a **contradiction edge** to an earlier node → invalidate old node's confidence
- This is structural staleness detection, not temporal

### 2. CodeRLM's Symbol Graph is the Code-Domain Analog

CodeRLM builds a symbol table (functions → callers → implementations) and makes it queryable. The RLM then recursively queries this graph rather than dumping files into context.

For Hermes memory:
- Current: distillates dumped into context, no structure
- Better: distillates as nodes in a relationship graph, new information can invalidate old nodes
- This is exactly what SSGM's "bounded semantic drift via periodic reconciliation" aims for

### 3. Reinforcement Studio's Drift Detection is a Concrete Pattern

Studio shows: `CodeRLM · 3h Drift: verify_token() now takes a device_id.`

This is **symbol-level drift detection** — the spec references `authenticate_user()` but the actual code now has `verify_token()` with different signature. This is a template for how drift detection could work at the concept level in heartbeat_learning.py.

### 4. Zero Python Dependencies (reinforcement)

CodeRLM CLI wrapper uses Python stdlib only. The heartbeat_v2.py dependency philosophy could learn from this.

---

## 未追蹤 Leads

- ~~https://arxiv.org/abs/2512.24601~~ → 已讀（見上方）
- ~~https://getreinforcement.com/~~ → 已讀（見上方）
- https://github.com/alexzhang13/rlm — RLM paper official codebase
- https://github.com/JaredStewart/coderlm — CodeRLM server (already in vault note)

## ✅ 本次探索完成
