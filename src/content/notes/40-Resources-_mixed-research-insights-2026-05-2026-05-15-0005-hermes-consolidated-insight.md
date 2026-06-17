---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-0005-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-0005-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: high
title: 約束即解放：agent 架構的兩個深層模式
updated: '2026-06-15'
type: research
status: budding
---

# 約束即解放：agent 架構的兩個深層模式

**消化筆記**:
- 2026-05-14-statewright-state-machine-guardrails
- 2026-05-14-context-mode
- 2026-05-14-llm-evaluation-landscape
- 2026-05-14-compaction-context-rot-handbook
- 2026-05-14-agent-cost-curve
- 2026-05-14-beads-agent-memory

把六篇筆記攤開看，兩個跨主題模式浮出來：一個是設計哲學層的（越限制越強大），一個是系統工程層的（cost/quality/context 根本是同一個問題的三個投影）。每個模式都有至少三篇獨立筆記交叉驗證。

---

## Cross-Cutting Theme 1: 約束作為能力倍增器（Constraint as Enabler）

**支援筆記**: statewright, context-mode, compaction-context-rot-handbook

三篇筆記來自完全不同的領域——tool 權限、output 壓縮、context 管理——但它們共享同一個深層邏輯：**對 LLM agent 而言，移除選項比增加能力更有效**。

### 證據鏈

1. **Statewright**：同一台機器、同一個模型，只加了 state machine 約束（per-state tool whitelist + Bash discernment + edit guardrails），local 13.8GB 模型從 2/10 → 10/10。不是讓模型更聰明，是讓問題更小。

2. **Context Mode**：把 raw tool output（56 KB Playwright snapshot、986 KB subagent 輸出）壓到 299 B 和 62 KB，session 可維持時間從 ~30 min → ~3 hr。不是給模型更多 context，是只給它「計算結果」。

3. **Compaction handbook**（Chroma Research 數據）：context quality 在 **25%** window fill 就開始下降，不是 100%。維持 40-60% utilization 的 agent 表現比「塞滿全部可用 context」的 agent 更好。不是保留更多，是保留更少。

### 為什麼這不是巧合

三個案例中，改善的機制不同但底層原理一致：LLM 的 attention 是稀缺資源。Statewright 減少的是 **decision space**（40 tools → 5 tools），Context Mode 減少的是 **information noise**（raw data → computed result），Compaction 減少的是 **temporal noise**（舊對話干擾新決策）。三者都在幫 attention 聚焦。

### 這對 Hermes 設計的含義

目前 Hermes 的設計直覺是「給 agent 越多能力越好」——全 tools 可用、全 context 保留、全 output 進 window。這六篇筆記的集體證據指向相反方向：**下一個重大效能跳躍不會來自更好的模型或更聰明的 prompt，會來自更精準的限制**。

具體來說：
- ContextForge MCP gateway 應該做 per-phase tool gating，不是「建議 agent 少用」，是「不該用的 tool 直接不存在於 tool list」
- Compaction 觸發時機不該等 LLM 自己發現（目前模式），heartbeat 應在每輪後檢查 token usage，超過 60% 就主動觸發
- terminal 輸出不該全量進 context——Context Mode 的 sandbox 模式值得在 Hermes 的 terminal tool 上做輕量版

### 可行動下一步

1. **在 ContextForge MCP gateway 實作最小可行 tool gating**：為三個 phase（planning/implementing/testing）各定義 allowlist，gateway 在轉發 tool list 時過濾。不需要 Rust engine 或完整 state machine——三個 phase 的 tool set 差異只有 2-3 個 tool，簡單的 allowlist 就夠。
2. **在 heartbeat 加 context utilization check**：每輪結束後算 `used_tokens / context_window`，超過 60% 時自動觸發 compaction 而非等 LLM 決定。這直接實作 40-60% 規則。

---

## Cross-Cutting Theme 2: Cost、Quality、Context 是同一個問題的三個投影

**支援筆記**: agent-cost-curve, compaction-context-rot-handbook, context-mode, llm-evaluation-landscape

這是最強的跨主題發現。四篇筆記各自討論看似獨立的問題——API 費用、agent 行為品質、context window 管理——但放在一起看，它們根本是同一個底層動態的三個面向。

### 三位一體的證據

| 面向 | 筆記 | 核心發現 |
|------|------|---------|
| **Cost** | agent-cost-curve | LLM agent 成本是 O(n²)，cache reads 在 ~27K tokens 後主導 |
| **Quality** | compaction-handbook | Context quality 在 25% fill 就開始降；LLM-as-judge 不一致 |
| **Context** | context-mode | 98% compression 讓 session 從 30 min → 3 hr |

關鍵洞察：**同一個 token 同時佔用三個資源**。它在 context window 佔空間、在 prompt cache 產生費用、在 attention 機制中稀釋品質。你不能只優化一個——壓縮 output（Context Mode）同時省錢、省空間、提升品質。放任 context 膨脹（無 compression、無 compaction、無 tool gating）同時在三個維度上累積債務。

### 具體的交互效應

- **Context → Cost**：O(n²) 成本曲線意味著 compaction 不只是品質優化，是直接的省錢手段。每砍掉 10K tokens 的歷史對話，不只讓下個 turn 更準，還讓下個 turn 的 cache read 便宜 10%。
- **Cost → Quality**：沒有 cost visibility 的 agent（Hermes 現狀）無法做 cost-quality tradeoff。如果 DeepSeek 便宜到不在乎，那應該跑更多 parallel subagent 做 isolation（compaction handbook Defense 5：multi-agent isolation 改善 90.2%）——但不知道成本就沒辦法做這個決策。
- **Quality → Context**：DeepEval 的 MCP metrics 和 compaction 的 40-60% 規則指向同一個需求：需要可量化的信號來判斷「何時該 compact」。目前 Hermes 靠 LLM 自己判斷，但 LLM 自己就是在 context rot 中運作的那個——讓它自評 context 品質是循環論證。
- **Cost → Context**：agent-cost-curve 筆記的 meta-point——「start a new conversation 通常比 continue 便宜」——直接挑戰 Hermes 的 auto-continue 設計。auto-continue 的 1h window 假設是「保持 conversation 活著比較好」，但 O(n²) 證據說：有時候重建 context 的 cache write cost < 繼續付 cache read tax。

### 這改變了優先級

原本這六篇筆記各自建議了不同的 next step：
- Cost curve → 加 token tracking
- Compaction → 加 40-60% compaction trigger
- Context Mode → 加 output compression
- Evaluation → 加 MCP metrics

但如果你理解這三個是同一件事，**最優雅的下一步不是分別做四個功能，而是一個 instrumentation point 同時服務三個目標**：

> **在 heartbeat 加 token counting**

這一個動作同時：
1. 給 cost visibility（cost curve 筆記的 Level 1）
2. 提供觸發 compaction 的客觀信號（compaction 筆記的 40-60% 規則）
3. 提供 context utilization 數據，用來評估 compression 的效益（Context Mode 筆記）
4. 為未來的 quality metrics 提供 baseline——正常 session 的 token 分佈長怎樣，異常 session 長怎樣（evaluation 筆記的方向）

### 可行動下一步

1. **在 heartbeat provider_health 加 token/cost tracking**：最簡單的實作——provider_health 已經在監控，加一個 token counter（從 API response 的 `usage` field 抓）。不改任何行為，純累計。
2. **跑一次 token audit**：用現有 session logs 回推過去一週的 token 消耗分佈。驗證 O(n²) 曲線在 Hermes 的實際 conversation 長度下是否成立。如果 typical conversation < 10K tokens（cost curve 筆記的 open question），quadratic curve 不適用，那整個 cost-quality-context trilemma 的緊急程度會不同——但先有數據再說。

---

## 附帶發現：Protocol-Layer Enforcement 作為 2026 的收斂方向

**支援筆記**: statewright, context-mode, llm-evaluation-landscape

Statewright 在 protocol 層（MCP）做 tool gating、Context Mode 在 protocol 層（PreToolUse hook）做 output routing、Confident AI 在 protocol 層（MCP server）做 evaluation——三個獨立專案不約而同把 enforcement/optimization 從 prompt 層拉到 infrastructure 層。這不是巧合，是 2026 上半年 agent 工程的關鍵轉向：**不再信任 LLM 自我監管**。

Hermes 的 ContextForge MCP gateway 已經坐在這個 architectural sweet spot 上——它是 protocol 層的 middleman。Theme 1 的 tool gating、Theme 2 的 token counting、Context Mode 的 output compression，全部可以在 gateway 層實作，不需要動 Hermes agent 本體。這是架構上的幸運：gateway 當初的設計意圖是整合外部 MCP servers，但它的位置恰好也是做 enforcement 的理想位置。

### 可行動下一步

ContextForge 下一個功能優先級應該是 **enforcement 而非 integration**。與其接更多 external MCP server，不如先把 per-phase tool gating + token tracking 做進去。

---

## 彙總：下一步行動清單（依優先級）

1. **[最高優先] Heartbeat token counting** — 一個 instrumentation point，服務 cost/quality/context 三個目標。改 `provider_health` skill，從 API response 抓 `usage.total_tokens`，累計寫入 `~/.hermes/metrics/token_usage.jsonl`。估計改動量 < 50 行。

2. **[高優先] ContextForge per-phase tool gating** — 定義三個 phase allowlist（planning: read_file/search_files/terminal:read-only, implementing: write_file/patch/terminal:full, testing: terminal:test-only），gateway 在轉發 tool list 時過濾。不需要完整 state machine，hardcoded allowlist 就夠。

3. **[中優先] Token audit** — 用現有 logs 回推一週用量分佈，驗證 O(n²) 是否適用於 Hermes 的典型 workload。

4. **[低優先] ContextForge enforcement-first roadmap** — 把 gateway 的開發方向從「接更多 MCP server」轉向「做更強的 guardrail」。
