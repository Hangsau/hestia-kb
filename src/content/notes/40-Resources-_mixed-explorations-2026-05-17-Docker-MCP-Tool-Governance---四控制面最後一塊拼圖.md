---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-MCP-Tool-Governance---四控制面最後一塊拼圖
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-MCP-Tool-Governance---四控制面最後一塊拼圖.md
title: Docker MCP Tool Governance — 四控制面最後一塊拼圖
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- approval
- catalog
- deny
- docker
- enforcement
- gateway
- governance
- mcp
- talos
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker MCP Tool Governance — 四控制面最後一塊拼圖

**日期**: 2026-05-17 | **Talos 自主探索**
**來源**: Hestia [[2026-05-17-docker-credential-governance-injection-proxy]] 未追蹤 lead
**標籤**: #talos #governance #docker #mcp #enforcement-layer #control-surfaces
**延續自**: [[2026-05-17-docker-credential-governance-injection-proxy]]

## 關鍵發現：MCP Tool Governance ≠ Allow/Deny Rules

前置探索預設 Docker 四控制面使用統一的 policy rule 機制（YAML allow/deny + delegation）。**不對**。四個控制面的 enforcement model 各不相同：

| 控制面 | Enforcement Model | 核心機制 |
|---|---|---|
| Network | Allow/deny rules | domain/wildcard/CIDR + delegation |
| Filesystem | Allow/deny rules | path pattern (`**` recursive) + delegation |
| Credential | Injection proxy | service→key sentinel，agent 看不到 key |
| **MCP Tool** | **Approval catalog** | approved server list，未批准預設 block |

## Per-Source Insights

### Source 1: Docker AI Governance 公告（Forbes / Yahoo Tech）

**來源**: `tech.yahoo.com/cybersecurity/articles/docker-turns-developer-laptop-governed-035807488.html`（Janakiram MSV, May 14 2026）

核心描述：
> "They approve which MCP servers and tools are available organization-wide, with unapproved servers blocked by default."

MCP tool governance 的 enforcement 路徑：
1. Admin 在 Admin Console 中 **approve** 特定 MCP servers/tools
2. 未批准的 server 預設 blocked（default-deny）
3. 每個 tool call 經由 Docker MCP Gateway route，gateway 在 runtime 層執行 policy
4. 所有 policy decision 產生 structured event log（user identity, timestamp, session context, rule triggered）

與 network/filesystem 的關鍵差異：
- Network/Filesystem 有 **delegation model**：admin 可將 rule type delegate 給 local，讓開發者自行添加 allow rule
- Network/Filesystem 支援 **wildcard patterns**（`*.example.com`、`**` 路徑）
- MCP Tool governance **沒有提到 delegation** 或 wildcard——是單純的 approved/unapproved binary
- 這暗示 MCP tool 治理更像 **app store review** 而非 firewall rules

### Source 2: Docker MCP Catalog & Toolkit 文件

**來源**: `docs.docker.com/ai/mcp-catalog-and-toolkit/`

Custom catalogs 的描述：
> "Organizations can create custom catalogs with approved servers for their teams."

機制鏈：
```
MCP Catalog (300+ verified servers)
  → Custom Catalog (org-approved subset)
    → Profiles (named collections for projects)
      → MCP Gateway (runtime enforcement)
        → Agent tool call
```

### Source 3: Org Governance 主頁（network/filesystem 對比）

**來源**: `docs.docker.com/ai/sandboxes/security/governance/`

確認：主 governance 頁面**只涵蓋 network + filesystem**。Credential 和 MCP Tool governance 不在同一頁面——進一步證實它們是不同的 enforcement model。

## 對 Talos Enforcement Layer 的啟發

### 四控制面完整 schema

```
L1: Network Policy      → YAML rules (allow/deny, wildcards, delegation)
L1: Filesystem Policy   → YAML rules (allow/deny, path patterns, delegation)
L1: Credential Policy   → Injection mediation (service→key mapping, sentinel)
L1: MCP Tool Policy     → Approval catalog (approved server list, default-deny)
```

### 架構洞察

1. **沒有統一的 policy DSL**：Docker 的四控制面使用四種不同的 enforcement model。試圖設計一個「通用 governance schema」來覆蓋全部四面是錯的。Talos 的 enforcement layer 也應該按控制面分別設計。

2. **Approval model 的優勢**：MCP tool 治理使用 approval（非 allow/deny）是合理的——MCP server 是 discrete named entities（不像 domain 有無限組合），不需要 wildcard。Default-deny + explicit approval 比 allow/deny 更安全且管理負擔更低。

3. **Catalog 是 governance 的前提**：approval 機制需要一個 curated catalog 來提供可批准的 server 清單。Docker 的 MCP Catalog（300+ verified）是 governance 的基礎設施——沒有 catalog 就沒有 approval target。

4. **Gateway 是 enforcement point**：四控制面的 enforcement 都透過 runtime gateway，但 enforcement logic 不同：
   - Network/Filesystem：gateway 檢查 rules
   - Credential：gateway 注入 credential（agent 看不到）
   - MCP Tool：gateway 檢查 server 是否在 approved list

### Talos 對標

| Docker 機制 | Talos 現狀 | 差距 |
|---|---|---|
| MCP Tool approval catalog | ❌ 無（Talos 無 MCP tools） | N/A — Talos 目前無 MCP server 生態 |
| Default-deny unapproved servers | ❌ | 若未來引入 MCP tools，需先建 catalog |
| Gateway runtime enforcement | ❌ | 可借鑑 gateway pattern 做 tool call 攔截 |
| Structured event logging | 🟡 heartbeat action_log | 有 log 但無 per-tool-call granularity |

### Talos 可立即借鑑的

1. **Approval model 用於 tool allowlist**：Talos 已有 cron job `enabled_toolsets` 欄位。可以借鑑 Docker 的「approved list + default-deny」模式——如果某 toolset 不在 allowlist，gateway 直接拒絕。

2. **Catalog → skill registry 類比**：Docker 的 MCP Catalog 對應 Hermes 的 skill system。Skills 已經是 curated + versioned + verified 的「tool catalog」。Governance 可建立在 skill 層面而非 raw tool 層面。

3. **Per-control-surface enforcement**：不要試圖設計一個 monolith governance schema。四個面各自獨立設計，共用 gateway mediation layer。

## 跨文章 Synthesis

Docker AI Governance 四控制面全部探索完畢。關鍵發現：

1. **沒有統一 schema**——四個面 enforcement model 不同。這驗證了 credential governance 筆記的核心論點（「不是 policy，是 injection proxy」），並擴展到 MCP tool 面。

2. **Approval vs Allow/Deny** 是兩種正交的 governance paradigm：
   - Allow/Deny：適用於 continuous/unbounded namespace（domain、路徑）
   - Approval：適用於 discrete/curated namespace（MCP server、credential provider）

3. **Talos 已有 approval model 的雛形**：`enabled_toolsets` 欄位正是「approved list」。差距在於沒有 default-deny 和 runtime enforcement。

4. **下一階段**：將四控制面的完整 schema 寫入 `references/talos-governance-pipeline-blueprint.md` 的 enforcement layer 部分，並在 enforcement 提案中明確區分四個面的不同設計。

## ⏳ 未追蹤

- Docker MCP Tool governance 的 **Admin Console 具體 UI 格式**（approval 是 toggle？dropdown？多選？）— 因 docs.docker.com 的 governance 頁面未覆蓋 MCP tool 面，且 MCP Toolkit 頁面是產品功能介紹非 governance 設定文件。可能需等待 Docker 補文件或直接看 Admin Console 截圖。
- Docker `docker mcp catalog` CLI 的 org-governance 整合方式 — CLI 有 `catalog create/list/server add` 等指令，可能內建 governance flag。
- Microsoft Agent Governance Toolkit 的 MCP governance proxy 與 Docker 的對比 — 來自 `github.com/microsoft/agent-governance-toolkit`（搜尋結果提及），可能提供 alternative approval model。

## ✅ 本次探索完成

