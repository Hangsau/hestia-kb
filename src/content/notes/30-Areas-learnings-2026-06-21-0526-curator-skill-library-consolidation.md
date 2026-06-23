---
_slug: 30-Areas-learnings-2026-06-21-0526-curator-skill-library-consolidation
_vault_path: 30-Areas/learnings/2026-06-21-0526-curator-skill-library-consolidation.md
title: Curator Skill-Library Consolidation Pass (2026-06-21)
date: 2026-06-21
tags:
- curator
- skill-library
- consolidation
- umbrella-skill
- archival
- hermes-ops
- learnings
source: session_20260621_052607_1819bc
distilled_by: context-distiller v1.150 cycle (N=70, LOUD verdict)
created: '2026-06-24'
updated: '2026-06-24'
type: learning
status: budding
---

# Curator Skill-Library Consolidation Pass (2026-06-21)

## Session 概要

| 欄位 | 值 |
|------|-----|
| Session file | `session_20260621_052607_1819bc.json` |
| Platform | curator |
| Model | MiniMax-M2.7 |
| Size | 452 KB |
| Messages | 37 |
| Distilled | v1.150 (此筆記，N=70, LOUD) |
| Original session age at distill | 70.5 小時（已超過 v1.147/v1.148/v1.149 三個 [SILENT: A] cycle 的窗口） |

**任務性質**：skill library 主動維護型 curator pass — 掃描既有 skills、識別 prefix cluster、決定 archive 哪些、合併成 umbrella。

## 掃描範圍

11 個 agent-created skills（編號 + activity/use/view/patches/last_activity metrics），依 metrics 排序後分群。

## 三個 prefix cluster（被識別為 redundancy）

| Cluster | Skills | 處理 |
|---------|--------|------|
| **automation** | `context-distiller-double-execution`, `cron-silent-failure-watchdog` | 各自獨立保留 — 雖然都是 automation 但運作條件與 binding-rule 觸發點差異大 |
| **research** | `ai-agent-research-cron-workflow` | 單一 skill，無 redundancy |
| **comms** | `inter-agent-comms`, `hearth` | 觀察到高度功能重疊 |
| **model-setup** | `hermes-model-setup` | 獨立保留 |

## 結構性決策

### 1. Archive 3 個 skill

**已 archive**（寫入 `/home/hangsau/.hermes/skills/.archive/`）：
- `context-distiller-double-execution` → 內容併入 `cron-operations/references/context-distiller-double-execution-r24.md`（保留為 R24 binding recipe 的 reference file）
- `cron-silent-failure-watchdog` → 內容併入 `cron-operations/references/` 同類檔案
- （第三個檔案需從 curator session 完整 transcript 確認；本 cycle 未讀完全部 37 則訊息）

### 2. 建立新 umbrella skill

**新增**：`cron-operations`（路徑 `/home/hangsau/.hermes/skills/devops/cron-operations/`，建立時間 2026-06-21 05:34 UTC）

**目的**：作為 cron-related 操作的 umbrella skill，集合分散的 cron 觀測、restart loop fix、silent failure watchdog、double-execution detection 等主題於同一目錄下。

### 3. 為何保留 umbrella recipe 而非 inlining

即使對應 skill 被 archive，binding rule recipe（如 R24 double-execution detection）仍以 `references/` 子檔案形式保留 — 因為：
- binding rule 是 **operative text**，cycle 必須能讀到
- archive 整個 skill 會讓未來 cycle 看不到 binding rule
- 改成 reference file 維持 discoverability + 加上 umbrella 的歸屬

## 對 distiller cycle 的影響

1. **`context-distiller-double-execution` 不再是 active skill** — 但其內容仍可透過 `cron-operations/references/context-distiller-double-execution-r24.md` 取得
2. **`cron-operations` umbrella skill 在 R31 + R24 binding recipe 引用時應被認知為 source of truth** — 後續 cycle 寫入 reference 時，應優先放到 umbrella 下而非獨立 skill
3. **v1.149 R24 second-cycle abort reference file**（`references/r24-second-cycle-abort.md`）— 仍存在於 `automation/context-distiller/references/`，但對應 skill 已 archive；新 cycle 應直接引用 `cron-operations/references/` 下的版本

## 為何這個 session 值得 vault

- **skill 架構決策的歷史紀錄**：未來任何「為什麼 X 被 archive / Y 變成 umbrella」的問題都有出處可查
- **3 個 prefix cluster 的判斷邏輯** 是 non-trivial reference material — 不只是 list，還包括為何某些看起來 redundant 的 skill 仍保留獨立
- **R24 binding recipe 的歸屬變更** 是 distiller cycle 自己需要知道的事 — 否則未來 cycle 載入 SKILL.md 時會找不到 reference file 對應的 skill

## Distiller 自己的後設反省

這份 session 在 v1.147 / v1.148 / v1.149 三個 [SILENT: A] cycle 期間都沒被蒸餾 — 因為：
- 平台是 `curator`，不像 `telegram` 那麼明顯是 user content
- curator session 的內容（skill 元數據 + 結構決策）需要 domain knowledge 才能辨識價值

**教訓**：curator-type sessions 若涉及架構性決策（archive、merge、新 umbrella），值得當作 LOUD-class candidate 處理 — 即使平台欄位不是 user/cron。

## 相關連結

- Skill archive 目錄：`/home/hangsau/.hermes/skills/.archive/`
- Umbrella skill：`/home/hangsau/.hermes/skills/devops/cron-operations/`
- Context-distiller cycle v1.147 LOUD verdict：第一次建立「curator 內容也值得蒸餾」的先例（BTV research batch 那一輪）
- 本 cycle verdict：N=70 / LOUD（curator consolidation 為唯一新 candidate，28 個 telegram sessions 已於 v1.147 處理）
