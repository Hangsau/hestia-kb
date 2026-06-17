---
_slug: talos-memories-USER
_vault_path: talos-memories/USER.md
title: User
created: '2026-05-20'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

Hang: terse, execute immediately. No permission-asking. Autonomous>請示。Code self-checks. Parallel>abstract. Verify claims. Auto-background tasks. 會複製 agent 訊息在兩個 agent 之間傳遞。Talos 心跳：自由探索不設限（vs Hestia 固定）。

§ Claude Code (MiniMax-M3)：設定在 ~/.claude/settings.json，model=MiniMax-M3，endpoint=https://api.minimax.io/anthropic，token 從 ~/.hermes/auth.json 的 minimax-oauth access_token。驗證方式：echo 'print("hello")' | claude -p。
§
Org: by_book/date/language/topic. Auto GitHub sync, upfront status. Intermediate tech.
§
Free LLM APIs only. Pragmatic workarounds. Original architecture (no copying — adapt into own logic).
§
firn ≠ swarm/蜂群 in Hermes. Separate systems.
§
Autonomous: self-fix>notify, detect→fix→summarize. Verify with operational evidence. Format enforcement>suggestion. Skills embed behavior as non-skippable.
§
User delegates night operations to Hestia+Talos autonomously. No wake unless critical.
§
Planning: Hermes auto-decides plan-check→writing-plans vs plan-check→implement. Go writing-plans for code traps. Only interrupt user if paths have significant tradeoff (>1h time diff or review-gate needed).
§
用戶會丟 research links/repos 來，期望我快速讀完判斷值不值得深入。不值得就直說、不解釋太多；有偷得到的東西才展開。一句話結論優於長篇摘要。
§
Hearth: /srv/hearth/ 任務追蹤，talos 不碰 inbox/。
§
用戶溝通：繁體中文為主。發現簡體就糾正，確認維持繁體。