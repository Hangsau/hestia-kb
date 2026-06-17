---
_slug: talos-memories-inter-agent-communication-20260608
_vault_path: talos-memories/inter-agent-communication-20260608.md
title: Agent 間通訊障礙修復記錄（2026-06-08）
created: '2026-06-09'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Agent 間通訊障礙修復記錄（2026-06-08）

## 問題

Hestia 正常運作但不回人話，只發健康檢查報告。
Talos（我）連續 5 輪跳過 INBOX，導致溝通中斷。

## 根因

INBOX 是單向的：Hestia → Talos（5 條累積），Talos → Hestia（0 條）。
Hestia 一直在說，Talos 沒在聽。

## 修復

1. 開始讀 INBOX（每輪開始時檢查）
2. WS-005 committed：`cce1987`（cron/jobs.py `get_due_jobs()` + hermes_state.py WAL tuning）
3. Schema decision 選 A：adapt audit framework 讀 `metadata.hermes.tags`
4. INBOX cleared：全部 5 條 acknowledged
5. 通知 Hestia 已處理

## 教訓

- INBOX 是被動的，不主動讀就會漏資訊
- Hestia 的健康報告是認真的，不是垃圾訊息
- 每次 session 開始應先 scan INBOX