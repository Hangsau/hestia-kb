---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索筆記-LLM-上下文管理---KV-Cache-壓縮與文件壓縮
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索筆記-LLM-上下文管理---KV-Cache-壓縮與文件壓縮.md
title: 探索筆記：LLM 上下文管理 — KV Cache 壓縮與文件壓縮
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- cache
- context
- llm
- min
- prompt
- skf
- token
- tokens
- zsmerge
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索筆記：LLM 上下文管理 — KV Cache 壓縮與文件壓縮

**日期**: 2026-05-22
**探索者**: Hestia
**主題**: LLM 上下文管理（KV Cache 壓縮 + 文件上下文壓縮）

## ✅ 本次探索完成

---

## Source 1: ZSMerge — Zero-Shot KV Cache Compression

**來源**: arXiv:2503.10714 | 65 pts, 19 comments
**URL**: https://github.com/SusCom-Lab/ZSMerge

### 核心貢獻

**ZSMerge** 是一套 zero-shot KV cache 壓縮框架，三個關鍵設計：

1. **三元分配預算**（Tripartite budget）: 把 cache 切成三個組件
   - `Bₚ`（proximity）：保留最近 N 個 token，維護 local pattern
   - `Bᶜ`（context）：根據 contribution score 保留最高分 token
   - `Bᵣ`（residual）： evicted token 動態合併到壓縮槽，透過相似度驅動的 aggregate

2. **Residual token merging**：低分 token 被驅逐時，不直接丟掉，而是合併進 residual slot。合併時用 dot-product 找最相似的 slot，合併後以 `log(wᵢ)` 補償 attention score（防止 merged token 被低估）。

3. **Zero-shot**：不需要 retraining 或 fine-tuning，適用於 LLaMA、Falcon、Mistral、Qwen、Yi 等多種架構。

### 關鍵數據

- **LLaMA2-7B**：20:1 壓縮比（cache 降至 baseline 的 5%），54k token 上下文時 throughput 提升 3x
- **InfiniteBench（100K+ token）**：達到 FullKV 的 96.8% 效能（52.95 vs 54.69 avg）
- **LongBench（512/1024 token cache）**：在多數任務與 SnapKV 持平或略優
- **Hyperparameters**：Bp/B = 0.5（proximity ratio），Br/(B-Bp) = 0.02（residual ratio），α = 1.0（scale factor）

### 與其他方法的比較

| 方法 | 特性 | 限制 |
|------|------|------|
| H2O / StreamingLLM | 純 sparse eviction（永久丟棄低分 token） | attention distribution drift，資訊丟失 |
| SnapKV | prefilling 時一次性 pruning | 無動態調整 |
| LESS | 需要 auxiliary networks + fine-tuning | 部署成本高 |
| ZSMerge | sparse + residual，zero-shot | — |

### Hermes 啟發

**直接相關**：這正是 WS-025（B+ tree phase navigation）探討的「如何在長 session 中管理不斷增長的 KV cache」的實際解法之一。ZSMerge 的 insight 在於：
- **不需要 B+ tree**——residual merging 的機制比 tree 更簡單，卻足夠有效
- **三元分配 + decay score** 是一種輕量級的「重要性追蹤」，可用於替代昂貴的 tree 結構
- **架構無關**（zero-shot）：這意味著任何 LLM 都適用，不只是特定模型

**可以提煉的 pattern**：Agent 對話歷史的「重要性」可以用 decay accumulation 追蹤（λ=0.98），而不是簡單的「最近 N 條」或「輪次計數」。這比 naive sliding window 更聰明，比 full tree 更輕。

---

## Source 2: llm-min.txt — AI-Powered Documentation Compression

**來源**: GitHub marv1nnnnn/llm-min.txt | 678 stars, 177 pts, 52 comments
**URL**: https://github.com/marv1nnnnn/llm-min.txt

### 核心概念

`llm-min.txt` 用另一個 LLM（預設 Gemini 2.5 Flash）把冗長的技術文件（原始可達 800K+ tokens）壓縮成 **SKF（Structured Knowledge Format）** 格式，達成 90-97% 的 token 節省。

### SKF 格式結構

```
# IntegratedKnowledgeManifest_SKF/1.4 LA
# SourceDocs: [origin]
# GenerationTimestamp: ...
# PrimaryNamespace: <top-level package>

# SECTION: DEFINITIONS (Prefix: D)
D001:G001_Entity [DEF_TYP] [NAMESPACE "path"] [OPERATIONS {op:RetT(p:T)}] [ATTRIBUTES {attr:Type}] ("Note")

# SECTION: INTERACTIONS (Prefix: I)
I001:Source INVOKES Target ("Note_Conditions_Error(Gxxx_ErrType)")

# SECTION: USAGE_PATTERNS (Prefix: U)
U_Name.1:[Actor] ACTION_KEYWORD (Target) -> [Result]
U_Name.2:[Actor] ACTION_KEYWORD -> [Result]
```

### 三步 pipeline

1. **Glossary Generation**：每個 chunk 抽 entity → merge 成 global glossary（Gxxx IDs）
2. **Definitions & Interactions**：每 chunk 生 D/I items，累計 global IDs
3. **Usage Patterns**：每 chunk 生 U items（含 numbered steps）

### 對比 llms.txt

| 特性 | llms.txt | llm-min.txt |
|------|---------|-------------|
| 格式 | Markdown（人類可讀） | SKF（機器優化） |
| 壓縮率 | 通常仍很大（數十萬 tokens） | 90-97% 節省 |
| 互動性 | 靜態文件 | AI 生成，可視化結構 |
| 適用範圍 | 通用 | 高度結構化的技術文件 |

### Hermes 啟發

**與 context-distiller 的潛在整合**：`context-distiller` 已經做了 input 層的萃取。llm-min 的 SKF 格式提供了一個更結構化的輸出格式——DEFINITIONS/INTERACTIONS/USAGE_PATTERNS 三段式比純散文更容易被 agent 快速檢索。

**應用場景**：
- 把 Hermes skill 文件壓縮成 SKF → agent 在推理時可以更精確地「定位」該用哪個工具
- 把 `references/` 下的藍圖文件從「描述性 Markdown」轉成「機器可解析的 SKF」

**代價注意**：需要 Gemini API，$0.01-$1.00 per library。對 Hermes 內部的檔案（本地文件），可以用 `--input-folder` 離線處理，但還是需要 LLM 做 distillation。

---

## Source 3: Prompt Caching Deep Dive（ngrok blog）

**來源**: ngrok.com/blog/prompt-caching/ | 306 pts, 72 comments | 6,034 words
**作者**: Sam Rose（ngrok Senior Developer Educator）

### 核心機制

這篇文章解釋了為什麼 prompt caching 會比一般 input tokens 便宜 10x——provider 在做的事情是：

**Cache K（Key）和 V（Value）矩陣**，而非整個 prompt。

完整推理 loop（無 cache）：
```
prompt → tokenize → embed → [attention* → feedforward*] → output token
                                             ↑
                                   每個 token 都要重算所有歷史的 attention
```

KV Cache 的真相：
1. 每次 decode step，Q 是新的（只看 current token），但 K 和 V 是從 **所有歷史 token** 來的
2. 歷史的 K 和 V 不會變（新 token 只追加到末尾）
3. 所以：**K 和 V 矩陣可以 cache，Q 每次重算**

Provider 做的事情：
- Request 完成後，保留這段對話的 K/V 矩陣 5-10 分鐘
- 下個 request 如果有相同前綴，直接用 cache 的 K/V，不需要重算
- 客戶端只付便宜 10x 的「cached input tokens」費用

### Anthropic vs OpenAI 的差異

| 特性 | Anthropic | OpenAI |
|------|-----------|--------|
| 控制粒度 | 手動指定 cache，100% hit rate | 自動嘗試，~50% hit rate |
| 成本 | 稍貴但可預測 | 便宜但 latency 不穩定 |
| 適合場景 | 長上下文、需要 predictable latency | 短/中 context |

### 與 ZSMerge 的關聯

這篇文章解釋了 ZSMerge 存在的層級：**Provider 層**（cache K/V between requests），**模型層**（cache K/V within a session via KV cache），**應用層**（如何組織 prompt 以最大化 cache 命中率）。

ZSMerge 在做的事情是：**模型內的 KV cache 壓縮**（當 cache 太大、GPU 不夠時），與 provider 層的 KV cache 是不同的優化方向。

### Hermes 啟發

**Prompt 設計的直接影響**：如果 Hermes 每次 heartbeat 的 system prompt 有大量重複內容（skill descriptions、context、system map），這些會持續佔用 input tokens。優化方向：
- 最小化 system prompt 的動態內容（把 stable 內容固化為 cached context）
- 讓每個新 request 的前綴最大程度與前一個 request 重疊（提高 provider-side cache 命中率）

---

## 跨文章 Synthesis

### 主題：LLM 上下文管理的三個層次

從這三篇文章可以歸納出一個框架：

```
┌─────────────────────────────────────────────────────────┐
│ Layer 3: 文件/知識壓縮 (llm-min)                          │
│ 把外部文件從 800K tokens → 10K tokens，SKF 格式          │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Agent Memory 壓縮 (ZSMerge 啟發)                │
│ 對話歷史用 decay-score 追蹤重要性，三元分配而非 naive window│
├─────────────────────────────────────────────────────────┤
│ Layer 1: Provider KV Cache (ngrok 揭示)                  │
│ 跨 request 的 K/V 矩陣共享，10x cost 節省                │
└─────────────────────────────────────────────────────────┘
```

### 共同的 design pattern

三篇文章都指向同一個核心原則：**不是把所有東西都留住，而是聰明地決定什麼值得留、什麼值得壓縮**。

- ZSMerge：三個 budget compartment + decay score → 決定哪些 token 值得留
- llm-min：AI distillation → 決定哪些文件 detail 值得保留
- ngrok prompt caching：Provider cache → 決定哪些 K/V 矩陣值得跨 request 共享

### 對 Hermes 的實用建議

1. **Prompt 設計**：如果 system prompt 有 500+ tokens 的 stable content，每次 request 都重複送 → 浪費且低效。考慮把 stable 部分抽出來作為 cached prefix。
2. **Session memory**：用「最近 N 條」或「最近 M 分鐘」太粗糙。引入 decay accumulation 追蹤每段對話的 contribution score，做更聰明的 sliding window。
3. **檔案 ingestion**：把 `references/` 的藍圖文件從 Markdown 轉成 SKF 格式，提高 agent 的檢索效率。

---

## 未追蹤 Leads

- https://github.com/GibsonAI/memori（Memori — Dual-Mode Memory Layer，4 pts）
- https://arxiv.org/abs/2502.14051（Accelerating Long-Context LLM Inference via Two-Stage KV Cache Compression，4 pts）
- https://github.com/salishforge/memforge（PostgreSQL-only agent memory，92% on LongMemEval）
- https://steve-yegge.medium.com/introducing-beads-a-coding-agent-memory-system（Steve Yegge 的 coding agent memory system，被 Cloudflare block）
