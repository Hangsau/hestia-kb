---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Hermes-Gateway-解剖-它到底做了什麼
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Hermes-Gateway-解剖-它到底做了什麼.md
title: Hermes Gateway 解剖：它到底做了什麼
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- auto
- cache
- gateway
- hermes
- lifecycle
- mcp
- message
- per
- session
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Hermes Gateway 解剖：它到底做了什麼

**Date**: 2026-05-14
**延續自**: [[2026-05-13-mcp-gateway-orchestrator-convergence]]（open question #1）
**Source**: `/usr/local/lib/hermes-agent/gateway/` source code
**Theme**: Hermes internal — gateway architecture

---

## TL;DR

`hermes gateway run` 是一個**嵌入式 agent runtime + messaging hub**，不是 MCP gateway。它管理 agent lifecycle（cache/sessions/interrupts），但**不做** MCP proxy、tool routing、protocol federation、credential vaulting。

之前 convergence 筆記推測的三個選項中，**Option C (Hybrid)** 比原先以為的更自然：Hermes gateway 已經有一半（agent lifecycle），缺的只是 MCP federation + credential 那半。

---

## 六層架構

### Layer 1: Transport — 17+ 個 Platform Adapter

```
user message → Telegram/Discord/Slack/WhatsApp/... adapter
              → BasePlatformAdapter._process_message()
              → GatewayRunner._handle_message()
```

每個 adapter 實作：connect、receive、send、media、interrupt。共用 base class 有 session guard、pending queue、auto-TTS、typing indicator 等。

### Layer 2: Session Management

- `SessionStore`：persistent session storage + reset policy + expiry
- `SessionSource`：platform/channel/user context tracking
- PII redaction（hash user/chat IDs）
- Session expiry watcher（每 5 分鐘 finalize 過期 session，清 agent cache）

### Layer 3: Agent Runtime — 這是重點

- **AIAgent cache**：LRU OrderedDict，max 128 entries，1h idle TTL
  - 為什麼要有 cache？因為 prompt caching。沒 cache 的話每個 message 重建 AIAgent = 重建 system prompt + memory = Anthropic prompt cache miss = 10x 成本
- **Running agent tracking**：`_running_agents` dict，追蹤每個 session 的 AIAgent 實例，供 interrupt 用
- **Per-session overrides**：`/model`、`/reasoning` 指令可以 per-session 換 model/provider/reasoning effort
- **Pending approvals**：`/approve`、`/deny` 的 exec approval 狀態
- **Queued events**：`/queue` 指令的 FIFO 隊列

### Layer 4: Background Subsystems（全部 asyncio task）

| Subsystem | 頻率 | 做什麼 |
|-----------|------|--------|
| Heartbeat v2 autonomic | 30s | sense-only：寫 state file，偵測 stuck agents，可能 auto-interrupt |
| Heartbeat v2 cognitive | 5min | idle 時 decide+act：WORK/EVOLVE/REST/CONNECT/REPORT |
| Kanban notifier | ~15s | 送 task completed/blocked/crashed 通知給訂閱者 |
| Kanban dispatcher | 30s | 從 kanban queue 挑 ready task，spawn worker |
| Session expiry | 5min | finalize 過期 session，cleanup agent cache |
| Platform reconnect | 可變 | 重試 failed platform connections |
| Stale-code check | per-message | 偵測 code update，觸發 auto-restart |

### Layer 5: Message Handling Loop

```
_handle_message(event)
  → resolve session (create or resume)
  → check auto-continue (tool-tail / interrupted turn)
  → get/create AIAgent (from cache or new)
  → run AIAgent.run_conversation()
  → deliver response via adapter.send()
  → fire post-delivery callbacks
```

Auto-continue freshness：如果上次 transcript timestamp 在 1 小時內，自動 resume（處理 gateway restart 後的 tool-tail）。

### Layer 6: Operational

- Stuck-loop detection：同一 session 在不同 restart 中被重複 suspend → auto-suspend
- Clean shutdown marker：`~/.hermes/.clean_shutdown` → 下次啟動不 suspend sessions
- Update notification：`/update` 完成後通知發起者
- Channel directory：`send_message` 的 name resolution
- Runtime status file：`gateway_state.json` 給外部監控用

---

## 對照：Hermes Gateway vs Convergence Landscape

| 能力 | ContextForge | Archestra | Hermes Gateway |
|------|-------------|-----------|----------------|
| MCP protocol federation | ✅ REST/gRPC/A2A→MCP | ✅ | ❌ |
| Credential vaulting | ✅ centralized | ✅ | ❌（per-adapter config） |
| Agent lifecycle mgmt | ❌ | ✅ K8s pods + OAuth | ✅ cache + sessions + interrupts |
| Audit trails | ✅ | ✅ | 部分（session transcripts） |
| Observability | ✅ | ✅ | 部分（heartbeat state + logs） |
| Rate limiting / cost | ❌ | ✅ | 部分（iteration budget） |
| Multi-platform messaging | ❌ | ❌ | ✅ 17+ platforms |
| Embedded kanban/orchestrator | ❌ | ❌ | ✅ |

## 關鍵洞察

### 1. Hermes gateway 的 agent lifecycle 比想像中完整

它不是單純的 message router。它有：
- Agent cache（prompt caching 最佳化）
- Session lifecycle（create/resume/expire/finalize）
- Interrupt support（busy session handling）
- Auto-continue（crash recovery）
- Stuck-loop protection

→ 這其實就是 Archestra 說的 "Agent Lifecycle Management"，只是規模不同（embedded vs K8s）。

### 2. MCP 完全是 client-side

Hermes 的 MCP servers 是透過 `native-mcp` skill 在 per-session 層級連接的。Gateway 不知道 MCP 的存在。這表示：
- 每個 session 獨立 connect MCP servers
- 沒有 MCP registry / discovery
- 沒有 tool routing（哪個 agent 可以用哪個 MCP tool）

### 3. Option C (Hybrid) 的路徑很明確

之前的 convergence 筆記提了三條路：
- A: Hermes 自己長成 Gateway+Orchestrator → 重造輪子太多
- B: Hermes 串外部 Gateway → agent lifecycle 那層浪費
- **C: Hybrid — Gateway 在外，Orchestrator 在內** → ✅

現在看來 C 更自然了：
- **Hermes gateway 做**：agent lifecycle（cache, sessions, interrupts）+ messaging + kanban
- **ContextForge 做**：MCP federation + credential vault + observability
- **整合點**：把 `native-mcp` skill 的 MCP connection 改走 ContextForge，而不是直接 connect

具體來說：
```python
# 現狀：per-session MCP
AIAgent → native-mcp skill → subprocess MCP servers

# 可能的 hybrid：
AIAgent → native-mcp skill → ContextForge (MCP proxy) → MCP servers
                                      ↑
                              credential vaulting
                              rate limiting
                              audit logging
```

---

## Open Questions

1. **ContextForge 的 PyPI package 實際能用嗎？** — 上次筆記提到它 3.7K 星 + 7K tests。需要實際裝來試才知道是不是 demo。值得一個 SPIKE。

2. **Gateway-level MCP registry 的價值？** — 如果 MCP servers 是 gateway-level 註冊而非 per-session，好處是 shared connection pool + centralized credential，但代價是失去 per-session isolation。Hermes 的使用情境需要哪個？

3. **Archestra 的 CNCF 規格動向？** — 如果 MCP gateway 有標準 spec，Hermes 應該優先實作 spec 而非自己發明。需要追蹤。

---

## Worth Tracking

- **ContextForge integration feasibility**：Python + PyPI，同 stack。最有機會的整合對象。
- **Gateway agent cache architecture**：128-entry LRU + 1h TTL 的設計，就是 Archestra 說的 "agent lifecycle management" 的嵌入式版本。如果有人想做 Hermes 的 enterprise 版，這層是最該被升級的。
- **MCP client → gateway bridge**：目前 `native-mcp` skill 直接 subprocess call MCP servers。如果改成走一個 local MCP proxy（ContextForge sidecar），就是 hybrid 架構的 MVP。

