---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0900-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0900-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: medium
title: 四控制面完成揭示：Namespace 特化才是 Enforcement Model 選擇的真正變數
updated: '2026-06-15'
type: research
status: budding
---

# 四控制面完成揭示：Namespace 特化才是 Enforcement Model 選擇的真正變數

**消化筆記**: 2026-05-17-docker-mcp-tool-governance

MCP Tool Governance 筆記補完了 Docker 四控制面的完整地圖。結合 credential injection proxy 筆記的發現，浮現一個之前未明確說出的原則。

---

## Cross-Cutting Theme 1: Enforcement Model 的選擇變數是 namespace 連續性，不是控制面數量

**支援筆記**: 2026-05-17-docker-credential-governance-injection-proxy, 2026-05-17-docker-mcp-tool-governance, 2026-05-17-docker-governance-policy-schema（Network/Filesystem 的 delegation + wildcard 確認）

兩篇筆記湊在一起可以畫出一個二維矩陣：

| | **連續/無邊界 namespace** | **離散/封閉 namespace** |
|---|---|---|
| **需要 wildcard** | Network (`*.example.com`)、Filesystem (`**` 路徑) | — |
| **不需要 wildcard** | — | Credential (service names)、MCP Tool (server names) |
| ** Enforcement Model** | Allow/Deny rules + delegation | Approval catalog 或 Injection proxy |

為什麼 Credential 用 injection proxy 而非 allow/deny？因為 credential namespace 是**離散的 service name → key mapping**（`anthropic`、`aws`、`github`），每一個新增的 service 需要 admin 明確註冊 keychain，不可能用 wildcard。「允許所有以 `a*` 開頭的 API key」沒有意義。

為什麼 MCP Tool 用 approval catalog 而非 allow/deny？因為 MCP server namespace 是離散的 named entities（伺服器 URL + capability），不是連續的 domain 空間。一個 server 要嘛在 catalog 裡，要嘛不在。「允許所有 `mcp.*.com` 的 server」違背了 curated catalog 的目的。

反過來：Network 為什麼不用 approval model？因為合法的 domain 集合是無邊界的（任何 public domain 都可能需要訪問），不可能維護一個「所有合法 domain」的 catalog。Filesystem 為什麼不用 injection proxy？因為路徑是樹狀結構，不是 service→key 的簡單映射。

**這個原則預測**：如果未來 Talos 引入第五個控制面， enforcement model 不是由「是新控制面」決定，而是由「新的 resource 的 namespace 是否離散、是否需要 wildcard」決定。

**可行動下一步**: 在 `talos-governance-pipeline-blueprint.md` 的 enforcement layer 章節，用 namespace 連續性替換「控制面數量」作為 enforcement model 選擇的判斷框架。先畫矩陣，再填入各控制面的具體 enforcement model。

---

## Cross-Cutting Theme 2: Talos 的 `enabled_toolsets` 是 approval model 的正確方向，但缺少兩層必備設施

**支援筆記**: 2026-05-17-docker-mcp-tool-governance（MCP Tool → approval catalog + default-deny + runtime enforcement 三合一）, 2026-05-17-docker-credential-governance-injection-proxy（credential governance 的完整三層棧：keychain → proxy → sentinel value）

MCP Tool governance 的完整 stack 是：
1. **Catalog**（300+ verified servers）= 可批准的 target 清單
2. **Approval decision**（admin 在 Admin Console approve）= 誰有權批准
3. **Default-deny**（未批准預設 block）= enforcement 方向
4. **Runtime gateway**（MCP Gateway 在 tool call 時檢查）= 執行點

Talos 的 `enabled_toolsets` 只有第 2 層（隱含的 approved list），缺少：
- **Catalog**：沒有 curated, verified toolset 清單作為批准的前提。`enabled_toolsets` 只是「目前啟用的」，不等於「經過安全審查的」。
- **Runtime enforcement**：`enabled_toolsets` 是 cron job 啟動時的開關，不是 runtime gateway 檢查。如果 agent 啟動後修改了 toolset 配置，沒有 enforcement point 攔截。

Credential governance 對此給了一個彌補的方向：即使有 catalog 和 approval，沒有 runtime proxy 也無法確保 agent 接觸不到 credential value。

**可行動下一步**: 
1. 在 `hermes-config` 中為 `enabled_toolsets` 加上 `catalog_ref` 欄位，每個 toolset 必須指向一個 verified catalog entry，否則視為「未分類」而非「已批准」。
2. 在 `gateway` layer 新增 toolset boundary check——不在 `enabled_toolsets` 的 tool call 直接返回 `ToolNotApproved` 錯誤，而非等到 cron job 下次執行才發現。
