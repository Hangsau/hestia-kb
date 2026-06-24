---
_slug: research-2026-06-25-0000-hermes-consolidated-insight
_vault_path: research/2026-06-25-0000-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-25'
confidence: high
title: 四套記憶架構的隱形收斂：Reader-Failure 閉環是 WS-035 Drift Penalty 的真正缺口
type: research
status: seedling
updated: '2026-06-25'
---

# 四套記憶架構的隱形收斂：Reader-Failure 閉環是 WS-035 Drift Penalty 的真正缺口

**消化筆記**: 
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 探索筆記各自描述了一套記憶系統（H-MEM/RecMem/MemoryOS/SAGE/Governed Memory），表面上是「分層架構」的四種變體。把它們放在一起才看得出來：**它們收斂到同一個尚未被任何單篇論文明確命名的設計原則**——reader-failure 閉環反饋。

## Cross-Cutting Theme 1: 觸發訊號是互補的，不是競爭的

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

每篇筆記各自挑選「一個」觸發訊號做 consolidation/invalidation：

| 系統 | 觸發訊號 | 失敗模式 |
|------|---------|----------|
| RecMem | recurrence count (θcount ≥ 5) | 不重複出現的隱性資訊會被永久忽略 |
| H-MEM | user feedback (approval/rebuttal) | 沒人反駁不代表沒失效（silent staleness） |
| MemoryOS | heat score (visit × interaction × recency) | 從未被檢索的「沉睡正確知識」會被蒸發 |
| SAGE | reader failure signal (closed-loop) | 缺乏 read-time feedback 時 writer 無法改進 |
| 治理論文 §3.2 | event-driven invalidation vs time decay | 純時間衰減無法捕捉「語意仍相關但語義已失效」 |

把它們疊起來看的 pattern：**每一種訊號對應不同的失敗模式**，五者互補而非互斥。一個只用 heat score 的系統會殺死沉睡但正確的知識；一個只用 recurrence 的系統會忽略 silent decay；一個只用 user feedback 的系統會在無人監督的長期運行中累積錯誤。

**洞察**：四篇筆記中沒有一篇明確指出「這五種訊號應融合」，但每一篇的量化結果都強烈暗示——任何單一訊號都會在 LoCoMo 的某個維度掉鏈子（RecMem 沒報 multi-hop 細節，H-MEM 在 single-hop 只贏 1.7，MemoryOS 在 temporal 領先但其他系統沒在同條件比）。

**可行動下一步**：在 `heartbeat_learning.py` 中實作 `DriftSignal` 多源融合器——每個 distillate 同時追蹤 `n_recurrence` (RecMem-style)、`n_user_rebuttal` (H-MEM-style)、`heat_score` (MemoryOS-style)、`reader_failure_count` (SAGE-style)、`semantic_drift_delta` (governance-paper §3.2 style)，以 weighted voting 決定是否標記為 stale。預設權重：reader_failure 0.4, user_rebuttal 0.3, semantic_drift 0.2, heat 0.05, recurrence 0.05（前兩個是強訊號，後三者是弱訊號）。**不**先寫完整 multi-signal fusion，而是先在現有 heartbeat_learning.py 加一個 `signals.json` per-distillate 結構，3 天後看哪個訊號真的有 signal。

## Cross-Cutting Theme 2: 讀取時的失敗反饋（Reader-Failure Loop）是研究 demo 與 production-grade 的分水嶺

**支援筆記**: sage, llm-agent-memory-governance-synthesis, memory-os, hmem-recmem

**支援證據的層級排序**（從最強到最弱）：

1. **SAGE 明確提出 writer-reader 閉環自演化**——"better reading exposes writing defects, better writing makes future reading more precise"。兩輪 self-evolution 達到 multi-hop QA 最佳排名。
2. **Governed Memory (Personize.ai, 已 production 部署) 的 reflection-bounded retrieval**——每輪由 LLM judge evidence completeness，incomplete 時 generate targeted follow-up queries。**62.8% vs 37.1% baseline（+25.7pp）**。這是 read-time feedback 的實戰數據。
3. **MemoryOS 的 heat-based eviction 是 reader-failure 的隱性代理**——低 heat = 讀取器長期未引用 = 實質上的 reader failure 訊號。
4. **H-MEM 的 user rebuttal** 是 read-time feedback 的人力版。
5. **RecMem 是反例**——純粹的 write-time signal，沒有 read-time feedback 機制。

**洞察**：把上述四個排序才看得出來——**所有 production-grade 或近 production-grade 的系統（SAGE 在 NeurIPS 2026 走完 2 輪閉環、Personize.ai 部署、MemoryOS 在 EMNLP 2025）都有 reader-failure 訊號**。純粹 write-time trigger 的系統（RecMem）即使有漂亮的 87% token 節省，量化結果的覆蓋維度也明顯較窄。Hermes 的 `heartbeat_learning.py` 目前是純 write-time trigger（蒸餾觸發 + 時間衰減），這是把研究 demo 當 production 在用。

**可行動下一步**：在 `heartbeat_learning.py` 增加 `reader_signal_collector.py`——每次 task context matching 找不到合適 distillate 時，記錄 `(task_signature, query_time, miss_reason)`。30 天後聚類「miss_reason」，產出「系統性缺失的蒸餾主題」清單，餵回 distillation trigger 作為 hint。預期 30 天內可識別 5-10 個「從未蒸餾但反覆被查詢」的概念。具體實作：在現有 retrieval path 加 try/except 包裹，catch `NoMatch` exception 寫入 `~/.hermes/miss_log.jsonl`（append-only），每週 cron 跑聚合。

## Cross-Cutting Theme 3: Substrate-Policy 分離是所有成功系統的隱形架構原則

**支援筆記**: 全部四篇

把四篇並排才看得出來的元模式：

- **H-MEM**：substrate = 階層式 index encoding (discrete position pointer)，policy = user-feedback-driven weight adjustment
- **RecMem**：substrate = subconscious store (raw embeddings, no LLM)，policy = recurrence-triggered abstraction
- **MemoryOS**：substrate = STM/MTM/LPM 分段分頁儲存，policy = heat-based FIFO eviction
- **SAGE**：substrate = entity-relation triple graph，policy = writer policy (when/how to write) + reader GFM (how to read)
- **Governed Memory**：substrate = dual memory (open-set + schema-enforced)，policy = quality gates + tiered routing (fast/full mode)

**洞察**：**沒有一個成功的系統把「存什麼」和「怎麼決定存/讀/蒸發」混在一起**。所有系統都明確分出 substrate layer（資料結構本身的特性）與 policy layer（動態決策邏輯）。這個分離讓 policy 可以獨立演進而不動 substrate（MemoryOS 換 heat 公式不影響 STM/MTM/LPM 三層結構；H-MEM 換觸發訊號不影響四層 index）。反過來說，Hermes 的 `distillate` 目前是 substrate-policy 耦合的——JSON 結構裡同時混了 metadata (substrate) 與 staleness rules (policy)，每次改 decay 公式都要 migration。

**可行動下一步**：refactor `distillate` JSON 為兩個檔：`distillate.substrate.json` (id, content, embedding, created_at) 和 `distillate.policy.json` (heat_score, decay_half_life, signals, last_rebuttal_at)。policy 檔可以單獨被 batch-update 而不碰 content。這個 refactor 是低風險的（讀取路徑加一個檔案讀取），但會讓未來引入 Theme 1 的多訊號融合時不必 schema-migration。

## 跨主題整合：為何這三個 theme 應一起看

Theme 1（多訊號融合）、Theme 2（reader-failure 閉環）、Theme 3（substrate-policy 分離）**不是三個獨立建議**——它們是同一個架構決策的三個面向：

- Theme 3 是**架構基礎**：先分開 substrate 與 policy
- Theme 1 是**policy 層的內容**：分開之後，policy 才能容納多訊號融合
- Theme 2 是**policy 訊號的關鍵來源**：reader-failure 訊號是其他訊號都沒捕捉到的維度

執行順序必須是 3 → 1 → 2。倒過來做（先寫 reader-failure collector 在耦合架構上）會在第一個 schema 變更時報廢。

## 信心標示

- Theme 1 信心：**high**（四篇筆記的觸發訊號表已交叉驗證，每篇的量化結果都間接支持單一訊號不足）
- Theme 2 信心：**high**（SAGE + Personize 兩個最強證據 + 兩個隱性代理；RecMem 反例強化論點）
- Theme 3 信心：**medium**（substrate-policy 分離是歸納推論，四篇沒有一篇明確使用此術語；歸納成分高但 pattern 一致）

## 下一次 consolidation 的觀察點

- 30 天後看 `miss_log.jsonl` 的 miss_reason 分佈（驗證 Theme 2 的「系統性缺失蒸餾主題」是否真的存在）
- 觀察 `signals.json` 哪個訊號實際有 signal、哪個永遠是零（驗證 Theme 1 的權重設定是否需要調整）
- 如果 `distillate.policy.json` 引入後 3 個月內需要改 ≥3 次 policy 而不碰 content，Theme 3 算證實
