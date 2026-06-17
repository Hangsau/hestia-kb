---
_slug: 40-Resources-_mixed-explorations-2026-06-06-pg_durable---PostgreSQL-In-Database-Durable-Execution
_vault_path: 40-Resources/_mixed/explorations/2026-06-06-pg_durable---PostgreSQL-In-Database-Durable-Execution.md
title: pg_durable — PostgreSQL In-Database Durable Execution
date: 2026-06-06
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- checkpoint
- durable
- execution
- external
- hermes
- postgres
- queue
- sql
- state
- workflow
created: '2026-06-06'
updated: '2026-06-15'
status: budding
---

# pg_durable — PostgreSQL In-Database Durable Execution

**Source**: Microsoft (752⭐, Rust) — https://github.com/microsoft/pg_durable

## Per-Source Insight

**What it is**: PostgreSQL extension that defines long-running workflows as SQL graphs using `|=>` (step) and `~>` (compose) operators. Each step checkpoints to Postgres; crash/resume from last checkpoint.

**Architecture**:
- Workflow = SQL function, not external service
- State in Postgres (`df.instances` table), survives crashes
- Fan-out: `df.start(...)` → parallel steps → join → dashboard step
- No Redis, no Temporal, no external queue

**Key properties**:
- **Durable**: crash survival via Postgres WAL + checkpoint state
- **SQL-native**: workflow defined in SQL composable operators
- **Zero infra**: extension only, no external dependencies

**Similar to**: Temporal's durable execution, but embedded in Postgres instead of separate service.

**When not to use**: sub-ms sync requests, can't install extensions, workflow spans many heterogeneous external systems.

## Hermes Relevance

**Directly relevant to WS-020 (Multi-Agent Write Queue)**:
- WS-020's problem: multiple agents writing to same vault/proposal without coordination
- pg_durable shows: **durable execution can live inside the data store itself**
- Instead of external queue (Redis, file lock) → workflow state in Postgres
- For Hermes: instead of `fcntl.LOCK_EX` on NFS (the rejected方案A), or external queue daemon (rejected 方案C)
- **Option**: use Hermes's existing state storage (proposals, vault) as the durable log
- Checkpoint = write to proposal/vault + record position; resume = read from last checkpoint
- Inspiration: `df.start()` pattern → `hermes_queue.start()` for write coordination

**Complements existing work**:
- `managed-agents-architecture` skill's Supervisor Agent pattern
- Pipelex typed pipe pattern from autonomous notes
- Orloj `join.mode: wait_for_all` DAG

**Not a full implementation** — provides architectural direction: durable workflow state can live in the data layer, not the application layer.

## Untracked Leads
- https://microsoft.github.io/pg_durable/ — official docs + quick example
- docs/ directory in repo for detailed operator reference
