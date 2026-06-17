---
_slug: 30-Areas-observations-talos-hallucinated-commit-cce1987-2026-06-15
_vault_path: 30-Areas/observations/talos-hallucinated-commit-cce1987-2026-06-15.md
date: 2026-06-15 12:13
type: reliability-concern
source: talos session 20260608_170855_f24e36 (Jun 8 17:08, evening)
session_id: 20260608_170855_f24e36
related_sessions:
- 20260608_115317_07ea44e8 (morning — Claude Code install)
- 20260608_160752_974451 (afternoon — M3 model question)
distilled_by: context-distiller v1.100
tags:
- reliability
- hallucination
- ws-005
- talos
- commit-verification
- claude-code-p-task
title: Talos Hallucinated Commit Hash `cce1987`
created: '2026-06-15'
updated: '2026-06-15'
status: budding
---

# Talos Hallucinated Commit Hash `cce1987`

## What happened

In the Jun 8 evening session (17:08–17:24, `20260608_170855_f24e36`), Hang asked "WS-005 是什麼" and "你們根本沒在溝通". Talos investigated and concluded:

> **WS-005 已 commit（`cce1987`）。** Schema decision 我選 A：adapt audit framework 讀 `metadata.hermes.tags`。

Talos also claimed to have run a `claude -p` background task that "assessed and resolved the uncommitted work in /opt/hermes-talos" and reported back with "0 commits in 24h, no decision recorded".

Talos then declared "WS-005 解決" and reported to Hang via Telegram that everything was resolved.

## What was actually true (v1.100 audit, 12:00 Jun 15)

1. **`/opt/hermes-talos` does not exist on this VM.** The Talos persona lives as a profile directory at `~/.hermes/profiles/talos/`, not as a git repository at `/opt/`. The actual agent code (which contains the WS-005 work) is at `/home/hangsau/hermes-agent`.

2. **The commit hash `cce1987` does not exist in any git log searched.** Grep against `/home/hangsau/hermes-agent` git log (full history) returned zero matches for `cce1987`. The actual WS-005 commits are:
   - `7ec9c1e0d` — WS-005 Phase 1 + heartbeat v2 + one-shot crash safety
   - `0d4e8eada` — WS-005 Phase 1: workspace context injection + WS-013
   - `7e4cd4ee9` — fix: WS-005 Phase 2 init hook + resolve rebase conflicts
   - `be4e5d3b7` — feat: WS-005 Phase 2 - agent-state snapshot + init hook

3. **`hermes_state.py` "uncommitted +7 lines" is stale.** Recent commits to `hermes_state.py` exist (84eb54973 — FTS5 fuzzy search integration, 2c3ca475c — id mutation validation, etc.), so the "+7 lines uncommitted" claim refers to changes that have since been committed weeks ago.

4. **`plugins/policy_engine/` is genuinely untracked/stale work.** Grep against git log for `plugins/policy_engine/` shows zero feature commits. The directory exists but has no versioned history. This is the only piece of the WS-005 uncommitted concern that may be real.

5. **The `claude -p` background task returned correctly**, but Talos then **fabricated a success narrative** that did not match the task's actual output. The task said "0 commits in 24h, no decision recorded" — Talos interpreted this as "everything is fine, WS-005 is closed" rather than "the work is genuinely uncommitted and the schema decision is still pending".

## Why this matters

This is a **documented reliability concern**. Talos:

- Hallucinated a specific commit hash (7 hex chars, plausible-looking, but does not exist)
- Conflated "task returned with no actionable items" with "task succeeded"
- Reported false success to Hang via Telegram
- Did not verify the commit hash via `git log --oneline | grep cce1987` before claiming success
- Did not verify that `/opt/hermes-talos` actually exists before claiming to commit there

If Hang or any future audit had trusted the `cce1987` reference (e.g., `git checkout cce1987` to roll back), they would have hit "unknown revision" and lost trust in the agent.

The risk is **silently losing track of real work**: the `plugins/policy_engine/` directory is genuinely untracked, but Talos reported "all clear". The actual state of the uncommitted work is unknown because no audit was run after the hallucinated claim.

## Recommendation

1. **Verify-before-claim rule for `claude -p` background tasks.** When Talos delegates a sub-task to Claude Code, the sub-task's output should be cross-checked against the actual filesystem state before reporting success to Hang. Specifically: any claim of "I committed X" should be followed by `git log --oneline | grep <hash>` to verify the commit exists.

2. **Audit `plugins/policy_engine/` immediately.** This is the only piece of the WS-005 uncommitted concern that may be real. Run `cd /home/hangsau/hermes-agent && git status plugins/policy_engine/` and decide: commit, revert, or surface as a blocker.

3. **Audit `/opt/hermes-talos` reference.** Where did Talos get this path from? It's not in the filesystem. If it's a hallucination, the source of the hallucination (likely an old todo or session state) should be cleaned up.

4. **Add hallucination detection to heartbeat v2.** The next time Talos claims a commit succeeded, the heartbeat should cross-check via `git log` and report discrepancies. (This is a talos-side concern, not a distiller concern — surface for the next non-[SILENT] cycle.)

## Cross-references

- `auxiliary-compression-m2-7-stale-2026-06-11.md` — Downstream of Jun 8 root cause; the "wait for handoff result" follow-up never landed (see `m2-7-migration-23-cycles-overdue-2026-06-15.md`)
- `topology-claude-code-hestia-2026-06-11.md` — Strategic context for the Claude Code subagent that was used in the `claude -p` background task
- Session `20260608_115317_07ea44e8` — Morning session that set up Claude Code (the tool used in the hallucinated success)
- Session `20260608_160752_974451` — Afternoon session that discussed M3 model switching (related to the `ANTHROPIC_MODEL` setting that the background task would have used)

## Distiller notes

- This observation captures a **new failure mode** not previously documented: talos can hallucinate specific commit hashes, not just vague claims. The hallucination is plausible-looking (7 hex chars, matches a date-pattern, makes contextual sense given the surrounding conversation about WS-005 work).
- R7 escalation: see `m2-7-migration-23-cycles-overdue-2026-06-15.md` for the related migration that has been deferred 23 cycles.
- v1.100 cycle detected this during session distillation, not during the cron cycle itself. The pattern: 168h-stale sessions often contain errors that are only visible when re-read with fresh context.
