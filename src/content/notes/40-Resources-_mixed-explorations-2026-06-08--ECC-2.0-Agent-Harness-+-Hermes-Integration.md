---
_slug: 40-Resources-_mixed-explorations-2026-06-08--ECC-2.0-Agent-Harness-+-Hermes-Integration
_vault_path: 40-Resources/_mixed/explorations/2026-06-08--ECC-2.0-Agent-Harness-+-Hermes-Integration.md
title: 'Exploration: ECC 2.0 Agent Harness + Hermes Integration'
created: '2026-06-08'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Exploration: ECC 2.0 Agent Harness + Hermes Integration

**日期**: 2026-06-08 | **來源**: HN trending + GitHub API | **類型**: Architecture Research

## Per-Source Insights

### ECC (affaan-m/ECC) — 182k⭐ Harness Operating System

ECC v2.0.0-rc.1 ships a dedicated `docs/HERMES-SETUP.md` — first external project to treat Hermes as first-class surface.

**Architecture (HERMES-SETUP.md)**:
```
Telegram / CLI / TUI
        ↓
      Hermes
        ↓
 ECC skills + hooks + MCPs + generated workflow packs
        ↓
 Google Drive / GitHub / browser automation / research APIs / media tools / finance tools
```

**ECC 2.0 Reference Architecture** references 10+ external agent systems:
- `NousResearch/hermes-agent` — "self-improving operator shell with memories, skills, scheduler, gateways, subagents, terminal backends, and migration tooling"
- `stanford-iris-lab/meta-harness` — "automated search over task-specific harness design"
- `greyhaven-ai/autocontext` — "recursive harness improvement using traces, reports, artifacts, datasets, playbooks"
- superset-sh/superset, stablyai/orca, standardagents/dmux, aidenybai/ghast, jarrodwatts/claude-hud, anthropics/claude-code, sst/opencode

**Core thesis**: "ECC 2.0 should be a harness operating system, not only a catalog of commands, agents, and skills."

**Suggested bring-up order**:
1. `ecc migrate audit --source ~/.hermes` — inventory legacy workspace
2. `ecc migrate plan` / `scaffold` — generate reviewable plans
3. `ecc migrate import-skills --output-dir migration-artifacts/skills`
4. Install ECC + verify baseline with `node tests/run-all.js`
5. Install Hermes + point at ECC-imported skills

### Dexto (truffle-ai/dexto) — 41pts Show HN

"A coding agent and general agent harness for building and orchestrating agentic applications." GitHub page is a standard landing page — no architecture details in the HTML fetch.

---

## Hermes Insights

1. **ECC ships Hermes integration as first-class citizen** — `HERMES-SETUP.md` is detailed, public, and maintained. ECC is the first external project to explicitly support Hermes as a primary operator surface. This validates the Hermes architecture decision (operator shell + reusable skills).

2. **Multi-harness ecosystem is real** — ECC's reference architecture explicitly models Claude Code, OpenCode, Cursor, Codex, Gemini, and Hermes as co-existing harnesses with different hook/plugin surfaces. This confirms Talos governance needs to handle harness heterogeneity, not assume a single canonical interface.

3. **Migration tooling = proof of concept for WS-035** — ECC's `ecc migrate audit` / `plan` / `scaffold` / `import-*` pipeline is exactly the kind of structured onboarding that heartbeat_learning.py drift penalty + memori integration should support. If ECC can migrate FROM Hermes, the reverse (memori → hermes-memori) should also be structured.

## Cross-Synthesis

ECC 2.0's "harness operating system" framing is directly relevant to Talos governance:
- Adapter compliance matrix (ECC tracks what each harness supports)
- Lifecycle hooks across harness matrix
- Session/worktree state exportable for external editors

## 未追蹤 Leads

- https://github.com/stanford-iris-lab/meta-harness — automated harness design search
- https://github.com/greyhaven-ai/autocontext — recursive harness improvement
- https://ecc.tools/ — ECC tools registry

## ✅ 本次探索完成