---
_slug: 30-Areas-learnings-cron-scheduler-observability
_vault_path: 30-Areas/learnings/cron-scheduler-observability.md
tags:
- learnings
- cron
- debugging
- observability
created: '2026-05-13'
version: 1
source_session:
- - 2026-05-13-session-notes
fingerprint: cron, ticker, backpressure, observability, silent-failure, action-run
title: Cron Scheduler 可觀測性
updated: '2026-06-15'
type: learning
status: budding
---

# Cron Scheduler 可觀測性

## Version 1 — 2026-05-13

### 觸發情境
手動觸發 `cronjob action='run'` 後 job 沒立即執行。花 ~2h 逆向程式碼 + log 考古後發現系統正常，只是 backpressure 導致延遲。

### 核心學習

1. **Silent tick 設計缺陷**
   - `scheduler.tick(verbose=False)` 在 daemon 模式下完全不輸出 log
   - 105 分鐘內沒有任何 tick 記錄 → 誤判 ticker thread 已死
   - **教訓**：daemon 組件 silent-by-default 是反模式。至少 critical path 要有 INFO 層級 heartbeat

2. **Backpressure skip 隱形**
   - `is_under_backpressure()` 在 `running_agents > 0` 時回傳 `True`
   - Skip log 是 `logger.debug` 層級 → production 完全不可見
   - 兩個 silent 機制疊加 = **完全失去可觀測性**

3. **`action='run'` 語義誤導**
   - 用戶認知：「立刻執行」
   - 實際行為：`next_run_at = now()`，等 ticker 撿，ticker 在 backpressure 就排隊
   - **建議**：至少回傳一個 warning，或繞過 backpressure（因為是使用者明確要求）

### 系統驗證
- Ticker 正常運作（heartbeat、context-distiller、西遊記全部準時執行）
- 手動觸發的 job 在 backpressure 解除後被撿起（延遲 19 分鐘）
- 報告產出正常、git push 成功

### 相關
- [[project-map-index]] — managed-agents 是 cron 主要使用者
- [[hermes-agent-framework]] — gateway run.py 的 `_start_cron_ticker` 實作
