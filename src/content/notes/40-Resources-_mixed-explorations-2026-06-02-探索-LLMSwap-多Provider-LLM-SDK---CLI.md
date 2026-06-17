---
_slug: 40-Resources-_mixed-explorations-2026-06-02-探索-LLMSwap-多Provider-LLM-SDK---CLI
_vault_path: 40-Resources/_mixed/explorations/2026-06-02-探索-LLMSwap-多Provider-LLM-SDK---CLI.md
title: 探索：LLMSwap 多Provider LLM SDK + CLI
date: 2026-06-02
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- cli
- cost
- gemini
- gpt
- hermes
- llmswap
- ollama
- provider
- sdk
- usage
created: '2026-06-02'
updated: '2026-06-15'
status: budding
---

# 探索：LLMSwap 多Provider LLM SDK + CLI

**日期**: 2026-06-02 | **來源**: HN Algolia (12 pts) | **類型**: EXPLORATION

---

## Source Insight

**URL**: https://pypi.org/project/llmswap | **Version**: 5.5.8 | **License**: MIT

LLMSwap = Python SDK + CLI，10 個 LLM provider 統一介面。

### Core Features

**Multi-provider**: OpenAI (GPT-5.2), Anthropic (Claude Sonnet 4), Gemini 3 Pro Preview, Grok 4.3, Cohere Command A+, Groq GPT-OSS, Perplexity Sonar, IBM watsonx, Sarvam, Ollama。統一 tool calling + MCP protocol + automatic fallback。

**CLI commands**:
- `llmswap ask` — quick one-off questions
- `llmswap chat` — interactive chat with memory
- `llmswap generate` — code/command generation from natural language
- `llmswap review` — AI code review (bugs/security/style/performance)
- `llmswap debug` — error analysis
- `llmswap providers` — status of all configured providers (table view)
- `llmswap compare --input-tokens N --output-tokens M` — cost comparison across providers
- `llmswap usage [--days N]` — usage stats by provider
- `llmswap costs` — cost analysis + optimization recommendations
- `llmswap config` — configuration management

**Cost comparison output example** (from docs):
```
Provider    │ Cost      │ Savings vs Most Expensive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ollama      │ $0.0000   │ 100.0%
Groq        │ $0.0001   │ 99.5%
Gemini      │ $0.0019   │ 90.5%
Claude      │ $0.0150   │ 25.0%
GPT-4       │ $0.0200   │ 0.0%
```

**Usage stats**:
```
Provider    │ Queries │ Tokens    │ Cost
OpenAI      │ 142     │ 45,231    │ $2.15
Anthropic   │ 89      │ 31,452    │ $1.87
Gemini      │ 203     │ 67,891    │ $0.45
Ollama      │ 567     │ 234,567   │ $0.00
Total       │ 1,001   │ 379,141   │ $4.47
```

### Hermes 啟發

**Cost tracking 整合價值高**：`llmswap usage` / `llmswap compare` 直接提供 token count + cost breakdown by provider。若 Hermes 的 `cost追踪` 用這個而非自己刻，直接省 80% code。

**Multi-provider fallback**：Hermes 目前 DeepSeek 為主，若要擴展 provider，LLMSwap 的 unified interface 是捷徑。但目前 Hermes 已穩定，不需要為了「擴展」而引入 dependency。

**可持續關注**：`llmswap costs` 的 optimization recommendations 是亮點，但需要实际跑過才能評估建議品質。CLI 整備程度高，install 來玩不難。

---

## 跨文章 Synthesis

N/A — 單一 source。

---

## 未追蹤 Leads

- https://llmswap.org — 官方文件（cli.html 已讀完，sdk.html 未讀）

---

## ✅ 本次探索完成
