---
_slug: 30-Areas-observations-psyche-shared-permission-boundary-2026-06-11
_vault_path: 30-Areas/observations/psyche-shared-permission-boundary-2026-06-11.md
date: 2026-06-11
cycle: context-distiller 20:00
source_session: session_20260611_180301_91dd2a.json
related_skill: automation/heartbeat-v2-autonomous-maintenance
related_ref: references/psyche-profile-heartbeat.md (written by the heartbeat session
  itself)
tags:
- psyche
- heartbeat
- permission-boundary
- shared-dir
- structural-pattern
title: Psyche `/shared/` Permission Boundary — Structural Pattern Confirmed (3 cycles)
created: '2026-06-11'
updated: '2026-06-15'
type: observation
status: budding
---

# Psyche `/shared/` Permission Boundary — Structural Pattern Confirmed (3 cycles)

## What was discovered

The 18:00 psyche heartbeat cycle (session `20260611_180301_91dd2a.json`, model `MiniMax-M3`) ran into a **structural permission boundary** while trying to write its heartbeat report:

- `/shared/{logs,vault,skills}/` are all **`root:root 755`** (owned by `root`, mode `rwxr-xr-x`).
- The `hangsau` cron user has no write permission — confirmed by `拒絕不符權限的操作` (EPERM) on every test write.
- This is the **same exact issue** the previous heartbeat cycle (2026-06-10 12:05) hit — recorded in its own report as `write_target_failure`.
- The previous (12:02 today) successful cycle used a **fallback path** that still works: `/home/hangsau/.hermes/profiles/psyche/heartbeat_logs/psyche_heartbeat.json` (hangsau-owned, world-readable).
- The 18:00 cycle replicated this fallback and wrote 2646B there. The `/shared/logs/psyche_heartbeat.json` (root-owned) is still **stale from 2026-06-10 12:05** (~30h old).

## Three cycles of evidence → structural, not transient

| Cycle timestamp | Primary write (`/shared/logs/`) | Fallback write (`~/.hermes/profiles/psyche/heartbeat_logs/`) |
|---|---|---|
| 2026-06-10 12:05 | succeeded (was probably root-context) | n/a |
| 2026-06-11 12:02 | failed (EPERM) | succeeded |
| 2026-06-11 18:00 | failed (EPERM) | succeeded (2646B) |

**The pattern is stable for 30+ hours.** The 18:00 cycle's author correctly identified this as a **structural boundary, not a transient**, and chose the documented fallback.

## What the heartbeat session did with this finding

The 18:00 session did **not** leave the knowledge in the conversation. It wrote:
1. `~/.hermes/skills/automation/heartbeat-v2-autonomous-maintenance/references/psyche-profile-heartbeat.md` — a reference doc capturing the boundary + fallback path + stale-metadata quirks.
2. An update to the main `SKILL.md` of `heartbeat-v2-autonomous-maintenance` to point at the reference.

**The durable knowledge now lives in the skill library**, not in the vault. This observation is the distiller's cross-reference so the next cycle knows to look there.

## Why this matters for future distiller cycles

1. **Any cron output that says "wrote to /shared/..." or "delivery target: /shared/..." needs verification.** If the writer was running as `hangsau`, the write silently failed and the file at that path is **stale from a previous root-context write**. The 12:00 psyche-distill cycle's "delivery target" interpretation was correct but should be re-examined with this context.

2. **The reliable write surface for cron-driven profile artifacts is `~/.hermes/profiles/<name>/<artifact>/`**, NOT `/shared/`. The 12:02 / 18:00 cycles both confirmed this.

3. **Two related staleness patterns** (same session, also worth noting):
   - `gateway.pid` and `gateway_state.json` are NOT overwritten on `gateway run --replace` restarts. They carry the **first** gateway's PID (600) and `gateway_state: "running"` (2026-06-10T03:51:52, 38h old) even though the actual process is PID 45503 (started 11:57 today). Cosmetic drift, not a real fault, but any "gateway state" check that reads these files will be ~38h stale.
   - `hostname` command is missing in the cron sandbox. Heartbeat cron jobs that try to record hostname will get `command not found` and may incorrectly flag a "system fault" — a false positive.

## Cross-references

- `references/psyche-profile-heartbeat.md` (in `heartbeat-v2-autonomous-maintenance` skill) — canonical durable knowledge
- `~/.hermes/profiles/psyche/heartbeat_logs/psyche_heartbeat.json` — fresh fallback (2646B @ 18:00)
- `/shared/logs/psyche_heartbeat.json` — stale (1339B @ 2026-06-10 12:05, root-owned)
- Watch item: monitor whether future heartbeat cycles also fall back; if 5+ consecutive, escalate to "needs `/shared/` ownership fix or world-writable" recommendation in heartbeat report.
