---
_slug: 40-Resources-_mixed-explorations-2026-06-09-探索-H-MEM---RecMem---階層式-vs--recurrence-triggered-記憶架構---2026
_vault_path: 40-Resources/_mixed/explorations/2026-06-09-探索-H-MEM---RecMem---階層式-vs--recurrence-triggered-記憶架構---2026.md
title: 探索：H-MEM + RecMem — 階層式 vs  recurrence-triggered 記憶架構 — 2026-06-09
date: 2026-06-09
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- consolidation
- eacl
- index
- layer
- llm
- mem
- memory
- recmem
- recurrence
- semantic
created: '2026-06-09'
updated: '2026-06-15'
status: budding
---

# 探索：H-MEM + RecMem — 階層式 vs  recurrence-triggered 記憶架構 — 2026-06-09

**延續自**: [[2026-06-09-llm-agent-memory-governance-synthesis]]

**日期**: 2026-06-09 | **來源**: H-MEM (EACL 2026, sun-etal-2026.eacl-long.15) + RecMem (ACL 2026 Findings, arxiv:2605.16045) | **類型**: Exploration

## Source 1: H-MEM — Hierarchical Memory (EACL 2026)

**URL**: https://aclanthology.org/2026.eacl-long.15/ | **日期**: March 2026

### 核心：四層階層索引 + Position Encoding

H-MEM 的創新在於用**positional index encoding**取代 exhaustive similarity search。記憶分四層，按語意抽象度遞增：

| Layer | 抽象層級 | 對應 |
|-------|---------|------|
| Domain Layer | 最高 | section |
| Category Layer | 次高 | subsection |
| Memory Trace Layer | 次低 | subsubsection |
| Episode Layer | 最低（實際內容） | content |

每層的 memory vector 附帶 **positional index encoding**，指向下一層的子記憶。這使得檢索時可以 top-down layer-by-layer 逐步縮小範圍，不需要對全部記憶做相似度計算。

### 關鍵量化結果

**LoCoMo benchmark（5種QA任務）**：

| | H-MEM F1 | 基線最佳 F1 | 提升 |
|--|---------|-----------|------|
| Single-Hop | 26.37 (DeepSeek-R1 1.5B) | 24.67 (MemGPT) | +1.70 |
| Multi-Hop | 39.45 (DeepSeek-R1 1.5B) | 39.24 (A-Mem) | +0.21 |
| Adversarial | 63.30 (DeepSeek-R1 1.5B) | 58.81 (A-Mem) | +4.49 |

**計算效率**（vs MemoryBank flat retrieval）：
- Flat: O(a·10^6·D)，100ms+ latency
- H-MEM: O((a+k·300)·D)，<100ms even at max memory load
- 隨記憶體增長，flat 呈指數增長，H-MEM 緩慢線性增長

### 與前期探索的差異

H-MEM 的四層架構（Domain→Category→Memory Trace→Episode）與 A-Mem 的 Zettelkasten network 不同：
- A-Mem 是 graph-based associativ retrieval（找到一個 node 後沿 link 擴展）
- H-MEM 是嚴格的 top-down hierarchical routing，index pointer 是 discrete position，不是 semantic similarity

### Per-source Insight

- 層級數=4 是 accuracy/efficiency 平衡的最優點（ ablation 確認）
- User feedback 直接影響 memory weight：approval → strengthen，rebuttal → decay → 對應 heartbeat_learning.py 的 event-driven invalidation 需求
- **LoCoMo 對 H-MEM 的適用性**：LoCoMo 是 social dialogue，任務是 QA；H-MEM 在 open-domain adversarial 表現最好（63.3 vs 基線 58.81），但 single-hop 優勢不明顯（+1.7）

---

## Source 2: RecMem — Recurrence-Based Consolidation (ACL 2026 Findings)

**URL**: https://arxiv.org/abs/2605.16045 | **日期**: May 2026

### 核心：Not all interactions deserve LLM-level consolidation

RecMem 的核心問題意識：**現有系統對每個 incoming interaction 都做 eager LLM consolidation，造成巨大 token 浪費**。

RecMem 的解答：cognitive science 的 Atkinson-Shiffrin + CLS 框架——
> "isolated experiences remain in transient stores, only repeated/recurring patterns drive consolidation into stable long-term memory."

### 三層架構

```
Subconscious Memory (raw embeddings, no LLM)
    ↓ recurrence triggered (θcount, θsim)
Episodic Memory (LLM summarization, event-level)
    ↓ semantic refinement
Semantic Memory (atomic facts, user preferences)
```

**Consolidation 觸發條件**：
- New unit si → query Subconscious → get top-k by cosine similarity
- Filter to Ri = {sj | cos(si, sj) ≥ θsim}
- If |Ri| ≥ θcount → trigger consolidation (預設 θcount=5, θsim=0.7)

**Token 節省**：up to **87% reduction** in memory construction token cost vs Mem0/A-Mem/MemoryOS on LoCoMo.

### 關鍵 Innovation：Semantic Refinement

Episodic abstraction 會漏掉 fine-grained facts。RecMem 在 LLM abstraction 之後，再次回到 raw interactions 萃取值（persistent but omitted）→ 補進 semantic memory。

這剛好解決 A-Mem 的弱點（Zettelkasten consolidation 的 lossy compression）。

### Per-source Insight

- RecMem 和 H-MEM 都在解決「層級化記憶」的問題，但切入點不同：
  - H-MEM：從**組織結構**下手（index encoding + hierarchical routing）
  - RecMem：從**何時 consolidation** 下手（recurrence-triggered instead of eager）
- 兩者的底層假設一致：semantic abstraction 的顆粒度應該是**資訊密度高的 cluster**，不是 individual turn
- RecMem 的 subconscious store 是 RecMem 區別於所有其他系統的關鍵——其他系統做 eager consolidation，沒有「不 consolidated」的 raw buffer

---

## 跨論文 Synthesis

### 共同收斂點

1. **Layered/Structured > Flat embedding retrieval**：H-MEM 的四層 index encoding、RecMem 的三層（subconscious/episodic/semantic）、A-Mem 的 Zettelkasten network，都收斂到「pure vector similarity 不足以支撐 long-term memory」

2. **Triggered consolidation > Eager consolidation**：RecMem 的 recurrence-triggered 是 event-driven，而 H-MEM 是 user-feedback-driven（memory weight dynamic adjustment）。兩者都否定「每個 interaction 都 consolidation」

3. **Token cost 是瓶頸**：RecMem 量化了 eager consolidation 的代價（87% token 節省），H-MEM 量化了 flat retrieval 的代價（exponential vs linear growth）

### 差異互補

| 維度 | H-MEM | RecMem |
|------|-------|--------|
| 分層觸發 | hierarchical routing（組織） | recurrence detection（時機） |
| 索引機制 | positional index encoding（discrete pointer） | cosine similarity + threshold（continuous score） |
| Consolidation 觸發 | user feedback（rebuttal → decay） | recurrence count（θcount ≥ threshold） |
| Refinement | 無（LW 層級掩蓋了這個需求） | semantic refinement（彌補 abstraction loss） |

### 對 Hermes/Talos 的具體建議

#### WS-035 Drift Penalty Design 的新維度

1. **Consolidation trigger** 不只要靠 semantic contradiction（衝突驅動），也要靠 **recurrence**（頻率驅動）——資訊重複出現代表它值得 consolidated representation，反之代表可能已過時
2. **Subconscious store** 的概念可以直接移植：不是每個新的 distillate 都進長期記憶，先在 lightweight buffer 等 recurrence signal
3. **Memory weight** 的動態調整（H-MEM）對應 event-driven invalidation：user approval/rebuttal → 直接影響 confidence，不必等 time-based decay

#### heartbeat_learning.py 架構建議

```
Current: distillate → (no staleness check) → retrieval
Proposed:
  distillate → [recurrence check: has this concept recurred?]
             → [contradiction check: does new info conflict?]
             → if neither: time-based decay (half-life=38d)
             → if recurrence without contradiction: strengthen
             → if contradiction: immediate staleness标记 + invalidation
             → consolidated representation stored in structured format
```

#### H-MEM 的 Position Index 可以移植到 Hermes Skills

Skills 的分層（trigger condition → action → verification）本質上也是 hierarchical routing：higher layer（如 skills list）指向具體 skill，skill 內部又有 steps。Position index 概念可以讓 skill retrieval 不需要遍歷所有 skills。

---

## 未追蹤 Leads

- ~~RecMem~~ — 已fetch（arxiv:2605.16045），本篇完整覆蓋
- ~~H-MEM~~ — 已fetch（EACL 2026.eacl-long.15），本篇完整覆蓋
- Memory OS (Kang et al., EMNLP 2025) — RecMem 的 comparison baseline 之一，有三層架構（Short/Mid/Long-term），但不如 RecMem 和 H-MEM 的設計精緻
- Zep Temporal Knowledge Graph — RecMem taxonomy 提到，graph-based consolidation，URL 待確認
- LongMemEval-S benchmark（500 conversations, 115k avg tokens）— RecMem 使用的第二個 benchmark，可作為 Hermes memory benchmark 的參照

## ✅ 本次探索完成

