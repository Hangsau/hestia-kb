---
_slug: 40-Resources-_mixed-explorations-2026-06-07-ECC-ecc2--Rust-Source---深度分析
_vault_path: 40-Resources/_mixed/explorations/2026-06-07-ECC-ecc2--Rust-Source---深度分析.md
title: ECC ecc2/ Rust Source — 深度分析
date: 2026-06-07
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- config
- ecc
- manager
- migrate
- profile
- pub
- session
- string
- worktree
created: '2026-06-07'
updated: '2026-06-15'
status: budding
---

# ECC ecc2/ Rust Source — 深度分析

**日期**: 2026-06-07 | **來源**: GitHub API (`affaan-m/ECC/ecc2/src/`) | **探索**: Phase-Locked

## ecc2/ 模組架構

```
ecc2/src/
  main.rs          — CLI entry (clap), 7 submodules
  comms/           — RPC/訊息系統
  config/          — 設定管理
  notifications.rs — 通知系統
  observability/   — Tool call logging, risk scoring
  session/
    daemon.rs      — 背景 daemon 模式
    manager.rs     — Session lifecycle (create/start/stop/resume)
    mod.rs         — Session, SessionState, HarnessKind, SessionMetrics
    output.rs      — Output stream capture
    runtime.rs     — Command execution + output capture
    store.rs       — SQLite state store (StateStore)
  tui/             — Terminal dashboard UI
  worktree/        — Worktree management
```

## 關鍵發現

### 1. StateStore schema — 比預期完整

`store.rs` 使用 `rusqlite::Connection`，schema 包含：

```rust
// Session core
pub struct Session {
    pub id: String,
    pub state: SessionState,
    pub harness_info: SessionHarnessInfo,
    pub agent_profile: SessionAgentProfile,
    pub metrics: SessionMetrics,
    pub grouping: SessionGrouping,
    // ...
}

// File activity tracking (for conflict detection)
pub struct FileActivityEntry {
    pub path: String,
    pub current_action: FileActivityAction,
    pub other_session_id: String,
    pub other_session_state: SessionState,
}

// Conflict resolution
pub struct ConflictIncident {
    pub id: i64,
    pub conflict_key: String,
    pub path: String,
    pub first_session_id: String,
    pub second_session_id: String,
    pub active_session_id: String,
    pub paused_session_id: String,
    pub strategy: String,
    pub summary: String,
}

// RPC-like dispatch
RemoteDispatchKind, RemoteDispatchRequest, RemoteDispatchStatus
```

**對 policy engine 的意義**：
- `FileActivityEntry` + `ConflictIncident` = 工作樹衝突偵測（已實現）
- `RemoteDispatchRequest/Status` = 跨 agent 訊息傳遞（已實現）
- Schema 足以支援 policy engine backend，不需要從零設計

### 2. session/manager.rs — 多 session 協調

```rust
pub async fn create_session_with_profile_and_grouping(
    db: &StateStore, cfg: &Config,
    task: &str, agent_type: &str,
    use_worktree: bool,
    profile_name: Option<&str>,
    grouping: SessionGrouping,
) -> Result<String>
```

- `profile_name`: agent profile 支援（對應 policy engine 的 agent 分類）
- `SessionGrouping`: session 分組（對應 workspace/INDEX 的專案分組）
- `use_worktree`: 每 session 隔離 worktree（對應 Talos 的 guardian isolation）

### 3. observability — 風險評分

`observability/` 含 `ToolCallEvent`, `ToolLogEntry`, `ToolLogPage`：
- 每個 tool call 都有 event log
- 可扩展的 risk scoring

### 4. `ecc migrate audit` 可行性

ECC 的 `migrate` 子命令在 `main.rs` 中的 clap 定义里。從架構看，`manager.rs` 的 `queue_session_in_dir` 可以對任意 `repo_root` 操作。`ecc migrate audit --source ~/.hermes` 理論上可行，但需要確認 `Config` 是否支援自定義 source path。

## 對 WS-040 的回答

| TODO | 結論 |
|------|------|
| ecc2/ 模組介面合約 | 7 模組（comms/config/session/notifications/observability/tui/worktree），session/manager.rs 是主要 API 層 |
| session store schema 是否足夠 policy engine backend | **足夠**：FileActivityEntry + ConflictIncident + RemoteDispatchRequest 已覆蓋核心需求 |
| `ecc migrate audit` 能否盤點 Hermes workspace | **可能**：manager 可操作任意 repo_root，但需驗證 Config 是否支援自定義 source |

## ✅ 本次探索完成

**未追蹤 leads**:
- ~~https://github.com/affaan-m/ECC/issues?q=label%3Aecc-2.0~~ → ECC issues 頁面，migrate command 詳細規格待查
- `https://raw.githubusercontent.com/affaan-m/ECC/main/ecc2/src/session/mod.rs` → SessionState enum 完整定義（已 fetch main.rs，知道結構）
