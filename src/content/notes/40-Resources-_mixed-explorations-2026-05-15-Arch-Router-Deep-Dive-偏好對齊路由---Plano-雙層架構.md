---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Arch-Router-Deep-Dive-偏好對齊路由---Plano-雙層架構
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Arch-Router-Deep-Dive-偏好對齊路由---Plano-雙層架構.md
title: Arch-Router Deep Dive：偏好對齊路由 + Plano 雙層架構
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- arch
- filter
- hermes
- llm
- model
- plano
- router
- routing
- tool
- turn
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# Arch-Router Deep Dive：偏好對齊路由 + Plano 雙層架構

**延續自**: [[2026-05-15-arch-router-preference-routing]] 的未追蹤 lead（Arxiv 論文全文 + Plano filter chains + Plano Orchestrator）

**日期**: 2026-05-15 | **來源**: arxiv.org/abs/2506.16655, docs.planoai.dev, huggingface.co/katanemo

---

## Source 1: Arch-Router 論文 (arxiv 2506.16655)

### 核心設計

Arch-Router 是一個 1.5B 的 generative model，把 LLM routing 重新定義為**偏好對齊問題**而非性能優化問題。

架構關鍵：**解耦路由選擇與模型分配**。$R = T ∘ F$，其中：
- $F$（Arch-Router）：query + 所有 route policies → 選出最佳 route policy
- $T$：route policy → LLM model 的靜態 mapping（可以隨意改，不用重訓練）

這和傳統 routing（RouteLLM 用 quality score 選 model）的根本差異：Arch-Router 不猜哪個 model 最好，而是「忠實映射用戶意圖到用戶定義的 policy」。品質判斷權在用戶手裡，不在 router 手裡。

### Route Policy 機制

用戶用 Domain-Action Taxonomy 定義 policy（例：`finance/summarization` → GPT-4o, `code/explanation` → Claude）。兩個關鍵組件：
- **Domain**：高層主題（travel, legal, healthcare）
- **Action**：具體操作（summarization, code generation, image editing）

如果 query 模糊到無法 match Action，router 可以 fallback 到 Domain-level routing — 比 flat list of composite labels 更 robust。

### Benchmark 結果

| 模型 | 整體準確率 | 延遲 (ms) |
|------|-----------|----------|
| **Arch-Router** | **93.17%** | **51±12** |
| Claude-Sonnet-3.7 | 92.79% | 1450±385 |
| GPT-4o | 89.74% | 836±239 |
| GPT-4o-mini | 82.79% | 737±164 |

關鍵數字：**28 倍**快於 Claude-Sonnet，同時準確率更高。這不是 trade-off — 是兩個維度都贏。

Multi-turn SGD benchmark（最難的場景）：
- Span accuracy: Arch 91.68% vs Claude 89.04%
- Full-conversation: Arch 90.05% vs Claude 87.29%

### Error Pattern 分析（很有啟發性）

Arch-Router 的失敗集中在 **turn 1**（初始意圖模糊時），一旦正確辨識意圖就高度穩定。Claude-Sonnet 相反 — turn 1 較不敏感，但後續 turn 容易 drift。

→ 這暗示 Arch-Router 的弱點是「冷啟動意圖辨識」而非「上下文追蹤」。如果 Hermes 要做類似 router，turn-1 disambiguation prompt 可能是關鍵。

### vs RouteLLM（Appendix C 對比）

11-turn coding conversation：Arch-Router 8/8 正確，RouteLLM 只對 5/8。RouteLLM 在三個 context-dependent follow-up 上失誤（"This doesn't work"、"runs too slow"、"Any other ones?"）— 因為它用 quality score 預測而非意圖追蹤。

## Source 2: Plano Filter Chains

Filter chains 是 Plano 的 dataplane programming model — 一個有序的 HTTP/MCP mutation pipeline：

```
Request → [Guardrails] → [Query Rewriting] → [RAG/Memory] → Agent/LLM
```

每個 filter 是獨立 HTTP/MCP service，用 HTTP status code 溝通：
- 200：通過，可 mutate request
- 4xx：政策拒絕（expected user-facing policy）
- 5xx：filter 崩潰（fatal）

和 Hermes tool pipeline 的相似性：都是 sequential mutation。差異：
- Hermes 的 tool calling 是 LLM 決策的（LLM 決定何時 call 什麼 tool）
- Plano 的 filter chains 是 **deterministic proxy-level pipeline**（request 一律經過，不經 LLM 判斷）

→ 這兩種模式不互斥。Plano 的模式適合安全/合規層（rule-based），Hermes 的模式適合靈活決策層。理想設計可能是 hybrid：proxy-level guardrails + LLM-driven tool selection。

## Source 3: Plano-Orchestrator（4B/30B）vs Arch-Router

Plano-Orchestrator 和 Arch-Router 是**兩個不同的模型，服務不同層級**：

| | Arch-Router (1.5B) | Plano-Orchestrator (4B/30B) |
|---|---|---|
| 用途 | LLM routing（選哪個 model） | Agent orchestration（選哪些 agent） |
| 輸出 | 單一 route | 多 route 陣列 |
| Multi-intent | ❌ | ✅（單一訊息 → 多 agent） |
| 基礎模型 | 未公開（推測 Qwen-based） | Qwen3-4B-Instruct |
| 評估規模 | ~43k training samples | 1,958 messages / 605 conversations / 130+ agents |

→ 這是 Plano 的**雙層 routing 架構**：下層 Arch-Router 選 LLM，上層 Plano-Orchestrator 選 agent(s)。兩層互補，不是競爭。

---

## Hermes 啟發

### 1. 偏好對齊 vs 性能最優 — 對 skill 系統的啟發

Hermes 的 skill description 欄位和 Arch-Router 的 route policy description 在做同一件事：用自然語言描述能力，供 LLM 匹配。但 Hermes 把匹配和執行綁在一起（LLM 自己讀 description → 自己決定載入 → 自己執行）。

Arch-Router 的關鍵洞察：**解耦匹配和執行**。如果可以分離：
- 匹配層：skill description → query 匹配（可以 cache、可以 optimize）
- 執行層：skill 內容載入 + tool calling

→ 就可以在匹配層做優化（cache frequent matches、pre-load likely skills）而不影響執行層。

### 2. Filter Chains 的確定性 pipeline — hybrid 設計可能性

Plano 的 filter chains 是 rule-based pipeline，Hermes 的 tool calling 是 LLM-driven。兩者結合的 hybrid pattern：
```
User query → [proxy-level guardrails] → LLM-driven tool selection → [tool execution pipeline] → response
```

但這需要一個 proxy layer（MCP gateway 或類似），目前 Hermes 沒有。這是之前 contextforge SPIKE 探索過的領域。

### 3. 28x 延遲優勢 — 1.5B 專用路由器的價值

51ms vs 1450ms 的差距讓人認真考慮：值不值得為 Hermes 跑一個專用的 skill router？目前 Hermes 的 skill 載入完全依賴主 LLM 的推理（每次載入一個 skill 就要跑一次 LLM call）。如果有一個輕量 router 預測「這個 query 可能需要哪些 skills」，可以 pre-load 減少 round trips。

但 1.5B 模型的部署成本（需要 GPU instance）vs 收益（節省 LLM round trips）需要量化。DeepSeek v4-pro 的推理延遲是多少？如果已經夠快，專用 router 的邊際價值可能不大。

### 4. Error pattern 的設計啟發

Arch-Router 的 turn-1 脆弱性很有意思。如果 Hermes 遇到類似的「初始意圖模糊」問題，解法可能是：
- 在 first turn 加入 disambiguation prompt（"如果意圖不明確，先問 clarifying question"）
- 或者在 skill description 中加入 trigger keywords（類似 Arch-Router 的 Domain-Action 層級）

---

## 未追蹤但值得注意

- **Plano-Orchestrator 的 Long-context evaluation**（235 messages）— README 有 benchmark 但沒具體數字。如果 long-context routing 準確度夠高，可能對 multi-session memory routing 有啟發。
- **Plano 的 dataplane 完整架構**（還有 tracing、observability、agent listener vs model listener）— 比 filter chains 更完整。Hermes 的 heartbeat EVOLVE 已經有類似 observability 功能，但沒有 dataplane 概念（所有的 tool execution 都在同一個 process 裡）。
- **RouteLLM 的 quality score 方法**（Ong et al., 2024）— 雖然被 Arch-Router 超越，但 cost-performance trade-off 的框架對 Hermes 的成本管理有參考價值。特別是多 model scenario 下如何做 cost-aware routing。
- **FrugalLLM**（Chen et al., 2024）— 從更大 pool 選 model + budget constraint。如果 Hermes 未來要支援多 provider 動態切換，這個 paper 的 budget-aware selection 機制值得看。

