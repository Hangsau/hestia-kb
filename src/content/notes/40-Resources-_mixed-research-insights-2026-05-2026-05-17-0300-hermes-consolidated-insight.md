---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0300-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0300-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: high
title: 治理三相缺口：Policy Definition / Enforcement / Audit 的斷層
updated: '2026-06-15'
type: research
status: budding
---

# 治理三相缺口：Policy Definition / Enforcement / Audit 的斷層

**消化筆記**: 2026-05-17-docker-agent-yaml-schema-policy-enforcement, 2026-05-17-docker-governance-aiuc1-changelog

（兩篇筆記各自描述了 Docker/AIUC-1 的治理元素，但分散在不同抽象層次。合成後發現：policy lifecycle 的三個 phases——definition、enforcement、audit——在 Hermes/Talos 框架中彼此斷裂。）

## Cross-Cutting Theme 1: Policy Lifecycle 三相斷裂

**支援筆記**: docker-agent-yaml-schema-policy-enforcement, docker-governance-aiuc1-changelog

Note 1 詳細描述 Docker 的 YAML schema 如何承載 policy definition（`permissions.allow/deny`、`filesystem.allow_list/deny_list`、`fetch.allowed_domains`），以及 Talos 可以用 `guardian_policy.yaml` 定義規則。Note 2 強調 Docker AI Governance 的核心設計原則：policy 必須在 runtime layer 強制執行（enforcement），並產生結構化稽核事件（audit）。

但這三個 phases 在 Hermes/Talos 框架中分佈極不均勻：

| Phase | 目前狀態 | 來源 |
|-------|---------|------|
| **Definition** | `guardian_policy.yaml` 草案存在 | note 1 |
| **Enforcement** | ❌ 完全缺失（只有 ad-hoc 檢查） | note 2 |
| **Audit** | ✅ heartbeat EVOLVE 雛形 | note 2 |

這意味著 Talos 目前是「有護欄設計圖、有事後記錄，但沒有護欄本體」。定義和稽核之間的 enforcement 層是斷層。

**可行動下一步**：在 `talos` skill 中實作 `enforce_policy()` hook，讓每次 tool call 發生前先走 `guardian_policy.yaml` 的 allow/deny check。目前 `ws-009` 的 L2 gateway mediation 只在 spike 階段，需要從 schema 規格化轉為實際的 policy evaluation engine。

---

## Cross-Cutting Theme 2: MCP 是第四個控制面，但 L2 未完整定義

**支援筆記**: docker-governance-aiuc1-changelog, docker-agent-yaml-schema-policy-enforcement

Note 2 引用 Docker AI Governance 的 Four Control Surfaces：Network & Filesystem、Credentials、MCP Tools、Role-based Policy。MCP Tools 是四分之一個獨立的信任邊界。

但 note 1 的 WS-009 三層框架（Tool Scoping / Gateway Mediation / microVM Sandboxing）只涵蓋了前三個控制面的前三個維度，L2 Gateway Mediation 究竟要怎麼治理 MCP tool calls，語焉不詳。`dev-team.yaml` 的 `sub_agents` 和 `handoffs` 討論的是 agent 間的 delegation，但 MCP server（如 `web_extract`、`process`）作為外部系統閘道的角色，完全沒有被處理。

**可行動下一步**：在 `mcp-gateway` skill 中建立 MCP server 白名單机制（`mcp_servers.allow_list` + `mcp_servers.blocked_list`），对标 Docker 的「unapproved servers blocked by default」原則，並作為 L2 enforcement 的具體著力點。

---

## Cross-Cutting Theme 3: Loop Prevention 是被遺漏的治理維度

**支援筆記**: docker-agent-yaml-schema-policy-enforcement, docker-governance-aiuc1-changelog（均未提及）

兩篇筆記覆蓋了 credential management、filesystem isolation、network filtering、tool call restriction，卻沒有一處提到「當 agent 進入重複循環呼叫時如何干預」。Docker `permissions.yaml` 提到 `max_consecutive_tool_calls` 和 `max_iterations`，但這是 schema 層面的欄位，沒有在任何具體實現中被驗證。

WS-009 三層框架中，L1 tool scoping 限制「哪些 tool 可以被呼叫」，但沒有任何層次限制「同一 tool 在短時間內被呼叫超過 N 次」。Loop prevention 是 AIUC-1 Q2 changelog 裡「multi-step workflow 是新的風險面」的延伸——chained tool calls 比單一 call 更難審計，也更容易形成隱性迴圈。

**可行動下一步**：在 `guardian_policy.yaml` 加入 `loop_prevention.max_consecutive_tool_calls: 10` 和 `loop_prevention.max_iterations: 50`，由 Talos 在每次 tool call 後遞增計數器，達閾值時觸發 Hestia 中斷確認（相當於「ask」模式的強制版本）。

---

## Cross-Cutting Theme 4: Sub-agent 協作缺乏正式的控制面

**支援筆記**: docker-agent-yaml-schema-policy-enforcement, docker-governance-aiuc1-changelog（secondary）

Note 1 記錄了 Docker 的兩種 multi-agent 協作模式：`sub_agents`（父子任務分配，樹狀）vs `handoffs`（對等對話轉交，圖狀）。Note 2 的 AIUC-1 Q2 changelog 在 E015 擴展了 logging 範圍到「sub-agent actions」和「provenance metadata」，暗示 sub-agent 行為已經是獨立的稽核對象。

但 Hermes 的現況是：Hestia（root）→ Talos（guardian）的關係是 implicit 的，沒有像 `sub_agents` 那樣的 formal declaration，也沒有像 `handoffs` 那樣的 routing graph 定義。Sub-agent 之間的信任邊界在哪裡、什麼情況下可以轉交對話、root 如何保留最終控制權——這些問題目前靠的是 convention 而非 policy。

**可行動下一步**：在 `multi-agent-collaboration` skill 中建立 `agent_relationships.yaml`，明確定義 Hestia/Talos/探索 sub-agent 的信任邊界、allowed handoffs，以及 escalation path。

---

## 總結：三個實質缺口優先順序

1. **最緊急**：`guardian_policy.yaml` 的 enforcement hook——Policy Lifecycle 斷裂最嚴重，沒 enforcement 等於沒 policy
2. **中等**：MCP server allowlist——L2 空白太久，會阻礙 futureproofing
3. **低優先**：Loop prevention 和 sub-agent formalization——空白但影響範圍可控
