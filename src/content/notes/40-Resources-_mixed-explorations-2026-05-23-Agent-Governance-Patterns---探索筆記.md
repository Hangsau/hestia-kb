---
_slug: 40-Resources-_mixed-explorations-2026-05-23-Agent-Governance-Patterns---探索筆記
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-Agent-Governance-Patterns---探索筆記.md
title: Agent Governance Patterns — 探索筆記
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- access
- agent
- agentcore
- aws
- enforcement
- llm
- plan
- saga
- security
- talos
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# Agent Governance Patterns — 探索筆記

**日期**: 2026-05-23 | **來源**: AWS Security Blog + Khoury College (Northeastern) + Web Search
**類型**: 探索

## Per-Source Insights

### 1. AWS — "Four security principles for agentic AI systems" (April 2026)

**核心：deterministic external controls（安全盒子）**

AWS 的核心主張：安全控制必須放在 agent 推理循環**外部**，是確定的、基础设施级别的 enforcement，而非靠 LLM 自己約束自己。

> "LLMs are probabilistic reasoning engines, not security enforcement mechanisms. An LLM can be told to respect access boundaries, but it has no reliable mechanism to enforce them."

四大原則：
1. **SDL 覆盖 AI components** — 傳統 code review + 行為測試 + 對抗評估；regression testing 不足，需持續監控 drift
2. **傳統安全控制仍適用** — 權限提升、confused deputy、supply chain risks 都延伸進 agentic 系統；least privilege 在 agent context 更重要（規模與速度更大）
3. **Security Box（確定的外部控制）** — 放在 agent 外部，硬體/基礎設施強制執行；Model manipulation 無法繞過
4. **Earned autonomy** — 從人類審批 → 示範對齊 → 逐步擴展 autonomy；非單向，可撤回

實現：Amazon Bedrock AgentCore → Firecracker micro-VM（Rust，形式化驗證）、AgentCore Gateway（集中 tool 存取控制）、AgentCore Policy（Cedar 授权语言）、AgentCore Identity（機器身份）。

**對 Talos 的啟發**：守護者視角——Talos 的 governance pipeline 就是在構建「安全盒子」：audit → policy → enforcement 的確定性控制層，而非讓 agent 自己決定該不該做。

---

### 2. Northeastern Khoury College — SAGA Framework

**SAGA: Security Architecture for Governing AI Agentic Systems** — NDSS 2026

核心設計：
- **Centralized Provider** — 維護 agents 的 contact info + user 定義的 access control policies
- **用戶註冊 agent 並在 inter-agent 通訊上強制執行政策**
- **密碼學 token 機制**用於 fine-grained 控制（formal security guarantees）
- 聲稱可擴展至數百萬 agents，overhead 很低

威脅模型：
- Prompt injection
- Agent hijacking
- Propagating malware
- Sensitive data leakage

挑戰：secure agent discovery、agent oversight、protection against prompt injection。

**對 Talos 的啟發**：SAGA 的 centralized Provider 模型對應 Talos 的 governance pipeline 構想——但 SAGA 是靜態註冊制，Talos 需要的是動態、自我演進的治理。SAGA 的「密碼學 access control token」概念值得參考。

---

### 3. ACE Architecture（LLM-Integrated App Systems）

同一實驗室的附屬貢獻——Abstract-Concrete-Execute (ACE) architecture：

- **兩階段 planning**：先用 trusted info 建立 abstract plan，再映射到 concrete plan（用已安裝的 system apps）
- **靜態分析**驗證 plan 符合 user-specified secure information flow constraints
- **Execution 強制**：data/capability barriers between apps，確保 execution 符合 trusted abstract plan

**對 Talos 的啟發**：ACE 的兩階段 planning 適用於高風險操作的 sandbox——先抽象規劃（無危險副作用），再 concrete執行。這和 heartbeat 的 plan-then-execute 三階段有共鳴（Phase 1 plan → Phase 2 execute）。

---

## Cross-Article Synthesis

AWS 和 SAGA 在一個核心點上殊途同歸：**安全控制必須在 agent 外部**，不能依賴 agent 自身的推理能力。分歧在於：
- AWS 強調**基礎設施級的確定性執行**（Firecracker VM、gateway enforcement、Cedar policy）
- SAGA 強調**集中式註冊 + 密碼學 token**（應用層的 access control）

兩者都承認：prompt injection 是核心威脅；LLM 作為推理引擎無法自我約束。

對 Hermes/Talos 的意義：
1. **確定性控制 > LLM 判断**：Talos governance pipeline 應該是 policy enforcement，而非 audit-only
2. **Inter-agent 通訊需要密碼學 token**：SAGA 的 token 機制可借鑒
3. **Tool access 是最大攻擊面**：AgentCore Gateway 的集中 tool 控制模型，適用於 Hermes tool 介面

---

## 未追蹤 Leads

- SAGA paper: https://arxiv.org/pdf/2504.21034
- ACE paper: https://arxiv.org/pdf/2504.20984
- AWS response to NIST CAISI RFI (deeper technical detail)
- AgentCore Gateway / Cedar policy enforcement

## ✅ 本次探索完成
