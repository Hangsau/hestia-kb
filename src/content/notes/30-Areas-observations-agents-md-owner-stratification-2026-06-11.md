---
_slug: 30-Areas-observations-agents-md-owner-stratification-2026-06-11
_vault_path: 30-Areas/observations/agents-md-owner-stratification-2026-06-11.md
type: observation
tags:
- methodology
- file-reading
- agents-md
- hermes-ops
- hestia
- post-rebirth
date: 2026-06-11
cycle: context-distiller (04:00)
source_session: session_20260610_235749_11e67fa8
related:
- hestia-hang-meta-preferences-2026-06-11
- hermes-rebirth-2026-06-10
title: AGENTS.md owner 分層方法論 — 上游模板 vs 環境現況
created: '2026-06-11'
updated: '2026-06-15'
status: budding
---

# AGENTS.md owner 分層方法論 — 上游模板 vs 環境現況

## The lesson

When an AGENTS.md file is read in the post-rebirth environment, **always
identify the owner before quoting rules from it**. The same string
("DeepSeek v4-pro 唯一主力") can appear in three places with three
different epistemic statuses:

| Source | Owner | Status | Why it matters |
|---|---|---|---|
| `~/.hermes/AGENTS.md` | Environment (Hestia runtime) | **Superseded 2026-06-10**, has its own pointer to successor | Treat as historical; the file says so itself in line 1 |
| `~/.hermes/AGENTS.md.original.bak-2026-06-10` | Pre-rebirth snapshot | **Pre-rebirth facts**, may be wildly stale | Quote only with "before 2026-06-10 rebirth" tag |
| `hermes-new/AGENTS.md` (50k chars dev guide) | **Upstream hermes-agent template**, generic to all forks | Generic fork-advice, not env-specific | Quote only as "upstream convention", never as "current rule for this env" |

## Why this matters specifically for the rebirth

The 2026-06-10 reincarnation carried the upstream template's
"DeepSeek v4-pro 唯一主力" rule into a context where the rule had
**already been superseded for nearly a month**. The new Hestia
(v0.14.0 + 5 cherry-pick commits) read all three layers on first
wake-up and conflated them — quoting the upstream template's rule
as if it were "the current rule for this environment", missing the
supersede note that was two lines up in the environment file.

## Rule of thumb (for future-self, and for the system prompt)

> **Before quoting a rule from AGENTS.md, identify which layer it
> belongs to**: environment (current) / archive (historical) /
> upstream template (generic fork-advice). Default to environment;
> demote upstream rules to "upstream convention" with explicit tag.

This is **a methodology error in reading, not a user preference** —
it does NOT belong in `~/.hermes/memories/USER.md` as a Hang-taught
rule. It belongs in vault as an observation so future-self can
self-check on first wake-up, and so the system prompt's
`AGENTS.md owner 分層` entry points to a documented incident rather
than just stating the rule abstractly.

## Trace

This observation was the **4th** thing Hestia added to user memory
on 2026-06-11 01:23, merged into the "主模型" entry:
> "§ 主模型 = minimax-oauth + MiniMax-M3 (不是 DeepSeek v4-pro)。
>  DeepSeek v4-pro 只備用。AGENTS.md 寫的「DeepSeek v4-pro 唯一主力」
>  過期於 2026-06-10 rebirth 後。"

Memory (1,375 chars, 92% used) is the source of truth for runtime;
this vault note is the incident record + rule documentation for
human review and cross-session context when memory is compressed.
