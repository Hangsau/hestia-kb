---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-1700-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-1700-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: medium
title: MCP Gateway 不是銀彈：可靠性、狀態管理、與既有架構的隱性依賴
updated: '2026-06-15'
type: research
status: budding
---

# MCP Gateway 不是銀彈：可靠性、狀態管理、與既有架構的隱性依賴

**消化筆記**: 2026-05-13-mcp-gateway-architecture

這篇筆記正確地指出 MCP Gateway 是 agent 架構的「缺失層」，但筆記本身停在「gateway 解決 credential sprawl + observability black hole」的論述。把 gate 跟已消化的筆記並置後，浮現三個筆記自己沒說的模式：gateway 引入新的可靠性依賴、session 抽象在三個層次上收斂、以及 gateway 的安全宣稱在實際工具鏈中有更便宜的替代方案。

---

## Cross-Cutting Theme 1: Gateway Reliability 是 Gateway Architecture 的隱性前提

**支援筆記**: 2026-05-13-mcp-gateway-architecture, 2026-05-15-hermes-gateway-shutdown-postmortem

MCP Gateway 筆記把 gateway 定位為 observability 的解答——「unified logging of all tool calls across all agents」。但 gateway shutdown postmortem 暴露了一個沒被討論的前提：**gateway 本身就是最需要 observability 的元件**。

Postmortem 記錄的 drain timeout 事件（一個 session 卡住 516.6s，拖垮整個 gateway shutdown）是 gateway-as-single-point 的經典症狀。當你把所有 agent 的 tool calls 都 route 過同一個 gateway，gateway 的 reliability 變成 N 個 agents 的 reliability 乘數——gateway 掛掉 = N 個 agents 同時失去工具存取。

這形成一個自我指涉的困境：gateway 是為了解決 observability black hole，但 gateway 本身的 failure mode（dirty shutdown、session drain、state loss）會創造一個更大的 black hole。Postmortem 的解法（startup hook 自動診斷 + heartbeat escalation）其實就是 gateway 對自己的 observability layer——這正是 gateway 筆記說 gateway 應該為 agents 做的事，只是對象變成 gateway 自己。

**非顯然推論**：Gateway 的 observability 必須是 recursive——gateway monitor agents，但誰 monitor gateway？答案不是另一個 gateway（那會無限遞迴），而是**心電圖模式**：heartbeat 從外部定時 ping gateway + 在 gateway 內部埋 self-diagnosis hook。Postmortem 的 `_analyze_last_shutdown()` + `_scan_shutdown_health()` 就是這個模式的 prototype。任何 MCP gateway 部署（不管是 Hermes 自建還是串 ContextForge/Archestra）都需要這一層，否則 gateway 從「observability 解答」變成「observability 單點故障」。

**可行動下一步**: 把 gateway shutdown postmortem 的 auto-diagnosis 從「phase 4 design」推進到實作。Task 1-3 已經 fully specced（~170 行 code + tests），先用真實 gateway.log 跑一次 `parse_shutdown_sequence()` 驗證 regex 覆蓋率，然後合併進 gateway startup flow。這是 gateway 要長成 MCP proxy 之前的必要基礎建設——先確保 gateway 自己的 reliability observable，再談 routing 別人的 tools。

---

## Cross-Cutting Theme 2: Stateful Session 是三層架構的共同抽象

**支援筆記**: 2026-05-13-mcp-gateway-architecture, 2026-05-13-shepherd-a-runtime-substrate-for-meta-agents-with-formalized-execution-traces, 2026-05-14-hermes-staged-delegation-pattern

三篇筆記各自在談不同層次的東西：MCP Gateway 筆記談 infrastructure 層的 session-aware connection management；Shepherd 談 runtime 層的 fork/discard/replay execution traces；Staged Delegation 談 application 層的 gather-only subagent with partial state survival。

但放在一起看，三者描述的是**同一個抽象**——一個 stateful execution context 需要以下能力：

| 能力 | MCP Gateway 筆記 | Shepherd | Staged Delegation |
|------|-----------------|----------|-------------------|
| **狀態持久化** | "manages persistent bidirectional connections with context" | "Every action is a commit, every fork is a branch" | "timeout 也可接受（資料已寫入檔案）" |
| **失敗恢復** | （未提及 — 這是 gap） | "All past states are reachable via checkout" | "檔案中有部分資料，仍可合成" |
| **隔離邊界** | "connection pooling, not just request pooling" | "fork/discard/merge are the primitives" | "子代理 timeout → 不影響其他" |
| **跨 session replay** | （未提及） | "95%+ prompt-cache reuse on replay" | "主代理接手合成（讀 gather 檔案）" |

這個表的右下角是空缺的：**Hermes 目前有 application 層的 partial failure recovery（gather subagent timeout → 檔案還在），但沒有 infrastructure 層的 session replay**。Shepherd 的 fork/discard/merge 原語如果套用在 MCP gateway session 上，會讓 gateway 不只是「forward tool calls」，而是「fork 一個 session state、在 fork 上重試失敗的 tool call、merge 回去」——這直接解決 staged delegation 裡最煩人的問題：gather subagent 在第三個 API call timeout，前兩個 call 的結果要手動拼回來。

**非顯然推論**：與其把 gateway session、execution trace、subagent state 當成三個獨立功能實作，不如定義一個統一的 `Session` primitive，然後在三層各自 thin-wrap：

- **Infra 層**（gateway）：Session = 有 lifecyle 的 MCP connection pool，支援 snapshot/restore
- **Runtime 層**（delegate_task）：Session = subagent 的 execution context，支援 fork/merge
- **Application 層**（staged delegation）：Session = gather 檔案的 immutable checkpoint

這不是要實作 Shepherd 的全部（那需要 overlay FS，太重），而是取其原語：**fork 一個 session = copy 當前的 MCP connection state + context summary**，discard = 丟掉 fork，merge = 把 fork 裡的 side effects（寫入的檔案、API responses）合併回 parent。底層實作可以先用 git worktree（已有 WS-002）+ JSON snapshot（stdlib），不需要 overlay FS。

**可行動下一步**: 在 `delegate_task` 加入 `checkpoint` 參數。子代理每完成一個 tool call 自動 checkpoint（snapshot context + 寫入的檔案到 `/tmp/hermes_checkpoint_{task_id}/`）。若 timeout → 下一個 delegate 從最新 checkpoint resume，而非從頭開始。第一版 checkpoint 只需包含：(1) conversation messages (JSON)，(2) 已修改的檔案路徑清單，(3) 已完成的 API call results。不碰 filesystem overlay，純 JSON。這是 staged delegation success rate 從 ~60% 拉到 ~90% 的最小可行改動。

---

## Cross-Cutting Theme 3: Token Isolation 是 Gateway 安全敘事的「夠用就好」替代方案

**支援筆記**: 2026-05-13-mcp-gateway-architecture, 2026-05-15-mcpc--MCP-CLI---Token-Isolating-Proxy

MCP Gateway 筆記把 credential vaulting 列為 gateway 的核心價值命題：「API keys scattered across agent configs, impossible to rotate」「Lateral movement risk: One compromised agent exposes credentials for dozens of services」。論述方向是：你需要一個 centralized gateway 來 vault credentials。

但 mcpc 的 token-isolating proxy 模式提供了一個更輕的替代路徑：**不需要 centralized gateway，只需要一個 local proxy 擋在 agent 和 credential 之間**。mcpc 的 `--proxy` 做的事：人類 OAuth 一次 → proxy hold token → agent 透過 proxy 呼叫 API，永遠看不到 token。安全模型本質一樣（agent 拿不到 credential），但架構複雜度天差地遠：

| | MCP Gateway（centralized） | mcpc Proxy（per-session） |
|---|---|---|
| Credential 儲存 | 集中 vault | 人類 browser session / env var |
| 部署複雜度 | 需要跑一個 gateway service | `mcpc connect --proxy 8080` |
| Failure mode | 單點故障（gateway 掛 = 所有 agent 失能） | per-agent 獨立（一個 proxy 掛不影響其他） |
| Audit trail | 集中 logging | 分散在各 proxy log |
| 適用場景 | multi-agent production deployment | single-user Hermes |

**對 Hermes 而言**，目前的使用情境是 single-user、cron-driven、非 production。MCP Gateway 筆記提出的 centralized vault 是 over-engineered——mcpc 的 per-session proxy 模式更吻合實際需求。如果有一天 Hermes 需要在同一台機器上跑多個隔離的 agent identity（例如不同的 GitHub org token），mcpc 的 `@session_name` 模型（`@personal` vs `@work`）比 centralized gateway 更輕更直接。

**非顯然推論**：MCP Gateway 的安全論述假設了 enterprise-scale threat model（credential rotation、audit compliance、lateral movement）。但 Hermes 的威脅模型是「一個 agent 不小心把自己的 GitHub token 寫進 code 然後 commit」。對後者，mcpc proxy 的 token isolation（agent 永遠看不到 token）已經足夠。Gateway 的安全價值在 single-user scenario 是 diminishing returns——反而引入了 gateway 本身的 reliability risk（見 Theme 1）。

**可行動下一步**: 不追 MCP Gateway 的 centralized credential vaulting。改在 `native-mcp` 的 config 層加入 `credential_proxy` 選項：如果 MCP server 有 `auth: oauth` 標記 → 提示使用者先跑 `mcpc login <server>` → Hermes 透過 `mcpc connect --proxy` 啟動 per-session proxy → `native-mcp` 只跟 proxy 溝通。這是 ~30 行 config schema change + SKILL.md 更新，不需要任何 infrastructure change。時機：等 mcporter 或 mcpc 的 INSTALL 提案通過後一併做。

---

## 附帶發現：Gateway 筆記的「Open Questions」有兩個已有答案

MCP Gateway 筆記結尾的三個 open questions：

1. **「Does the Hermes gateway process already exist?」** → 答案在 gateway shutdown postmortem：有，就是 `hermes gateway run`（WebSocket/HTTP transport），而且它有自己的 failure mode（drain timeout）、有自己的 health check（heartbeat sensor）、正在加 auto-diagnosis。它不是 MCP proxy，但它是可以長成 MCP proxy 的基底。

2. **「Could we add an MCP proxy mode to the gateway?」** → 條件是：先完成 Theme 1 的 gateway reliability work（dirty shutdown diagnosis + heartbeat escalation），再談 proxy mode。在 gateway 還需要手動追 crash log 的階段加 proxy mode 是 technical debt。

3. **「How does this relate to kanban-orchestrator / subagent-driven-development?」** → 見 Theme 2：gateway session、subagent session、orchestrator task 是同一個 Session primitive 的三個視圖。先統一 Session 抽象，再決定 gateway 在 orchestrator 架構中的角色（是 transparent proxy 還是 active session manager）。
