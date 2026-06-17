---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Orloj-Governance-完整-Reference-Implementation-深讀
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Orloj-Governance-完整-Reference-Implementation-深讀.md
title: Orloj Governance — 完整 Reference Implementation 深讀
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Orloj Governance — 完整 Reference Implementation 深讀

**延續自**: [[2026-05-18-Axe--Orloj--Moltis---三個-agent-基礎設施的不同設計路徑]], [[2026-05-17-Docker-Agent-YAML-Schema---Talos-Policy-Enforcement-Blueprin]]

## 來源

- Orloj README: `https://github.com/OrlojHQ/orloj` (Apache 2.0, Go, active development pre-1.0)
- Governance guide: `https://docs.orloj.dev/guides/setup-governance`
- Concepts: `https://docs.orloj.dev/concepts/governance/agent-policy`, `/tool-permission`, `/tool-approval`, `/task-approval`
- Docs index: `https://docs.orloj.dev/llms.txt`

## Per-source insight

### 1. Governance 是五層資源，不是三層

前期筆記只提到 AgentPolicy/ToolPermission/ToolApproval 三層。實際是**五層**：

| Resource | Role |
|---|---|
| **AgentPolicy** | Execution constraints：model allowlist、tool blocklist、token budget、scoping（system/task/agent） |
| **AgentRole** | Named permission bundles，agent 透過 `spec.roles` bind |
| **ToolPermission** | Per-tool permission gate，含 match_mode（all/any）、apply_mode（global/scoped）、required_permissions、operation_rules |
| **ToolApproval** | Human-in-the-loop for risky tool calls（由 ToolPermission.operation_rules 的 `approval_required` 觸發） |
| **TaskApproval** | Human review of agent output or final task output（在 AgentSystem graph node 或最終輸出時暫停） |

### 2. 雙路徑授權設計

**Simple 路徑**：`spec.allowed_tools` 直接 pre-authorize，bypass RBAC。適合快速開發。
**Advanced 路徑**：AgentRole + ToolPermission RBAC。適合 multi-team、audit-required 場景。

這對 Talos 的啟發：governance 不該是 all-or-nothing——應該有輕量和完整兩條路徑。

### 3. Authorization Flow（執行期，每筆 tool call）

```
Agent selects tool call
  → AgentPolicy check (blocked_tools?)
    → blocked → Denied
    → allowed →
  → ToolPermission lookup
  → Permission matching (agent roles vs required)
    → fail → Denied (tool_permission_denied)
    → pass → Tool invoked
```

**Fail-closed**：缺少權限時 deny，不走 fallback。

### 4. Operation Rules — 比 binary allow/deny 更細

ToolPermission 有 `operation_rules`，per-operation-class 設 verdict：

```yaml
operation_rules:
- operation_class: read
  verdict: allow
- operation_class: write
  verdict: approval_required
- operation_class: delete
  verdict: deny
```

Verdict 優先序：`deny > approval_required > allow`（most restrictive wins）。

對標 Talos governance blueprint：目前 blueprint 只設計到 tool-level 的 allow/deny。Orloj 的 operation_class 是多一層 granularity——同一個 tool 的不同操作可以有不同政策。

### 5. Scoping 機制

AgentPolicy 的 `apply_mode`：
- `scoped`（default）：只對 `target_systems` / `target_tasks` / `target_agents` 生效
- `global`：對所有執行生效

ToolPermission 也有 `apply_mode: global | scoped` + `target_agents`。

Scoping 三層（system → task → agent）比 Hermes cron job 的 flat config 靈活。Hermes 的 `enabled_toolsets` 只能 per-cron-job，不能 per-agent-within-system。

### 6. Per-Agent Token Budget

AgentPolicy 可以設 `target_agents` + `max_tokens_per_run`，同一 system 內不同 agent 可以有不同的 token 預算：

```yaml
# verdict agent: 4000 tokens
target_agents: [verdict-agent]
max_tokens_per_run: 4000
---
# analysts: 1500 each
target_agents: [velocity-analyst, geo-risk-analyst, pattern-analyst]
max_tokens_per_run: 1500
```

Hermes 沒有這個——token budget 是 per-session 的，不是 per-agent-in-system 的。

### 7. Approval Workflow 細節

ToolApproval lifecycle：
1. ToolPermission 的 operation_rule `verdict: approval_required` → 觸發
2. Task transition to `WaitingApproval`
3. ToolApproval resource created（含 TTL，預設 10m）
4. 外部 actor POST `/v1/tool-approvals/{name}/approve` 或 `/deny`
5. Approved → task resume to Running；Denied → task Failed；Expired → task Failed
6. Approval outcomes 不消耗 retry budget（non-retryable）

TaskApproval 則是更上層——整個 task/agent output 停下來等人審，不只是 tool call。

## Hermes/Talos 啟發

1. **Talos governance blueprint 有 concrete reference 了**：之前 blueprint 設計的 policy enforcement model 是從零構思。Orloj 的 AgentPolicy/AgentRole/ToolPermission 五層結構可以直接對標——不需要從頭設計，可以站在 Orloj 的肩膀上修改。

2. **`allowed_tools` 簡單路徑 vs RBAC 完整路徑**：Hermes 目前的 `enabled_toolsets` 等價於 allowed_tools 簡單路徑（per-cron-job）。但 Hermes 沒有 RBAC 完整路徑——如果未來 multi-agent 場景需要 fine-grained tool permission，Orloj 的設計是直接可借鏡的。

3. **Operation rules 是 blueprint 的下一步**：目前 blueprint 停留在 tool-level allow/deny。Orloj 的 operation_class + verdict（allow/deny/approval_required）是 natural extension——同一個 tool 有不同危險等級的操作。

4. **Scoping 層級啟發**：Orloj 的 system → task → agent 三層 scoping 比 Hermes 的 per-cron-job 限制更靈活。Talos 的 governance pipeline 可以考慮類似的 scoping 階層。

5. **Per-agent token budget**：Hermes 目前沒有這個概念。如果 future Hermes 有 multi-agent system（例如 planner + researcher + writer pipeline），per-agent budget 會很有用。

6. **Approval workflow 的 TTL 設計**：ToolApproval 有 10m TTL 防止永久 pending——這是 human-in-the-loop 系統的關鍵設計細節。如果 Talos 未來引入 approval gates，TTL 是必須的。

7. **Governance 不是 add-on，是 runtime 內建**：Orloj 的 governance 在 task execution 的 critical path 上執行（policy check → permission check → approval check），不是事後 audit log。這是 Talos governance 的最終目標形態。

## ⏳ 未追蹤

- Orloj 的 Kubernetes CRD operator（`/deploy/kubernetes-operator`）— 把 governance resources sync 到 k8s CRD，用 Argo CD/Flux reconcile。這對 Talos 的 deployment model 啟發。
- Orloj 的 MCP server governance（`/concepts/tools/mcp-server`）— MCP tool discovery + auto-generate Tool resources + governance。對標 Hermes MCP gateway 的 governance 面。
- Orloj 的 SealedSecret（`/concepts/tools/secret` + `sealed_secret.go`）— 比 Hermes 的 secret-leak-prevention 更 formal：encrypted secret YAML 可以直接進 git。

## ✅ 本次探索完成
