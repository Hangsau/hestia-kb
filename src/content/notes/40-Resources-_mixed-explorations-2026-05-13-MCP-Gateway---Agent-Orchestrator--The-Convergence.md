---
_slug: 40-Resources-_mixed-explorations-2026-05-13-MCP-Gateway---Agent-Orchestrator--The-Convergence
_vault_path: 40-Resources/_mixed/explorations/2026-05-13-MCP-Gateway---Agent-Orchestrator--The-Convergence.md
title: 'MCP Gateway × Agent Orchestrator: The Convergence'
date: 2026-05-13
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- archestra
- casdoor
- contextforge
- credential
- gateway
- hermes
- identity
- mcp
- orchestrator
created: '2026-05-13'
updated: '2026-06-15'
status: budding
---

# MCP Gateway × Agent Orchestrator: The Convergence

**Date**: 2026-05-13  
**延續自**: [[2026-05-13-mcp-gateway-architecture]], [[2026-05-13-agent-orchestrator-patterns]]  
**Source**: IBM/mcp-context-forge (3.7K ⭐), archestra-ai/archestra (3.7K ⭐), casdoor/casdoor (13.6K ⭐), ascending-llc/jarvis-registry (791 ⭐)  
**Theme**: 週三 — Multi-Agent Systems × MCP Infrastructure

---

## The Convergence Thesis

三個月前，「MCP Gateway」還只是 credential proxy。現在，三大 gateway 實作全部長出了 **orchestrator 功能**。Gateway 和 Orchestrator 正在合併成同一層 infrastructure。

## Landscape

| Project | Stars | Stack | Identity |
|---------|-------|-------|----------|
| Casdoor | 13.6K | Go | IAM-first agent gateway，重點在 auth/identity |
| IBM ContextForge | 3.7K | Python | 純 gateway：federation + protocol translation + observability |
| Archestra | 3.7K | TypeScript | Gateway + orchestrator + security + cost，最完整的 platform |
| jarvis-registry | 791 | Python | Enterprise MCP + Agent gateway，強調 single secure endpoint |
| Azure AI Gateway | 918 | Jupyter | Microsoft 的 reference implementation，Azure-native |

## 三個層次的收斂

### 1. Protocol Federation（ContextForge 強項）
Gateway 不只是 forward MCP — 它把 REST、gRPC、A2A 全部轉成 MCP 對外暴露。這是「向下統一」：讓 agent 只需要講 MCP，gateway 幫它翻譯各種後端。

### 2. Agent Lifecycle Management（Archestra 強項）
不只 forward tool calls，還管理 agent 的執行：K8s pod per agent、OAuth lifecycle、cost tracking、observability。這是「向上管理」：gateway 變成 agent 的 runtime。

### 3. Security as Platform Feature（共通）
所有 gateway 都內建：
- **Credential vaulting** — API keys 不散落在 agent config 裡
- **Audit trails** — 追蹤哪個 agent 何時調了哪個 tool
- **Rate limiting / cost control** — 不讓 agent 無限燒錢
- **Prompt injection defense**（Archestra 的 Dual-LLM 最激進）— 用第二個 LLM 審查 tool response，防止 data exfiltration

## Why This Matters for Hermes

### Hermes 現在的位置
- 有一個 gateway（`hermes gateway run` — WebSocket/HTTP transport）
- 有一個 MCP client（`native-mcp` skill）
- 有 agent orchestration pattern（`subagent-driven-development`, `kanban-orchestrator`）
- **但這三層是分開的** — gateway 不做 tool routing，orchestrator 不知道 MCP，MCP client 是 per-session

### 三個可能的演化方向

**A. Hermes 自己長成 Gateway+Orchestrator**
- 把 `hermes gateway` 擴充成能做 MCP proxy + registry
- 把 `delegate_task` 的 subagent 改走 gateway 而不是直接 call
- 優點：完全自主，不用外部依賴
- 缺點：重造輪子，ContextForge/Archestra 已經做得很完整

**B. Hermes 串外部 Gateway**
- Hermes 的 MCP servers 全部接到 ContextForge 或 Archestra
- Hermes 本身當成一個 agent client，透過 gateway 存取 tools
- 優點：借力成熟方案，拿到 observability/security 開箱即用
- 缺點：多一層 dependency，self-hosted 複雜度上升

**C. Hybrid — Gateway 在外，Orchestrator 在內**
- 用 ContextForge 處理 MCP federation + credential + observability
- Hermes 保留自己的 `delegate_task` / `kanban-orchestrator` 做 agent 排程
- 兩層各做各擅長的事
- 這可能是最務實的路徑

## Open Questions

1. **Hermes gateway 的現狀**：`hermes gateway run` 現在實際做了什麼？是不是只處理 WebSocket transport？需要看 code。（已標注，下次探索方向）

2. **ContextForge 的 Python 生態親和性**：它是 PyPI package，跟 Hermes 同語言。如果用 `uvx` 或 pip install，是不是可以當成 Hermes 的 sidecar？

3. **Archestra 的 CNCF 會員**：加入 Linux Foundation/CNCF 是為了標準化 MCP gateway 規格。如果 MCP gateway 有標準 spec，Hermes 應該直接實作 spec 而不是自已發明。

4. **Casdoor 的 13.6K 星**：IAM-focused gateway 有最高的星數，暗示 auth/identity 是這個市場最痛的點。Hermes 的 multi-provider auth 目前是 per-config 管理 — 有沒有 gateway-level 的 credential 管理需求？

## Worth Tracking

- **ContextForge** — Python, 同 stack，最可能整合。7K+ tests，serious engineering。
- **Archestra** — 規格制定者（CNCF），定義了「MCP platform」該長什麼樣子。即使不用它，也該參考它的 design。
- **Casdoor** — auth/identity 層的 reference。如果 Hermes 要做 multi-user，這是必看。
- **MCP Gateway 標準化** — 如果 CNCF 出 spec，Hermes 的 gateway 應該優先實作那個 spec。

