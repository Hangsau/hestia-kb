---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Arch-Router--偏好驅動的-LLM-路由
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Arch-Router--偏好驅動的-LLM-路由.md
title: 'Arch-Router: 偏好驅動的 LLM 路由'
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arch
- gateway
- hermes
- llm
- model
- plano
- proxy
- router
- routing
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Arch-Router: 偏好驅動的 LLM 路由

**日期**: 2026-05-15 | **來源**: HN Show HN (66 pts, 15 comments) | **類型**: 探索筆記

## 一句話

Arch-Router 是一個 1.5B 的輕量模型，用**自然語言偏好規則**（不是 intent classifier、不是 benchmark score）來決定 prompt 該送給哪個 LLM。

---

## Per-Source Insights

### Arch-Router (katanemo/Arch-Router-1.5B)

- **論文**: [arxiv.org/abs/2506.16655](https://arxiv.org/abs/2506.16655)
- **HuggingFace**: [katanemo/Arch-Router-1.5B](https://huggingface.co/katanemo/Arch-Router-1.5B)
- **Proxy**: [github.com/katanemo/plano](https://github.com/katanemo/plano)（原 archgw，已改名 Plano）

**核心思路**：三種 LLM routing paradigm 的第三條路：

| Paradigm | 做法 | 致命弱點 |
|---|---|---|
| Embedding-based | 意圖分類器（「這是 SQL query → 送 SQL 模型」） | 多輪對話中 topic shift 會讓 classifier 崩潰；加新意圖需 retrain |
| Performance-based | 看 benchmark（MMLU, MT-Bench）或 cost/latency curve | benchmark 不等於 production 偏好；「法務會不會接受這個條款？」benchmark 不回答這種問題 |
| **Preference-based (Arch-Router)** | 用自然語言寫偏好規則（「合約條款 → GPT-4o」「快速旅遊建議 → Gemini Flash」），1.5B 模型 map prompt → 規則 | 目前只看到優點——不需要 retrain、支援多輪、換模型只改一行 config |

**關鍵數字**：
- 1.5B params，單 GPU 可跑（CPU 也能測試）
- 在 conversational routing benchmark 上**勝過更大的 closed model**
- 輸入來自 Twilio & Atlassian 團隊的實際需求

**怎麼做到的**：不是用 embedding similarity，而是 autoregressive——把 prompt + conversation context 餵給 1.5B 模型，模型直接輸出應該匹配的 preference rule。這讓它能處理多輪對話中的 intent drift。

### Plano（原 archgw）：整合 Arch-Router 的 proxy

- **建在 Envoy 上**，由 Envoy 核心貢獻者開發
- Rust 寫的，三個支柱：**Orchestration**（agent 路由 + 4B orchestrator 模型）、**Model Agility**（LLM routing，含 Arch-Router）、**Observability**（Agentic Signals™ + OTEL）
- 有 **Filter Chains** 概念：guardrails → moderation → memory hooks，作為 pipeline 串接
- YAML 宣告式 config：agent URL + 自然語言描述，proxy 自動路由

**值得注意的設計選擇**：
1. 用**專用輕量模型做 infra 決策**（1.5B routing / 4B orchestration），而非呼叫 GPT-4 處理 routing——成本低、延遲低
2. Filter chains 是 pipeline 模式，不是 flat list——和 Hermes skills 的 sequential tool calling 有結構上的呼應
3. "Agentic Signals" 是他們給 tracing 取的行銷名詞，但概念值得偷：zero-code capture of agent-specific traces

---

## Hermes 啟發

### 1. Model routing 的三種 paradigm 值得內化

Hermes 目前沒有 smart routing——使用者手動選 provider/model，或 cron 用固定配置。但如果未來要支援多 model 動態切換，preference-based 是比 embedding-based 務實得多的起點：

- **Config-driven**：偏好規則是純文字 config，不需要 ML pipeline
- **無 retraining**：加新 model 只加一行 config
- **可解釋**：「為什麼送到 GPT-4o？」→ 因為 preference rule「法律文件 → GPT-4o」match 了。比 embedding 的「cosine similarity 0.87」好懂十倍

Hermes 已經有 `config.yaml` 的多 provider 配置——如果未來加一個 `routing.preferences` 區塊（例如 `"system operations → deepseek-v4-pro"`），就是 preference-based routing 的雛形。

### 2. Filter chains 和 Hermes 的 tool chain 是同一種 pattern

Plano 的 filter chains（guardrails → moderation → memory hooks）和 Hermes 的 sequential tool calling 都是 pipeline 模式。差別在於：
- Plano 的 chain 是 proxy 層的（request 經過 proxy 時自動觸發）
- Hermes 的 chain 是 agent 層的（LLM 決定何時呼叫工具）

一個可能的整合點：把某些 Hermes skill（如 secret-leak-prevention）包成 filter，掛在 gateway 層，讓它對所有 agent session 生效，而不是等 LLM 決定要不要檢查。

### 3. 「輕量專用模型處理 infra 決策」是趨勢

Arch-Router (1.5B) + Plano Orchestrator (4B) 的組合說明了一件事：**你不需要 GPT-4 來決定 routing**。這個原則可能適用於 Hermes 的其他 infra 層決策：
- 哪些 error 需要 escalate？（heartbeat severity classification）
- 哪個 session 該被 interrupt？（目前基於簡單 timeout）
- 哪個 skill 適合這個 task？（目前 LLM 自己判斷）

目前這些都是 LLM 驅動的（要花 token），但如果有輕量模型處理這些判斷，可以省成本。不過話說回來——Hermes 的 deepseek-v4-pro 已經夠便宜了，overhead 可能不足以 justify 多跑一個模型。

### 4. agent description → 自動 routing 的思路

Plano 的做法：agent 用自然語言寫 description（"Handles: weather queries, flight searches"），proxy 的 orchestrator 模型自動判斷哪個 agent 處理哪個 request。這和 Hermes 的 **skill descriptions 有類似的語意角色**——skills 的 description 欄位也是自然語言，幫助 LLM 選擇何時載入。差別在於 Hermes 是 LLM 自己讀 description 然後決定，Plano 是用專用模型做這個決定。

一個延伸想法：如果 Hermes 的 skill selection 太重（128 個 skills，LLM 每次都要 scan），可以考慮把 description → 適合 task 的 mapping 預先 cache（embedding index），省去 LLM 的 skill listing overhead。但這是 premature optimization——目前 skill listing 不是瓶頸。

---

## 跨文章 Synthesis

這篇沒有和其他筆記交叉——Arch-Router 是今天第一篇真正全新的 topic。但和前幾天的內容有鬆散關聯：

- **[[2026-05-14-hermes-gateway-anatomy]]** 分析了 Hermes gateway 的現狀（messaging hub，非 smart proxy）。Plano/Arch-Router 正好展示了「如果 gateway 要變聰明，它可以長什麼樣子」——而答案可能不是 gateway 本身變聰明，而是在 gateway 前面加一個專用 routing model。
- **[[2026-05-15-mcpc-mcp-cli-proxy]]** 討論了 MCP proxy/gateway 的競爭格局。Plano 是另一個維度的 proxy——不處理 MCP，處理 agent orchestration + LLM routing + observability。這三層（MCP gateway、agent orchestration、LLM routing）目前是分開的生態，但長期可能收斂。

---

## 未追蹤但值得注意

- **Arxiv 論文全文**（arxiv.org/abs/2506.16655）：只讀了 abstract。論文裡應該有 benchmark 細節、對比 RouteLLM 的數據、failure case 分析。值得深入。
- **Plano 的 Filter Chains 文件**（docs.planoai.dev/concepts/filter_chain.html）：pipeline 設計細節，可能對 Hermes 的工具鏈有參考價值。
- **RouteLLM 對比**：HN 評論有人問「和 RouteLLM 比如何？」，論文裡應該有答案，但沒讀到。
- **Plano Orchestrator (4B)**：除了 Arch-Router 之外，Plano 還有一個 4B 的 orchestrator 模型。兩個模型的關係（是 stacked 還是替代）值得弄清楚。

