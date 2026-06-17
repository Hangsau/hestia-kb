---
_slug: 40-Resources-_mixed-research-2026-06-12-0801-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-12-0801-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- governance
- feedback-loop
source: multi
created: '2026-06-12'
confidence: high
title: 2026-06-09 記憶架構四連擊的隱藏共識：時間衰減已死，回饋閉環當立
updated: '2026-06-15'
type: research
status: budding
---

# 2026-06-09 記憶架構四連擊的隱藏共識：時間衰減已死，回饋閉環當立

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 06-09 同日產出的探索筆記，表面上在談不同系統（H-MEM、RecMem、MemoryOS、SAGE、OCL、Governed Memory），底層卻收斂到同一個尚未被任何一篇明確說出口的判斷：**uniform time-based decay 已被業界集體判死，但取代它的「事件觸發」目前是碎片化的——四篇論文各自選了不同事件源，沒有人把它們組合成單一閉環**。這篇 insight 把這個分散的訊號接起來。

## Cross-Cutting Theme 1: 「事件觸發」是新的共識，但事件源分裂了

**支援筆記**: hmem-recmem, memory-os, sage, memory-governance-synthesis

四篇論文共同拒絕「每個 interaction 都 eager consolidation」（RecMem 87% token 浪費論據）、共同拒絕「純時間衰減」（2605.06716 Section 3.2 明確指出 semantic 看起來仍相關時知識已失效）。但它們各自挑選的事件源完全不同：

| 系統 | 事件源 | 觸發條件 |
|------|--------|----------|
| RecMem | 結構性 recurrence | `\|Ri\| ≥ θcount` (cosine ≥ 0.7 的鄰居數量) |
| H-MEM | 用戶反饋 | approval → strengthen weight, rebuttal → decay |
| MemoryOS | 混合熱度 | `Heat = α·N_visit + β·L_interaction + γ·R_recency` |
| SAGE | 檢索失敗 | Reader 找不到證據 → 反饋 Writer |
| OCL (2606.04306) | 約束違反 | proposal 撞到 πgate → revise/block/escalate |
| 2603.17787 | Quality gate 失敗 | coreference/self-containment/temporal anchoring score |

**非顯然的 pattern**：沒有一篇把這些事件源**並聯**起來。它們其實互補——recurrence（頻率）告訴你「這個值得留」、contradiction（語意衝突）告訴你「這個已過時」、retrieval failure（找不到）告訴你「結構有缺」、user feedback（人為）告訴你「這個不對」。但每篇只挑一個維度做觸發。

**對 Hermes 的含義**：`heartbeat_learning.py` 目前是純 time-decay（half-life=38d）+ semantic contradiction 的雙軌，但**這兩軌都沒有閉環信號回流到 distillation trigger**。WS-035 drift penalty 應該是一個**多源事件聚合器**，而不是單一 trigger 邏輯。

**可行動下一步**:
1. **本週內**：在 `heartbeat_learning.py` 加一個 `event_log.jsonl`，append-only 記錄四類事件：`{type: recurrence | contradiction | retrieval_miss | user_rebuttal, distillate_id, ts, signal}`。先收集資料，不改邏輯。
2. **下週**：寫一個 `drift_score(distillate) = w1·recency + w2·(1-recurrence_rate) + w3·contradiction_count + w4·retrieval_miss_rate` 的 prototype。權重先用 [0.4, 0.3, 0.2, 0.1] 啟動（recency 主導但不是唯一）。
3. **觀察期 2 週後**：對比新 score 與現有 half-life 排名的差異，量化「哪些 distillate 新方法會提前標 stale、哪些會延後」。

## Cross-Cutting Theme 2: 治理不是記憶的外掛，是記憶結構的回饋信號

**支援筆記**: sage, memory-governance-synthesis, hmem-recmem

SAGE 的核心 insight 是「**Graph as dynamic substrate, not static index**」——圖結構本身是 writer-reader 閉環的產物，不是預先定義的索引。2603.17787 提出 Dual Memory Model 強制 schema-enforced memory 與 open-set memory 並存，理由是「schema enforcement 讓記憶可被下游系統消費，否則就是孤島」。OCL 把四個 policy component（πrole/πgate/πescalate/πaudit）寫成「**所有 proposed decisions 都經過 constraint check + audit trail**」。

**非顯然的 pattern**：這三個系統都在做同一件事——**把 governance 從「輸出檢查」改寫成「記憶結構本身的生成規則」**。SAGE 的 reader-failure 不只是給 writer 看的 log，是 writer 改寫圖結構的輸入；2603.17787 的 schema 不只是 metadata，是 extraction 時的 typed output 約束；OCL 的 audit trail 不是 log，是下一次 replan 的 evidence。

反觀 Hermes 的現狀：
- `PolicyInterceptor` 設計是「在 tool call execution 前 pause + 檢查」——典型的 output-side governance
- `heartbeat_learning.py` 的 distillate 結構不帶 schema，是 free-form markdown
- 兩者**沒有交叉**——policy 不知道某個 distillate 已經被標 stale 過、distillate 不知道某個 tool call 被 block 過

**對 Hermes 的含義**：WS-035 + Talos PolicyInterceptor 應該共用一個 event bus，而不是兩條獨立 pipeline。Memory writes 應該被 policy 攔截（同樣的 πrole 規則），policy decisions 應該被 distillate 結構記住（schema 欄位）。

**可行動下一步**:
1. **立即**（不用寫 code）：在 obsidian-vault `02-Areas/Hermes-Ops/` 開一個 `governance-memory-bus-design.md`，列出目前 heartbeat_learning 與 PolicyInterceptor 各自有哪些 event type，標出重疊與缺口。
2. **1 週內**：在 `vault.db` 或 `distillates.jsonl` 加一個 `governance_events` 欄位（nullable JSON），暫時只是被動記錄，不主動觸發。
3. **2 週內**：找一個**具體案例**（過去某個 distillate 後來被證明錯誤、或某個 tool call 被 user 推翻）走完整個新 pipeline，確認 schema 設計足夠 capture 該案例的因果鏈。如果連一個回溯案例都 capture 不了，schema 設計失敗。

## 收尾觀察

四篇論文的 LoCoMo 結果是 noise（benchmark 飽和、baseline 各異），但有兩個**數字**值得單獨記住：
- **MemoryOS STM = 7 pages 固定長度** + **Governed Memory 7 memories/entity saturation** = 工作集大小有 ~7 的魔術數字
- **RecMem 87% token reduction** + **Governed Memory 50% token reduction（progressive delivery）** = 結構化帶來的 token 節省是 50-87% 級別

這兩個數字在 Hermes 沒有人驗證過。`obsidian-vault` 載入時的 context window 成本、heartbeat distillate 累積速度，可以用這兩個數字當 benchmark anchor。

**信心標示**: Theme 1 high（4 篇直接引用且互補），Theme 2 high（3 篇有顯式機制），魔術數字 low（純樣本巧合、單一觀察不足以驗證）。
