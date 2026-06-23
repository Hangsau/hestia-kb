---
_slug: 30-Areas-observations-cross-check-hestia-silent-failure-2026-06-11
_vault_path: 30-Areas/observations/cross-check-hestia-silent-failure-2026-06-11.md
type: observation
tags:
- cron
- silent-failure
- hermes-ops
- hestia
date: 2026-06-11
cycle: context-distiller (04:00)
source_session: session_20260611_012343_e7fa52
related:
- silent-failure-class-2026-06-08
- hc-22-architecture
title: '`cross-check-hestia` cron — third silent-failure instance of the same class'
created: '2026-06-11'
updated: '2026-06-15'
status: budding
---

# `cross-check-hestia` cron — third silent-failure instance of the same class

## What happened

Cron job `b4bf57d18c03` (`cross-check-hestia`, schedule `0 1 * * *`) returned
`last_status: ok` every day for an unknown period while the underlying script
`/home/hangsau/.hermes/scripts/cross-check-hestia.sh` **did not exist on disk**.

Root cause: the cron was designed to mirror Talos's `cross-check-talos.sh`
(staggered schedule 30 1 \* \* \* for Talos → 0 1 \* \* \* for Hestia), but
the Hestia-side script was **never written** — it predates the 2026-06-10
reincarnation archive too (no `cross-check-*` in `archive/2026-06-10-hermes-rebirth/`).

This is the **third** confirmed silent-failure instance of the same class
(see also `hc-21`, `hc-22` in `~/.hermes/INBOX.md`):
- gateway records `last_status: ok`
- the actual run failed (script missing / skill missing / etc.)
- humans only learn about it when an external trigger surfaces the error

## Resolution applied

- `cronjob.update` to set `enabled: false` + `state: paused`
- `name` rewritten to `cross-check-hestia [DISABLED — hestia-side script never created; see INBOX hc-22 architecture; reincarnation 2026-06-10]`
- `prompt` rewritten to disable-annotation text

## Outstanding questions (not addressed in-session)

1. **Should `cross-check-hestia` be reimplemented, or is the symmetric
   cross-check design itself flawed?** Echoing the same failure back and
   forth between two agents is negative value. Talos 暫停 (see
   `topology-claude-code-hestia-2026-06-11.md`) means there's no receiver
   for the check even if it ran.
2. **The silent-failure problem is structural at the gateway level**, not
   per-cron. A watchdog that cross-checks `last_status` against a known
   post-condition (script exists, output file mtime within N hours) is
   needed. `cron-audit-watchdog.sh` exists in `~/.hermes/scripts/` but
   is unconfirmed whether it covers this class.
