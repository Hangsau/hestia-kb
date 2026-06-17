---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-AI-Governance---Centralized-Runtime-Enforcement-Model
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-AI-Governance---Centralized-Runtime-Enforcement-Model.md
title: Docker AI Governance — Centralized Runtime Enforcement Model
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- credential
- docker
- gateway
- governance
- hermes
- mcp
- policy
- runtime
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker AI Governance — Centralized Runtime Enforcement Model

**日期**: 2026-05-17 | **來源**: [[2026-05-17-docker-sandboxing-landscape]] 未追蹤 lead
**標籤**: #talos #governance #policy-enforcement #runtime-security #credential-governance #mcp-tool-governance
**延續自**: [[2026-05-17-docker-sandboxing-landscape]]

## Per-Source Insights

### 1. Docker AI Governance Product (docker.com, May 12, 2026)

- **定位**：Centralized control plane over agent execution。四控制面：network、filesystem、credentials、MCP tools。
- **核心理念**：Governance at the runtime layer, not as advisory rules。Agent 有兩條作惡路徑：執行 code（sandbox 擋）＋ 呼叫 MCP tool（MCP Gateway 擋）。兩條路都守住才算治理。
- **Runtime-level enforcement**：policy 定義一次 → 自動傳播到所有執行節點（laptop → CI → production）。同一個 sandbox primitive 在所有環境一致運作。
- **Credential governance**：Agent session 只能看到被授權的 credential，scope 限 session 生命週期，block exfiltration 到未批准目的地。
- **MCP tool governance**：組織層級 managed policy，未批准 MCP server 預設 blocked。每 call 經 policy engine 檢查。
- **Role-based policy**：SAML/SCIM 整合，team-specific rules 疊加在 org-wide guardrails 上。
- **Audit trail**：Structured event（user identity、timestamp、session context、triggered rule）→ 直接 export 到 SIEM。
- **Availability**：GA now，enterprise sales channel。

### 2. Forbes/Yahoo Analysis (Janakiram MSV, May 14, 2026)

- **MCP adoption context**：產業分析指 MCP 在 production AI 團隊中 adoption 已達 ~78%，public registry 有 9,400+ servers。每個 MCP endpoint 都是 agent 可以呼叫的 tool。
- **競爭格局**：Docker vs Bifrost、Cloudflare AI Gateway、Kong、Azure API Management。Docker 的結構性優勢：runtime 層到處都是（laptop + CI + cloud），endpoint 工具做不到。
- **Hyperscaler 威脅**：AWS/Google/Microsoft 在建自己的 agent registries + governance layers 綁 identity + compute。Docker 賭 runtime 層會贏。
- **CXO 三問**：Agent 上一小時碰了什麼？用了什麼 credential？資料去了哪裡？多數 CISO 答不出。
- **對 Talos 有意義的 framing**：Laptop = new production。Agent = new workload。Runtime = new control plane。

## Hermes 啟發

### Talos Governance Phase 2-3 的 Concrete Reference

目前 Talos governance 藍圖（從 Docker Agent YAML Schema 筆記）：
```
Phase 1: Ad-hoc auditing (heartbeat EVOLVE) — ✅
Phase 2: Policy definition (guardian_policy.yaml)
Phase 3: Enforcement (tool call policy check)
Phase 4: Lifecycle supervision
Phase 5: Credentialless exploration
```

Docker AI Governance 給 Phase 2-3 提供了 runtime-level 的 reference implementation：

| Dimension | Docker AI Governance | Talos 對應 |
|---|---|---|
| Policy definition | Admin console → YAML rules | `guardian_policy.yaml` |
| Enforcement layer | Sandbox + MCP Gateway | Tool gateway mediation |
| Credential control | Session-scoped, exfiltration blocked | `secret-leak-prevention` → upgrade to hook-based |
| MCP tool governance | Org-wide allow/block lists | WS-009 tool scoping (L1) + gateway mediation (L2) |
| Audit | Structured events → SIEM | heartbeat EVOLVE + structured tool call log |
| Policy propagation | Auto-pull on auth | `guardian_policy.yaml` at known path, read on session start |

### 關鍵架構決策：Runtime vs Advisory

Docker 的核心洞察：**policy 必須在 runtime 層執行，不能是 advisory**。對 Talos 的意義：

- ❌ 錯誤做法：在 system prompt 加「請不要做危險操作」→ 可以被繞過
- ✅ 正確做法：在 tool gateway 層攔截 → `pre_tool_use` 等級的 enforcement
- 這對應 Docker Agent 的 `hooks` 機制（`pre_tool_use` event → policy check → allow/deny）

### Credential Governance 是 Hermes 的 Blind Spot

Docker 的三個 credential 控制維度：
1. **Visibility control**：Agent session 只能看到被授權的 credential
2. **Lifecycle scoping**：Credential 只在 session 期間有效
3. **Exfiltration prevention**：Block credential 外洩到未批准目的地

Hermes 現狀：
- `secret-leak-prevention` skill 只做 post-hoc regex scan（tool output 層）
- 沒有 `pre_tool_use` 層的參數掃描
- 沒有 `before_llm_call` 層的訊息掃描
- Credential 在 agent 的 system prompt 或 tool call 參數中可能被洩漏

### MCP Tool Governance 是下一個戰場

MCP adoption 78% → 9,400+ public servers → 每個都是潛在攻擊面。Docker 的做法：org-wide managed policy → unapproved servers blocked by default。

Hermes 現狀：
- WS-009 提供 tool scoping（探索模式限制 tool set）
- `enabled_toolsets` 在 cron job config 中
- 但沒有 per-session、per-agent 的 MCP tool approval workflow

### 競爭格局對 Hermes 的啟發

Docker vs hyperscalers 的 runtime-vs-catalog 之爭對 Hermes 無直接影響（Hermes 是 single-user/host），但架構原則是共通的：
- **控制應該在最接近執行點的地方**：對 Hermes 來說就是 tool gateway 層
- **Policy 不應該只存在一個地方**：laptop/CI/production 的一致性對 Hermes 不適用，但 Hestia/Talos 之間的 policy 一致性適用

## 未追蹤

- Docker Captain: Comparing Different Approaches to Sandboxing (May 2026) — containers vs microVMs 深度比較（也是 [[2026-05-17-docker-sandboxing-landscape]] 的 lead）
- Bifrost MCP Gateway — in-VPC deployments, air-gapped 環境；對 Hermes 的 local-only MCP gateway 設計有參考
- Cloudflare AI Gateway — edge network MCP gateway；與 Docker 的 laptop 覆蓋範圍比較
- Docker AI Governance 的具體 YAML policy schema（實際 admin console 產出的 policy 格式）

## ✅ 本次探索完成

