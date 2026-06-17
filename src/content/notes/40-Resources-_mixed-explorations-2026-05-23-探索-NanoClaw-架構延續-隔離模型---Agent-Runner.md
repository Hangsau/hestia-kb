---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-NanoClaw-架構延續-隔離模型---Agent-Runner
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-NanoClaw-架構延續-隔離模型---Agent-Runner.md
title: 探索：NanoClaw 架構延續（隔離模型 + Agent-Runner）
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- channel
- gateway
- hermes
- message
- messages
- nanoclaw
- provider
- session
- string
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "探索：NanoClaw 架構延續（隔離模型 + Agent-Runner）"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [agent, container, database, gateway, hermes, message, messages, nanoclaw, provider, routing, session, sqlite, status]
---

---
domain: architecture
tags: [exploration, session-management, sqlite, multi-agent]
**日期**: 2026-05-23（用 date 命令取實際系統日期，不要自己估算）
**延續自**: [[2026-05-23-探索-NanoClaw-架構深度解析-延續]]  [[2026-05-23-探索-Claws-生態系實作---nanobot---ZeroClaw]]
---

# 探索：NanoClaw 架構延續（隔離模型 + Agent-Runner）

**延續自**: [[2026-05-23-探索-NanoClaw-架構深度解析-延續]]  [[2026-05-23-探索-Claws-生態系實作---nanobot---ZeroClaw]]

## Per-Source Insight

### NanoClaw Channel Isolation Model（raw README）

**三層隔離模型** — NanoClaw 用 entity model 解耦 messaging channels 和 agent groups：

```
agent_groups (workspace, memory, CLAUDE.md, personality)
↕ many-to-many
messaging_groups (channel/chat/group on a platform)
via
messaging_group_agents (session_mode, trigger_rules, priority)
```

**三個 Isolation Level**：
1. **Shared Session**（`session_mode: 'agent-shared'`）：多個 channel 進入同一 conversation，GitHub PR comment + Slack message 並排顯示，適合 webhook/notification channel + chat channel 組合
2. **Same Agent, Separate Sessions**（`session_mode: 'shared'` 或 `'per-thread'`）：同一 workspace/memory/CLAUDE.md，但 conversation thread 各自獨立。典型：個人用戶跨多個平台（3 個 Telegram chat，各自獨立 thread）
3. **Separate Agent Groups**：每個 channel 有自己的 workspace、memory、CLAUDE.md，完全隔離。典型：不同人參與（朋友 A vs 團隊 B）

**Hermes 對比**：Hermes 的 gateway 目前沒有明確的三層隔離模型——所有 channel 都走同一 gateway process，session resolution 靠 gateway 的 single-instance shared state。這在單人使用場景沒問題，但多人協作（用戶 A vs 用戶 B）或隱私邊界場景（工作 vs 個人）會遇到困難。

**實作啟發**：
- NanoClaw 的 `messaging_group_agents` 連結表是個好設計——在不改 agent group 本體的情況下，動態調整 channel-to-agent 的 mapping
- Hermes 可以朝同樣方向演進：從「所有 channel 進同一 gateway」→「messaging_group 是 first-class entity」，支援動態 routing 配置

### NanoClaw Agent-Runner 實作（raw README）

**核心切割**：Agent-runner 兩層分離：
1. **Agent-runner core** — 擁有 poll loop、message formatting、DB 讀寫、MCP tool 實作、routing、status 管理
2. **Agent provider** — 擁有 SDK 互動，把格式化後的 prompts 送給 SDK，回傳 events

**這個切割的價值**：provider 是 protocol adapter，可以插拔（Claude / Codex / OpenCode）。core 不變，provider 替換代價極低。

**AgentProvider Interface**：
```typescript
interface AgentProvider {
  query(input: QueryInput): AgentQuery;
}
interface QueryInput {
  prompt: string | ContentBlock[];  // 已經格式化的 prompt
  sessionId?: string;
  resumeAt?: string;               // Claude-specific：從特定 message UUID 恢復
  cwd: string;
  mcpServers: Record<string, McpServerConfig>;
  systemPrompt?: string;
  env: Record<string, string>;
  additionalDirectories?: string[];
}
interface AgentQuery {
  push(message: string): void;    // 推送 follow-up message
  end(): void;
  events: AsyncIterable<ProviderEvent>;
  abort(): void;
}
type ProviderEvent =
  | { type: 'init'; sessionId: string }
  | { type: 'result'; text: string | null }
  | { type: 'error'; message: string; retryable: boolean; classification?: string }
  | { type: 'progress'; message: string };
```

**Poll Loop 的狀態管理邏輯**（與 Hermes 設計高度相似）：
```sql
-- Pick up: 標記 processing
UPDATE messages_in SET status='processing', status_changed=now(),
     tries=tries+1 WHERE id IN (...)

-- Complete
UPDATE messages_in SET status='completed', status_changed=now()

-- Error: Agent-runner 不設定 failed，只留 processing
-- Host（NanoClaw 的主程式）透過 status_changed 檢測 stale，重新設定 pending + backoff
```

**MCP Tool 全貌**（agent-runner 自己實作的一組 tools，寫入 session DB）：
- `send_message` — 發送聊天訊息到當前 conversation 或指定 destination
- `send_file` — 發送檔案（寫入 outbox目錄 + messages_out row）
- `send_card` — 發送結構化卡片
- `ask_user_question` — **Blocking tool call**：寫入 messages_out 等待 response，poll messages_in 找答案。這是 NanoClaw 的 user-in-the-loop 機制，與 WS-010 的 OTP gate 概念同構
- `edit_message` / `add_reaction` — 修改已發送的訊息
- `send_to_agent` — 跨 agent group 通信（routing via `channel_type: 'agent'`）
- `schedule_task` / `list_tasks` / `cancel_task` / `pause_task` / `resume_task` / `update_task` — 任務調度（recurrence = cron expression，直接存 messages_in）
- `register_agent_group` — Admin 專用，寫 system action message

**ask_user_question 的 blocking 實作**（重要！與 Hermes 的差異）：
1. 寫 `messages_out` 帶 `operation: 'ask_question'` + questionId
2. Poll `messages_in` 等 response row 帶 matching questionId
3. 返回 selectedOption 作為 tool result
4. Agent execution 停在 tool call，provider 的 query 保持 open（Claude holds the tool call open）
5. Timeout 後返回 timeout error

這個機制比 Hermes 目前的 polling 更乾淨——它把等待變成 explicit DB polling，而不是 Hermes 的 event-driven 架構（event 進來後怎麼處理靠 gateway 的 dispatch 邏輯）。

**Claude Provider 的 hooks**：
- `PreCompact`：transcript archiving（每次 compact 前存檔）
- `PreToolUse`：sanitizeBashHook（清理 bash env vars）

**Hermes 對比啟發**：
- Hermes 的 gateway 也需要類似的 hook system（pre-tool-use sanitization、pre-compaction archiving）——目前在 `gateway/platforms/telegram.py` 裡是散落的，沒有 uniform 介面
- Hermes 的 tool unblock 機制（`resolve_gateway_approval`）與 NanoClaw 的 `ask_user_question` 是同一個問題的不同解法。NanoClaw 用 DB polling，Hermes 用 gateway 的 approval queue

---

## 跨文章 Synthesis

**DB-as-IO 架構的完整畫面**：

NanoClaw 的架構是三層分離：
1. **Host**（NanoClaw 主程式）— 管理 agent groups、sessions、routing、central DB、container lifecycle
2. **Agent-runner**（container 內）— Poll session DB、format messages、送 prompt 給 provider、處理 provider events、MCP tools、寫 messages_out
3. **Agent provider**（container 內）— SDK 包裝（Claude/Codex/OpenCode），與 SDK 通信

**這個架構與 Hermes 的對應**：
| NanoClaw | Hermes |
|----------|--------|
| Host | Hermes gateway（process） |
| Agent-runner | Agent session（LLM 執行層） |
| Agent provider | Model provider（DeepSeek v4-pro 等） |
| Central DB | Gateway 的 in-process state |
| Session DB | Agent session 的 context/history |

**最大差異**：NanoClaw 把 IO 放到 SQLite，Hermes 把 IO 放在 gateway process 的 shared state。前者的好處是重啟不丟 state（DB 持久化），後者的好處是低延遲（in-memory）。NanoClaw 的 stale detection 靠 `status_changed` 欄位追蹤，Hermes 用 watchdog（瞬時活性測試）。

**DB-as-IO 的訊息狀態機**（NanoClaw 的設計更完整）：
```
pending → processing → completed
                        → failed（max retries exhausted，host 重置為 pending + backoff）
```
Hermes 目前沒有這麼完整的 message-level state machine——tool call 的狀態（blocked / unblocked / completed）更多是分散在 gateway 邏輯裡。

---

## Hermes 內部啟發

1. **messaging_group 概念**：NanoClaw 的 `messaging_group_agents` 連結表讓 routing 完全可配置。Hermes 可以朝這個方向演進——把「channel 進哪個 session」做成 first-class data model，而非 hardcoded logic。

2. **Blocking tool call 模式**：`ask_user_question` 用 DB polling 實現 blocking 的方式比 Hermes 的 event 監聽更簡單。考慮在 Hermes 的 `resolve_gateway_approval` 改用類似的 polling 機制（或者用 NanoClaw 的 DB-as-IO 模式）。

3. **Hook system 抽象**：Claude 的 `PreCompact` / `PreToolUse` hooks 讓行為改寫不需要修改 SDK 本體。Hermes 可以建立同樣的 hook 層（目前散落在 telegram.py 各處，應該統一）。

4. **Pre-agent script 模式**：tasks 的 `script` field + `wakeAgent` signal 是個聰明設計——script 可以先過濾不需要 agent 介入的任務。Hermes 的 cron job 模式類似但更重。

---

## 未追蹤 Leads

- NanoClaw architecture.md（高層設計）— https://raw.githubusercontent.com/nanocoai/nanoclaw/main/docs/architecture.md
- NanoClaw api-details.md（channel adapter interface）— https://raw.githubusercontent.com/nanocoai/nanoclaw/main/docs/api-details.md
- ClawHub API / developer docs — https://clawhub.ai/docs

## ✅ 本次探索完成
