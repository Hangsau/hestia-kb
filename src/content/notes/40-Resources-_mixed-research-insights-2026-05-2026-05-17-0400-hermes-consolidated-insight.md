---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0400-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0400-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: medium
title: 跨筆記綜合洞察：Governance 的兩層缺口與 Lazy Capability 的收敛
updated: '2026-06-15'
type: research
status: budding
---

# 跨筆記綜合洞察：Governance 的兩層缺口與 Lazy Capability 的收敛

**消化筆記**: 2026-05-17-docker-agent-internals-hooks-defer-redact, 2026-05-17-aiuc1-q2-2026-detailed-changes

（摘要）Docker Agent 的三層治理架構（hooks/defer/redact）與 AIUC-1 Q2 新增的 execution-level controls（B006.3、E015.2、D003.4）指向同一個系統性缺口：當 agent 動態啟動 sub-agent 或載入新工具時，父層的 policy 與 logging 邊界沒有跟著擴展。

---

## Cross-Cutting Theme 1: Sub-Agent Tracing Gap — E015.2 映射 heartbeat 實作缺口

**支援筆記**: 2026-05-17-docker-agent-internals-hooks-defer-redact, 2026-05-17-aiuc1-q2-2026-detailed-changes

### 分析

AIUC-1 E015.2 要求 logging 覆蓋 tool calls 與 sub-agent actions。兩篇筆記都指向同一個問題：當前的 tracing/loglevel 是**平面**的，沒有層次。

| 層次 | 現況 | AIUC-1 需求 |
|------|------|------------|
| Parent agent actions | Heartbeat action_log 覆蓋 | E015.2 明確要求 |
| Sub-agent tool calls | ❌ 空白 | E015.2 明確要求 |
| Sub-agent activation (delegate_task) | ❌ 無獨立 record | D003.4 提到 multi-step workflow human approval |

Docker Agent 的 hook 架構解決了「何時執行治理」的時機問題，但**沒有解決治理邊界跟著 delegation 擴展**的問題。當 Heartbeat 啟動 `claude-code` 或 `delegate_task` 時：
- 父層的 `pre_tool_use`鉤子不會作用於 sub-agent 的 tool calls
- `action_log.json` 沒有 sub-agent 層的 tool 記錄
- 人類核准機制（`pending_approvals`）只到 tool-level，沒有 workflow-level

B006.3 的 wording 提供了更具體的描述：「limit blast radius when an agent or approved MCP server behaves unexpectedly at runtime」— 這個 "behaves unexpectedly at runtime" 暗示的是 sub-agent 在執行中才暴露的行為，靜態 policy 無法完全覆蓋。

**可行動下一步**: 在 `heartbeat_v2.py` 的 `delegate_task` 進入點（以及 `claude-code` subprocess 啟動處）加入 action_log 寫入，schema 為 `{type: "sub_agent_start", parent_session: <id>, sub_agent_type: <>, timestamp: <>}`。同時在 sub-agent 的 tool call 返回路徑上（非 blocking 讀取，而是非同步寫入），補一條 `{type: "sub_agent_tool_call", session: <>, tool: <>, args_hash: <>}` 的 record。

---

## Cross-Cuting Theme 2: Lazy Capability Loading 收斂 — Defer Pattern 與 AIUC-1 A003.4 的對齊

**支援筆記**: 2026-05-17-docker-agent-internals-hooks-defer-redact, 2026-05-17-aiuc1-q2-2026-detailed-changes

### 分析

Docker 的 `defer` pattern（`search_tool` + `add_tool`）與 AIUC-1 A003.4（Agent access and permissions management）表面上談的是不同層面的事，但內核相同：**最小權限不應該是靜態配置，而應該是動態發現與啟用的過程**。

具體的對應：

| Docker Defer 概念 | AIUC-1 A003.4 對應 | 共同原則 |
|------------------|-------------------|---------|
| Tool 初始狀態 = 不存在於 agent tool list | Agent 初始狀態 = 無任何 capability | 預設 deny |
| `search_tool` 發現可用 tool（case-insensitive substring） | Agent 的 permissions 需為 configurable + auditable | 可審計的發現過程 |
| `add_tool` 激活特定 capability | 顯式授權（opt-in）方才 grant capability | 明示同意 |
| 激活後 permanent（session lifetime） | 存取管理需 enterprise IAM integration | 需要身份綁定 |

Docker 沒有 IAM 的概念（只是 session-scoped），但 AIUC-1 A003.4 的 enterprise IAM 方向彌補了這一點。如果把這兩個視角合併，會得到一個更完整的設計：**capability lifecycle = discover → request → approve → activate → audit**。

Talos 作為 governance layer，目前 Phase 2-3 的設計處於「policy definition」與「pre_tool_use enforcement」的階段，但**還沒有把 capability discovery（相當於 Docker 的 search_tool）納入 policy scope**。也就是說：policy 定義了「哪些 tool 不准用」，但沒有定義「哪些 tool 允許被動態啟用」。

**可行動下一步**: 在 Talos Phase 2（Policy definition schema）新增一個 `DynamicCapabilities` section，schema 如同：

```yaml
dynamic_capabilities:
  require_explicit_activation: true   # 相當於 Docker deferAll=true
  discoverable_tools: ["git_*", "docker_*"]  # glob, 相當於 addSource 的 toolNames
  activation_requires_approval: ["terminal", "write_file"]  # 高風險 tool 需要 human-in-the-loop
```

這個 schema 同時滿足：A003.4 的 configurable permissions（`require_explicit_activation`）+ D003.4 的 workflow-level approval（`activation_requires_approval`）+ defer pattern 的實作對齊。

---

## 備註：Governance Stack 的三層對應

| 層次 | Docker 機制 | AIUC-1 Control | Talos Phase | 現有缺口 |
|------|------------|----------------|-------------|---------|
| When（時機） | Hook system（20+ event types） | B006.3（runtime execution safeguards） | Phase 3（Enforcement） | Sub-agent 層的 hook 傳播 |
| What（範圍） | Defer（capability 顆粒度） | A003.4（access/permissions mgmt） | Phase 2（Policy schema） | 缺少 DynamicCapabilities section |
| Protection（保護） | Portcullis redact（三攔截點） | E015.2（logging） | 相關 module | Sub-agent action logging |

兩篇筆記湊在一起才能看出：這三層缺口**不是獨立的**，它們共享同一個根本問題——delegation 打破了 policy 的邊界。
