---
_slug: 40-Resources-_mixed-explorations-2026-06-04-Exploration---2026-06-04---Microsoft-AGT-Policy-Engine-Archi
_vault_path: 40-Resources/_mixed/explorations/2026-06-04-Exploration---2026-06-04---Microsoft-AGT-Policy-Engine-Archi.md
title: Exploration — 2026-06-04 | Microsoft AGT Policy Engine Architecture
date: 2026-06-04
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agt
- deny
- governance
- intervention
- manifest
- model
- policy
- tool
- verdict
created: '2026-06-04'
updated: '2026-06-15'
status: budding
---

# Exploration — 2026-06-04 | Microsoft AGT Policy Engine Architecture

**延續自**: 2026-06-04-ai-agent-tooling-architecture.md

## Sources

### Microsoft Agent Governance Toolkit (AGT) — 3902 stars
**URL**: https://github.com/microsoft/agent-governance-toolkit
**Points**: Trending (HN, recent update 3 days ago)

**Per-Source Insight**:
AGT's `policy-engine/` contains the Agent Control Specification (ACS) v0.3.1-beta — a formal, machine-readable policy enforcement specification. Key architectural findings:

**8 Formal Intervention Points**:
| Point | Position | Policy Target |
|-------|----------|---------------|
| `agent_startup` | Session start | Agent metadata |
| `input` | External request ingress | User input/payload |
| `pre_model_call` | Before model request | Model request |
| `post_model_call` | After model response | Model response |
| `pre_tool_call` | Before tool invocation | Tool arguments |
| `post_tool_call` | After tool invocation | Tool result |
| `output` | Final response assembly | Final output |
| `agent_shutdown` | Session end | Full snapshot |

**Verdict Hierarchy**: `allow` | `warn` | `deny` | `escalate` | `transform`
- `deny` always wins (cannot be overridden by lower-severity verdicts)
- `transform` verdict carries replacement value, applied in `enforce` mode

**Policy Manifest Format**: YAML or JSON, key fields:
- `agent_control_specification_version`: version string
- `policies`: map of named decision rules
- `intervention_points`: configuration for each intervention point
- `tools`: catalog for projection
- `extends`: parent manifest inheritance (URL or path, with sha256 integrity pinning)

**Path Grammar** (formal snapshot selector):
- `$snap`: raw host snapshot
- `$pi`: policy input
- `$policy_target`: value at `$pi.policy_target.value`
- `.name` selects object member, `[n]` selects array element

**Runtime Invariants**:
1. **Stateless**: no mutable state between evaluations
2. **Deterministic**: same manifest+snapshot+mode → same verdict
3. **Fail closed**: any runtime error → `deny` verdict with reserved reason

**Key Security Design**:
- URL `extends` must be HTTPS only; plain http fails closed
- sha256 integrity pinning for URL fetches
- Path traversal in file-based loader confined to top-level manifest directory
- Cycle detection in manifest inheritance

**deny.toml** (Cargo workspace policy):
- License allowlist: Apache-2.0, BSD-2/3, MIT, etc.
- Unknown registry/git → deny
- Private registry ignored

---

## 跨文章 Synthesis

AGT's ACS formalizes what the Talos governance pipeline proposals have been circling:
- **Intervention point model** = the "where do we intercept" question answered with 8 defined hooks
- **Policy = named decision rule at intervention point** = the "what happens at each hook" answer
- **Manifest-based declarative config** = the "how do we express rules" answer (TOML/YAML)
- **Transform verdict** = the "how do we modify rather than block" answer (relevant to heartbeat's correction mechanism)
- **Fail-closed on runtime error** = the "what's the default behavior when something breaks" answer

Three converging patterns across all recent explorations (Axe CLI, Tabstack, AGT):
1. **Declarative policy over imperative code** — both Axe (TOML agent config) and AGT (YAML manifest) use structured config
2. **Structured interception points** — 8 formal hooks (AGT) vs filesystem sandbox + SSRP (Axe)
3. **Token/budget as first-class enforcement** — exit code 4 on budget exceeded (Axe) maps to `runtime_error:budget_exceeded` in AGT's reserved reasons

---

## Hermes 啟發

1. **Talos governance pipeline should adopt ACS intervention point model** — 8 defined hooks give us a formal vocabulary for "where Talos intercepts". Existing proposals (ws-035, dcgs integration) can reference ACS rather than inventing custom taxonomy.

2. **AGT's `transform` verdict is relevant to heartbeat correction** — instead of just allow/deny, we can replace the policy target. This maps to heartbeat's "auto-fix" rather than "just alert" behavior.

3. **Manifest inheritance with integrity pinning** — AGT's `extends` with sha256 is a good model for Talos policy versioning. We could have base policy + per-agent overrides.

4. **Rust policy engine (policy-engine/)** — written in Rust, suggesting performance-critical. Could be relevant if Talos governance needs high-throughput interception.

---

## 未追蹤 Leads
- https://github.com/microsoft/agent-governance-toolkit/tree/main/agent-governance-python/agent-hypervisor (Python hypervisor implementation)
- https://github.com/microsoft/agent-governance-toolkit/tree/main/policy-engine/spec/agt/AGT-RESOLUTION-1.0.md (resolution algorithm for manifest inheritance)

## ✅ 本次探索完成
