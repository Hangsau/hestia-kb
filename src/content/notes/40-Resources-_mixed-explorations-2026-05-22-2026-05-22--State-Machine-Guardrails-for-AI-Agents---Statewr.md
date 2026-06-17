---
_slug: 40-Resources-_mixed-explorations-2026-05-22-2026-05-22--State-Machine-Guardrails-for-AI-Agents---Statewr
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-2026-05-22--State-Machine-Guardrails-for-AI-Agents---Statewr.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 18:\n    title: 2026-05-22: State Machine Guardrails for A ... \n  \
  \                   ^"
_raw_fm: '

  title: 2026-05-22: State Machine Guardrails for AI Agents — Statewright

  date: 2026-05-22

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, enforcement, guardrails, hermes, https, loop, pass, state,
  statewright, tool]

  created: 2026-05-22

  updated: 2026-06-15

  status: active

  '
title: '2026-05-22: State Machine Guardrails for AI Agents — Statewright'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# 2026-05-22: State Machine Guardrails for AI Agents — Statewright

**延續自**: [[2026-05-22-agent-loop-design]]

**來源**: https://github.com/statewright/statewright (345 ⭐, 126 pts HN)
**標籤**: #agent-guardrails #state-machine #tool-enforcement #reliability

## Per-Source Insights

### 核心洞察：Structure Beats Reasoning

Statewright 的核心論點：不要叫模型變大（更多 token / 更強模型），而是把問題變小（用狀態機約束工具空間）。

> "State machines constrain the tool and solution spaces so the model reasons in a focused context at each step."

這和 Sketch 作者的 agent loop 設計高度呼應——Sketch 用一個通用 `bash` tool + 簡單輪詢架構處理多數任務；Statewright 則用狀態機限制每個 phase 可用工具。

### 架構設計

Rust engine（確定性，無 LLM in the loop）+ MCP plugin layer。

每個 state 有：
- `allowed_tools`: 該 phase 允許的工具
- `max_iterations`: 最大迭代次數
- `guards`: 條件式過渡（如 test_result eq pass → 進入下一 state）

### 實驗數據（5-task SWE-bench subset）

| Model | Size | Bug Fix | SWE-bench (5) |
|-------|------|---------|---------------|
| gemma3 | 3.3GB | FAIL | FAIL |
| gpt-oss:20b | 13.8GB | PASS | PASS (5/5) |
| llama3.3 | 42.5GB | PASS | PASS (2/2) |

關鍵 threshold：~13GB。模型需要能 retain 足夠 file context 才能做精確編輯。

### Guardrails 列表

- Per-state tool enforcement（階段限制工具）
- Bash discernment（即使 Bash 允許，仍阻止 `echo >`, `rm -rf`, `sed -i`）
- Edit guards（限制單次編輯行數上限）
- Command allow-lists（白名單前綴，如 `pytest`, `cargo test`）
- Conditional transitions（狀態機條件分支）
- Approval gates（人工審批）
- Interrupt transitions（某些操作自動觸發驗證 state → 返回）
- Fork/join（並行分支）
- Environment scoping（遮蔽環境變數）

### Hermes 啟發

1. **Hermes 的階段化 tool enforcement**：Hermes 目前沒有狀態機約束。`heartbeat_v2.py` 有 15 steps 序列（EVOLVE → SNAPSHOT → REST），但沒有 phase-based tool restriction。對某些操作（特別是涉及危險操作的 tool calls）可以借鑑 Statewright 的 phase guard。

2. **Confabulation vs tool enforcement**：Statewright 的 research 指出模型的問題不是「不會」而是「太多 choice」。這呼應了 agent-loop-design 提到的「skip test → claim success」confabulation pattern。限制工具 = 減少 confabulation 的空間。

3. **Rust engine 的確定性**：Statewright 的 Rust engine 完全不依賴 LLM 做決策，這是結構性 guarantee vs soft prompt engineering。Hermes 的 heartbeat 裡哪些是 LLM 決定、哪些是確定性 code？EVOLVE 是 LLM，SNAPSHOT/REST 是確定性 code。這是一個架構選擇，不是缺點。

4. **13GB threshold 的啟發**：對本地模型（gemma3 3.3GB → FAIL），Statewright 的 insight 合理。Hermes 的主力是 DeepSeek v4-pro（server-side，無此限制），但如果是部署 subagent 到 memory-constrained 環境，這個 threshold 值得注意。

## 與前期探索的連結

- **[[2026-05-22-agent-loop-design]]**：Sketch 的「9 行核心 agent loop」vs Statewright 的「狀態機 guardrails」——兩者都在解決同一問題（agent 不可靠），不同切入點：loop 架構 vs tool 限制
- **[[2026-05-18-Zerostack-Doom-Loop-Detection---原始碼深潛]]**：doom-loop detection 也是一種「agent 異常行為偵測」，但它是 reactive（出事後偵測），Statewright 是 proactive（出事前約束）

## 未追蹤 Leads

- https://statewright.ai/pricing（定價、免費額度）
- https://github.com/statewright/statewright/blob/main/docs/guardrails.md（完整 guardrails 技術文件）
- https://github.com/statewright/statewright/tree/main/crates（Rust engine 原始碼結構）

## ✅ 本次探索完成
