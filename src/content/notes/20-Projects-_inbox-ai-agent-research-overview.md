---
_slug: 20-Projects-_inbox-ai-agent-research-overview
_vault_path: 20-Projects/_inbox/ai-agent-research-overview.md
date: 2026-05-12
tags:
- research
- ai-agent
- daily
- reports
- logs
project_path: ~/ai-agent-research/
title: AI Agent Research Log
created: '2026-05-13'
updated: '2026-06-15'
type: research
status: budding
---

# AI Agent Research Log

> Daily autonomous research on AI Agent / MCP / Multi-Agent technologies.

## Structure

```
ai-agent-research/
├── reports/    # Daily research reports (YYYY-MM-DD-{topic}.md)
├── drafts/     # Experimental ideas, project concepts
├── skills/     # Skill drafts (eventually move to ~/.hermes/skills/)
└── assets/     # Charts, screenshots, clips
```

## Scope (IN)

- LLM agent architecture (planning, memory, tool use)
- Multi-agent systems (swarm, orchestration)
- MCP (Model Context Protocol)
- Agent evaluation benchmarks
- Novel agent construction patterns

## Scope (OUT)

- General LLM research (not agent-specific)
- Product comparisons ("A has X, B lacks Y")
- Unrelated topics

## Research Quality Bar

- Rejects feature-comparison tables as meaningless
- Must answer the actual question, produce new knowledge
- Must go beyond cataloging differences between unrelated systems

## Automation

Daily cronjob at 8 AM (`daily-ai-research`) and 11 PM (`daily-ai-agent-research`) dispatch the research pipeline.

## See Also

- [[project-map-index]] — Central index of all active projects
