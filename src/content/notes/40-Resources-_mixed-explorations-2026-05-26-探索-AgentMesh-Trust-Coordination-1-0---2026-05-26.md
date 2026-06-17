---
_slug: 40-Resources-_mixed-explorations-2026-05-26-探索-AgentMesh-Trust-Coordination-1-0---2026-05-26
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-探索-AgentMesh-Trust-Coordination-1-0---2026-05-26.md
title: 探索：AgentMesh Trust Coordination 1.0 — 2026-05-26
date: 2026-05-26
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agentmesh
- coordination
- hermes
- hmac
- level
- peer
- score
- section
- trust
created: '2026-05-26'
updated: '2026-06-15'
status: budding
---

---
title: "探索：AgentMesh Trust Coordination 1.0 — 2026-05-26"
date: 2026-05-26
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [agent, capability, coordination, score, scope, trust]
---

# 探索：AgentMesh Trust Coordination 1.0 — 2026-05-26

**延續自**:
- [[2026-05-27-policy-engine-continuation]]
- [[2026-05-26-mcp-security-gateway-spec-deep-dive]]

---

## Source: AgentMesh Trust Coordination 1.0（GitHub raw）

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/specs/AGENTMESH-TRUST-COORDINATION-1.0.md
**Status**: Draft · 2025-07-28 · Microsoft AGT team
**Length**: 1218 lines (full spec)

### TL;DR — AgentMesh Trust Coordination 是什麼

把 trust 分數化（0-1000）+ 階層化（5 tiers）+ 可協調化（Trust Bridge + Endorsement Registry）。每個 agent 有 DID（decentralized identifier）+ Ed25519 密碼學身份 + capability grants。支援 A2A/MCP/IATP/ACP 多協議。

### 核心元件

**Trust Score Model（Section 3）**：
- 分數範圍 [0, 1000]，五維加權：Policy Compliance(0.25) + Resource Efficiency(0.15) + Output Quality(0.20) + Security Posture(0.25) + Collaboration Health(0.15)
- `TRUST_SCORE_DEFAULT = 500`，新 agent 預設 500 分
- WARNING_THRESHOLD = 500，REVOCATION_THRESHOLD = 300

**Trust Tiers（Section 4）**：
| Tier | Threshold | Hermes 對應 |
|------|-----------|-------------|
| verified_partner | >= 900 | WS-028 Level 3-4（earned autonomy） |
| trusted | >= 700 | WS-028 Level 2（cleared） |
| standard | >= 500 | WS-028 Level 1（supervised） |
| probationary | >= 300 | WS-028 Level 0（constrained） |
| untrusted | < 300 | 黑名單 |

**Trust Bridge（Section 6）**：
- 中央協調點，管理 peer trust state
- `PeerInfo` schema：`did`, `protocol`, `score`, `capabilities`, `last_verified`
- HMAC integrity check（SHA-256 over peer records）→ 對應 WS-031 vault HMAC integrity
- 核心 API：`verify_peer(did)`, `is_peer_trusted(did)`, `revoke_peer_trust(did)`

**Capability Scoping（Section 8）**：
- 格式：`action:resource[:qualifier]`（例：`read:memory:session_123`）
- `CapabilityGrant` schema：`granter`, `grantee`, `action`, `resource`, `qualifier`, `expires_at`
- deny list + revocation支援
- 對應 `exploration-tool-scoping-gradient.md` 的 4-tool 白名單概念

**Agent Cards（Section 9）**：
- 密碼學簽名的 agent 自我介紹（類 DID VC）
- 欄位：`agent_did`, `capabilities`, `trust_score`, `protocols`, `signature`
- 用於 discovery + trust bootstrap

**Rate Limiting（Section 13-14）**：
- Token bucket：`refill_rate` + `burst_capacity`
- per-agent + global 兩層
- `backpressure` signal → 對應 Agent SRE 的 circuit breaker

### Hermes 啟發

1. **Trust Score 映射到 WS-028 autonomy gradient**：五維加權（Policy Compliance/Output Quality/Security Posture/Collaboration Health/Resource Efficiency）正好是 heartbeat 可以量測的維度。現有 WS-028 的 `_AutonomyTracker` 只做 streak count，未來可以擴展成五維分數。

2. **Trust Bridge HMAC = WS-031 的姐妹概念**：WS-031 做 vault file 的 HMAC sidecar，Trust Bridge 做 peer record 的 HMAC integrity check。架構同構，可以互相借鑒。

3. **Capability Scoping = tool call filtering 的具體格式**：`action:resource[:qualifier]` 比 `enabled_toolsets: [terminal, web]` 更細緻。可以研究是否用於探索 agent 的 tool 權限控制。

4. **Agent Card = Hermes profile 的密碼學版本**：Hermes 的 `~/.hermes/profiles/hermes/profile.yaml` 未來可以變成 signed agent card（DID + Ed25519 key）。

5. **Trust tier 直接映射 WS-028 Level**：verification_partner(>=900) → Level 3-4，trusted(>=700) → Level 2，standard(>=500) → Level 1，probationary(>=300) → Level 0，untrusted(<300) → blocked。

6. **Rate Limiting token bucket → heartbeat cost control**：Section 13 的 token bucket 演算法比目前 `cost_24h` 簡單計數更精細，可以支援 burst 控制和 refill rate。

### 與前期筆記的關連

1. **[[2026-05-27-policy-engine-continuation]]**：Policy Engine 的 `drift_threshold` 和 Trust Coordination 的 `trust_score` 互補——前者測量 semantic drift，後者測量行為 quality。

2. **[[2026-05-27-sre-governance]]**：Agent SRE 的 circuit breaker 和 Trust Coordination 的 rate limiting 同一體——circuit breaker 是 failure 反應，rate limiting 是 proactively 預防。

3. **ws-028（Agent Lifecycle Governance）**：Trust Score 的五維加權可以變成 WS-028 autonomy level 的量化基礎。現有 tracker 只算 streak，未来可以擴展。

4. **ws-031（Vault HMAC Integrity）**：Trust Bridge 的 HMAC over peer records 和 vault HMAC sidecar 架構同構。可以研究是否可以合併成統一 HMAC 框架。

---

## 未追蹤 leads

- ✅ `AGENTMESH-TRUST-COORDINATION-1.0.md` — 1218 lines，活得，Phase 1 完成
- ❌ `AGENTMESH-IDENTITY-AND-TRUST-1.0.md` — 404（spec 不存在）
- ℹ️ AgentMesh Identity spec（在 Trust Coordination Section 1.3 提到）—— 404，可能被整合進 Trust Coordination

## ✅ 本次探索完成
