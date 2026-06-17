---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-14-hermes-staged-delegation-pattern
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-14-hermes-staged-delegation-pattern.md
title: Hermes delegate_task 分階段委派模式
created: '2026-05-14'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Hermes delegate_task 分階段委派模式

> **適用場景：** DeepSeek v4-pro（或其他慢速免費模型）的 web research / multi-source 任務
> **最後更新：** 2026-05-14
> **背景：** 我們用 DeepSeek v4-pro 跑了 5 次 delegate_task 研究任務，3 次 timeout、2 次成功。成功的兩次都是「gather-only subagent + parent synthesis」模式。

---

## 核心原則

**不要把蒐集和合成塞進同一個子代理。**

DeepSeek v4-pro 在 200K+ tokens 的 context 下太慢，單一子代理負責「fetch + synthesize」的完整週期需要 400-600 秒，經常中途 timeout。解法是把任務拆兩段：

1. **Phase 1 (Gather):** 子代理只 fetch → 寫入檔案。不求合成，timeout 也可接受（資料已寫入檔案）。
2. **Phase 2 (Synthesis):** 主代理（或第二個 synthesis-only 子代理）讀取檔案後合成結論。不碰 web，快且穩定。

---

## 模式 1：Gather-Only Subagent

子代理只負責抓取資料、寫入檔案，不合成。

**子代理 goal 範例：**

```
Fetch web content from these URLs:
- https://docs.crewai.com/concepts/tasks
- https://docs.crewai.com/concepts/agents

Append all findings to /tmp/crewai_research_raw.md.
Record: URL, page title, key facts, code snippets, config examples.
Do NOT synthesize or draw conclusions. Just collect and record.
```

**特點：**
- 子代理 timeout → 檔案中有部分資料，仍可用
- 多個 source → 開多個平行 gather subagent（各抓一個來源）
- 不需要合成能力，只求忠實記錄

---

## 模式 2：Parent Synthesis

主代理讀取 gather subagent 寫的 `/tmp/*_raw.md` 檔案，自己合成結論。

**主代理 synthesis prompt 範例（給自己的）：**

```
Read /tmp/crewai_research_raw.md and /tmp/openai_research_raw.md.
Synthesize into a report covering:
1. Common patterns across frameworks
2. Unique approaches per framework
3. What's applicable to our Python-only, no-paid-API setup
Output to /tmp/research_synthesis.md
```

**特點：**
- 主代理 context 由自己控制（讀檔案時用 offset/limit 分段）
- 合成品質由主代理模型決定（DeepSeek v4-pro 在本機合成 300K+ tokens 也沒問題 → 分多次 read_file）
- 不需要第二個子代理

---

## 模式 3：Parallel Gather + Dedicated Synthesizer

開 3-4 個 gather subagent 平行抓取，全部完成後開一個 synthesis subagent 讀檔案合成。

```python
# Pseudocode (delegate_task batch mode)
tasks = [
  {"goal": "Fetch CrewAI docs, write to /tmp/crewai_raw.md", "toolsets": ["web", "terminal", "file"]},
  {"goal": "Fetch OpenAI Agents SDK docs, write to /tmp/openai_raw.md", "toolsets": ["web", "terminal", "file"]},
  {"goal": "Fetch LlamaIndex Workflow docs, write to /tmp/llamaindex_raw.md", "toolsets": ["web", "terminal", "file"]},
]
# After all complete...
# Single synthesis subagent or parent synthesis
```

**特點：**
- 平行子代理各自獨立，一個 timeout 不影響其他
- Synthesis subagent 只讀檔案不碰 web → `toolsets: ["terminal", "file"]`
- 最適合 3+ 來源的任務

---

## 錯誤處理

| 狀況 | 處理方式 |
|------|---------|
| Gather subagent timeout | 檔案中有部分資料，仍可合成（標記為 incomplete） |
| 兩個來源衝突 | 標記衝突，不強行融合。報告兩邊說法 |
| 來源 403/404 | 跳過該來源，記錄缺失 |
| Synthesis subagent timeout | 主代理接手合成（讀 gather 檔案） |
| 所有 gather subagent 都 timeout | 失敗——但至少知道哪些來源打不開，下次調整策略 |

---

## 何時用一站式（不拆分）

以下情況可以回到傳統 single-subagent 模式（fetch + synthesize 一次做完）：

- 任務只涉及 1 個來源，預估 <100K tokens
- 任務是純 code 操作（terminal + file），不碰 web
- 子代理模型改為快速模型（Claude Haiku / GPT-4o-mini）——未來選項
- 任務時間預估 <120s（簡單查詢）

---

## 實證

| 模式 | 子代理數 | 結果 | 時間 |
|------|---------|------|------|
| 一站式（LangGraph 研究） | 1 | timeout | 600s |
| 一站式（context management 研究） | 1 | timeout | 403s |
| 平行 gather（CrewAI） | 1 of 3 | ✅ | 124s |
| 平行 gather（OpenAI+LlamaIndex） | 1 of 3 | ✅ | 97s |
| 平行 gather（LangGraph） | 1 of 3 | timeout | — |
| 主代理合成 | 0 | ✅ | ~30s |

**成功率：** 一站式 0/2，分階段 3/3（含 partial success）
