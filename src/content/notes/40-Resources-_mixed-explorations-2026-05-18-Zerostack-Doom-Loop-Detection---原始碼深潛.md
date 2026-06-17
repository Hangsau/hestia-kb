---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Zerostack-Doom-Loop-Detection---原始碼深潛
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Zerostack-Doom-Loop-Detection---原始碼深潛.md
title: Zerostack Doom-Loop Detection — 原始碼深潛
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- detection
- doom
- hermes
- input
- loop
- permission
- sensor
- session
- tool
- zerostack
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

# Zerostack Doom-Loop Detection — 原始碼深潛

**延續自**: [[2026-05-18-zerostack-semble.md]]

## 來源

- Zerostack `src/permission/checker.rs` — doom-loop detection 完整實作
- Zerostack `src/permission/mod.rs` — PermissionConfig schema
- Zerostack `CONFIG.md` — config 文件

## Per-source insight

### Zerostack 的 doom-loop detection 實作（checker.rs）

**核心資料結構**：
```rust
recent_calls: VecDeque<(String, String)>,  // capacity=16
doom_loop_action: Action,                    // configurable: Allow/Ask/Deny
```

**偵測邏輯**（`is_doom_loop`）：
```rust
fn is_doom_loop(&self, tool: &str, input: &str) -> bool {
    let count = self.recent_calls
        .iter()
        .filter(|(t, i)| t == tool && i == input)
        .count();
    count >= 3
}
```

**觸發流程**：
1. 每次 `check()` / `check_path()` 通過 permission check 後 → `track_doom_loop(tool, input)`
2. `track_doom_loop` 將 `(tool, input)` push 到 `VecDeque`，超過 16 則 pop_front
3. 立刻呼叫 `is_doom_loop` — 若同一個 `(tool, input)` 在 window 內出現 ≥3 次 → 觸發
4. 根據 `doom_loop_action` 回傳 `Denied` / `Ask` / `Allow`

**關鍵設計決策**：

| 維度 | Zerostack 選擇 | 理由 |
|------|---------------|------|
| 比對粒度 | 完整 `(tool, input)` pair | 同 tool 不同 input 不算 loop（如 `write a.rs` → `write b.rs`） |
| 窗口大小 | 16 entries | 超過 16 次 call 後舊記錄自動淘汰，防止 stale match |
| 閾值 | 3 次 | 第一次是正常 call，第二次是重試，第三次就是 loop |
| 偵測時機 | Inline（每次 tool call 時） | 在下一次執行前攔截，不做事後分析 |
| 反應 | Deny / Ask / Allow（可設定） | 預設 Ask（給使用者介入機會） |
| 防禦位置 | Permission layer | 和 permission rules 共用同一 check path |

**Config 格式**：
```json
{
  "permission": {
    "doom_loop": "deny"  // allow | ask | deny
  }
}
```

### 與 Hermes doom-loop-detection-sensor 提案對標

現有提案（`proposals/doom-loop-detection-sensor.md`）的設計方向：

| 維度 | Zerostack（inline） | Hermes 提案（sensor） |
|------|---------------------|----------------------|
| 偵測層級 | Permission layer（每次 tool call） | EVOLVE step（事後掃描 session logs） |
| 時機 | 即時攔截 | 每 15-30 min 批次檢查 |
| 數據源 | 記憶體內 VecDeque | Session log 檔案 |
| 反應 | Deny tool call | Error report → severity escalation |
| 適合 Hermes？ | ❌ Hermes 沒有 native permission checker | ✅ 適合 heartbeat 自我監控架構 |

**Hermes 提案的實作注意事項**（從 Zerostack 學到的）：

1. **`(tool, input)` pair 是正確的比對粒度**。不能只比 tool name，否則 `write a.rs` 和 `write b.rs` 會被誤判為 loop。但 Hermes 的 `input` 可能很長（如 terminal command），需 normalize（strip whitespace, truncate 到合理長度）。

2. **窗口大小的 tradeoff**：16 是 Zerostack 的 inline 窗口。Hermes sensor 掃描 session log 時窗口應更大（如最近 50-100 次 tool call），因為 sensor 是批次跑而非即時。但太大會降低 sensitivity。

3. **Session boundary 是關鍵**：Hermes 的 session log 橫跨多個 session。同一 session 內 3+ 次重複 call 是 doom loop；跨 session 的重複可能是正常任務。Sensor 必須以 session 為單位重置 counter。

4. **不要只偵測 `tool` 重複，要偵測 pattern**：Hermes 的 doom loop 可能表現為「同一 task 反覆失敗後重試不同 tool」而非「同一 tool call」。Zerostack 的純 counter 無法偵測這種模式。Hermes sensor 可以加第二層：如果同一 session 內連續 N 次 `tool call → error/failure → retry with different tool`，也是 doom loop。

### Hermes 啟發

1. **Zerostack 的 `doom_loop_action` 三態設計值得借鏡**：Hermes sensor 也可以分級反應 — Allow（記錄但不阻擋）、Ask（發 warning）、Deny（觸發 severity escalation + Telegram 通知）。這對應到 severity 系統中的 info/warning/critical。

2. **Inline vs sensor 不是互斥的**：長期來看，Hermes 可以在 gateway 層（如果有）加入 inline doom-loop detection（類似 Zerostack），而 heartbeat sensor 做為事後補充。雙層防禦。

3. **Config schema 的 ergonomics**：Zerostack 用 `"doom_loop": "deny"` 一個 key 搞定，比分散在多處設定更直覺。Hermes ISSUES.md 的 known-issue 管理也可以用類似的簡潔 config（而非目前的 verbose YAML）。

## 跨文章 synthesis

Zerostack 的 doom-loop detection 和我們前期的 sandboxing/guardian 研究是同一條線：
- **Sandbox（L3）**：bubblewrap 隔離，防的是 bash command 的破壞力
- **Permission checker**：glob-based 白名單，防的是 unauthorized tool access
- **Doom-loop detection**：counter-based 重複檢測，防的是 agent 自我死循環

三者形成 Rust agent 的 defense-in-depth。對比 Hermes：
- Sandbox → 沒有（靠 filesystem 權限和 venv 隔離）
- Permission checker → 沒有（cron jobs 靠 `enabled_toolsets` 欄位做 coarse-grained 限制）
- Doom-loop detection → 提案階段

**Gap analysis**：Hermes 的工具矩陣比 Zerostack 更複雜（128 skills, 10+ cron jobs），但防禦層反而更薄。這是 Talos governance pipeline 要解決的問題。

## ⏳ 未追蹤

- Zerostack session allowlist persistence — `load_session_allowlist()` 從哪裡讀？檔案格式？
- Zerostack pattern matching engine（`src/permission/pattern.rs`）— glob pattern 的完整語法（`**` recursion? brace expansion?）
- `doom_loop` 的 `Ask` 模式在使用者離線時的行為 — 會 timeout 轉 deny 還是永久卡住？
- 將 Zerostack 的 doom-loop 演算法移植到 Hermes heartbeat sensor 的具體 diff（見 `proposals/doom-loop-detection-sensor.md`）

## ✅ 本次探索完成

