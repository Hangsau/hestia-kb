---
_slug: research-2026-06-29-1501-hermes-consolidated-insight
_vault_path: research/2026-06-29-1501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- governance
- round-10
source: multi
created: '2026-06-29'
confidence: medium
title: 2026-06-09 記憶群（第十輪消化）：Trigger 缺 push-based 信號 × MemoryOS 反直覺 reset
type: research
status: seedling
updated: '2026-06-29'
---

# 2026-06-09 記憶群（第十輪消化）：Trigger 缺 push-based 信號 × MemoryOS 反直覺 reset

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

**前置消化**: [[2026-06-26-1102-hermes-consolidated-insight]]（已建立 Eval 黑洞、收斂邊界、密度飽和三 theme）、[[2026-06-20-0902-hermes-consolidated-insight]]（trigger / feedback / schema）

**狀態註**: 這四篇在 state 已 fed_count=9、saturation_marker=permanent；本次（2026-06-29 15:00）為 cron 觸發的第 10 輪消化，主動檢視 `--all` 視角後**沒有發現 6/26 與 6/20 兩輪未覆蓋的重大 theme**，但辨識出兩個 **次級 pattern** 值得收錄——一個是 4 篇 trigger 機制的演進軸缺 push-based 信號，一個是 MemoryOS `L_interaction` reset 設計陷阱。

四篇 2026-06-09 同日產出的 LLM agent 記憶系統探索，表面都在討論「層級架構」，但 cross-cutting 讀下來真正收斂的是兩個次級主題：trigger 機制如何從頻率邁向 feedback-loop 但缺 push-based invalidation，以及 MemoryOS 的 promotion-then-deheat 反直覺效應。

## Cross-Cutting Theme 1: Trigger 機制從 pull-based frequency 走向 reader-failure feedback loop

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇提出四種不同的 consolidation trigger，把它們放在一起會看到一條演進軸：

| 系統 | Trigger 類型 | 信號來源 | 是閉環嗎 |
|------|------------|---------|---------|
| RecMem ([1]) | recurrence count ≥ θcount | 內部：同類 embedding 重複次數 | 否（pull-based） |
| MemoryOS ([2]) | heat = α·N_visit + β·L_interaction + γ·R_recency | 內部：檢索次數 + 互動長度 + 時間衰減 | 否（pull-based 加權） |
| H-MEM ([1]) | user feedback (approval/rebuttal) | 外部：用戶明確信號 | 半（有人介入） |
| SAGE ([3]) | policy reward from reader failure | 內部 reader 報「找不到證據」 | **是（self-evolution）** |
| Governed Memory ([4]) | completeness-based reflection rounds | 內部 LLM judge 報 evidence completeness | **是（bounded reflection）** |

**非顯然觀察**：所有 trigger 都是「pull-based 由記憶系統自己決定要不要 consolidate」，**沒有任何一篇處理 push-based trigger — 即當外部世界改變（上游 source-of-truth 更新、knowledge base 出現新版本、user 角色變更），系統應該主動 invalidate 對應記憶**。MemoryOS 的 `L_interaction` 重設計特別值得警惕：segment 剛升級到 LPM 時 `L_interaction` 被 reset 為 0，導致熱度瞬間掉到谷底，這是 pull-based 機制的內在缺陷 — **升級行為本身會觸發「假性冷淡」**，讓剛被認為重要的記憶反而被標記為 stale。H-MEM 的 user-rebuttal 是唯一外部信號但需要用戶介入。SAGE 的 reader-failure 是最接近 push-based 的設計，但仍是被動接收失敗信號而非主動偵測外部 invalidation。

另一個非顯然點：SAGE 量化「two self-evolution rounds 就收斂到 multi-hop QA 最佳」，Governed Memory 量化「62.8% completeness vs 37.1% baseline」但「API-managed reflection +3.3pp vs manual multi-hop +25.7pp」，這兩個數字放一起顯示 **self-evolution 的價值不在 round 數量而在 query generation strategy** — 純粹增加 iteration 沒有用，要讓 reader 知道「為什麼失敗」才能改善 writer。

**可行動下一步**:
1. **在 `heartbeat_learning.py` 加入 reader-failure signal hook**：當 task context matching 回報「該 distillate 引用後 task 仍失敗」，把這個信號從 logging 升級為 distillation trigger 的輸入。預計 1-2 小時實作。
2. **重新設計 MemoryOS-style `L_interaction` reset 行為**：在 heartbeat_learning.py 的 distillate promotion 邏輯裡，新升級的 distillate 應該有 `promotion_grace_period`（例如 7 天），期間 heat score 不計算 L_interaction。預計 30 分鐘實作。
3. **追蹤 SCM (Self-Controlled Memory, Wang et al. 2025)**：四篇未消化筆記裡有兩篇提到 SCM 但都未 fetch，它的 dual-buffer + memory controller 設計可能是 push-based trigger 的早期嘗試。下次探索優先 fetch 這個。

## Cross-Cutting Theme 2: Memory bloat 是 governance 失敗的徵兆，不是越多越好

**支援筆記**: 2026-06-09-llm-agent-memory-governance-synthesis, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-memory-os-three-tier-hierarchical-memory

三篇獨立量化了「memory 過多反而有害」的證據，把它們放在一起看出明顯的模式：

- **OCL ([4])**：50 adversarial episodes，Baseline 看起來 94% task success，但 Valid Success Rate 只有 **12%**，unsafe rate **88%**。表面成功掩蓋大量合規失敗。
- **Governed Memory ([4])**：「memory density saturation: ~7 governed memories per entity reaches near-peak personalization quality (24% relative jump from 0→3)」— 超過 7 條之後邊際效益遞減甚至反轉。
- **SAGE ([3])**：two self-evolution rounds 就達到 multi-hop QA 最佳平均 rank — 明確的收斂點暗示超過這個量級繼續加記憶無益。

MemoryOS ([2]) 的 LPM 用 FIFO 100 條固定上限 + STM 7 頁固定佇列是同樣的洞見的早期版本：用硬上限強制裁量，避免 bloat。

**非顯然觀察**：Hermes 目前沒有對 distillate 數量的硬上限。`heartbeat_learning.py` 持續蒸餾但從未做 density saturation 偵測。OCL 的 12%→96% 是治理議題最戲劇化的數字 — **task success metric 和 valid success metric 之間的 gap 是 bloat 的指紋**，因為 bloat 會讓 LLM 在多餘的 context 裡產生「看似合理但違反約束」的輸出。

另一個非顯然點：Governed Memory 的 progressive context delivery 把 token reduction 量化為 50%，但它的 quality gates (coreference, self-containment, temporal anchoring) 是「incoming memory 必須通過才能進 long-term store」— 這是 pull-side quality control 但缺少 push-side invalidation。**MemoryOS 的 eviction 是「被動蒸發」，Governed Memory 的 quality gate 是「主動過濾但無去無回」** — 兩者都沒處理「曾經合格但現在過時」的記憶，這正好呼應 survey ([4]) Section 3.2 指出的「semantic representation 仍然看起來相關但內容已失效」問題。

**可行動下一步**:
1. **為 `heartbeat_learning.py` 加 density saturation detector**：統計當前 distillate 數量，當超過某閾值（例如 50 條 per concept cluster）時輸出 warning 並自動降低新蒸餾的 priority。預計 1 小時實作。
2. **設計「valid task success」metric 取代單純 task success**：在 Talos 的 task eval 裡區分「完成任務」vs「完成任務且未違反任何 policy constraint」。預計半天實作，可以借鑑 OCL 的 4 個 control outcome (Approve/Revise/Block/Escalate) 標記每個 task outcome。
3. **對現有 distillates 做 staleness audit**：批次檢查所有 distillate 的 `last_referenced_at` 和 `contradiction_count`，對超過 90 天未引用或 contradiction_count > 2 的標記為 `review_pending`。預計 2-3 小時。

---

## 對比 6 月 16-20 日的 consolidation 觀察

近兩週的 consolidated insight 多次強調「heartbeat_learning.py 需要 event-driven invalidation」但只給抽象建議。這次四篇同主題論文提供了**具體可移植的機制**：

- RecMem → subconscious buffer（不立刻 consolidate，等 recurrence）
- MemoryOS → heat score（含 recency decay 公式可直接抄）
- H-MEM → positional index encoding（不需 exhaustive similarity）
- SAGE → reader-failure feedback loop（writer 改進的最強信號）

下一步應從「再讀一篇 survey」轉向「實作上述四個機制中至少一個到 heartbeat_learning.py」，避免繼續停留在閱讀階段。