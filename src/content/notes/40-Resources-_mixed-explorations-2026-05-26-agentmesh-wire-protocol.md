---
_slug: 40-Resources-_mixed-explorations-2026-05-26-agentmesh-wire-protocol
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-agentmesh-wire-protocol.md
title: 探索：AgentMesh Wire Protocol 1.0 — 2026-05-26
created: '2026-05-26'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：AgentMesh Wire Protocol 1.0 — 2026-05-26

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/specs/AGENTMESH-WIRE-1.0.md
**Status**: Draft · 2026-04-21 · Microsoft AGT team
**Length**: 1028 lines (raw) → 782 lines (sanitized)

## TL;DR — Wire Protocol 是什麼

AgentMesh 的通信層：E2E encrypted agent-to-agent messaging，定義了 4 種角色（Initiator/Responder/Relay/Observer）和 3 種 channel 類型（trust_channel/anon_channel/delayed_channel）。

## 核心元件

### 角色模型（Section 3）
- **Initiator**: 發起連線方（client）
- **Responder**: 接收方（server）
- **Relay**: 中間轉發（不具備 keys，只能轉發加密內容）
- **Observer**: 監聽方（需雙方同意才能上線）

### Channel 類型
- `trust_channel`: 雙方已有 trust relationship，直接加密
- `anon_channel`: 匿名通道，使用 route redirect 避免暴露 IP
- `delayed_channel`: 離線消息轉發（類似 email 的 async 模式）

### E2E Encryption（Section 5）
- 使用 X25519 key exchange + ChaCha20-Poly1305 AEAD
- Forward secrecy: 每個 session 獨立EPHEMERAL KEY
- Identity binding: KEY CONFIRMATION 步驟防中間人攻擊

### Message Format（Section 4）
- Frame structure: `VERSION | FLAGS | SRC | DST | TIMESTAMP | NONCE | CIPHERTEXT | HMAC`
- All fields fixed-size (no variable-length headers)
- `HMAC-SHA256` over entire frame (not just ciphertext)

### Trust Establishment（Section 6）
- Out-of-band verification: 指紋比對、QR code scan
- Trust escalation: `anonymous → trust_verified → fully_trusted`
- 層級可降（trust revocation）

### Routing（Section 7）
- 支援 Onion routing: 多 Relay 串聯，每層獨立加密
- Route redirect: 隱藏真實 endpoint IP
- 支援 MQTT 和 libp2p 兩種 transport（Section 8）

### 延遲通道（Section 9）
- Offline message relay: message 存儲在 Relay 直到目標上線
- TTL + 降級策略：超過 7d 的 message 降級到 cold storage
- Deletion protocol: 双方 delete 後 Relay 移除備份

## 與前期筆記的關連

1. **Policy Engine（2026-05-27 筆記）**：Wire Protocol 提供的是 transport layer security，Policy Engine 提供的是 authorization layer。兩者組合 = 完整的安全通信棧（TLS + mTLS + policy enforcement）。

2. **Trust Coordination（2026-05-26）**：`AGENTMESH-TRUST-COORDINATION-1.0.md` 處理 trust 建立和維護，Wire Protocol 是其 transport 底層。Trust Coordination 使用 Wire Protocol 的加密通道建立 trust relationship。

3. **WS-028（Agent Lifecycle Governance）**：Wire Protocol 的 trust escalation 模型（anonymous → trust_verified → fully_trusted）正是 earned autonomy gradient 的具象化——初始連線匿名，隨著互動歷史累积 trust level。

4. **Execution Rings**：Wire Protocol 的 Relay role 不具備 keys（只能轉發），對應 Ring 3 Sandbox（無 filesystem、無 network direct）的隔離概念。

## Hermes 啟發

1. **E2E encryption 的最小實現**：Wire Protocol 的 X25519 + ChaCha20-Poly1305 是現代標準，libsodium 封裝良好。Hermes 目前無 agent-to-agent 加密通信，但 vault sync 和 heartbeat relay 已實現——若要加強安全性，Wire Protocol 的 key exchange pattern 值得參考。

2. **Trust escalation 應用於 agent session**：anonymous → trust_verified 的分級模型可以用來管理 cron job 的執行權限（exploration agent = anonymous, verified cron = trust_verified, approved operation = fully_trusted）。

3. **Delayed channel 適用於 async 協調**：Talos 和 Hestia 的通信有時差，delayed_channel（TTL 7d、cold storage降級）正好解決「agent 離線時的 message retention」問題。

## 未追蹤 leads

- ✅ `AGENTMESH-WIRE-1.0.md` — 1028 lines，活得，已 fetch 完成
- ✅ `AGENTMESH-IDENTITY-TRUST-1.0.md` — 活得，已於 2026-05-26 fetch（見 [[2026-05-26-agt-identity-sre-hypervisor-specs]]）
- ❌ `AGENT-SRE-1.0.md` — 404（確認死 lead）
- ❌ `AGENTMESH-IDENTITY-AND-TRUST-1.0.md` — 404（確認死 lead）

## ✅ 本次探索完成