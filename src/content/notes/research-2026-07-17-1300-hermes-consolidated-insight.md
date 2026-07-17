---
_slug: research-2026-07-17-1300-hermes-consolidated-insight
_vault_path: research/2026-07-17-1300-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- sentinel
- pipeline-stagnation
source: multi
created: '2026-07-17'
confidence: high
title: 2026-07-17 13:00 — 連續空轉第 2 天：管線飽和的時間序列訊號
type: research
status: seedling
updated: '2026-07-17'
---

# 2026-07-17 13:00 — 連續空轉第 2 天：管線飽和的時間序列訊號

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

第二輪連續觀察到同一現象：`consolidate_memory.py --status` 仍回報這 4 筆 `fed_count=3`、最後 fed_at 為 2026-07-16T10:03。`--no-skip-redundant` 強制重讀也只回同樣的 4 篇 — 與 2026-07-17 07:00 / 2026-07-17 00:00 兩輪 cron 觀察到完全相同的狀態。

跨主題連結在第 1-3 次消化已窮盡；本輪真正的素材是「**連續 cron 週期觀察到管線飽和**」這個 meta 訊號本身 — 它的時間維度第一次有意義地累積起來。

## Cross-Cutting Theme 1: 連續 N 天同樣 4 篇被拒 = 真正的「輸入枯竭」哨兵

**支援筆記**: `2026-07-17-0000-hermes-consolidated-insight.md`, `2026-07-17-0700-hermes-consolidated-insight.md`, 加上 `consolidate_memory.py --status` 回報的 4 篇 06-09 歷史筆記作為餵食飽和的證據

**分析**: 單輪的「4 篇 redundant」只是飽和；**兩輪以上**同樣的 4 篇被拒絕，訊號強度從「這批消化完了」升級成「**整個未消化池已經 N 天沒有新成員**」。這個時間序列才是管線真正想要的監控目標：
- 第 1 輪（同 24 小時內）：飽和
- 第 2 輪（連續 2 天）：開始值得當哨兵事件
- 第 3+ 輪：應該觸發「研究輸入枯竭」警報，需要人為介入拉新素材

但目前的 `consolidate_memory.py` **沒有跨輪次的狀態記憶** — 每次 `--status` 都是當下快照，無法區分「剛飽和」vs「已飽和 5 天」。這是工具的盲點。

**可行動下一步**:
1. 在 `consolidate_memory.py` 加一個簡單的 `pipeline_state.json`（放 `~/.hermes/state/`），紀錄「上次觀察到非空未消化池的時間」。cron 比對該時間戳，超過 7 天就在 log 打 WARN。
2. 短期不必寫新模組 — 直接在 insight note 的 frontmatter 加 `stagnation_days: N` 欄位，由 cron 自己計算並寫入，比外掛 state file 更省事。

## Cross-Cutting Theme 2: 「飽和」與「過時」是兩個不同問題，目前只有一個開關

**支援筆記**: `2026-07-17-0000-hermes-consolidated-insight.md` 已提「superseded-by」概念、本輪 4 篇 06-09 筆記本體、`consolidate_memory.py --skip-redundant` 的 7 天/2 次閾值

**分析**: `--skip-redundant` 對待這 4 篇的方式是「**它被餵夠多次了所以跳過**」；但實際上這些 06-09 筆記**同時**是：
- (a) 已被消化飽和（fed_count=3）→ skip-redundant 正確處理
- (b) 主題已被 07-15 / 07-16 更新版研究取代 → 應該標 `superseded-by` 而非繼續留在未消化池

目前這兩種訊號被混在同一個開關下處理 — 都歸類為「skip」。結果是：就算有新的同主題舊筆記被 Hermes 撈回來，也會因為 fed_count 不夠而**先**被當作新素材餵一次，造成 insight 倒退回去講 5 週前的結論。`superseded` 標記會是「**先於** redundant」的更早攔截點。

**可行動下一步**:
1. 對這 4 篇 06-09 筆記加 frontmatter `superseded-by: [[2026-07-15-context-compaction-safety-governance]]` 或類似指向（實際指向要查 vault），讓它們直接從未消化池消失而非被反覆視為「還沒消化完」。
2. 給 `consolidate_memory.py` 加 `--respect-superseded` 旗標（預設 ON）：掃描 frontmatter 有 `superseded-by` 的筆記直接 skip，不計 fed_count。
3. 順手處理 vault 內其他可能有相同狀況的舊研究筆記 — 用 `search_files` 找 `created: <2026-06-*` 且未標 `superseded-by` 的研究筆記批次補標。

## Cross-Cutting Theme 3: 哨兵型 insight note 的格式開始有 pattern

**支援筆記**: `2026-07-17-0000-hermes-consolidated-insight.md`, `2026-07-17-0700-hermes-consolidated-insight.md`

**分析**: 兩天內已經產出 2 份結構幾乎一樣的「無 insight / 哨兵報告」型 insight note — 標題都明示「無可 consolidation」、都有 `confidence: low` 或 `confidence: high`（哨兵類）、都列出「為何本輪無事」。這個 pattern 正在 self-organize：當輸入為空時，**consolidation 工具自己演化出哨兵型產出格式**。

但缺一個東西：沒有「**連續哨兵次數**」欄位。如果未來再連續 5 天、10 天同樣哨兵，光看當天檔案很難看出「這是第幾天」。需要 frontmatter 加 `consecutive_empty_days` 自動計算。

**可行動下一步**:
1. 給哨兵型 insight note 加 frontmatter schema：
   ```yaml
   type: sentinel
   consecutive_empty_days: N
   last_non_empty_at: 2026-07-XX
   ```
   由 cron 自己計算（grep `research/` 內最近一份非哨兵 insight 的日期）。
2. 若 `consecutive_empty_days >= 7`，自動在 insight note 標題加 `[ALERT]` prefix，給 Obsidian 搜尋/過濾用。
3. 重新檢視 sentinel 是否應取代每日 cron — 若確定 N 天內不會有新筆記，把頻率從 daily 降到 weekly 更省 token。

---

**結論**: 本輪真正的 insight 是**管線本身的 meta 狀態在第二輪觀察下首次浮現**：連續冗餘已經是一個時間序列事件，而非單次飽和。`consolidate_memory.py` 缺跨輪次記憶、`superseded-by` 概念未實作、哨兵 note 缺結構化欄位 — 三個可立即動手的小改進，全部都不需要新研究素材。