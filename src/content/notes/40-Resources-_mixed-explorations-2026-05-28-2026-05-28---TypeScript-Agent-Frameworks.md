---
_slug: 40-Resources-_mixed-explorations-2026-05-28-2026-05-28---TypeScript-Agent-Frameworks
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-2026-05-28---TypeScript-Agent-Frameworks.md
title: 2026-05-28 — TypeScript Agent Frameworks
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agentkit
- based
- hermes
- loop
- mcp
- router
- routing
- state
- typedai
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 2026-05-28 — TypeScript Agent Frameworks

**延續自**: 無既有筆記

## Per-Source Insights

### 1. AgentKit (inngest/agent-kit) — 880 ⭐

JavaScript/TypeScript 多 agent 網路框架，強調**確定性路由 + MCP 豐富工具**。

**核心設計**：
- **State-based routing**：共享狀態（KV store）驅動路由決策，Router 函數可以讀寫網路狀態，根據狀態更新決定下一步 agent
- **兩種路由模式**：
  - Code-based routing（確定性）：Router 函數直接根據狀態 return agent
  - Agent-based routing（自主）：Routing Agent 自主決策，但保留 `onRoute` lifecycle callback 保持控制
- **Network = Agents + State + Router**：三元素組合，State 是雙向讀寫（agent tools 寫入，router/其他 agent 讀取）
- **MCP 一等公民**：`createMcpServer()` 直接整合 Smithery 等 MCP registry，Agent 可聲明多個 MCP server
- **fault-tolerant**：結合 Inngest  orchestration engine，agent 失敗不影響整體網路

**與 Hermes 對照**：
- Hermes 的 tool call routing 是由 LLM 隱式決定；AgentKit 的 router 是顯式函數，可讀狀態做條件分支
- AgentKit 的 Network ~= Hermes 的 multi-agent delegation，但 Hermes 沒有 shared KV state 機制
- MCP 整合模式：AgentKit 用 `transport: streamable-http` 聲明；Hermes 用 `mcp-server` cron config

**關鍵啟發**：
- State-based routing 是避免 LLM 盲目探索的有效機制——讓 router 根據已完成的事實（狀態）做決策，而非讓 LLM 自己決定下一步
- Lifecycle callbacks (`onRoute`) 提供干預點，不犧牲自治性的同時保留 human-in-the-loop

---

### 2. TypedAI (TrafficGuard/typedai) — 1.2k ⭐

HN title「Nous」實際是 TypedAI（TrafficGuard），一個 TypeScript-first 全功能 AI 平台。

**核心設計**：
- ** Autonomous agents**：記憶 + 函數調用歷史 + 迭代計劃 + 層次化任務分解
- **Software Developer Agents**：Code editing loop（detect → edit → compile → lint → test → fix）
- **SWE-bench style pipeline**：Code editing agent 含編譯錯誤分析，能線上搜尋、補檔案、裝 package
- **Human-in-the-loop**：預算控制、agent 發起的問題、錯誤處理
- **@func decorator 自動生成 function schema**：避免 zod/JSON 重複定義
- **OpenTelemetry observability**：所有 LLM 調用可追蹤
- **不依賴 LangChain**：自建完整棧（覆蓋 LangChain + LangSmith 功能）

**與 Hermes 對照**：
- SWE agent 的 compile→test→fix loop ~= Hermes 的 delegate_task + feedback cycle
- `@func` decorator 自動 schema ~= Hermes 的 tool registry，但更聲明式
- OpenTelemetry 整合是 Hermes 欠缺的（目前只有 basic logging）
- TypedAI 的 codebase awareness（index creation for file selection）~= session tree / context building

**關鍵啟發**：
- SWE agent 的「編譯錯誤驅動的自主修復」loop 是實際可工作的架構——Hermes 的 delegated subagent 若能加入編譯反饋，會更強
- OpenTelemetry observability 對 multi-agent 系統是剛需（Hermes 的 `errors.log` 不足以支撐 complex coordination debugging）

---

## 跨文章 Synthesis

兩者都指向同一個結論：**TypeScript 生態的 agent 框架正在複製 LangChain 的功能深度，但避開 LangChain 的抽象複雜度**。

| 維度 | LangChain | AgentKit | TypedAI |
|------|-----------|---------|---------|
| 路由模型 | Chain/Router 抽象 | State-based 明確函數 | Agent workflow |
| 工具集成 | 統一 Tool 介面 | MCP 一等公民 | @func decorator |
| 多 agent | 抽象 Chain | Network + State | 明確 agent 分工 |
| 可觀測性 | LangSmith（付費） | 内建 tracing | OpenTelemetry |
| 生態位置 | Python 為主 | JS/TS 生態 | JS/TS 生態 |

**對 Hermes 的啟發**：
1. State-based routing 機制（像 AgentKit 的 KV + Router）可作為 Hermes multi-agent coordination 的藍圖
2. OpenTelemetry 整合緊迫性提高——當 subagent 數量增加，basic logging 不够
3. `@func` decorator 模式是 Hermes tool registry 的可行簡化方向

---

## 未追蹤 Leads

- https://github.com/inngest/agent-kit/tree/main/examples/mcp-neon-agent (AgentKit MCP 範例)
- https://github.com/TrafficGuard/typedai/tree/main/examples (TypedAI 各類 agent 範例)
- https://github.com/inngest/agent-kit/blob/main/packages/agent-kit/src/router/router.ts (AgentKit router 實作)
- https://typedai.dev/ (官方文檔)

---

## ✅ 本次探索完成

*探索時間：2026-05-28 14:10 CST*
