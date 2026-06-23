---
_slug: 40-Resources-_mixed-explorations-2026-05-22-2026-05-22---LLM-Agent-Memory--Production-Patterns---Backtra
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-2026-05-22---LLM-Agent-Memory--Production-Patterns---Backtra.md
title: '2026-05-22 — LLM Agent Memory: Production Patterns & Backtracking'
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- backtracking
- crdt
- decay
- github
- https
- llm
- mattbusel
- memory
- wasm
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 2026-05-22 — LLM Agent Memory: Production Patterns & Backtracking

**延續自**: （本篇為獨立探索，無前期筆記）

## Per-Source Insights

### Source 1: Mattbusel/rust-crates (GitHub, 8⭐)
URL: https://github.com/Mattbusel/rust-crates

Production Rust crates for AI agent infrastructure. 6 focused crates:

**記憶系統**：
- `tokio-agent-memory` — episodic + semantic + working memory with **decay scheduling**; includes a **shared memory bus for multi-agent coordination** (key for Talos/Hestia comms design)
- `tokio-memory` — Ebbinghaus forgetting curve implementation; consolidation pipelines; pluggable persistence. Ebbinghaus curve = scientific memory model, not just TTL

**狀態同步**：
- `llm-sync` — CRDT + vector clock primitives for **distributed agent state sync** — GCounter, PNCounter, LWWRegister, ORSet; deterministic state merge. 直接回答了多 agent 記憶整合的實作方式

**邊緣/成本**：
- `llm-wasm` — WASM + edge LLM primitives: FNV-1a cache, TTL cache, retry with backoff, guard chain, cost ledger
- `llm-budget` — 自治成本治理：hard budget enforcement（request 發出前就block）；per-model/per-agent/fleet-wide accounting

**工具執行**：
- `wasm-agent` — ReAct loop for WASM/edge; Thought-Action-Observation with tool dispatch, full reasoning traces, **resumable state serialization**

**設計原則**：zero panic（所有 fallible operation 返回 Result）、typed errors (thiserror)、property-based testing。

### Source 2: DeepClause — Backtracking Through Agent Memory (Substack)
URL: https://deepclause.substack.com/p/backtracking-through-memory

Core problem: 當 agent 策略失敗時，context window 累積 error messages + apologies + stack traces，下一次嘗試被這些「失敗包袱」汙染。

Solution: Prolog 的 backtracking mechanics 應用於 LLM context management。

**Mechanism**：
- DML (DeepClause Meta Language, Prolog dialect) 定義的不是 if/else，而是**可能的執行路徑**
- 當路徑失敗，Prolog runtime 自動 restore messages[] 到 branch point 的狀態
- 5000 tokens 的失敗嘗試 → 完全從 context 抹除，agent 乾淨重來

**Code example insight**：
```prolog
attempt_strategy(Strategy, Req) :-
    system("Current Strategy: {Strategy}"),
    task("Write script for: {Req}. Output pure code.", Code),
    exec(vm_exec(command: "python3 -c '{Code}'"), Result),
    get_dict(exitCode, Result, 0).  % 若 exit code ≠ 0 → backtrack
```
第一個策略失敗時，messages[] 自動恢復，絲毫不殘留。

**DeepClause CLI** 用 Markdown 規格驅動 compiler，編譯成 DML/Prolog，再由 meta-interpreter 追蹤 state（messages[] array）。自然語意 + 形式化確保性。

## Hermes 啟發

### 1. Ebbinghaus forgetting curve → 自訂 decay 而非 TTL
目前 heartbeat severity 用的是 fixed TTL suppression。`tokio-memory` 的 Ebbinghaus 曲線模型更符合真實資訊價值衰減。可以考慮：
- 短期內重複出現的 error → decay 慢（可能真的是系統問題）
- 長期未見的 error → decay 快（可能是 transient）

### 2. Multi-agent memory bus（CRDT + vector clocks）
目前 Talos/Hestia 通訊是 polling 模式（每 15 分）。`llm-sync` 的 CRDT primitives 可以支援：
- 方向性：comms 是 double-ended queue，CRDT 可以支援多 writer 并發寫
- 缺點：CRDT狀態最終一致，非即時一致。不適合即時回覆，但適合非同步長期狀態共享（如 task PLAN 進度）

### 3. Backtracking = 乾淨的 context 恢復
DeepClause 的 backtracking mechanic 揭示了 append-only context 的替代方案。Hermes 目前沒有類似的「失敗路徑隔離」機制。可能的應用場景：
- 當 subagent delegate_task 失敗時，可以「回滾」而不保留失敗的 stack trace
- 不過這需要 framework-level 支援，短期内不適合直接實現

### 4. WASM sandbox tool execution
`wasm-agent` + `llm-wasm` 的組合（ReAct loop + WASM isolation）呼應了 guardian sandboxing gradient 的 L1/L3 設計。WASM sandbox 比 container 輕量，適合工具隔離。

## 跨文章 Synthesis

兩個 source 都指向同一個結論：**production LLM agent 需要明確的 memory management 策略，而非讓 context 自然膨脹**。

| 維度 | Mattbusel | DeepClause |
|---|---|---|
| Memory model | 結構化 decay + consolidation | 失敗時主動回滾 |
| Sync | CRDT/vector clocks（分散式） | N/A（單 agent） |
| Execution | WASM + ReAct | Prolog meta-interpreter |
| Cost control | Budget enforcement | 透過去除失敗 tokens 間接降低 |

兩者都重視**記憶的時間維度**（decay / backtracking），而非只管 storage。

## Untracked Leads（純 URL）

- https://github.com/Mattbusel/tokio-agent-memory （v0.1.0，含 memory bus 設計）
- https://github.com/Mattbusel/llm-sync （CRDT + vector clock 實作）
- https://github.com/Mattbusel/tokio-prompt-orchestrator （multi-core LLM pipeline orchestration）
- https://craftjarvis-jarvis1.github.io/ （Jarvis-1 multi-task memory-augmented agents）

## ✅ 本次探索完成
