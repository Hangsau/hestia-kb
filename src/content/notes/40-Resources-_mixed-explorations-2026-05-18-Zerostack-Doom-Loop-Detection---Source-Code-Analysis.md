---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Zerostack-Doom-Loop-Detection---Source-Code-Analysis
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Zerostack-Doom-Loop-Detection---Source-Code-Analysis.md
title: Zerostack Doom-Loop Detection — Source Code Analysis
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- call
- calls
- doom
- hermes
- input
- loop
- recent
- self
- tool
- window
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

---
date: 2026-05-18
source: [[2026-05-18-zerostack-doom-loop-code.md]]
related_proposal: [[doom-loop-detection-sensor.md]] (WS-018)
---

# Zerostack Doom-Loop Detection — Source Code Analysis

**延續自**: [[2026-05-18-zerostack-doom-loop-code.md]] 的未追蹤 leads

## 原始碼位置

`src/permission/checker.rs` — `PermissionChecker` struct

## 核心實作

```rust
// 1. 狀態：16-call sliding window（VecDeque，capacity = 16）
recent_calls: VecDeque<(String, String)>,  // (tool_name, input_string)

// 2. 追蹤：每次 non-Deny 的 tool call 後 push
fn track_doom_loop(&mut self, tool: &str, input: &str) {
    self.recent_calls.push_back((tool.to_string(), input.to_string()));
    if self.recent_calls.len() > 16 {
        self.recent_calls.pop_front();  // ring buffer
    }
}

// 3. 偵測：window 內 identical (tool, input) >= 3 次
fn is_doom_loop(&self, tool: &str, input: &str) -> bool {
    let count = self.recent_calls.iter()
        .filter(|(t, i)| t == tool && i == input)
        .count();
    count >= 3
}
```

## 關鍵設計決策

| 面向 | Zerostack 選擇 | 對 Hermes 的啟示 |
|------|---------------|-----------------|
| **比對方式** | 精確字串比對 (`tool` + `input`) | 最簡單、零 FP，但漏掉「參數微調的 loop」 |
| **Window size** | 16 calls（hardcoded） | Hermes 可以設為最近 N sessions 或 24h |
| **Threshold** | 3 次 | 合理；heartbeat 建議用 3+ 次 |
| **觸發時機** | 僅在 `action != Deny` 時追蹤 | Deny 的 call 不計入（避免 deny-storm 被誤判為 loop） |
| **可配置動作** | `doom_loop_action: Deny / Ask / Allow` | Hermes 可直接設為 `warning` 或 `critical` severity |

## 移植到 Hermes 的具體路徑

Proposal WS-018 要求「實作 `_check_loop_detection` + EVOLVE step + 測試」。根據原始碼分析，實作可大幅簡化：

1. **資料來源**：讀取 `~/.hermes/sessions/` 的 session JSON（metadata 層已有 tool call 序列）
2. **偵測邏輯**：
   - 對每個 session，取最近 N 個 tool calls
   - 用 `(tool_name, arguments_json)` 當 key
   - `collections.Counter` 統計，任一 key >= 3 → 報 `LOOP:{session_id}:{tool_name}(×N)`
3. **Severity**：`TRANSIENT`（首次 warning，連續 → critical）— 與提案一致
4. **測試**：mock session JSON，塞重複 tool calls，確認 threshold 觸發

## 與提案的對照

- 提案問「counter-based or pattern-based?」→ **counter-based，精確字串匹配**
- 提案問「sliding window?」→ **是，16-call ring buffer**
- 提案問「掃描範圍？」→ 原始碼是 runtime window，Hermes 建議用「最近 24h sessions」或「最近 5 sessions」

## ✅ 本次探索完成

回答了 WS-018 提案的所有未確認技術細節，實作路徑已清晰。

