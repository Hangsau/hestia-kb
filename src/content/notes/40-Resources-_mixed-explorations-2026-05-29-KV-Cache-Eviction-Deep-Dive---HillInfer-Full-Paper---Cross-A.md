---
_slug: 40-Resources-_mixed-explorations-2026-05-29-KV-Cache-Eviction-Deep-Dive---HillInfer-Full-Paper---Cross-A
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-KV-Cache-Eviction-Deep-Dive---HillInfer-Full-Paper---Cross-A.md
title: KV Cache Eviction Deep Dive — HillInfer Full Paper + Cross-Architecture Synthesis
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- bidirectional
- cache
- eviction
- full
- hermes
- hillinfer
- pinning
- pool
- priority
- temporal
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

---
title: "KV Cache Eviction Deep Dive — HillInfer Full Paper + Cross-Architecture Synthesis"
date: 2026-05-29
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [aware, cache, eviction, hardware, hillinfer, hit, llm, memory, priority, scheduling, smartssd]
---

# KV Cache Eviction Deep Dive — HillInfer Full Paper + Cross-Architecture Synthesis

**日期**: 2026-05-29 | **Topic**: HillInfer full paper deep-dive + cross-architecture synthesis with TRT-LLM and HotPrefix

---

## 延續自

**延續自**: [[2026-05-29-Hardware-Aware-KV-Cache-Eviction---LLM-Inference-Optimizatio]]

本次 fetch 完整論文（full HTML），補充摘要版缺失的實作細節，並與同日探索的 TRT-LLM priority eviction API 交叉合成。

---

## Per-Source Insights

### HillInfer Full Paper — Key Details Not in Abstract

**HKM: Bidirectional KV Cache Pools (BKP)**

三層啟發對 Hermes 記憶管理的對應：
1. **Temporal-Aware Pinning** = session pinning（最近 N 個事實持續 retain，重要性 >> 舊的）。HillInfer 靜態鎖定 recent α·N tokens 在 Hot Pool，防止 PCIe傳輸。Hermes 對應：session context 內的 recent facts 不應該主動 evict，即使 global relevance score 下降
2. **Frequency-Aware Tracking** = attention sink tracking。HillInfer 維護一個 2N bytes 的 KV Cache Hit-Rate Table（global）。Hermes 可以對應：每個 entity 的 access frequency tracking，用於區分「經常被提起」和「曾經重要但已過時」的 facts
3. **Bidirectional Promotion/Demotion** = 動態升降級。cold token 在 SmartSSD 突然變重要 → 立即 promote 到 CPU Hot Pool；同等 volume hot token demote 到 Cold。Hermes 對應：entity 隨對話重新被提起時，應從「cold archive」promote 回 active working memory

**APP: Adaptive Prefetch-based Pipeline**

核心：analytical latency model 平衡 CPU 和 SmartSSD 的工作負載。
公式：`TCPU = Mc/fc + αMc/Bc ≈ Ms/fs + αMs/Bs = TSmartSSD`
目標：讓兩個設備同時完成，避免 straggler（ faster processor 等 slower processor）。

對 Hermes 的啟發：不同的「記憶壓縮」目標（fast distill vs. thorough distill）也可以用類似的 latency model 平衡——不想浪費 compute 在已經足夠 compression 的事实上。

**CEC: Asymmetric Precision — 對 Hermes 的啟發**

HillInfer 在 FPGA 上用 INT8/INT4 做重要性評估，拿到 top-K indices 後才 retrieve 原始 FP16 KV。
→ Hermes 的 memory distillation 也可以用類似思路：先用 lightweight hash/signature 評估 fact 是否有重複（INT8 equivalent），確認值得 retain 後再做完整的 semantic embedding（FP16 equivalent）。

**I/O Thrashing 的量化**

HillInfer 指出 naive eviction 會導致「每個 decoding step 都在 CPU 和 SSD之間來回 ping-pong」。解決方案是 partition + bidirectional pools。
→ Hermes heartbeat 的重複問題（同一個指紋連續錯誤）：本質上也是一種 I/O thrashing——系統在「處理」和「抑制」之間來回震盪，沒有 partition 就會導致震盪持續。解決方案：partition 為「已知問題抑制池」和「新問題探索池」， bidirectional 就是在抑制無效時 promote 到更嚴重的 escalation。

**Hit-Rate Table 的資源成本**

HillInfer 的 Hit-Rate Table = 2N bytes for N tokens。OPT-6.7B with 32K context ≈ 64KB overhead。
→ Hermes 的 entity access frequency tracking：每個 fact 的 access count + last_access timestamp。N facts × (4 bytes count + 8 bytes timestamp) ≈ 12N bytes。如果有 10,000 facts，≈ 120KB，完全可接受。

---

## Cross-Architecture Synthesis

### KV Cache Eviction ↔ Hermes Lifecycle Governance

| KV Cache Concept | Hermes Equivalent | Implication |
|-----------------|-------------------|-------------|
| Hot Pool (CPU DRAM) | Active session context | 最近的事實/工具使用 = pinned |
| Cold Pool (SmartSSD) | Vault/archived knowledge | 不常訪問的內容 = cold storage |
| Bidirectional promotion | Entity re-activation in conversation | 話題重現時自動 promote |
| Hit-Rate Table | Access frequency tracking | 區分「經常被提起」vs「曾經重要已過時」|
| I/O Thrashing | Doom-loop (same fingerprint errors) | Partition + bidirectional 解決震盪 |
| α (retention ratio 10-20%) | Context window budget | 必須 eviction 才能容納新內容 |
| Straggler effect | Resource contention | 必須 balance 否則某設備空轉等另一個 |

### Priority-Based Eviction API (TRT-LLM) ↔ Hermes Tool Permission Gradient

TRT-LLM 的 `TokenRangeRetentionConfig {start, end, priority, duration}` 明確表達「這段 KV cache 重要程度」。
→ Hermes 的 tool permission 也可以用類似 API：`ToolPermissionConfig {tool, session_id, priority, duration}`。System prompt tools = priority=100, user tools = priority=50, experimental tools = priority=10。Duration 控制何時降級。

### Staleness (Mem0 Blog) ↔ HillInfer Temporal Pinning

Mem0 的 staleness problem：「用戶換公司後，高相關性記憶變成 confidently wrong」。
HillInfer 的 solution：「temporal locality — recently generated tokens are extremely likely to remain critical for immediately following steps」。

Synthesized insight：staleness 的根本解法不是 decay（BM25 之類的時序衰減），而是**事件驅動 invalidation + temporal pinning 的組合**：
- 用戶換公司 = 觸發事件 → 對「前公司」相關 facts 全部降 priority 並加 stale flag
- Temporal pinning 確保「當前公司」相關 facts 留在 Hot Pool
- 兩者結合 = HillInfer 的 bidirectional promotion/demotion 概念應用於事實蒸發

---

## 未追蹤 Leads

- `https://arxiv.org/abs/2602.18750` — HillInfer full PDF（已 fetch HTML；PDF 未 fetch）
- `https://cs.nju.edu.cn/tianchen/lunwen/2026/sigmod26-liyuhang.pdf` — HotPrefix SIGMOD 2026 full paper（Phase 1 未驗證）
- SGLang RadixAttention internal eviction policy — 需從 GitHub source code 驗證（Contents API fetch）
- Mooncake global cache directory — 需 fetch 確認 cross-cluster KV-aware routing 實作

## Hermes Relevance

- **Hit-Rate Table (2N bytes)**: Lightweight entity access frequency tracking，適用於 Hermes facts.jsonl 的 staleness detection
- **Bidirectional promotion/demotion**: 對 Hermes session re-activation 的具體實作啟發（old fact 被重新提起時從 vault promote 回 working context）
- **I/O Thrashing pattern**: 對 DoomLoopTracker 的修復——partition "known issue suppress pool" vs "new issue explore pool"
- **Asymmetric precision distillation**: 先用 lightweight signature 評估 fact 重複度，再做完整 semantic embedding——可用於 memory distillation 的兩階段 pipeline
- **Staleness + Temporal Pinning synthesis**: 事件驅動 invalidation + temporal pinning 組合 = 根本解決 Mem0 staleness problem 的可行架構

## ✅ 本次探索完成

