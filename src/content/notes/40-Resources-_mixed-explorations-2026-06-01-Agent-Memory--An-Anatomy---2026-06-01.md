---
_slug: 40-Resources-_mixed-explorations-2026-06-01-Agent-Memory--An-Anatomy---2026-06-01
_vault_path: 40-Resources/_mixed/explorations/2026-06-01-Agent-Memory--An-Anatomy---2026-06-01.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 20:\n    title: Agent Memory: An Anatomy — 2026-06-01\n            \
  \           ^"
_raw_fm: '

  title: Agent Memory: An Anatomy — 2026-06-01

  date: 2026-06-01

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, com, consolidation, eviction, llm, memory, procedural, prospective,
  retrieval, semantic]

  created: 2026-06-01

  updated: 2026-06-15

  status: active

  '
title: 'Agent Memory: An Anatomy — 2026-06-01'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Agent Memory: An Anatomy — 2026-06-01

**來源**: HN (39 pts) | https://brgsk.xyz/agent-memory-anatomy/

## 核心架構：三個零件

任何 agent memory library 都由三個零件構成：

| 零件 | 功能 | 典型實作 |
|------|------|---------|
| Extractor | 對話轉錄 → 語句（去脈絡化的事實） | LLM call + schema |
| Store | 資料庫（vector/relational/graph） | 含 timestamp + confidence + source |
| Retriever | 查詢時搜尋並回傳最相關語句 | vector similarity + keyword + reranker |

Timing 是 extractor 最重要決定：太 eager 浪費 token，太 lazy 會遇到 lost-in-the-middle。

## 四種記憶 vs 實際庫存

| 類型 | 現況 |
|------|------|
| **Episodic** | 存成 timestamped statement → 下一代碼是 semantic |
| **Semantic** | 主戰場：autobiographical memory（用戶事實） |
| **Procedural** | 大部分是 mislabeled semantic — LangMem 是乾淨的例外（單獨 mechanism） |
| **Prospective** | 幾乎不存在 — "do Y when condition X" 無庫存 |

> **Prospective memory gap 是 open territory**。這精準對應 WS-039 的 eviction decision 問題——但這篇文章是從 prospective/intention side 切入，WS-039 是從 eviction side 切入。兩者互補。

## Consolidation：線上 vs 離線

| 類型 | 實作 |
|------|------|
| 線上（同步） | 每條消息後 extraction — budget 下的退化版 |
| 離線（異步） | Dreams（Anthropic）、Letta sleep-time compute — 對齊生物學 |

**生物analog**：睡眠時 replay + prune → 慢速壓縮。離線 consolidation 架構更乾淨。

## Forgetting 是 retrieval 問題，不是 storage 問題

> "Forgetting in biological memory is a **constraint**, not a **feature**"

核心主張：
- 生物忘記是因為儲存能力有限（被迫）
- Agent 沒有這個限制（磁碟便宜）
- **保留一切** = 可審計、可 debug、可回答 "what did we know last March?"
- 真正問題：隨 store 變大，retrieval 降級
- **解決方案**：consolidation（離線 reorganize）+ retrieval ranking（current > stale）

對 WS-035 drift penalty 的直接啟發：不是加 decay，而是確保 retrieval 給 current facts 更高權重。Decay 是症狀治療；consolidation + retrieval-layer priority 才是根本解。

## 這個詞彙比產品更穩定

> "The vocabulary is more stable than the products. Learn the parts."

盤點常見 library 的工程實現差異：
- **LangMem**: procedural = 單獨 mechanism（Evolving system prompt），無 vector store writes
- **Mem0**: procedural 與 semantic 共享同一 index，只差在 metadata label
- **Graphiti**: 全部進同一 bitemporal graph，無 procedural 概念

## 對 Hermes 的具體啟發

1. **Consolidation 層次缺失**：heartbeat_learning.py 目前只有 distillate（蒸餾觸發），沒有 offline reorganization。Dreams/Letta 的 sleep-time compute 模式值得研究。

2. **Prospective memory**：目前沒有任何 library 處理 "do Y when X next appears"。這是 WS-039 learned eviction 的另一面——learned eviction 是 eviction when stale，而 prospective 是 remember-to-do when condition。三個 GRPO-trained tool：Add/Update/Delete 對應 semantic memory management；Retrieve/Summary/Filter 對應 episodic retrieval。

3. **Forgetting as retrieval problem**：heartbeat_learning.py 的 decay 機制方向可能偏了。應該聚焦 retrieval-layer staleness penalty，而非 storage-layer decay。

4. **Emotion salience absent**：純文字 agent 無法有 affect signal。嘗試用 importance scoring 是 LLM-judged proxy，不是真正的情緒編碼。

## Cross-Synthesis: Sleep-Time Compute Closes the Consolidation Gap

Fetched letta.com/blog/sleep-time-compute (2025-04-21) for direct details.

**Core paradigm**: Sleep-time compute transforms "raw context" → "learned context" during idle periods, mirroring biological sleep's offline reorganization. Key architecture: two-agent model (primary + sleep-time), where memory management is offloaded to the sleep-time agent. This decouples memory formation from conversation latency.

**Bio-analog**: Biological sleep = replay + prune offline. MemGPT's original bundling of memory + conversation in one agent caused "memories become messy and disorganized over time" — sleep-time agents solve this via continuous async reorganization.

**For Hermes consolidation gap** (original note §3): heartbeat_learning.py currently has **no offline reorganization** — only on-demand distillation. Letta's sleep-time compute architecture suggests a clean pattern:
- Primary agent = heartbeat EVOLVE (no memory-edit tools)
- Sleep-time agent = background distill/correct job (memory-edit tools, async)
- Anytime memory = partial distill output readable without waiting for full cycle

**Implementation path**: `memory-auto-distill` cron already handles on-demand distill. A sleep-time equivalent would be a cron that runs during natural idle (between heartbeat cycles) and rewrites the facts store — not incremental add, but full reorganization. This is distinct from on-demand distill which only fires when staleness ≥ 0.8.

**Prospective memory connection** (original note §2): Sleep-time compute is the *infrastructure* for "do Y when X next appears." A sleep-time agent can maintain a prospective memory queue and revise it continuously, checking conditions even when the primary agent is idle. WS-039's bounded dereferencing could feed into this queue.

**WS-039 status**: Phase 3 `_log_eviction_decision()` already integrated into `check_distillation_freshness()` (heartbeat_learning.py:371). The eviction decision log accumulates training data for Phase 2 `_mine_eviction_rules()`. The sleep-time architecture provides the runtime context for surfacing those learned rules.

## 未追蹤 Leads
- https://news.ycombinator.com/item?id=45789672 — HN thread
- Anthropic Dreams: platform.claude.com/docs/en/managed-agents/dreams
- Sebastian Lund "Ultimate Guide to LLM Memory": fastpaca.com/blog/ultimate-guide-to-llm-memory
- LangMem (LangChain): github.com/langchain-ai/langmem

## ✅ 本次探索完成

