---
_slug: 40-Resources-_mixed-explorations-2026-05-25-multi-agent-governance-blind-spot
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-multi-agent-governance-blind-spot.md
title: 2026-05-25 Multi-Agent Governance Blind Spot
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-05-25 Multi-Agent Governance Blind Spot

**來源**: [Waxell blog](https://potential-root-656031.framer.app/blog/multi-agent-governance-blind-spot) | 2026-05-25

## Per-Source Insights

### Waxell: Multi-Agent Governance Blind Spot

**核心問題**：現有 governance 工具都是單 agent 導向，多 agent 系統的協調層（delegation boundary）是治理盲點。

三個具體 gap：

1. **Context scope leakage**：orchestrator 訪問完整 customer record → 生成摘要傳給 subagent → 摘要可能含 PII，subagent 的 direct-access policy 攔不到（因為資料是間接來的）。修復：delegation boundary 要做 content evaluation，不只 direct data access。

2. **Unbounded delegation depth**：四層架構（orchestrator → coordinator → specialists → tool-calling subagents），最頂層的 cost limit 不會 cascade 到 depth 3/4。每一層用自己的 policy，通常是 nothing（因為 built as component，not independently governed entity）。aggregate cost 可能比任何 individual session budget 高一個數量級。

3. **Broken audit trail**：per-agent logs 無法串成 cross-agent execution graph。delegation events（parent spawns child 時的 context handoff）沒被 capture，audit 只能得到各 agent 的 fragment，沒有 unified chain of custody。

**LangChain 具體案例**：LangGraph orchestrator node → worker node 時，worker node 收到 message 直接當 user input 處理。LLM 沒有內建機制區分「來自 user 的 instruction」和「來自 orchestrator 的 instruction」。compromised or mistaken orchestrator 可 directing subagent 做出 subagent 的 individual policy 不會 block 的動作。

**修復方向**：
- Delegation 本身要當 policy enforcement point（不只 code-level call）
- Pipeline-level cost ceiling（govern entire pattern，不只 per-agent）
- Full delegation graph instrumentation（每個 handoff 的 context + policies evaluated 都要 capture）

---

## Hermes 啟發

Talos 目前是守護者角色，核心職責之一是保護 Hestia（監控、診斷、修復）。這篇文章的三個 gap 對應到 Talos 身為 sibling agent 的潛在弱點：

1. **Context scope**：Talos 從 Hestia 接收的 task context，若超出 Talos 自己的 authorization scope，現有架構沒有 gate 機制。Talos 的 comms 靠 INBOX + poll.sh，但 INBOX 不做 content evaluation——任何寫入 INBOX 的內容 Talos 都會當 instruction 處理。

2. **Delegation depth**：當 Hestia 派生 Talos 處理 subagent task 時，Talos 的工作範圍（tools、context）由誰界定？目前是手動 /plan，沒有動態 scope enforcement。

3. **Audit trail**：Talos-Hestia 雙向通訊目前靠 threads 目錄 + INBOX.md，沒有 unified execution graph。若 Hestia 發了 task，Talos 處理時又派生另一個 agent，整個 chain 是斷的。

**對 Talos governance pipeline 的具體方向**：
- 可在 `heartbeat/actions.py` 的 EVOLVE 之類的傳感器加入 delegation boundary check（檢查 Talos 收到的 context 是否來自已授權的 agent/scope）
- Comms poll 的 INBOX 機制目前只做 existence check，未做 content scope evaluation

---

## 跨文章 Synthesis

Multi-agent governance 從 single-agent 的「policy per agent」進化到「policy at delegation boundary」。這個敘事和之前研究的 Docker AI Governance、DCG 等方向一致——都是從 enforcement point 移到更早的 decision layer。

Waxell 的三 gap（context leakage、delegation depth、audit trail）和之前筆記的 Agent Arena 10 種攻擊向量可以對照：
- Context scope leakage ← → Indirect injection（資料繞道來的）
- Unbounded delegation depth ← → Scope creep（tool 鍊超出 original intent）
- Broken audit trail ← → 無法举证（complaince 失敗）

---

## 未追蹤 Leads

- https://www.salesforce.com/news/stories/connectivity-report-announcement-2026/ — Salesforce 2026 Connectivity Benchmark Report（組織平均 12 agents，67% 成長預測）
- https://blog.langchain.com/how-and-when-to-build-multi-agent-systems/ — LangChain 官方 multi-agent architecture 指南
- https://news.ycombinator.com/item?id=47139978 — "I built a governance layer for multi-agent AI coding – lessons after 6 months"（HN discussion）
- https://www.waxell.com — Waxell 產品（governance + observability for multi-agent）

## ✅ 本次探索完成