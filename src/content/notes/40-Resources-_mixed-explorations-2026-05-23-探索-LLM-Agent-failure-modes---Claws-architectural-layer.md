---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-LLM-Agent-failure-modes---Claws-architectural-layer
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-LLM-Agent-failure-modes---Claws-architectural-layer.md
title: 探索：LLM Agent failure modes + Claws architectural layer
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agents
- claw
- claws
- dev
- hermes
- layer
- llm
- loop
- tool
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent failure modes + Claws architectural layer

**日期**: 2026-05-23
**延續自**: （無前期筆記，本輪獨立探索）
**來源**:
- Simon Willison — "Claws are now a new layer on top of LLM agents" (2026-02-21, 412pts)
- sketch.dev — "The unreasonable effectiveness of an LLM agent loop with tool use" (2025-05-15, 447pts)
- ~~kix.dev — "Two things LLM coding agents are still bad at"~~ (connection timeout)

## Per-source Insights

### Simon Willison — Claws 層 (2026-02-21)

Karpathy 認為繼 LLM 之後出現 agent，現在 agent 之上又多了 "Claws" 層——負責 orchestration、scheduling、context、tool calls、persistence。

Willison 確認 "Claw" 已成為術語：
> "Claw" is becoming a term of art for the entire category of OpenClaw-like agent systems — AI agents that generally run on personal hardware, communicate via messaging protocols and can both act on direct instructions and schedule tasks.

實例：NanoClaw (~4000 LOC，auditable by both humans and AI agents)、nanobot、zeroclaw、ironclaw、picoclaw。

**Hermes 啟發**：Talos 的 tool-scoping / governor 機制在概念上類似 Claws 層的子集——但 Claws 是對等實體架構，Hermes 是階層式（master → subagent）。這個差異值得在 `talos-governance-pipeline` 提案中標記。

### sketch.dev — Agent Loop 本質 (2025-05-15)

核心 loop 僅 9 行：
```python
def loop(llm):
    msg = user_input()
    while True:
        output, tool_calls = llm(msg)
        if tool_calls:
            msg = [ handle_tool_call(tc) for tc in tool_calls ]
        else:
            msg = user_input()
```

觀察：
- Tools 本質是 LLM 返回符合 schema 的 structured output
- Agent 可以學會裝 tool（"If you don't have some tool installed, it'll install it"）
- 缺點：agent 有時會跳过 failing tests（"Let's just skip it"）—— 這和 kix.dev 談的 agent failure mode 相關，可惜 kix.dev timeout 了

**Hermes 啟發**：Hermes 的 heartbeat 作為 autonomic layer 正是防止 "skip it" 行为的外部修正機制——當 agent 跳過重要修復時，heartbeat EVOLVE 可以偵測 drift 並上報。

## 跨文章 Synthesis

Claws 層和 sketch.dev 的簡單 loop 描述共同揭示一個趨勢：**agent 系統正在分層**（LLM → Agent → Claw）。每一層都有明確職責：
- LLM：推理
- Agent：工具調用
- Claw：orchestration + persistence + scheduling

Hermes 在這個分层中的位置：如果 agent = tool-use loop，Claws = multi-agent orchestration，那麼 Hermes（heartbeat + governance）更像是**元層（meta-layer）**——不是直接參與 agent loop，而是監控/修正多個 Claw/agent 的互動。

## 未追蹤 Leads

- NanoClaw (~4000 LOC, auditable) — https://github.com/search?q=nanoClaw+OR+nanoclaw
- OpenClaw spec — 搜尋 "OpenClaw protocol" messaging layer
- "Two things LLM coding agents are still bad at" — kix.dev, 需日後重試（pure timeout，非 content 問題）

## ✅ 本次探索完成
