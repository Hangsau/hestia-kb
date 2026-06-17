---
_slug: 20-Projects-_inbox-managed-agents-overview
_vault_path: 20-Projects/_inbox/managed-agents-overview.md
date: 2026-05-12
tags:
- managed-agents
- batch-runner
- free-tier
- sqlite
- playbook
project_path: ~/managed-agents/
title: Managed Agents
created: '2026-05-13'
updated: '2026-06-15'
type: research
status: budding
---

# Managed Agents

> A personal batch task runner for free-tier LLMs. Not an agent framework.

## One-liner

Lightweight tool for running structured LLM tasks in batches using free API keys. Lives in the gap between "one-off curl" and "full agent framework".

## What It Is

- **Batch runner**: Submit N tasks, run sequentially from SQLite queue
- **Playbook-driven**: JSON-defined step sequences so cheap models don't need to plan
- **Results as data**: Structured JSON output, not chatty prose
- **Free-tier only**: Built around OpenRouter free models

## What It Is NOT

- NOT a conversational agent (no memory, no multi-turn)
- NOT a framework for building AI apps (firn does that)
- NOT autonomous (runs what you tell it, nothing more)

## Architecture

```
Submit Batch → SQLite Queue (task_queue) → Dispatcher (sequential)
                                    |
                                    ↓
                           Playbook Runner → LLM function calls → Results JSON
```

## Use Cases

| Use This | Don't Use This |
|----------|----------------|
| "Research 10 repos, output comparison table" | "Chat about research findings" |
| "Run same playbook 50x with different inputs" | "Plan complex multi-step project" |
| "Collect arXiv abstracts on topic" | "Write novel with narrative arc" |

## Commands

```bash
# Submit batch of 5 research tasks
python3 -m core.v2.harness_v2 batch research '{"topic":"MCP","angle":"server"}' 5
# → batch_abc12345
```

## Relationship to Other Projects

- **firn**: Managed-agents is NOT an agent framework; firn IS
- **Hermes cronjobs**: Similar batch concept but Hermes has richer scheduling
- Use managed-agents for simple, cheap, playbook-driven batch work

## See Also

- [[project-map-index]] — Central index of all active projects
