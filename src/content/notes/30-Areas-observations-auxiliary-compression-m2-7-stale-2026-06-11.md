---
_slug: 30-Areas-observations-auxiliary-compression-m2-7-stale-2026-06-11
_vault_path: 30-Areas/observations/auxiliary-compression-m2-7-stale-2026-06-11.md
_parse_error: "while scanning for the next token\nfound character '`' that cannot\
  \ start any token\n  in \"<unicode string>\", line 9, column 8:\n    title: `auxiliary.*`\
  \ config block — sta ... \n           ^"
_raw_fm: '

  type: observation

  tags: [config-mismatch, hermes-ops, model-naming, delegation-pattern, hestia, post-rebirth,
  12:00-cycle]

  date: 2026-06-11

  cycle: context-distiller (12:00)

  source_session: session_20260611_063957_1aa5ef15 (06:39 Telegram DM, file mtime
  11:47:08, last block 11:41–11:47)

  follows_from: [agents-md-stratification-2026-06-11-0639]

  related: [hermes-rebirth-2026-06-10]

  title: `auxiliary.*` config block — stale `MiniMax-M2.7` model name across 4 sibling
  blocks

  created: 2026-06-11

  updated: 2026-06-15

  status: active

  '
title: '`auxiliary.*` config block — stale `MiniMax-M2.7` model name across 4 sibling
  blocks'
type: area
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# `auxiliary.*` config block — stale `MiniMax-M2.7` model name across 4 sibling blocks

## TL;DR

2026-06-11 11:41, Hang pasted a runtime warning that `auxiliary.compression provider 'minimax-oauth' is unavailable` and asked how to handle it. Hestia traced it to `~/.hermes/config.yaml` and found all 4 auxiliary sub-blocks (approval / compression / curator / mcp) hard-code `model: MiniMax-M2.7` while the active profile is `MiniMax-M3` via `minimax-oauth`. Hestia surfaced 4 options to Hang, did not auto-fix, and Hang delegated the fix to Claude Code. Hestia wrote 5 handoff guardrails for the delegation.

## The config state (read 11:46, `~/.hermes/config.yaml` auxiliary block)

| Sub-block | model | provider | Status |
|---|---|---|---|
| `auxiliary.approval` | `MiniMax-M2.7` | `minimax-oauth` | ⚠️ 跟 profile 不符 |
| `auxiliary.compression` | `MiniMax-M2.7` | `minimax-oauth` | ❌ **this is the warning** |
| `auxiliary.curator` | `MiniMax-M2.7` | `minimax-oauth` | ⚠️ 跟 profile 不符 |
| `auxiliary.mcp` | `MiniMax-M2.7` | `minimax-oauth` | ⚠️ 跟 profile 不符 |

The `provider: minimax-oauth` is correct (matches the profile's main provider). The `model: MiniMax-M2.7` is the stale part — the active main model is `MiniMax-M3`. The `M2.7` name is presumably a placeholder that was never updated post-rebirth, OR a model that exists in the provider's catalog but is not the one the agent is authenticated for, OR a typo (M2.7 vs M3).

## What the warning actually means

> "Configured auxiliary compression provider 'minimax-oauth' is unavailable — context compression will drop middle turns without a summary."

Per Hestia's 11:41 explanation to Hang: context compression is a separate, cheaper model call (not the main provider) that summarizes the middle of a long conversation when context window fills. The provider is `minimax-oauth` (configured), the model is `MiniMax-M2.7` (configured, stale). The provider is "unavailable" because the model is wrong — the call to `minimax-oauth` with `model=M2.7` returns an error.

**Consequence if unfixed**: long conversations will have middle turns **silently dropped** instead of summarized. This is a P0 latent issue for any long-running session (e.g., the 06:39 DM which already has 6 user turns + 11 assistant turns).

## The 4 options Hestia surfaced to Hang (11:46)

1. **Fix only `compression`** (minimal action, focused on the warning) — change `model: MiniMax-M3`, leave the other 3 blocks stale.
2. **Fix all 4 auxiliary blocks** (consistency) — set all 4 to `MiniMax-M3`.
3. **Verify M3 can actually run compression first** (recommended) — use `model_setup` skill or curl probe to confirm `MiniMax-M3` supports the compression API endpoint before committing the fix.
4. **Disable compression** (`compression.enabled: false`) — accept context window limit, eliminate the warning.

**Hestia's recommendation**: option 3 (verify) first, then 1 or 2. Reasoning: "修了還壞比不改更糟" — committing to a fix that still fails is worse than leaving the warning visible (the warning at least signals the problem).

## The decision + delegation

- Hang: "去做吧"
- Hestia reframed: "我去讓 claude code 處理好了" (Hang's actual words)
- Hestia handed off 5 guardrails for Claude Code (the relevant 5 of these are the "don't do X" guardrails, not the "do Y" instructions):

  1. **Scope is 4 blocks, not 1** — the mismatch is in `auxiliary.{approval,compression,curator,mcp}`, all using `MiniMax-M2.7`. Don't fix only the one in the warning; either fix all 4 (consistency) or explicitly justify fixing just one.
  2. **Active model is `MiniMax-M3` via `minimax-oauth`** — that's what `model:` should become. Don't guess at other model names (`M2.7-high`, `M3-turbo`, etc.) without verifying.
  3. **Verify M3 supports compression API before fixing** — use `model_setup` skill or a curl probe to `minimax-oauth` with `model=MiniMax-M3` to confirm the endpoint accepts the call. The probe must be **end-to-end** (real API request), not just a config-validate.
  4. **Reload / restart and confirm warning is gone before claiming done** — the warning fires at session start; if the fix isn't reloaded, the next session will still see it. A `hermes restart` or `config reload` is part of "done".
  5. **Verification method for "compression works"**: deliberately force a long conversation (or a synthetic one) to trigger compression, then check that a real **summary** appears in the middle-turn drop. "Compression happened" is not the bar — "compression produced a summary that preserves the key points" is.

## Why this is durable knowledge (not ephemeral)

- The `MiniMax-M2.7` stale name is a **config-level environmental fact** that survives across sessions. Any future Hestia cycle reading `config.yaml` will see it and may be confused.
- The "verify-before-fix" guardrail is a **methodology lesson** that applies beyond this specific config: any time a config change is driven by a runtime warning, the fix should be probed (not just written) before being committed.
- The 5 handoff guardrails are a **reusable delegation pattern** for "Hestia → Claude Code" config fixes: scope the actual blast radius (not just the warning), state the correct target, verify before committing, reload to confirm gone, and define a *behavioral* (not config-validate) success criterion.

## What's NOT in this observation

- The actual `config.yaml` file content beyond the auxiliary block (not needed for the observation; out of scope).
- The Claude Code execution itself (in progress; will be a separate observation if/when the fix lands and verification succeeds/fails).
- Memory implications — this does **not** go in `~/.hermes/memories/USER.md` (not a Hang-stated preference; one-time technical decision; a vault observation is the right scope).

## Trace

- Session: `session_20260611_063957_1aa5ef15` (model `MiniMax-M3`, base `https://api.minimax.io/anthropic`, started 06:39, file mtime 11:47:08)
- 對話標題：權限測試 + AGENTS.md 對齊 → **延伸至** `auxiliary.compression` warning 處理
- 接續：2026-06-11 08:00 cycle 的 AGENTS.md 對齊 observation（見 `agents-md-stratification-2026-06-11-0639.md`）—— 該 cycle 沒看到 11:41–11:47 區段
- 11:46 對話中 Hestia 提問「我先去抓檔案?」+ 11:47 結束於「好，那就交給他」+ 「Claude Code 那邊做完結果貼回來」
- Config state captured from `~/.hermes/config.yaml` auxiliary block at 11:46

## Action items

- [ ] Wait for Claude Code handoff result. If fix lands and verification passes: mark this observation `status: resolved` and add a "post-fix verification" entry to `hestia/log.md`.
- [ ] If verification fails: escalate. The "M3 supports compression" assumption is unconfirmed; if false, the right answer may be option 4 (disable compression) rather than chasing model name variants.
- [ ] Check whether other post-rebirth config sections (non-auxiliary) have similar stale model references — `MiniMax-M2.7` may appear elsewhere. (Not investigated this cycle, low priority.)
