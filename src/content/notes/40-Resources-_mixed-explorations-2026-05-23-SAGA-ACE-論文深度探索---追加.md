---
_slug: 40-Resources-_mixed-explorations-2026-05-23-SAGA-ACE-論文深度探索---追加
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-SAGA-ACE-論文深度探索---追加.md
title: SAGA/ACE 論文深度探索 — 追加
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- access
- agent
- hermes
- otk
- pac
- provider
- saga
- talos
- token
- user
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# SAGA/ACE 論文深度探索 — 追加

**日期**: 2026-05-23 | **來源**: arXiv 2504.21034（直接 fetch） | **延續自**: [[2026-05-23-agent-governance-patterns]]

## 主要發現

### SAGA 核心機制（之前筆記只有概述，fetch 後確認的細節）

**User Registration**：
- User 生成 `uid_U` + `passwd` + keypair `(SK_U, PK_U)`
- 透過 service S 驗證人類身份（人類驗證是防禦 A7 的關鍵）
- Provider 維護 `D_U[uid_U] = <H(passwd), Cert_U>`

**Agent Registration**：
- User 為每個 agent 生成 `aid_A` + endpoint description (`ED_A`) + contact policy (`CP_A`)
- 一次生成 N 個 OTK（public, stored at Provider）+ secret（stored locally）
- 簽名流程：`σ_A^U = Sign_SK_U(<aid_A, ED_A, PK_A, PAC_A, PK_Prov>)`
- Provider 驗證後發回 `σ_A^Prov = Sign_SK_Prov(<Cert_U, ED_A, PAC_A, σ_A^U>)`

**Agent Communication（核心握手）**：
1. B 向 Provider 請求接觸 A → Provider 檢查 `Budget_OTK(aid_B, aid_A) > 0`
2. Provider 返回 A 的 metadata + OTK_i + σ（由 U1 簽名）
3. B 驗證簽名 → 建立 TLS → Diffie-Hellman 交換
4. A 用 DH shared key 加密並發送 Access Control Token（含 expiry + quota）
5. B 在後續所有通訊附上 token（不再需要 Provider）

**Key insight — 密碼學 token 的 vulnerability window**：
- token 包含 `<N, T_issued, T_expire, Q_max, PAC_B>`（PAC_B = intended recipient）
- 發送方在驗證時檢查 token 的 `PAC` 與自己匹配（A5 攻擊的防禦）
- A8 攻擊：即便攻擊者有有效 token，vulnerability window 由 `T_expire` 和 `Q_max` 決定

**ProVerif 形式驗證**：攻擊者模型是 Dolev-Yao（可觀察/攔截/重放/重排序/合成任意訊息）。SAGA 在此模型下被證明滿足：
- Token secrecy
- Agent 與 Provider 間的 authentication
- 任意兩 agent 間的 mutual authentication

**Fault Tolerance**：
- RAFT replication：5-node replica throughput degradation 幾乎為零
- Sharding：linear throughput increase（7 sharders + 24h token → 260M agents）
- 這對 Talos 的 governance pipeline 有直接意義：Talos 作為 Provider 角色需要 fault tolerance

### ACE Architecture（2504.20984，附帶）

與 SAGA 同實驗室，補充：
- Abstract plan → Concrete plan 的兩階段 planning
- 靜態分析驗證符合 user 安全約束
- 執行時 data/capability barriers 確保不偏离 trusted abstract plan
- 對應 heartbeat 的 Phase 1 (Plan) / Phase 2 (Execute) 架構

## 對 Hermes/Talos 的直接應用

### 1. Talos 作為 SAGA Provider 的實現路徑

SAGA 的 Provider 維護：User Registry + Agent Registry + OTK Budget + Contact Policies
Talos 目前沒有這些結構，但需求類似：

```
Talos governance pipeline 需要：
- User/Agent identity registry（Hearth task system 已有 user/agent 概念）
- Access control policies（現行的是 task-level，沒有 agent-level）
- OTK mechanism（目前每個 action 都是「一次性」——但缺 token 機制）
```

**缺口**：Talos 目前是 audit-only，沒有 OTK/token 機制。SAGA 的設計可以移植。

### 2. Hermes Tool Access 作為 AgentCore Gateway

AWS AgentCore Gateway = 集中 tool 存取控制。Hermes 的 tool interface 目前是 flat list，沒有分層控制。

可探索：`~/.hermes/tools/` 下的 tool 定義加 `access_policy` 欄位，讓 Talos enforcement。

### 3. Earned Autonomy 梯度

AWS 的「earned autonomy」概念：從 human approval → demonstration → gradual expansion。

對 heartbeat system：每個心跳 cycle 可以被視為一個「demonstration」。如果連續 N 次乾淨（無 error/warning），可以擴展 autonomy scope（例如探索更深的 topic 或執行更高風險的 action）。

這個指標目前在 EVOLVE 輸出中已經有（clean steps count），但沒有被用來調整 autonomy level。

## ✅ 本次追加完成

實際 fetch 了 SAGA paper（120K+ chars），確認了之前筆記的概述與原文一致，並發現了三個具體可行動的點：
1. Talos 需要 Agent Registry 結構
2. Hermes tool 層可加 access policy
3. Earned autonomy gradient 可整合進 EVOLVE
