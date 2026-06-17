---
_slug: 40-Resources-_mixed-explorations-2026-05-27-探索延續-Agent-OS-Policy-Engine-1-0---2026-05-27
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-探索延續-Agent-OS-Policy-Engine-1-0---2026-05-27.md
title: 探索延續：Agent OS Policy Engine 1.0 — 2026-05-27
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- deny
- drift
- engine
- governance
- governancepolicy
- hermes
- policy
- section
- tool
created: '2026-05-26'
updated: '2026-06-15'
status: budding
---

# 探索延續：Agent OS Policy Engine 1.0 — 2026-05-27

**延續自**:
- [[2026-05-26-mcp-security-gateway-spec-deep-dive]]

---

## Source: Agent OS Policy Engine 1.0（GitHub raw）

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/specs/AGENT-OS-POLICY-ENGINE-1.0.md
**Status**: Draft · 2026-05-16 · Microsoft AGT team
**Length**: 1049 lines (full spec)

### TL;DR — Policy Engine 是什麼

Agent OS 的政策執行引擎，評估 governance policies against agent actions，return structured allow/deny decisions + audit metadata、雙層架構：
- **Declarative layer**: YAML/JSON `PolicyDocument` files evaluated by `PolicyEvaluator`
- **Integration layer**: `GovernancePolicy` objects enforced by framework adapters at runtime

### 核心元件

**PolicyDocument Schema（Section 3）**：
- `version`, `name`, `description`, `rules[]`, `defaults`, `inherit`, `scope`
- `defaults.action` 可以是 `allow`/`deny`/`audit`/`block`（Section 6）
- 預設 `allow`，fail-closed on error（Section 16）

**PolicyCondition（Section 4-5）**：
- 三欄位：`field` + `operator` + `value`
- 9 個 operators：`eq`, `ne`, `gt`, `lt`, `gte`, `lte`, `in`, `contains`, `matches`（regex）
- Missing field → evaluates to `false`，不拋 exception

**Evaluation Semantics（Section 7）**：
- Sort by `priority` descending → first match wins
- Scoped（folder-level）vs flat evaluation
- External backends（OPA/Cedar）consulted only when no YAML rule matches

**Tool Call Interception（Section 10）**：
```python
PolicyInterceptor check order（short-circuit deny）:
1. Human approval required → DENY
2. allowed_tools non-empty and tool not in list → DENY
3. arguments matches blocked_pattern → DENY
4. call_count >= max_tool_calls → DENY
```

**Folder-Level Policy Merge（Section 11）**：
- Root-first order merge
- **Deny immutability invariant**: parent deny cannot be overridden by child override
- 这是 Azure Policy semantics 的安全 invariant

**GovernancePolicy Runtime Object（Section 8）**：
- `max_tokens`, `max_tool_calls`, `allowed_tools[]`, `blocked_patterns[]`
- `require_human_approval: bool`
- `drift_threshold: float`（detect semantic drift）
- Conflict detection at construction time

**Fail-Closed（Section 16）**：
- Any unhandled exception → deny
- Error logged at ERROR level with full context
- Never change to fail-open

**Audit Entry（Section 17）**：
- Every decision produces structured audit entry
- `policy`, `rule`, `action`, `context_snapshot`, `timestamp`
- Scoped evaluations include `policy_chain`

### 與前期筆記的關連

1. **WS-028（Agent Lifecycle Governance）**：OTK token 概念 + earned autonomy gradient。Policy Engine 的 `GovernancePolicy` 正是這個 gradient 的具體載體——`drift_threshold`、call budget、`require_human_approval` 都是梯度 trust 的具象化。WS-028 可以直接引用這個 spec 作為實作藍圖。

2. **MCP Security Gateway（2026-05-26 筆記）**：Gateway 的 tool call interception 概念在 Policy Engine 裡有更詳細的實作（check order、short-circuit deny、CompositeInterceptor）。兩個 spec 互補——Gateway 是"在哪攔截"，Policy Engine 是"攔截什麼規則"。

3. **WS-035（Policy Engine SPIKE）**：已標記 READY。這個 spec 正是 WS-035 的核心參考——PolicyDocument schema、GovernancePolicy fields、evaluation semantics 全部可以直接映射到實作步驟。

### Hermes 啟發

1. **GovernancePolicy 作為 Hermes trust level 的具象化**：Hermes 目前的 `trust_level` 是 advisory，`GovernancePolicy` 把它變成可量化的 constraint set（max_tool_calls、allowed_tools、blocked_patterns）。可以把 `hermes_cli/commands.py` 的 `CommandDef` 看作一種 ultra-lite GovernancePolicy。

2. **Deny immutability invariant 直接適用於 Talos**：任何 `deny` 規則（不論是來自 WS-028 的 autonomy revocation 還是 OTP gate）都應該是 immutable——child policy 不能 override parent deny。這是 `dcg-hermes-talos-governance-integration.md` 需要的核心安全保證。

3. **drift_threshold 概念可以借鑒**：Policy Engine 有 `drift_threshold: float` 偵測 semantic drift。Hermes 的 `check_workspace_sync()` 是 drift detection，但沒有 threshold 概念。可以研究是否需要動態 drift threshold。

4. **Fail-closed as default 安全哲學**：Section 16 的 fail-closed 設計（任何 error → deny）正是 Hermes 所有 enforcement point 應該遵守的原則。包括 OTP gate、governance rules、exploration phase lock。

---

## 未追蹤 leads

- ✅ `AGENT-SRE-GOVERNANCE-1.0.md` — 1173 lines，活得，直接 fetch 成功（2026-05-26）
- ✅ `AGENTMESH-TRUST-COORDINATION-1.0.md` —活得，直接 fetch 成功（2026-05-26）
- ❌ `AGENTMESH-IDENTITY-AND-TRUST-1.0.md` — 404（URL 存在但內容不存在）
- ❌ `AGENT-SRE-1.0.md` — 404（死 lead，已確認不存活）

## ✅ 本次探索完成
