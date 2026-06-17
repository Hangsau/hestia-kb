---
_slug: 40-Resources-_mixed-explorations-2026-05-23-Moltis-vs-mcp-agent---Rust-Agent-Server---MCP-Pattern-比較
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-Moltis-vs-mcp-agent---Rust-Agent-Server---MCP-Pattern-比較.md
title: Moltis vs mcp-agent — Rust Agent Server + MCP Pattern 比較
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- hermes
- hook
- mcp
- memory
- moltis
- patterns
- self
- server
- skill
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# Moltis vs mcp-agent — Rust Agent Server + MCP Pattern 比較

**延續自**: [[2026-05-18-Moltis-Hook-System---Skill-Self-Extension---完整深讀]]  [[2026-05-20-2026-05-20---mcp-agent-Agent-as-MCP-Server-深度解析]]

**日期**: 2026-05-23 | **來源**: HN Show HN (131pts, 52 comments) + mcp-agent GitHub README | **類型**: 主題延續

---

## Phase Context

- **Theme-Based Continuation**: Following Moltis leads from prior notes, now with fresh community feedback from HN

---

## Per-source Insight

### Source 1: Moltis — Show HN (131pts)

**文章**: [Show HN: Moltis – AI assistant with memory, tools, and self-extending skills](https://www.moltis.org) (131 pts, 52 comments)
**類型**: Open-source agent server

**核心定位**：Rust 寫的單一二進位，sandboxed by default，支援 20+ 即時通訊頻道（TG/Discord/Slack/WhatsApp/Teams...）。目標是真正的 personal agent server，不是 SaaS 產品。

**核心功能**：
- 全頻道覆蓋：TG、WhatsApp、Discord、Slack、Matrix、Nostr、Teams、語音
- 記憶：persistent memory with vector + full-text search
- 排程：自然語言 cron jobs
- 安全：sandboxed，key 不離本機，Docker/Apple Containers 隔離
- 自延伸：runtime 建立自己的 skills、hooks、MCP tools

**社群討論亮點**：
- `theturtletalks` 問「有沒有 heartbeat 等價物？」→ Moltis 目前缺少主動驅動的能力（cron/heartbeat 模式），純響應式
- `vessenes`（OpenClaw 用戶）抱怨 compaction 吃掉太多 token， continuity 差 → Moltis 的 file-based memory 可能是解答
- `eibrahim` 問 self-created skills 的 trust boundary → Moltis 用 hook system 做 guardrails
- `ck_one` 對單一二進位執行有安全疑慮 → Moltis 的 sandboxing 是對應，但 binary trust 仍是問題

> **對 Hermes 的啟發**：Moltis 的「self-extending skills via hook system」與 Hermes 的 `skill_manage` 相似，但 Moltis 是 runtime self-modification（agent 自己創建 hook），Hermes 是離線 skill authoring。兩者互補——Moltis 的 hook guardrails 值得研究。

---

### Source 2: mcp-agent — GitHub (lastmile-ai, 80pts)

**文章**: [mcp-agent – Build effective agents with Model Context Protocol](https://github.com/lastmile-ai/mcp-agent)
**類型**: MCP framework

**核心定位**：用 MCP 作為唯一整合介面，實作 Anthropic "Building Effective Agents" 的所有 patterns（map-reduce、orchestrator、evaluator-optimizer、router），以 composable 方式串聯。

**三大支柱**：
1. **Full MCP support**：完整實作 MCP，包含 OAuth/Sampling/Elicitation 等進階功能
2. **Effective agent patterns**：以裝飾器（decorator）方式實作 workflow patterns
3. **Durable agents**：對接 Temporal，pause/resume/recover 無需改 API

**Agent-as-MCP-Server**：mcp-agent 可以把任何 agent 本身 expose 成 MCP server，讓其他 agent 透過 MCP 協議呼叫它。這是 Hermes 目前沒有的能力——Hermes 的 tool interface 是 flat list，沒有分層的 agent-as-tool 概念。

**Cloud deployment**：`mcp-c` 讓任何 app 部署為 MCP server，提供 managed agent runtime。

> **對 Hermes 的啟發**：mcp-agent 的「composable workflow patterns」與 Hermes 的 `subagent-driven-development` 相似，但 mcp-agent 用 MCP 協議實現 inter-agent communication，而不是 HTTP/WS。Hermes 的 `native-mcp` skill 可以考慮參考 mcp-agent 的 workflow pattern 實作方式。

---

## 跨文章 Synthesis

Moltis 和 mcp-agent 代表兩條不同的 agent 架構路徑：

| 維度 | Moltis | mcp-agent |
|------|--------|-----------|
| **語言** | Rust (single binary) | Python (uvx/pip) |
| **核心抽象** | Channel (TG/Discord/...) + Hook | MCP Protocol + Workflow patterns |
| **自延伸** | Runtime hook system | Skill authoring at design time |
| **安全模型** | Sandbox (Docker/Apple Containers) | MCP permissions |
| **通訊協議** | Proprietary channels | MCP (standardized) |
| **Heartbeat/主動性** | ❌ 純響應式 | ✅ Temporal durable execution |
| **目標用戶** | 個人/家庭 | 開發者/企業 |

**Hermes 的定位介於兩者之間**：
- 有 heartbeat 主動性（Moltis 沒有）
- 有 MCP 原生整合（mcp-agent 的核心）
- 但缺少「composable workflow patterns」（mcp-agent 的亮點）和「full-channel 覆蓋」（Moltis 的亮點）

**值得偷的兩點**：
1. **Moltis 的 file-based memory**：`eibrahim` 在 HN 說「file-based memory 比 vector DB 更容易 debug、更容易讓 agent reasoning、infrastructure overhead 更低」——這與 Hermes 的 L1 MEMORY.md → L2 memory-consolidator 架構方向一致，不需要引入 vector DB。
2. **mcp-agent 的 agent-as-MCP-server**：把 Herme 作為 agent expose 成 MCP server，讓其他工具/agent 透過 MCP 呼叫，會是 `native-mcp` skill 的自然延伸。

---

## ⏳ 未追蹤

- https://github.com/lastmile-ai/mcp-agent/tree/main/examples/temporal — Temporal durable execution 細節
- https://www.moltis.org/security — Moltis sandboxing 實作（fetch 失敗，需 retry）
- https://github.com/lastmile-ai/mcp-agent/blob/main/examples/mcp_agent_server — agent-as-MCP-server 實例

---

## ✅ 本次探索完成
