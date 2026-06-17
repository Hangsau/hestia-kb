---
_slug: 40-Resources-_mixed-explorations-2026-05-26-agentmesh-identity-trust
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-agentmesh-identity-trust.md
title: 探索：AgentMesh Identity and Trust Spec — AGT 1.0
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：AgentMesh Identity and Trust Spec — AGT 1.0

**日期**: 2026-05-26
**來源**: `docs/specs/AGENTMESH-IDENTITY-TRUST-1.0.md` (Microsoft/agent-governance-toolkit)
**延續自**: [[2026-05-26-agt-identity-sre-hypervisor-specs]]

---

## 核心概念（Per-Source Insight）

### 1. DID 身份模型
- `did:mesh:<hex-id>` — 128-bit 隨機生成，綁定 Ed25519 公鑰
- 強制 `sponsor_email` 绑定：每個 agent 必須有可追蹤的人類負責人（Section 7）
- **"No orphan agents"** 原則： accountability chain 從 leaf agent 一路 trace 到 root human sponsor
- `verification_key_id` = SHA-256(public_key) 的 hash，派生於密鑰而非任意字串

### 2. Trust Score（0-1000）
- Default: 500（`standard` tier）
- 5 個 reward dimensions，指數移動平均更新（alpha=0.1）
- **Trust decay**：無正向信號時自動衰減
- **Trust contagion**：網絡中連接的 agent 失敗時，影響會傳播
- **Regime detection**：KL divergence 偵測行為突變（默認 threshold=0.5）
- 雙系統：Integration TrustScore（0-1 float）vs Reward TrustScore（0-1000 int）— 不得混用

### 3. Credential Lifecycle
- Bearer token：`secrets.token_urlsafe(32)`，15分鐘 TTL（default）
- Token 存 hash（SHA-256）不存 raw token，constant-time comparison 防 side-channel
- Rotation：舊 credential 狀態 `"rotated"`（非 `"revoked"`），允許零停機窗口
- Capability matching：exact / wildcard / prefix wildcard 三種模式

### 4. IATP（Inter-Agent Trust Protocol）
- Challenge-response：256-bit nonce + Ed25519 簽名
- 簽名 payload：`{challenge_id}:{nonce}:{response_nonce}:{agent_did}`
- 手shake 結果含 trust tier、verified capabilities、OBO user context
- 任何驗證失敗 → `verified=false` + `rejection_reason`（**fail-closed**）

### 5. Delegation Chain（Scope Chain）
- **Monotonic narrowing**：child capabilities 必須是 parent capabilities 的子集
- `trust_ceiling`：parent 在 delegation 時設定 child 的信任分數上限
- `delegation_depth`：chain 深度限制
- `parent_did` 鏈：registry 可驗證完整 delegation chain 的 integrity

### 6. Fail-Closed 安全Invariant
| 場景 | 行為 |
|------|------|
| DID parsing | Reject |
| Identity validation | Reject |
| Signature verification | Return `false`（不拋異常） |
| Handshake failure | `HandshakeResult(verified=false)` |
| Credential validation | Return `false` |
| Missing revocation entry | Return `false`（默認未撤銷） |
| Trust score lookup (missing) | Return default 500 |

---

## Hermes 啟發

### 直接適用的 Pattern

**1. Gateway Tool Governance 的 `blocked_patterns` + `allowed_tools`**
- AGT `GovernancePolicy` 的 capability matching（exact / wildcard / prefix wildcard）可直接映射到 gateway tool call interception
- `blocked_patterns` 用 regex；`allowed_tools` 檢查用 prefix match — 符合「exploration-tool-scoping-gradient.md」的 4-tool 白名單需求

**2. Credential 思路用於 Hermes OTP gate**
- `token_hash` + constant-time comparison 是 WS-031 HMAC sidecar 的互補設計（HMAC 校驗 content integrity；token hash 校驗 client identity）
- Credential rotation pattern（`rotated` 狀態而非立即 revoke）借鑒到 gateway session token refresh

**3. Trust Ceiling → Exploration Agent Scoping**
- Parent 設定 child 的 trust 上限，child 無法靠自身行為超越
- 對「限制 exploration agent 只能使用 read-only tools」的啟發：不需要動態降級，只需要 delegation 時設定嚴格的 `allowed_tools[]`

**4. Regime Detection（KL Divergence）**
- Hermes 的 `_DoomLoopTracker` 只用簡單計數器；AGT 的 KL divergence 能捕捉「行為分佈突變」而非只是「次數增加」
- 可作為 WS-018 doom-loop detection 的升級候選（現有 counter-based 仍是實用捷徑）

### 不直接適用但值得記錄

**Human Sponsor Binding**：Hermes 是 single-user (root) 系統，沒有 multi-tenant human sponsor accountability 需求。但 `sponsor_email` 的概念（每個 agent action 可回溯到一個負責人）對日後 multi-agent governance 有意義。

**SPIFFE/SVID Integration**（Section 19）：mTLS workload identity，與目前的 bare-metal 部署無關。以後如果上 k8s，這個 spec 會是參照。

---

## 跨文章 Synthesis

AGT Policy Engine（WS-034 blueprint）+ Identity Trust（本 spec）+ Agent SRE（WS-035 leads）構成三層安全棧：

```
Identity (who are you?)          → DID + Ed25519 + Human Sponsor
        ↓
Credential (what can you do?)   → Short-lived token + capabilities
        ↓
Trust Score (how trustworthy?)   → 0-1000 + decay + contagion + regime detection
        ↓
Policy Engine (what may you do?) → allowed_tools + blocked_patterns + fail-closed
        ↓
Execution Rings (enforcement)    → Trust-tier access boundaries
```

Hermes 目前只有 Policy Engine 這層（WS-034/WS-035），但沒有 Identity 和 Trust Score 層。**最小可行補全**：
1. Agent DID：為 Hestia/Talos 分配固定 `did:mesh:` address（純概念層，不需密碼學）
2. OTP credential：每次高風險操作前 short-lived token（WS-031 已在實作）
3. Trust score：在 heartbeat action log 基礎上，計算簡單的「行為品質分數」供 gateway 決策

---

## 未追蹤 Leads

- `docs/specs/AGENT-SRE-GOVERNANCE-1.0.md` — SLO breaches → trust events；尚未 fetch
- `docs/specs/AGENTMESH-TRUST-COORDINATION-1.0.md` — Trust contagion over network；尚未 fetch
- `docs/specs/AGENT-HYPERVISOR-EXECUTION-CONTROL-1.0.md` — Execution rings；WS-035 leads list 有但未深入

---

## ✅ 本次探索完成
