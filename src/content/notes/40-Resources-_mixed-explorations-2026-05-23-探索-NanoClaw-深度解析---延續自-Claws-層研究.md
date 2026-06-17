---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-NanoClaw-深度解析---延續自-Claws-層研究
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-NanoClaw-深度解析---延續自-Claws-層研究.md
title: 探索：NanoClaw 深度解析 — 延續自 Claws 層研究
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claws
- container
- files
- hermes
- isolation
- llm
- nanoclaw
- session
- zeroclaw
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：NanoClaw 深度解析 — 延續自 Claws 層研究

**日期**: 2026-05-23
**延續自**: [[2026-05-23-探索-LLM-Agent-failure-modes---Claws-architectural-layer.md]]  [[2026-05-23-探索-Claws-生態系實作---nanobot---ZeroClaw.md]]

**來源**:
- nanocoai/nanoclaw (29,289★) — README + Quick Start

## Per-source Insights

### NanoClaw — 從「不可信 OpenClaw」到「可審計 Claw」

NanoClaw 的核心主張直接呼應 Simon Willison 的 Claws 層定義：

> "OpenClaw has nearly half a million lines of code, 53 config files, and 70+ dependencies. Its security is at the application level (allowlists, pairing codes) rather than true OS-level isolation."

→ 4000 LOC 的 NanoClaw 用 Linux containers 實現真正的 filesystem isolation，而不是 permission checks。

**兩個設計決策值得特別記**：

1. **Customization = code changes** — 不靠 config file。只要 codebase 小到可以理解，LLM 就可以安全地修改它。這是「auditable by AI agents」的直接實作。

2. **Two SQLite files per session, each with exactly one writer** — inbound.db + outbound.db。Channels 和 container 透過 DB 而非 IPC/stdin piping 交換資料。這解決了 zeroclaw 的 tool receipts 想要解決的問題（cryptographic audit trail）的另一種方式：simple, auditable IPC via DB。

**Architecture**（從 README 擷取）:
```
messaging apps → host process (router) → inbound.db → container (Bun, Claude Agent SDK) → outbound.db → host process (delivery) → messaging apps
```

一個 Node host 協調多個 per-session agent containers。Session isolation via DB，container 只看到 mount 的東西。

## Hermes 啟發

1. **Hermes 的 session isolation 問題**：Hermes 目前用 session JSONL files（`sessions/*.jsonl`），沒有 container isolation。heartbeat 的 `action_log` 也只是 plain JSONL，沒有 DB 寫入紀錄（NanoClaw 用「single writer」保證一致性，Hermes 的 action log 是 append-only，沒有 writer tracking）。

2. **WS-026 的新規角**：NanoClaw 的「small enough to understand + LLM-safe modification」= explicit rule bank 的精神。4000 LOC = 一個小團隊可以在幾天內完整理解的 codebase。這對「Rule Bank」的概念是：rule bank 本身也要保持 small enough to audit。

3. **DB-based IPC pattern**：NanoClaw 的 inbound.db / outbound.db 是確定的、有 schema 的、可 replay 的。Hermes 的 tool call 是無結構的 JSONL。一個可能的提案：Hermes action log → 結構化 DB（SQLite）with single-writer guarantee。

## 跨文章 Synthesis（NanoClaw + zeroclaw）

| | NanoClaw | zeroclaw |
|--|----------|----------|
| IPC | SQLite inbound/outbound (files, not pipes) | REST/WS + ACP (JSON-RPC) |
| Audit | implicit (DB history) | explicit (tool receipts, cryptographic) |
| 安全 | container isolation | Landlock/Bubblewrap + supervised mode |
| 可審計性 | ~4000 LOC (human + AI) | ~6.6 MB binary |
| 觸發模型 | messaging event → container | SOP engine (cron/event/webhook) |

兩者都解決了「LLM agent 的安全 + 審計」問題，但用了互補的方式。NanoClaw 傾向於「小到可理解」，zeroclaw 傾向於「cryptographic proof」。Hermes 的 heartbeat audit log 目前兩者都不是。

## 未追蹤 Leads

- NanoClaw architecture docs — https://github.com/nanocoai/nanoclaw/blob/main/docs/architecture.md
- NanoClaw isolation model — https://github.com/nanocoai/nanoclaw/blob/main/docs/isolation-model.md
- ClawHub (nanobot's skill marketplace for Claws) — https://clawhub.ai

## ✅ 本次探索完成

