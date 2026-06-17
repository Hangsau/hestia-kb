---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Ralphex---Stalemate-Detection---Autonomous-Plan-Execution
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Ralphex---Stalemate-Detection---Autonomous-Plan-Execution.md
title: Ralphex — Stalemate Detection & Autonomous Plan Execution
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- heartbeat
- hermes
- loop
- plan
- ralph
- ralphex
- review
- stalemate
- task
- worktree
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Ralphex — Stalemate Detection & Autonomous Plan Execution

**日期**: 2026-05-17 | **來源**: [[2026-05-17-ralph-wiggum-autonomous-loops]] 未追蹤 lead
**延續自**: [[2026-05-17-ralph-wiggum-autonomous-loops]]
**標籤**: #autonomous-agents #loop-pattern #stalemate-detection #plan-execution

## Per-Source Insight

### Ralphex: Extended Ralph Loop for Autonomous AI Plan Execution

**基礎**：ralphex = standalone CLI，無需 IDE plugin 或雲端服務，只要 Claude Code + 一個 binary。目標：讓複雜 multi-task feature 在無人值守下完成。

**核心机制（相較原始 Ralph）**：
- Plan file 格式（`### Task N:` + `- [ ]` checkboxes）= explicit completion criteria
- 每次 task 在 fresh Claude Code session 執行（context 不累積）
- 驗證命令（test、linter）跑在每個 task 完成後
- Git branch per plan → commits after each task → 不怕中斷

**Stalemate Detection 演算法**（關鍵未追蹤 lead 的答案）：
```
The loop terminates when:
  1. all issues resolved
  2. max iterations reached
  3. stalemate detected (via --review-patience)
  4. manual break via Ctrl+\ (SIGQUIT)
```

**Stalemate 觸發條件**：
- `--review-patience=N`：當 external tool（codex review）和 Claude 連續 N 輪都沒有新增 commit 或 working tree change，終止
- 本質：連續 N 輪雙方都「沒有進展」，就停止浪費 tokens

**Phase 1 vs Phase 2 的差異**：
- Task phase：Ctrl+\ 暫停（不是終止），讓你 mid-run 編輯 plan 後 retry
- Review phase：Ctrl+\ 立即終止 external review loop

**Multi-phase review pipeline**（5 agents → codex → 2 agents）：
- 不是簡單的「code review」，是獨立的 LLM agents 鍊
- External tool 可以是 codex（預設）或其他

**其他值得注意的設計**：
- `--serve`：browser dashboard，streaming output + timestamps + colors
- `--worktree`：多個 plan 在 parallel worktrees 執行（相當於 Hermes 的 worktree-subagent-isolation）
- `--wait=1h`：rate limit 時等 1 小時而非直接退出（vs Ralph 直接 fail）
- Notifications：Telegram/Email/Slack/Webhook/custom script（completes Heartbeat 的 notify pipeline）

## Hermes 啟發

### 1. Stalemate detection 填補 Heartbeat 的缺口

Ralph Wiggum 筆記提到「如何偵測 loop 已經不可能收斂」是未追蹤的 lead。ralphex 的答案：
- **連續 N 輪無 progress = 放棄**，不是无限retry
- 參數 `--review-patience` 是 user-configurable patience threshold
- 對 Hermes Heartbeat 的意義：REPAIR action 目前沒有「試 N 次都失敗就放棄」的機制

**具體應用**：heartbeat 的 `check_gateway_health()` REPAIR：
```
current: gateway down → restart → check again
missing: gateway down → restart → still down → restart → still down → stalemate → escalate/alert
```
ralphex 的 patience counter pattern 可以在 REPAIR 加入：連續 3 次 REPAIR 都失敗 → 停止 retry → severity escalation → Telegram（而非一直重啟）。

### 2. Plan file as explicit completion criteria

ralphex 的 plan file = structured task list + validation commands：
```
## Validation Commands
- `go test ./...`

### Task 1: Implement feature
- [ ] Add the new functionality
- [ ] Add tests
```

Heartbeat 目前只有隱性 completion criteria（EVOLVE clean）。如果需要讓人類定義「什麼情況算完成」：
- REPAIR：gateway responds 200 + pytest canary passes
- EXPLORE：筆記寫完 + synthesis 完成 + 未追蹤 leads 列出
- PROPOSE：提案檔存在 + workspace INDEX 同步

**但這和 Heartbeat 的「自主」設計有 tension**：Explicit completion criteria 適合 human-in-the-loop，Ralph/Wiggum 都是人定義目標讓 agent 執行。Heartbeat 的設計是「自己判斷什麼值得做」，不適合預先定義完成標準。

ralphex 的 plan file 更適合 `hermes-otp-human-in-the-loop` 之類的提案。

### 3. Worktree isolation 是實用設計

ralphex 的 `--worktree` flag 讓多個 plan 在 parallel git worktrees 執行，解決了「獨立 context window」的物理問題。

Hermes 的 `worktree-subagent-isolation` 提案（WS-014）正是同一個問題。ralphex 的 `--worktree` 實作細節（flag + path handling）可作為參考。

### 4. `--wait` on rate limit 的 graceful degradation

ralphex 的 `--wait=1h` 讓 rate limit 發生時「等一小時再試」而非直接放棄。這比 Ralph 的 immediate fail 更 user-friendly。

Heartbeat 的 TRANSIENT errors（rate limit、503）目前會怎麼處理？需要看 `heartbeat/actions.py` 的 REPAIR 實作。但 ralphex 的 `--wait` 模式暗示：遇到 rate limit → sleep → retry，而不是 fail。

## 未追蹤

- ralphex 的 5-agent review pipeline 詳細運作（`--external-only` mode）— review agents 如何選擇？
- `--serve` web dashboard 的實作（Python? Go?），是否適合嵌入 Hermes 的 TUI
- Geoffrey Huntley "Everything is a Ralph Loop" (Jan 2026) 的具體內容

## ✅ 本次探索完成

