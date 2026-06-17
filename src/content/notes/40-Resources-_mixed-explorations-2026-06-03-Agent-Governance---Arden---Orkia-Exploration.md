---
_slug: 40-Resources-_mixed-explorations-2026-06-03-Agent-Governance---Arden---Orkia-Exploration
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-Agent-Governance---Arden---Orkia-Exploration.md
title: 2026-06-03 Agent Governance — Arden + Orkia Exploration
date: 2026-06-03
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arden
- cupcake
- enforcement
- governance
- layer
- opa
- orkia
- policy
- runtime
created: '2026-06-03'
updated: '2026-06-15'
status: budding
---

# 2026-06-03 Agent Governance — Arden + Orkia Exploration

**延續自**: [[2026-06-03-agent-governance-cupcake]] (Cupcake 已探索，本筆記聚焦 Arden + Orkia)

## Sources

### 1. Arden — Runtime Policy Enforcement

**URL**: https://www.arden.sh/
**Source**: HN Show HN (8pts)
**Points**: 8

**Key Findings**:
Arden is an OPA-based runtime governance layer for AI agents — similar in spirit to Cupcake but with a different approach:

- **Policy Enforcement**: OPA (Open Policy Agent) based, per-tool policies with conditions/thresholds
  - `allowstripe.refund < $50` / `reviewstripe.refund ≥ $50` / `blockdb.delete_*`
- **Human-in-the-Loop**: Slack notification for approvals — one click approve/deny, no dashboard login
- **Audit Trail**: Full session replay, policy coverage gap detection ("no policy configured" → shows which tools need guardrails)
- **Token/Cost Governance**: Built-in token capture, cost per agent/session/day breakdown, budget enforcement before runaway
- **Integration**: `pip install ardenpy` → `arden.configure(api_key="...")` — auto-patches LangChain/CrewAI/OpenAI Agents SDK with zero code changes
- **Native integrations**: LangChain, CrewAI, OpenAI Agents SDK, LlamaIndex, AutoGen
- **Free tier**: 10k actions/month, no credit card required

**Architecture insight**:
Arden is a **proxy layer** — tool calls go through Arden before execution. This is different from Cupcake's compilation-time OPA policy embedding. Arden intercepts at runtime, which means:
1. No agent code changes required
2. Policy changes without redeployment
3. Works with any framework that uses standard tool calling patterns

**Comparison with Cupcake (from previous session)**:
- Cupcake: compile-time OPA embedding via LSP server, better for security-hardened environments
- Arden: runtime proxy, better for operational flexibility and gradual policy rollout

**Hermes relevance**: The governance pipeline proposals (WS-034/WS-035) could use Arden as the policy enforcement layer. The audit trail + HITL approval pattern is directly applicable.

---

### 2. Orkia — Rust Runtime Governance

**URL**: https://github.com/orkiaHQ/orkia (404 — repo removed or private)
**Source**: HN Show HN (2pts)
**Points**: 2

**Status**: ~~https://github.com/orkiaHQ/orkia~~ → 404, page removed

Rust-based enforcement runtime, but the repository is no longer accessible. Not enough information to extract meaningful insights.

---

## Cross-article Synthesis

**Convergence on proxy-layer governance**: Both Arden and the Cupcake approach (from previous session) converge on the same insight — governance should be a **separate layer** from the agent logic itself, not baked into the agent code.

- Cupcake: compile-time embedding (LSP + OPA)
- Arden: runtime interception (proxy layer)
- Orkia: attempted Rust runtime (dead link)

This confirms the architectural direction of WS-035 (policy engine gateway integration): Hermes should implement a **gateway-level enforcement layer** that intercepts tool calls, evaluates policies, and optionally holds for human approval — before the tool executes.

**Policy language**: OPA/Rego appears in both Cupcake and Arden. This suggests OPA is becoming the de-facto standard for agent policy languages, not a custom DSL.

---

## Untracked Leads

- https://www.arden.sh/ — confirmed, worth deeper dive (GitHub + docs)
- https://github.com/akz4ol/contextgraph-cloud — HN governance infrastructure, not yet explored

## ✅ Exploration Complete
