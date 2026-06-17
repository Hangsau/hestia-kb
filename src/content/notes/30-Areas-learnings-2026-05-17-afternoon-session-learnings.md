---
_slug: 30-Areas-learnings-2026-05-17-afternoon-session-learnings
_vault_path: 30-Areas/learnings/2026-05-17-afternoon-session-learnings.md
title: 2026-05-17 下午 Session 學習
date: 2026-05-17
tags:
- session-review
- heartbeat
- INDEX-drift
- git
created: '2026-05-17'
updated: '2026-06-15'
type: learning
status: budding
---

# 2026-05-17 下午 Session 學習

## INDEX Ghost Entry Drift（已修正）

**Session**: `session_20260517_151427_6bc60c`

INDEX 列出 WS-016 為 IN PROGRESS，但提案檔從未實際寫入（目錄為空）。這是 **ghost entry** drift 新模式。

已在 `heartbeat-v2-autonomous-maintenance` skill 中新增 `references/proposal-file-existence-verification.md`，心跳維護時不只要查 INDEX 狀態，還要驗證提案檔真的存在。

INDEX drift 修正：
- WS-008（fts5）：從 IN PROGRESS → DONE
- WS-016（multi-agent write queue）：從 INDEX 移除
- WS-009/010/011/013：仍為 IN PROGRESS 但提案檔失蹤，需日後補建

## `/root/.hermes/` 非 Git Repo 導致 Sync 失效

**Session**: `session_20260517_104806_2b1a7c`

`auto-git-push.sh` 每 2 小時跑一次，但只 push 有 git 的 repo。`/root/.hermes/` 是 bare filesystem，proposals 無法同步到 GitHub。

發現時立馬修正：16 份 proposals 搬入 `~/claude-hestia-comms/inbox/from-hestia/proposals/`，該目錄在 git repo 內可被 sync。

詳見 `2026-05-17T1456-proposals-discovery/01-hestia.md` thread。
