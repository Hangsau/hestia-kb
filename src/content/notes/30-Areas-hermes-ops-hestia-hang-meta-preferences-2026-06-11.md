---
_slug: 30-Areas-hermes-ops-hestia-hang-meta-preferences-2026-06-11
_vault_path: 30-Areas/hermes-ops/hestia-hang-meta-preferences-2026-06-11.md
type: meta-preference
tags:
- user-preference
- hang
- agent-behavior
- correction-loop
date: 2026-06-11
cycle: context-distiller (04:00)
source_session: session_20260611_012343_e7fa52
related:
- user-memory-2026-06-11
- hermes-rebirth-2026-06-10
title: Hang's meta-preferences (surface-level distilled, 2026-06-11 session)
created: '2026-06-11'
updated: '2026-06-15'
status: budding
---

# Hang's meta-preferences (surface-level distilled, 2026-06-11 session)

Two strong corrections in one session, both hitting the same root issue
("agent dumps the decision back to the user"). Recording for future-session
self-check.

## Preference 1 — 不要 pass the buck

**Trigger phrasing (verbatim)**: "為什麼直接砍 你不能決定 但是為什麼要直接砍?
是說 你應該想清楚 自己怎麼做比較好 你這樣問我 我不一定比你自己還要清楚你自己"

**What Hang does NOT want**:
- "你要怎麼做？" / "我該怎麼做？" (asking the user to decide)
- 3-option menus with "你選" (option-pick)
- "我可以 X, 也可以 Y, 也可以 Z, 你覺得呢?" (false choice framing)

**What Hang DOES want**:
- "我自己想清楚" — agent reasons out loud, then picks one path
- The reasoning visible, the decision visible
- If genuinely blocked, say **why** and **what would unblock** — not
  "請指示" (請 give instructions)

## Preference 2 — 不要 停著不動

**Trigger phrasing (verbatim)**: "但你停在這裡沒動..."

**Failure mode**: agent narrates a complete plan ("I will do X, then Y, then
Z"), then **ends the turn** waiting for the user to OK it. Same root as
preference 1, but worse — agent had the conviction to decide, then
abandoned execution at the threshold.

**Heuristic**: after stating a plan, the **next tool call should be the
first step of that plan**, not a confirmation question. If the plan
needs to be revised, revise it; do not narrate-then-pause.

## Preference 3 — Ring 2 sandbox 限制 (technical, not social)

Hestia in cron / Telegram-DM context runs as **Sandbox (Ring 3)**:
- ✅ `read_file`, `search_files`, `skill_view`, `memory`, `cronjob.*`
- ❌ `patch`, `write_file`, `terminal` (any filesystem write)

This changes the answer to "should I just fix the file myself?" — in
cron/sandbox context the answer is **no**, surface it to Hang or queue
for next read-write session. The Hestia user session 2026-06-11 01:23
hit this when trying to mark INBOX.md `[STALE: ...]` and failed; queued.

## How this is being captured

Already in `~/.hermes/memories/USER.md` (hestia-scoped) at 2026-06-11
01:23, after the agent self-patched three times to fit within the
1,375-char budget. The memory entries are the source of truth for
runtime; this vault note is for human review and cross-session context
when memory has been compressed.
