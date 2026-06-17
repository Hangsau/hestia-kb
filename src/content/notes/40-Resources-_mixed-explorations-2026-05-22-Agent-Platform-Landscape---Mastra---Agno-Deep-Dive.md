---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Agent-Platform-Landscape---Mastra---Agno-Deep-Dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Agent-Platform-Landscape---Mastra---Agno-Deep-Dive.md
title: Agent Platform Landscape — Mastra × Agno Deep Dive
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agno
- context
- hermes
- human
- layer
- mastra
- mcp
- memory
- observational
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# Agent Platform Landscape — Mastra × Agno Deep Dive

**延續自**: [[2026-05-21-MemR3---Memory-Retrieval-via-Reflective-Reasoning---2026-05-21]]  [[2026-05-21-2026-05-21-memori-atlas-long-term-memory-deep-dive]]

**時間**: 2026-05-22T04:30 CST

## 核心發現：TypeScript 框架 vs Python SDK 的不同抽象層

Mastra（JS/TS）和 Agno（Python）代表 agent platform 的兩個截然不同的設計方向。

### Mastra — Web-first TypeScript Agent Framework

**定位**：YC W25 batch，從 Gatsby 生態延伸出來。目標是讓 AI agent 和現有 web stack 無縫整合。

**記憶層架構**：
- Conversation history（標準）
- Semantic recall（RAG-style）
- Working memory（短期）
- **Observational memory**（離散事實萃取，非摘要）— 這個在 05-14 筆記已標過，是 Hermes 缺的層級

**Human-in-the-loop**：Suspend + resume，可用 storage 持久化執行狀態，適合長任務中斷。→ 對應 Hermes OTP/human-approval 提案的實作參考。

**MCP 整合**：原生的 MCP server authoring，expose agents/tools 為 MCP interface。這和 WS-024 的 MCP 工具化方向一致。

**Licensing 警訊**：Dual license——核心 Apache 2.0，但 `ee/` 目錄是 Enterprise license（source-available but not production-ready without license）。對 Hermes 的意義：如果要用 Mastra 的 enterprise features，需確認法律兼容性。

### Agno — Python Agent Platform SDK

**定位**：直接標榜「5000x faster than LangGraph, 50x less memory」。這是 aggressive marketing，但架構本身值得看。

**核心主張**：
- 6-layer context grounding（Dash tutorial: grounding answers in 6 layers）
- 100+ integrations，50+ API endpoints
- 內建 RBAC、multi-tenant isolation、OpenTelemetry tracing
- "Auto-improving agent platform managed entirely by Claude Code"（starter tutorial）

**Context Providers**：Slack, Drive, wikis, MCP, custom sources — 這是 Agno 的核心差異化：讓 agent 從多個 live source 取 context，而非只是 RAG。

**Storage 层**：Sessions, memory, knowledge, traces 全存自己的 DB——不依賴外部 vector DB。這讓 storage 成為 first-class citizen。

**Telemetry 注意**：預設開 telemetry（`AGNO_TELEMETRY=false` 可關）——部署前需了解資料去哪裡。

### 交叉分析：Mastra vs Agno vs Hermes

|| Mastra | Agno | Hermes（目前）|
|---|---|---|---|
| **語言** | TypeScript | Python | Python |
| **記憶類型** | 4層（conv/semantic/working/observational）| 6-layer grounding | 3層（summary/episodic/FTS5）|
| **Observational** | ✅ 原生 | 未標 | ❌ 缺 |
| **MCP** | ✅ 原生 | ✅ 原生（MCP tool）| 實驗中（WS-024）|
| **Human-in-loop** | ✅ suspend/resume | ✅ human-approval | OTP 提案 |
| **Storage 持久化** | ✅ 有限 | ✅ 全域 | ❌ 限 session |
| **Licensing** | Apache 2.0 + Enterprise | MIT（從 README 推）| N/A |

### 對 Hermes 的具體應用

**1. Observational Memory 是明顯缺口**
Mastra 的離散事實萃取（"user prefers dark mode", "last deploy failed"）比 summary 更精準。Hermes 目前缺這個層級。實作方向：
- 在 `heartbeat/snapshot.py` 加一個 `_extract_observations()` step
- 從最近的 action log entries 萃取 key facts（`result: ERROR` → 觀測到某個 action type 失敗率高）
- 存到 `observations/` 目錄，比 episodic 細但比 summary 輕

**2. Agno 的 6-layer context 可借鑒架構**
Agno 的 Dash agent 用 6 layers grounding——類似的思路可以引入 comms reliability 評估：
- Layer 1: active session count（目前有）
- Layer 2: recent error fingerprints
- Layer 3: pending inbox messages
- Layer 4: artifact staleness（heartbeat_state.json timestamp）
- Layer 5: vault sync divergence
- Layer 6: system map drift
→ 把 heartbeat 的 snapshot result format 從 flat dict 改成 hierarchical layers

**3. Mastra suspend/resume 是 OTP 提案的參考實作**
Mastra 的 human-in-the-loop 用 storage 持久化狀態 + indefinite pause。Hermes OTP 提案（MCP relay）可以借鑒：讓 agent 在需要 human approval 時「凍結」在 await state，而不是 timeout 或放棄。

## 未追蹤 Leads

- `https://mastra.ai/docs/memory/observational-memory` — Mastra 離散事實萃取的完整文件
- `https://docs.agno.com/runtime/context` — Agno context providers 的實作細節
- LangGraph MemR3 implementation — GitHub 找找有沒有參考實現

## ✅ 本次探索完成

**Token cost**: 極低（2個 README direct fetch，無需 sanitize）
**品質**: 中—框架文件資訊密度高但缺少底層演算法細節
**價值**: 確認 Observational Memory 缺口、Agno 6-layer 可借鑒、OTP suspend 模式有參考
