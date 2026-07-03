---
_slug: research-2026-07-03-1601-hermes-consolidated-insight
_vault_path: research/2026-07-03-1601-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- ws-035
- governance
source: multi
created: '2026-07-03'
confidence: high
title: 2026-06-09 Memory Architecture Quartet 的隱藏軸線：為何 WS-035 應設計成「read→write 反饋閉環」而非「trigger
  選擇題」
type: research
status: seedling
updated: '2026-07-03'
---

# 2026-06-09 Memory Architecture Quartet 的隱藏軸線：為何 WS-035 應設計成「read→write 反饋閉環」而非「trigger 選擇題」

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇都是 2026-06-09 同日針對 LLM agent memory 的探索，個別已做過跨論文比較。把它們疊起來才看見的元模式：所有系統都在解同一個三軸問題（**storage 結構 / write trigger / death condition**），但只有當 read→write 閉環存在時，系統才真正勝過基線——這直接決定 WS-035 drift penalty 的架構應該長什麼樣。

## Cross-Cutting Theme 1: Read→Write 反饋閉環是唯一穩定勝過基線的設計特徵

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

**分析**:

把四篇量化結果攤開看，唯一**跨所有架構都成立**的勝出條件是「reader 失敗信號能否流回 writer」：

| 系統 | 是否有 read→write 反饋 | 在 LoCoMo / 對抗實驗上的結果 |
|------|----------------------|----------------------------|
| RecMem | ❌ 只有 write-side recurrence threshold | 87% token 節省，但 F1 未直接報告 |
| MemoryOS | ❌ 只有 write-side heat score | Avg F1 36.23（1st on LoCoMo） |
| H-MEM | ⚠️ user rebuttal → memory weight（半閉環） | Adversarial 63.30 vs 58.81 |
| SAGE | ✅ writer-reader 兩 rounds self-evolution | Multi-hop QA 最佳 mean rank |
| Governed Memory（OCL） | ✅ reflection-bounded retrieval（25.7pp） | Valid success 12% → 96% |
| OCL governance | ✅ pre-execution gate | Unsafe rate 88% → 0% |

**關鍵觀察**：RecMem 和 MemoryOS 在 LoCoMo 上都很強，但它們的設計都把**淘汰條件寫死**（recurrence count ≥ θcount / heat < τ）——系統自己不會問「為什麼我找不到證據」。SAGE 和 Governed Memory 則讓 reader 主動告訴 writer「這條資訊不足」，系統就能自我修正。

對 Hermes 的含義：WS-035 drift penalty 目前的設計是把 trigger（recurrence / heat / contradiction / time decay）當**選擇題**在討論——但四篇疊起來看，這是錯的問題。正確問題是：**heartbeat_learning.py 的 retrieval 端有沒有 channel 把「找不到」這個信號送回 distillation trigger？** 只要這個閉環存在，trigger 用哪一種其實都是次要問題。

**可行動下一步**:
在 `heartbeat_learning.py` 加一個 `reader_failure_signal` 機制：當 task context 對某個 distillate 連續 N 次檢索不到匹配時，產生 `staleness_candidate` 事件送回 distillation queue。具體實作（今天可做）：
1. 在 retrieval 端加 hook，記錄 `(distillate_id, miss_count, last_queried_at)`
2. `miss_count > 3 AND heat < threshold` → 標記 `potentially_stale`
3. `potentially_stale` 的 distillate 進入下個 distillation cycle 的「應否重蒸餾」清單
預期效益：把目前純粹 time-based decay 改成 evidence-based，預計可消除 sage 論文指出的「semantic 看起來相關但實際失效」問題。

## Cross-Cutting Theme 2: 所有系統都在偷偷解同一個三軸問題，但沒有一個命名它

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

**分析**:

把四篇的設計拆成 component，會發現它們其實都在做**同一件事的三個不同軸**：

| 軸線 | H-MEM | RecMem | MemoryOS | SAGE | Governed Memory |
|------|-------|--------|----------|------|-----------------|
| **Storage 結構** | 4 層 positional index | 3 層 subconscious/episodic/semantic | OS segment-page | Entity-relation graph | Open-set + schema-enforced dual |
| **Write trigger** | 每次 interaction | Recurrence count ≥ θcount | Heat > τ | Writer policy (RL) | Single extraction pass |
| **Death condition** | Memory weight dynamic | θsim filter | Heat < τ AND eviction | Reader failure signal | Schema violation / staleness |

四篇 paper 各自強調自己的 trigger 或結構，但**沒有一篇把這三軸明顯分開討論**——都是「我發明了一個 X 層架構」之類的命名。

但其實它們做的是同一件事：定義「東西住在哪、什麼時候進來、什麼時候滾蛋」。如果我們承認這是**三個正交軸**，WS-035 的設計就有 8 種可能的組合（2³），不該在某一個軸上糾結。

更重要的：**Storage 結構的選擇和 trigger 選擇是無關的**。H-MEM 證明了 hierarchical routing + user-feedback trigger 可以 work，MemoryOS 證明了 OS-style paging + heat trigger 也可以 work。Hermes 不需要選邊站。

**可行動下一步**:
把 WS-035 的設計文件改寫成三個獨立的 module spec：
- `WS-035-A Storage Schema`: 採用 H-MEM 的 4 層概念 + MemoryOS 的 segment-paging 啟發的 session 分組
- `WS-035-B Write Trigger`: 採用 RecMem recurrence + H-MEM user-feedback 的組合
- `WS-035-C Death Condition`: 採用 heat score（MemoryOS）+ reader failure signal（Theme 1）
這三個 module 之間**不應共享 code path**，應該各做各的，結果在 retention score 上加權合併。
具體動作：今天在 `~/obsidian-vault/30-Areas/hermes-ops/` 開 `WS-035-decomposition.md`，把這三個 module spec 寫成各自獨立的 ADR，迫使未來 review 時分別評估每個軸線的決策。

## Cross-Cutting Theme 3: 「寫入時強制結構」是所有 production-grade 系統的共同特徵

**支援筆記**: memory-os, sage, llm-agent-memory-governance-synthesis (Governed Memory 部分)

**分析**:

MemoryOS 的 90 維度 User Traits、SAGE 的 entity-relation triple 強制 schema、Governed Memory 的 schema-enforced property values——三個 production-grade 或 NeurIPS 級的系統，全部在**寫入時**就強制結構。

反觀 Hermes 目前的 distillate 是 free-form markdown。雖然在 retrieval 時有 embedding similarity，但「寫入時是鬆的、讀取時才強求結構」是 OCL 論文裡 88% unsafe rate 的典型成因——寫入時的 quality gate 比讀取時的 rule 重要得多。

Governed Memory 量化了 schema enforcement 的價值：cross-entity leakage 在 500 個 adversarial queries 上 0%。MemoryOS 的 90-dim trait vector 是它能拿到 LoCoMo 第一名的關鍵差異化。

這是一個**目前四篇個別 note 都沒明說、但疊起來才看得見**的批評：Hermes 的 distillate schema 太自由了。

**可行動下一步**:
給 distillate 強制一個**最輕量的 schema**（不用 90 維度，但至少有基本結構）：
- `id`, `created_at`, `last_validated_at`
- `entity_refs: [str]` （類似 SAGE 的 entity 概念）
- `relation_to_existing: str | null` （consolidation trigger 觸發點）
- `confidence: float`
- `evidence_trace: [str]` （類似 Governed Memory 的 source anchoring）

實作：在 `heartbeat_learning.py` 的 distillation step 加 Pydantic model validation，缺欄位的 distillate 不寫入。
這個改動**預期效益最高、改動量最低**——大概 50 行 code，但能立刻讓 Hermes 對齊 production-grade 系統的最低標。

## 信心標示

- Theme 1 (read→write 閉環): **high** — 四篇都有量化數據支持，且這個 pattern 跨越 memory system 和 execution governance 兩類系統
- Theme 2 (三軸分解): **medium-high** — 三軸的劃分是 cross-paper 觀察的 abstraction，四篇各自沒明說這個結構，但都符合
- Theme 3 (寫入時強制結構): **medium** — 三篇支持（memory-os, sage, governed memory），但 hmem-recmem 那篇對結構強制較弱（purely hierarchical），可能有 selection bias

## 對 Talos / Hermes 路線的整合判斷

這四篇 paper 共同指出：**Hermes 目前的 distillate 系統不是「記憶系統」，是「軌跡保存」**（對應 arXiv:2605.06716 的 Storage 階段）。要進化到 Experience 階段，三個架構決策必須做：

1. **建立 read→write 反饋**（Theme 1）——這是從「軌跡」到「經驗」的最低門檻
2. **承認三軸正交性**（Theme 2）——停止在 trigger 類型上選擇題糾結
3. **寫入時強制 schema**（Theme 3）——這是 production-grade 的入場券

如果只能做一件事，做 Theme 1 的 reader failure signal channel——它的 ROI 最高、改動量最小、且能直接消除 88% unsafe rate 等價的「distillate 失效但系統不知道」問題。
