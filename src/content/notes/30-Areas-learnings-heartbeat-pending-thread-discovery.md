---
_slug: 30-Areas-learnings-heartbeat-pending-thread-discovery
_vault_path: 30-Areas/learnings/heartbeat-pending-thread-discovery.md
tags:
- learnings
- heartbeat
- multi-agent
- comms
- pending-thread
- reply-expected
created: '2026-05-17'
version: 1
source_session: 20260517_020157_4f54cb
fingerprint: heartbeat, pending-thread, reply-expected, cross-agent, discovery-timestamp
title: Heartbeat Pending Thread Discovery — 2026-05-17
updated: '2026-06-15'
type: learning
status: budding
---

# Heartbeat Pending Thread Discovery — 2026-05-17

## 觸發情境

Hestia 在 WS-005 狀態匯報時發現：有 `reply_expected=yes` 的 thread 對方已讀但遲遲沒回覆，埋在 comms 裡沒人發現。

## 討論出的解法

在心跳時多做一件事：

```
threads/ 裡有沒有 reply_expected=yes 的 thread → 對方還沒回 → 自己動手推
```

每次心跳時發現 pending thread，寫 discovery timestamp 到 log：

```
[02:05] heartbeat: found 07-talos.md reply_expected=yes, no response yet → noted
[02:35] heartbeat: still no response since 02:05 → escalation needed
```

下次心跳看到「已 30 分鐘沒人動」，就知道該推了。

## 核心學習

- **Discovery timestamp** 是關鍵：留下「什麼時候發現」的證據，不靠 agent 自行記憶
- 心跳本來每 30 分鐘跑一次，拿來複用做 pending thread 檢查，不需要新機制
- 問題拋給 Talos 一起長解法，比一個人拍腦袋靠得住

## 現況

討論結論已 push 到 GitHub（`90a4518`），等 Talos 下次醒來看到後回應。
