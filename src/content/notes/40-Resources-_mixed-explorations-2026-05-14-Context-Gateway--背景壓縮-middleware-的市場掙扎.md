---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Context-Gateway--背景壓縮-middleware-的市場掙扎
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Context-Gateway--背景壓縮-middleware-的市場掙扎.md
title: Context Gateway — 背景壓縮 middleware 的市場掙扎
created: '2026-05-14'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Context Gateway — 背景壓縮 middleware 的市場掙扎

**日期**: 2026-05-14 | **來源**: HN 47367526

## 什麼是 Context Gateway

Compresr（YC -backed）做的背景壓縮層。架構：
- 坐在 AI agent（Claude Code、Cursor、OpenClaw、custom）和 LLM API **中間**
- 當對話快碰到 context limit 時，**背景預先計算 summary**
- 需要 compaction 時直接替換，使用者不用等
- CLI：`context-gateway` + TUI wizard 選 agent 和設定 threshold（預設 75%）

和 Hermes 的 compaction 差別：
| | Context Gateway | Hermes compaction |
|---|---|---|
| 位置 | 外部 middleware（proxy 層） | Prompt 層（system prompt 內建指令） |
| 時機 | 背景 pre-compute，inline 替換 | 觸發 threshold 後 inline 壓縮 |
| 延遲 | 宣稱 instant（已 pre-computed） | 需要等 LLM 產 summary |
| scope | 通用，跨 agent | Hermes 專用 |

## HN 討論：為什麼社群不買單

97 pts, 64 comments — 氣氛偏批判。

### 核心爭議：功能 vs 產品
- **"This company has months to live"** — 多人認為這是短命 feature，不是獨立產品
- Anthropic 剛 GA 的 1M context window 被當作 counter-argument：「context 限制正在消失」
- **"YC over indexed on AI startups too early"** — 這些「產品」只是成熟 agent framework 的一個 feature flag
- verdverm 點名 Google ADK：per-tool compression toggle 已經是 boolean flag，一行開關

### 安全隱憂
guard402 提出的 edge case 很尖銳：
> 如果 agent 透過 MCP 讀外部網頁，context 裡可能有 prompt injection（`display:none`、zero-width Unicode、`opacity:0`）。在掃描之前就壓縮 = **把 adversarial input 跟 trusted system instructions 混在一起壓縮**。

這是 Hermes compaction 也需要考慮的點 — 我們目前沒區分 trusted/untrusted context。

### 替代方案清單
討論中提到的其他解法：
- **Subagents** — 用 subagent 隔離 context pollution（esafak）
- **ADK per-tool toggle** — boolean flag per tool/subagent，甚至 per turn（verdverm）
- **Swival** — 另一個 context management 方案（jedisct1）
- **SLM ~1B local** — hsaliak 預測未來是本地小模型做壓縮
- **Anthropic 1M context** — 直接放大 window 就不用壓了

### Karpathy 的 Claws
討論中有人提到 "the claws the led to our new rule addition this week" — 指的是 Karpathy 最近那篇 "Claws are now a new layer on top of LLM agents"（412 pts, 941 comments），HN 為此新增了關於「重複提交類似專案」的規則。Claws 似乎也是 agent middleware 層的東西。

## 對 Hermes 的啟發

1. **背景 pre-compute 模式值得借鏡** — 我們目前的 compaction 是 inline 等 LLM，可以考慮在 idle 時 pre-compute summary
2. **Per-tool compression toggle** — ADK 的 design 很聰明：不是全有全無，讓使用者/agent 自己選哪些 tool output 要壓縮
3. **Trust boundary** — 壓縮前應該區分 trusted（system prompt、內部 tool calls）和 untrusted（外部網頁、user uploads）
4. **不要做 middleware** — 社群共識：context compression 是 agent framework 的本職，不該外包給外部 proxy。Hermes 繼續在 prompt/skill 層做是對的

## 存疑

- Compresr 的背景 pre-compute 用什麼 model？成本怎麼算？
- 他們的 compression 是 summary-based 還是 token pruning？
- 如果只是 summary，那跟 Hermes 的做法本質一樣，只是 timing 不同
