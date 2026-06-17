---
_slug: 40-Resources-_mixed-research-2026-06-09-0701-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-09-0701-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-09'
confidence: high
title: WS-035 drift penalty 收斂：四種觸發信號應該組裝成 ensemble，而不是二選一
updated: '2026-06-15'
type: research
status: budding
---

# WS-035 drift penalty 收斂：四種觸發信號應該組裝成 ensemble，而不是二選一

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇獨立探索全部收斂到 WS-035 drift penalty 的設計缺口，但**每一篇推薦了不同的觸發信號**：H-MEM 推 user feedback、RecMem 推 recurrence count、MemoryOS 推 heat score、SAGE 推 reader failure。把它們疊起來看才看得出來——這不是「選哪個」的問題，是「四個都是不同維度」的問題。

---

## Cross-Cutting Theme 1: 四種記憶淘汰信號其實是正交的，不是競爭的

**支援筆記**: hmem-recmem, memory-os-three-tier, sage-self-evolving, llm-agent-memory-governance-synthesis

**分析**:

四篇論文各自發明了一個 "trigger" 機制，但放在一起才看出來它們在**測量不同的東西**：

| 信號 | 來源 | 測量什麼 | 該系統 |
|------|------|---------|--------|
| **User feedback** (approve/rebuttal) | H-MEM | 這個蒸餾物「對人類有沒有用」 | H-MEM |
| **Recurrence count** (θcount≥5) | RecMem | 這個 pattern 出現得夠不夠多次 | RecMem |
| **Heat score** (visit × length × recency) | MemoryOS | 這個 segment 整體被引用得多熱 | MemoryOS |
| **Reader failure signal** (找不到證據) | SAGE | 這個蒸餾物「失敗過幾次」 | SAGE |

每個系統都把單一信號當作 SSOT（single source of truth），但每個信號都有盲點：
- 只用 user feedback → 沒有 user 在場時蒸餾物永遠不會被淘汰
- 只用 recurrence count → 一個新出現的重要但尚未重複的 pattern 會被誤刪
- 只用 heat score → 高度相關但已過時的舊事實會被保留（heat 仍在但內容已 stale）
- 只用 reader failure → 從未被查詢過的蒸餾物（可能很重要但任務沒觸發）會被當作 stale

把它們組合成 ensemble 才是正解：四個維度各打 0/1/2 分，加權成 single staleness score。**這是單篇論文看不到、只有四篇一起讀才浮現的模式。**

額外證據：Note 4 的 "From Storage to Experience" 論文 Section 3.2 提到「uniform time decay 的失效模式」——而這四個信號裡**沒有一個是純時間**的。MemoryOS 有 recency component 但被 visit 和 length 稀釋。這反過來確認：純時間的解（half-life=38d）就是錯的，必須是 multi-signal。

**可行動下一步**: 在 `heartbeat_learning.py` 新增 `staleness_score.py`，實作加權 ensemble：
- `score = 0.3·(1-user_approval) + 0.2·(1-recurrence_norm) + 0.3·(1-heat_norm) + 0.2·(reader_failure_rate)`
- 四個信號的 raw data 來源要分別 instrument 化：user approval 從 task post-mortem 收集、recurrence 從 distillate 寫入時的 cosine dedup 收集、heat 從 retrieval log 收集、reader failure 從 task context matching 的 confidence threshold 收集
- 預設 threshold = 0.7，超過就標記為 `potentially_stale`，下個 self-evolution round 觸發 reconciliation

---

## Cross-Cutting Theme 2: 「Reader failure signal」是 Hermes 唯一尚未 instrument 的維度

**支援筆記**: hmem-recmem, memory-os-three-tier, sage-self-evolving, llm-agent-memory-governance-synthesis

**分析**:

前 3 個信號（user feedback、recurrence、heat）在 Hermes 都可以**從現有日誌推導出來**——不用新增 instrumentation，只要 query `distillate_usage.log`、`memory_consolidation.log`、retrieval history 即可算出。

但 **reader failure signal 是 structural gap**：Hermes 目前沒有「task context 找不到足夠蒸餾物」這個事件的紀錄。當 task context matching 失敗（confidence < threshold）時，結果只有「找不到」這個 fallthrough，**沒有人知道失敗模式**——是某個特定蒸餾物應該存在但沒有？還是蒸餾物存在但 stale 了？還是 query 表徵不對？

SAGE 把這個信號當作 **self-evolution loop 的核心**：「Reader 的檢索失敗信號 → Writer 的改進目標」。這是 writer←reader 的 closed loop，其他三個系統（H-MEM、RecMem、MemoryOS）都沒有這個 loop——它們都是 open-loop 的內部觸發。

Note 4 隱含證實了這點：Governed Memory 的 silent quality degradation (#5 in Five structural challenges) 就是 reader failure signal 缺失的症狀。沒有反饋，品質退化是 silent 的。

對 Hermes 的直接意涵：instrumenting reader failure signal 比 instrumenting 任何其他三個都更有**結構性價值**——因為它能直接 close loop，讓 distillation trigger 變成 self-evolution 而不是手動觸發。

**可行動下一步**: 在 `heartbeat_learning.py` 的 retrieval path 加一個 `confidence_recorder.py`：
- 每次 task context matching 結束時，記錄 `(query, top_k_results, max_similarity, threshold_passed, fallback_used)`
- 如果 `max_similarity < 0.6` 或 `fallback_used=True` → 寫一條 `reader_failure_event` 到 `~/hermes/memory_archive/reader_failures/`
- 這個 event 帶上 timestamp + query embedding（用於後續 cluster 分析：「哪些類型的查詢」失敗最多次）
- 下個 digest cycle 把 reader failure event 做 cluster，把「常失敗但無蒸餾物覆蓋」的 cluster 標記為 distillation priority

---

## Cross-Cutting Theme 3: 「Reflection 層假裝是 Experience 層」是 WS-035 的 root cause

**支援筆記**: hmem-recmem, memory-os-three-tier, sage-self-evolving, llm-agent-memory-governance-synthesis

**分析**:

四篇筆記各自提到「heartbeat_learning.py 缺 cross-trajectory abstraction」，但**沒有一篇指出更深層的結構性問題**：目前的 distillate pipeline 從架構上就只是 Reflection 層，永遠到不了 Experience 層。

依 Note 4 的 "From Storage to Experience" 框架：

```
Storage      → 保留 raw trajectory（1:1 對應）
Reflection   → trajectory → 點評/corrective insights（已做）
Experience   → 跨 trajectory 抽象、MDL 壓縮、schema 化（未做）
```

WS-035 drift penalty 試圖在 Reflection 層上「修補」Experience 層才有的問題（stale knowledge, contradiction）。這是錯的 layer——你不能在 Reflection 層加 staleness score 就期待它表現得像 Experience 層。

正確的 fix 是 **新增第三條 pipeline**（Experience pipeline）：
- Trigger：reader failure cluster 累積到 N 個 OR recurrence + contradiction 同時發生
- 動作：把 N 個 reflection distillates 做 abstraction → schema 化的 experience rule
- 輸出：寫到 `~/hermes/memories/experiences/` 而不是 `~/hermes/memories/distillates/`
- 特性：Experience rule 比 distillate 更穩定（stale threshold 更高）、更結構化（typed schema）、更通用（cross-task）

四篇筆記全部隱含了這個 fix，但沒有一篇明說「加第三條 pipeline」。這是把它們並排才看得到的：H-MEM 是 schema 化（4 層 index encoding = experience schema）、RecMem 是 abstraction 時機（trigger 時機 = 何時升級到 experience）、MemoryOS 是熱度驅動的生命週期（segment → persona = experience layer）、SAGE 是閉環演化（reader failure → writer improvement = experience 的 self-evolution）。**四個系統其實都把 experience layer 當作頂層，只是各自用了不同名字。**

**可行動下一步**: 開一個 worktree `~/hermes/worktrees/ws-035-experience-pipeline`，做以下三件事：
1. 在 `heartbeat_learning.py` 同層新增 `experience_distiller.py`，input 是 N 個 distillates（cluster 觸發），output 是 typed experience rule
2. 設計 `ExperienceRule` schema：`(rule_id, condition_predicate, action_template, source_distillate_ids, conflict_count, success_count, created_at)`——這是 typed，不是 free-text
3. 把 `staleness_score.py`（Theme 1 的下一步）改成同時計算 distillate 和 experience rule 的 staleness，但 experience rule 的 decay rate 慢 5x（它代表 cross-task 真理，比單一 distillate 更穩定）

---

## 信心標示

- **Theme 1** (high): 4 篇全部命中，且每篇推薦不同信號是事實可驗證的（grep 表中已展示）
- **Theme 2** (high): SAGE 明說、Note 4 隱含證實、Hermes 現有日誌的實際狀態可由 code review 驗證
- **Theme 3** (medium): Framework 借用自 Note 4，三層架構的對應有推測成分，但「Reflection 假裝 Experience」這個診斷可以由 `heartbeat_learning.py` 的現有架構直接驗證
