---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-hermes-session-learnings-20260522
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-hermes-session-learnings-20260522.md
title: Session Learnings 20260522
date: 2026-05-22
tags:
- session-review
- memory
- vault
- bug-pattern
aliases:
- Session Learnings 2026-05-22
created: '2026-05-22'
updated: '2026-06-15'
type: research
status: budding
---

# Session Learnings — 2026-05-22

## 發現的 Bug Pattern：LLM 自行估算未來日期

**問題**：vault `research/` 出現 5 個未來日期檔案（`2026-05-26`、`2026-05-27`、`2026-05-28`、`2026-05-29`），但主機時間是 `2026-05-22`。

**根因**：LLM 在自主探索時，**自己用相對日期估算未來日期**寫入檔名（不是 cron job bug）。54 個檔案受影響（三個目錄合計）。

**症狀**：
- 檔名含未來月份/日期
- mtime 是真實時間，但 filename date 是錯誤估算值

**修復方式**：`mv` rename 到當日日期（不改 mtime）。

**預防**：未來 heartbeat autonomous maintenance 遇到未來日期檔案應自動偵測並修正。

---

## 發現的 Workflow：autonomous_notes 清理機制

**問題**：`autonomous_notes/`（staging）有 133 個檔案，但 ingest 到 vault `explorations/` 後 source 未清除，導致 staging 堆積 26 個已入庫的舊檔。

**修復**：
1. `ingest_to_vault.py` 新增 `--rm-on-success` flag：只在 `DONE: new`（vault 無此內容）時刪 source；`DONE: append`（內容相似被 merge）則保留
2. Batch ingest 範例加入 `&& rm "$f"` 邏輯

**新 flag 用法**：
```bash
python3 ingest_to_vault.py --source "$f" --type exploration --rm-on-success
```

**注意**：`autonomous_notes/` 和 `explorations/` 的**檔名不直接對應**（ingest 會根據內容指紋 dedup/merge，並用中文標題重新命名）。相同內容會被視為同一筆記，而非新增。
