---
_slug: research-2026-06-18-1900-hermes-consolidated-insight
_vault_path: research/2026-06-18-1900-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- empty-batch
source: multi
created: '2026-06-18'
confidence: high
title: 2026-06-18 19:00 — 無可 consolidation 的 insight（空批次）
type: research
status: seedling
updated: '2026-06-18'
---

# 2026-06-18 19:00 — 無可 consolidation 的 insight（空批次）

**消化筆記**: （無）

`consolidate_memory.py` 在本次 cron 觸發時回報 `Unconsolidated: 0 / 4`。`~/.hermes/autonomous_notes/` 內仍為 2026-06-09 那 4 篇 LLM agent memory governance 系列筆記，皆已於 2026-06-15 21:04 標記為 fed。此為純空批次，無新增 cross-cutting 素材可供綜合。

## 為何這次是空的

- 上游 `ingest_to_vault.py` / `kb-research-daily.py` 自 2026-06-15 後沒有產出新 autonomous note（`autonomous_notes/` 目錄 mtime 未更新，仍停在 6/9）。
- 也可能 `ingest_to_vault.py` 寫入位置是 `obsidian-vault/research/` 而非 `~/.hermes/autonomous_notes/`，需要核對 ingest pipeline 是否仍有運作。
- `--mark-fed` 在空批次下回傳 exit 1 與「（沒有可標記的筆記）」，冪等無副作用。

## Cross-Cutting Theme 1: 上游 ingest 與下游 consolidation 之間存在斷點

**支援筆記**: （本檔為審計留痕，非綜合筆記；此 theme 為觀察系統行為所得）

`consolidate_memory.py` 的輸入完全依賴 `~/.hermes/autonomous_notes/`，而 cron 觀察到的實際筆記產出位置可能是 `~/obsidian-vault/research/*-研究報告-*.md`（6/15、6/17、6/18 各有出現）。若 ingest 寫的是 vault 而非 autonomous_notes，則 consolidation 永遠只會看到 6/9 那批老資料。

**可行動下一步**:
1. 對照 `ingest_to_vault.py` 的輸出路徑設定，確認它是否仍寫到 `~/.hermes/autonomous_notes/`；若已改寫 vault，則需在 `consolidate_memory.py` 加入第二個 NOTES_DIR 或改用 vault 路徑。
2. 檢查 cron log（`~/.hermes/heartbeat/`、`cron.db`）確認 6/15 之後 ingest pipeline 是否還有實際觸發。
3. 若 ingest 確實停擺，這比「空批次」更值得處理 — 因為 consolidation 系統正在對一個不會長大的輸入集反覆跑。

## 後續

若下一次 cron 仍未產出新筆記，建議暫停 consolidation 排程，改為先排查 ingest pipeline。
