---
_slug: 40-Resources-_mixed-explorations-2026-05-27-AGT-Architecture---Competitive-Gap-Analysis
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-AGT-Architecture---Competitive-Gap-Analysis.md
title: AGT Architecture + Competitive Gap Analysis
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- action
- agent
- agt
- asi
- hermes
- identity
- llm
- ring
- tool
- trust
created: '2026-05-27'
updated: '2026-06-15'
status: budding
---

# AGT Architecture + Competitive Gap Analysis

**日期**: 2026-05-27
**延續自**: [[2026-05-26-agt-identity-sre-hypervisor-specs]], [[2026-05-25-mcp-gateway-tool-governance-blueprint]]

## 核心洞察：兩層模型

```
LLM Output Layer (NeMo, Guardrails AI, Portkey, LiteLLM)
  └─ "Did the model say something safe / structured / on-topic?"

Agent Action Layer (Agent Governance Toolkit)
  └─ "Should this agent be allowed to execute this action right now?"
```

**Hermes 已在 Agent Action Layer**：heartbeat 的 tool call interception、execution ring enforcement proposal（WS-035）、MCP Security Gateway blueprint（WS-034）都是在這層。這是正確的架構位置。

**這解釋了為什麼 Hermes 需要 AGT 而非其他工具**：NeMo/Guardrails 解決 LLM output 問題，Hermes 沒有這個問題——它的問題是「怎麼確保 agent 做它該做的事」。

## Execution Rings — 實作確認

AGT Architecture.md 確認了 4-tier ring 模型：

| Ring | Name | FS | Network | Subprocess | Max Tools |
|------|------|----|---------|------------|-----------|
| 0 | Root | full | Yes | Yes | 32 |
| 1 | Privileged | full | Yes | Yes | 16 |
| 2 | Standard | scoped | allowlist | Yes | 8 |
| 3 | Sandbox | none | **No** | **No** | 2 |

Hermes 對應：
- Ring 3（Sandbox）= 探索 agent → `{web_search, web_extract, read_file, search_files}`，4-tool 限制
- Ring 2（Standard）= 一般 cron job → `enabled_toolsets` 層級
- Ring 1（Privileged）= auto-git-push 之類 → full tool set + dangerous tools
- Ring 0（Root）= system-level → 目前無對應

## OWASP Agentic Top 10 Coverage — 缺口分析

| Risk | Hermes 現況 | AGT 提供的 |
|------|------------|-----------|
| ASI-01 Goal Hijack | 部分（policy engine proposal） | Policy engine blocks unauthorized goal changes |
| ASI-02 Tool Misuse | 部分（tool scoping proposal） | Capability model enforces least-privilege |
| ASI-03 Identity Abuse | ❌ 無 Ed25519 | Ed25519 / SPIFFE zero-trust identity |
| ASI-04 Supply Chain | ❌ | Dependency-confusion scanning |
| ASI-05 Unexpected Execution | 部分（RING-3 sandbox） | 4-tier rings + sandboxing |
| ASI-06 Memory Poisoning | 部分（episodic memory 有） | Episodic memory integrity checks |
| ASI-07 Insecure Comm | 部分（MCP gateway） | Encrypted channels + trust gates |
| ASI-08 Cascading Failures | 部分（SLO tracking） | Circuit breakers + SLO enforcement |
| ASI-09 Human Trust | 部分（audit log） | Full audit trails + flight recorder |
| ASI-10 Rogue Agents | 部分（HMAC proposal） | Kill switch + ring isolation + anomaly detection |

**最大缺口：ASI-03（Identity）** — Hermes 目前沒有任何 cryptographic identity 機制。AGT 的 Ed25519 / SPIFFE 證書系統是 Zero-Trust 的基礎。這個缺口影響深遠：無法真正實現 inter-agent trust。

## COMPARISON.md 的實用 framing

> "They guard LLM outputs. We govern agent actions. Complementary, not competing."

這個 framing 讓我們可以直接定位 Hermes 的 positioning：**Hermes 是 Agent Action Layer 的governance infrastructure，not an LLM output validator**。這簡化了工具選擇決策——不需要考慮 NeMo/Guardrails，專注在 action governance。

## Competitive Landscape — 實際產品定位

| 工具 | 層 | 適合 Hermes 嗎 |
|------|---|---------------|
| Agent Governance Toolkit | Agent Action ✅ | ✅ 直接採用架構 |
| NeMo Guardrails | LLM Output ❌ | ❌ 不是同一層問題 |
| Guardrails AI | LLM Output ❌ | ❌ 不是同一層問題 |
| LiteLLM | LLM Gateway ❌ | ❌ 不是同一層問題 |
| Portkey | LLM Gateway ❌ | ❌ 不是同一層問題 |

## 對 WS-035 的影響

WS-035 的 Policy Engine SPIKE 現在有了更清晰的 competitive context：
- AGT Policy Engine 是當前最好的 agent action governance spec
- 它與 Hermes 的架構位置完全匹配（都是 agent action layer）
- 缺口分析直接導出實作優先級（ASI-03 Identity 最優先）

## 未追蹤 Leads
- `AGENT-OS-POLICY-ENGINE-1.0.md` — PolicyDocument schema，YAML policy format
- `agent-governance-python/agent-os/docs/TRUST-SCORING.md` — Trust score algorithm 0-1000
- `docs/benchmarks/OWASP-agentic-top10-architecture.md` — 詳細 OWASP mapping

## ✅ 本次探索完成
