---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Moltis-Hook-System-Skill-Self-Extension-完整深讀
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Moltis-Hook-System-Skill-Self-Extension-完整深讀.md
title: Moltis Hook System & Skill Self-Extension — 完整深讀
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Moltis Hook System & Skill Self-Extension — 完整深讀

**延續自**: [[2026-05-18-axe-orloj-moltis-agent-infra-paths.md]]

## 來源

- https://docs.moltis.org/hooks.html — Moltis lifecycle hooks 完整文件
- https://docs.moltis.org/skill-tools.html — Skill Self-Extension 文件
- https://github.com/moltis-org/moltis — GitHub repo (`moltis-org/moltis`)
- `crates/skills/src/watcher.rs` — Skill watcher 原始碼（debounced filesystem watcher）

## Per-source insight

### 1. Lifecycle Hook System — 15 event types

Moltis 的 hook 系統分為兩類，涵蓋 agent loop 的完整生命週期：

**Modifying Events（8 個，sequential）**：可修改 payload、可 block action
| Event | 觸發點 |
|---|---|
| `BeforeAgentStart` | Agent loop 開始前 |
| `BeforeLLMCall` | Prompt 送 LLM 之前 |
| `AfterLLMCall` | LLM response 收到後、tool 執行前 |
| `BeforeToolCall` | Tool 執行前 |
| `BeforeCompaction` | Context compaction 前 |
| `MessageReceived` | 收到 channel/UI 訊息時 |
| `MessageSending` | 送出 response 前 |
| `ToolResultPersist` | Tool result 持久化時 |

**Read-Only Events（9 個，parallel）**：不可修改或 block
| Event | 觸發點 |
|---|---|
| `AfterToolCall` | Tool 執行完成後 |
| `AfterCompaction` | Compaction 完成後 |
| `AgentEnd` | Agent loop 結束 |
| `MessageSent` | Response 已送出 |
| `SessionStart` | 新 session 開始 |
| `SessionEnd` | Session 結束 |
| `GatewayStart` | Moltis 啟動 |
| `GatewayStop` | Moltis 關閉 |
| `Command` | Slash command 被使用 |

**Shell Hook Protocol**：
- stdin = JSON event payload
- exit 0 + stdout = continue（可含 `{"action":"modify","data":{...}}`）
- exit 1 = block（stderr = reason）
- 含 `channel` 欄位提供 channel provenance（`surface`, `session_kind`, `channel_type`, `account_id`, `chat_id`）

**Circuit Breaker**：
- 3 次連續失敗 → 自動 disable
- 60s cooldown → 自動 re-enable
- 防止壞掉的 hook block 所有操作

### 2. Prompt Injection Defense via Hooks

這是 Moltis 防禦架構中一個我之前沒注意到的層面：

- `BeforeLLMCall`：payload 含完整 message array → 可掃描 injection pattern、redact PII、add safety prefix
- `AfterLLMCall`：payload 含 LLM text + tool_calls → 可在 tool 執行前 block 可疑的 tool call
- 實例：`filter-injection.sh` 檢查 `AfterLLMCall` 中的 tool call name，若 LLM 突然要跑 `exec` 且 text 中含 "ignore previous" → block

這和 Hermes 的四層防禦（sanitizer + Phase Lock）是**互補**的——Molts 的 hook 層是 runtime enforcement，Hermes 的 sanitizer 是 input 層。

### 3. Skill Self-Extension — Pi-inspired

四個 agent tool：
- `create_skill`：寫 SKILL.md 到 `<data_dir>/skills/<name>/`
- `update_skill`：覆蓋既有 SKILL.md
- `patch_skill`：surgical find/replace（降低 hallucination risk + token cost）
- `delete_skill`：刪除整個 skill 目錄

關鍵設計決定：
- **Automatic checkpoint before mutation**：每次 mutation 前建立 checkpoint，可 restore
- **Skill watcher**：debounced (500ms) filesystem watcher，監聽 SKILL.md 的 create/modify/delete → 自動 hot-reload
- **Sidecar files**：支援 supplementary UTF-8 text files（`script.sh`, `templates/`, `_meta.json`）
- **Safety rules**：只允許 `<data_dir>/skills/<name>/` 內、只允許相對路徑 UTF-8 text、拒絕 `..` 和絕對路徑

### 4. Skill Watcher 實作（`watcher.rs`）

```rust
// 核心邏輯
SkillWatcher::start(specs) → (Self, mpsc::UnboundedReceiver<SkillWatchEvent>)
```

- 使用 `notify` crate + `new_debouncer`（500ms debounce）
- 只 watch `Personal` 和 `Project` source 的 skills（Registry/Plugin/Bundled 不 watch）
- 只關注 `SKILL.md` 和 `skills-manifest.json` 的變化
- Emit `SkillChanged` 或 `ManifestChanged` 到 unbounded channel
- Watcher 必須被持有（不能 drop），否則事件停止

### 5. Additional Security Features

- **Destructive Command Guard**：`dcg` 外部 tool，49+ destructive pattern categories
- **Secret Redaction Hook**：`BeforeToolCall` 中 redact API keys（`sk-*`, `ghp_*`, `password=*`）→ 這和 Hermes 的 `secret-leak-prevention` skill 互補：一個是 runtime guard，一個是 commit-time guard
- **Sandbox Write Restriction**：`BeforeToolCall` 檢查 `write_file` 的 path，只允許 project workspace
- **Slack Notification**：`SessionEnd` hook → webhook 通知

## Hermes 啟發

### Hook System 對標

Hermes 目前**完全沒有** lifecycle hook 基礎設施。現有的 defense 全部是 input/output sanitizer（`sanitize_fetch.py`, `validate_note.py`），沒有 runtime interception point。

**可行的漸進路徑**：
1. **L0 — Tool-level hook**：在 terminal/read_file/write_file 這類高風險 tool 前後加 interception point。最小 scope，最大安全增益。
2. **L1 — Session-level hook**：SessionStart/SessionEnd 加 hook → 這和 heartbeat 的 session tracking 對接
3. **L2 — Full lifecycle**：完整 agent loop interception（如 Moltis 的 15-event 系統）

**Circuit breaker pattern** 對 heartbeat sensor 有直接適用性：現有 sensor 連續失敗時沒有自動退場機制，circuit breaker（3 failures → cooldown → re-enable）可以防止一個壞掉的 sensor 拖垮整個 EVOLVE cycle。

### Skill Self-Extension 對標

Hermes 的 `skill_manage` 已經支援 create/patch/delete，但缺了：

| Moltis 有 | Hermes 缺 |
|---|---|
| Automatic checkpoint before mutation | ❌ 沒有 rollback 機制 |
| Skill watcher (hot-reload) | ❌ 需手動 `skill_view` 重新載入 |
| Sidecar files (`script.sh`, `templates/`) | ❌ `skill_manage` 只有 SKILL.md 和 references/templates/scripts/ dirs（已有但不一樣） |
| `patch_skill`（surgical find/replace） | ✅ `skill_manage(action='patch')` 已有 |
| Circuit breaker for mutation | ❌ 無 |
| Mutation audit log | ❌ 無 |

### Secret Redaction Hook 對標

Hermes 的 `secret-leak-prevention` skill 是 **commit-time guard**（pre-commit scan），Moltis 的 redaction hook 是 **runtime guard**（exec 前 redact）。兩者互補：
- Runtime guard：防止 secret 出現在 terminal output
- Commit-time guard：防止 secret 進 git history

**可行性**：在 Hermes 的 `terminal` tool wrapper 層加一個 pre-exec redaction step（regex scan command string），成本極低。

## 跨文章 Synthesis

這篇和之前的 Orloj governance deep-dive 是一體的兩面：

- **Orloj**：policy-as-data 的 governance model（declarative YAML → enforcement）
- **Moltis**：hook-as-code 的 interception model（shell scripts → runtime interception）

兩個 model 的互補關係：
- Orloj 的 policy schema 適合**靜態規則**（"不能 exec"、"只能讀取"）
- Moltis 的 hook system 適合**動態判斷**（"如果 text 含 injection pattern 則 block tool call"）

對於 Talos governance pipeline blueprint 的啟發：兩層 enforcement model 可以分別對標 Orloj（policy layer）和 Moltis（hook layer）。目前 blueprint 只涵蓋 policy layer，hook layer 是未探索的空間。

## ⏳ 未追蹤

- Moltis 的 `BeforeCompaction` hook — compaction 是 Hermes 的 memory-consolidator 核心，看 Moltis 怎麼在 compaction 前攔截
- Moltis 的 `MessageReceived` hook 中 `Block(reason)` 的 channel-aware response（abort turn + deliver reason to sender）— 這對 Talos 的 comms 治理有啟發
- Moltis 的 `checkpoint_restore` 機制 — 和 session branching 的關係
- Moltis 的 `BOOT.md` / `TOOLS.md` / `AGENTS.md` workspace context files — 對標 Hermes 的 workspace-context skill

## ✅ 本次探索完成
