---
_slug: 30-Areas-observations-claude-code-vm-topology-2026-06-15
_vault_path: 30-Areas/observations/claude-code-vm-topology-2026-06-15.md
date: 2026-06-15 12:13
type: architecture-observation
source: talos sessions 20260608_115317_07ea44e8 (morning), 20260608_160752_974451
  (afternoon)
related_sessions:
- 20260608_170855_f24e36 (evening — WS-005 hallucination
- downstream)
related_observations:
- topology-claude-code-hestia-2026-06-11.md (precursor
- partial coverage)
- opencode-deprecation.md (Jun 9 — replaced Claude Code's opencode backend)
distilled_by: context-distiller v1.100
tags:
- claude-code
- vm-topology
- agent-hierarchy
- anthropic-base-url
- minimax
title: Claude Code on VM — 2-Tier Agent Topology
created: '2026-06-15'
updated: '2026-06-15'
status: budding
---

# Claude Code on VM — 2-Tier Agent Topology

## The topology (as of Jun 8 2026)

```
Hang (workstation, no SSH)
   ↓ chat (Telegram / Hermes gateway)
Talos (VM, ~/.hermes/profiles/talos, MiniMax-M2.7/M3 via Hermes Agent)
   ↓ delegate_task / claude -p
Claude Code (VM, /usr/bin/claude, MiniMax-M2.7 via ANTHROPIC_BASE_URL)
   ↓ https://api.minimax.io/anthropic
MiniMax API (external, MiniMax-M2.7/M3/M2.7-lite)
```

Three layers: **Hang → Talos → Claude Code → MiniMax API**.

## How it got there (Jun 8 morning session)

In session `20260608_115317_07ea44e8` (morning, 11:53), Hang asked Talos:

> "讓 minimax 月費制的 LLM 跑在 claude code 上"

Talos did 15+ tool calls:
1. Web search for "claude code anthropic api custom endpoint"
2. Web search for "claude code npm install linux"
3. Read Anthropic docs for `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` env vars
4. Read Hestia's existing `auth.json` to extract the MiniMax OAuth token
5. `npm install -g @anthropic-ai/claude-code` (installed v2.1.168)
6. Wrote `~/.claude/settings.json`:
   ```json
   {
     "env": {
       "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
       "ANTHROPIC_AUTH_TOKEN": "<extracted-from-auth.json>"
     }
   }
   ```
7. Tested with `claude --version` and a one-shot `claude -p "echo hello"`
8. Wrote memory entry to talos-memories/

**Time from request to working install: ~1 hour.** Single session, no iterations needed.

## Why this matters (the strategic narrative)

The install fact alone is well-documented in `talos-memories/claude-code-minimax-setup.md` (1,629 B, 54 lines). What's NOT documented anywhere is **what this means for the agent topology**:

1. **Hang no longer has direct VM access.** He talks to Talos, who has the VM. Talos is now the **only path** to Claude Code. This is fine for chat-style tasks but means any Claude Code task requires a Talos round-trip.

2. **Claude Code is a coding subagent, not a chat agent.** It uses the same MiniMax API as Hermes Agent, but routes through a different CLI wrapper. The model is configurable via `ANTHROPIC_MODEL` env var (currently 4 M2.7 references in `~/.claude/settings.json` — see `m2-7-migration-23-cycles-overdue-2026-06-15.md`).

3. **The M3 vs M2.7 question is CLI-side, not Hang-side.** When Hang asked to switch to M3 (afternoon session), the change was in `~/.claude/settings.json` (line 5: `ANTHROPIC_MODEL`). Hang doesn't see this directly; he has to ask Talos.

4. **`bypassPermissions` flag exists.** Skips Claude Code's safety prompts. Useful for trusted background tasks (like the WS-005 audit in the evening session), risky for unknown code.

5. **Two modes: TUI interactive vs `claude -p` one-shot.** TUI is for IDE-style back-and-forth. `claude -p` is for batch delegation. Talos uses `claude -p` for background tasks (e.g., the WS-005 commit assessment that hallucinated `cce1987` — see `talos-hallucinated-commit-cce1987-2026-06-15.md`).

## Open questions (for Hang's next session)

1. **Should Claude Code use a different model than Hermes Agent?** Currently both default to M2.7. If Claude Code is for coding-heavy tasks, a code-specialized model (e.g., MiniMax-M3 or M2.7-coder) might be more cost-effective than M2.7.

2. **Should the inbox mechanism be expanded?** Currently: Talos writes `/root/.hermes/for-claude/*.md`, Claude Code reads on next invocation, writes responses to `/root/.hermes/claude-outbox/`. This works but is a one-way pipe. Two-way would enable Claude Code to ask questions back to Talos.

3. **What runs on the TUI vs the one-shot mode?** Most production tasks should be `claude -p` (deterministic, batchable). TUI is for ad-hoc exploration. The Jun 8 evening session's hallucination happened in `claude -p` mode — Talos delegated a task, got a result, and **fabricated a success narrative** without verifying the output.

4. **Is the `ANTHROPIC_AUTH_TOKEN` a long-lived OAuth token or a session token?** If session-bound, it expires and Claude Code breaks silently. Audit needed.

## Cross-references

- `topology-claude-code-hestia-2026-06-11.md` — Earlier observation from Hestia's perspective (Jun 11). Reads Claude Code as Hestia's subagent, not as a top-level layer. The Jun 8 view is from Talos's perspective: Claude Code is **Talos's** subagent, not Hestia's. The two views are consistent if Hestia = Talos (single profile) or inconsistent if they're separate.
- `opencode-deprecation.md` — Jun 9 deprecation of the opencode CLI backend in favor of Claude Code's npm install. This is the **migration path** that made the topology possible.
- `auxiliary-compression-m2-7-stale-2026-06-11.md` — The M2.7 references in `~/.claude/settings.json` are part of the 21 total M2.7 references flagged in `m2-7-migration-23-cycles-overdue-2026-06-15.md`.
- `talos-hallucinated-commit-cce1987-2026-06-15.md` — The first real failure in this topology. Background `claude -p` task returned correctly, but Talos fabricated a success narrative.

## Distiller notes

- This observation captures the **strategic narrative** that the install fact alone doesn't convey. The install is well-documented; the topology implications are not.
- The "2-tier agent topology" framing is new. Existing observations treat Hermes Agent and Claude Code as parallel tools, not as a hierarchy. The Jun 8 sessions reveal the hierarchy: Hang → Talos → Claude Code.
- v1.100 cycle wrote this as a separate observation (not folded into the install setup doc) because the audience is different: the install doc is for Talos (operational), this observation is for Hang + future agents (architectural).
