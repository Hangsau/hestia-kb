---
_slug: 40-Resources-_mixed-explorations-2026-05-22-MCP-OpenMemory---Concrete-MCP-Memory-Server-Reference
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-MCP-OpenMemory---Concrete-MCP-Memory-Server-Reference.md
title: MCP OpenMemory — Concrete MCP Memory Server Reference
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- context
- hermes
- mcp
- mem
- memory
- openmemory
- server
- sqlite
- tool
- tools
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# MCP OpenMemory — Concrete MCP Memory Server Reference

**延續自**: [[2026-05-29-mem0-ecai-deep-dive-hermes-integration]]

**時間**: 2026-05-29T04:45 CST

## 來源

- GitHub: baryhuang/mcp-openmemory (⭐73, JavaScript)
- npm: @peakmojo/mcp-openmemory
- License: MIT

---

## 核心發現：MCP Memory Server 最小可行實作品

### 工具設計（只有 4 個）

| Tool | 功能 |
|------|------|
| `save_memory` | 存單筆對話訊息 |
| `recall_memory_abstract` | 取當前摘要 |
| `update_memory_abstract` | 更新摘要 |
| `get_recent_memories` | 取近期對話歷史 |

極簡設計——每個 tool 對應一個核心需求，沒有過度工程。

### 儲存架構

```
SQLite (單一 .sqlite 檔)
├── messages table (原始對話)
├── abstracts table (摘要)
└── 透過 MEMORY_DB_PATH 配置路徑
```

明確警告：`MEMORY_DB_PATH` 必須指向**持久化位置**，否則預設 `./memory.sqlite` 會在 app 重啟時消失。

### Namespace 策略（兩種）

**硬隔離**：不同 app 用不同 DB 檔（Claude vs Cursor 各一個 `.sqlite`）
**軟隔離**：同一 DB，call tool 時傳 `context: "project-x"` 欄位

README 明確說：`🔍 Semantic search is not supported yet.` — 這是已知限制。

---

## Hermes 啟發

### 1. Hermes 能否作為 MCP Memory Server？

mcp-openmemory 是「外部 client（如 Claude Desktop）連入記憶系統」。Hermes 的情境相反：「Hermes 自己就是 agent，要向外暴露記憶能力」。

但實作品值得參考：
- **4-tool 介面設計**：Hermes 若要暴露 memory tools，可以考慮類似的最小工具集
- **SQLite 持久化**：Hermes 目前用 JSONL，這個實作品證明 SQLite 是可行選擇
- **Context namespace**：同一 DB 內的專案隔離模式，適用於 Hestia/Talos 各自記憶

### 2. Hermes-as-MCP-Server 的實作路徑

參考 `mcp-agent` skill 和 `native-mcp` skill，已知：
- Hermes 已有 `hermes_mcp_server.py`（`~/.hermes/scripts/`）
- FastMCP 可作為 framework
- 挑戰：Hermes 沒有「外部 client」的概念——Hermes 是用戶端，記憶在內部

更實際的應用：Hermes 用 MCP 工具連入**外部記憶 server**（如 mcp-openmemory），而不是自己 host 一個。

### 3. 與 Mem0 的對比

| | mcp-openmemory | Mem0 |
|--|---------------|------|
| 架構 | SQLite + npm | Redis/Pg + Python |
| 索引 | 無（全文搜）| 向量 + BM25 + entity |
| 摘要 | 使用者自己更新 | LLM 自動萃取 |
| Namespace | context 欄位 | user_id/session_id |
| 複雜度 | 極簡（4 tools）| 完整（3-layer）|

**互補**：mcp-openmemory 的簡單性適合小型場景；Mem0 適合 production。

---

## Cross-Article Synthesis

### 從 Mem0 到 OpenMemory：記憶系統的兩極

Mem0（ECAI 2025）是「最大化的記憶系統」：三層儲存、圖變體、LLM entity extraction、91% latency  reduction。

mcp-openmemory 是「最小化的記憶系統」：SQLite + 4 tools + 0 vector search + 使用者自管摘要。

兩者之間是連續光譜：

```
極簡              中等              完整
mcp-openmemory ← Mem0-G ← Mem0 ← 企業級向量 DB
(SQLite, 4 tools) (multi-signal)  ( Neo4j + Redis)
```

Hermes 的定位顯然在中間偏右——不需要 Mem0-G 的 entity graph，但也比 mcp-openmemory 的無索引要好。Phase tree navigation（WS-025）是屬於這個中間地帶的設計。

---

## Per-Source Insight

- **What**: Standalone MCP server that gives Claude persistent conversation memory via 4 simple tools (save/recall/update/get)
- **Architecture**: SQLite persistence, Node.js/npm, context-based namespacing, no semantic search
- **Key design**: Minimalism over completeness — explicit tradeoffs documented (no vector search, manual abstract updates)
- **Hermes relevance**: MCP server pattern for exposing memory; SQLite as storage alternative to JSONL; context namespacing for Hestia/Talos separation

---

## 未追蹤

- osent77/OpenMemory-MCP (⭐61) — repo returned empty from GitHub API, likely deleted/private. Skip.
- baryhuang/mcp-openmemory source code (GitHub API gave description only, not code structure) — could fetch `server.js` directly if deeper dive needed.

## ✅ 本次探索完成

