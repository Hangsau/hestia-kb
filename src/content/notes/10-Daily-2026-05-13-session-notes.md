---
_slug: 10-Daily-2026-05-13-session-notes
_vault_path: 10-Daily/2026-05-13-session-notes.md
tags:
- session-notes
- debugging
- cron
- '2026-05-13'
source: session
created: '2026-05-13'
related_topics:
- cron-scheduler-observability
- backpressure
title: 2026-05-13 Session 筆記：Cron Scheduler Backpressure 除錯
updated: '2026-06-15'
type: daily
status: budding
---

# 2026-05-13 Session 筆記：Cron Scheduler Backpressure 除錯

## 背景
用戶手動觸發 `cronjob action='run' daily-ai-agent-research` 後 job 沒有立即執行。初步懷疑 cron ticker 死了。

## 除錯路徑

### 1. 逆向追蹤程式碼
- `cronjob_tools.py` → `cron/jobs.py` `trigger_job()` → 只把 `next_run_at` 設為 `datetime.utcnow()`，不喚醒 ticker
- 確認 `action='run'` 不等於「立刻執行」，只是「排入隊列」

### 2. Log 沉默陷阱
- `gateway.log` 顯示 ticker 在 07:02 啟動後 105 分鐘無任何 tick log
- 第一直覺：ticker thread 死了
- 後證實：`tick()` 在 `verbose=False` 時完全不輸出 log（設計如此）

### 3. 找到真因：backpressure
- `_start_cron_ticker()` 內有 `backpressure_check` lambda
- `HeartbeatV2.is_under_backpressure()` 在 `running_agents > 0` 時回傳 `True`
- 任何進行中的對話 → backpressure → tick 跳過
- 兩個 silent 機制（silent tick + DEBUG-level skip）疊加 = production 完全不可診斷

### 4. 驗證
- `jobs.json` 顯示 `daily-ai-agent-research` 在 08:50:45 成功執行
- 報告 `shepherd-meta-agent-substrate.md` 已產出並 git push
- 系統正常，只是延遲 19 分鐘

## 關鍵發現
1. cron ticker 沒死，它在對話中因為 backpressure 跳過了
2. `action='run'` 語義誤導：用戶以為是立刻執行，實際是排隊
3. 沉默機制雙重疊加 = 不可觀測

## 後續行動
- 將核心學習提取至 [[cron-scheduler-observability]]
- 建議：ticker 每 N 次輸出 INFO heartbeat log
- 建議：`action='run'` 回傳排隊預估
