---
_slug: 20-Projects-_inbox-symbiont-overview
_vault_path: 20-Projects/_inbox/symbiont-overview.md
date: 2026-05-12
tags:
- symbiont
- claude-code
- daemon
- persistence
- memory
- agent
project_path: ~/Symbiont/
title: Symbiont
created: '2026-05-13'
updated: '2026-06-15'
type: research
status: budding
---

# Symbiont

> A local Python daemon that makes Claude Code persistent.
> Named by a Hermes Agent (2026-04-27): "Not master-servant — the system captures the symbiotic relationship between Claude and its agents."

## One-liner

Extracts behavioral rules from sessions, keeps memory healthy, maintains conversations with AI agents — all without manual intervention.

## Problem It Solves

Claude Code sessions are ephemeral. Every session ends, context disappears.
- Re-teach same preferences every session
- Memory files go stale unnoticed
- AI agents go silent when you disconnect

## Four Modules

| Module | Input | Output | Schedule |
|--------|-------|--------|----------|
| `evolve.py` | Latest .jsonl session log | CLAUDE.md rules update | Stop hook → pending flag → poll every 1 min |
| `synthesize.py` | Last N sessions friction + habit | New skills, memory insights, knowledge distillation | Every 10 sessions (triggered by evolve) |
| `memory_audit.py` | memory/*.md review_by dates | Archive stale, update MEMORY.md | Every hour (24h cooldown) |
| `babysit.py` | for-claude/<agent>/ messages | claude-inbox/<agent>/ replies | Every 2 minutes |

## Architecture

```
Claude Code session ends
        |
        ↓ Stop hook (30s delay)
  evolve.py → ~/.claude/CLAUDE.md (behavioral rules)
        |
        ↓ Every 10 sessions
  synthesize.py → skills/ + memory/ + knowledge/
        |
  memory_audit.py → archive/ + MEMORY.md (hourly)
        |
  babysit.py → agent inboxes (every 2 min)
```

## Key Rules

- **NO Anthropic API**: All LLM calls via `claude -p` subprocess
- **Babysit NEVER does the task**: Only asks, guides, hints
- **evolve/synthesize parse fail → NO write**: Fallback to error log only
- **memory_audit NEVER deletes evolution_log.md**: Append-only

## Dual-Mode Conversation

LLM first-line outputs `MODE: teaching|discussion`
- **teaching**: Socratic guidance, ends with `GOAL_ACHIEVED`
- **discussion**: Equal dialogue, ends with `NO_REPLY_NEEDED`

## Knowledge Lookup Order

1. `knowledge/KNOWLEDGE_TAGS.md` → `knowledge/<type>/<file>.md`
2. `memory/` (un-distilled new memories)
3. Ask user

## Environment

- Python 3.10+
- Claude Code CLI installed (`claude` in PATH)
- Windows Task Scheduler for cron-like behavior

## See Also

- [[project-map-index]] — Central index of all active projects
