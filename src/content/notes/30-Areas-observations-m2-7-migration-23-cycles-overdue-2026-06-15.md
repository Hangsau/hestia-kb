---
_slug: 30-Areas-observations-m2-7-migration-23-cycles-overdue-2026-06-15
_vault_path: 30-Areas/observations/m2-7-migration-23-cycles-overdue-2026-06-15.md
_parse_error: "while parsing a flow sequence\n  in \"<unicode string>\", line 5, column\
  \ 24:\n    previous_observations: [auxiliary-compression-m2-7-stal ... \n      \
  \                     ^\nexpected ',' or ']', but got '<scalar>'\n  in \"<unicode\
  \ string>\", line 5, column 118:\n     ...  aux blocks, \"wait for handoff\" follow-up)]\n\
  \                                         ^"
_raw_fm: '

  date: 2026-06-15 12:13

  type: r7-escalation

  severity: critical

  previous_observations: [auxiliary-compression-m2-7-stale-2026-06-11.md (downstream,
  4 aux blocks, "wait for handoff" follow-up)]

  status: handoff never landed; 23 cycles deferred

  distilled_by: context-distiller v1.100

  tags: [m2-7, minimax, model-migration, r7-critical, config-yaml, deferred-action]

  title: M2.7 → M3 Migration — 23 Cycles Overdue, CRITICAL

  created: 2026-06-15

  updated: 2026-06-15

  '
title: M2.7 → M3 Migration — 23 Cycles Overdue, CRITICAL
type: area
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# M2.7 → M3 Migration — 23 Cycles Overdue, CRITICAL

## Status as of 12:00 Jun 15 2026

**R7 (M2.7 → M3 config.yaml fix) has been deferred 23 consecutive cycles** (v1.92 → v1.100, with N=23 tally). The migration is now **CRITICAL** (escalated from LOUD at v1.99).

## Audit results — 21 total M2.7 references across 4 config files

| File | M2.7 refs | Lines | Status |
|------|-----------|-------|--------|
| `~/.hermes/config.yaml` | 8 | 27, 34, 41, 48, 56, 63, 70, 85 | NOT migrated |
| `~/.hermes/profiles/psyche/config.yaml` | 8 | (auxiliary blocks, exact lines TBD) | NOT migrated |
| `~/.hermes/profiles/talos/config.yaml` | 1 | 229 (`default: MiniMax-M2.7`) | NOT migrated |
| `~/.claude/settings.json` | 4 | 5, 6, 7, 8 (ANTHROPIC_MODEL + 3 defaults) | NOT migrated |
| **TOTAL** | **21** | — | **ALL UNFIXED** |

All 21 references still point to `MiniMax-M2.7` at 12:00 Jun 15. None have been migrated to `MiniMax-M3`.

## Why this is critical (not just loud)

The Jun 11 hestia observation `auxiliary-compression-m2-7-stale-2026-06-11.md` said:

> Follow-up action: "Wait for Claude Code handoff result"

The "handoff" was the Jun 8 morning session where Talos installed Claude Code and wrote `~/.claude/settings.json` with `ANTHROPIC_MODEL` set. **The handoff was supposed to migrate the 4 M2.7 references in `~/.claude/settings.json` to M3, but it did not.** As of 12:00 Jun 15, those 4 references are still M2.7.

This means:
1. **Any Claude Code invocation that uses `ANTHROPIC_MODEL` env var will hit M2.7**, not M3.
2. **Any M3 call via the 4 auxiliary blocks in `~/.hermes/config.yaml` will fail-over to M2.7** (the only model listed in 8 blocks).
3. **The `talos` profile's default model is still M2.7** (`~/.hermes/profiles/talos/config.yaml:229`), so any new session that doesn't override the default gets M2.7.

**Net effect**: 23 cycles of M2.7 are still being served, with the user believing (or hoping) they're getting M3. This is a **silent data quality regression** — outputs are M2.7 quality, billed as M3 (or at minimum, the model metadata is incorrect).

## Why it wasn't done (the failure chain)

1. **v1.92** (Jun 14 20:00): First surfaced. "Persistent ≥ 7 cycles. Surface via non-distiller cron or Hang's next session." — Hang's next session didn't address it.

2. **v1.93–v1.98** (Jun 15 00:00–08:00): 6 more cycles, all deferred with the same rationale. N grew from 7 to 22.

3. **v1.99** (Jun 15 08:30): Review pass. Bumped N to 22. Noted ≥ 16 cycles persistent.

4. **Jun 8 morning session** (BEFORE the v1.92 surface): Talos installed Claude Code and wrote `~/.claude/settings.json`. The 4 M2.7 references were COPIED FROM `~/.hermes/config.yaml` (which had 8 M2.7 refs). Talos did not migrate them at install time.

5. **Jun 11 hestia observation**: Captured the 4-aux-block symptom but framed as "downstream of Jun 8 root cause". The "wait for handoff" was ambiguous — handoff could mean (a) the Claude Code install (which already happened, with 4 M2.7 refs added) or (b) a future migration session. The ambiguity let the issue sit.

6. **v1.100** (Jun 15 12:00): v1.100 cycle audited ALL 4 config files. Found 21 total M2.7 refs. The "handoff" was never a migration event — it was the install event that **added** 4 more M2.7 refs.

## Action required (cannot be done from [SILENT] cycle)

The migration is a 1-shot terminal session. Pseudo-code:

```bash
# ~/.hermes/config.yaml: 8 occurrences (sed inline)
sed -i 's/MiniMax-M2\.7/MiniMax-M3/g' /home/hangsau/.hermes/config.yaml

# ~/.hermes/profiles/psyche/config.yaml: 8 occurrences
sed -i 's/MiniMax-M2\.7/MiniMax-M3/g' /home/hangsau/.hermes/profiles/psyche/config.yaml

# ~/.hermes/profiles/talos/config.yaml: 1 occurrence (default line)
sed -i 's/MiniMax-M2\.7/MiniMax-M3/g' /home/hangsau/.hermes/profiles/talos/config.yaml

# ~/.claude/settings.json: 4 occurrences (JSON edit, not sed)
# Use python or jq — sed can break JSON
python3 -c "
import json
with open('/root/.claude/settings.json', 'r') as f:
    data = json.load(f)
# Replace in env section
if 'env' in data and 'ANTHROPIC_MODEL' in data['env']:
    data['env']['ANTHROPIC_MODEL'] = data['env']['ANTHROPIC_MODEL'].replace('MiniMax-M2.7', 'MiniMax-M3')
# Also check default model lists
for k in ['default_sonnet', 'default_opus', 'default_haiku']:
    if k in data and isinstance(data[k], str):
        data[k] = data[k].replace('MiniMax-M2.7', 'MiniMax-M3')
with open('/root/.claude/settings.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# Verify
grep -c "MiniMax-M2.7" /home/hangsau/.hermes/config.yaml /home/hangsau/.hermes/profiles/*/config.yaml /root/.claude/settings.json
# Expected: 0 across all files
```

After migration, restart any running Hermes sessions to pick up the new model.

## Why the distiller can't do this

- The distiller runs in [SILENT] mode (no user interaction, no terminal side effects beyond distiller's own files)
- Migration is a side effect on user config files (potentially destructive if syntax is wrong)
- Verification requires a working API call to confirm M3 is reachable
- All of this is out of scope for the distiller's role

The distiller's job is to **surface** the issue and **escalate** when it becomes critical. v1.100 has done both. The next step requires Hang or a non-[SILENT] cycle.

## Cross-references

- `auxiliary-compression-m2-7-stale-2026-06-11.md` — The Jun 11 observation that captured only the 4-aux-block subset. This observation is the v1.100 superset (21 total refs).
- `claude-code-vm-topology-2026-06-15.md` — Documents the 4 M2.7 refs in `~/.claude/settings.json` as part of the 2-tier agent topology. The migration must include the settings.json file, not just the Hermes config.yaml files.
- `talos-hallucinated-commit-cce1987-2026-06-15.md` — The Jun 8 hallucination happened in a `claude -p` background task. The M2.7 model in `ANTHROPIC_MODEL` may have contributed to the hallucination (M2.7 is known to have weaker code-verification than M3). The migration may also reduce future hallucination rate.
- `opencode-deprecation.md` — The Jun 9 deprecation of opencode was the first step in the Claude Code migration. The M2.7→M3 migration is the second step that's been deferred.

## Distiller notes

- This is the v1.100 cycle's primary R7 escalation. R7 has been silent for 22 cycles; v1.100 promotes it to CRITICAL with a full audit + action plan.
- The distiller will continue to count N (currently 23) in every future cycle until the migration lands.
- If a non-[SILENT] cycle is triggered in the next 7 days, this observation is the recommended first action.
