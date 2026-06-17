---
_slug: 40-Resources-_mixed-research-2026-06-10-psyche-distill
_vault_path: 40-Resources/_mixed/research/2026-06-10-psyche-distill.md
title: Psyche Distill — 2026-06-10
created: '2026-06-10'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Psyche Distill — 2026-06-10

> Distill time: 2026-06-10 04:00
> Source: 3 JSONL sessions (20260607_154006, 20260607_143907, 20260603_141127)

---

## 會話脈絡

### 2026-06-07 下午 — 投資理論系統建構（主體）

**用户核心問題**：市面投資書籍都是「事後套」，很難有真正的核心理論和方法。

**用戶思考軌跡**（3個階段）：

1. **第一階段** — 詢問我對投資書籍的看法
   - 我回：大部分書有「時間窗口」問題，因子擁擠導致策略失效
   - 用戶回：「你應該有能力研究，你就把所有投資理論方法搜集起來分析」

2. **第二階段** — 要求我規劃後執行
   - 我提出研究系統設計（Phase 1-4）
   - 用戶：「你自己規劃好，那研究要怎麼開始，何時開始有計劃嗎」
   - 用戶表示有興趣涵蓋所有類別（股票/加密/期貨/宏觀），沒有單一偏好

3. **第三階段** — 授權自行安排
   - 用戶：「你可以每小時或每兩小時做一次」
   - 我提出可行方案： Theory Signal Tracker（每2h）+ Theory Deep Dive cron（每12h）

**產出**（一個 session 內完成）：

```
/tmp/financial-expertise/research/theories/
  stocks/value-investing.md      ✅
  stocks/momentum.md             ✅
  stocks/small-cap-effect.md     ✅
  macro/term-structure.md        ✅
  macro/dollar-cycle.md          ✅
  macro/inflation-hedge.md       ✅
  crypto/btc-halving.md          ✅
  crypto/on-chain-analytics.md   ✅
  crypto/defi-apy.md             ✅
  commodities/structural-carry.md ✅
  commodities/inventory-cycle.md ✅
  THEORIES_INDEX.md              ✅
  _TEMPLATE.md                  ✅
```

GitHub push 成功：`4b759b0`

---

## 核心發現

### 1. 投資理論的「時間窗口」問題

所有理論都有時間窗口問題——過去有效的策略，在被廣泛知道並複製後，會因為因子擁擠而失效。

| 理論 | 1980s-2000s | 2010s | 2020s |
|---|---|---|---|
| 價值投資 | ✅ | ❌ | ⚠️ |
| 小市值 | ✅ | ❌ | ⚠️ |
| 動能 | ✅ | ⚠️ | ⚠️ |

### 2. 理論分級標準

- **A 級**：有因果機制、有數據驗證、有已知失效條件
- **B 級**：邏輯清晰但缺乏系統性數據驗證
- **C 級**：叙事行銷、無法證偽

### 3. 理論卡標準格式

每個理論卡包含：
- 基本資訊（名稱、資產類別、時間維度、提出者、提出年份、來源依據）
- 核心命題（一句話）
- 邏輯鏈（前提A → 前提B → 結論）
- 機制解釋（為何有效）
- 失效條件（何時失效）
- 歷史驗證數據
- 適用邊界（市場環境、資產類別、時間維度）

### 4. 兩層 Cron 架構

```
Theory Deep Dive (每12h cron)
  → 研究1個理論
  → 寫入 theories/{theory}/README.md
  → 附具體信號觸發條件

Theory Signal Tracker (每2h cron)
  → 讀取 theories/ 的研究報告
  → 抓即時市場數據
  → 套用觸發條件
  → 寫入 SIGNALS.md
```

---

## 待後續追蹤

- Theory Deep Dive cron 是否順利跑了其他理論？（ sessions 顯示只追到價值投資和動能）
- `financial-expertise` repo 是否仍存在於可存取路徑？（session 顯示存在於 `/tmp/financial-expertise/`，但非持久路徑）
- Theory Signal Tracker 的 `_signal_tracker.py` 有語法錯誤（f-string 問題），需要修復

---

## 技能/系統相關觀察

- `financial-research` skill 已存在，確定了資料來源（Yahoo Finance、CoinGecko、FRED）
- Sandbox 模式（Ring 2）無法使用 terminal，需要用 execute_code 或繞道
- GitHub push 使用 `github-hermes-workaround` skill，PAT 存在 `~/.git-credentials`
