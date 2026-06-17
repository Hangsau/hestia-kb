---
_slug: 40-Resources-_mixed-explorations-2026-05-17-12-Factor-Agents---Endless-Toil---守護者視角的-Reliability-模式
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-12-Factor-Agents---Endless-Toil---守護者視角的-Reliability-模式.md
title: 12-Factor Agents + Endless Toil — 守護者視角的 Reliability 模式
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agents
- check
- code
- error
- evolve
- factor
- llm
- state
- talos
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# 12-Factor Agents + Endless Toil — 守護者視角的 Reliability 模式

**日期**: 2026-05-17 | **來源**: HN 自主探索
**標籤**: #reliability #self-healing #observability #code-quality #12-factor #talos
**延續自**: 無（新主題）

## Per-Source Insights

### 1. 12-Factor Agents — 生產級 LLM 應用的可靠性原則

**來源**: `github.com/humanlayer/12-factor-agents` | **475 pts** | 作者 Dex（HumanLayer）

核心論點：**好的 agents 不是 loop-until-done，而是大部分由 deterministic code 組成，LLM 只在關鍵點介入。**

> "Most of the products billing themselves as 'AI Agents' are not all that agentic. A lot of them are mostly deterministic code, with LLM steps sprinkled in at just the right points."

這和 Anthropic 的 "Building Effective Agents" 一致，但更具體地提出了 12 條可操作原則。

**Factor 8: Own Your Control Flow**（直接對應 Talos enforcement 層）
- 自建 control structures，不要依賴框架的 loop
- 關鍵：在 tool **selection** 和 tool **invocation** 之間插入 interrupt point
- 三種 pattern：sync continue（fetch data → 回到 LLM）、async break（請求人類核准 → 等 webhook）、high-stakes break（部署等危險操作 → 強制中斷）
- 對 Talos 的意義：這正是 Talos governance 的 enforcement 點——不是在 loop 外面監控，而是在 tool selection ↔ invocation 之間插入 policy check

**Factor 9: Compact Errors into Context Window**（直接對應 heartbeat self-healing）
- 核心：把 error 放回 context window，讓 LLM 自己修
- 防 spin-out：errorCounter 限制單一 tool 重試 ≤3 次
- 進階：不只放 raw error，可以重構 error representation、移除舊 events、壓縮 context
- 對 Talos 的意義：heartbeat EVOLVE 的 error handling 目前是 deterministic（category → severity → escalate），沒有讓 LLM 嘗試修復的環節。可以加一個 `_attempt_self_heal()` step：EVOLVE 發現 error → compact error + context → 問 LLM 怎麼修 → 執行修復 → 重試

**Factor 10: Small, Focused Agents**（Talos↔Hestia 架構驗證）
- 每個 agent 3-10 步驟，最多 20
- 小型 agent 的 context window 可控，LLM 表現穩定
- 範例：NotebookLM 團隊特意保持在模型能力邊界上操作
- 對 Talos 的意義：Talos（守護者）和 Hestia（建造者）的角色分離正是這個 pattern。未來新增 agent 時繼續保持這個原則

**Factor 12: Stateless Reducer**（持久化模式）
- Agent 應該是 `(state, event) → new_state` 的 reducer
- 狀態存在 DB，context window 從 DB rebuild
- 對 Talos 的意義：heartbeat state files 已經是這個模式（JSON state → EVOLVE → write new state），但 EVOLVE step 之間的 state 存在 memory 而非 file。更徹底的 stateless 化可讓 EVOLVE 跨 session 斷點續傳

**其他值得注意的 factors**：
- Factor 5: Unify execution state and business state（單一 state object）
- Factor 6: Launch/Pause/Resume with simple APIs（和 Factor 8 互補）

### 2. Endless Toil — Affective Observability

**來源**: `github.com/AndrewVos/endless-toil` | **216 pts** | 作者 AndrewVos

一個 code quality 的「情緒化 observability」工具：scan 程式碼 → 根據 heuristic 打分 → 播放人類呻吟聲。核心不是音效，而是那套 heuristic scanner。

**Scanner 的 10 個 patterns**（直接可移植到 EVOLVE code quality sensor）：

| Pattern | Regex | Weight | 說明 |
|---|---|---|---|
| debug logging | `console.log\|debugger\|print(\|println!\|fmt.Print\|dump(\|var_dump` | 1 | 遺留的 debug 輸出 |
| TODO/FIXME | `\b(TODO\|FIXME\|HACK\|XXX)\b` | 1 | 技術債標記 |
| ignored lint | `ts-ignore\|type:\s*ignore\|eslint-disable\|pylint:\s*disable\|rubocop:disable` | 2 | 關掉的 linter |
| explicit any | `:\s*any\b\|as\s+any\b\|Any\b` | 1 | TypeScript 型別規避 |
| dynamic execution | `\b(eval\|exec\|Function\s*(\|setTimeout\s*\(\s*['\"]\|setInterval\s*\(\s*['\"])` | 6 | eval/exec 等高風險 |
| shell execution | `\b(os\.system\|subprocess\.(Popen\|call\|run)\|child_process\.(exec\|spawn))` | 3 | subprocess 呼叫 |
| broad exception | `catch\s*\([^)]*\)\s*\{\|except\s+(Exception\|BaseException)?\s*:\|rescue\s+StandardError` | 2 | 過寬的異常捕獲 |
| empty catch | `catch\s*\([^)]*\)\s*\{\s*\}\|except[^\n:]*:\s*(pass)?\s*$` | 4 | 空的異常處理 |
| secret-shaped literal | `(?i)\b(api[_-]?key\|secret\|token\|password)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]` | 7 | 疑似 hardcoded secret |
| force unwrap | `(!\.\|!!\|unwrap\(\)\|expect(\|assert\s+False)` | 2 | 強制 unwrap |

**結構性信號**（非 regex）：
- File size > 800 lines: +5 pts | > 400: +3 pts
- Long lines (>140 chars): +1 per，max +5
- Nesting depth ≥7: +5 | ≥5: +3

**七級 escalation**：silence(0) → murmur(4) → groan(7) → moan(12) → wail(18) → howl(25) → shriek(32) → abyss(40)

**支援 34 種語言/格式**（`.py`, `.ts`, `.rs`, `.go`, `.java`, `.yaml`, `.md` 等），涵蓋 Hermes codebase 的主要語言。

## Hermes 啟發

### 1. EVOLVE Code Quality Sensor

Endless Toil 的 heuristic scanner 幾乎可以直接移植為 EVOLVE 的 `_check_code_quality()` sensor：
- 從 `heartbeat/` package 開始掃（Python + Markdown + YAML + Shell）
- 10 patterns + 3 structural signals → 加權評分
- 用現有的 severity escalation 框架（score ≥ 25 → warning，≥ 40 → critical）
- 不需 LLM（純 static analysis），成本為零
- 這比現有的 `_check_script_integrity()`（`ast.parse` syntax check）更全面——syntax check 只抓 broken code，code quality sensor 抓 technical debt + security smell

### 2. Tool-Level Interrupt Point（Factor 8 啟發）

Talos 的 governance 目前是 audit-only（觀察 → 報告）。12-factor Factor 8 給出了 enforcement 的正確插入點：**在 tool selection 和 tool invocation 之間**。

Hermes 的路徑：
```
LLM decides action → [Talos policy check] → tool executes → result back to LLM
```

現有 cron job `enabled_toolsets` 已經是 coarse-grained 的 tool 白名單，但缺少 per-action policy check（例：`patch` tool 只能改特定目錄的檔案）。Factor 8 的 interrupt pattern 可以在不改 gateway 的前提下實現——用一個 wrapper 在 tool call 前檢查 policy。

### 3. Self-Healing Loop for EVOLVE（Factor 9 啟發）

目前 EVOLVE 發現錯誤 → 記錄 → escalate。沒有修復環節（除了 autonomic 層的 REST action）。

可以加一個 opt-in 的 `_attempt_auto_fix()`：
```
EVOLVE finds error → categorize → if category in [CONFIG, TRANSIENT, DATA]:
  compact error + instructions → ask LLM for fix → validate → apply → re-run
```
限制：每個 fingerprint 每 24h 最多 self-heal 3 次，防止 spin-out。

### 4. Single-Agent Scope Boundary（Factor 10 驗證）

12-factor Factor 10 正式化了 Talos↔Hestia 的角色分離：
- Hestia：建造 + 探索（10-20 step agents，產出筆記/提案/code）
- Talos：守護 + 診斷（3-5 step agents，產出警報/修復/報告）

未來若新增 agent（如專門做 code review 的 Minos），保持 ≤10 step scope 和明確的 input/output contract。

## 跨文章 Synthesis

12-factor Agents 和 Endless Toil 從兩個方向匯聚到同一個結論：**reliability 來自 deterministic infrastructure，不是 smarter LLM**。

- 12-factor 的論點：production agents 是 80% deterministic code + 20% LLM。Factor 8-9-10 三連擊（control flow + error compacting + small scope）就是 agent reliability 的基礎設施。
- Endless Toil 的論點：code quality 不需要 LLM 判斷——10 個 regex + 3 個 structural metric，純靜態分析，零 token 成本。

對 Talos 的具體路徑：
1. **短期**：移植 Endless Toil scanner → EVOLVE `_check_code_quality()` sensor
2. **中期**：實作 Factor 9 style self-healing loop（error compact → LLM fix → retry）
3. **中期**：定義 tool invocation interrupt point（Factor 8），加 policy check wrapper
4. **長期**：全面 stateless reducer 化（Factor 12），讓 EVOLVE state 可跨 session 恢復

## ⏳ 未追蹤

- 12-factor Factor 3（Own Your Context Window）— context engineering 的具體技巧（compaction、pre-fetch、summarization strategy）。Heartbeat 已經用 context-distiller skill 做 compaction，可以對標 Factor 3 檢查是否有遺漏的最佳實踐。
- 12-factor Factor 5（Unify execution state and business state）— 單一 state object 的 schema 設計。Heartbeat state files 目前是多個 JSON 檔案分散管理，unified state 可能減少 race condition。
- 12-factor Factor 6（Launch/Pause/Resume）— durable execution 的 API 設計。Hermes cron jobs 目前沒有 pause/resume 機制（job 只有 enabled/disabled）。
- Endless Toil 的 secret-shaped literal pattern — 和 hermetic `secret-leak-prevention` skill 的差異。兩個都是 regex-based secret detection，可以 cross-reference 彼此的 pattern 庫。
- `npx/uvx create-12-factor-agent` — 12-factor 的 scaffolding CLI（還在 discussion 階段，尚未實作）。可能對 Hermes agent template 有參考。

## ✅ 本次探索完成

