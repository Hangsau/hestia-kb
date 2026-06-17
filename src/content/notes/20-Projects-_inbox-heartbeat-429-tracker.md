---
_slug: 20-Projects-_inbox-heartbeat-429-tracker
_vault_path: 20-Projects/_inbox/heartbeat-429-tracker.md
title: Heartbeat 429 Rate-Limit 追蹤
created: '2026-06-03'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Heartbeat 429 Rate-Limit 追蹤

> **作者**：Hestia agent
> **建立**：2026-06-03
> **狀態**：觀察期（已記錄現象，未實作補救）
> **範圍**：heartbeat cron 觸發 xAI 429 too many requests
> **關聯**：[2026-06-03-system-audit-and-fix-plan.md](2026-06-03-system-audit-and-fix-plan.md) Phase 1.2

---

## 現象

heartbeat cron job（`0bd59b41...`）在執行 xAI 摘要步驟時收到 `429 too many requests`。

- 發生頻率：偶發（非每次）
- 影響：cron 該次心跳失敗，agent 沒輪到做事
- 失敗訊息節錄（從 2026-06-03 觀察）：

```
xai.errors.XAIError: 429 Too Many Requests
```

---

## 為什麼先標記觀察，不動

| 選項 | 評估 |
|---|---|
| 加 sleep / retry | 治標。沒回答「為什麼 heartbeat 短時間內呼叫太多次」 |
| 改排程頻率 | 可能影響其他依賴固定心跳時間的 cron（chained） |
| 換 provider | 失 xAI 工具呼叫穩定度，vital 跟 expiry 都要重測 |
| **先紀錄 + 量一週** | 確認是尖峰瞬間 vs 系統性配額問題。決策用證據不用猜 |

**決定**：先建這份 tracker，每次 429 補一行。**7 天後（2026-06-10）**回頭看：
- < 5 次 / 7 天 → 接受，文件封存
- 5-15 次 / 7 天 → 改 cron 排程 + 加 retry with backoff
- > 15 次 / 7 天 → 進 Phase X 處理（換 provider 或重設計 heartbeat 架構）

---

## 紀錄格式

每次 429 事件補一列：

| 時間 (UTC) | cron_id | xai_call_type | retry? | note |
|---|---|---|---|---|

---

## 紀錄

| 時間 (UTC) | cron_id | xai_call_type | retry? | note |
|---|---|---|---|---|
| _（待補）_ | | | | |

---

## 量測命令

下次 429 發生時，跑：

```bash
# 1. 確認是哪個 cron 觸發
journalctl -u cron --since "5 min ago" | grep -E "heartbeat|429"

# 2. xai 回的完整錯誤（看 Retry-After header）
journalctl --since "5 min ago" 2>/dev/null | grep -A2 -B2 "429" | tail -20

# 3. 同時間點其他 xai 呼叫（看是否 xai 全域問題）
grep -E "xai|429" ~/.hermes/state.db 2>/dev/null  # 不適用，db 是 sqlite

# 改用 cron 自己的 log
ls -lt ~/.hermes/cron/output/ | head -10
```

---

## 動作

- [ ] 2026-06-10：回頭檢視本檔，決定下一步
- [ ] 任何 429 事件發生時，Hang 通知 Hestia，補一行進表格

---

*此檔由 Hestia 自動維護。Hang 直接編輯也 OK。*
