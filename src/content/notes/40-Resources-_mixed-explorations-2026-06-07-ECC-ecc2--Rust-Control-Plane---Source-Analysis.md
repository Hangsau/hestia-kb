---
_slug: 40-Resources-_mixed-explorations-2026-06-07-ECC-ecc2--Rust-Control-Plane---Source-Analysis
_vault_path: 40-Resources/_mixed/explorations/2026-06-07-ECC-ecc2--Rust-Control-Plane---Source-Analysis.md
title: ECC ecc2/ Rust Control Plane — Source Analysis
date: 2026-06-07
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- default
- ecc
- null
- pub
- rust
- score
- session
- src
- text
- tool
created: '2026-06-07'
updated: '2026-06-15'
status: budding
---

# ECC ecc2/ Rust Control Plane — Source Analysis

**探索日期**: 2026-06-07
**延續自**: `2026-06-07-ecc-deerflow-harness-exploration.md`

---

## 1. ecc2/ 是真實可用的 Alpha

ECC 2.0 的 Rust 控制平面已達 alpha 品質：可編譯、可本地測試、可用，但**不是 GA 發布**。

官方口徑：
> "treat as real code, alpha quality, valid to build and test locally"

Source: `ecc2/README.md`

---

## 2. 核心架構

```
Hermes (front door)
    ↓
ECC 2.0 control plane (ecc2/)
    ├── CLI: dashboard / start / sessions / status / stop / resume / daemon
    ├── SQLite-backed state store
    ├── Risk scoring engine
    ├── Worktree-aware session scaffolding
    └── Multi-session tracking
```

Source: `ecc2/README.md` + `ecc2/src/main.rs`

---

## 3. SQLite Schema — 關鍵 Table 設計

### sessions 表（核心狀態）
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    project TEXT NOT NULL DEFAULT '',
    task_group TEXT NOT NULL DEFAULT '',
    agent_type TEXT NOT NULL,
    harness TEXT NOT NULL DEFAULT 'unknown',
    state TEXT NOT NULL DEFAULT 'pending',
    pid INTEGER,
    worktree_path TEXT,
    worktree_branch TEXT,
    worktree_base TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    tool_calls INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    duration_secs INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_heartbeat_at TEXT NOT NULL
);
```

**觀察**：
- 包含完整 token 用量、cost_usd、tool_calls、files_changed — 支援完整成本追蹤
- `task_group` 支援分組（對應 WS-035 的 multi-agent session grouping）
- `worktree_path/branch/base` — 隔離的工作樹追蹤

### tool_log 表
每個 tool call 記錄：session_id、tool_name、input_summary、output_summary、duration_ms、**risk_score**

### context_graph 表
儲存 `ContextGraphEntity`、`ContextGraphRelation`、`ContextGraphObservation` — agent 的認知圖谱

### conflict_incidents 表
```rust
pub struct ConflictIncident {
    pub id: i64,
    pub conflict_key: String,
    pub path: String,
    pub first_session_id: String,
    pub second_session_id: String,
    pub active_session_id: String,
    pub paused_session_id: String,
    pub first_action: FileActivityAction,
    pub second_action: FileActivityAction,
    pub strategy: String,
    pub summary: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub resolved_at: Option<DateTime<Utc>>,
}
```
**觀察**：ECC 已有完整的衝突偵測機制——並非從零實作

### daemon_activity 表
追蹤 dispatch pass 的狀態，用於 `operator_escalation_required()` 判斷

Source: `ecc2/src/session/store.rs`

---

## 4. Risk Scoring Engine — 實作細節

位置：`ecc2/src/observability/mod.rs`

### 四因子評分模型
```rust
pub fn compute_risk(tool_name: &str, input: &str, thresholds: &RiskThresholds) -> RiskAssessment {
    // 1. base_tool_risk — 工具類型風險（file write > file read > search）
    let (base_score, base_reason) = base_tool_risk(&normalized_tool);

    // 2. assess_file_sensitivity — 檔案敏感性（config、credentials、system files）
    let (file_sensitivity_score, file_sensitivity_reason) = assess_file_sensitivity(&normalized_input);

    // 3. assess_blast_radius — 爆炸半徑（recursive delete、glob、**）
    let (blast_radius_score, blast_radius_reason) = assess_blast_radius(&normalized_input);

    // 4. assess_irreversibility — 不可逆性（rm、drop、destroy）
    let (irreversibility_score, irreversibility_reason) = assess_irreversibility(&normalized_input);

    // clamp 到 [0.0, 1.0]
    let score = score.clamp(0.0, 1.0);
    let suggested_action = SuggestedAction::from_score(score, thresholds);
}
```

### SuggestedAction 等級
```rust
pub enum SuggestedAction {
    Allow,               // 0 — 直接執行
    Review,              // 低風險 — 記錄後執行
    RequireConfirmation, // 中風險 — 需要操作者確認
    Block,               // 高風險 — 直接阻擋
}
```

### RiskThresholds（來自 config）
```rust
pub struct RiskThresholds {
    pub review: f64,      // 低於此 → Review
    pub confirm: f64,     // 低於此 → RequireConfirmation
    pub block: f64,       // 高於此 → Block
}
```

Source: `ecc2/src/observability/mod.rs`

---

## 5. Daemon Loop — 心跳與排程協調

位置：`ecc2/src/session/daemon.rs`

```rust
pub async fn run(db: StateStore, cfg: Config) -> Result<()> {
    resume_crashed_sessions(&db)?;  // 啟動時搶救崩潰的 session

    let heartbeat_interval = Duration::from_secs(cfg.heartbeat_interval_secs);
    loop {
        check_sessions(&db, &cfg)?;           // 心跳檢查
        maybe_run_due_schedules(&db, &cfg).await;   // 排程任務 dispatch
        maybe_run_remote_dispatch(&db, &cfg).await; // 遠端請求
        coordinate_backlog_cycle(&db, &cfg).await;   //  backlog 協調
        maybe_auto_merge_ready_worktrees(&db, &cfg).await; // 自動合併
        maybe_auto_prune_inactive_worktrees(&db, &cfg).await; // 自動清理

        time::sleep(heartbeat_interval).await;
    }
}
```

### 慢性飽和偵測（與 WS-035 高度相關）
```rust
pub fn operator_escalation_required(&self) -> bool {
    self.dispatch_cooloff_active()                    // cooloff 期間
        && self.chronic_saturation_streak >= 5        // 連續 5 次慢性飽和
        && self.last_rebalance_rerouted == 0           // rebalance 無效
}
```
**這是 ECC 的 operator escalation 觸發條件**——與 Talos 守護者角色的 escalation 需求高度共鳴。

Source: `ecc2/src/session/daemon.rs`

---

## 6. Hermes 啟發

### 直接支撐 WS-035 的具體設計

| WS-035 需求 | ecc2/ 實作 |
|---|---|
| Policy engine state store | SQLite (`StateStore::open()`) |
| Session lifecycle management | `sessions` table + `manager.rs` |
| Risk scoring | `observability/mod.rs` — 4-factor model |
| Tool call audit logging | `tool_log` table |
| Conflict detection | `conflict_incidents` table |
| Daemon heartbeat | `daemon.rs` loop with configurable interval |
| Worktree isolation | `worktree_path/branch/base` in sessions |
| Operator escalation | `operator_escalation_required()` |
| Cost tracking | `cost_usd`, `tokens_used`, `tool_calls` |
| Multi-session grouping | `task_group` column |

### 不可直接移植的部分
1. **Rust → Python**：Hermes 是 Python 專案，無法直接用 Rust crate。需要從 Rust 萃取設計，用 Python 實作。
2. **CLI framework**：ecc2 用 `clap`（Rust），Hermes 用自己的 cron/agent 架構
3. **TUI dashboard**：ecc2 有 terminal UI，Hermes 用 heartbeat/observer pattern

### 實作路徑建議（針對 WS-035）
1. **不需要從零實作 risk scoring** — 4-factor model 可以直接翻譯成 Python
2. **SQLite 是對的選擇** — Hermes 已有 `heartbeat/` package，改用 SQLite 而非 JSON state
3. **衝突偵測已有 ECC 實作** — 直接採用 `conflict_incidents` schema concept
4. **慢性飽和 streak 追蹤** — `daemon_activity` table 的設計適合追蹤 WS-035 的 escalation history

---

## 7. 未追蹤 Leads

- `ecc2/src/config.rs` — RiskThresholds 的具體數值（目前只看到 struct 定義，未看到預設值）
- `ecc2/src/session/manager.rs` — session lifecycle 完整狀態機
- `ecc2/src/comms/` — agent 通訊層實作
- ECC v2.0 GA timeline — alpha 何時變 stable？

## ✅ 本次探索完成
