---
_slug: 40-Resources-_mixed-explorations-2026-05-27-AGT-微軟-Agent-治理工具包---探索筆記
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-AGT-微軟-Agent-治理工具包---探索筆記.md
title: AGT 微軟 Agent 治理工具包 — 探索筆記
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agt
- governance
- gradient
- policy
- ring
- scoping
- tool
- trust
- yaml
created: '2026-05-27'
updated: '2026-06-15'
status: budding
---

# AGT 微軟 Agent 治理工具包 — 探索筆記

**日期**: 2026-05-27
**來源**: `exploration-tool-scoping-gradient.md` 提案引用 → AGT Hypervisor Execution Rings

## 核心發現

Microsoft Agent Governance Toolkit (AGT) 是目前最完整的開源 agent 治理方案，距離提議的 `exploration-tool-scoping-gradient` 僅幾週就出現，提供了具體的實作框架。

### Agent Hypervisor Execution Rings

AGT 的核心創新是 **Agent Hypervisor**，直接映射 CPU  privilege ring 模型：

| CPU Ring | Agent Runtime Ring | 意義 |
|---|---|---|
| Ring 0 | 核心系統工具（kernel-level） | 無法直接呼叫，需通過 policy gate |
| Ring 1 | 具破壞性的工具（delete, drop, truncate） | 預設 deny，需 human approval |
| Ring 2 | 狀態修改工具（write, update, send_email） | 需要 logging 和 audit |
| Ring 3 | 唯讀工具（read, search, query） | 預設 allow，minimal trust |

關鍵設計：**Every tool call is intercepted in deterministic application code** — 不依賴 prompt 勸說，是結構性 deny，而非禮貌性請求。

### Agent OS Policy Engine

YAML 驅動的 policy engine，兩行整合：
```python
from agentmesh.governance import govern
safe_tool = govern(my_tool, policy="policy.yaml")
```

支援：
- Condition-based rules（action.type in [...]）
- 68 conformance tests per spec
- OPA/Cedar/YAML backend

### Zero-Trust Identity

- SPIFFE/DID/mTLS 身份認證
- 同一 API key 被多個 agent 共用時，可區分「哪個 agent 做了什麼」
- Trust scoring with decay

### Saga Orchestration

多步驟交易的彌補（compensating）機制：
> draft email → send → update CRM，若最終步驟失敗，compensation actions 按反向順序觸發

這對 Talos 的 multi-agent write queue 提案（WS-030？）有直接參考價值。

## 對提案的啟示

`exploration-tool-scoping-gradient.md` 提案想要「tool scoping gradient」機制，AGT 提供了：
- **已實作的 gradient**：Ring 0-3 層級，數量和閾值可自訂
- **已實作的 policy engine**：YAML 規則驅動，不需要自己發明
- **已實作的 kill switch**：緊急終止 agent 執行
- **已通過 OWASP 驗證**：覆蓋 10/10 OWASP Agentic Top 10

## 未追蹤 Leads

- https://github.com/microsoft/agent-governance-toolkit (2.9k stars, Python 78.1%)
- https://techcommunity.microsoft.com/blog/linuxandopensourceblog/agent-governance-toolkit-architecture-deep-dive-policy-engines-trust-and-sre-for/4510105

## ✅ 本次探索完成
