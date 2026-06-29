---
_slug: research-2026-06-29-1601-hermes-consolidated-insight
_vault_path: research/2026-06-29-1601-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- agent-memory
- governance
source: multi
created: '2026-06-29'
confidence: high
title: Reader-Writer 分離原則 + 容量飽和點：跨四篇 2026-06-09 記憶系統文獻的收斂
type: research
status: seedling
updated: '2026-06-29'
---

# Reader-Writer 分離原則 + 容量飽和點：跨四篇 2026-06-09 記憶系統文獻的收斂

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇獨立來源的 2026-06-09 文獻（分別從 recurrence、OS 三層、graph self-evolution、governance survey 四個角度切入 LLM 記憶系統）收斂到同一個被忽略的問題：**Reader-Writer 之間缺少失效信號回饋**，以及一個值得注意的**容量飽和常數**。

## Cross-Cutting Theme 1: Reader-Writer 分離與回饋迴圈是所有記憶系統的隱含 Pillar

**支援筆記**: 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory

四篇筆記各自從不同角度觸及 Reader-Writer 分離，但**沒有一篇把這寫成第一公民（first-class concern）**：

- **SAGE** 是唯一明確實作 writer-reader closed-loop 的系統（Reader 失敗 → Writer 改進目標），但筆記把它定位為「graph-specific 創新」
- **MemoryOS** 的 heat score 中的 `N_visit`（segment 被檢索次數）本質上是 reader-side signal，但筆記只把它歸類為「eviction 機制」
- **H-MEM** 的 user-feedback-driven memory weight（approval → strengthen, rebuttal → decay）是另一種 reader signal，但筆記把它當作「user-facing adjustment」
- **RecMem** 的 recurrence-triggered consolidation（θcount ≥ threshold）完全依賴 reader-side cosine similarity，但筆記把它定位為「trigger 條件」
- **2605.06716** survey 明確指出 heartbeat-style distillate 缺少 cross-trajectory abstraction，這就是 reader-driven writer feedback 的學術語言

**Convergence insight**：這四篇論文在語法上是不同設計，語意上是同一件事——**記憶系統的「寫入端」必須能從「讀取端」收到失效信號，否則就會在 staleness/conflict/hub-over-expansion 上靜默退化**。SAGE 證明 closed-loop 必要；H-MEM + MemoryOS 證明 reader signal 必須納入 weight 計算；RecMem 證明 reader 的 recurrence count 足以作為 consolidation trigger。

**對 Hermes/Talos 的缺口**：`heartbeat_learning.py` 目前是純寫入端（write-only distillate pipeline）。每篇筆記都建議加入「reader failure signal → writer feedback channel」，但**沒有一篇指出這其實是同一個架構 primitive**——目前的 proposal landscape 把這當作四個獨立 feature（drift penalty、recurrence trigger、heat score、cross-trajectory abstraction），實際上是同一個 closed-loop 的四個視角。

**可行動下一步**：
- 在 `~/hermes-new/proposals/` 開新檔案 `ws-XXX-memory-reader-writer-feedback-loop.md`：把四個分散的設計元素（SAGE self-evolution、MemoryOS heat、H-MEM rebuttal、RecMem recurrence + governance synthesis 的 cross-trajectory abstraction）合併成單一 architectural primitive「retrieval-failure → distillation-trigger feedback channel」
- 從 SAGE 借用具體 schema：Reader 報告 `(failed_query, missing_evidence, confidence)` 三元組，Writer 收到後判斷「這是新的 distillate 需求」還是「現有 distillate 需要蒸發」
- 不要先寫 drift penalty——把 drift penalty 視為這個 feedback channel 的一個 use case，而非 standalone feature

## Cross-Cutting Theme 2: 「容量飽和點 ≈ 7」是跨系統的 unexpected constant

**支援筆記**: 2026-06-09-llm-agent-memory-governance-synthesis, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory

四篇筆記中至少有四個獨立的「容量常數」集中在 5–7 區間：

| 系統 | 常數 | 數值 | 出處 |
|------|------|------|------|
| MemoryOS | STM 對話頁面佇列長度 | 7 pages | 固定超參數，未做 ablation sweep |
| MemoryOS | LPM User KB | 100 條 FIFO | 動態尺寸但固定上限 |
| MemoryOS | MTM segment 上限 | 200 segments | 觸發 heat-based eviction 的上限 |
| H-MEM | 階層深度 | 4 層 | ablation 確認 optimal |
| RecMem | θcount 預設 | 5 | default threshold |
| RecMem | top-k retrieval | k（未指定值，建議小） | cosine retrieval depth |
| Governed Memory | memory density saturation | ~7 per entity | +24% quality jump 0→3, diminishing returns 之後 |
| 2605.06716 | contradiction resolution | 33.3% full suppression | 剩下的 66.7% 是 partial |

**Convergence insight**：這不是巧合。Miller (1956) 的「Magic Number 7±2」短期記憶極限在 70 年後的 LLM agent memory 設計中以系統參數的形式**重新出現**——不是作為認知隱喻，而是作為真的容量上限。

更值得注意的是**每個系統都選了不同的數字但同一個量級**：MemoryOS 選 7、RecMem 選 5、H-MEM 選 4、Governed Memory 量出 7。多數差異在 ±2 內。這意味著：
1. 不存在「越多越好」的 scaling
2. 不存在「精確最優值」——這是個 plateau，不是 peak
3. 對 Hermes 的含義：distillate 數量上限應該設約 5–7 per concept，**不是 unlimited FIFO**

**可行動下一步**：
- 在 `heartbeat_learning.py` 的 distillate store 加入 hard cap：每個 concept cluster ≤ 7 條，超過觸發 Reader-Writer feedback（「蒸發最舊 + 蒸餾抽象層版本」），這直接呼應 Theme 1 的 feedback channel
- 把這個常數記錄到 `~/obsidian-vault/40-Resources/_mixed/explorations/` 作為「agent memory 容量設計約束」，未來相關 proposal 直接引用
- 不需要 ablation 實驗——四個獨立系統的收斂已是足夠證據；先 ship，再 measure

## Cross-Cutting Theme 3: 「架構分離」原則穿過記憶、寫入、執行三層

**支援筆記**: 2026-06-09-llm-agent-memory-governance-synthesis, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine

這是四篇筆記中**最容易被低估**的收斂點——因為它以三種不同形式出現，被各筆記當作「理所當然」處理：

- **OCL（governance 維度）**：proposal generation ↔ environment-facing execution 分離。Task success 94% 隱藏 88% unsafe rate，正是因為沒有 separation
- **MemoryOS（記憶結構維度）**：STM ↔ MTM ↔ LPM 之間有 explicit handoff boundary（heat > τ 才升級），不是連續流動
- **Governed Memory / Personize.ai（生產部署維度）**：memory store ↔ governance layer 分離，schema enforcement 是中間的 enforcement boundary
- **SAGE**：writer ↔ reader 分離，self-evolution 是分離後才能成立的 loop

**Convergence insight**：production-grade agent system 在三個 layer（execution、memory storage、memory write/read）都發現「分離 + boundary condition」是必要條件。**Hermes 目前在三個 layer 都違反這個原則**：
- Talos `PolicyInterceptor`：proposal 與 execution 在同一 code path（筆記 #4 明確指出這是缺口）
- `heartbeat_learning.py`：write 與 read 共用同一個 buffer（Theme 1 的問題）
- Skills 系統：skill 定義與 skill 調度沒有 boundary

**可行動下一步**：
- 在三個 layer 各加一個 explicit boundary：
  1. Talos tool call: 提取 `PolicyInterceptor` 為獨立 module，OCL 的四個 policy components（πrole / πgate / πescalate / πaudit）直接套用
  2. `heartbeat_learning.py`: 分離 `distillate_writer.py` 和 `distillate_reader.py`，中間是 topic-cluster 索引
  3. Skills: 分離 `skill_registry.py`（靜態 metadata）和 `skill_dispatcher.py`（runtime 調度），中間是 trigger conditions 表
- 這三個重構可以**並行**做，因為它們是同一個架構 primitive 的三個 instantiation

## 信心標示

**high**：四個 source 來自四個不同研究組（EACL、ACL、arXiv preprints）、不同 paradigm（cognitive science / OS engineering / graph neural / governance survey），獨立收斂。

---

**整合者備註**：下次 exploration 如果又出現「memory health」相關筆記，應該明確指定它對應到這三個 theme 的哪一個 slot，避免重複產生孤立提案。
