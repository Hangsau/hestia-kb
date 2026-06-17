---
_slug: 40-Resources-_mixed-research-2026-05-25-1430-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-05-25-1430-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-25'
confidence: high
title: Agent Governance + MCP 整合：跨主題綜整
updated: '2026-06-15'
type: research
status: budding
---

# Agent Governance + MCP 整合：跨主題綜整

**消化筆記**: agent-governance-toolkit-deep-dive, mcp-server-implementation-patterns

（摘要）Docker/Microsoft 的 governance 框架與 MCP 協議規範在 Herms 中交匯：MCP 同時是工具暴露層與治理執行層，兩篇筆記合計揭示從 advisory-level regex 升級到 protocol-native enforcement 的具體路徑。

## Cross-Cutting Theme 1: MCP 是 Governance 的天然執行層，而非僅僅是整合層

**支援筆記**: agent-governance-toolkit-deep-dive, mcp-server-implementation-patterns

（分析）

兩篇筆記表面上各自獨立的結論，事實上指向同一個架構結論：

- Docker AI Governance 將 MCP Gateway 定調為「single chokepoint for auth/authorization/logging」，明確把 MCP 協議層視為 enforcement point，而非純粹的 RPC 層。
- MCP Server Implementation Patterns 強調 tools 用 JSON Schema 做 input/output validation，並記錄「User consent for tool execution」和「Activity logs」作為 security best practices——這些都是 governance 的核心構件，只是還沒被命名為 governance。

MCP protocol 的三個 building blocks（Tools/Resources/Prompts）中，Tools 層已經是「model 主動觸發帶 side-effects 的操作」。這就是 governance 的戰場。Docker 的架構已經說明：把 MCP Gateway 放在 runtime 和 agent之間，是「enforcement at the runtime layer, not advisory」的最低阻力路徑。

Hermes 的 `hermes_mcp_server.py` 目前實作的是「expose tools」，但沒有對應的 governance layer。從這兩篇筆記的交叉可以看出：下一個架構演化是讓同一個 MCP server 同時承載工具暴露與 policy enforcement——而不需要另外建一套 governance bridge。

**可行動下一步**: 在 `hermes_mcp_server.py` 中新增一個 `governed_tool()` decorator，内部呼叫 `govern()`（policy engine），對每個 tool call 做 deny/allow/logging。以 AGT 的 policy YAML 格式為準則，先從 `vault_search` tool 開始試點。

---

## Cross-Cutting Theme 2: Advisory-Level Enforcement 的失敗率缺口，剛好被 MCP 的 Protocol-Level Enforcement 填補

**支援筆記**: agent-governance-toolkit-deep-dive

（分析）

AGT 的 red-team 數據：prompt-based safety（ advisory layer）26.67% violation rate，application-layer enforcement 0.00%。這個差距說明：單靠 agent 內部的意圖識別（sanitizer、prompt injection defense）是不夠的——enforcement 必須在 agent 的意圖執行之前就完成。

現有 Hermes 的 DCG regex matching + Phase-Locked Exploration 落在 advisory 層（regex 可被繞過，sanitizer 可被 jailbreak 突破）。兩篇筆記合計指向的解法是：把 enforcement 往下推一層到 MCP transport layer。當 tool call 經由 MCP protocol 到達 server 端時，JSON Schema validation + policy check 已經在資料路徑上，agent 無法繞過（除非它放棄使用 tool）。

這個模式的美妙之處在於：它不需要重新發明 enforcement 機制——MCP protocol 本身的 request/response 流程已經是個 policy checkpoint，只需要把 policy engine 嵌入 server 端。

**可行動下一步**: 研究 `FastMCP` 的 middleware/hook 機制，在 `hermes_mcp_server.py` 的 transport 層（streamable-http）前插入一個 policy middleware。參考 AGT 的 `govern()` wrapper pattern，以 `vault_search` tool 為第一個受保護端點，寫一個 end-to-end 的 deny test 確認 enforcement 不可被繞過。

---

## Cross-Cutting Theme 3: Policy Propagation 的即時性需求（Medium Confidence）

**支援筆記**: agent-governance-toolkit-deep-dive

（分析）

Docker 的「authenticate → pull latest policy → automatic propagation」機制，對應到 Hermes 的 `heartbeat_v2.py` 有一個具體的差距：當前 Talos 的 policy 是靜態存在 workspace session 中的，沒有版本檢查也沒有主動更新。AGT 的 multi-language support（Python/TypeScript/.NET/Rust/Go）隱含一個假設：policy 在不同 runtime 環境中必須保持一致。Hermes 目前沒有處理這個問題。

**可行動下一步**: 在 `heartbeat_v2.py` 的 EVOLVE 階段加入 `policy_version` field，每次 heartbeat 時比對本地 policy version 與中央 policy store（可用 vault 中一個 `governance/policies/` 目錄）的 version，過期時 trigger reload + notify。同步更新 `SESSION.md` 的 governance 區塊。