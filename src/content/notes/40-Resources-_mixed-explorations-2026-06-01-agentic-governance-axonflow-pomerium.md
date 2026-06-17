---
_slug: 40-Resources-_mixed-explorations-2026-06-01-agentic-governance-axonflow-pomerium
_vault_path: 40-Resources/_mixed/explorations/2026-06-01-agentic-governance-axonflow-pomerium.md
tags:
- agentic-governance
- axonflow
- pomerium
- llm-policy
source: autonomous-note
created: '2026-06-01'
title: AxonFlow + Pomerium — Agentic Governance Tools Exploration
updated: '2026-06-15'
type: exploration
status: budding
---

# AxonFlow + Pomerium — Agentic Governance Tools Exploration

**日期**: 2026-06-01 | **來源**: HN Algolia search (LLM agent policy enforcement) | **類型**: exploration

## 探索背景

從 HN Algolia 搜尋「LLM agent policy enforcement」找到兩個相關項目：AxonFlow (11 pts) 和 Pomerium Agentic Access Gateway (10 pts)。兩者都是 self-hosted 治理工具，但切入角度不同。

## AxonFlow — Runtime Execution Authority

**URL**: https://github.com/getaxonflow/axonflow | **PyPI**: axonflow (v8.3.0) | **License**: BSL 1.1 → Apache 2.0 (4 years)

### 核心定位
Self-hosted 控制平面，位於 workflow logic 和 model/tool call 的執行路徑上。**不是 observability tool**（這是 LangChain/LangSmith 的定位），而是 **inline enforcement**——在單一 digit milliseconds 內預防而非事後觀測。

### 架構
```
Agent (:8080) → Policy Engine, PII/SQLi Detection, MCP Connectors, Media Governance, Circuit Breaker
Orchestrator (:8081) → WCP (Workflow Control Plane), MAP (Multi-Agent Planning), Cost Controls, HITL Approval Gates, Evidence Export
```

- **WCP Mode**: step-level gate checks, durable step ledger, cancellation, SSE streaming. Your code controls execution, AxonFlow controls governance.
- **Gateway Mode**: pre-check → your LLM call → audit. For existing stacks.
- **Proxy Mode**: full request lifecycle: policy, planning, routing, audit.

### 60+ Built-in Policies
- Security: SQL injection (37 patterns), unsafe admin access, schema exposure
- PII: SSN, credit cards, PAN, Aadhaar, email, phone, salary, medical
- Compliance: GDPR, PCI-DSS, HIPAA basic; EU AI Act, SEBI/RBI, MAS FEAT, DORA (Enterprise)
- Runtime: tenant isolation, environment restrictions, approval gates
- Cost & Abuse: per-user/team limits, anomalous detection, token budgets

### Governance Plugins
OpenClaw, Claude Code, Cursor, Codex, Google ADK, n8n, LiteLLM. All enforce same policy surface + shared audit trail.

### HITL Approval Gates
High-risk workflow steps require explicit approval. Configurable expiry, pending limits by tier, automatic abort on expiration. (Enterprise feature)

### vs LangChain/LangSmith

| | AxonFlow | LangChain/LangSmith |
|--|--|--|
| Governance | Inline enforcement | Post-hoc monitoring |
| Architecture | Active prevention | Passive detection |
| Workflow Execution Control | Step-level gates, durable ledger | Chain sequencing only |
| Evidence & Replay | Compliance exports, decision replay | Trace logging |
| Self-Hosted | Full core available | Partial (monitoring requires cloud) |

**Best of both worlds**: Many teams use LangChain for orchestration + AxonFlow as governance layer.

### SDKs
Python, TypeScript, Go, Java, Rust (preview). All thin wrappers over REST APIs.

### 三層授權
- **Community**: 20 tenant policies, 3-day audit, 5 concurrent executions, no license key
- **Evaluation (free)**: 50 tenant policies, 14-day audit, 25 concurrent, HITL gates, policy simulation
- **Enterprise**: unlimited, 3650-day retention, SSO/SAML, SCIM, EU AI Act workflows

---

## Pomerium — Zero Trust Agentic Gateway

**URL**: https://www.pomerium.com/secure-agentic-access | **Type**: Open-source identity-aware proxy

### 核心定位
Zero trust gateway for AI agents. 核心理念：**authorize every prompt, authenticate every agent**。把每個 agent action 綁定到已驗證的使用者身份。

### 與 API Gateway 的區別
- Traditional API gateway: session-level auth at entry point
- Agentic gateway: **per-action auth**, every tool call is verified individually
- Agents powered by LLMs make decisions at runtime that static credentials can't anticipate

### 關鍵能力
1. **Tie agent actions to verified user identity** — agents only act on behalf of authorized users
2. **Verify and log every request** — full visibility into agent behavior, not just session-level
3. **Centralized AuthN/AuthZ for MCP servers** — extends Zero Trust to MCP without re-architecture
4. **Native MCP support** — tool-level authorization policies that understand agent context

### vs AxonFlow
- **AxonFlow**: what happens during LLM/agent execution (policy enforcement, PII detection, step-level gates)
- **Pomerium**: who is allowed to make what requests (identity, access control, per-action auth)
- Complementary: Pomerium gates access, AxonFlow governs what happens after access is granted

---

## 跨文章 Synthesis

### 共鳴：Self-hosted > Cloud-native
兩個工具都強調 self-hosted deployment。對於治理/审计/合規相關工具，data locality 和自主控制比便利性更重要。

### 共鳴：Action-level granularity
- AxonFlow: step-level gate checks in WCP
- Pomerium: per-action auth (not just per session)

這個趨勢呼應 Synix 探索中「structured memory > pure embedding retrieval」共識——細粒度控制比粗粒度 policy 更有價值。

### 對 Talos governance pipeline 的啟發

**AxonFlow 的借鑒**:
- WCP step ledger → 可參考作為 Talos 的 tool-call 審計 log 結構
- Policy simulation (dry-run) → 對應 WS-035 提案的 enforcement 層
- HITL approval gates → 對危險 tool 的 extra verification step
- Circuit breaker (kill switch) → 緊急狀況的最終防線

**Pomerium 的借鑒**:
- MCP-native auth → Talos 的 MCP tool governance 方向
- Per-action vs per-session auth → 更精細的 access control model
- Zero trust預設 → 適用於 Talos 作為守護者的角色

**兩者都確認的 pattern**: 治理工具必須在 execution path 內（inline），不是旁觀（post-hoc）。這是從「monitoring」轉向「enforcement」的典範轉移。

---

## 未追蹤 Leads

- https://docs.getaxonflow.com/docs/integration/computer-use/ — Anthropic Computer Use governed deployment
- https://docs.getaxonflow.com/docs/integration/claude-agent-sdk/ — MCP tool governance patterns
- https://www.pomerium.com/blog/what-is-an-agentic-gateway-definition-architecture-and-why-its-different-from-an-api-gateway — agentic gateway vs API gateway deep dive
- https://try.getaxonflow.com — SaaS trial (no Docker, for quick evaluation)

## ✅ 本次探索完成