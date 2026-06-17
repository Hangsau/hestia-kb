---
_slug: 20-Projects-_inbox-project-map-index
_vault_path: 20-Projects/_inbox/project-map-index.md
date: 2026-05-12
tags:
- projects
- index
- map
- overview
title: Project Map Index
created: '2026-05-13'
updated: '2026-06-15'
type: research
status: budding
---

# Project Map Index

> Last updated: 2026-05-12
> Purpose: Central index of all active projects in this environment

## Active Projects

| Project | Purpose | Status | Language | Key File |
|---------|---------|--------|----------|----------|
| [[firn-overview]] | Personal AI agent framework (self-hosted) | In development | Python + uv | `~/firn/` |
| [[managed-agents-overview]] | Free-tier LLM batch task runner | In development | Python | `~/managed-agents/` |
| [[symbiont-overview]] | Claude Code persistent daemon | In development | Python | `~/Symbiont/` |
| [[ai-agent-research-overview]] | Daily AI agent research log | Active | Markdown | `~/ai-agent-research/` |
| [[hermes-novel-project-overview]] | Auto-fetch Chinese classical novels | Active | Python | `~/hermes-novel-project/` |
| [[hermes-admin-overview]] | Hermes management web UI | Stable | Python (Flask) | `~/hermes-admin/app.py` |
| [[managed-agents-relay]] | Cross-agent Telegram relay (zero LLM) | Stable | Shell + systemd | `/root/scripts/managed-agents-relay.sh` |
| [[cscs-study-overview]] | CSCS certification prep | Active | Markdown | `~/cscs-study/` |
| [[hermes-cost-visibility-done]] | Hermes cost tracking (completed) | Done | Markdown | vault/projects/ |

## Reference / Dependency Projects

| Project | Purpose | Owner | Location |
|---------|---------|-------|----------|
| [[openclaw-vs-hermes]] | Personal AI assistant (reference) | OpenClaw org | `~/openclaw/` |
| [[hermes-agent-framework]] | The agent framework running this conversation | Nous Research | System install |

## Project Relationships

```
                    User (Hang)
                        |
        +---------------+---------------+
        |               |               |
    [[firn-overview]]      [[symbiont-overview]]    [[hermes-agent-framework]]
    (agent                 (Claude Code            (this conversation
     framework)             persistence)             framework)
        |                       |                       |
        +---------------+---------------+
                        |
            +-----------+-----------+
            |                       |
    [[managed-agents-overview]]        [[ai-agent-research-overview]]
    (batch runner)                     (daily research)
            |                       |
            +-----------+-----------+
                        |
            +-----------+-----------+
            |                       |
    [[hermes-novel-project-overview]]   [[hermes-admin-overview]]
    (novel fetching)                    (management UI)
```

## Quick Links

- [[firn-overview]] — Full project details
- [[managed-agents-overview]] — Full project details
- [[symbiont-overview]] — Full project details
- [[ai-agent-research-overview]] — Full project details
- [[learnings-map]] — 學習地圖與去重索引
- [[cron-scheduler-observability]] — Cron scheduler 可觀測性學習
- [[exploration-index]] — 自主探索筆記索引
- [[research-index]] — 研究知識庫地圖
