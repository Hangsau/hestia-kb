---
_slug: 40-Resources-_mixed-explorations-2026-05-27-CUGA-Agent---5-Layer-Runtime-Governance---Repo-Architecture
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-CUGA-Agent---5-Layer-Runtime-Governance---Repo-Architecture.md
title: CUGA Agent — 5-Layer Runtime Governance + Repo Architecture
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- cuga
- draft
- hermes
- layer
- mode
- policies
- skill
- supervisor
- tool
created: '2026-05-27'
updated: '2026-06-15'
status: budding
---

# CUGA Agent — 5-Layer Runtime Governance + Repo Architecture

**日期**: 2026-05-27 | **來源**: github.com/cuga-project/cuga-agent (742★, main branch) | **類型**: 研究筆記
**延續自**: [[2026-05-26-cuga-runtime-governance]]

---

## 核心：CUGA Policy System 的五層實作

### Layer 1 — Intent Guard（意圖守衛）
- **代碼位置**: `src/cuga/policies/intent_guard.py`（推测）
- **Trigger**: keyword + embedding similarity（threshold 0.65，from arXiv paper）
- **行為**: 立即終止執行，agent 完全看不見惡意/危險請求
- **優先級**: 90（最高，blocking > advisory）

### Layer 2 — Playbook（劇本注入）
- **位置**: system prompt 動態注入
- **功能**: step-by-step 指令引導 agent planning
- **關鍵設計**: 「精確指導而非膨脹 prompt」—— shaping 而非 blocking
- **CUGA 實作**: `settings.toml` 的 `[features] cuga_mode` 切換 reasoning mode

### Layer 3 — Tool Guide（工具指南）
- **觸發**: 在 tool description 執行前動態充實（附加 warning/context）
- **可疊加**: cumulative，session-scoped deep-copy
- **CUGA 實作**: `mcp_servers.yaml` + tool registry config

### Layer 4 — Tool Approval（工具審批）
- **位置**: code generation **之後**、實際執行**之前**
- **功能**: pause execution graph，等待 human-in-the-loop 確認
- **關鍵設計**: 脫離 agent reasoning loop，確保高風險操作有獨立把關
- **配置**: `api_planner_hitl = true` in `settings.toml`

### Layer 5 — Output Formatter（輸出格式化）
- **位置**: 最終 response 返回之前
- **功能**: structured JSON / verbatim template / Markdown 格式化
- **觸發**: 同時看 user input + generated response

---

## 與 Hermes 的對應映射

| CUGA 層 | Hermes 現狀 | 缺口 |
|---------|-----------|------|
| Intent Guard | `exploration-tool-scoping-gradient.md`（提案）| 無實作 |
| Playbook | `hermes-session-tree`（概念）| 動態注入未實作 |
| Tool Guide | `disabled_packs` DCG outbound | advisory 未串入 |
| Tool Approval | WS-035 blueprint | HITL gate 未實作 |
| Output Formatter | `heartbeat/actions.py`（basic）| 無 structured output |

**最大缺口**: Tool Approval（Layer 4）—— CUGA 在 code gen 後、execution 前有獨立的 human confirmation gate。Hermes 的 `gateway/run.py` 目前沒有這層。WS-035 blueprint 定義了 `PolicyInterceptor` 的 enforcement order，但實作細節（如何在 tool call 這個 hop 插入 pause）是空白。

---

## 實作架構亮點

### 1. Manager Mode — Draft → Publish Lifecycle
- `cuga start manager` 啟動 web UI
- Draft 模式允許編輯 tools/MCP/LLM/policies，try in draft chat
- Publish 後建立新 version，生產 chat 使用
- **對 Hermes 啟發**: cron job 的 skill set 版本管理是否也能走 Draft → Publish？

### 2. Multi-agent Supervisor（A2A + Remote Agents）
- External agent entries in supervisor config
- `[supervisor]` section in `settings.toml`
- CugaSupervisor SDK docs
- **對 Hermes 啟發**: Talos 作為 supervisor 的架構是否參考此模式？

### 3. Agent Skills — SKILL.md 格式
- `.agents/skills/SKILL.md` under repo
- `load_skill` tool 動態載入
- `sandbox_mode = "native"` or `"opensandbox"`
- **對照**: Hermes 的 skill 系統是 profile 目錄下的 `.md` 檔，CUGA 是 `.agents/skills/` 子目錄

### 4. Knowledge Engine — Docling Ingest
- Agent-level（永久） + Session-level（per-thread）的 scope 區分
- Docling 用於 PDF/Office/HTML/Markdown 解析
- **對照**: Hermes vault ingest 用 `sanitize_fetch.py` + Jaccard dedup，scope 只有 vault 全域

---

## 未追蹤 Leads

- https://docs.cuga.dev/docs/sdk/policies/ — Policies SDK 完整文件（CUGA 的 5-layer 實作細節）
- https://github.com/cuga-project/oak-bench — OAK benchmark（customer-care, 27 tasks）
- https://huggingface.co/datasets/ibm-research/BPO-Bench — BPO benchmark（26 tasks, enterprise workflows）

## ✅ 本次探索完成
