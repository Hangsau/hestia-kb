---
_slug: 40-Resources-_mixed-research-2026-06-02-HHMM-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-02-HHMM-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-02'
confidence: medium
title: Agentic Governance 的兩個 cross-cutting 原則
updated: '2026-06-15'
type: research
status: budding
---

# Agentic Governance 的兩個 cross-cutting 原則

**消化筆記**: 2026-06-01-agentic-governance-axonflow-pomerium, 2026-06-01-Graphiti-Bi-Temporal-Edge-Source-Analysis

（兩篇自主探索筆記，分別研究 Agentic Access Gateway 工具鏈與 bi-temporal memory 實作。交叉閱讀後發現兩者共同指向同一套治理哲學，且與 Hermes 當前設計缺口高度相關。）

## Cross-Cutting Theme 1: Action-Level Granularity 是治理的正確粒度

**支援筆記**: 2026-06-01-agentic-governance-axonflow-pomerium, 2026-06-01-Graphiti-Bi-Temporal-Edge-Source-Analysis

兩篇筆記各自獨立研究不同領域，卻收斂到同一個結論：無論是安全治理（AxonFlow 的 step-level gate, Pomerium 的 per-action auth）還是知識管理（Graphiti 的 edge-level fact embedding, episode provenance），**比粗粒度更有價值的都是細粒度**。

- AxonFlow 的 WCP step ledger 在每個 tool call 級別做 blocking pattern check，不是 chain 級別
- Pomerium 強調 per-action 而非 per-session 的 auth model
- Graphiti 每個 EntityEdge 有獨立的 `fact_embedding`，支援 edge-level semantic search

這個 pattern 在 Synix 探索裡也有共鳴（「structured memory > pure embedding retrieval」）。細粒度控制比粗粒度 policy 更容易實作精確的審計、 rollback 和解釋。

**可行動下一步**: 在 Talos governance design 文件中，明確採用 `hermes.{tool_name}.{action}` 作為 permission check 的命名空間，不要用 `hermes.tool.{tool_name}` 這種粗粒度格式。

---

## Cross-Cutting Theme 2: Inline Enforcement 而非 Post-Hoc Monitoring

**支援筆記**: 2026-06-01-agentic-governance-axonflow-pomerium（主要）, 2026-06-01-Graphiti-Bi-Temporal-Edge-Source-Analysis（次要）

AxonFlow vs LangChain/LangSmith 的對比表中，核心差異欄是「inline enforcement」vs「post-hoc monitoring」。Pomerium 的 zero-trust 預設也是同樣邏輯——每個 action 當下授權，不事後補救。

Graphiti 的 bi-temporal model 在這點是微妙的對應：它的 `invalid_at` 欄位讓系統在精確時間點知道何時某個 fact 變得 stale，而不是靠事後輪詢或 TTL 來發現問題。這是一種資料層面的 inline enforcement。

對照 Hermes 的 heartbeat 系統，發現自己也在往 inline 方向移動——`heartbeat_decisions.jsonl` 已經在做事前預防（cancellation, circuit breaker），不只是事後 log。

**可行動下一步**: 將 `WS-035 enforcement` 的規格從「日誌 + 報警」改為「同步 blocking check + 非同步 audit log」，用 AxonFlow ComputerUseGovernor 的 10-pattern blocklist 作為初始規則集，先在 observe mode 累積 trail，再逐步切換到 enforce mode。