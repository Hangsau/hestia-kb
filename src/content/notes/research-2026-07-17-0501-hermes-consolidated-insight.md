---
_slug: research-2026-07-17-0501-hermes-consolidated-insight
_vault_path: research/2026-07-17-0501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- saturation
- cron-cadence
source: multi
created: '2026-07-17'
confidence: high
title: 飽和確認第三輪：cron cadence 與真實新輸入脫節，且 `--mark-fed` exit-1 bug 已升至 multi-sample
type: research
status: seedling
updated: '2026-07-17'
---

# 飽和確認第三輪：cron cadence 與真實新輸入脫節，且 `--mark-fed` exit-1 bug 已升至 multi-sample

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

今日 00:00 與 05:01 連續兩輪 cron 命中同樣 4 篇 fed_count=3 筆記、無新 theme 可產出。差別在於這次可以把兩個累積中的弱點升級成正式 theme：(1) cron 觸發頻率（5h 一輪）vs 真實新輸入（近一週無新研究筆記）之間的脫節；(2) `--mark-fed` 在空 batch 時回 exit 1 的假陽性 bug，今日樣本已累積到第三輪。

## Cross-Cutting Theme 1: cron cadence 5h 是浪費，沒有新輸入時應該跳過

**支援筆記**: 2026-07-17-0000-hermes-consolidated-insight（自身前輪）, 2026-07-16-2306-hermes-consolidated-insight（首輪 gate runtime evidence）, 本次 0501 觀測

00:00 那篇 Theme 1 已指出「飽和訊號」並建議「暫停每日 cron 直到有新研究筆記入庫」。但那只是降頻建議，沒量化損失。今天 05:01 又跑一次的事實顯示：**實際 cron 仍以預設週期（看 prompt 為 5h 一次）運行，並未消化 00:00 的建議**。換言之，consolidator 自己產出的「暫停 cron」建議沒有任何執行回路把它接上 cron 排程本身——這是典型的 **prose-level recommendation 沒有閉環**。

00:00 → 05:01 兩個小時視窗內：
- 兩次 cron 都消耗 LLM call
- 兩次都產出內容近乎相同的 insight note
- 兩次都讓 `--mark-fed` 在空 batch 時回 exit 1
- 真正可執行的動作是「沒事」

這比單純的飽和更深一層：**prose 飽和 ≠ 系統飽和**。系統仍在每輪強行做事，prose 已說「無事可做」三輪。

**可行動下一步**:
1. 修改 cron 入口（包一個 wrapper 或在 `consolidate_memory.py` 加 `--auto-skip` flag）：先跑 `--status`，若 `--status` 顯示 `Unconsolidated (after redundant-skip): 0` 且自上次 `fed_at` 不到 24h，直接 exit 0 並寫一行到 cron log，不進 LLM。
2. 把「prose 建議 cron 降頻」這件事本身寫成一個閉環 token——consolidator 產出的 `confidence: low` + 「無新 insight」連續 3 次時，自動在 `~/.hermes/state/cron-caden ce.json` 寫下一筆 `recommended_skip_until` 給 cron wrapper 讀。
3. 不需要修改 consolidate_memory.py 的核心邏輯——只需要在 cron 那一層加 guard，這樣飽和判定本身仍由 consolidator 產出，但實際執行被 cron 抑制。

## Cross-Cutting Theme 2: `--mark-fed` 空 batch 回 exit 1 已升至 multi-sample bug

**支援筆記**: 2026-07-16-2306-hermes-consolidated-insight（首個樣本）, 本次 0501 觀測 + 剛剛 00:00 的隱性樣本（檔案存在 = 上一輪 `--mark-fed` 沒死但 stdout 應出現「（沒有可標記的筆記）」）

2306 那篇 Theme 2 把 `--mark-fed` 空 batch → exit 1 列為「弱點 / 假陽性告警」，信心 medium。今日實測：
```
$ python3 consolidate_memory.py --mark-fed
（沒有可標記的筆記）
EXIT=1
```
且 cron log 路徑（從 00:00 與 0501 兩份 insight note 都被產出來推斷）並未因 exit 1 中斷——也就是說 **bug 是真實的告警噪音**，但目前沒有監控在聽。三輪獨立樣本（2306、0000、0501）足以把信心從 medium 升到 high，且把這條從「未來會稀釋告警」升為「現在就在稀釋告警」。

更深一層：這個 bug 是 **honest skip pattern 的副作用**。當 consolidator 學會辨識空集合並誠實記錄，它就更頻繁地踩到 `--mark-fed` 空 batch 路徑——bug 與改進同時發生且耦合。

**可行動下一步**:
1. 一行 patch：`consolidate_memory.py` line 243 將 `return 1` 改為 `return 0`。這是把 2306 那篇「短期」建議從 prose 升為程式碼——比起再寫一篇 insight，patch 本身有更高 signal-to-noise。
2. 跑 patch 後，用 `--mark-fed` 連續觸發 5 次驗證 stdout 變 `nothing to mark` + exit 0 的一致性。
3. 把這次 patch 視為「insight note → code change」閉環的第一個範例：consolidator 不只是寫 prose，它可以回頭把 prose 變成 cron 行為。如果這個循環跑得通，未來飽和判定、cron 降頻、降頻後恢復等都可以走同一條路徑。

## 為何這次沒有「跨筆記」新 theme

4 篇 06-09 筆記之間的 cross-cutting（階層化 / 蒸發 / 圖記憶 / 治理綁定）在前 3 次 consolidation 已窮盡，今日再寫同一批 theme 就是昨日 insight 的第四份複本——00:00 那篇已明確說過這點。本篇轉而把觀察對象從「筆記之間」轉到「consolidator 自己的產出 + 執行環境之間」，這是單純讀 4 篇 paper-digest 看不到、只有把多輪 cron 結果放在一起才浮現的模式。
