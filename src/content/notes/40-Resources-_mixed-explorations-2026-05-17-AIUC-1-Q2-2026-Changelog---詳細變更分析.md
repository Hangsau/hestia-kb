---
_slug: 40-Resources-_mixed-explorations-2026-05-17-AIUC-1-Q2-2026-Changelog---詳細變更分析
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-AIUC-1-Q2-2026-Changelog---詳細變更分析.md
title: AIUC-1 Q2 2026 Changelog — 詳細變更分析
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- aiuc
- changelog
- heartbeat
- level
- logging
- mcp
- net
- sub
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# AIUC-1 Q2 2026 Changelog — 詳細變更分析

**延續自**: [[2026-05-17-docker-governance-aiuc1-changelog]]
**日期**: 2026-05-17 03:31 CST
**標籤**: #agent-governance #aiuc1 #compliance #talos

## Per-Source Insights

### AIUC-1 Changelog (aiuc-1.com) — 完整 Q2 2026 變更

**直接 fetch 的內容**：整個 changelog 頁面本身就有完整的 14 requirements + 23 controls 變更明細，不需要再去找 GitHub diff。GitHub compare 連結 (`github.com/AIUC-1/aiuc-1/compare`) 404 — 可能還沒公開或只有認證會員能看。

**核心新增 controls**：
1. **A002.2** — Opt-in/opt-out 實作測試（net new）
2. **A003.4** — Agent access and permissions management（從 A003 拆分出來，net new）
3. **B006.3** — Execution-level safeguards：限制 agent 或 approved MCP server 異常行為的 blast radius（net new）
4. **B008.2/B008.3/B008.4** — MCP + A2A protocol 的 authentication、transport security、data integrity（net new）
5. **E015.2** — AI agent logging implementation：覆蓋 tool calls、sub-agent actions、provenance metadata（net new）

**與 Hermès 直接相關的變更分析**：

| Control | 變更類型 | 對 Hermès/Talos 的影響 |
|---------|---------|----------------------|
| B006.3 | **Addition** | WS-009 L3 sandboxing 直接對標。AIUC-1 明確定義「execution-level containment」是獨立 control，blast radius 限制是 explicit requirement |
| D003 | Revision | 從 approved functions 擴大到 MCP servers + multi-step workflows。Hermes 的 tool scoping 目前只覆蓋 functions，沒有針對 MCP server 層次的顆粒度控制 |
| D003.4 | Revision | 人類核准範圍從單一操作擴大到 multi-step workflows。探索 agent 現在是 fully autonomous，缺少 human-in-the-loop 機制 |
| E015.2 | **Addition** | Net new。明確要求 logging 覆蓋 tool calls 和 sub-agent actions。Heartbeat action log 目前只有 action 層，sub-agent 層（delegate_task）的 traceability 是空白 |
| A003.3/A003.4 | Revision/Separation | Agent identity 和 access management 拆成獨立 controls，要求 configurable + auditable + enterprise IAM integration |

**重要啟發**：
1. **E015.2 是 Heartbeat 的 immediate gap**：Heartbeat 的 `action_log.json` 記錄了 heartbeat 自己的 actions，但當 Heartbeat 啟動 sub-agent（via `delegate_task` 或 `claude-code`）時，那些 sub-agent 的 tool calls 不在 Heartbeat 的 logging 範圍內。如果要符合 AIUC-1 E015.2，sub-agent 層也需要獨立的 logging mechanism。
2. **B006.3 替 WS-009 提供了更清楚的 requirements text**：之前 WS-009 只說「microVM sandboxing」，但 AIUC-1 的 execution-level safeguards 控制面定義更具體——「limit blast radius when an agent or approved MCP server behaves unexpectedly at runtime」。這個 wording 可以直接拿來當 WS-009 的 success criteria。
3. **D003.4 human approval for multi-step workflows 是探索 agent 的 policy gap**：目前探索 agent 的human-in-the-loop 只有 `heartbeat_v2.py` 的 `pending_approvals` 机制（用於 tool-level approval），但沒有 workflow-level 的核准流程。

## 未追蹤

- （無）

## ✅ 本次探索完成

