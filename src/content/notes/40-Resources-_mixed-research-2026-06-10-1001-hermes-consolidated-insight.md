---
_slug: 40-Resources-_mixed-research-2026-06-10-1001-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-10-1001-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-10'
confidence: high
title: 2026-06-10 10:01 — 治理斷層主題：Proposal/Execution 分離是 WS-035 缺失的第四根支柱
updated: '2026-06-15'
type: research
status: budding
---

# 2026-06-10 10:01 — 治理斷層主題：Proposal/Execution 分離是 WS-035 缺失的第四根支柱

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

> 註：這 4 篇筆記已於 2026-06-10 02:01 被消化過一次，產出三 theme insight note（Event-Driven、Reader-Writer、Structured）。本次 cron 觸發時 `consolidate_memory.py` 報告 0 篇未消化（狀態檔一致）。本文不重複前次的三 theme，**只補一個當時沒被獨立成 theme、但回頭看應該是 theme 級別的橫切模式：執行斷層（Execution Boundary）**——它把前次三 theme 串成同一個架構論點，且對 WS-035 的 `PolicyInterceptor` 有直接缺口指出。

## Cross-Cutting Theme 1: Proposal 與 Execution 之間必須有顯式 Governance Layer

**支援筆記**: llm-agent-memory-governance-synthesis（OCL 2606.04306 主源）、sage、memory-os（3 篇，high confidence）

這是前次 insight note 沒獨立出來的模式。OCL 的 50 個 adversarial episodes 給出最直接的量化證據：

| Metric | Baseline | OCL (with governance layer) |
|--------|----------|-----|
| Success Rate | 94% | 96% |
| **Valid Success Rate** | **12%** | **96%** |
| **Unsafe Rate** | **88%** | **0%** |
| Executed Violations | 205 | 0 |

**核心 architectural principle**（OCL 原文）：
> "Deployment-grade agent systems should **separate proposal generation from environment-facing execution**."

**這個 principle 在另外兩篇以不同形式出現**：
- **SAGE**: Writer（propose graph mutations）與 Reader（execute queries）就是分離的，但「分離的失敗」會被反饋。SAGE 的 writer 雖然會自動 mutate graph，但 mutation 不直接 affect 外部 world state——這是隱式的 governance。
- **MemoryOS**: STM→MTM→LPM 的遷移不是「即寫即生效」——FIFO 佇列與 heat-based eviction 是**顯式的 staging layer**，每段遷移都有觸發條件（`Heat > τ`）。沒有 staging 就是 eager execution，正是 OCL 警告的失敗模式。

**Hermes 的現狀缺口**: WS-035 的 `PolicyInterceptor` 草案有 gate 概念，但**沒有 architectural separation between LLM proposal generation and tool call execution**。CUGA Layer 4（tool approval）已被探索筆記標記為 OCL 的同位素——但實際 CUGA 與 OCL 都還沒被 integrate 進 Hermes。`heartbeat_learning.py` 的 distillate writer 也不區分「propose distillate」與「commit distillate to L2」——直接寫入，這是 eager execution 的典型反模式。

**可行動下一步**:
1. 在 `heartbeat_learning.py` 加入 `proposed_distillates/` staging 目錄：distillation 完成後不直接寫入 MEMORY.md，先放 staging 帶 `proposed_at` 與 `evidence_refs`。
2. 觸發 commit 的條件：累積 ≥ 2 個 evidence refs（呼應 RecMem 的 θcount=5 但門檻較低）+ heat score > 0（被任何 task context 引用過）。
3. WS-035 修正清單：把 `PolicyInterceptor` 從「事後 audit log」改為「pre-execution gate」，所有 tool call 必須經過 `πgate` 與 `πrole` 兩道 check 才允許執行——這直接對應 OCL 的四個 policy components。
4. 量化目標：對齊 OCL 的 205→0 unsafe execution reduction 指標；Hermes 的 proxy 是「`PolicyInterceptor` 介入後被 block 的 high-risk tool call 數 / 總 tool call 數」。

## Cross-Cutting Theme 2: 「冷知識」訊號必須來自 Reader 而非時間

**支援筆記**: memory-os、sage、hmem-recmem（3 篇，high confidence）

前次 insight Theme 2 已提到「Reader-Writer Feedback 閉環」，但具體**「什麼算冷」**沒有收斂。三篇給出三種不同但可融合的 cold signal：

- **MemoryOS**：`Heat = α·N_visit + β·L_interaction + γ·R_recency < τ` → 蒸發。N_visit=0 是冷訊號的硬指標。
- **SAGE**：Reader 找不到足夠證據 → 反饋「圖中缺少什麼結構」→ 該路徑上的 entity 自動變 cold candidate。**冷訊號是結構性而非頻率性**。
- **H-MEM**：user rebuttal 直接 decay memory weight——**最強冷訊號是 user explicit signal**。

**這三種 cold signal 構成一個優先級層級**（從最強到最弱）：
1. **User rebuttal**（H-MEM）—— human-in-the-loop，最權威
2. **Structural failure**（SAGE）—— reader 端結構性失敗，反饋給 writer
3. **Zero visit + recency**（MemoryOS）—— 純系統觀測，最弱但最自動化

**前次 insight 把這三種都歸到「Event-Driven」theme，但實際上 event 的 source 不同**（user / reader / system）——這是更細的 sub-classification。把優先級層級化才能決定 conflict 時誰 win。

**可行動下一步**:
1. 在 `heartbeat_learning.py` 的 `cold_distillate_detector`（前次 Theme 2 next step #1）中加入優先級：
   - `priority_1 = user_rebuttal_in_log`（直接 invalidate）
   - `priority_2 = reader_failure_signal_30d > 0`（標記為 structural_cold，下個 evolution round 重蒸餾）
   - `priority_3 = heat_score < threshold AND age > 60d`（passive decay，僅在無 priority 1/2 時觸發）
2. Conflict resolution：priority_1 > priority_2 > priority_3，priority 1 永遠覆蓋 priority 3。
3. 把這三層 cold signal 的 log 寫到 `drift_events.jsonl`——這個檔案同時是 OCL 的 `πaudit` 與 SAGE 的 self-evolution training signal 的最小可行實作。

---

## 為何這次補 theme 而非重寫

前次 02:01 的 insight note 完整覆蓋了 Event-Driven、Reader-Writer、Structured 三 theme，且每個 theme 都有 3-4 篇引證，confidence high。**重寫會稀釋前次的 effort**。本次只補兩個**前次沒獨立成 theme 但實際應該是 theme** 的橫切模式：Execution Boundary（最關鍵，因為它直接命中 WS-035 的 `PolicyInterceptor` 設計缺口）與 Cold Signal 優先級（對 Theme 2 提供 sub-classification）。

如果之後要 merge 進前次 insight note，建議把這兩個 theme 加在「三 theme 交集」段落之前，標題改為「**五個 Cross-Cutting Theme**」——Execution Boundary 是「where/who decides」、Cold Signal 是「how to weight events」，加上原本的 when（Event-Driven）、who learns（Reader-Writer）、what format（Structured）就構成完整的新典範語義空間。
