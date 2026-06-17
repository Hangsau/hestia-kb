---
_slug: 30-Areas-learnings-2026-05-27-0916-psyche-financial-research-architecture
_vault_path: 30-Areas/learnings/2026-05-27-0916-psyche-financial-research-architecture.md
tags:
- psyche
- financial-research
- cron
- learnings
source: psyche/sessions/session_20260527_*
created: '2026-05-27'
title: Psyche 每日市場掃描系統架構（2026-05-27）
updated: '2026-06-15'
type: learning
status: budding
---

# Psyche 每日市場掃描系統架構（2026-05-27）

## 核心問題與修復

### 1. Cron 檔案系統隔離問題

**問題**：`cron job run` 是獨立的 agent session，看不見 terminal 的 `/tmp/financial-expertise/` 目錄狀態。git push 看似成功但寫入位置錯誤。

**修復方案**：
- 選項A：建立 cron 時指定 `workdir=/tmp/financial-expertise`
- 選項B：使用 `no_agent=True`（direct script execution，無 LLM agent）

**驗證**：檢查 GitHub commit 是否在正確 repository。

---

### 2. DXY 資料異常

**問題**：`^DXY` Yahoo Finance 返回 `instrumentType: MUTUALFUND`，`quote[0].close = null`，無法取得收盤價。

**處理**：
- 移除 `^DXY` 先嘗試再 fallback 的邏輯
- 改用 `UUP`（ProShares UltraShort Euro ETF）期貨作為代理
- 必須標註：「UUP 為代理指標，非直接 DXY 報價」

---

## 每日 Cron 循環架構

| Job ID | 名稱 | Schedule | 功能 |
|--------|------|----------|------|
| `98216e02d5f5` | 每日上午市場快照 09:30 | 每天 09:30 | 台股開盤方向 + 隔夜美股 |
| `0fad0dab8a44` | 每日市場快照 13:45 | 每天 13:45 | 台股真正日終結算 |
| `ab1557e0f0b7` | Psyche 每日自檢 14:00 | 每天 14:00 | 品質關卡自檢 |
| `64cbcabd2f24` | 日結蒸餾 | 每天 23:30 | session 蒸餾 |

---

## 品質關卡（交付前自我檢查）

```
交付前自我檢查：
1. 數學一致：日高低差距 > 2% → 漲跌% 不能接近 0%
2. 數字完整：每市場5維度都有數字
3. 口徑一致：DXY/UUP 不混用
4. 場面話檢測：出現「區間整理」「成交量平淡」等關鍵詞 → 重寫
5. 時間戳：資料時間是否合理（台股13:45前不是真正日終）

若發現問題 → 修正後再交付
若無法修正 → 在報告中標註「⚠️ 數據存疑」
```

---

## 時間邏輯（台股）

| 時間 | 含義 |
|------|------|
| 09:00 | 台股開盤 |
| 09:30 | 开盘30分鐘，方向初步確立（不是收盤，是盤中） |
| 13:45 | 收盤後15分鐘，真實日終結算數據 |

**原設計錯誤**：早上 9:30 標記為「收盤掃描」邏輯矛盾。

---

## Hang 的角色定位

**核心觀察**：Hang 不回答技術決策問題。他的角色是「觀察 Psyche 的能力成長」，不是「幫我做規劃」。

**Psyche 需要的行為**：
- 自己規劃、自己決定
- 無法決定時說「我決定了」而不是「你要我做什麼」
- 不要問，直接做

---

## 宏觀事件日曆（最小可行）

每週在報告中加一block：

```
本週宏觀日程
- 日期 - 事件（發布機構）
- 05/28（三）— FOMC 會議紀錄
- 06/04（三）— 非農就業報告（NFP）
- 06/05（四）— CPI 年增率（美國）
```

時間已知，不需要爬蟲，沒有搜索成本。

---

## 債市分析框架（2026-05-27）

### 核心數據

| 項目 | 數值 | 變化 |
|------|------|------|
| 10Y 殖利率 | 4.493% | -1.43% |
| 2Y 殖利率 | 3.582% | -0.08% |
| 30Y 殖利率 | 5.026% | -0.75% |
| 10Y-2Y 利差 | +0.911% | 正（未倒掛）|
| VIX | 17.01 | +2.53% |

### 判斷框架

**不是危機，是慢性壓力。**

| 風險維度 | 影響 |
|----------|------|
| 10Y 持續 > 4.5% | 股市本益比天花板下移，涨不動 |
| 30Y = 5.026% | 房貸/企業借貸成本高，抑制經濟活力 |
| 曲線持續 0.5-1% 低利差 | 一有風吹草動容易再次倒掛 |