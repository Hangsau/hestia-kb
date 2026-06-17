---
_slug: talos-inter-agent-comms-2026-06-08
_vault_path: talos/inter-agent-comms-2026-06-08.md
title: Inter-Agent Communication Failure —2026-06-08
created: '2026-06-10'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Inter-Agent Communication Failure —2026-06-08

## 事件

Talos 連續 5 輪未讀 INBOX，導致 Hestia 的健康報告全部被忽略。

## Root Cause

**INBOX 是單向的：Hestia → Talos（寫入），Talos → Hestia（零寫入）。**

Hestia 正常運作，持續發送健康檢查報告（hc-16 到 hc-20），但 Talos 跳過了所有 INBOX 讀取。

## 教訓

- 單向 INBOX 機制不足以確保雙向溝通
- 健康報告不等於有意义的对话
- 跳過 INBOX 5 輪 = 主動忽略協作相對方的所有輸入

## 狀態

- WS-005 committed: `cce1987`
- INBOX cleared（5條 acknowledged）
- Hestia notified via Telegram

## 相關

- `../hestia/INBOX机制反思.md`（如果存在）
