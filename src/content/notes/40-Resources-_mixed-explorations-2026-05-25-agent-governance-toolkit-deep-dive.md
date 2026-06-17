---
_slug: 40-Resources-_mixed-explorations-2026-05-25-agent-governance-toolkit-deep-dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-agent-governance-toolkit-deep-dive.md
title: 探索：Docker AI Governance + Agent Governance Toolkit — 2026-05-25
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：Docker AI Governance + Agent Governance Toolkit — 2026-05-25

**延續自**: (none — 獨立探索)

## Source 1: Docker AI Governance (Blog Post)

**URL**: https://www.docker.com/blog/docker-ai-governance-unlock-agent-autonomy-safely/

### Core Insights

**Why agents = new prod**:
- Agents run on developer laptop with developer credentials, reaching into private repos, production APIs, customer records, and open internet — all in one session
- "The laptop just became the most powerful node in your enterprise, and it also became the most exposed"
- "Agents don't stay on the laptop. They migrate to CI runners, to staging clusters, to production"

**Governance must solve two paths**:
1. Execute code (touch files, open network connections) — handled by Docker Sandbox (microVM-based isolation with hard boundary)
2. Call tools via MCP server — handled by Docker MCP Gateway (single chokepoint for auth/authorization/logging)

**Four control surfaces**:
- Network: allow/deny rules for domains, IPs, CIDRs
- Filesystem: mount rules for paths with read-only or read-write scope
- Credentials: session-scoped, blocks exfiltration to unapproved destinations
- MCP tools: org-wide managed policies, unapproved servers blocked by default

**Key insight — "enforcement at the runtime layer, not advisory"**:
- Enforcement happens at the proxy and mount level, not as a suggestion the agent can ignore
- Policy defined once, enforced everywhere (laptop, CI, staging, production)
- No other vendor can say that — because no other vendor IS the runtime

---

## Source 2: Microsoft Agent Governance Toolkit (GitHub)

**URL**: https://github.com/microsoft/agent-governance-toolkit

### Core Insights

**Prompt-based safety failure**: 26.67% policy violation rate in red-team testing. Application-layer enforcement (AGT): 0.00%.

**Policy YAML format**:
```yaml
apiVersion: governance.toolkit/v1
name: production-policy
default_action: allow
rules:
  - name: block-destructive
    condition: "action.type in ['drop', 'delete', 'truncate']"
    action: deny
    description: "Destructive operations require human approval"
  - name: require-approval-for-send
    condition: "action.type == 'send_email'"
    action: require_approval
    approvers: ["security-team"]
```

**Policy engine evaluation**:
```python
from agentmesh.governance import govern
safe_tool = govern(my_tool, policy="policy.yaml")
# every call checked, logged, enforced
# denied → raises GovernanceDenied
```

**Multi-language support**: Python, TypeScript, .NET, Rust, Go — all implement core governance (policy, identity, trust, audit).

**Framework adapters**: LangChain, LangGraph, AutoGen, CrewAI, OpenAI Agents SDK, Google ADK, Mastra, etc.

**OWASP Agentic Top 10**: 10/10 covered.

**Privilege rings** (Agent Runtime): Four privilege rings for execution sandboxing.

**CLI tools**:
- `agt doctor` — check installation
- `agt verify` — OWASP compliance check
- `agt red-team scan` — prompt injection audit
- `agt lint-policy` — validate policy files

**MCP Security Gateway**:
- Tool poisoning detection
- Drift monitoring
- Typosquatting detection
- Hidden instruction scanning

---

## Hermes 啟發

### 1. Advisory vs Enforcement — Talos Governance Pipeline核心差距

Hermes 目前的 DCG 整合是 advisory-level（regex pattern matching），沒有 enforcement guarantee。Docker/AGT 的架構清楚說明：真正的 governance 必須在 runtime 層（process level），不是 suggestion the agent can route around.

**建議**：Talos governance pipeline 的下一階段應該是：
- 採用 AGT 的 policy YAML 格式（已驗證可行）
- 用 Agent Runtime 的 privilege ring 概念作為 enforcement 基礎
- 從 "audit after" 升級到 "deny before"

### 2. MCP Tool Governance — WS-028 直接相關

Docker AI Governance 的 MCP tool governance（"unapproved servers blocked by default"）是 WS-028 Agent Lifecycle Governance 的具體參考。現有 `enabled_toolsets` 欄位可以擴展為：
- 明確的 MCP server 允許清單
- per-agent policy group 分配
- session-scoped credential scoping

### 3. prompt injection 防禦量化

AGT 報告 prompt-based safety 26.67% violation rate vs 0.00% application-layer enforcement。這與 Hermes 的 Phase-Locked Exploration + sanitizer 雙層防禦架構一致，但需要量化驗證。建議在 `exploration-tool-scoping-gradient` SPIKE 完成後，做一次紅隊測試確認防禦率。

### 4. Policy propagation 機制

Docker 的 "authenticate → pull latest policy → automatic propagation" 是 Talos heartbeat 可以借鑒的。Hermes 的 `heartbeat_v2.py` 可以在 EVOLVE 時檢查 policy 版本，確保多 agent 環境中 policy 一致性。

---

## 跨文章 Synthesis

Docker AI Governance 描述 runtime enforcement 的硬邊界（microVM sandbox + MCP Gateway），Microsoft AGT 提供 policy YAML 格式和 application-layer enforcement 框架。兩者合在一起是完整的 governance 解決方案：runtime isolation + policy enforcement + audit trail。

Talos 目前落在兩者之間：
- 有 DCG regex enforcement（advisory level）
- 有 Phase-Locked Exploration（sanitizer defense，但無 enforcement）
- 缺少的是 runtime isolation（Docker 的 microVM）和 centralized policy（AGT 的 YAML）

**最短實作路徑**：
1. 採用 AGT 的 YAML policy format 替換 DCG 的 pattern-matching
2. 在 `heartbeat_v2.py` 加入 policy_version check
3. 以後再擴展到 Docker-style runtime isolation（如果需要的話）

---

## 未追蹤 leads

- https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/specs/MCP-SECURITY-GATEWAY-1.0.md — MCP Security Gateway spec
- https://microsoft.github.io/agent-governance-toolkit/ — full documentation
- https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/OWASP-COMPLIANCE.md — OWASP 10/10 coverage details
- https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/PACKAGE-FEATURE-MATRIX.md — per-language feature matrix

## ✅ 本次探索完成