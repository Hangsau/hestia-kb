---
_slug: 40-Resources-_mixed-explorations-2026-05-13-MCP-跨工具記憶層---second-brain-cloudflare
_vault_path: 40-Resources/_mixed/explorations/2026-05-13-MCP-跨工具記憶層---second-brain-cloudflare.md
title: MCP 跨工具記憶層 — second-brain-cloudflare
date: 2026-05-13
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- brain
- cloudflare
- embedding
- hermes
- https
- mcp
- obsidian
- second
- session
- workers
created: '2026-05-13'
updated: '2026-06-15'
status: budding
---

# MCP 跨工具記憶層 — second-brain-cloudflare

**Source**: https://github.com/rahilp/second-brain-cloudflare (47⭐, MIT)
**Date**: 2026-05-13
**Theme**: 週二 MCP & Tool Use
**Confidence**: medium（只讀 README，未部署測試）

## Core Idea

一個跑在 Cloudflare Workers 免費層的 MCP server，提供跨 AI 工具的持久記憶層。任何 MCP-compatible client（Claude、Cursor、ChatGPT、Hermes）都能共用同一個記憶庫。

## 機制

- **儲存**：`remember` 寫入 D1 (SQLite) + Vectorize (384-dim embedding)
- **搜尋**：`recall` 用 bge-small-en-v1.5 做 cosine similarity 語義搜尋
- **去重**：寫入前自動檢測 near-duplicate，block 或 flag
- **分段**：長內容自動 split 成 overlapping chunks 再 embedding
- **追回**：`append` 更新既有條目而非複寫

五個 tools: `remember`, `append`, `recall`, `list_recent`, `forget`

## Why It Matters for Hermes

Hermes 已經有自己的記憶系統（session 搜尋、Obsidian vault、context distiller），但這些都是**單一 agent 內部**的。second-brain 解決的問題是：**你用多個 AI 工具時，它們彼此不知道對方知道什麼。**

如果 Hang 同時用 Hermes + Claude Desktop + Cursor，second-brain 可以當成一個共享的 long-term memory。Hermes 透過 native MCP client 接上去就能存取。

## 誠實的 Limitation

1. **Cloudflare 綁定** — 不是 fully self-hosted，依賴 Cloudflare 生態
2. **embedding 只用英文** — bge-small-en-v1.5，中文語義搜尋可能不太準
3. **沒有 auth 以外的 access control** — 所有人用同一個 token 看到全部記憶
4. **單一 Worker** — 不是分散式，大規模會爆
5. **對 Hermes 來說** — 我們已經有 Obsidian vault + session_search，這東西的邊際價值待驗證

## 如果真的要試

```bash
# Hermes 的 MCP config 加一筆：
# config.yaml → mcp_servers:
#   second-brain:
#     type: http
#     url: https://<worker>.<subdomain>.workers.dev/mcp
#     headers:
#       Authorization: Bearer <token>
```

但目前的 session_search + Obsidian 已經覆蓋大部分 use case。除非 Hang 明確說他要在多個 AI 工具間共享記憶，否則這個優先級不高。

