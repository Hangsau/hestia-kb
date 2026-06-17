---
_slug: 30-Areas-learnings-2026-05-18-Context-Distiller
_vault_path: 30-Areas/learnings/2026-05-18-Context-Distiller.md
title: Context Distiller 回顧｜2026-05-18
date: 2026-05-18
tags:
- learnings
- context-distiller
created: '2026-05-18'
updated: '2026-06-15'
type: learning
status: budding
---

# Context Distiller 回顧｜2026-05-18

## 本次複習範圍

- 4 場 user session + 5 場 cron session（May 17 22:00 ~ May 18 00:03）

---

## 新發現：Hearth Task 需要 PROPOSAL.md + PLAN.md 雙檔機制

**問題**：hearth task 只放 `PROPOSAL.md`，Talos 的 `hearth-gap-analysis` cron 不會主動偵測。導打從來沒有任務靠「放進 hearth pending」自動完成過。

**修復**：
- `PROPOSAL.md` = 提案內容（給人類看的摘要）
- `PLAN.md` = Talos 可以解析的執行計劃
- 需要處理的任務：同時要有 `PLAN.md`（格式合規）+ comms thread 通知（引起注意）

**相關**：`claude-hestia-comms` skill 已更新格式規則；commit `1278b17` 記錄在 `references/hearth-gap-analysis-20260517.md`

---

## 新發現：Ghost DONE Row 有兩種類型

INDEX DONE table 中「看起來 DONE 但實際無效」的記錄有兩種：

| 類型 | 診斷方式 | 處理 |
|------|----------|------|
| **Type A**：proposal 檔案根本不存在 | `ls proposals/<ws-id>*.md` 確認 | 從 `reports/` 復原或刪除 INDEX row |
| **Type B**：proposal 檔存在，但 STATUS block 是空表格（無資料列） | 需要 `tail -20` 才能發現 | 不是真的 ghost，但也不算有效 DONE record |

WS-006、WS-007 是 Type B 案例。`heartbeat-v2-autonomous-maintenance` skill 已 patch 進 `INDEX drift 模式識別` 段落。

---

## 新發現：self-evolving-research GitHub API 模式

從研究 cycle 學到：
- GitHub API 是 agent tooling 領域資訊的首選源（比 arXiv 有效）
- OTEL GenAI conventions 是 trace 格式的事實標準
- GitHub API 返回格式是 `{'items': [...]}` 不是純陣列（parse 時要小心 `items` key）

已寫入 `self-evolving-research/references/cron-research-workflow.md`

---

## 備註

- 其他 sessions（`231324`、`231212` 後半、`b48ea` 2309/2334）皆無新發現，session 自己回報了 `[SILENT]` 或「Nothing to save」
- 整體系統乾淨：EVOLVE 13 steps clean，proposals 無 drift，inbox 空
