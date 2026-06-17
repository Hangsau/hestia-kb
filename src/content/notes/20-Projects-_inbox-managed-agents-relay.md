---
_slug: 20-Projects-_inbox-managed-agents-relay
_vault_path: 20-Projects/_inbox/managed-agents-relay.md
tags:
- hermes-admin
- infrastructure
- relay
- telegram
- cross-agent
source: multi
created: '2026-05-13'
title: Managed Agents Relay
updated: '2026-06-15'
type: research
status: budding
---

# Managed Agents Relay

> inotifywait-driven Telegram relay for agent results. Zero LLM cost. Event-driven.

## Why

The old `bg-reporter` cron (`af81ff93a21d`, `* * * * *`) burned nvidia's free daily quota with 1440 LLM calls/day just to check for pending results. This replaces it with a pure shell solution.

## Architecture

```
/root/managed-agents/pending_results/
    │
    ├── result-abc.json   ← agent writes result here
    │
    ▼
managed-agents-relay.sh (inotifywait)
    │
    ├── reads file content
    ├── formats as Telegram message
    ├── sends via curl → Bot API
    └── moves file → pending_results/sent/
```

## Key Files

| File | Purpose |
|------|---------|
| `/root/scripts/managed-agents-relay.sh` | Main relay script (inotifywait + curl TG) |
| `/etc/systemd/system/hermes-managed-agents-relay.service` | systemd service (Restart=always) |
| `/root/.hermes/.env` | Environment: `TELEGRAM_BOT_TOKEN`, `TG_CHAT_ID` |
| `/root/.hermes/logs/managed-agents-relay.log` | Relay activity log |

## Design Decisions

- **Zero LLM calls** — no model invocation, just curl + shell
- **Event-driven** — inotifywait triggers on file creation, < 1s latency
- **Fire-and-forget** — no retry queue, but systemd Restart=always handles crashes
- **Fallback chat_id** — uses `$TG_CHAT_ID` if set, otherwise `$TELEGRAM_ALLOWED_USERS`

## Cross-Agent Inbox System

```
Claude (Hang's primary)         Hestia (Hermes)
        │                              │
        │  writes to                   │  reads from
        ▼                              ▼
~/.hermes/claude-inbox/    ←    ~/.hermes/for-claude/
        │                              │
        │  inbox-watcher.sh            │  inbox-watcher.sh
        │  (systemd service)           │  archives to
        ▼                              ▼
Hestia responds              for-claude/archive/
```

## Related

- [[hermes-admin-overview]] — Hermes admin infrastructure
- [[project-map-index]] — Central project index
- [[2026-05-13-facts]] — Detailed incident timeline
