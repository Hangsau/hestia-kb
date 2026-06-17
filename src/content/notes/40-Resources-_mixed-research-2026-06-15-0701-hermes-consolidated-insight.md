---
_slug: 40-Resources-_mixed-research-2026-06-15-0701-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-15-0701-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-systems
- ws-035
source: multi
created: '2026-06-15'
confidence: high
title: Memory 系統的觸發條件分類學 +「Reflection→Experience」過渡的三種實作路徑
updated: '2026-06-15'
type: research
status: budding
---

# Memory 系統的觸發條件分類學 +「Reflection→Experience」過渡的三種實作路徑

**消化筆記**:
- 2026-06-09-llm-agent-memory-governance-synthesis
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine

2026-06-09 同日產出的四篇 memory 探索構成一個**收斂系列**，全部指向 `heartbeat_learning.py` 的 WS-035 drift penalty 設計。把它們並排看，能看到兩條單篇都沒明說的跨主題脈絡。

## Cross-Cutting Theme 1: 四種記憶操作「觸發器」構成完整分類學

**支援筆記**: hmem-recmem, memory-os-three-tier, sage-self-evolving-graph, governance-synthesis

四篇筆記各自提出一種「什麼時候該做 memory 操作」的觸發機制，但**沒有一篇把它們並列比較**。並列後可看到一個清晰的二維分類：

| 系統 | 觸發器類型 | 訊號來源 | 時序 |
|------|-----------|---------|------|
| RecMem | 頻率（recurrence count） | 內容相似度 ≥ θsim | 被動（資料到達時） |
| H-MEM | 使用者回饋（rebuttal/approval） | user feedback loop | 被動（事件後） |
| MemoryOS | 熱度（heat = visit × length × recency） | 檢索行為累積 | 被動（持續累積） |
| SAGE | 失敗回饋（reader 找不到證據） | reader failure signal | 主動（缺什麼補什麼） |

兩個維度的差異有意義：
- **訊號來源**：內容相似度（純內部）↔ 使用者行為（外部）↔ 檢索行為（內部+隱性外部）↔ 系統失敗（自我觀察）
- **時序**：所有四種都**不是**在資料到達瞬間做事後判斷，而是延遲到某個累積信號出現

關鍵洞察：**這四種觸發器不是互斥選項，是互補層**。一個 production-grade memory system 應該至少組合兩種：頻率型觸發（避免 eager consolidation 的浪費）+ 失敗型觸發（捕捉「圖中缺少什麼」這種主動信號）。MemoryOS 的 heat score 已經是「頻率 + 內部使用」的合體，但**缺了失敗型觸發**——這是 SAGE 補上的缺口。

governance-synthesis 提到的「三階段框架」（Storage→Reflection→Experience）本質上也是觸發器演化：Storage 沒觸發（直接存），Reflection 有內容觸發（軌跡變化時），Experience 有跨軌跡衝突觸發。

**可行動下一步**:
修改 `heartbeat_learning.py` 的 drift penalty 公式，從單一時間衰減改為**雙信號加權**：
- `decay_score = exp(-Δt/μ) × (1 - failure_signal_weight)`
- `failure_signal_weight` 來自 reader 端的「找不到足夠 distillate 證據」事件計數
- 這樣「長期沒人引用」和「最近檢索失敗」會分別拉低 score，而不是被時間衰減一視同仁
- 對應 WS-035 的 issue 應該新增一個 metric：`drift_penalty_v2 = heat_score × failure_adjustment`

## Cross-Cutting Theme 2: 跨越「Reflection → Experience」鴻溝的三條具體路徑

**支援筆記**: governance-synthesis（提出鴻溝）, hmem-recmem（RecMem 的 semantic refinement）, memory-os-three-tier（LPM persona update）, sage-self-evolving-graph（self-evolution loop）

governance-synthesis 第一篇點出問題：現有系統（包括 Hermes 的 heartbeat_learning）卡在 Reflection 層（軌跡精煉），沒做到 Experience 層（跨軌跡歸納）。但它沒給出具體解法。

後三篇**各給出一條**跨越這條鴻溝的具體路徑：

1. **RecMem 的 semantic refinement 路線**：LLM abstraction 完成後，**再回到 raw interactions 萃取**被 abstraction 漏掉的 fine-grained facts。這是「先粗後細」的補救路徑。
2. **MemoryOS 的 LPM persona update 路線**：segment 達到 heat threshold 時，**直接更新結構化的 User Traits / User KB**。這是「結構化 schema 作為 abstraction target」路徑。
3. **SAGE 的 writer-reader self-evolution 路線**：reader 失敗 → 告訴 writer「圖中缺少什麼」→ writer 補上新結構。這是「閉環反饋」路徑。

三條路徑的根本差異是**abstraction 的目標格式**：
- RecMem：text 補回 text（仍是 un-structured）
- MemoryOS：text → typed 結構（schema-enforced）
- SAGE：text → 圖結構（entity-relation triple）

governance-synthesis 的 Survey Source 3（Governed Memory）也提到「schema-enforced memory」是 downstream 消費的關鍵，但沒有跟 MemoryOS / SAGE 的 abstraction target 對接起來。**跨四篇看，schema-enforced 是 Experience 層的最低可用品**——Mem0 的 key-value 太弱，MemoryOS 的 90 維度 trait 中等，SAGE 的 entity-relation triple 最豐富。

**可行動下一步**:
- 為 heartbeat_learning.py 的 distillate 設計**雙格式輸出**：`distillate_text`（給人/後續 LLM 讀）+ `distillate_triples`（給自動 retrieval 用，遵循 `[entity, relation, entity]` 格式）
- 對應的 `distillate.py` schema 應包含 `triples: List[Tuple[str, str, str]]` 欄位，schema 定義參考 SAGE 的 entity-relation triple 規範
- **不要**先做 90 維度 trait（MemoryOS 太重）也**不要**只做 key-value（Mem0 太弱），triple 是 sweet spot

## Cross-Cutting Theme 3: 架構分離是必要條件，但在三個不同抽象層次重複出現

**支援筆記**: governance-synthesis（OCL: proposal vs execution）, hmem-recmem（RecMem: subconscious vs episodic vs semantic）, sage-self-evolving-graph（writer vs reader）

**信心**: medium（只有 3 篇明確支持，但模式強烈）

三篇都提出某種「雙路徑」或「雙層」分離，但**抽象層次不同**：

| 系統 | 分離軸 | 高層 | 低層 |
|------|--------|------|------|
| OCL | proposal vs execution | 提議生成（LLM） | 環境執行（tool） |
| RecMem | consolidation trigger | subconscious（不 consolidate） | episodic/semantic（已 consolidate） |
| SAGE | memory lifecycle | writer（寫入） | reader（讀取） |

**這是同一個原則的三個尺度**：
- OCL 的尺度是**單次決策**（proposal→execute 的瞬間）
- RecMem 的尺度是**資料生命週期**（raw→processed 的時間軸）
- SAGE 的尺度是**系統閉環**（write→read→feedback 的循環）

**可行動下一步**:
- 在 `system-map` 中新增一個 cross-cutting 條目「Architectural Separation Principle」，引用這三個尺度，標明 WS-035 / Talos / heartbeat_learning 各自對應哪個尺度
- 這樣未來設計任何新 component 時，可以先問「這個 component 屬於哪個尺度的哪一層」，避免層次混淆
- 對應檔案路徑：`~/obsidian-vault/02-Areas/Hermes-Ops/architectural-separation-principle.md`（待建立）

## Cross-Cutting Theme 4: 共同的「反面假設」——所有四個系統都否定 eager consolidation

**支援筆記**: 全部四篇

**信心**: high（4 篇交叉驗證，但每篇只在自己的段落提到，沒有一篇把它作為主軸論述）

這個系列最強的隱性論點是：**「每個 interaction 都應該被 LLM 級 consolidation」是錯的**。但四篇用四種不同方式否證：

- RecMem：量化否定（87% token 節省）
- H-MEM：架構否定（hierarchical routing 不需要 flat similarity 的 eager index）
- MemoryOS：實作否定（heat-based eviction 取代 eager write）
- SAGE：機制否定（reader failure signal 取代 eager schema construction）
- governance-synthesis（Survey Source 3）：系統否定（governance routing 的 fast/full mode 區分）

**可行動下一步**:
- 在 `heartbeat_learning.py` 的 design doc 開頭加入「Anti-Eager-Consolidation Principle」段落，引用這五個來源
- 這比「值得研究」更實用：它直接給出「不要做 X」的設計約束，避免之後有人重提「每個 distillate 都應該立即 LLM 重寫」這種 eager 方案

---

## 系列完整性評估

這四篇構成的 series 已經收斂到一個明確的設計藍圖：
- **觸發器**：heat score + failure signal（Theme 1）
- **Abstraction 目標**：schema-enforced triples（Theme 2）
- **架構分離**：三個尺度（Theme 3）
- **底層原則**：否定 eager consolidation（Theme 4）

下一步應該是**整合**而非繼續探索：把這四篇的結論寫成一份 `WS-035-drift-penalty-design-v2.md` 設計文件，停止在同一個主題上 fetch 更多 paper。
