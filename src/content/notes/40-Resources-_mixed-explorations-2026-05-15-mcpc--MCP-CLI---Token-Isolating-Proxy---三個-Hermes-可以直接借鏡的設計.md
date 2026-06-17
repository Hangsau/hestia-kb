---
_slug: 40-Resources-_mixed-explorations-2026-05-15-mcpc--MCP-CLI---Token-Isolating-Proxy---三個-Hermes-可以直接借鏡的設計
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-mcpc--MCP-CLI---Token-Isolating-Proxy---三個-Hermes-可以直接借鏡的設計.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 12:\n    title: mcpc: MCP CLI × Token-Isolating Prox ... \n        \
  \       ^"
_raw_fm: '

  title: mcpc: MCP CLI × Token-Isolating Proxy — 三個 Hermes 可以直接借鏡的設計

  date: 2026-05-15

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, apify, cli, hermes, mcp, mcpc, proxy, server, token, tools]

  created: 2026-05-15

  updated: 2026-06-15

  status: active

  '
title: 'mcpc: MCP CLI × Token-Isolating Proxy — 三個 Hermes 可以直接借鏡的設計'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# mcpc: MCP CLI × Token-Isolating Proxy — 三個 Hermes 可以直接借鏡的設計

**日期**: 2026-05-15
**來源**: HN Algolia（延續自 [[2026-05-15-claws-agent-sandboxing]] 的未追蹤 lead）
**標籤**: #mcp #cli #security #proxy #tool-design #ws-009

**延續自**: [[2026-05-15-claws-agent-sandboxing]]、[[2026-05-15-agent-tool-simplicity]]

---

## mcpc: Apify 的 MCP CLI

**Repo**: [apify/mcpc](https://github.com/apify/mcp-cli) (590⭐, npm: `@apify/mcpc`)
**HN**: 50 pts, 5 comments | **作者**: Apify 團隊

mcpc 把 MCP 操作 mapping 成直覺的 CLI 指令：`mcpc @server tools-call search query:="hello"`。agent 只需要一個 `Bash()` tool，mcpc 處理所有 MCP 伺服器通訊。

```
  ┌──────────┐         Bash()         ┌──────────┐           MCP          ┌────────────┐
  │ AI agent │  ────────────────────► │   mcpc   │  ────────────────────► │ MCP server │
  └──────────┘                        └──────────┘    Sessions, OAuth,    └────────────┘
                                                      Tools, Resources,
                                                      Prompts, Tasks
```

這是 Doug Turnbull「笨工具」哲學的極致體現——不給 agent 50 個 MCP tools，只給一個 Bash + mcpc。

**競爭生態**（來自 mcpc README 的 comparison table）：

| Tool | Stars | Lang | 關鍵差異 |
|------|-------|------|---------|
| steipete/mcporter | 4.4k | TS | 最熱門，Hermes 已引用但無 skill |
| knowsuchagency/mcp2cli | 2.1k | Python | 支援 OpenAPI + TOON encoding（token 最佳化） |
| IBM/mcp-cli | 2.0k | Python | 內建 LLM 整合 |
| apify/mcpc | 590 | TS | **OAuth proxy**、sessions、x402 payments |
| f/mcptools | 1.6k | Go | Pure Go |

---

## 三個 Hermes 可以直接借鏡的設計

### 1. MCP Proxy：Token Isolation（→ WS-009 hijacking resilience）

mcpc 的 `--proxy` 是最有價值的功能：

```bash
mcpc login mcp.apify.com                          # 人類認證一次
mcpc connect mcp.apify.com @relay --proxy 8080     # 開 proxy session
mcpc connect localhost:8080 @sandboxed             # agent 透過 proxy 連線
# agent 永遠看不到原始 OAuth token
```

**安全模型**：
- 預設 bind `127.0.0.1`（無網路暴露）
- 原始 token/headers 永遠不傳給 proxy client
- 可選 bearer token 做第二層防護

**對 Hermes 的意義**：WS-009（hijacking resilience）的 OTP gate 和 micro-VM sandbox 之間，可以插入這個 token-isolating proxy 作為中間防禦層。不是取代 VM 隔離，而是讓「不需完整沙箱但想保護 credential」的情境有一個輕量方案。

具體場景：當 Hermes agent 需要呼叫第三方 MCP server（如 GitHub、Airtable），與其在 `config.yaml` 裡明文存 token 並直接 expose 給 agent，不如跑一個 local mcpc proxy——agent 只看到 proxy，永遠碰不到 token。

### 2. Progressive Tool Discovery（省 token）

mcpc 支援 `grep` 搜尋所有 active session 的 tools：

```bash
mcpc grep "search"      # 跨所有 MCP server 搜尋相關工具
mcpc @server grep "actor"
```

**對 Hermes 的意義**：Hermes 的 `native-mcp` 在 startup 時就把所有 tools 註冊進 tool registry。這對小型 MCP server 很合理，但如果有 10 個 server 各 20 個 tools，context 會被 200 個 tool schema 塞爆。Progressive discovery（「先用 grep 找出相關 tools，再看 schema」）是一個 token-efficient 的替代方案。與昨天 cost-security-convergence 筆記的 quadratic cache read 問題直接相關——tool schema 也是 context 的一部分。

### 3. Sessions as Named Entities（狀態管理）

mcpc 用 `@session_name` 管理多個 persistent connection：

```bash
mcpc connect mcp.apify.com @prod
mcpc connect mcp.apify.com @staging
mcpc @prod tools-call deploy
mcpc @staging tools-call deploy
```

**對 Hermes 的意義**：Hermes 的 `native-mcp` 用 server name 區分連線（`mcp_github_list_issues`），但沒有 session 層的概念——一個 server 只有一個連線。如果未來需要同一個 server 的多個 auth profile（如不同 GitHub org），mcpc 的 session model 是 cleaner 的 abstraction。

---

## 與 Hermes 現有架構的關係

Hermes MCP 架構現在有兩層：
- **native-mcp**：startup 註冊 MCP tools 為 first-class tools（thick interface）
- **terminal/bash**：agent 可以用 shell 直接跑 MCP CLI（thin interface）

mcpc 走的 thin interface 路線（agent 只用 Bash），和 Doug Turnbull 的「笨工具」論點一致。但 Hermes 的 hybrid approach（同時有兩層）其實是對的——不同場景需要不同 interface。

**mcporter**（4.4k⭐，生態最熱門的 MCP CLI）在 `native-mcp` SKILL.md 的 `related_skills` 裡被引用，但 Hermes 還沒有實際的 mcporter skill。可以考慮開一個 INSTALL 提案來試 mcporter 或 mcpc。

---

## 未追蹤但值得注意

- **mcporter** (steipete/mcporter, 4.4k⭐) — 最受歡迎的 MCP CLI，Hermes 已引用但尚未整合。值得開 INSTALL 提案。
- **mcp2cli** (knowsuchagency, 2.1k⭐) — Python，支援 OpenAPI + TOON encoding（據稱可省 60% token）。如果 Hermes 要自建 MCP CLI layer，TOON encoding 值得研究。
- **Code mode**（Anthropic 官方文章 + Cloudflare blog）— 「agent 寫 code 而不是直接 call tool」的模式。和 mcpc 的 `--json` + jq 管線是同一件事。值得另開探索。

