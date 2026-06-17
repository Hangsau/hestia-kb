---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Semble-Token-Savings-實測---Hermes-安裝可行性
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Semble-Token-Savings-實測---Hermes-安裝可行性.md
title: Semble Token Savings 實測 — Hermes 安裝可行性
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- code
- hermes
- mcp
- savings
- search
- seemble
- semble
- token
- tokens
- uvx
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

# Semble Token Savings 實測 — Hermes 安裝可行性

**延續自**: [[2026-05-18-zerostack-semble.md]]

**日期**: 2026-05-18 | **來源**: GitHub README + Benchmarks page

---

## Source 1: GitHub README

**URL**: https://github.com/MinisLab/semble | **Stats**: 1.1k ⭐, MIT

### 核心數據

| 指標 | 數值 |
|------|------|
| Index time | 263ms（average repo） |
| Query latency | 1.5ms p50 |
| Token savings vs grep+read | **98% fewer**（566 vs 45,692 tokens/query） |
| NDCG@10 | 0.854（99% of CodeRankEmbed Hybrid 137M） |
| 底層模型 | potion-code-16M（16M params, static, CPU） |

### 安裝方式

```bash
# 方式1: uvx（推薦，零安裝）
uvx --from "semble[mcp]" seemble  # 注意拼寫

# 方式2: pip（需要 --break-system-packages 或 venv）
pip install semble

# 方式3: MCP server
claude mcp add seemble -s user -- uvx --from "semble[mcp]" seemble
```

### Hermes 整合路徑

1. **MCP gateway 整合**：現有 `native-mcp` skill 可接入。Semble MCP server 支援 Claude Code、Codex、OpenCode、Cursor。需確認 Hermes 的 MCP gateway 是否支援 `uvx --from` 形式。

2. **Bash integration**：`pip install seemble` 或 `uv tool install seemble`，然後在 `AGENTS.md` 加 snippet。缺點：每次 call 都要 `uvx` 啟動（~100ms cold start），不是 background service。

3. **Python API**：`from seemble import SembleIndex`。可封裝成 Hermes skill，直接呼叫 Python API 不走 MCP。

### Token Savings 計算方式

`(file chars − snippet chars) / 4`。保守估算：baseline 是讀取完整 matched file。Stats 存在 `~/.semble/savings.jsonl`。

---

## Source 2: Benchmarks Page

**URL**: https://github.com/MinishLab/semble/tree/main/benchmarks

### Token Efficiency 數據

| Method | Expected tokens/query | Savings |
|--------|----------------------|---------|
| ripgrep + read file | 45,692 | baseline |
| **semble** | **566** | **98% fewer** |

| Budget | 500 | 1k | 2k | 4k | 8k | 16k | 32k |
|--------|-----|----|----|----|----|----|----|
| semble | 0.685 | 0.849 | 0.938 | 0.976 | 0.991 | 0.996 | 0.996 |
| ripgrep+read | 0.001 | 0.008 | 0.037 | 0.088 | 0.212 | 0.379 | 0.583 |

Semble 在 2k token budget 就能達到 93.8% recall，ripgrep+read 需要完整 32k window 才能達到 58.3%。

### Ablation — Ranking 貢獻

| | Raw | + Ranking |
|-|-----|-----------|
| BM25 | 0.675 | 0.834 |
| potion-code-16M | 0.650 | 0.821 |
| **semble hybrid** | — | **0.854** |

Ranking 信號（definition boosts、identifier stems、file coherence、noise penalties）對 NDCG@10 的貢獻約 +0.18（從 raw 0.675 到最終 0.854）。

### 關於 benchmark 的限制

- 1,250 queries over 63 repos in 19 languages — 規模可接受
- Claude Sonnet 4.6 做 LLM-as-judge — 可能有 bias
- 有被排除的方法：codanna（6 語言不支援）、claude-context（需要 paid OpenAI + vector DB）

---

## Hermes 整合評估

### 可行性

1. **`uvx --from "semble[mcp]" semble` 可正常執行**（已驗證，103ms 啟動）
2. Python API 可用：`from semble import SembleIndex`
3. MCP server 模式需要 `uv` — Hermes 環境有 uv

### 風險

1. **每次 bash call 都有 ~100ms cold start** — 不適合高頻 search_files 場景
2. **index 建立需要 263ms + 模型下載** — 首次搜尋有延遲，之後 session 內cached
3. **依賴外部模型下載** — `potion-code-16M` 首次會 fetch HuggingFace（網路環境影響）
4. **Python API vs MCP** — MCP 需要 gateway 支援，Python API 更直接但需要封裝

### 預估效益

假設 Hermes 每 session 平均 50 次 code search（`search_files` call）：
- 每次節省 98% tokens → 50 × (45,692 − 566) / 4 ≈ **564k tokens/session**
- 以 DeepSeek 100k tokens/$0.14 ≈ **$0.79/session 節省**
- 每小時心跳假設 2 sessions → **$1.58/hour**

（未計入快取讀寫，實際應該更低，但數量級有意義）

---

## 跨文章 Synthesis

Zerostack + Semble 的共同啟發：Rust/高效工具正快速填補 AI coding agent 市場。

| | Semble | Hermes search_files |
|---|---|---|
| Token/query | 566 | ~15,000-50,000（視檔案大小） |
| Latency | 1.5ms | 取決於檔案數量 |
| Semantic | ✅ | ❌（regex only） |
| Setup | 需安裝 | 內建 |

**結論**：Semble 是 Hermes code search 的高價值補充，尤其在 Semantic search 和 token efficiency 兩個維度。建議列為 INSTALL 提案。

---

## ⏳ 未追蹤

- Semble MCP 在 Hermes native-mcp skill 下的實際整合測試
- Hermes `search_files` vs Semble 在實際任務上的 token 對比（A/B test）
- `find_related` 在 Hermes codebase 上的準確度測試

## ✅ 本次探索完成

