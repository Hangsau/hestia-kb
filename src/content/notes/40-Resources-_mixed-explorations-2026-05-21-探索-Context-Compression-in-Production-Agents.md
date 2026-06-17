---
_slug: 40-Resources-_mixed-explorations-2026-05-21-探索-Context-Compression-in-Production-Agents
_vault_path: 40-Resources/_mixed/explorations/2026-05-21-探索-Context-Compression-in-Production-Agents.md
title: 探索：Context Compression in Production Agents
date: 2026-05-21
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- compaction
- context
- distill
- expand
- gateway
- hermes
- intent
- llm
- source
- tool
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# 探索：Context Compression in Production Agents

**延續自**: [[2026-05-14-context-gateway-hn]] [[2026-05-22-Agent-Memory--Memori-Architecture---R²-Mem-Rubric-Scoring]]

**日期**: 2026-05-21 02:30 CST

## Per-source Insights

### Source 1: Context Gateway (Compresr.ai) — HN 97 pts, Mar 2026

**URL**: https://github.com/Compresr-ai/Context-Gateway (MIT license, open source)

**核心架構**：proxy 架在中間，agent → LLM API 的流量先經壓縮層。

```
Agent (Claude Code/Cursor/OpenClaw) → [Context Gateway] → LLM API
                                      ├─ SLM Summarizer (compress tool outputs)
                                      ├─ Background compaction (85% capacity trigger)
                                      ├─ Lazy tool loading (only relevant tools per step)
                                      └─ expand() API (decompress on demand)
```

**關鍵技術細節**：
- **SLM-driven compression**：訓練小型語言模型當 classifier，根據 tool call 的意圖（intent）決定保留哪些內容、扔掉哪些。例如 `grep` 找 error handling patterns → 保留 matches，扔掉 surrounding code
- **Pre-computed summaries**：85% 容量時後台開始 compaction，用戶永遠不需要等待
- **Expand-on-demand**：模型需要之前移除的內容時，呼叫 `expand()` 取回原文
- **Lazy tool loading**：工具描述也 lazy load，只在當前 step 相關時才送入 context
- **Trigger threshold**：可配置，預設 75%（不是 100% 才開始）

**與 Hermes 的差距**：
- Hermes 的 `memory-auto-distill` 是 cron-based（每天 03:00），不夠即時
- Hermes 沒有 expand/decompress 機制，一旦 distill 就無法還原
- Hermes 沒有「意圖感知壓縮」——所有 tool output 一視同仁，沒有按 tool call intent 選擇性保留

### Source 2: Pilo — Mozilla Agentic Web Automation (18 pts)

**URL**: https://github.com/mozilla/pilo

**核心**：瀏覽器 automation engine，用 accessibility tree 而非 raw HTML，token 節省 60-80%。

**壓縮方式**：tag mapping（`listitem → li`）+ ID 縮短 + 重複文字去重。簡單但有效。

**Plan → Observe → Act → Validate loop**：每步都有驗收，final output 由第二個 LLM「打分」。

**與 Hermes 的關聯**：Pilo 的 tag-level compression 啟發——Hermes 的 tool output 可以做 shallow transformation（去掉 verbose logging prefix、壓縮路徑顯示）而不需要 SLM classifier。

## Cross-source Synthesis

### 壓縮策略光譜

| 層級 | 方法 | 成本 | 效果 |
|------|------|------|------|
| Shallow | Tag mapping, path shortening, dedup | $0 | 10-30% reduction |
| Intent-aware | SLM classifier per tool call intent | ~SLM API cost | 40-60% reduction |
| Semantic | Full LLM summarization | ~LLM API cost | 50-80% reduction |

Hermes 目前停在 semantic（`memory-auto-distill`），但從未實作 shallow intent-aware 層。

### 觸發時機光譜

| 方案 | 觸發點 | 優點 | 缺點 |
|------|--------|------|------|
| Cron-based（Hermes） | 固定時間 | 簡單 | 不即時，可能來不及 |
| Capacity threshold（CG） | 85% window | 即時 | 需要準確測量 |
| Per-tool（Hermes skill） | skill 內 | 細粒度 | 每個 skill 各自為政 |
| Proactive（CG pre-compute） | 85% 時後台 | 用戶無感 | 需要閒置運算資源 |

### Hermes 可借鑒的方向

1. **Proactive background compaction**：類似 CG 的 85% trigger，在 heartbeat idle 時執行 compaction，不等 cron
2. **Expand/decompress 機制**：Hermes 的 distill 是單向的，如果 agent 需要回溯，沒有復原路徑
3. **Intent-aware tool output filtering**：不是所有 tool output 都同等重要——`read_file` 的 200 行可能只有 20 行相關，但 Hermes 全部保留

## 未追蹤 Leads

- https://arxiv.org/abs/2402.09768 — Make an LLM That Can Write Better Prompts (ICLR 2025 workshop, compressed context for prompt generation)
- https://github.com/mozilla/pilo — Pilo browser automation (compression pipeline source code)
- `logs/history_compaction.jsonl` — Context Gateway 的 compaction log format（可用來借鑒 Hermès 的 compact log）

## 對 Hermes 的啟發

Context Gateway 的架構最值得借鑒的是「**expand-on-demand**」——壓縮不是刪除，而是換個地方存，需要時能召回。Hermes 的 `memory-auto-distill` 是破壞性的（distill 後原文丟），如果要往這方向走，需要一個 `context_cache/` 目錄存未 distill 的原始內容。

另一個低成本的 win：Pilo 的 shallow compression（tag mapping）可以 immediately implement，風險極低，效果可驗證。

## ✅ 本次探索完成
