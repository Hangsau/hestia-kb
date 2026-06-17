---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-AI-Governance---AIUC-1-Q2-Changelog---守護者深度追蹤
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-AI-Governance---AIUC-1-Q2-Changelog---守護者深度追蹤.md
title: Docker AI Governance + AIUC-1 Q2 Changelog — 守護者深度追蹤
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- aiuc
- docker
- governance
- hermes
- mcp
- policy
- security
- talos
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker AI Governance + AIUC-1 Q2 Changelog — 守護者深度追蹤

**延續自**: [[2026-05-17-docker-multi-agent-sandbox-comparison]], [[2026-05-17-aiuc1-hermes-gap-analysis]]
**日期**: 2026-05-17 02:16 CST
**標籤**: #agent-governance #aiuc1 #mcp-security #compliance #credential-management #talos

## Per-Source Insights

### 1. Docker AI Governance: Unlock Agent Autonomy, Safely (May 12, 2026)

- **來源**: https://www.docker.com/blog/docker-ai-governance-unlock-agent-autonomy-safely/
- **作者**: Srini Sekaran (Docker)

**核心論點 — Two Paths Framework**：
Agent 造成傷害只有兩條路徑：
1. Agent 自己執行程式碼（碰檔案、開網路連線）
2. Agent 透過 MCP server 呼叫工具（操作外部系統）

Govern both paths → governed the agent。Miss either → haven't governed。

**Docker 的解法**：
- Path 1 → microVM sandbox（process-level enforcement，不是 advisory rules）
- Path 2 → MCP Gateway 作為 centralized chokepoint（authenticate, authorize, log every tool call）

**四個控制面**：
1. **Network & Filesystem**：allow/deny domains/IPs/CIDRs + mount rules (r/o or r/w)
2. **Credentials**：agent session 只能看到 scoped credentials，duration-limited，block exfiltration to unapproved destinations
3. **MCP Tools**：org-wide managed policies，unapproved servers blocked by default
4. **Role-based Policy**：SAML/SCIM integration，team-specific rules on top of org-wide guardrails

**關鍵設計原則**：
- Policy 必須在 runtime layer 強制執行，不能是 advisory
- 可攜性：同一 policy 在 laptop / CI runner / production cluster 都生效（因為底層都是 Docker runtime）
- 稽核：每次 policy evaluation 產生 structured event（user identity, timestamp, session context, triggered rule）

**Hermes 啟發**：
1. Two paths framework 是很好的 security 思維模型。Hermes 目前的 tool 層（terminal, write_file, process 等）對應 path 1；未來的 MCP gateway 對應 path 2。但缺少 centralized policy engine 把兩條路徑統一起來。
2. **Credential scoping 是 Hermes 的盲點**：terminal tool 繼承 host env vars，探索 agent 理論上可以讀到 API keys。Docker 的 "scoped to session duration" 是更安全的 model。WS-009 的 tool scoping 已處理部分問題，但 credential isolation 還沒被當成獨立控制面。
3. "Your laptop is the new prod" 這句話對單人 Hermes 也成立——只是 laptop = VPS。治理思維不應該因為規模小而省略。
4. Docker 的 governance 定位是 "定義一次，到處強制"——這和 Talos 作為統一守護者的角色一致，但 Talos 目前是 ad-hoc 檢查而非系統性 policy enforcement。

### 2. AIUC-1 Q2 2026 Changelog (April 15, 2026)

- **來源**: https://www.aiuc-1.com/changelog
- **更新範圍**: 14 requirements + 23 controls updated
- **下版**: July 15, 2026

**Q2 2026 三大主題**：
1. MCP & A2A protocol security（認證、傳輸安全、runtime containment、logging）
2. Third-party risk（E009 第三方監控改為強制）
3. Agent identity & access management（A003 拆分 agent identity 和 access management 為獨立 controls）

**與 Hermes/Talos 直接相關的 changes**：

| Control | Change | Hermes 對應 |
|---------|--------|------------|
| B006.3 執行層 containment | **新增**：限制 agent 或 approved MCP server 異常行為的 blast radius | WS-009 L3 microVM sandboxing 直接對標 |
| D003 限制不安全 tool call | **擴展**：從 approved functions 擴大到 MCP servers + 多步驟 workflow | Hermes tool scoping 需考慮 chained tool calls |
| D003.4 人類核准 workflow | **擴展**：從單一操作擴大到多步驟 workflow | 自主探索的 human-in-the-loop 缺失（WS-009 未涵蓋） |
| E015 系統活動 logging | **擴展**：從 model 層擴大到整個系統，包含 tool calls、sub-agent actions、provenance metadata | Heartbeat action log 已有雛形，但缺少 sub-agent 層的 traceability |
| E009 第三方監控 | **改強制** | 對 Hermes 不適用（單人 agent） |

**Pattern 觀察**：
- AIUC-1 正從 "API-level security" 轉向 "execution-level + protocol-level security"——這和 Docker AI Governance 的 runtime enforcement 方向完全一致
- MCP 被當作獨立的安全邊界（不只是一個 protocol），需要自己的認證/授權/稽核層
- Multi-step workflow 是新的風險面——agent chaining tool calls 比單一 call 更難審計

## 跨文章 Synthesis

**治理的收斂方向**：Docker AI Governance 和 AIUC-1 Q2 在兩個點上完全收斂：
1. **Runtime enforcement > advisory rules**：policy 必須在 agent 執行層強制，不能只是 prompt 裡的建議
2. **MCP 是獨立的信任邊界**：MCP server 不只是另一個 tool，它是 agent 通往外部系統的閘道，需要獨立的認證/授權/稽核

對 Hermes 的意義：
- WS-009 的 three-layer gradient（L1 tool scoping / L2 gateway mediation / L3 microVM）正好對標這兩個收斂方向
- L1 tool scoping → 對應 restrictive tool calls (D003)
- L2 gateway mediation → 對應 MCP tool governance（Docker）+ MCP protocol security（AIUC-1）
- L3 microVM → 對應 execution-level containment (B006.3)
- 但 Hermes 目前只有 L1 實作中，L2 在 spike 階段，L3 是設計構想

**Talos 的定位**：
- Docker AI Governance 的 centralized admin console → Talos 是 Hermes 的 centralized guardian
- 但 Talos 目前是 ad-hoc 檢查者而非 systematic policy enforcer
- 差距在於：Docker 的四個控制面（network/filesystem/credentials/MCP）有明確的 policy definition + enforcement + audit 三層；Talos 目前只有 audit（heartbeat EVOLVE），缺少 policy definition 和 enforcement

## 未追蹤

- Docker AI Governance 的技術細節（policy propagation mechanism、sandbox-to-gateway integration）— 現有文件只講 what，不講 how
- Docker MCP Gateway 的架構文件（`docs.docker.com` 上可能有更技術的文件）
- AIUC-1 Q3 2026 preview page（此 URL 404，可能尚未上線或已變更）— 可等 July 15 正式 release
- AIUC-1 GitHub side-by-side diff（changelog 提到但未給連結）— 了解 actual requirement wording changes
- Lovable 的 AIUC-1 合規實作細節（他們預定 Q2 2026 Schellman audit）— 第一個實際案例

## ✅ 本次探索完成

