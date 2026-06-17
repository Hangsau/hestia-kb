---
_slug: 40-Resources-_mixed-research-2026-06-14-0500-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-14-0500-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- drift-penalty
- feedback-loops
source: multi
created: '2026-06-14'
confidence: high
title: 跨四篇 LLM Agent 記憶論文：drift penalty 缺少的半塊拼圖
updated: '2026-06-15'
type: research
status: budding
---

# 跨四篇 LLM Agent 記憶論文：drift penalty 缺少的半塊拼圖

**消化筆記**: 2026-06-09-llm-agent-memory-governance-synthesis, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine

四篇 2026-06-09 的自主探索筆記合在一起，暴露了一個所有 WS-035 drift penalty 設計共通的結構盲點：只有 SAGE 建構了 reader→writer 閉環，其他三套（MemoryOS heat、RecMem recurrence、H-MEM user feedback）都是**單向信號**——staleness 偵測天然是閉環問題，卻被當開環問題處理。

## Cross-Cutting Theme 1：Staleness 偵測被當開環問題處理（高信心）

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四套系統在 consolidation 觸發條件上有驚人收斂：

| 系統 | 寫入/淘汰觸發信號 | 信號方向 |
|------|---------------|--------|
| MemoryOS | `Heat = α·N_visit + β·L_interaction + γ·R_recency > τ` | write→record（heat 計進去，write policy 不讀回） |
| RecMem | `|Ri| ≥ θcount`（重複次數門檻） | write→record（recurrence 計進去，trigger 不讀回品質） |
| H-MEM | user rebuttal → memory weight decay | user→record（feedback 寫進去，routing 不讀回） |
| **SAGE** | **Reader 檢索失敗 → Writer 改進目標** | **reader→writer 閉環** |

前三套的本質都是「寫入時記錄一個信號，讀取時用這個信號排序/淘汰」——這是**開環**的：寫入決策與讀取品質完全解耦。SAGE 是唯一讓 reader 失敗信號反饋給 writer 的——「我找不到證據」直接成為「圖中缺少什麼」的目標函數。

對 Hermes 的直接意涵：heartbeat_learning.py 目前的 distillate lifecycle（寫入→recency decay→淘汰）就是開環的。drift penalty 算出來的分數只決定要不要淘汰這個 distillate，**從來不告訴 distillation trigger「哪類知識正在失效」**。所以新 distillate 會繼續用同樣的萃取方式產出同樣的失效模式，沒有學習。

**可行動下一步**：

在 `heartbeat_learning.py` 加入 `retrieval_miss_signal` 通道：
- 當 task context matching 連續 N 次（建議 N=3）未引用某 distillate 主題 cluster，回報一個 `cold_topic_signal(topic_embedding)` 給 distillation trigger
- distillation trigger 把 `cold_topic_signal` 列入下次新 distillate 的「應優先覆蓋」清單
- 預期效果：distillate 的寫入策略從「每次都萃取新東西」變成「有目標地修補 reader 失敗的區域」
- 預期工時：1-2 小時（修改 heartbeat_learning.py + 寫 unit test 模擬 reader 失敗）

## Cross-Cutting Theme 2：Heat-score 三元公式 `visit + interaction + recency` 被獨立重發明三次（高信心）

**支援筆記**: 2026-06-09-memory-os-three-tier-hierarchical-memory（明文公式）, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory（複用為「recurrence + similarity + recency」）, 2026-06-09-sage-self-evolving-graph-memory-engine（複用為「visit count + recency decay + reader signal」）

MemoryOS 給出明確公式 `Heat = α·N_visit + β·L_interaction + γ·R_recency`，其他三篇用不同詞彙複用同一個三元結構。**但每家用它做的控制決策不同**：

- MemoryOS：蒸發（淘汰冷 segment）
- RecMem：觸發 consolidation
- H-MEM/RecMem 推薦給 Hermes：用於 drift penalty 計算
- OCL/Governed Memory：兩階 enforcement（fast/slow）的 routing 依據（不同公式但同樣的「用歷史信號決定要不要 LLM call」邏輯）

關鍵 insight：**這三個用途（淘汰 / 觸發 / penalty）應該用同一個底層 heat 計算，傳回不同的動作決策**。目前 Hermes 規劃是「drift penalty 用 heat score」——但其實 heat score 也應該決定**新 distillate 的寫入優先級**（高 heat 概念周邊優先補）和**淘汰時機**（低 heat 概念優先 evict）。

**可行動下一步**：

把 `heartbeat_learning.py` 的 `distillate_heat()` 函式（目前若無，則新建）獨立成 `lib/heat_score.py`，讓三個呼叫端共用：
1. **Drift penalty 計算**：現有計畫
2. **Distillation priority queue**：新 distillate 候選先看是否能修補低 heat cluster（這就是 Theme 1 的閉環）
3. **Eviction policy**：當 memory storage 超過上限，淘汰 heat < threshold 的 segment（FIFO 太粗暴，MemoryOS 數據顯示 heat eviction 在 LoCoMo temporal QA +118.80%）

預期工時：抽 lib 1 小時 + 三個呼叫端改寫各 30 分鐘 = 半天。

## Cross-Cutting Theme 3：兩階 enforcement（fast deterministic + slow LLM）是隱性收斂（中信心）

**支援筆記**: 2026-06-09-llm-agent-memory-governance-synthesis（OCL πgate 決定論 + πrole 角色檢查; Governed Memory Fast mode 850ms / Full mode 2-55s）, 2026-06-09-memory-os-three-tier-hierarchical-memory（STM 7-page FIFO 不進 LLM、MTM 才進 LLM）, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory（RecMem Subconscious 不進 LLM、Episodic 才進）

三套系統都內建了「cheap path 不呼叫 LLM、expensive path 才呼叫」的兩階設計，但**沒有一篇把它當成主要 insight 強調**。Governance synthesis 提到 OCL 的「deterministic replan」和 Governed Memory 的「fast vs full mode」，MemoryOS 的 STM/MTM 本質上就是這個結構。

對 Talos PolicyInterceptor 的意涵：目前設計是「攔截 → 規則匹配 → 必要時 LLM 判定」——這已經是兩階。但**沒有 fast path 的延遲預算**。建議：
- Fast path 目標延遲：<200ms（純規則匹配、預先編譯的 allowlist/blocklist）
- Slow path 目標延遲：<3s（單次 LLM 分類呼叫）
- Audit 永遠走 fast path append（不論結果）

**可行動下一步**：

在 Talos PolicyInterceptor 加延遲 instrumentation（`time.perf_counter()` 包住 fast/slow path），未來兩週的 telemetry 收集後決定 threshold。不需先動 LLM 邏輯，只加計時與日誌。預期工時：1 小時。

---

## 反向驗證：為何這次 synthesis 比單篇更深

四篇筆記各自都做了 intra-paper synthesis（governance synthesis 3 份 paper、H-MEM/RecMem 2 份 paper、MemoryOS 1 份、SAGE 1 份）。把它們放在一起才浮現的 insight：

1. **「Heat score 公式」獨立重發明**——單篇看不出，因為每篇都把它當作論文的次要細節
2. **「SAGE 是唯一閉環」**——單篇 SAGE 強調 self-evolution，但讀者會以為是常態；對照三篇開環系統才知道 SAGE 是異類
3. **「兩階 enforcement」**——OCL/Governed Memory/MemoryOS 三家不互相引用，但收斂到同樣設計，這是強訊號
