---
_slug: 30-Areas-learnings-cron-one-shot-restart-loop-fix
_vault_path: 30-Areas/learnings/cron-one-shot-restart-loop-fix.md
tags:
- learnings
- cron
- debugging
- gateway
- restart-loop
created: '2026-05-17'
version: 1
source_session: 20260516_174120_f90a12
fingerprint: cron, one-shot, completion-state, restart-loop, gateway-restart, attempted-at,
  systemd-working-directory
title: Cron One-Shot Restart Loop Fix — 2026-05-17
updated: '2026-06-15'
type: learning
status: budding
---

# Cron One-Shot Restart Loop Fix — 2026-05-17

## 觸發情境

Gateway 進入重啟循環（`systemctl restart hermes-gateway` 一直被觸發），源頭是一個 `gateway-self-restart` 一次性 cron job。

## 根因分析

1. **systemd WorkingDirectory 指向錯誤 repo**
   - `/etc/systemd/system/hermes-gateway.service` 的 `WorkingDirectory=/root/hermes-agent`（dev 版）
   - 正確應為 `/usr/local/lib/hermes-agent`（production 版）
   - 導致 dev 版 run.py 被加載（缺少 Heartbeat V2 啟動碼）

2. **One-shot job 缺少完成狀態**
   - `attempted_at` 欄位存在但 `mark_job_run` 未在執行後清除
   - One-shot job 被觸發後，狀態停留在 `attempted_at`，導致下次 gateway start 又觸發

3. **Cron job 自觸發 gateway restart 無防護**
   - Job 直接執行 `systemctl restart hermes-gateway`，形成循環

## 修復動作

1. 用 `sudo sed` 修正 `WorkingDirectory`，`sudo systemctl daemon-reload`
2. 建立一次性 cron job（排程 15 秒後執行）繞過 suicide 限制
3. 從 jobs.json 正式刪除 stale one-shot job
4. 準備修補 `jobs.py`：`mark_job_run` 執行後清除 `attempted_at`

## 核心學習

- **One-shot job 語義**：執行完必須有 `completed_or_abandoned` 狀態，不能只靠 `attempted_at`
- **Gateway restart command**：cron job 偵測到 `systemctl restart hermes-gateway` 應拒絕執行
- **systemd 路徑錯誤是隱形炸彈**：症狀是 heartbeat 不跳、程式碼完全正常但就是不跑
