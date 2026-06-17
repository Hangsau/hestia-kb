---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-Memori-論文---Context-Gateway
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-Memori-論文---Context-Gateway.md
title: 探索：Memori 論文 + Context Gateway
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- context
- gateway
- llm
- memori
- memory
- phase
- semantic
- tree
- triples
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：Memori 論文 + Context Gateway

**延續自**: [[2026-05-21-memori-production-memory-engine.md]] [[2026-05-21-context-compression-production-agents.md]]
**日期**: 2026-05-23 | **探索來源**: prior notes untracked leads

## Memori 論文核心 (arXiv:2603.19935)

**題目**: Memori: A Persistent Memory Layer for Efficient, Context-Aware LLM Agents
**作者**: Luiz C. Borro 等 5 人 | 9 pages, 2026-03-20

### 核心主張

Memori 把 memory 當作「資料結構問題」而非「上下文大小問題」：

1. **Advanced Augmentation Pipeline**
   - 對話 → 語意三元組 (semantic triples)
   - 對話 → 摘要 (conversation summaries)
   → 精確檢索 + 一致推理

2. **數字說了什麼**
   - 81.95% accuracy on LoCoMo benchmark
   - 1,294 tokens/query（full context 的 ~5%）
   - 比競爭方案少 67% tokens
   - 比 full-context 方法省 20x

3. **關鍵設計抉擇**
   - Semantic triples（不是原始對話）→ 可合成、可索引
   - LLM-agnostic（不綁 vendor）
   - Pipeline 有 summary + triples 兩種表示，視查詢類型切換

### 與現有研究的對照

| System | 策略 | 封閉/開放 |
|--------|------|----------|
| MemR³ | Closed-loop evidence gap, multi-pass | 開放 |
| Memori | Semantic triples + BM25 rerank, open-loop | 開放 |
| ChatIndex | B+ tree, LLM-guided topic generation | 開放 |
| Mem0 | 雲端托管, 封閉 | 封閉 |

Memori 的架構在 open-loop（無迭代收斂）上類似 MemR³ 的單一 pass，但用了 semantic triples 而非向量相似度。`RankedFact` 雙分數（cosine similarity + BM25 rank_score）也已驗證是 production 可行的。

### Hermes 啟發

Memori 的成功（81.95% accuracy, 20x cost reduction）驗證了：
- **structured representation > raw context injection** 這個方向是對的
- Hermes 的 session tree（phase skeleton → semantic nodes）方向符合這個趨勢
- Phase-based navigation（Plan/Execution/Review）是一種有效的 topic generation，與 Memori 的 semantic triples 互補

**下一步**：WS-025 (session tree phase navigation) 已 READY，整合時可參考 Memori 的 Advanced Augmentation pipeline 概念，把 tool_calls 驅動的 phase detection 升級為 semantic triple extraction。

---

## Context Gateway

**來源**: https://github.com/Compresr-ai/Context-Gateway | MIT License

### 定位

Go-based proxy（代理層），坐落在 AI agent（Claude Code、Cursor 等）和 LLM API 中間：
```
Agent → Context Gateway → LLM API
```

當對話太長時，在**背景**執行 compaction，所以 agent 不需要等待。

### 架構

- 語言：Go（高併發，适合長对话压缩）
- License: MIT（開放）
- 特色：background compaction（不 block agent）、multi-agent support

### Hermes 啟發

Context Gateway 的 proxy 模式和 WS-025 的 session tree 架構不同——它是即時壓縮，WS-025 是離線索引。但「background, non-blocking」的設計值得參考：如果 session tree 在 cron tick 時建立（不即時），agent 端的查詢體驗更好。

---

## 跨文章 Synthesis

**核心 insight**：production agent memory 的兩個有效路徑：
1. **結構化表示**（Memori: semantic triples, MemR³: ranked facts）
2. **非阻塞索引**（Context Gateway: background compaction, ChatIndex: offline tree build）

兩者並不矛盾——結構化表示是「怎麼存」，非阻塞索引是「何時建」。理想的 agent memory system 需要兩者兼具。

Hermes 現在的缺口：session tree 建立了 Phase skeleton，但每個 phase 內的 semantic representation（triples/summaries）還未實作。這是 WS-025 下一階段的核心。

---

## 未追蹤 Leads

- https://github.com/Compresr-ai/Context-Gateway — 查看 `start_agent.sh` 实际压缩策略
- https://arxiv.org/abs/2505.23735 — LongMemEval-V2（評估記憶系統的 benchmark）

## ✅ 本次探索完成
