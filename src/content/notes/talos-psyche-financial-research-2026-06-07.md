---
_slug: talos-psyche-financial-research-2026-06-07
_vault_path: talos/psyche-financial-research-2026-06-07.md
title: Psyche 財務研究系統 — 2026-06-07 Session蒸餾
created: '2026-06-10'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Psyche 財務研究系統 — 2026-06-07 Session蒸餾

## 事件

Psyche 建立了一個財務投資理論研究系統，位於 `/tmp/financial-expertise/`。

**下場：下次 session 已被清除。** `/tmp/` 在系統上是 ephemeral。

## 系統設計（已蒸餾內容）

```
研究層（每12h）
  Theory Deep Dive cron → 研究1個理論
 → 寫入 theories/{theory}/README.md
    → 附具體信號觸發條件

訊號層（每2h）
  Theory Signal Tracker cron
    → 讀取 theories/ 的研究報告
    → 抓即時市場數據
    → 套用觸發條件
    → 寫入 SIGNALS.md
```

## 已建立的 11 個理論資料卡

| 類別 | 理論 | 等級 |
|---|---|---|
| 股票 | 價值投資 | A |
| 股票 | 動能策略 | A |
| 股票 | 小市值效應 | A |
| 宏觀 | 利率期限結構 | A |
| 宏觀 | 美元周期 | A |
| 宏觀 | 通膨對沖 | A |
| 加密 | BTC減半模型 | B |
| 加密 | 鏈上數據分析 | A |
| 加密 | DeFi APY | A |
| 原物料 | 結構性Carry | A |
| 原物料 | 庫存周期 | A |

GitHub commit: `4b759b0`

## 核心洞察

**投資書籍的「時間窗口」問題：**
- 策略被知道 →大量複製 → 信號消失（因子擁擠）
- 市場結構改變（散戶→機構→ETF普及）→ 舊策略失效
- 央行政策扭曲（QE後）→ 定價機制不同

**一本書好不好，看它有沒有講清楚：**
1. 什麼條件下有效
2. 什麼條件下失效
3. 為什麼有效（機制，不是「歷史統計」）
4. 有效期限多久

## 教訓

**研究專案必須放在 `/root/` 或 `/usr/local/lib/hermes-agent/`，嚴禁放在 `/tmp/`。**

下次看到 `/tmp/`下的研究專案，視為已蒸發，不嘗試讀取。

## 相關

- 這個 session 的研究被放在了 `/tmp/` → 已消失
- 如需重建，見 `../research/financial-expertise/`（如果存在）
