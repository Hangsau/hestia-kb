---
_slug: 40-Resources-_mixed-explorations-2026-05-14-The-LLM-Agent-Cost-Curve---Hermes
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-The-LLM-Agent-Cost-Curve---Hermes.md
title: The LLM Agent Cost Curve & Hermes
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- cache
- conversation
- cost
- curve
- hermes
- quadratic
- tokens
- tracking
- turn
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# The LLM Agent Cost Curve & Hermes

**Date**: 2026-05-14
**Source**: [Expensively Quadratic: the LLM Agent Cost Curve](https://blog.exe.dev/expensively-quadratic) (exe.dev, 2026-02-03)
**Theme**: 自主探索 — agent economics × Hermes architecture
**Confidence**: high（有實際 API pricing 數據，有 Hermes source code 對照）

---

## TL;DR

LLM agent 的成本不是線性的——是 **O(n²)**。cache reads 在 ~20K tokens 後主導成本，到 ~50K tokens 時佔總成本 87%。Hermes 的架構**隱含地**做了很多對的事（agent cache、auto-continue、subagent delegation），但**完全沒有 cost visibility**，也不知道自己的 conversation 成本曲線長怎樣。

---

## The Quadratic Curve（from the article）

### 為什麼是 O(n²)？

每個 turn 都要把整個 conversation history 送進 prompt cache。第 n 個 turn 讀 n 個 turn 的 cache，成本累積成 sum(1..n) = O(n²)。

### 具體數字（Anthropic pricing）

Cache read 是 input price 的 1/10，但因為每個 turn 都要讀全部歷史，累積起來還是貴。

### 一個實際 conversation 的 breakdown

- 總成本 $12.93
- 到 27,500 tokens 時，cache reads 佔總成本 50%
- 到 conversation 結束時，cache reads 佔 87%

作者的 meta-point：**start a new conversation 通常比 continue 便宜**——重建 context 的成本 < 繼續付 cache read 稅。

---

## Hermes 架構對照

### 已經做對的事

1. **Agent Cache（LRU 128, 1h TTL）** — 直接對應 prompt caching 最佳化
2. **Auto-Continue（1h window）** — 避免 cache expiration 後的昂貴重建
3. **Iteration Budget** — hard stop-loss，但是 count-based 不是 cost-based
4. **Subagent Delegation** — delegate_task/kanban 把 iteration 移出 main context，正是文章推薦的模式

### 缺的東西

1. **No Token/Cost Tracking** — 完全不知道花了多少錢
2. **No Cost-Aware Conversation Break** — 不知道何時該 reset conversation
3. **No Cache Hit Rate Visibility** — cache 效益無法量化
4. **No Provider-Aware Budgeting** — 90 iterations DeepSeek vs Opus 成本差 10-50x

---

## 對 Hermes 的務實建議

### Level 1: Visibility（低成本，高價值）
在 heartbeat 或 session stats 加 token/cost tracking。不改行為，純觀測。

### Level 2: Cost-Aware Conversation Management
conversation tokens > N 時提示 break。可做 /cost slash command。

### Level 3: Provider-Aware Budgeting
iteration_budget 改成 dollar-based + provider multiplier。

---

## Open Questions

1. Hermes typical conversation 多長？如果 < 10K tokens，quadratic curve 不適用
2. Anthropic prompt cache hit rate 有收嗎？
3. Subagent fresh start 的 cache write cost 會不會抵消省下的 cache read cost？

---

## Worth Tracking

- Token cost tracking for Hermes — 最有 immediate value 的 instrumentation
- Conversation length distribution — 先有數據再優化

