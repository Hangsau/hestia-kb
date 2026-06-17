---
_slug: 40-Resources-_mixed-explorations-2026-05-23-Statewright-追加---README-補充
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-Statewright-追加---README-補充.md
title: Statewright 追加：從 README 補充 Guardrails 實作細節
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- control
- guardrails
- state
- statewright
- tool
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# Statewright 追加：從 README 補充 Guardrails 實作細節

**日期**: 2026-05-23
**來源**: raw GitHub README（statewright/statewright）
**延續自**: [[2026-05-22-2026-05-22--State-Machine-Guardrails-for-AI-Agents---Statewr]]

## 核心補充：State Machine vs DAG 的差異

Statewright README 明確點出為何 agent workflow 應該用 state machine 而非 DAG：

> State machines **loop and retry** (unlike DAGs), which is what agentic work actually needs.

這是關鍵洞察：DAG 是有向無環圖，適合靜態規劃；但 agentic work 需要來回迭代（寫 code → 測試 → 失敗 → 重寫），DAG 無法表達這種回饋環。State machine 的 phase transition + retry 機制更符合實際開發流程。

## 實驗結果（SWEBench 子集）

| Model | Size | Bug Fix | SWE-bench (5 tasks) |
|-------|------|---------|---------------------|
| gemma3 | 3.3GB | FAIL | FAIL |
| gemma4:e2b | 7.2GB | PASS* | FAIL |
| gpt-oss:20b | 13.8GB | PASS | PASS (5/5) |
| gemma4:31b | 19.9GB | PASS | PASS (5/5) |
| llama3.3 | 42.5GB | PASS | PASS (2/2) |

低於 13GB 的模型能產生 tool calls，但無法 retain 足夠檔案內容做準確編輯。13GB 是門檻值。

## 與 Hermes 的對應

Statewright 的 phase transition model 類比：
- `planning` phase → 對應 Hermes 的 `autonomic` 層（read-only health check）
- `implementing` phase → 對應 Hermes 的 `cognitive` 層（LLM 自主決策）
- `testing` phase → 對應 Hermes 的 EVOLVE validation
- `completed` phase → 對應心跳 cycle 的 end-state

Statewright 的工具限制（planning 只能用 read tools）是 `structure beats reasoning` 的具體實現——不靠 prompt engineering 禁止某 tool，而是由狀態機控制 tool 可用性。

## 未追蹤 Leads

- https://statewright.ai（定價、免費額度）
- https://statewright.ai/docs/guardrails（完整 guardrails 技術文件）
- https://github.com/statewright/statewright/tree/main/crates（Rust engine 原始碼結構）

## ✅ 本次追加完成