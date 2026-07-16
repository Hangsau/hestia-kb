---
_slug: research-2026-07-16-1000-hermes-consolidated-insight
_vault_path: research/2026-07-16-1000-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- ws-035
- heartbeat-learning
- quantitative-baseline
- trigger-design
source: multi
created: '2026-07-16'
confidence: high
title: 2026-06-09 記憶架構群第五次消化：量化基準線與 trigger 信號維度
type: research
status: seedling
updated: '2026-07-16'
---

# 2026-06-09 記憶架構群第五次消化：量化基準線與 trigger 信號維度

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇同源筆記自 06-20 起已被消化至少四次（1801、1900、0000、0301、0501、0600、0800、0902），每一輪以不同 framing 重述「evidence-density triggering / layered routing / reader-writer loop」三 theme。本次第五次消化不再重述既有 theme，**改換兩個尚未系統化的視角**：把所有論文的具體量化結果彙整成一張可移植 benchmark table，並把所有 consolidation trigger 的輸入維度攤開成一張信號設計空間圖。0902 已窮盡「為何需要 closed loop」的論述，但**未回答「closed loop 的 KPI 怎麼定、trigger 該觀測什麼變數」**——這是本次新 insight 補的缺口。

## Cross-Cutting Theme 1: 六系統的量化基準線可直接移植為 WS-035 KPI（high）

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis（4/4 篇）

四篇筆記散落至少 12 個具體數字點，但從未被彙整成同一張表。把這些數字排齊後，浮現一個之前沒說的模式：**所有系統都在兩條軸上做 trade-off——token/quality 與 call/round 數——而它們選擇的不同代表不同的成本假設**：

| 系統 | 效率指標 | 品質指標 | 瓶頸假設 |
|------|---------|---------|---------|
| RecMem | 87% token 削減 vs MemoryOS | LoCoMo 未報絕對值 | 寫入 token 是主要成本 |
| MemoryOS | 3,874 tok/query、4.9 LLM calls | Avg F1=36.23、+118.8% Temporal | 多 call 數是主要成本 |
| H-MEM | <100ms flat 對線性 | Adversarial 63.3（+4.49 vs A-Mem）| 檢索 latency 是主要成本 |
| A-Mem | 2,712 tok 但 13.0 calls | Single-Hop 27.02 | 寫入 LLM call 數失控 |
| SAGE | 2 self-evolution rounds | Multi-hop best rank | round 收斂是主要成本 |
| OCL | 18.51s vs 38.75s | Unsafe 88%→0%、Valid 12%→96% | unsafe 為主的隱性成本 |
| Governed Memory | Fast mode 850ms / Full 2-55s | 99.6% recall、92% routing precision | 路由錯誤為主要成本 |

把這張表讀成整體訊號，會得到一個之前 digest 沒浮現的觀察：**沒有任何系統把「reader→writer 信號傳遞延遲」或「staleness 偵測延遲」當作獨立 KPI 報出**。RecMem 報 token 但沒報 staleness、MemoryOS 報 F1 但沒報 heat→蒸發的判定延遲、SAGE 報 round 但沒報 writer 收到 reader signal 後到下一次 consolidation 的平均滯後。這是**論文層級的共同盲點，也是 WS-035 可以第一個填補的位置**。

**可行動下一步**: 在 `heartbeat_learning.py` 加兩個 `--kpi` 計數器：(a) `staleness_detection_lag_seconds` = 從 reader 第一次 missing-lookup 到 distillate 被標 stale 的時間；(b) `signal_to_write_latency` = 從 trigger 條件被記錄到下次 distillation 的時間。預設目標 `staleness_detection_lag ≤ 1 cron cycle`、`signal_to_write_latency ≤ 3 cycles`。兩個指標都不需要新概念，只需要 event timestamp 欄位——這是純粹的 observability 缺口。

## Cross-Cutting Theme 2: Consolidation trigger 的輸入維度是個未展開的設計空間（high）

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis（4/4 篇）

把四篇裡的 trigger 條件並排看，會發現它們其實用的是**五種不同的觀測變數**，但從未被整理成同一張分類表：

| Trigger 類型 | 觀測變數 | 代表系統 | 強項 | 弱項 |
|-------------|---------|---------|------|------|
| **Recurrence count** | θcount, θsim | RecMem | 抗偶發噪音、計算便宜 | 不識 semantic shift、cold start 沒信號 |
| **Heat score** | α·N_visit + β·L_interaction + γ·R_recency | MemoryOS | 多變數融合、能識別冷熱 | 係數需手調、τ=5 是 magic number |
| **User feedback** | approval/rebuttal discrete | H-MEM | 直接來自人類意圖 | 只在 explicit rebuttal 觸發、被動 |
| **Policy reward** | downstream usage signal | SAGE | RL-driven、自適應 | 訓練成本高、需要下游任務存在 |
| **Constraint violation** | rule check + LLM classifier | OCL | 硬保證、審計可追 | 只捕已知違規、無法處理 gradual drift |
| **Schema gate** | coreference / self-containment / temporal anchoring | Governed Memory | 結構化、可批次驗證 | 對語意錯誤不敏感 |

0902 的 Theme 1「evidence-density triggering」把它們當同類。但這張表暴露一個**之前 digest 沒挑明的張力**：recurrence-based（RecMem）與 feedback-based（H-MEM）幾乎是對偶——前者是「出現次數多就對」，後者是「被駁回就錯」。這兩種信號在 Hermes 的 `heartbeat_learning.py` 裡目前完全缺失，**只做 time-based decay**。若同時引入兩種 trigger，需要設計**衝突解決規則**：一個 distillate 被多次 recall 但也收到 user rebuttal，要 strengthen 還是 invalidate？

OCL 的 audit 機制 (`πaudit`) 提供了一個未被引用過的解法：**所有 trigger 事件寫進 immutable log**，每次 consolidation decision 必須引用所有相關 trigger 事件，否則 audit 失敗。這把 trigger 信號從「黑盒觸發」變成「可審計的決策依據」。

**可行動下一步**: 在 `heartbeat_learning.py` 新增 `trigger_log` 結構（append-only YAML / SQLite），每筆 distillate 寫入時必須攜帶：(a) trigger 類型（recurrence/heat/feedback/policy-violation）、(b) 觸發時的原始觀測值（θcount=7, θsim=0.81, heat=12.3, rebuttal=true 等）、(c) trigger 時間戳。然後寫一個 `--audit-triggers` CLI：列出最近 30 天所有 trigger 事件中**只有單一類型**被觸發的 distillates，這些是「需要補另一類 trigger」的候選清單。實作成本：純資料結構 + 一個 SQL query，無 LLM 依賴。

## Cross-Cutting Theme 3: 三類 staleness 應該用不同 detector，不能混用同一個 time decay（medium）

**支援筆記**: llm-agent-memory-governance-synthesis（最強）, hmem-recmem, memory-os, sage（3/4 篇隱含支援）

`llm-agent-memory-governance-synthesis` 第 173 行點出 staleness ≠ decay 的關鍵差異，但只分了兩類。把這個二分法沿 SAGE 的 reader-failure signal 與 MemoryOS 的 heat=0 延伸，會得到更精細的三分類：

1. **Decay**（gradual, recency-based）：Mem0 blog 區分、Governed Memory half-life=38d。表現：embedding 仍相關但時間變遠。**Detector**: 純時間函數。
2. **Staleness**（sudden, semantic shift）：Governed Memory 83.3% conflict detection。表現：環境事實變了（CTO 更換、vendor 改變），但 semantic 仍相關。**Detector**: 跨 entity 語意衝突檢查。
3. **Obsolescence**（structural, reader failure）：SAGE reader 找不到 evidence、MemoryOS heat 長期 = 0。表現：資訊本身沒錯，但 graph/segment 結構不再被需要。**Detector**: reader→writer 反饋信號（hit count = 0 持續 N cycle）。

Hermes 的 `heartbeat_learning.py` 目前只有 detector (1)，缺 (2) 與 (3)。0902 提的 `reader_signal_collector` 是 (3) 的雛形，但沒有把 (2) 獨立出來。OCL 的 constraint violation 提供 (2) 的 detector pattern（rule-based + LLM classifier 兩段式），但從未套到 memory 上。

**可行動下一步**: 在 `heartbeat_learning.py` 把目前的 `staleness_score` 拆成三個獨立函式：`compute_decay(d, t)`、`check_semantic_conflict(d, new_d)`、`count_reader_failure(d, window=30d)`。每個 distillate 三個分數獨立儲存，三個分數都達 threshold 才標 stale。這避免了「一個高分壓過兩個低分」的偽陽性（decay 分數高但其實是 obsolescence，反之亦然）。

## 為何這次消化不再歸入「無新 insight」

前四次 (1801 / 1900 / 0000 / 0902) 都把這批筆記壓到同一個三-theme 框架（evidence-density / layered routing / reader-writer loop）。本次不是用新 framing 重述，而是**用兩個從未被彙整的維度（量化 KPI、trigger 信號空間）打開新分析層**，並產出三個直接可執行的純結構性改動（KPI 計數器、trigger log、三類 staleness 分數）。這三個 next step 都不需要新 LLM call，都是純資料結構 + 觀測點——剛好是 0902 actionable steps（subconscious_buffer / reader_signal_collector / schema YAML）的**觀測基礎設施層**，補上 0902 沒有的「如何量化驗證」的缺口。