---
_slug: 40-Resources-_mixed-explorations-2026-05-14-ContextForge-SPIKE-實際可行性評估
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-ContextForge-SPIKE-實際可行性評估.md
title: ContextForge SPIKE：實際可行性評估
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- cache
- contextforge
- docker
- gateway
- hermes
- mcp
- python
- server
- skill
- uvx
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# ContextForge SPIKE：實際可行性評估

**Date**: 2026-05-14
**延續自**: [[2026-05-14-hermes-gateway-anatomy]]（open question #1）
**Source**: 實際嘗試安裝 + GitHub source code 解剖
**Theme**: Hermes internal — MCP gateway integration feasibility

---

## TL;DR

ContextForge **不能直接 pip install** 到 Hermes 環境（Python 3.14 不支援），但可以透過 **Docker sidecar** 跑。它不是 library 而是 standalone FastAPI 應用，整合路徑跟原先設想不同。

---

## 嘗試安裝的過程

```
pip install mcp-context-forge      → 404 (PyPI 名稱不同)
pip install mcp-contextforge-gateway → 找到但 Requires-Python <3.14
Hermes 環境: Python 3.14.4         → ❌ blocked
Docker: 有 GHCR image              → ❌ 這台機器沒裝 Docker/Podman
```

## 架構解剖（從 source code）

### 它不是 library，是 application

ContextForge 的 `mcpgateway/main.py` 是一個完整的 FastAPI 應用，不是你可以 `import mcpgateway` 的 library。整合路徑不是 Python import，是 **Docker sidecar**。

### 核心元件

| 層 | 檔案/目錄 | 做什麼 |
|---|---|---|
| Entry point | `main.py` | FastAPI app，MCP protocol handler（JSON-RPC, SSE, WebSocket） |
| MCP proxy | `reverse_proxy.py` | **關鍵**：把 local stdio MCP server 橋接到 remote gateway |
| Plugin system | `plugins/gateway_plugin_manager.py` | 40+ plugins，用 IBM 的 cpex framework |
| Auth | `auth.py`, `auth_context.py` | JWT + basic auth + RBAC + OAuth |
| Observability | `observability.py` | OpenTelemetry（Phoenix, Jaeger, Zipkin） |
| DB layer | 55+ Alembic migrations | SQLAlchemy + PostgreSQL |
| Admin UI | HTMX 2.0.3 + Alpine.js | Bundled，支援 airgapped deployment |
| Caching | `cache/` | Redis-backed, registry cache, session cache, tool lookup cache |

### 依賴樹

- FastAPI + uvicorn + gunicorn
- SQLAlchemy + Alembic + PostgreSQL
- Redis
- cpex（IBM plugin framework）
- httpx, orjson, jinja2, brotli, argon2-cffi
- 7,000+ tests

---

## 對 Hermes 的整合意義

### 原先的 Hybrid 設想（從 convergence 筆記）

```
AIAgent → native-mcp skill → ContextForge (MCP proxy) → MCP servers
```

假設 ContextForge 是 Python library，可以直接 import。

### 實際狀況

ContextForge 是 standalone server。整合模式是：

```
AIAgent → native-mcp skill → stdio MCP server
                                  ↕ (透過 reverse_proxy.py 橋接)
         ContextForge (Docker) ←─ MCP servers (REST/gRPC/A2A)
```

也就是說：ContextForge 不是取代 native-mcp skill，而是**坐在 MCP servers 前面當 reverse proxy**。

### 對 Hermes 的價值

1. **MCP federation** — 如果 Hermes 需要接多個 MCP server（不只 native-mcp 那幾個），ContextForge 可以統一管理
2. **Credential vaulting** — API keys 不散落在 Hermes config
3. **Observability** — OpenTelemetry tracing，追蹤 tool call 效能
4. **Rate limiting / cost control** — 防止 agent 無限燒錢
5. **REST/gRPC → MCP translation** — 把任意 API 變成 MCP tool

### 對 Hermes 不適用的部分

- **Agent lifecycle** — Hermes gateway 自己做了（cache, sessions, interrupts）
- **Messaging** — 17+ platform adapters 是 Hermes 自己的
- **Kanban/orchestrator** — Hermes 內建

---

## 反向思考：Hermes 需要 MCP gateway 嗎？

目前 Hermes 的 MCP servers 是 per-session 透過 `native-mcp` skill 直接 stdio connect：

```
每個 session → 獨立啟動 MCP server process → 直接 stdio 溝通
```

這個架構的問題：
1. 每個 session 重複啟動 MCP server（浪費資源，但有 prompt cache 所以還好）
2. 沒有 MCP tool registry（不知道哪些 tools 可用，靠 skill 定義）
3. 沒有 credential vault（API keys 在 skill config 裡）
4. 沒有 rate limiting（agent 可以無限調 tool）

**但實際上這些對 Hermes 的 single-user 場景都不是大問題。** ContextForge 的價值在 multi-tenant / enterprise 場景。

---

## Open Questions（更新）

1. ~~ContextForge 的 PyPI package 實際能用嗎？~~ → ❌ Python 3.14 blocker，需 Docker
2. **Docker 路徑值得試嗎？** → 如果這台機器有 Docker 的話。目前沒有。要不要裝 Docker 只為了試 ContextForge？ROI 不高。
3. **uvx 路徑？** — README 提到 `uvx --from mcp-contextforge-gateway mcpgateway`。uvx 應該會自動選相容的 Python 版本。如果裝 uv 的話可以繞過 Python 3.14 問題。值得一試，比裝 Docker 輕量。

---

## Worth Tracking（更新）

- ~~ContextForge integration feasibility~~ → ✅ evaluated。PyPI 路徑 blocked，Docker 路徑可行但缺 Docker，uvx 路徑未試。
- **uvx 方案**: `uvx --from mcp-contextforge-gateway mcpgateway` — uv 會自動管理 Python 版本，可能繞過 3.14 限制。不需要 Docker。
- **ContextForge 對 single-user Hermes 的邊際價值偏低**。核心功能（MCP federation, credential vaulting, rate limiting）在 multi-tenant 場景才發光。
- **但如果未來 Hermes 要做 multi-user**，ContextForge 跟 Casdoor 的組合（gateway + IAM）是 reference architecture。

