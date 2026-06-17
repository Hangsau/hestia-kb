---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-NanoClaw-架構深度解析-延續
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-NanoClaw-架構深度解析-延續.md
title: 探索：NanoClaw 架構深度解析（延續）
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- container
- gateway
- hermes
- host
- message
- messages
- nanoclaw
- session
- status
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
domain: architecture
tags: [exploration, session-management, sqlite, multi-agent]
**日期**: 2026-05-23
**延續自**: [[2026-05-23-探索-NanoClaw-深度解析---延續自-Claws-層研究]]  [[2026-05-23-探索-Claws-生態系實作---nanobot---ZeroClaw]]
---

# 探索：NanoClaw 架構深度解析（延續）

**延續自**: [[2026-05-23-探索-NanoClaw-深度解析---延續自-Claws-層研究]]  [[2026-05-23-探索-LLM-Agent-failure-modes---Claws-architectural-layer]]

## Per-Source Insight

### NanoClaw 架構文檔（raw README，架構完整文件）

**Core Design**: 每個 agent session 掛載一個 SQLite DB作為唯一的 IO 機制。兩張表：`messages_in`（host→agent）與 `messages_out`（agent→host）。無 stdin/stdout IPC，無外部 message queue。

**雙層 DB 設計**：
- Central DB（host 端）：agent groups、conversations、routing tables
- Per-session DB（掛載進 container）：messages_in + messages_out，每 session 獨立 DB

**這個設計解決了什麼**：Hermes 的 gateway/agent 通信目前依賴共享狀態（gateway process）、HTTP API、filesystem 三種混合機制。NanoClaw 用 SQLite 統一所有 IO——agent 不需要知道訊息從哪來，只要讀 DB 寫 DB。Channel adapter 把外部 event（Slack/Discord/Telegram）轉成 DB rows，agent 把 tool call results 寫成 DB rows。Host 負責路由。

**Session DB Schema 關鍵設計**：
```sql
messages_in: id, kind(chat|task|webhook|system), status(pending|processing|completed|failed),
             process_after, recurrence(cron expr), tries, content(JSON blob)
messages_out: id, in_reply_to, delivered, deliver_after, recurrence,
              content(JSON blob), kind(chat|task|system)
```

**這個 schema 的厲害之處**：inbound 有 `status` 狀態機（pending→processing→completed/failed）+ `tries` 計數 + `process_after` 延遲——這讓 NanoClaw 自己實作了 message-level retry，不需要外部 queue 系統。Recurrence 直接存 cron expression，不需要外部 scheduler。

**Stale Detection**：如果 `status=processing` 但 `status_changed` 太舊（>10min），host 認定 container crash，重置為 `pending` + exponential backoff。這個 pattern 比 Hermes 的 watchdog（只測瞬時活性）更精確——它在追蹤「有沒有在合理時間內處理完」。

**Container Lifecycle 狀態機**：
```
stopped → running → idle → stopped
                   ↗
         idle → running（新 message 觸發）
```
Idle timeout = 30min，container 只在有 message 要處理時啟動，沒有 warm pool。Host 管理 lifecycle（spawn on wakeUpAgent, kill on idle timeout）。

**PR Factory 範例**（三 agent groups 協作）：
- Worker: per-thread session，每個 PR thread 一個 session
- Manager: shared session，查詢跨 worker sessions 的資料
- Supervisor: admin channel 的主 session + 被 @tagged 時在 worker thread 建立新 session（帶 context duplication）

Context duplication 是亮點：Supervisor 被呼叫時，host 把 worker thread 的 messages 複製進 supervisor session，這樣 supervisor 能在獨立 session 裡處理同一個 thread 的上下文。

---

## Hermes 啟發

### 1. SQLite 統一 IO 模式（高價值）

Hermes 目前 gateway/agent 通信複雜：gateway 寫 filesystem → agent 讀 filesystem → agent 寫 response → gateway 讀 response。這依賴 filesystem 作為 shared medium。

**NanoClaw 的 insight**：SQLite 的 WAL mode 支援 concurrent reader + writer（不同 table），天然適合這個 pattern。

**可以實驗的**：`~/.hermes/gateway_messages.db`，一張 `inbound`(agent-reads) + 一張 `outbound`(agent-writes)，WAL mode。Agent polling 改為 DB query。這比 filesystem 多了結構化查詢能力（哪些 pending? 按 timestamp 排序?）而且 atomic write。

### 2. Status-Based Message Processing（已有類似但更嚴謹）

Hermes 的 agent 狀態（running/suspended/idle）在 process 層，NanoClaw 把狀態機下放到 message 層：每個 message 都有自己的 lifecycle（pending→processing→completed/failed）。這個粒度更細——container crash 不會丟 message，因為 `processing` 的 message 會被 detect 並 retry。

**可以實驗的**：Heartbeat 的 action log 裡每個 step 的狀態目前是 flat list。可以讓 step 有自己的 status（pending→in_progress→done/error），failed step 在下次 EVOLVE 自動重跑。

### 3. Stale Detection 比 Watchdog 更好（高價值，現有痛點）

Hermes 的 watchdog 只測「gateway 活著」（重啟後 3 秒測 `active=true`），無法捕捉「重啟後穩定然後 crash」的 pattern（2026-05-19 實戰案例）。

NanoClaw 的方案：每個 message 有 `status_changed` timestamp。如果 `status=processing` 超過 10 分鐘，認定 crash。這個方案：
- 不需要 external health check
- 不需要 polling external process
- 只看 data 自己就能 detect failure

**可以實驗的**：`heartbeat_state.json` 加 `last_step_timestamp`，每個 action step 記 timestamp。如果 step `in_progress` 超過 N 分鐘沒有更新，trigger recovery。

### 4. Per-Session Isolation + Shared Agent Group

NanoClaw 的 container mount structure：
```
/workspace/           ← session folder（每次 session 不同）
  .claude/            ← SDK session data
  session.db          ← session SQLite
  outbox/             ← outbound files
/workspace/agent/     ← agent group folder（所有 session 共享同一份）
  CLAUDE.md
  skills/
```

這個 pattern 解決了「共享同一套 skills 但每個 conversation 隔離」的需求。Hermes 目前每個 conversation 是獨立的 session folder，但 `skills/` 是 symlink 到 global location——這本質上是一樣的設計，只是 Hermes 用 symlink 而非 mount。

**差距**：Hermes 的 session isolation 靠 filesystem（每個 session 有自己的 `.hermes/sessions/<id>/`），NanoClaw 用 container boundary 做強隔離。兩者殊途同歸。

### 5. Recurring Task as DB Feature（高價值）

NanoClaw 把 recurring task 實現為：message 有 `recurrence` cron expression，host sweep（~60s）找到 `deliver_after` 已到的 row，遞推下一個 occurrence。Host 而不是 agent 負責遞推。

**Hermes 的對比**：目前的 scheduled tasks 是 cron job 外部觸發。如果把 recurring task 內化為 data feature（message 有 recurrence + host sweep），就能讓 agent 自己建立 recurring tasks——而不需要外部 cron 干預。

**可以實驗的**：`_DoomLoopTracker` 的 cooldown機制目前是 in-memory counter。可以改成 per-scenario 的 DB row（scenario_id, last_alert_at, escalation_level）。這樣 heartbeat 重啟後 cooldown 狀態不丟。

### 6. Cross-Session Read Access（Agent-to-Agent 訊息）

NanoClaw 的 Manager agent 可以 query 其他 worker sessions 的 messages_in/messages_out。不同 access level（manager 只能看 content，supervisor 可以看 agent logs）。

這個功能對 Hermes 的 Hearth 系統很有用：Talos 可以 query Hestia 最近的 sessions，了解她在處理什麼任務，而不是靠 heartbeat state.json 的間接信號。

---

## 跨文章 Synthesis

NanoClaw 的核心 insight 是：**把 agent 當作 pure computation engine，所有 IO 都透過 DB**。Agent 不需要知道訊息從哪來（Slack/Discord/Telegram），不需要知道往哪去，不需要知道有沒有其他 agents 在通信。所有這些都由 host + channel adapters 處理。

這個設計與 Hermes 的 current architecture 比：
- ✅ 相似：agent 只處理 task，不管 platform specifics
- ✅ 相似：filesystem/DB 作为 shared state
- **差距**：Hermes 的 agent 仍然需要知道很多 gateway internal（tool names, session state），NanoClaw 的 agent 完全隔離（只讀 messages_in 寫 messages_out）
- **差距**：Hermes 沒有 NanoClaw 的 structured message status/recurrence/error-handling

**Claws ecosystem 的層次（整合前兩篇）**：
- nanobot: agent runner（每個 claw 是一個 MCP tool server）
- ZeroClaw: 零配置 claw 打包格式
- NanoClaw: 完整架構（host + container + DB + channel adapters）
- ClawHub: skill marketplace

NanoClaw 的 host 實作了 Hermes gateway 的很多職能（routing, lifecycle, scheduling），但用了更明確的架構。ClawHub 的 skill marketplace 概念對應 Hermes 的 skill system，但 NanoClaw 的 skill 是「分支並入主倉庫」的開發模式，不是「發布後下載」的發布模式。

---

## 未追蹤 Leads

- NanoClaw isolation model — https://raw.githubusercontent.com/nanocoai/nanoclaw/main/docs/isolation-model.md
- NanoClaw agent-runner details（MCP tools 全貌）— https://raw.githubusercontent.com/nanocoai/nanoclaw/main/docs/agent-runner-details.md
- ClawHub skill marketplace — https://clawhub.ai
- Statewright 的 DB-first architecture 與 NanoClaw 的 DB-as-IO 的比較（架構同構）

## ✅ 本次探索完成
