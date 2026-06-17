---
_slug: 40-Resources-_mixed-explorations-2026-05-14-lazy-tool--MCP-Prompt-Bloat-的本地解法
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-lazy-tool--MCP-Prompt-Bloat-的本地解法.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 17:\n    title: lazy-tool: MCP Prompt Bloat 的本地解法\n                \
  \    ^"
_raw_fm: '

  title: lazy-tool: MCP Prompt Bloat 的本地解法

  date: 2026-05-14

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [gateway, hermes, lazy, mcp, prompt, proxy, schema, search, tool, tools]

  created: 2026-05-14

  updated: 2026-06-15

  status: active

  '
title: 'lazy-tool: MCP Prompt Bloat 的本地解法'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# lazy-tool: MCP Prompt Bloat 的本地解法

**延續自**: [[2026-05-14-agent-cost-curve]], [[2026-05-14-hermes-gateway-anatomy]], [[2026-05-14-contextforge-spike]]

## 一句話

Single Go binary，用 "search before invoke" 模式解決 MCP tool schema 佔據 prompt context 的問題。數據：-46% input tokens, -32% latency。

## 核心設計

### 問題
連越多 MCP server → 每個 tool schema 都塞進 prompt → token 浪費 + 模型選錯 tool 的機率上升。這是 known problem。

### 解法
```
直接連 MCP server:         Agent 看到所有 tool schemas，call 任意 tool
透過 lazy-tool:            Agent 看到 5 個 meta-tools，search → find → invoke
```

5 個 meta-tools：
- `search_tools` — 用關鍵字找 tool
- `inspect_capability` — 看完整 schema
- `invoke_proxy_tool` — 實際呼叫（proxy 到 upstream）
- `get_proxy_prompt` — 讀 upstream prompt
- `read_proxy_resource` — 讀 upstream resource

### 三種模式
| 模式 | 適用場景 |
|------|---------|
| **Direct** (透明 proxy) | 小型/便宜模型 (Haiku, GPT-4.1-mini)，不會 multi-step reasoning |
| **Search** (default) | 強模型 + 大 tool catalog (50+ tools) |
| **Hybrid** | 漸進遷移或混合工作負載 |

### 架構亮點
- **本地 SQLite** 存 tool catalog，用 full-text search
- **Auto-import** IDE config：讀 Claude Desktop / Cursor / VS Code 的 MCP 設定
- **Provider-agnostic**：任何支援 MCP stdio/HTTP 的 client 都能用
- **可靠性內建**：circuit breaking, caching, session reuse, tracing
- **零依賴**：一個 Go binary，不用 Docker / vector DB / cloud

## 與現有方案的比較

| | lazy-tool | RAG-MCP | MetaMCP | AWS AgentCore | Claude built-in |
|---|---|---|---|---|---|
| 語言/平台 | Go binary | Python | Docker | Cloud | Client-side |
| 本地運行 | ✅ | ✅ | ✅ | ❌ | ✅ (Claude only) |
| Provider 無關 | ✅ | ❓ | ❓ | ❌ | ❌ |

## 與 Hermes 的關聯

### 接入點：Hermes Gateway (port 8811)

lazy-tool config 可以直接指向 Hermes Gateway：

```yaml
sources:
  - id: hermes-gateway
    type: gateway
    transport: http
    url: http://localhost:8811/mcp
```

→ lazy-tool 變成 gateway 前面的 tool search proxy，減少傳給 LLM 的 schema 量。

### 與 ContextForge 的關係

| | ContextForge (提案中) | lazy-tool (現成) |
|---|---|---|
| 方向 | 從 MCP server output 萃取 context | 減少 MCP tool schema 輸入 |
| 解決什麼 | 「tool 回傳太多東西」 | 「tool 定義太多，佔滿 prompt」 |
| 語言 | Python (較重) | Go (單 binary) |
| 互補性 | ✅ 不同問題，可共存 | ✅ |

**結論**：lazy-tool 處理 input side（tool schema bloat），ContextForge 處理 output side（tool result bloat）。兩者不衝突。

### 延伸想法

1. **CLI 整合**：Hermes Gateway 可以在 `hermes config set gateway.tool_search_proxy lazy-tool` 之類的方式選擇性啟用 lazy-tool 作為中間層
2. **成本估算**：Hermes Gateway 紀錄每個 request 的 tool schema token 數，交叉比對 lazy-tool 啟用前後的差異 → 量化效益
3. **Go 1.25+** 需求：目前 Ubuntu 24.04 的 Go 是 1.22，需要 install 新版

## 數據（宣稱）

llama-3.1-8b-instant, 47 tools, 20 repeats：
- Input tokens/turn: 1,701 → 915 (−46%)
- Latency/turn: 0.232s → 0.158s (−32%)

## 出處

- GitHub: https://github.com/mcp-shark/lazy-tool (org: mcp-shark, 原 rpgeeganage)
- HN: https://hn.algolia.com/?query=lazy-tool (23 points, 2026-03-31)
- Repo 狀態: 25 stars, 2 forks, 12 commits, MIT license
- 看起來是小團隊/個人專案，但設計思路紮實

## 待確認

- [ ] Go 1.25+ 在本地環境可行性
- [ ] 與 Hermes Gateway 的 stdio transport 相容性（它支援 HTTP，但 gateway 是 stdio mode）
- [ ] 實際測試 token 節省量（不是 benchmark 宣稱）
- [ ] SQLite FTS 搜尋品質對中文 tool description 的表現

