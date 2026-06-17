---
_slug: 40-Resources-_mixed-explorations-2026-05-27-pg-mcp-server-patterns
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-pg-mcp-server-patterns.md
title: 探索：pg-mcp — Postgres MCP Server 架構分析
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：pg-mcp — Postgres MCP Server 架構分析

**日期**: 2026-05-27 | **來源**: HN Search (167 pts, stuzero/pg-mcp-server)

## 核心洞察

pg-mcp 是 production-grade Postgres MCP server，539 stars，Python + FastMCP + asyncpg。從 Arcade.dev 的 tool design patterns 視角看，這是一個「資料庫作為 first-class MCP resource」的實作範本。

## 對 Hermes 的啟發

### 1. Connection ID 模式 — 不暴露 credential

pg-mcp 的核心設計：agent 拿到的不是 `postgresql://user:pass@host/db`，而是 opaque `conn_id`（UUID）。Credential 只在初始連線時傳一次，之後所有 operation 用 ID 引用。

**對應到 Hermes**：heartbeat/heartbeat_state.json 裡有 API key、provider token。Tool call 時不應把完整 credential 傳給每個 sub-tool，應該用 session-level credential store（類似 `conn_id` pattern）。這比每次 tool call 都傳完整 credential 更乾淨，也更安全。

**具體缺口**：目前 `heartbeat_v2.py` 的 `running_agents_count` 讀取、EVOLVE scoring 讀取的 state file 路徑是直接硬編碼，沒有「resource URI」抽象層。

### 2. Read-only enforcement at transaction level

pg-mcp 的 security design：`ALTER DATABASE SET default_transaction_read_only = true` — 安全不是靠 application logic 而是靠 DB transaction setting。這是「promised by the tool, guaranteed by the substrate」的最佳範例。

**對應到 Hermes**：目前的安全保證（`otp_gate.py` 的 HMAC、gateway 的 auth check）都靠 code enforcement。如果能將部分 invariant 提升到 infrastructure level（如 Linux sandbox、container isolation），安全性會大幅提升。

### 3. pgmcp:// URI scheme for resource discovery

pg-mcp 定義了 `pgmcp://{conn_id}/schemas/{schema}/tables` 這樣的 resource URI scheme。Agent 可以用 URI 探索資料庫結搆，不需要 tool call 即能 discover。

**對應到 Hermes**：目前 Hermes 的 exploration/heartbeat 狀態沒有 URI-based resource model。工具之間無法用 URI 互相引用狀態或資源。如果要讓多個工具組合使用（例：EVOLVE 讀 heartbeat_state.json → 觸發 snapshot → 寫入 vault），需要 resource URI abstraction。

### 4. Rich error messages for agent recovery

pg-mcp README 的 security 段落提到「error message doesn't leak connection details」。但從 Arcade.dev 的「Error-Guided Recovery」原則，error message 應該同時提供 recovery hint。

**對應到 Hermes**：目前 heartbeat error 的 error message 常常只是 `[critical×N]` 數字，沒有「what to do about it」。可以改進成：每次 error 包含 `suggested_action` field。

### 5. Extension context via YAML

pg-mcp 的 PostGIS/pgvector 知識是 YAML 設定檔的形式，不 hardcode。這讓新的 database extension 可以透過新增 YAML 而不需要改 code。

**對應到 Hermes**：目前 skill/library 的 tool descriptions 是 static string。如果改成 YAML 設定檔動態載入，新工具的描述可以在 runtime 註冊，不需要重啟。

## 架構映射

```
pg-mcp 層次           Hermes 對應
─────────────────────────────────────
conn_id (UUID)        session token / API key reference
pgmcp:// URI scheme   resource URI (未來)
transaction-level RO   infra-level sandbox
YAML extension ctx    skill registry (partially exists)
```

## 未追蹤 Leads
- https://github.com/stuzero/pg-mcp-server — 539 stars, Python, production-grade
- https://github.com/modelcontextprotocol/servers/tree/main/src/postgres — MCP 官方 Postgres 實作（pg-mcp 基於此擴展）

## ✅ 本次探索完成
