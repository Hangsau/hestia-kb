---
_slug: 40-Resources-_mixed-explorations-2026-05-19-探索-LLM-Agent-長期記憶架構---2026-05-19
_vault_path: 40-Resources/_mixed/explorations/2026-05-19-探索-LLM-Agent-長期記憶架構---2026-05-19.md
title: 探索：LLM Agent 長期記憶架構 — 2026-05-19
date: 2026-05-19
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aegis
- append
- dpm
- github
- heartbeat
- hermes
- llm
- log
- memory
- mnemora
created: '2026-05-19'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent 長期記憶架構 — 2026-05-19

**延續自**: （無前期筆記，本輪首度探索）

## 資料來源

### 1. HN Algolia — "LLM agent memory architecture" 搜尋結果
- **Aegis Memory v1.2** (GitHub, 1 pt) — 標榜「解決了什麼值得記住的問題」
- **Mnemora** (GitHub, 4 pts) — serverless memory DB，強調「no LLM in CRUD path」
- **Entelgia** (GitHub, 1 pt) — consciousness-inspired multi-agent，persistent memory
- **其他**: LoCoMo benchmark memory system (80.1%)、VAC Memory System

### 2. arXiv 趨勢（摘要推斷）
- **Memory for Autonomous LLM Agents: Mechanisms, Evaluation** (2603.07670) — 多層記憶架構 survey
- **R²-Mem: Reflective Experience for Memory Search** (2605.13486) — fine-grained historical retrieval without heavy memory pre-loading
- **Deterministic Projection Memory (DPM)** (2604.20158) — append-only event log + task-conditioned projection

## Hermes 啟發

### 現有記憶層（已實現）
| 層次 | 實作 | 現況 |
|------|------|------|
| 短期 | session context、running_agents tracking | ✅ 心跳監控 |
| 中期 | `heartbeat_state.json`、memory-consolidator cron | ✅ 運作中 |
| 長期 | Obsidian vault + FTS5 index | ⚠️ FTS5 做完，ML training 未開始 |

### 「什麼值得記」問題 → Aegis Memory 的核心命題
Aegis Memory 號稱解決的問題，其實是 Hermes heartbeat scoring 每天在做的事：
- 區分 signal vs noise（EVOLVE sensor 的 severity escalation）
- 萃取值得保留的 pattern（`heartbeat_learning.py` 的 pattern extraction）
- 過濾已知的 transient error（ISSUES.md suppression）

**但 Hermes 缺少的是**：壓縮後的壓縮——當 vault 累積大量筆記後，如何快速判斷哪些資訊「值得在下一個 session 拿出來當 context」？

### Mnemora 的啟發：「No LLM in CRUD path」
目前 Hermes 的 memory pipeline 每一步都有 LLM 參與（extract → distill → brief）。Mnemora 的 architecture 提示：也許可以用更簡單的 DB query 回答「你上次處理過這個專案嗎？」，而不需要每次都經過 LLM。

### DPM 的 append-only event log
目前 heartbeat 只追蹤 state change（running_agents_count、severity.json）。DPM 的 append-only log 概念或許能用來建一個 lightweight audit trail，記錄「每個 cron cycle 做了什麼決定」，而不只是結果狀態。

## 跨文章 Synthesis

三個方向交匯在同一点：**selective memory**（選擇性記憶）。

- Aegis → 解決「哪些要記」
- DPM → 解決「怎麼組織」（append-only + conditioned projection）
- Hermes 現有系統 → 解決「哪些要alert」

缺口：當三者結合時，「selective memory + append-only log + alerting」的實際系統長什麼樣子？現有提案（`hermes-consolidation-step`、`hermes-fts5-doc-index`）只涵蓋了部分。

## 未追蹤 Leads

- https://github.com/quantifylabs/aegis-memory
- https://github.com/mnemora-db/mnemora
- https://arxiv.org/abs/2603.07670
- https://arxiv.org/abs/2605.13486

## ✅ 本次探索完成
