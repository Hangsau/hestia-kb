---
_slug: 20-Projects-_inbox-firn-overview
_vault_path: 20-Projects/_inbox/firn-overview.md
date: 2026-05-12
tags:
- firn
- agent-framework
- python
- uv
- open-source
project_path: ~/firn/
repo: github.com/your-username/firn
title: Firn
created: '2026-05-13'
updated: '2026-06-15'
type: research
status: budding
---

# Firn

> Personal AI agent framework you can self-host. Python + uv. Open-source.

## One-liner

Firn gives you a persistent agent with long-term memory, background tasks, scheduled jobs, and a Telegram interface — all backed by a local SQLite database.

## Architecture

```
src/firn/
├── cli/           # Click CLI 入口（I0）
├── context/       # ContextBuilder（I2）
├── memory/        # 記憶系統：blocks、messages、embedding、search（I1）
├── agents/        # ConversationAgent、TaskAgent、CronAgent（I2-I7）
├── gateway/       # Gateway ABC、CLIGateway、TelegramGateway（I2-I3）
├── skills/        # Skill loader、SkillService（I4）
├── tasks/         # TaskService、Watchdog、Dispatcher、Scheduler（I5-I7）
├── llm/           # LLMClient、CircuitBreaker（I2、I8）
├── observability/ # TurnsLogger（I8）
├── tools/         # ToolExecutor、ToolRegistry、schemas（I2-I5）
└── db.py          # schema + migration（I0）
```

## Key Decisions (from CLAUDE.md)

- **Python 3.12+ + uv** (ADR-12)
- **Anthropic API** primary; OpenAI / Ollama supported
- **Memory**: structured blocks (persona, user facts, context, notes) + full-text search
- **Tasks**: background agents + dispatcher claims + auto-run
- **Gateway**: Telegram + CLI

## Iterations (I0-I22 from ROADMAP)

| Iteration | Focus | Status |
|-----------|-------|--------|
| I0 | CLI + DB schema | Done |
| I1 | Memory system | Done |
| I2 | Context + Gateway | Done |
| I3 | Telegram gateway | Done |
| I4 | Skills | Done |
| I5 | Tasks + Watchdog | Done |
| I6 | Dispatcher | Done |
| I7 | Cron + Scheduler | Done |
| I8 | LLMClient + CircuitBreaker + Observability | Done |
| I9-I22 | (see ROADMAP) | In progress |

## Model Routing Rules

| Task Type | Model | Why |
|-----------|-------|-----|
| plan-check | Opus | Planning needs full reasoning |
| implement (list) | Opus | Must be complete with inline line numbers |
| Write code | Sonnet (via agent) | Execution tasks |
| code-audit | Sonnet | Code review |

## Research Dependencies

All design decisions have documented sources:
- `~/research/agent-research/research/17_requirements.md` — M1-M10 requirements
- `~/research/agent-research/research/18_adr.md` — ADR-01–ADR-12
- `~/research/agent-research/research/23_architecture_v2.md` — v2 architecture
- `~/research/agent-research/research/24_iteration_plan.md` — Iteration specs
- `~/research/agent-research/research/25_repo_reference_guide.md` — Six-repo reference

## Commands

```bash
uv sync              # Install deps
uv run pytest        # Tests
uv run firn <cmd>    # CLI
firn init            # Setup wizard
firn status          # Verify
firn chat            # Start chatting
```

## Competitors

- **OpenClaw** — TypeScript, npm-based, more channels
- **Hermes Agent** — This system (Nous Research)
- Firn positions as Python alternative with SQLite persistence

## See Also

- [[project-map-index]] — Central index of all active projects
