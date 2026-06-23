---
_slug: 40-Resources-_mixed-explorations-2026-05-17-2026-05-17---AgentKit--Multi-Agent-Networks-in-TypeScript
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-2026-05-17---AgentKit--Multi-Agent-Networks-in-TypeScript.md
title: '2026-05-17 — AgentKit: Multi-Agent Networks in TypeScript'
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agentkit
- heartbeat
- hermes
- mcp
- network
- plan
- router
- routing
- state
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# 2026-05-17 — AgentKit: Multi-Agent Networks in TypeScript

**來源**: HN Show HN | https://github.com/inngest/agent-kit ⭐863

## Per-Source Insight

### AgentKit Architecture

TypeScript-first multi-agent SDK，核心概念：
- **Agents**: LLM call + prompt + tools + MCP servers
- **Networks**: 多個 agents 協作，共享 State，支援 handoff
- **State**: KV store，跨 agents 共享，是 routing 的基礎
- **Routers**: 兩種模式
  1. **Code-based routing**: 純 deterministic — router 函式 access `state.kv` 決定下一步用哪個 agent
  2. **Agent-based routing**: Routing 也是一個 agent，用 `onRoute` lifecycle callback 攔截決定

```tsx
// Code-based routing — 最有控制力
router: ({ network }) => {
  if (!network?.state.kv.has("code") || !network?.state.kv.has("plan")) {
    return codeAssistantAgent;
  } else {
    const plan = network?.state.kv.get("plan") as string[];
    const nextAgent = plan.pop();
    if (nextAgent) {
      network?.state.kv.set("plan", plan);
      return network?.agents.get(nextAgent);
    } else if (!network?.state.kv.has("summary")) {
      return summarizationAgent;
    }
  }
}
```

Router 的狀態傳遞靠 `network.state.kv`（key-value）+ agent 的 tools（副作用寫 state）。每個 agent 都是 pure function-style — 沒有共享內存，只有 state store。

**MCP native**: 直接在 agent 設定 `mcpServers`，支援 streamable-http transport。Smithery 整合實例：Neon database MCP server。

**Tracing built-in**: local + cloud tracing，Dev Server 在本地重放 agent 執行。

### 和 Hermes 的共鳴

Hermes 的 design 也有類似的問題：subagent 的狀態怎麼傳遞？目前靠 `workspace/INDEX.md` 和檔案系統。AgentKit 的 `network.state.kv` 是 in-memory 方案，對單行程式有效但不利於跨 session 持久化。

MCP native 這點和 Hermes 的 MCP gateway 方向一致 — 把工具抽象成 MCP server，而非 hardcode tool definitions。

## Hermes 啟發

- **Routing pattern**: Hermes 的 autonomous maintenance 選單（explore / review proposals / etc.）本質上也是一個 router，只是用 LLM 做而非 code-based。AgentKit 的 code-based routing 給了另一种思路：如果把 heartbeat 的 action pool 建模成 network state，router 可以根據心跳分數、系統溫度等條件 deterministic 決定 action，而不需要每次都叫 LLM
- **State persistence**: Hermes 跨 session 的狀態靠 `heartbeat_state.json`（Python 寫）和 `workspace/INDEX.md`（LLM 改）。AgentKit 的 `state.kv` 是每個 network run 內的。如果要讓 Hermes heartbeat action 也用類似設計，可以考慮把 `heartbeat_state.json` 建模成 network state 的一部分

## 跨文章 Synthesis

今天的探索：從 firn 三層重整（分工明確化）到 AgentKit（架構元件的具體實作）。兩個主題都指向同一個問題：**分散系統裡誰負責什麼？**

AgentKit 的答案是：router 負責，state 是共享介面。Hermes 的答案是：layered architecture + heartbeat scoring。但 Hermes 目前缺乏像 AgentKit 那樣的**明確 routing decision log** — `heartbeat_v2.py` 有 `decisions.json` 但沒有像 router trace 那樣的決策鏈（為什麼選了這 action？依據什麼 condition？）。

## 未追蹤
- UltraContext (21 pts): https://ultracontext.ai/ — context API for AI agents with auto-versioning
- AgentKit SWE-bench example: https://github.com/inngest/agent-kit/tree/main/examples/swebench
- Inngest Dev Server: local dev + cloud orchestration combo，值得了解

## ✅ 本次探索完成

