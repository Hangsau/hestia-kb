---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Statewright-用狀態機給-AI-Agent-上枷鎖
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Statewright-用狀態機給-AI-Agent-上枷鎖.md
title: Statewright：用狀態機給 AI Agent 上枷鎖
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- cache
- code
- fail
- machine
- phase
- state
- statewright
- tool
- tools
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Statewright：用狀態機給 AI Agent 上枷鎖

**日期**: 2026-05-14 | **來源**: [HN Show HN](https://news.ycombinator.com/item?id=48108778) (115 pts, 53 comments) | **Repo**: [statewright/statewright](https://github.com/statewright/statewright) (260★)

> *"Agents are suggestions, states are laws."*

## 核心命題

與其讓 agent 在 40+ tools 的開放空間中迷失，不如用**確定性狀態機**約束每個 phase 可用什麼 tool。不是讓模型更大，是讓問題更小。

```
傳統: 模型 × 40 tools × open-ended prompt → 讀檔地獄、工具亂叫
Statewright: planning(Read/Grep/Glob) → implementing(Edit/Write) → testing(Bash:pytest only)
```

## 架構

- **Rust 核心引擎** (`crates/engine`): 無 runtime 依賴，Apache 2.0，可嵌入。評估 state machine definition (states, transitions, guards, tool restrictions)，**無 LLM 在 loop 中**
- **MCP plugin 層**: 整合 Claude Code / Codex / opencode / Cursor / Pi
- **強制力分級**: Claude Code=Hard（protocol 層阻擋）、opencode=Hard（TypeScript plugin）、Cursor=Advisory（只能注入 rules）

## 核心 Guardrails

| Guardrail | 效果 |
|-----------|------|
| Per-state tool enforcement | 不在 `allowed_tools` 裡的 tool 直接隱形 |
| Bash discernment | Redirect (`>>`)、destructive (`rm`, `shred`)、interpreter 在非 write 狀態直接擋 |
| Edit guards | `max_edit_lines` + `max_files_per_state` 上限 |
| Command allow-lists | `allowed_commands` 前綴匹配（只准 `pytest`、`cargo test`） |
| Conditional transitions | Guards with predicates (eq, gt, exists) on context data |
| Approval gates | `requires_approval` 在高風險 transition 前等人類點頭 |

## 研究數據

5-task SWE-bench subset，local models：

| Model | Size | No Statewright | With Statewright |
|-------|------|---------------|-----------------|
| gemma3 | 3.3GB | FAIL | FAIL |
| gemma4:e2b | 7.2GB | FAIL | PASS* |
| gpt-oss:20b | 13.8GB | FAIL | PASS (5/5) |
| gemma4:31b | 19.9GB | FAIL | PASS (5/5) |

> 13.8GB+ 模型從 2/10 → 10/10。**同一台機器、同一個模型**，只加了 state machine 約束。

## HN 討論要點

**質疑**：
- **Cache busting**: 頻繁切換 tool list = 每次 transition 都是 cache miss，長 session 成本可觀
- **專利模糊地帶**: 核心引擎 Apache 2.0，但 provisional patent #64/054,240 涵蓋 "state machine guardrail enforcement for LLM agent tool access"。到底什麼是 open 的？
- **彈性 vs 剛性**: 太 restrictive 的 workflow 會讓 agent 卡死（`statewright_deactivate` 是逃生口）
- **Workflow 定義太簡**: JSON schema 很漂亮但它能傳遞多豐富的 phase instruction？transition 時只說「你在 act mode 了，這是新 tools」夠嗎？

**共鳴**：
- 多人提到自己做過類似的事（ticketing system、structured output harness、Beads-like）
- 共識：狀態機是讓 local models 可用化的關鍵路徑
- `davidkpiano`（stately.ai 的人）出現說 "Looks like stately.ai but for agents"

## 與現有方案對比

| 方案 | 做法 | 強制力 |
|------|------|--------|
| **Statewright** | State machine + tool gating | 硬（protocol 層） |
| **Beads** | Compaction-based agent memory | 軟（context 管理） |
| **opencode Plan/Build** | 兩階段分割 | 軟（context switch） |
| **structured output harness** | No tool calling，純 structured output | 硬（根治） |

Statewright 的差異化：**enforcement 在 protocol 層，不在 prompt 層**。不是「建議 agent 不要亂用 tool」，是直接讓 tool 對 agent 不存在。

## 對 Hermes 的啟發

1. **Heartbeat 已經有 phase 概念**（autonomous maintenance 有選單），但沒有 per-phase tool gating。Hermes agent 在全對話中都能 access 所有 tools。
2. **ContextForge MCP gateway** 如果在 gateway 層做 tool gating，理論上可以實現類似效果——gateway 根據當前 phase 過濾 tool list 再傳給 model。
3. **Cache 成本**：頻繁切換 tool list 是 tradeoff。但如果 phase 夠粗（planning 階段穩定幾十個 turn），cache 影響有限。
4. **不需要 Rust engine**：Hermes 的 phase 概念比 SWE-bench 簡單得多——「探索 vs 回顧 vs 健康檢查」的 tool set 差異可能只有 2-3 個 tool，不需要完整 state machine runtime。簡單的 allowlist + Bash discernment 就夠了。

## 值得追蹤

- 等他們 release benchmark reproduction code（目前還沒放）
- 觀察 Claude Code 會不會內建類似機制
- FSL license 2029 年才轉 Apache 2.0——self-hosting 目前有限制

