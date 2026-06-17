---
_slug: 40-Resources-_mixed-explorations-2026-05-25-mcp-server-implementation-patterns
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-mcp-server-implementation-patterns.md
title: MCP Server Implementation Patterns
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# MCP Server Implementation Patterns

**日期**: 2026-05-25 | **主題**: Model Context Protocol 伺服器實作模式

## 來源

1. [MCP Official Introduction](https://modelcontextprotocol.io/introduction)
2. [MCP Server Concepts](https://modelcontextprotocol.io/docs/learn/server-concepts.md)
3. [Python SDK README](https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md)

## 核心概念

MCP 是「AI 應用的 USB-C」——開放標準，讓 AI 應用連接外部工具、資料、workflows。

### 三個 Building Blocks

| Feature | 控制方 | Protocol ops |
|---------|--------|--------------|
| **Tools** | Model | `tools/list`, `tools/call` |
| **Resources** | Application | `resources/list`, `resources/templates/list`, `resources/read` |
| **Prompts** | User | `prompts/list`, `prompts/get` |

**Tools** — LLM 主動呼叫，schema-based input/output（JSON Schema validation）。可用於寫資料庫、call APIs、改檔案、觸發 logic。強調 human oversight（consent dialogs, permission settings）。

**Resources** — 純讀取，URI-based（`file:///path/to/doc.md`），支援 resource templates（動態 URI 如 `weather://forecast/{city}/{date}`）。Application 決定如何處理讀到的資料。

**Prompts** — 預建模板，user 顯式呼叫，可帶參數。

### Python SDK Quickstart

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo", json_response=True)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"

# 傳輸：streamable-http / sse / stdio
mcp.run(transport="streamable-http")
```

**安裝**：`uv add "mcp[cli]"` 或 `pip install "mcp[cli]"`

### Transport 選項

- **stdio**: 適合 local、Claude Desktop integration
- **Streamable HTTP**: 適合 web deployment，可 Mount 到 ASGI server
- **SSE**: Server-Sent Events，適合 push-based updates

## 與 Hermes 的關聯

### ws-033: FTS5 vault_search as MCP Tool

MCP pattern 非常適合將 Hermes 的 vault search 暴露為 tool：
- `search_files()` 可以包裝成 `vault_search` tool，inputSchema 定義 query/limit/regex flags
- Transport 選擇 Streamable HTTP 適合 Hermes 的 server-client 架構
- 參考 `FastMCP` 的 `@mcp.tool()` decorator pattern

### OpenMemory MCP

兩個 repos（61★ 和 73★），可直接研究其 MCP server 實作模式作為參考。

### 安全性考量

MCP 文件有專門的 Security Best Practices 章節（SEP-1024 等），強調 local server 的 client security requirements。Hermes 若要實作 MCP gateway，需注意：
- OAuth 2.1 authorization
- User consent for tool execution
- Activity logs

## 未追蹤 Leads

- `https://modelcontextprotocol.io/docs/develop/build-server.md` — 建 server 完整指南
- `https://modelcontextprotocol.io/specification/latest` — 完整 spec
- OpenMemory MCP repos: 兩個 production MCP 實作可直接 study

## ✅ 本次探索完成