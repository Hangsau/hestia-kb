---
_slug: 40-Resources-_mixed-explorations-2026-06-03-Exploration---2026-06-03-AI-Agent-Governance
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-Exploration---2026-06-03-AI-Agent-Governance.md
title: Exploration — 2026-06-03 AI Agent Governance
date: 2026-06-03
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- cupcake
- enforcement
- evaluation
- governance
- mcp
- opa
- policy
- talos
- tool
created: '2026-06-03'
updated: '2026-06-15'
status: budding
---

# Exploration — 2026-06-03 AI Agent Governance

**延續自**: 2026-06-03-forge-gambit-agent-harness

## Cupcake — Native Policy Enforcement Layer for AI Coding Agents

### Source
- GitHub: `eqtylab/cupcake` (268⭐, Apache 2.0, Rust)
- Homepage: https://cupcake.eqtylab.io/
- HN: https://news.ycombinator.com/show?hn=48387229 (12 pts)

### What it is
Policy enforcement layer that intercepts agent actions, evaluates them against OPA/Rego policies compiled to WebAssembly, and returns enforcement decisions (Allow/Modify/Block/Warn/Require Review).

### Architecture

```
Agent → (proposed action) → Cupcake → (policy decision) → Agent runtime
```

1. **Interception**: Agent prepares to execute a tool-call (e.g., `git push`, `fs_write`)
2. **Enrichment**: Cupcake gathers real-time **Signals** — environment facts (Git branch, CI status, DB metadata)
3. **Evaluation**: Action + signals packaged as JSON → evaluated against Wasm-compiled OPA/Rego policies in milliseconds

### Two evaluation models
1. **Deterministic Policies**: OPA/Rego compiled to Wasm — fast, sandboxed
2. **LLM‑as‑Judge**: Secondary LLM agent for dynamic oversight (Cupcake Watchdog)

### Five enforcement decisions
- **Allow**: Proceed + optional context injection ("Remember: you're on main branch")
- **Modify**: Sanitize commands, add safety flags, enforce conventions before execution
- **Block**: Stop + feedback explaining why (agent self-corrects)
- **Warn**: Proceed but log warning
- **Require Review**: Pause for human approval

### Supported Harnesses
| Harness | Status |
|---------|--------|
| Claude Code | ✅ Fully Supported |
| Cursor | ✅ Fully Supported |
| Factory AI | ✅ Fully Supported |
| OpenCode | ✅ Fully Supported |
| AMP | Coming soon |
| Gemini CLI | Coming soon |

Policies are separated by harness (`policies/claude/`, `policies/cursor/`, etc.) — harness-specific event formats.

### Key features relevant to Talos governance

**1. MCP tool governance**
Native handling of `mcp__memory__*`, `mcp__github__*` tools. Directly addresses `exploration-tool-scoping-gradient` proposal — enforces which MCP tools are allowed/blocked at the policy layer, not at the agent level.

**2. Granular Tool Control**
Prevent specific tools or arguments (e.g., blocking `rm -rf /`). Uses policy-as-code rather than model instruction.

**3. Observability**
All inputs, signals, decisions generate structured logs and evaluation traces — directly maps to `agent-observability-landscape` research (Product Analytics + Task Eval layers).

**4. Multi-harness support**
First-class integrations for Claude Code, Cursor, Factory AI, OpenCode — exactly the scope Talos governance pipeline needs to cover.

**5. Deterministic evaluation via Wasm**
OPA/Rego compiled to WebAssembly — fast, sandboxed execution. No model context consumption.

### Comparison to existing exploration references

| Aspect | AGT (Microsoft) | Cupcake |
|--------|----------------|---------|
| Policy language | OPA/Cedar YAML | OPA/Rego → Wasm |
| Enforcement model | Agent Hypervisor | Hook-based interception |
| MCP tool governance | Yes | Yes (native) |
| LLM-as-Judge | Via orchestrator | Built-in (Watchdog) |
| Supported agents | General | Claude Code/Cursor/Factory/OpenCode |
| Implementation | TypeScript | Rust |

### Relevance to Talos

**Directly applicable to**:
- `exploration-tool-scoping-gradient` — tool whitelist enforcement without fine-tuning
- `agent-observability-landscape` — structured evaluation traces for Product Analytics layer
- WS-035 (structured memory governance) — MCP tool governance pattern

**Pattern to extract**:
The core insight: policy enforcement should be **decoupled from agent** and executed **before** action. Wasm-compiled OPA gives deterministic, fast, sandboxed evaluation. This is the "proxy guardrails" pattern from Forge + Gambit research, but with explicit enforcement (block/modify) rather than just monitoring.

**Not a replacement for**:
Talos governance pipeline — Cupcake operates at tool-call level, not at session/agent coordination level. But the policy-as-code + Wasm evaluation pattern is directly portable to Talos tool isolation.

---

## Hermes Notes

**Relevance to Talos governance pipeline**:

Cupcake's architecture confirms the "enforcement layer" approach is correct and production-viable. Key lessons:

1. **OPA/Rego as policy language** — already in Talos governance references (AGT, DCG). Cupcake shows it compiles to Wasm for speed.
2. **Signal enrichment** — gathering environment facts (Git branch, CI status) before evaluation. Maps to Talos heartbeat snapshot approach.
3. **Decision taxonomy** (Allow/Modify/Block/Warn/Require Review) — concrete enforcement outcomes. Better than "enforce" vs "monitor" binary.
4. **MCP tool governance** — native `mcp__*` handling. Directly fills the MCP governance gap in `exploration-tool-scoping-gradient`.
5. **Context injection** — "Allow + inject context" pattern. Maps to `guardian-sandboxing-gradient` — not just blocking but guiding.

**Action**: Update `exploration-tool-scoping-gradient` proposal to mark as PARTIAL — Cupcake (via OPA/Wasm) + AGT (via YAML policy) together cover tool whitelist enforcement, though neither provides the multi-agent coordination layer Talos needs.

## Untracked Leads
- https://cupcake.eqtylab.io/getting-started/ — getting started docs for each harness
- `eqtylab/cupcake` GitHub — check `policies/` directory structure for concrete policy examples
- Cupcake Watchdog (LLM-as-Judge mode) — separate installation path from core enforcement

## ✅ 本次探索完成
