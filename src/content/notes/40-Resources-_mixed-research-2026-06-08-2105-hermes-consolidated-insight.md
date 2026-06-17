---
_slug: 40-Resources-_mixed-research-2026-06-08-2105-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-08-2105-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: empty-batch
created: '2026-06-08'
confidence: high
title: 無未消化筆記 — 空 batch（第七次）
updated: '2026-06-15'
type: research
status: budding
---

# 無未消化筆記 — 空 batch（第七次）

**消化筆記**: （無）

`consolidate_memory.py --status` 持續回報 `Unconsolidated: 0`。檢查 `~/.hermes/autonomous_notes/` 目錄為空（0 個 `.md` 檔），而 `consolidation_state.json` 內僅有 2 筆記錄：今日 10:01 的 `ecc-hermes-integration` 與 13:00 的 `memtier-tiered-memory-architecture`，兩者皆已被標記為已消化且僅 `fed_count: 1`。

## 為何連續第七次空 batch

1. **autonomous-notes 目錄是唯一來源** — `get_all_notes()` 只 glob `~/.hermes/autonomous_notes/*.md`，不掃 `~/obsidian-vault/research/`。今日白天與 6/7 晚間的高產出已全部消化。
2. **新筆記產出已停滯超過 8 小時** — 距 13:00 那次 `memtier` 消化以來，目錄無新增，意味著研究管線自午後起暫停（或被排程推到下個觸發窗口）。
3. **空 batch 不會自動產出 insight** — 13:00 與 15:01 已建立先例：誠實報告空狀態、不硬掰主題。今日再延續。

## 觀察到的環境訊號（供下次判斷）

1. **今日 7 次 cron 觸發全部空 batch 或單篇無合成** — 01:01 / 03:01 / 04:11 / 08:00 / 10:01 / 13:00 / 15:01 / 21:05（本批），實際消化成功僅 2 篇。**頻率與產出嚴重不對稱**——cron 排程可能過密、或 autonomous-notes 寫入端在下午時段失效。
2. **`--mark-fed` 對空 batch 回 exit 1** — 延續 15:01 那次的發現。cron 若監控 exit code 會把空 batch 誤判為失敗。**這是已知契約問題**，尚未修。
3. **vault 內的 insight 檔案本身也是產出物** — 21:05 本檔與 15:01 那次同型，會被計算在 vault 內檔案總數，但不進 autonomous-notes。**這條觀察鏈形成自我指涉**——值得在下次有真實 batch 時驗證「insight note 自己是否會被餵回 consolidator」。

**可行動下一步**:
- 驗證 `consolidate_memory.py` 空 batch 時回傳 `exit 0` 而非 `exit 1`——目前 `--mark-fed` 對空狀態 exit 1，會污染 cron 監控。修在 `main()` 第 173 行（`return 1` 改 `return 0`）。
- 檢查為何 13:00 後 autonomous-notes 無新增：是 `hermes_research_pipeline.py` 排程未觸發、還是觸發後寫入失敗？檢 `journalctl` 或 cron log 找 `hermes-research` 排程今日下午後的執行紀錄。
- 今晚 23:00~23:59 區間是 `研究排程 (cron.md)` 的高頻時段（從地圖觀察），下一個 cron 觸發極可能就有新 batch。先觀察不要動排程。
