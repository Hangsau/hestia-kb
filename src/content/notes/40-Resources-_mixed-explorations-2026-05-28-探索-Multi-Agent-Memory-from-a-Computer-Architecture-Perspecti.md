---
_slug: 40-Resources-_mixed-explorations-2026-05-28-探索-Multi-Agent-Memory-from-a-Computer-Architecture-Perspecti
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-探索-Multi-Agent-Memory-from-a-Computer-Architecture-Perspecti.md
title: 探索：Multi-Agent Memory from a Computer Architecture Perspective
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- architecture
- cache
- consistency
- hermes
- mem
- memory
- multi
- protocol
- session
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 探索：Multi-Agent Memory from a Computer Architecture Perspective

**日期**: 2026-05-28 | **來源**: arXiv 2603.10062 (2026-03) | **主題**: 以計算機架構視角分析 multi-agent memory 挑戰

---

**延續自**: [[2026-05-28-agent-memory-architectures-2026]]

---

## Core Thesis

> Multi-agent memory should be framed as a computer architecture problem: memory hierarchy, bandwidth, caching, and consistency.

兩大 paradigm：
- **Shared memory**：所有 agent 訪問同一記憶，知識 reuse 容易但需要 coherence（否則互相 overwrite、讀到 stale data）
- **Distributed memory**：每個 agent 有自己的 local memory，selective sync，isolation 好但需要 explicit synchronization

---

## Three-Layer Memory Hierarchy（對應到 Hermes）

| 架構層 | Agent 對應 | Hermes 現況 |
|--------|-----------|------------|
| **I/O layer** | 攝取/發出資訊（audio, text, images, network calls） | MCP tools, user input |
| **Cache layer** | 快速、有限容量（compressed context, recent tool calls, KV caches, embeddings） | heartbeat_state, working context |
| **Memory layer** | 大容量、較慢（synthesized facts, conclusions, plans） | MEMORY.md, facts.jsonl, proposals |

> **核心原則**：Agent 效能瓶頸在 memory bandwidth 不是 compute。

---

## 兩個 Missing Protocols

### 1. Agent Cache Sharing Protocol（最緊迫）

現有研究：KV cache sharing（Liu 2024, Fu 2025b, Ye 2025）已有初步探索，但缺乏** principled protocol** 讓一個 agent 的 cached results 能被另一個 agent transformed + reused。

analogous to cache transfers in NUMA systems。

**對 Hermes 的啟示**：
- 當 Hestia 和 Talos 共同處理同一用戶請求時，Hestia 的 KV cache 產出能否給 Talos 直接使用？
- 目前沒有——兩個 agent 的 cache 完全隔離，每次都需要從頭 compute
- **實務 gap**：MCP 的 tool call 結果能否視為一種「cache」被跨 agent 共享？

### 2. Agent Memory Access Protocol（治理層）

現有框架（MemGPT, A-Mem, Mem0）都沒有明确规定：
- 一個 agent 能否讀取另一個 agent 的 long-term memory？
- 是 read-only 還是 read-write？
- 存取單位是什麼？（整體 / session / fact level）

**對 Hermes 的啟示**：
- Talos 能否讀取 Hestia 的 MEMORY.md conclusions？
- 兩個 agent 的 memory 是否應該有**主從關係**（guardian vs executor）？
- 目前沒有明確的 access protocol，純靠 convention（都在同一 vault 但沒有明確的 access control）

---

## Multi-Agent Consistency — The Hard Problem

Memory consistency models（從 SP/TSO/PSO 到弱排序）決定並發記憶操作的語意。

Multi-agent 的等價問題：
- Agent A 寫入一條結論，Agent B 在多久之後能看到？
- 如果兩個 agent 同時更新同一 fact，誰的版本正確？
- Agent C 加入 session 時，應該看到「當前一致狀態」還是「所有歷史」？

**Figure 3 的 consistency model comparison**：從傳統 memory architecture 到 multi-agent memory 的映射——這是有形的 framework，可以用來評估任何 multi-agent architecture 的 consistency guarantees。

**對 Hermes 的啟示**：
- Hearth 的 heartbeat_learning distillate 過程本質上是一種「跨 session memory synchronization」
- 如果 Hestia 在 session N 得出結論，Talos 在 session N+1 應該如何看待這個結論的 valid period？
- 目前沒有 consistency model，完全靠「默契」

---

## 與前期筆記的 Cross-Synthesis

前期筆記（Mem0 + Atlan）已經識別出：
1. **Temporal validity** 是 open problem
2. **Actor-aware** 對 multi-agent 關鍵
3. **Token efficiency** 差距可達 3.7x

本文填補了**協議層**的缺口：
- Mem0/Atlan 討論的是「如何儲存/檢索」——data model 層
- 2603.10062 討論的是「如何跨 agent 訪問/同步」——protocol 層
- 兩者結合：正確的 data model（Mem0/Atlan）+ 正確的 access protocol（本文）= 完整的 multi-agent memory architecture

---

## 未追蹤 Leads

- https://arxiv.org/abs/2510.12872 — KVcomm: online cross-context KV-cache communication for multi-agent（直接相關 cache sharing protocol）
- https://arxiv.org/abs/2502.12110 — A-Mem: agentic memory for LLM agents
- https://arxiv.org/abs/2409.05591 — Memorag: moving towards next-gen RAG via memory-inspired knowledge discovery
- https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/multi-agent-debate.html — Microsoft multi-agent debate pattern

---

## ✅ 本次探索完成

