---
_slug: 40-Resources-_mixed-explorations-2026-06-02-Exploration---2026-06-02--Agentic-Gateway-Implementation-Lan
_vault_path: 40-Resources/_mixed/explorations/2026-06-02-Exploration---2026-06-02--Agentic-Gateway-Implementation-Lan.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 32:\n    title: Exploration — 2026-06-02: Agentic Gateway Implementation\
  \ ... \n                                   ^"
_raw_fm: '

  title: Exploration — 2026-06-02: Agentic Gateway Implementation Landscape

  date: 2026-06-02

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, agentgateway, axonflow, gateway, governance, guardrails, mcp,
  policy, sdk, tool]

  created: 2026-06-02

  updated: 2026-06-15

  status: active

  '
title: 'Exploration — 2026-06-02: Agentic Gateway Implementation Landscape'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Exploration — 2026-06-02: Agentic Gateway Implementation Landscape

**日期**: 2026-06-02 | **來源**: 延續 2026-06-01 AxonFlow/Pomerium 探索（vault）| **類型**: SPIKE

## Per-Source Insights

### Source 1: Agentgateway (github.com/agentgateway/agentgateway)

**URL**: GitHub raw README — `raw.githubusercontent.com/agentgateway/agentgateway/main/README.md`

**核心架構**：
- **LLM Gateway**: OpenAI-compatible API，budget/spend controls、prompt enrichment、load balancing、failover
- **MCP Gateway**: MCP tool federation、stdio/HTTP/SSE/Streamable HTTP transports、OpenAPI integration、OAuth authentication
- **A2A Gateway**: Agent-to-agent communication via A2A protocol、capability discovery、modality negotiation、task collaboration
- **Inference Routing**: Self-hosted model routing via Kubernetes Inference Gateway extensions（GPU utilization、KV cache、LoRA adapters、queue depth）
- **Guardrails**: Multi-layered content filtering — regex、OpenAI moderation、AWS Bedrock Guardrails、Google Model Armor、custom webhooks
- **Security & Observability**: JWT/API keys/OAuth auth、CEL policy engine、RBAC、rate limiting、TLS、OpenTelemetry

**重要發現**：
- Linux Foundation 項目（不是純商業產品）
- Apache 2.0 許可
- 明確定位為「first complete connectivity solution for Agentic AI」
- A2A Gateway — 明確標記為「in active development」（不是 GA）
- 開源：可研究實作細節

**對 Talos 的啟示**：
1. MCP Gateway 底層能力（stdio/HTTP transports + OAuth）= 直接可用的 tool federation 參考
2. A2A 仍在 active development → 不適合現在依賴，但值得關注
3. Guardrails 的 multi-layer 設計（regex + OpenAI moderation + Bedrock Guardrails + Model Armor）= 疊加式 defense 範本

---

### Source 2: AxonFlow Claude Agent SDK — MCP Tool Governance

**URL**: `https://docs.getaxonflow.com/docs/integration/claude-agent-sdk/`

**核心整合模式**：
```
Agent Loop → Tool Selected → mcpCheckInput() → Tool Execution
    ↓
Agent Response ← mcpCheckOutput() ← Tool Result
```

**mcpCheckInput() — Input Policy Enforcement**：
- SQL injection detection
- PII in queries（SSN, credit card in search parameters）
- Dangerous operations（DELETE without WHERE）
- Custom tenant policies

**mcpCheckOutput() — Output Policy Enforcement**：
- PII redaction（email, phone, SSN in results）
- Exfiltration detection（large-scale data extraction, 10,000+ rows）
- Response filtering（credit card numbers）
- Custom tenant policies

**Latency Overhead**：
- mcpCheckInput: 2-5ms
- mcpCheckOutput: 2-5ms
- Audit write: 0ms（async, non-blocking）
- Total per tool call: 4-10ms（與 50-500ms tool call 比起來可忽略）

**Connector Type Naming Convention**：
- `agent_sdk.{tool_name}` — 例：`agent_sdk.query_customers`
- 可用 `agent_sdk.*` 匹配所有 tool
- 可用 `agent_sdk.db_*` 匹配整類 tool

**Observe Mode**：`PII_ACTION=log` — logging only, no blocking/redaction。audit trail 仍寫，可用於測試階段。

**與 Claude Code 整合的差異**：
| Aspect | Claude Code | Claude Agent SDK |
|---|---|---|
| Integration point | Shell hooks (pre/post tool) | TypeScript SDK methods |
| Protocol | HTTP calls to AxonFlow agent | mcpCheckInput/mcpCheckOutput |
| Scope | Developer CLI tool governance | Custom agent tool governance |
| Runtime | Bash scripts | Node.js/TypeScript |

---

## 跨文章 Synthesis

**收斂到一個核心架構模式**：

```
Agent → Tool Call Request
    ↓ (pre-execution)
Policy Check (input validation)
    ↓ (allowed)
Tool Execution
    ↓ (post-execution)
Policy Check (output sanitization + audit)
    ↓
Agent receives result
```

這個 pre/post 雙向鉤子模式（AxonFlow）+ 疊加式 content filtering（Agentgateway guardrails）= 生產級 agent governance 的最小可行架構。

**對 Talos governance pipeline 的具體更新**：

1. **DCG（Destructive Command Guard）整合路徑確認**：DCG 的 regex-based blocking 可作為 Agentgateway-style 的第一層 guardrail（inline, no network call）。第二層由 AxonFlow mcpCheckInput() 處理需狀態的 policy（PII detection、exfiltration）。

2. **MCP tool governance 的 concrete design**：AxonFlow 的 `connectorType` 命名 convention 直接適用於 Talos 的 MCP tool 白名單。`agent_sdk.{tool_name}` → `talos_mcp.{resource}`。

3. **A2A Protocol — 別急著用**：Agentgateway 明確說 A2A Gateway 仍在 active development，意味著 spec 還在變。現在投入實作會浪費精力。建議：等 A2A spec 穩定再整合。

4. **Observability 是標配不是選配**：Agentgateway 和 AxonFlow 都內建 OpenTelemetry。Talos governance pipeline 必須有對應的 audit trail，否則無法應對 SOC2 之類的合規要求。

---

## 對 Hermes 的具體影響

### 對 `dcg-hermes-talos-governance-integration` 提案（WS-032）的更新

**更新狀態**：READY — 技術方向已確認，現有 DCG foundation 可擴展

具體發現：
- DCG 的 context-aware matching 可作為第一層 inline blocking（local regex, no network）
- AxonFlow 的 mcpCheckInput/mcpCheckOutput 模式是第二層 policy enforcement 的參考藍圖
- `connectorType` naming convention → 直接借鑽

### 對 `exploration-tool-scoping-gradient` 提案（WS-044）的更新

**更新狀態**：PARTIAL — WS-044 方向驗證了

具體發現：
- Agentgateway 的 Guardrails 層（regex + OpenAI moderation + AWS Bedrock Guardrails + Google Model Armor）是多層疊加式 filtering 的實作範本
- AxonFlow 的 pre/post dual-hook 是「在 execution path 內的 inline blocking」的具體模式
- 兩者整合 = shortest path to production-grade tool governance

---

## 未追蹤 Leads

- https://agentgateway.dev/docs/quickstart — Agentgateway standalone quickstart（還沒 fetch）
- https://agentgateway.dev/docs/ — Agentgateway standalone docs（還沒 fetch）
- https://agentgateway.dev/docs/kubernetes/latest — Kubernetes deployment（還沒 fetch）

## ✅ 本次探索完成
