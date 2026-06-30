---
_slug: research-2026-07-01-0401-hermes-consolidated-insight
_vault_path: research/2026-07-01-0401-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- drift-penalty
- ws-035
source: multi
created: '2026-07-01'
confidence: high
title: 2026-06-09 記憶系統四篇綜合：未組合的四大軸線 + Reader 失效信號為通用缺失原語
type: research
status: seedling
updated: '2026-07-01'
---

# 2026-06-09 記憶系統四篇綜合：未組合的四大軸線 + Reader 失效信號為通用缺失原語

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇同日記的記憶系統探索，表面都在談「layered / hierarchical / triggered」記憶架構，但放在一起才看到一個共同缺口：**四個正交的設計軸線在所有論文中都只解決了 1-2 個，沒有一篇閉環；Hermes 目前連一個都沒閉環**。

## Cross-Cutting Theme 1: 四大正交軸線被各家獨立解決，Hermes 卻是「全平面」

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance

把四篇的設計焦點拆開，可以歸納出四條獨立軸線：

| 軸線 | 問題 | 誰解了 |
|------|------|-------|
| **結構** (how to organize) | 純向量檢索不夠，要怎麼分層/分圖？ | H-MEM (positional index, 4 層)、MemoryOS (segmented paging, 3 層)、SAGE (entity-relation graph) |
| **時機** (when to write/promote/evict) | 不是每個 interaction 都該 consolidation | RecMem (recurrence count ≥ 5)、MemoryOS (heat score ≥ 5) |
| **反饋** (reader → writer) | 讀取端失敗時，寫入端如何被告知？ | SAGE (writer-reader self-evolution)、H-MEM (user rebuttal → decay)、Governed Memory (bounded reflection rounds) |
| **治理** (organizational constraint) | 誰能寫誰能讀，schema 怎麼強制？ | OCL (proposal-execution separation)、Governed Memory (schema enforcement, dual memory) |

**核心觀察**：RecMem 解了 timing 沒解 structure；H-MEM 解了 structure + 粗略 feedback 但沒解 governance；MemoryOS 是唯一同時解 structure + timing 的，但它的 feedback 只有 heat score（隱式），沒有顯式的 reader failure channel；SAGE 解了 structure + feedback，但 timing 完全靠 policy 學；Governed Memory 解了 governance + feedback（reflection rounds）但沒解 timing。

**Hermes 現狀**：`heartbeat_learning.py` 目前的 distillate 流程 = 一個純粹的 eager write path，**四個軸線都沒解**——沒有結構分層（flat distillate list）、沒有時機觸發（每個 distillate 都進 LTM）、沒有反饋（reader 不報告 stale）、沒有治理（沒有人/模組邊界）。筆記 4 (llm-agent-memory-governance) 的 Storage→Reflection→Experience 框架明確指出，目前 distillate 是 Reflection 層，卻在宣稱解 Experience 層的問題——這個定位錯位本身就證明軸線沒分清楚。

**可行動下一步**：
1. 在 `heartbeat_learning.py` 加一個 `MemoryAxes` enum/結構，把這四個軸線變成可獨立開關的 feature flag（不要試圖一次寫完整個 OS）
2. 第一個要實作的軸線是 **反饋**（最便宜、改動最小）：在 distillate schema 加 `last_reader_signal: {matched, mismatched, missing}`，由 task context matching 在每次檢索時回填——這一個改動就能讓 H-MEM 風格的 user rebuttal 機制變成自動的、read-time 的
3. **不要**先做結構（segment / layer 化）——那是最大的改動，應該在 feedback 通道穩定後再做

信心：**high**（四篇筆記全部交叉驗證）

---

## Cross-Cutting Theme 2: Reader-side failure signal 是各家隱藏的通用原語，Hermes 完全缺

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance

每個有效方案的底層都有一個 reader-side observation channel：

- **SAGE** 最顯式：reader 找不到足夠證據 → 直接反饋給 writer policy → 下個 evolution round 補寫入
- **Governed Memory** 用 reflection-bounded retrieval：每 round LLM judge evidence completeness → 若 incomplete 則生 follow-up queries（+25.7pp vs baseline，遠超純 round count 的 +3.3pp）
- **H-MEM** 用 user rebuttal 當作 read-time 失效信號（粗略但有效）
- **MemoryOS** 的 heat score `N_visit` 本質就是 read counter——沒有讀過就驅逐
- **RecMem** 反過來用：reader 沒找到 ≥ 5 個相似就不 consolidation（隱性 reader gating）

**核心觀察**：這個 reader→writer 信號是**通用原語**，不是任何一篇的專利。但單看任何一篇都不會這樣歸納——只會覺得「H-MEM 是階層式」、「SAGE 是 self-evolution」。把四篇疊起來才看到：**所有表現好的系統都有一條從 reader 觀察寫回 writer 的信號線**。

**Hermes 現狀**：`heartbeat_learning.py` 沒有這條線。`system-map` 提到的「30 skills 無 domain」問題就是缺 reader signal 的後遺症——沒有人告訴 writer「這 skill 從未被讀過」。

**可行動下一步**：
1. 在 distillate / skill / segment 三層都加 `read_signals` 欄位：`{match_count, last_match_at, miss_count, miss_context_hash}`
2. 在每次 task context matching 後，無論 hit/miss 都寫入這欄位（miss 才是最有價值的信號）
3. 設定 `miss_count > N` 的 threshold，觸發「蒸餾候選」（不一定直接刪除，而是 flag 為需要重新生成或合併）
4. 預期 30 天內就能從 `read_signals` 看到哪些 distillate 是「cold knowledge」——這比 `last_accessed` timestamp 更有資訊量

信心：**high**（四篇交叉驗證）

---

## Cross-Cutting Theme 3: 「5-7」記憶飽和點的非巧合收斂

**支援筆記**: memory-os, llm-agent-memory-governance（recmem 間接支援）

三個獨立的設計選擇落在相近的數字上：

| 系統 | 飽和/容量參數 | 值 |
|------|--------------|-----|
| MemoryOS | STM page 數上限 | 7 |
| MemoryOS | LPM User KB FIFO | 100（但 persona 演化建議 ~7 條/實體） |
| RecMem | θcount recurrence threshold | 5（默認） |
| Governed Memory | governed memories per entity 飽和點 | ~7 |
| H-MEM | 階層層數 | 4（ablation 確認最優） |

**核心觀察**：4-7 這個範圍反覆出現，對應認知科學的 Miller's Law (7±2 working memory items)。這不是各家隨便選的——是經驗收斂到 cognitive science 的 working memory bound。

**對 Hermes 的含義**：Hermes 對單一 topic 的 distillate 沒有上限。這違反了飽和點經驗：超過 ~7 條/主題後，個人化品質的邊際增益歸零，新增的 distillate 反而稀釋 retrieval precision。

**可行動下一步**：
1. 盤點 `~/obsidian-vault/research/` 內每個 topic 的 distillate 數（用 tag 或 frontmatter 聚合）
2. 對超過 7 條的 topic 標記為 `oversaturated`，在下次 consolidation 時觸發 merge / supersede 流程
3. 在 `heartbeat_learning.py` 的寫入端加 soft cap：同一 topic 超過 7 條時，新寫入需先通過「是否真的不是既有 distillate 的變體」檢查

信心：**medium**（三篇支援，數字相近但不完全一致；含推測成分是飽和點對 Hermes 是否通用——LoCoMo 是 social dialogue，Hermes 是 technical/research 場景，可能飽和點不同）

---

## 未列入但值得 follow-up 的非顯然點

- **MemoryOS 的 90 維度 User Traits** vs **Hermes 的隱式偏好**——90 維度可能過度工程化，但 Hermes 目前連 explicit 的偏好表示都沒有，是個 0→1 的缺口
- **H-MEM 的位置索引可移植到 Hermes skills**（triggers → actions → verifications）——這在 hmem-recmem 筆記裡已提，但放在這裡的觀察是：skills 也是 hierarchical routing，position index 不只能用在記憶，也適用於所有 hierarchical state
- **OCL 的 12% valid success rate**：96% surface success 藏 88% unsafe。Hermes 的工具調用目前完全沒測過 valid success rate——建議在下次 audit 加這個 metric