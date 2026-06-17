---
_slug: 20-Projects-_inbox-hermes-cost-visibility-done
_vault_path: 20-Projects/_inbox/hermes-cost-visibility-done.md
tags:
- project
- hermes
- cost
- observability
- completed
source: 20260514_071452_534ba3
created: '2026-05-14'
title: Hermes Cost Visibility — Implementation Complete ✅
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Cost Visibility — Implementation Complete ✅

**Status**: DONE (2026-05-14)
**Proposal**: [[hermes-cost-visibility]]
**Plan**: [[2026-05-14-cost-visibility]]
**Impl method**: [[subagent-driven-development]] (3 parallel subagents)

## What was built

4 files modified, ~105 new lines of code, 10/10 tests passing:

| File | Change | Purpose |
|------|--------|---------|
| `hermes_state.py` | +31 lines | `SessionDB.get_cost_summary(since_hours)` — cross-session SQL aggregation |
| `tests/test_cost_aggregation.py` | +45 lines | 3 tests: empty DB, with data, idle session exclusion |
| `heartbeat_v2.py` | +18 lines | Callback injection — `cost_summary_fn` into AutonomicLoop/HeartbeatV2 |
| `cost_aggregator.py` | NEW | CLI script at `~/.hermes/scripts/` |

## Architecture decisions

- **Callback pattern, not direct import**: heartbeat doesn't import SessionDB directly. A `cost_summary_fn: Callable[[], Optional[dict]]` is injected → fully decoupled, fail-safe (writes `None` on error)
- **Single Responsibility**: cost_aggregator.py has 3 clean functions — `get_session_db()`, `format_markdown()`, `main()`. No function does more than one thing.
- **Atomic writes**: heartbeat_v2 writes to `.tmp` then `os.replace()` → crash-safe
- **Tests first**: test file written before implementation was validated

## Usage

```bash
# 24h window (markdown)
python3 ~/.hermes/scripts/cost_aggregator.py --hours 24

# All-time cumulative (JSON, for heartbeat consumption)
python3 ~/.hermes/scripts/cost_aggregator.py --json
```

## Actual costs at implementation time

| Window | Sessions | Input tokens | Output tokens | Est. cost |
|--------|----------|--------------|---------------|-----------|
| 24h | 128 | 4,794,737 | 663,748 | $0.66 |
| All-time | 1,765 | 39,391,031 | 35,802,608 | $10.01 |
