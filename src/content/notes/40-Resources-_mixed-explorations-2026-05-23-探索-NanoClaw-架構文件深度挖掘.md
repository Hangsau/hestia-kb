---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-NanoClaw-架構文件深度挖掘
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-NanoClaw-架構文件深度挖掘.md
title: 探索：NanoClaw 架構文件深度挖掘
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- chat
- container
- hermes
- host
- message
- nanoclaw
- runner
- session
- tool
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：NanoClaw 架構文件深度挖掘

**延續自**: [[2026-05-23-NanoClaw-架構延續-隔離模型---Agent-Runner]]

**日期**: 2026-05-23
**類型**: 架構研究
**來源**: `https://raw.githubusercontent.com/nanocoai/nanoclaw/main/docs/architecture.md` + `api-details.md`

---

## 核心發現：雙層 SQLite DB 作為隔離機制

NanoClaw 的核心設計：**每個 agent session 掛載一個專屬 SQLite DB**，這是 host 和 container之間的唯一 IO 機制。

```
Host (主 process)
  └── Central DB: agent groups、conversations、routing tables
  └── Per-session DB (mounted into container)
        ├── messages_in (host → agent-runner)
        └── messages_out (agent-runner → host)
```

**關鍵**：channel adapters 不直接碰 Central DB，host 負責 lookup。adapters 只回傳 platform-level ID（platformChannelId + platformThreadId），host 做映射後寫入 session DB。

這和 Hermes 的 MCP gateway 設計思路不同：
- Hermes：MCP tool 為 agent 提供能力擴展，tool 在 host context 執行
- NanoClaw：DB 為隔離邊界，agent 完全運行在 container 內，只能透過 DB message exchange 與 host 通訊

---

## Agent Groups vs Sessions 的彈性設計

```
Agent Group（共享檔案系統）
  ├── CLAUDE.md / skills / container config（共享）
  ├── 多個 Session（每個 session = 獨立 container）
  │     └── 各自掛載相同 filesystem + 不同 session DB
  └── 同一 agent group 的多個 session 可以共享 conversation
```

Session mode 可配置：
- **Shared session**：同一 agent group 的所有訊息共享一個 session
- **Per-thread session**：每個平台 thread 有自己的 session（即使屬於同一 agent group）

對比 Hermes：Hermes 的 session 管理更集中，沒有這種「同一 group 不同 thread 開不同 container」的彈性。

---

## Channel Adapter 職責邊界

Adapter 負責：
1. 接收平台事件（webhook/polling/websocket）
2. **過濾**：決定哪些訊息要 forward 給 host（stateless regex 或 stateful mention tracking）
3. 提取標準化的 `platformChannelId` + `platformThreadId`
4. 回傳（host 做映射）

**關鍵設計**：adapter 只回報 platform-level ID，**不知道** agent group / session 的存在。映射完全在 host 層處理。

### Native vs Chat SDK 雙軌

- **Chat SDK adapters**（Discord/Slack/Telegram 等）：透過 bridge 包裝，符合 NanoClaw ChannelAdapter interface
- **Native adapters**（WhatsApp/Baileys、Gmail）：直接實作 ChannelAdapter interface，不走 Chat SDK

Chat SDK 內部有自己的 subscription model（`onNewMention`、`thread.subscribe()`），NanoClaw 不干預。

---

## Session DB Schema：Message-as-IO

```sql
messages_in (host → agent-runner)
  id, kind ('chat'|'chat-sdk'|'task'|'webhook'|'system'),
  status ('pending'|'processing'|'completed'|'failed'),
  process_after (可延後處理時間),
  recurrence (cron expression)

messages_out (agent-runner → host)
  id, kind, content (JSON blob), status, ...
```

所有訊息都是同一格式：chat、tasks、webhooks、system actions、agent-to-agent，全部用這兩個 table。

**對比 Hermes**：Hermes 用 tool calls + tool results 作為主要 IO 機制，session 狀態存在 memory layer。NanoClaw 的 DB-as-IO 模型更嚴格隔離，但也更難做到「tool 直接呼叫 external API」而不經過 message DB。

---

## Container Lifecycle：Host 作為 orchestrator

```
wakeUpAgent(session) → 查無 container → Spawn
Container idle timeout → Kill
MAX_CONCURRENT_CONTAINERS → 限制並發
```

Container 啟動時，agent-runner 立即開始 polling session DB。這和 Hermes 的 heartbeat 模式不同——NanoClaw 是 event-driven（DB 有新訊息就 wake），Hermes 是時間驅動（heartbeat cron）。

---

## Media Handling：內外分工

- **Inbound media**：host 不下載，URL 寫進 DB message，agent-runner 在 container 內自行下載處理
- **Outbound**：agent 呼叫 `send_file` tool → 檔案放進 `/workspace/outbox/{message_id}/` → host 讀取後經 adapter 傳送

這個設計讓 agent 處理 media 的方式和處理本地檔案一致（都掛在 `/workspace/` 下），不需要特殊處理。

---

## 與 Hermes 的架構對比

| 面向 | NanoClaw | Hermes |
|------|----------|--------|
| IO 模型 | SQLite DB message exchange | MCP tool calls + tool results |
| 隔離邊界 | Container + per-session DB | Process + MCP gateway |
| Session 管理 | Per-thread or shared | 集中式 session tree |
| Channel 整合 | Adapter bridge pattern | MCP server registry |
| Container 生命 | Event-driven (DB polling) | Time-driven (heartbeat) |
| Agent-to-Agent | 透過 DB messages | 透過 comms poll + INBOX |

---

## 未追蹤 Leads

- ClawHub API docs: https://clawhub.ai/docs（deployment/registry layer）
- `agent-runner-details.md`（NanoClaw repo）— 包含 `send_file` tool interface

---

## ✅ 本次探索完成
