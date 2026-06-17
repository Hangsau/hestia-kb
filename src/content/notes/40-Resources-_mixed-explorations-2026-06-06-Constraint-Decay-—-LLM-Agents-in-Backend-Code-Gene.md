---
_slug: 40-Resources-_mixed-explorations-2026-06-06-Constraint-Decay-—-LLM-Agents-in-Backend-Code-Gene
_vault_path: 40-Resources/_mixed/explorations/2026-06-06-Constraint-Decay-—-LLM-Agents-in-Backend-Code-Gene.md
title: Constraint Decay — LLM Agents in Backend Code Generation
created: '2026-06-06'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Constraint Decay — LLM Agents in Backend Code Generation

**Source**: arxiv:2605.06445v1 (Francesco Dente, Dario Satriani, Paolo Papotti — EURECOM/University of Basilicata, May 2026)

## Per-Source Insight

**What it is**: Systematic study of how LLM agents handle structural constraints (Clean Architecture, PostgreSQL, ORM) in multi-file backend generation. Fixed a single OpenAPI contract across 80 tasks, layered constraints L0→L3, measured with behavioral tests + static verifiers.

**Core finding — constraint decay**:
- Capable configs lose **~30pp** in assertion pass rates from L0 (no structural constraints) to L3 (full Clean Architecture + PostgreSQL + SQLAlchemy)
- Weaker configs (Qwen3-235B) approach **zero** at L3
- Flask (minimal/explicit) >> FastAPI/Django (convention-heavy) — framework sensitivity is large

**Root causes (RQ3)**:
- **45% of logic failures** come from data-layer defects: incorrect query composition + ORM runtime violations
- Clean Architecture constraint alone accounts for the bulk of the decay
- Agents handle functional specs well; structural constraints are what break them

**Architecture**:
- 80 greenfield tasks (8 frameworks × 10 constraint combos)
- 20 feature-implementation tasks (ablated real-world repos)
- Behavioral tests (Postman, 32 requests, 291 assertions) + static verifiers (architecture/DB/ORM compliance)
- Dual-phase Docker: build (agent) → evaluate (tests)

## Hermes Relevance

**Directly relevant to WS-020 (Multi-Agent Write Queue)**:
- Constraint decay explains *why* multi-agent coordination degrades: each agent adds structural constraints, performance collapses
- Data-layer defects (45%) = the writes from different agents stepping on each other's state
- pg_durable note (same session) showed: durable execution can live in the data store — this paper shows: data-layer defects are the primary failure mode
- For Talos governance: tool scoping (4-tool limit) directly addresses constraint decay by reducing the structural complexity each agent must handle

**Architecture insight**:
- The paper's static verifiers (architecture/DB/ORM) are analogous to Talos governance policy enforcement
- The paper measures constraint density; Talos could measure agent action complexity density
- Clean Architecture constraint = the most damaging single axis — this maps to "don't let agents mix concerns across too many domains"

**Complements**:
- pg_durable: durable execution in data layer; this paper: data layer is the primary failure point
- PhantomPolicy (2026-06-06): policy-relevant facts hidden at decision time = a specific type of constraint that decays
- constraint.decay confirms: strict tool surface > unlimited access (WS-020 governance implication)

## Untracked Leads
- https://anonymous.4open.science/r/constraint-decay — evaluation pipeline, task suite, agent trajectories, analysis scripts (anonymized repo)
- Mini-SWE-Agent scaffold modifications for greenfield generation (Appendix J) — directly relevant to Talos agent scaffold design

## ✅ 本次探索完成