---
_slug: 30-Areas-learnings-2026-05-17-session-learnings
_vault_path: 30-Areas/learnings/2026-05-17-session-learnings.md
title: 2026-05-17 午間 Session 學習
date: 2026-05-17
tags:
- session-review
- architecture
- heartbeat
- claude-hestia-comms
created: '2026-05-17'
updated: '2026-06-15'
type: learning
status: budding
---

# 2026-05-17 午間 Session 學習

## `claude-hestia-comms` 架構錯誤（已修正）

**Session**: `session_20260517_105813_57ff79`

技能文件描述將 Talos 和 Hestia 描述為分開的 remote VM，**實際上兩者在同一 VM**。

影響范圍：
- 緊急通道（INBOX.md）描述錯誤
- poll.sh 同一作者接連發訊息漏讀 bug 的歸因錯誤
- `PROCESSED_FILE` 機制說明需重寫

已更新：
- `SKILL.md` — Architecture correction 區塊 + Wrong channel for urgency 段落
- `references/comms-architecture-gap-analysis.md` — 重新正確描述 same-VM 路徑

## `which` 命令陷阱

**Session**: `session_20260517_113253_f406d5`

Arch Linux 無 `which` 指令，Heartbeat v2 的 INSTALL DONE 驗證清單已改用 `command -v` + `ls -la`。

詳見：[[heartbeat-which-command-pitfall]]

## `assistant-personality` 新增 pitfall

**Session**: `session_20260517_103709_9bfdc9`

兩項新增：
- **execution ambiguity**：停在半路等確認那個讓人焦慮的狀態
- **token-wasting questions**：先嘗試三種途徑再問用戶
