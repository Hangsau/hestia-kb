---
_slug: 40-Resources-_mixed-explorations-2026-05-26-探索-MCP-Security-Gateway-1-0-Spec---2026-05-26
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-探索-MCP-Security-Gateway-1-0-Spec---2026-05-26.md
title: 探索：MCP Security Gateway 1.0 Spec — 2026-05-26
date: 2026-05-26
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- asi
- gateway
- governance
- mcp
- response
- schema
- security
- tool
- toolkit
created: '2026-05-26'
updated: '2026-06-15'
status: budding
---

# 探索：MCP Security Gateway 1.0 Spec — 2026-05-26

**延續自**:
- [[2026-05-25-agent-governance-toolkit-deep-dive]]（MCP-SECURITY-GATEWAY-1.0.md lead）

---

## Source 1: MCP Security Gateway 1.0 Spec（GitHub raw）

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/specs/MCP-SECURITY-GATEWAY-1.0.md
**Status**: Draft · 2025-07-28 · Microsoft Agent Governance Toolkit team
**Length**: 1908 lines

### TL;DR

MCP Security Gateway 是 MCP 協定的 defense-in-depth interception layer，架在 agent runtime 和 MCP tool servers 之間。所有 tool call 和 response 都經過雙階段 pipeline：

```
Agent ──► [Tool Call Interception] ──► MCP Server
              │                              │
              ├─ Deny/Allow lists            │
              ├─ Approval workflow           │
              ├─ Rate limiting              │
              └─ Audit entry                │
                                           │
Agent ◄── [Response Scanning] ◄────────────┘
              ├─ Prompt injection scan
              ├─ Credential leak scan
              ├─ PII scan
              ├─ Exfiltration URL scan
              └─ Policy enforcement (BLOCK/SANITIZE/LOG)
```

### 核心元件

**Tool Call Interception（4.1-4.7）**：
- `intercept_tool_call(agent_id, tool_name, params)` → `(allowed: bool, reason: string)`
- 評估順序：Deny list → Allow list → Sensitive-tool（需 approval callback）→ Rate limit
- `ApprovalStatus` enum：`PENDING | APPROVED | DENIED`
- Per-agent call budget（sliding window）
- 每次 interception 必產 AuditEntry

**Response Scanning（5.1-5.9）**：
- `intercept_tool_response(agent_id, tool_name, response_content)` → `MCPResponseDecision`
- `ResponsePolicy` enum：`BLOCK | SANITIZE | LOG`
- Threat categories（`MCPResponseScanner`）：
  1. Instruction tag injection（`<SYSTEM>`, `[INST]`, `<|im_start|>`, `<<SYS>>`等）
  2. Imperative injection（自然語言命令，如「ignore previous」）
  3. Credential leaks（API keys, tokens, passwords）
  4. PII leaks（SSN, email, credit card）
  5. Exfiltration URLs（query param 嵌入敏感資料）
- `sanitize_response()` 回傳 `(sanitized_content, threats)`

**Security Scanner（6.1-6.7）**—靜態分析 tool definitions：
- `MCPThreatType` enum：
  - `TOOL_POISONING` — tool definition 含惡意指令
  - `RUG_PULL` — description/schema 自上次 registration 後被改（supply-chain attack）
  - `CROSS_SERVER_ATTACK` — tool 試圖引用/呼叫其他 MCP servers
  - `CONFUSED_DEPUTY` — tool 試圖提權或冒充其他 agent
  - `HIDDEN_INSTRUCTION` — tool description 含隱藏 Unicode/encoded payload
  - `DESCRIPTION_INJECTION` — prompt injection 嵌入 tool description/schema
- `ToolFingerprint`：SHA-256(`description_hash` + `schema_hash`) + version counter
- `check_rug_pull()`：比對 current vs registered fingerprint，detect supply-chain attack

**其他元件**：
- Message Signing（7）：HMAC-SHA256 + nonce replay protection
- Session Authentication（8）：cryptographic session tokens，TTL + concurrency limits
- Rate Limiting（9）：sliding-window algorithm，per-agent call budgets
- CVE Feed（11）：OSV API integration，追蹤 MCP server dependencies 的已知漏洞
- Trust-Gated MCP（14）：identity-verified tool access + minimum trust scores
- Schema Drift Detection（16）：baseline comparison for tool schema changes + severity classification
- Audit Trail（12）：every decision（allow/deny/sanitize）必產 immutable record
- Metrics（13）：`record_decision()`, `record_rate_limit_hit()`

**Fail-Closed by Default**：任何 component 錯誤時 deny，不 silently permit。

---

## Source 2: OWASP Agentic Top 10 Compliance（GitHub raw）

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/OWASP-COMPLIANCE.md

### Coverage Matrix

| # | OWASP Risk | Coverage | Component |
|---|-----------|----------|-----------|
| ASI-01 | Agent Goal Hijack | ✅ | Agent OS — Policy Engine |
| ASI-02 | Tool Misuse & Exploitation | ✅ | Agent OS — Capability Sandboxing |
| ASI-03 | Identity & Privilege Abuse | ✅ | AgentMesh — DID Identity & Trust Scoring |
| ASI-04 | Agentic Supply Chain Vulnerabilities | ✅ | AgentMesh — AI-BOM |
| ASI-05 | Unexpected Code Execution | ✅ | Agent Runtime — Execution Rings |
| ASI-06 | Memory & Context Poisoning | ✅ | Agent OS — VFS Policies + CMVK Verification |
| ASI-07 | Insecure Inter-Agent Communication | ✅ | AgentMesh — IATP + Encrypted Channels |
| ASI-08 | Cascading Agent Failures | ✅ | Agent SRE — Circuit Breakers + SLOs |
| ASI-09 | Human-Agent Trust Exploitation | ✅ | Agent OS — Approval Workflows |
| ASI-10 | Rogue Agents | ✅ | Agent Runtime — Kill Switch + Ring Isolation |

**所有 10 項都有 mapping**。

---

## Hermes 啟發

### 1. MCP Response Scanner 可以補足現有 sanitize_fetch.py

Hermes 的 `sanitize_fetch.py` 只處理 fetch 階段的 HTML 淨化。MCP Security Gateway 的 `MCPResponseScanner` 是互補的——它在 tool response 層次做掃描，針對：
- Imperative injection（自然語言指令）
- Credential/PII leaks
- Exfiltration URLs

**差距**：Hermes 目前沒有在 tool response 返回 agent 之前做掃描的機制。若要實作對稱的防禦，需要在 gateway 或 tool wrapper 層加入 response scanning。

### 2. Security Scanner 的 RUG_PULL detection 正是 Talos governance 需要的

`ToolFingerprint` + `check_rug_pull()` 解決了 MCP tool 被 supply-chain attack 替換的問題。Talos 的 `dcg-hermes-talos-governance-integration.md` 提案有類似概念但未深入實作。這個 spec 給了一個 concrete 的 fingerprinting 演算法（SHA-256 of description + schema, version counter）。

### 3. Schema Drift Detection 是新發現

`Schema Drift Detection`（Section 16）是對 tool schema 做 baseline comparison，detect additions/removals/modifications。這和提案 `exploration-tool-scoping-gradient`（要 detect tool 白名單偏離）方向接近但更具體。

### 4. OWASP ASI-06（Memory Poisoning）對應現有 drift sensor

ASI-06 Coverage 提到 "CMVK Verification"（Context Model Verification Key？）用於 detect memory poisoning。這和 heartbeat 的 `check_workspace_sync()` drift sensor 概念相通但更嚴格（cryptographic verification）。

### 5. Fail-closed by default 是正確的安全哲學

所有 component 在 error 時 deny，適用於 Talos governance pipeline 的所有 enforcement 點。

---

## 未追蹤 leads

- https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/specs/AGENT-OS-POLICY-ENGINE-1.0.md — Policy Engine spec（對應 ASI-01/ASI-02）
- https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/specs/AGENTMESH-IDENTITY-AND-TRUST-1.0.md — DID Identity spec（對應 ASI-03）
- https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/specs/AGENT-SRE-1.0.md — Agent SRE（對應 ASI-08）

## ✅ 本次探索完成

