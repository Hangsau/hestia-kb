---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Moltis-Lifecycle-Hooks---Session-Branching-Checkpoints---Her
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Moltis-Lifecycle-Hooks---Session-Branching-Checkpoints---Her.md
title: Moltis Lifecycle Hooks + Session Branching/Checkpoints — Hermes 對標
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- branching
- checkpoints
- fork
- heartbeat
- hermes
- hooks
- moltis
- sensor
- session
- skill
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# Moltis Lifecycle Hooks + Session Branching/Checkpoints — Hermes 對標

**延續自**: [[2026-05-18-moltis-hooks-self-extending-skills.md]]

## 來源

- https://docs.moltis.org/hooks.html — 完整 hooks 參考
- https://docs.moltis.org/session-branching — Session forking 機制
- https://docs.moltis.org/checkpoints — Per-turn 自動快照與 rollback

## Per-source Insight

### 1. Hook System — 架構精華

**Modifying vs Read-Only 分離**是核心設計決定：
- Modifying（8 個）：sequential execution，可 block 可 modify payload
- Read-Only（9 個）：parallel execution，不可 block

**Shell Hook Protocol**（stdin/stdout + exit code）：
- `exit 0` + empty stdout = continue
- `exit 0` + `{"action":"modify","data":{...}}` = replace payload data
- `exit 1` + stderr = block

**Circuit Breaker**：3 consecutive failures → disable，60s cooldown → auto re-enable。防止壞掉的 hook block 整個系統。

**Channel Provenance**：所有 channel-bound events 都含 `surface`/`session_kind`/`channel_type`/`account_id`/`chat_id`，讓 hook 能針對不同 channel 做差異化策略。

### 2. Session Branching — Fork 模型

**繼承關係**：
```
parent ──fork_point:N──▶ forked_session
```
- Inherited: messages, model, project, agent ID, MCP disabled flag
- NOT inherited: worktree branch, sandbox settings, channel binding

**Parent-child storage**：`parent_session_key` + `fork_point` 存 SQLite，驅動 sidebar 樹狀顯示。

**獨立性**：forked session 和 parent 完全獨立，之後各自演化不同步。

**`branch_session` tool**：agent 可程式化 fork，指定 `fork_point`（message index）和 label。

### 3. Checkpoints — Per-turn 快照

**觸發時機**：每次 file-mutating tool call 前（Write, Edit, MultiEdit）+ skill/memory mutations。

**範圍**：
- `create_skill`, `update_skill`, `delete_skill`, `write_skill_files`
- `memory_save`, `memory_forget`, `memory_delete`
- Silent pre-compaction memory flush

**儲存**：`~/.moltis/checkpoints/`，每個 turn 一組，manifest-backed snapshot。

**Cleanup**：超過 500 個時自動刪除最舊的 20%。

**Tool surface**：`checkpoints_list` + `checkpoint_restore`，每個 mutation result 帶 `checkpointId` 方便直接 restore。

**與 git 的區別**：checkpoint 是內部 safety artifact，不碰 user 的 git history。

## Hermes 啟發

### 1. Hook Architecture 三層漸進路徑

| Layer | 範圍 | 實作複雜度 | 安全增益 |
|-------|------|-----------|---------|
| **L0 — Tool-level** | terminal/read_file/write_file 前后 | 低 | 高 |
| **L1 — Session-level** | SessionStart/SessionEnd | 中 | 中 |
| **L2 — Full lifecycle** | 15-event model | 高 | 完整 |

**L0 最值得先做**：Hermes 的 `terminal` tool 是最高風險操作，在 exec 前加 pre-exec redaction（regex scan command string）成本極低。可以從 `secret-leak-prevention` skill 的 commit-time guard 延伸到 runtime guard，兩者互補。

**L1 的 heartbeat 價值**：SessionStart/SessionEnd hook 可以和 `heartbeat_v2.py` 的 session tracking 整合——每次 session start 做 snapshot，session end 記錄 duration/error，全程不需要 LLM 介入。

### 2. Session Branching — Hermes 的缺口

Hermes 沒有任何 session fork 等效物。當前架構中：
- `delegate_task` 開新的 subagent，但那是獨立的 process，不繼承 conversation history
- 沒有 `/fork` 或等效操作讓使用者experiment without losing context
- 沒有 parent-child session 關係追蹤

**實際價值**：
- 使用者想「try a different approach」時不用開新 session 然後手動 copy context
- `/fork` 在 UI 層很直覺，channel（Telegram、Discord）都可以用
- 對於 dangerous 操作（`rm -rf`、`exec` with destructive commands），fork 提供免費的安全網

**對 heartbeat 的應用**：每次 EVOLVE 前可以自動 fork session？→ 實驗性的，不確定價值。

### 3. Checkpoint/Rollback — Hermes 的缺口

Hermes 沒有任何等效物。Destructive 操作（`write_file`、`terminal rm`）是永久性的，沒有 automatic snapshot。

**Hot reload for skills** 的價值：Moltis 的 skill watcher（debounced 500ms）在 SKILL.md 變化時自動 reload。Hermes 需要手動 `skill_view` 重新載入——這是個真實的 ergonomics 痛點。

**checkpoint_restore 的 mutation 追蹤**：每個 mutation result 帶 `checkpointId`。Hermes 的 `heartbeat_v2.py` 如果支援 rollback，會是強大的 safety net。

### 4. Circuit Breaker → Heartbeat Sensor 應用

Moltis 的 circuit breaker pattern 可以直接應用於 heartbeat EVOLVE 的 sensor 連續失敗：

```
3 consecutive failures → disable sensor
60s cooldown → re-enable
```

目前 `heartbeat_v2.py` 的 sensor 連續失敗時沒有自動退場機制——一個壞掉的 sensor（如 `check_workspace_sync()` 遇到 drift 就一直失敗）會拖累整個 EVOLVE cycle。

**具體改法**（如果要做）：
- 在 `heartbeat/scoring.py` 或 `heartbeat/actions.py` 對每個 sensor track failure count
- 3 次失敗後在 state file 標記 `sensor_disabled`
- 60s 後自動 re-enable
- EVOLVE output 報告 `sensor X disabled (circuit open)`

## 跨文章 Synthesis

Moltis 的三個系統（Hooks / Branching / Checkpoints）構成一個完整的安全+可逆性架構：

```
Hooks = interception layer (runtime policy enforcement)
Checkpoints = mutation safety net (automatic rollback)
Branching = experiment boundary (diverging without cost)
```

Hermes 目前只有 Hooks 概念中的部分（L0 tool-level 有 `sanitize_fetch.py`），其他兩個系統完全缺失。這個差距是架構性的，不是單一功能差距。

對於 **Talos governance pipeline blueprint** 的啟發：
- Policy layer → Orloj 的 declarative YAML（靜態規則）
- Runtime interception → Moltis hooks（動態判斷）
- Rollback → Checkpoints（mutation safety）
- Branching → 使用者 experiment without fear

## ⏳ 未追蹤

- Moltis 的 `AgentPresets` — 有沒有類似 system prompt version management？
- Moltis 的 `ToolPolicy` — 和 Orloj policy schema 的功能覆蓋差異
- Moltis 的 `session-memory` surface — Hermes 的 session memory 怎麼實作？

## ✅ 本次探索完成

