---
_slug: 20-Projects-hestia-roadmap-stalled-2026-06-09
_vault_path: 20-Projects/hestia/roadmap-stalled-2026-06-09.md
type: learning
date: 2026-06-09
trigger: Hang asked "evolution-roadmap 有在動嗎? 看你第一天做完就沒進度了"
status: seedling
title: Evolution Roadmap 卡住紀錄
created: '2026-06-09'
updated: '2026-06-15'
tags: []
---

# Evolution Roadmap 卡住紀錄

## 狀態
- 開始: 2026-06-06, Day 1 `provider-latency-tracker.py` ✅
- 衍生: Day 1b `cron-audit.py` 強化 ✅
- 之後: 12 天 roadmap 全部 ⏳,3 天 (6/7-6/9) 完全沒動
- 文件: `~/obsidian-vault/hestia/evolution-roadmap-2026-06.md`

## 根本原因
**Roadmap 設計假設「Hestia 會自己醒來繼續做」,但實際上 Hestia 只在 user 觸發時醒。**

Restart SOP (roadmap line 114-121) 寫「新的 Hestia 醒來讀 roadmap」,但沒說「誰叫醒 Hestia」。Driver = Hang,但 Hang 不會每天主動 trigger「接 roadmap」這種事。

這不是 bug,是設計假設錯。

## 修法選項 (2026-06-09 已討論, 未實作)

| 選項 | 取捨 | 為什麼沒做 |
|---|---|---|
| 加 cron driver (每天 wake Hestia) | 結構修,但 = 新長期工作 + 需驗證 | 本 session 資源已用很多 (vault bug + root 密碼 + X + pacman 升級),再加 cron 是過度承諾 |
| 本 session 接 Day 2 | 短期止血 | 同上,熱鍋上不該加第 5 個改動 |
| 維持現狀 (Hang 手動) | 簡單,不會有新 bug | 已接受 (Hang 說「你自己決定 怎麼做好吧」) |

## 給未來 Hestia 的判準
- 如果 Hang 主動 trigger 「做 roadmap」或 「Day N」,接 roadmap,別重新發明
- 如果有新的 driver 機制 (e.g. heartbeat 選單多一條「推進 evolution-roadmap」),優先用那個
- 如果本 session 已在 3+ 個改動中途,**不要**再開新長期工作 (cost-heatmap / cron driver / 新 skill)

## 連動
- 跟 MEMORY.md § "Session hygiene" 同一條紀律: 「在多步驟工作中間不開新工作」
- 跟 USER profile § "輸出優先序 3 留 future" 同類: future bucket 不搶 active 資源
