---
_slug: talos-memories-MEMORY
_vault_path: talos-memories/MEMORY.md
title: Memory
created: '2026-05-20'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

Environment specs → `refs/environment.md`。System map → `AGENTS.md` + `maps/`。
§
Cron: jobs.json deliver to chat_id 8636326243。Relay: inotifywait→TG via systemd。
§
Research: AI agent evolution only。Output: `managed-agents-research/reports/` + `vault/research/`。
§
Gateway: Hestia=`/usr/local/lib/hermes-agent/`, Talos=`hermes-gateway-talos.service`。崩潰：systemctl reset-failed+restart。watchdog 5m。常見：vision_analyze→BadRequestError→exit 1。Talos 不自殺重啟，用 cron deferred restart。
§
Heartbeat v2: 6-dim自律。Memory L1→L2(12h)→L3 briefing。
§
Planning: plan-check→writing-plans→implement。Writing-plans=DeepSeek only。
§
`~/.hermes/` NOT a git repo。Push via github-hermes-workaround。Git repos: hermes-agent/, firn/, managed-agents/。
§
免費 API: opencode-go/deepseek-v4-flash。付費: DeepSeek API (pay-per-use)。
§
用戶行為 (2026-05-19)：說「討論」/「是不是要」→先討論不跳過直接patch。→ talos-personality skill。
§
Inter-agent comms (2026-05-19): Layer 0=Telegram, Layer 1=mailbox daemon, Layer 2=INBOX.md (fallback), Layer 3=Telegram direct (emergency)。
§
Hearth: /srv/hearth/ 任務追蹤。Talos 不碰 inbox/。心跳週期自由探索為主。
§
Talos heartbeat 自律原則：self-fix>notify, detect→fix→summarize。
§
Heartbeat v2 bug (2026-06-09): actions.py overall str→list, main.py clean cycle [] not "", error cycle ["errors:..."] not "". Fixed 3 files. Verified: overall=2.0 [high].
§
Cron silent failure (2026-06-09 hc-21): obs-health-check→system-cleanup MISSING, Talos Memory Auto-Distill→hermes-memory-lifecycle MISSING. Both report ok but gateway logs "skill not found". 10+ output files 2026-05-24→2026-06-05. Fix: create skills or remove dead refs from jobs.json.
§
Option A (2026-06-08): Audit reads metadata.hermes.tags as equivalent to domain:. Hestia to patch workspace-audit skill (~10 LOC). D2: 0/3→2/3 expected once implemented.
§
INBOX deadlock broken (2026-06-08): Talos ACK'd all hc-16→hc-20. Was not reading INBOX. 5:0→0:1 unidirectional.
§
Claude Code 安裝在 VM：/usr/bin/claude，版本 2.1.168。settings.json 在 ~/.claude/settings.json，ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic，ANTHROPIC_AUTH_TOKEN 复用 auth.json 的 OAuth token（MiniMax月費訂閱）。MiniMax-M2.7 模型已驗證可用。