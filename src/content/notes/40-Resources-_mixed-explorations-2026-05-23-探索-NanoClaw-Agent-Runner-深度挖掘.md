---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-NanoClaw-Agent-Runner-深度挖掘
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-NanoClaw-Agent-Runner-深度挖掘.md
title: 探索：NanoClaw Agent-Runner 深度挖掘
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claude
- hermes
- interface
- messages
- nanoclaw
- provider
- runner
- string
- tool
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：NanoClaw Agent-Runner 深度挖掘

**延續自**: [[2026-05-23-NanoClaw-架構文件深度挖掘]]

**日期**: 2026-05-23
**類型**: 架構研究
**來源**: `https://raw.githubusercontent.com/nanocoai/nanoclaw/main/docs/agent-runner-details.md`

---

## 核心發現：AgentProvider Interface — 三種 SDK 同一介面

NanoClaw 的核心抽象是 **AgentProvider interface**：

```typescript
interface AgentProvider {
  query(input: QueryInput): AgentQuery;
}
interface QueryInput {
  prompt: string | ContentBlock[];
  sessionId?: string;
  resumeAt?: string;        // Claude 專用：從特定訊息 UUID 恢復
  cwd: string;
  mcpServers: Record;
  systemPrompt?: string;
  env: Record;
  additionalDirectories?: string[];
}
interface AgentQuery {
  push(message: string): void;
  end(): void;
  events: AsyncIterable<ProviderEvent>;
  abort(): void;
}
```

三個實作：
- **Claude Provider** (trunk): Wraps `@anthropic-ai/claude-agent-sdk` — 最完整，有 hooks (PreCompact, PreToolUse)、resumeSessionAt
- **Codex Provider** (技能安裝): Wraps `@openai/codex-sdk` — 用 abort+restart 模式處理 follow-up
- **OpenCode Provider** (技能安裝): Wraps `@opencode-ai/sdk` — 用 local gRPC/HTTP server + SSE，**不支援 session resume**

**對 Hermes 的啟發**：如果未來要支援多個 LLM backend，可以學 NanoClaw 定義一個 `AgentProvider` interface，把 SDK 差異封裝在 provider 層。Hermes 目前用 MCP gateway 模式，agent 呼叫 tool；NanoClaw 是 host 呼叫 provider API，方向相反。

---

## ask_user_question — Blocking Human-in-the-Loop

這是整份文件最有價值的部分：

```typescript
// 實作：寫一個 messages_out row，poll messages_in 等回應
async function ask_user_question(params) {
  1. Generate questionId
  2. Write messages_out with operation: 'ask_question', questionId
  3. Poll messages_in for matching questionId
  4. Return selectedOption as tool result (or timeout error)
  // Agent execution is PAUSED at this tool call
}
```

**Blocking tool 模式**：Claude holds the tool call open，agent-runner 在背景 polling。這個模式和 Hermes 的 OTP gate 互補：

| 面向 | NanoClaw ask_user_question | Hermes OTP gate |
|------|---------------------------|-----------------|
| 觸發方式 | Agent 主動呼叫 tool | Gateway 在高風險操作前阻斷 |
| 回應方式 | Poll messages_in | User 輸入 OTP 到 Telegram |
| 等待機制 | Async poll loop | In-memory token store |
| Timeout | 預設 300s | 預設 300s |

NanoClaw 的 blocking tool 模式可以直接借鑒：未來可以在 MCP tool 層實作 `ask_approval` tool，用 polling 機制實作 blocking wait，而非現在的 OTP 模式。

---

## Pre-Agent Scripts — Task 前置腳本決策

```typescript
// bash 腳本運行，JSON output 決定是否 wake agent
if (scriptOutput.wakeAgent === false) {
  mark_completed(); return;
}
enrich_prompt_with(scriptOutput.data);
invoke_provider();
```

**對 Hermes 的啟發**：`schedule_task` 的 script 欄位可以做：爬蟲 fetch → JSON → 判斷是否需要 agent 介入。這是「不需要就跳過」的 lazy agent 模式，和 Hermes heartbeat 的 time-driven 互補。

---

## Provider 差異細節

### Claude 專有功能
- `PreCompact` hook：壓縮前歸檔對話 transcript
- `PreToolUse` hook：sanitize bash 環境變數
- `resumeAt`：從特定訊息 UUID 恢復
- `allowedTools`：工具白名單

### Codex/OpenCode 差異
- 不支援 streaming input → 用 abort+restart 模擬
- 不支援 resumeSessionAt
- OpenCode 用 local server lifecycle 管理 sessions

### sessionId 處理
- 三個 provider 都從 `ProviderEvent { type: 'init', sessionId }` 捕獲 session ID
- Claude 寫 Central DB sessions table；Codex/OpenCode 自己管
- Container 重啟後：host 從 Central DB 讀 sessionId 重建；但 `resumeAt` (UUID level) 會丟失

---

## DB-as-IO 的 MCP 工具實現

所有 MCP tool 都寫入 session DB：

```typescript
// send_message → 寫 messages_out row
// ask_user_question → 寫 messages_out + poll messages_in
// schedule_task → 寫 messages_in row (self, with recurrence)
// edit_message → 寫 messages_out row with operation: 'edit'
// send_to_agent → 寫 messages_out row，routing 指向另一個 session
```

MCP server 用第二個連接（SQLite WAL 模式）打開同一個 DB file。這保證了：
- 隔離：agent 在 container 內，只能透過 DB 和 host 通訊
- 並發安全：WAL mode 允許多 reader + 1 writer

**對 Hermes 的對比**：Hermes 用 MCP tool 直接呼叫外部 API 或寫本地檔案；NanoClaw 所有 IO 都經過 DB message exchange。這讓 NanoClaw 的 audit trail 非常完整（每個 action 都是一筆 DB row），但犧牲了直接 API 呼叫的便利性。

---

## Status Management — Host-side Retry

```
pending → processing → completed
                      → failed (max retries exhausted)
```

**關鍵**：agent-runner 只更新 pending→processing 和 processing→completed。**不直接標 failed**——留給 host 檢測 stale processing 做 retry policy。這把重試邏輯集中到 host 層，agent-runner 只負責狀態機的一小段。

---

## 未追蹤 Leads

- `/providers` branch 的額外 provider 安裝機制（NanoClaw skill 如何註冊新 provider）
- `translateClaudeEvents` 的完整實作（event mapping logic）
- `additionalDirectories` 在 agent-runner 的實際使用方式

---

## ✅ 本次探索完成

