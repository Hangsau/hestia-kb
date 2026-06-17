---
_slug: 40-Resources-_mixed-explorations-2026-05-25-llm-memory-architecture-trends
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-llm-memory-architecture-trends.md
title: LLM Agent Memory Architecture — Trends & Patterns
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# LLM Agent Memory Architecture — Trends & Patterns

**延續自**: (fresh exploration)

**日期**: 2026-05-25

## Per-Source Insights

### Source 1: CASCADE — 6-layer memory architecture (HN, 2025-11)
- **URL**: https://news.ycombinator.com/item?id=46016824
- **Repo**: https://github.com/For-Sunny/nova-mcp-research (MIT)
- **架構**: 6-layer memory on consumer GPUs (RTX 3090)
- **關鍵數字**:
  - Sub-2ms semantic search across 11,000+ memories (Faiss + GPU)
  - 9.68x computational amplification
  - 95% GPU utilization (up from 8% baseline)
- **三層核心**: episodic / semantic / procedural layers
- **發布模式**: Research Edition (unrestricted) + Enterprise Edition (guardrails)
- **觀察**: 明確區分「研究版需要信任無 guardrails」vs「企業版需要合規」——這和 Talos 的 governance 思路共鳴

### Source 2: Lossless Context Management — tiered summarization (HN Ask, 2026-03)
- **URL**: https://news.ycombinator.com/item?id=47449389
- **模式**: level 0 summaries (per-exchange) → level 1 summaries (periodic roll-up)
- **Context 結構**: `[intro prompt] + [old exchanges lvl1] + [system prompt] + [recent lvl0] + [temporal] + [recent messages]`
- **Tool results progressive stripping** — 幾輪後移除，只留近期
- **單一永久 session**，不壓縮（until explicitly compacted）

## Hermes 啟發

1. **Tiered memory** 已在 Hermes 的 L1→L2→L3 記憶管線中隱含實作，但缺少明確的「summary level」命名層級。lossless context 的 lvl0/lvl1 命名值得借鑒。

2. **CASCADE 的 Research vs Enterprise dual release** 呼應我們在 `docker-agent-policy-schema.md` 看到的 enforcement gradient——從 unrestrictive research 到 production-ready 的光譜，是 Hermes governance 可以考慮的。

3. **Faiss + GPU sub-2ms** 是純量化的數字。Hermes 目前是 SQLite FTS5，沒必要跟這個竞争，但 snapshot pipeline 的查詢延遲可以記錄下來，未來評估是否需要升级。

4. **Tool results progressive stripping** — 這個 pattern 值得加入 `memory-consolidator` 的 eviction policy。

## Cross-Article Synthesis

兩個 sources 都指向同一個核心結論：**階層式記憶比純 RAG 有效**。

| Approach | Pattern | Status |
|---|---|---|
| RAG/embeddings | 2023-2024 主流 | 已被质疑 |
| Local markdown + grep | OpenClaw 等 | 表現更好 |
| Tiered summarization (lvl0→lvl1) | lossless context | 新興 |
| Multi-layer episodic/semantic/procedural | CASCADE | 生產級 |

Hermes 目前走在「階層式摘要」這條路上（MEMORY.md → consolidator → briefing），但尚未引入 semantic layer 的 embedding search。CASCADE 的 6-layer 架構中 semantic/procedural 分離是未來可能的擴展方向。

## 未追蹤 Leads

- https://github.com/For-Sunny/nova-mcp-research — CASCADE 原始碼 (MIT)
- https://news.ycombinator.com/item?id=46016824 — 原文 HN 討論
- https://news.ycombinator.com/item?id=47449389 — Ask HN 討論串
- lossless context management — 搜尋該術語找更多實作

## ✅ 本次探索完成