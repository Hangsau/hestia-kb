---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-NanoClaw-架構文件深度挖掘---architecture-md---api-details-md
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-NanoClaw-架構文件深度挖掘---architecture-md---api-details-md.md
title: 探索：NanoClaw 架構文件深度挖掘 — architecture.md + api-details.md
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- architecture
- chat
- container
- hermes
- host
- nanoclaw
- runner
- sdk
- session
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "探索：NanoClaw 架構文件深度挖掘 — architecture.md + api-details.md"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
domain: architecture
**日期**: 2026-05-23（用 date 命令取實際系統日期，不要自己估算）
**延續自**: [[2026-05-23-探索-NanoClaw-架構延續-隔離模型---Agent-Runner]]
---

# 探索：NanoClaw 架構文件深度挖掘 — architecture.md + api-details.md

**延續自**: [[2026-05-23-探索-NanoClaw-架構延續-隔離模型---Agent-Runner]]

## Per-Source Insight

### NanoClaw 架構文件核心發現（architecture.md — 53KB raw README）

architecture.md 比 README.md 更深入，是完整的系統設計文件。

**DB-as-IO 的完整狀態機**：
```
pending → processing → completed
                      → failed（max retries exhausted，host 重置為 pending + backoff）
```
stale detection：若 `status='processing'` 且 `status_changed` 超過 10 分鐘，host 認定 container crash → reset to pending + 線性遞增 backoff（5s/10s/20s/40s）。

**Per-Session DB 的 session scope**：
- 每個 session 有自己獨立的 SQLite file：`sessions/{session_id}/session.db`
- Session folder 包含：`session.db` + `.claude/`（Claude SDK session data）+ `outbox/`
- Agent group folder 作為 second mount：`/workspace/agent/`（CLAUDE.md、skills）
- 兩個目錄掛載隔離：session scope 的 state vs agent group scope 的 config

**Container lifecycle 狀態機**：
```
stopped → running → idle → stopped
  ↗
idle → running（new message while warm）
```
- idle timeout：30 分鐘後 host 殺 container
- idle detection 的缺口（文件自己列出）：當 `ask_user_question` blocking 時，container 不該被認定 idle；agent 有 active tool calls 時也不該殺

**Host sweep 兩層 polling**：
- Active containers：~1s polling 檢查 messages_out
- All sessions：~60s sweep 處理 `process_after` / `deliver_after` + recurrence

**Code Structure 的五大原則**（從 33 個 skill branches 衝突分析得來）：
1. 分離按 entity 不按 layer（messaging-groups.ts, sessions.ts, agent-groups.ts）
2. 衝突熱點獨立出去（index.ts 太肥 → 拆成 router/delivery/session-manager）
3. Config 宣告在使用處而非集中（每個 module 讀自己的 env）
4. 掛載用 registration pattern（channel 宣告 mounts，container runner 讀 registry）
5. DB 用 migration runner（schema.ts 為 current state，migrations 為 append-only history）

**PR Factory 範例**（architecture.md 的完整實例）：
- Worker agent：每個 GitHub PR thread 一個 session，共用 pr-worker agent group
- Manager agent：single session，查詢所有 worker session DB 回答 aggregate 問題
- Supervisor agent：在 admin channel 有主 session；被 @tagged 時建立 per-thread session（context duplicated）
- 關鍵：cross-session read 是 filesystem/DB 存取（mount 或 query），不需要特殊抽象

**Schema 的 user_roles 設計**：
```sql
role: 'owner' | 'admin'
agent_group_id: TEXT | NULL  -- NULL = global
```
Owner 只能 global（agent_group_id = NULL）；admin 可以 global 或 scoped。這防止了 owner 權限洩漏到特定 agent group。

### NanoClaw API Details（api-details.md）

**ChannelAdapter interface 完整定義**：
```typescript
interface ChannelAdapter {
  name: string; channelType: string;
  setup(config: ChannelSetup): Promise;
  teardown(): Promise;
  isConnected(): boolean;
  deliver(platformId, threadId, message): Promise;
  setTyping?(platformId, threadId): Promise;
  syncConversations?(): Promise;
  updateConversations?(conversations): void;
}
```

**Chat SDK Bridge 實作模式**：
bridge 包裝 Chat SDK adapter + Chat instance → 符合 NanoClaw ChannelAdapter interface。具體職責：
- 訂閱機制：Chat SDK 自己管理 thread-level subscription（`onNewMention` / `onNewMessage` / `thread.subscribe()`）
- NanoClaw 在 channel level 運作（listen to channel）；bridge 在 thread level 處理（Chat SDK）
- Bridging 兩者的差異：Chat SDK subscription 是 sub-channel granularity

**Native Channel（WhatsApp/Baileys）範例**：
native channel 直接實作 ChannelAdapter，不走 Chat SDK。Trigger check 在 adapter 內（不靠 host），trigger pattern 是 regex string。

**messages_in content 格式**：
- `chat`：純 NanoClaw format（sender, text, attachments）
- `chat-sdk`：Chat SDK SerializedMessage（完整結構化）
- Question response：多了 `questionId` + `selectedOption`（由 pending_questions table routing 回來）

**messages_out operation types**：
- `operation: 'ask_question'` — 發卡、等待回應（blocking tool call）
- `operation: 'edit'` — 修改已發訊息
- `operation: 'reaction'` — 加 emoji
- `action: 'reset_session'` — system action（host 处理）

---

## 跨文章 Synthesis

**DB-as-IO 架構的完整畫面（architecture + api-details）**：

architecture.md 定義了高層設計（per-session DB、host-agent 分離、entity model），api-details.md 定義了實作介面（ChannelAdapter、message content 格式、host delivery logic）。兩者合起來是完整系統。

**NanoClaw 與 Hermes 的架構對應（更新版）**：
| NanoClaw | Hermes |
|----------|--------|
| Host | Hermes gateway |
| Agent-runner（container 內） | Agent session（LLM 執行層） |
| Agent provider（SDK 包裝） | Model provider（DeepSeek v4-pro） |
| Central DB | Gateway 的 in-process state |
| Per-session DB | Agent session 的 context/history |
| ChannelAdapter interface | Platform handlers（Telegram, etc.） |
| messaging_group_agents routing table | Gateway session resolution |
| pending_questions table | Gateway approval queue |
| Host sweep（60s） | Heartbeat cron（30min） |

**最大差異（architecture.md 強調）**：
- NanoClaw：IO 放 SQLite，重啟不丟 state（WAL mode）
- Hermes：IO 在 gateway process shared state，重啟丟 state（依賴 session persistence）
- NanoClaw 的 stale detection：靠 `status_changed` 欄位追蹤 processing 超時
- Hermes 的 stale detection：靠 watchdog（瞬時活性測試，會漏掉重啟後 crash）

**DB schema 分離模式（教訓）**：
- Central DB：entity model、routing、user_roles、sessions
- Per-session DB：messages_in/messages_out、outbox
- 這個分離讓 NanoClaw 能支援「cross-session read」（manager agent 查 worker sessions）而不需要特殊抽象——只要 filesystem mount 就好

---

## Hermes 內部啟發

1. **pending_questions pattern 值得借鑒**：Hermes 的 approval queue 目前是 in-process。NanoClaw 的 `pending_questions` 是 DB table，query by `question_id`，不需 scan session DBs。考慮在 Hermes 加入 `pending_gateway_actions` table（`action_id`, `session_id`, `target_session_id`, `payload`, `response`，由 gateway 管理）。

2. **Container lifecycle 的 idle detection 缺口**：NanoClaw 自己列出這個問題（blocking tool call / active tool calls 不該被認定 idle）。Hermes 的 watchdog 有同樣問題（只是測瞬時，不測持續）。這是架構限制，目前沒有乾淨解法——需要通訊器架構（消息持久化）。

3. **Code structure 的五大原則**：
   - Conflict hotspot analysis（33 skill branches）→ 具體知道哪個檔案最需要重構（index.ts, config.ts, container-runner.ts, db.ts, ipc.ts）
   - Registration pattern over switch statement
   - Mount declaration as first-class concept
   - Hermes 的 gateway handlers（Telegram, etc.）可以受益於類似的 registration pattern

4. **session_db 位置的分離設計**：`sessions/{session_id}/` 是 session scope，`/workspace/agent/` 是 agent group scope。Hermes 的 session state 沒有這個分離——context 跟 agent config 混在一起。考慮引入類似的雙目錄概念。

5. **Pragma 模式的自然嵌入**：PR Factory 範例展示了三種 agent role 的協作。Hermes 目前沒有類似的 multi-agent workspace 概念（只有 Hearth 的外部協作）。這個模式值得研究。

---

## 未追蹤 Leads

- NanoClaw agent-runner-details.md — MCP tool 完整定義、provider 實作細節
- NanoClaw container/agent-runner/src/db/ — session DB connection/messages-in-out 的具體程式碼
- NanoClaw src/db/migrations/ — migration runner 實作

## ✅ 本次探索完成
