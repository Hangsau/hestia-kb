---
_slug: research-2026-06-23-1600-hermes-consolidated-insight
_vault_path: research/2026-06-23-1600-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- agent-memory
- drift-penalty
source: multi
created: '2026-06-23'
confidence: high
title: 四套記憶架構收斂到同一個設計原語：Event-Triggered State Transition
type: research
status: seedling
updated: '2026-06-23'
---

# 四套記憶架構收斂到同一個設計原語：Event-Triggered State Transition

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 同日探索的 LLM agent 記憶論文，表面上各自關注不同面向（H-MEM 的 hierarchical routing、RecMem 的 recurrence detection、MemoryOS 的 segment-paging、SAGE 的 graph self-evolution、Governed Memory 的 schema enforcement），但讀完放在一起看，它們**全部獨立收斂到同一個底層設計原語：event-triggered state transition**——也就是「不要在固定排程上做事，要等具體事件信號才動作」。這是單篇筆記自己沒說、但四篇放在一起才浮現的模式。

## Cross-Cutting Theme 1: 「何時觸發」比「怎麼儲存」才是真正的設計瓶頸

**支援筆記**: hmem-recmem (RecMem θcount + H-MEM user feedback), memory-os (Heat score > τ), sage-self-evolving (reader failure signal), llm-agent-memory-governance (semantic contradiction event + Storage→Reflection→Experience 的 task-typed trigger)

每篇論文都在回答同一個問題的變體：「新資料進來時，agent 應該立刻做事、等一會兒、還是不做？」但答案清一色是**事件驅動**：

| 論文 | 觸發事件 | 對應狀態轉換 |
|------|---------|------------|
| RecMem | `cos(si, sj) ≥ θsim` 累計 ≥ θcount | subconscious → episodic（consolidation） |
| H-MEM | user approval/rebuttal | memory weight 升降 |
| MemoryOS | `Heat = α·N_visit + β·L_interaction + γ·R_recency > τ` | MTM → LPM（promote）|
| MemoryOS | segment count > 200 | LPM heat-based eviction |
| SAGE | reader retrieval failure signal | writer → 補寫缺失鏈路 |
| Storage→Reflection→Experience | semantic conflict between trajectories | immediate staleness 標記 |
| Governed Memory | governance routing ambiguity | fast path → full path |

**為什麼這是真正的瓶頸**：當你想把這四套系統移植到 Hermes 的 heartbeat_learning.py 時，發現它們的「儲存格式」差異很大（hierarchical index vs segment-page vs graph triple vs dual open-set+schema），但**觸發條件的設計空間其實非常窄**——全部都在 [count, similarity, heat, contradiction, reader-failure] 這五個維度裡挑組合。

**可行動下一步**：
- 把 heartbeat_learning.py 的 `drift_penalty` 從「時間衰減 + 全量掃描」改寫成**事件累加器**：維護五個獨立 counter（recurrence_count, heat_score, last_contradiction_ts, last_reader_failure_ts, user_feedback_score），每個 distillate 的最終 confidence 是這五個信號的 fusion function
- 先在 vault 標一個小的 experiment 對象（例如 5 個 distillate），手動標記 6/9 之前觀察到的事件，驗證 fusion 是否能正確把 recurrent 但無矛盾的 distillate 留住、矛盾發生的 distillate 立即降權
- 不要再寫「time-based decay 是錯的」這種空泛結論——具體要做的：把現有 `decay_half_life=38d` 的計算邏輯**保留為 fallback**，只在 5 個事件 counter 全部沒動靜時才走它

信心：**high**（4 篇論文 × 5 個 trigger 機制交叉驗證，且這個 pattern 在 Hermes 內部已經被 CUGA、governance-routing 多處呼應）

## Cross-Cutting Theme 2: 雙軌記憶不是設計選擇，是資料物理的必然

**支援筆記**: hmem-recmem (subconscious raw embedding + episodic LLM summary), memory-os (STM FIFO + MTM segment + LPM persona), sage-self-evolving (writer 即時 append + reader 多輪查詢), llm-agent-memory-governance (open-set atomic facts + schema-enforced typed properties)

四套架構**全部**都有兩個並行的儲存軌：

| 系統 | 軌 A（保留原貌）| 軌 B（抽象後設）| 橋接機制 |
|------|--------------|--------------|---------|
| RecMem | subconscious（raw embedding） | semantic（atomic facts） | recurrence trigger → semantic refinement |
| MemoryOS | STM（page queue） | LPM（persona traits） | Heat > τ → promote + L_interaction reset |
| SAGE | writer appends to G_t 即時 | reader's calibrated target graph | reader failure → writer 補寫 |
| Governed Memory | open-set memory | schema-enforced memory | single extraction pass dual output |

**單篇筆記沒明說，但四篇放在一起才浮現**：
- 軌 A 一定是**低成本、無 LLM、可隨時丟**
- 軌 B 一定是**高成本、有結構、有 LLM**
- 兩個軌永遠不會合併成單一軌（RecMem 試過，發現 lossy compression 漏掉 fine-grained facts → 才加了 semantic refinement 這個反向補回機制）

這是**資料物理**決定的：軌 A 必須廉價才能 hold 住高 throughput（MemoryOS STM 7 pages fixed size；RecMem subconscious no LLM call）；軌 B 必須有結構才能讓下游 governance / CRM / LoCoMo QA 消費（schema enforcement 在 Governed Memory 是核心賣點）。

對 Hermes 來說，這意味著：
- **不要試圖用一個 vector store 同時做「未加工 distillate」和「結構化 schema」**——硬要做一定會 trade off 一邊（軌 A 變貴或軌 B 漏資訊）
- 目前 Hermes 的 `heartbeat_learning.py` 看起來只有一個 distillate 軌，這個雙軌缺口對應「為什麼 recurrent contradiction 偵測不到」（因為沒有 raw buffer 留著新事件來對照）

**可行動下一步**：
- 在 `heartbeat_learning.py` 加一個 **distillate-raw 暫存層**（sqlite table 或 jsonl，**無 LLM**），保留過去 90 天的原始 task output 與 distillate 來源 quote
- distillate 本體（已存在的）保留為軌 B，只動**結構欄位**（加 `source_raw_id` 外鍵指向軌 A）
- 寫一個 `detect_contradiction(distillate_B, raw_buffer_A_window=30d)` 函式——這正是 Storage→Reflection→Experience 框架中 cross-trajectory abstraction 的具體實作，也是 SAGE reader failure signal 在 Hermes 的具體實作
- 先用 vault 裡已有的 A-Mem、MemoryBank 案例做 unit test（cross-check：同一個 entity 在兩個 raw buffer 條目下，B 軌 distillate 是否能正確標記 contradiction）

信心：**high**（4 篇獨立論文全部收斂到雙軌，且每篇都明確解釋了「為什麼單軌會失敗」）

## Cross-Cutting Theme 3: 「Reader Failure Signal」是 Hermes 目前最大的未填補缺口

**支援筆記**: sage-self-evolving（核心賣點）, llm-agent-memory-governance（BEAM contradiction_resolution 指標）, hmem-recmem（recurrence count 是 reader-side 訊號）, memory-os（N_visit 是 reader-side 訊號）

SAGE 把「reader 找不到 → writer 補寫」做成顯式的 self-evolution loop。其他三篇沒有這樣明確的閉環，但**它們都有 reader-side 的計數器**：

- MemoryOS `N_visit` = reader 命中次數
- RecMem `θcount` = reader 端 recurrence detection 命中次數
- Governed Memory `governance routing precision 92%` = reader 分流的失敗率

把這四個數字放在一起看，浮現一個 Hermes 內部**到處都有「reader-side 計數」但沒有「reader-side 失敗回饋通道」**的系統性缺口：

- `heartbeat_learning.py` 的 `N_visit`（如果有）只影響 heat score，不會回頭告訴 writer「這個 distillate 已經 90 天沒人讀、可能是 stale 或 missing」
- `drift_penalty` 完全沒有 reader failure signal 輸入——只有時間衰減和偶然的 contradiction event
- `system-map` 的 30 個 skills 無 domain 問題，本質也是 skill registry 沒有「skill 沒有被 reader 命中過」的信號

**為什麼這是 cross-cutting 而不是單篇發現**：SAGE 論文自己點名這個是它的核心創新，但其他三篇的設計**雖然收集了同樣的數據，卻沒有閉環**。把這四篇放在一起才看出：reader failure signal 不是 SAGE 獨門絕活，是**所有成熟記憶系統的必備基礎設施**——只是其他論文把它埋在計數器裡沒拉出來。

**可行動下一步**：
- 在 `heartbeat_learning.py` 加一個 `reader_feedback_hook(retrieval_query, retrieved_distillates, downstream_success)` API：每次 task context 檢索 distillate 後，把 `downstream_success ∈ {hit, partial, miss}` 寫回每個命中的 distillate
- `miss` 與連續多次 `partial` 累積到閾值（例如 5 次）後，觸發一個 `candidate_stale_distillates` 集合
- 下一輪 distillation 觸發時，這個集合優先被重新蒸餾（不是直接刪除——SAGE 明確說 self-evolution 是 two rounds 才收斂）
- 短期先用 Telos/task tracking 的執行 log 模擬 reader feedback（task 完成度 + 用戶後續行為），不必等 telemetry 完整

信心：**medium**（4 篇都有相關機制，但只有 SAGE 明確建模閉環；其他三篇的計數器目前只是 dormant data，沒有實際接到 writer。推測成分存在於「這些 dormant 計數器接起來真的能 work」這一塊，但 SAGE 已經量化了 two rounds 收斂的證據）

---

## 為什麼這些 theme 對 Hermes 是 actionable

四篇論文都明確建議到 heartbeat_learning.py / WS-035 drift penalty，但單篇給的建議是**互補且不重疊**的：

- RecMem → recurrence trigger
- MemoryOS → heat score
- SAGE → reader failure signal
- Storage→Reflection→Experience → contradiction event

把它們當成「選一個來實作」是錯的。它們是**同一個 fusion function 的四個輸入維度**。Theme 1 把這個融合框架講清楚，Theme 2 解釋為什麼雙軌架構是必然，Theme 3 點出目前 Hermes 最缺的那一塊（reader feedback 閉環）。三個 theme 串起來就是一個完整的 v2 heartbeat_learning.py 設計藍圖，而不是四份各自獨立的 paper summary。

---

## 標記

本次消化完成後執行：
```
python3 /home/hangsau/.hermes/scripts/consolidate_memory.py --mark-fed
```