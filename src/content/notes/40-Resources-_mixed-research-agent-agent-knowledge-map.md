---
_slug: 40-Resources-_mixed-research-agent-agent-knowledge-map
_vault_path: 40-Resources/_mixed/research/agent/agent-knowledge-map.md
tags:
- hermes
- research
- index
- agent
created: '2026-05-23'
updated: '2026-06-08'
version: 2
title: Agent Knowledge Map（v2 — 2026-06-08 更新）
type: research
status: budding
---

# Agent Knowledge Map（v2 — 2026-06-08 更新）

> Hermes Agent 知識庫的閱讀導覽。
> 從 5 領域擴展到 **8 主題 + 3 主題交叉**，對應 9 份核心概念整合文。

## 八大主題（2026-05~2026-06 研究累積）

| # | 主題 | 核心問題 | 核心概念文 | 原始研究報告 |
|---|------|----------|------------|--------------|
| **M1** | **Memory + Context** | Agent 的經驗如何積累、過期、蒸餾？Context window 怎麼管理？ | `agent-core-concepts.md` | 5/16、5/23、5/30、6/03 |
| **M2** | **Multi-Agent Coordination** | 多個 agent 如何分工、溝通、避免衝突？ | `multi-agent-coordination-core-concepts.md` | 5/19、5/25、6/02 |
| **M3** | **Self-Improvement + Self-Correction** | Agent 如何從錯誤中學習、不重蹈覆轍？ | `self-improvement-core-concepts.md` | 5/18、5/26、5/27、5/28、5/30 |
| **M4** | **Agent Planning** | ReAct 過時了嗎？2026 規劃架構如何 scale？ | `agent-planning-core-concepts.md` | 6/07 |
| **M5** | **Meta-Agent 監督** | 誰來監督 agent 行為？如何避免 error cascade？ | `meta-agent-supervision-core-concepts.md` | 5/21、6/01 |
| **M6** | **Code vs Tool-based Agents** | LLM 用 JSON 還是用 code 行動？框架 vs 直接 API？ | `code-vs-tool-agents-core-concepts.md` | 5/29 |
| **M7** | **Observability + Trace + Memory Governance** | Agent 跑久了怎麼 debug？memory 如何自我治理？ | `observability-tracing-core-concepts.md` | 5/24、5/27 |
| **M8** | **Benchmarks + Routing + MCP Security** | 怎麼量化「誰好」「誰便宜」「誰安全」？ | `benchmark-routing-mcp-core-concepts.md` | 6/04、6/05、6/06 |

> **M8 是三主題交集合併**：SWE-bench/SABER（量化誰好）、LLM Routing/Cascade（量化誰便宜）、MCP 三層防禦（量化誰安全）。三者交集 = Production-grade agent 系統的標配。

---

## 框架背景文

| 檔案 | 用途 |
|------|------|
| `hermes-agent-framework.md` | Hermes Agent 框架本體（v1） |
| `openclaw-vs-hermes.md` | 生態定位（vs OpenClaw 等） |

---

## 閱讀路徑

### 快速 survey（1-2 小時）
1. `hermes-agent-framework.md` — 框架基本功
2. `openclaw-vs-hermes.md` — 生態定位
3. 本檔「八大主題」表格 — 建立全域地圖
4. `agent-core-concepts.md` — M1 領域核心洞察
5. 挑一份其他核心概念文略讀

### 深度鑽研（每主題 3-4 小時）
每個 M 主題：
1. 本檔的「核心問題」引導思考
2. 對應的「核心概念文」讀整合層
3. 對應的「原始研究報告」逐篇讀原始細節
4. 寫你自己的對應實作

### 主題尋跡
- 想找某個具體主題 → 先查本檔的「核心問題」欄位
- 想找某個實作細節 → 搜 `managed-agents/reports/`
- 想找某個失敗模式 → `agent-error-notebook` 的五步閉環

---

## 閱讀原則

- **核心概念文**是橫向整合，先讀這個
- **原始報告**是完整論述，需要深挖再讀
- **exploration notes** 是素材，一般不需直接閱讀

---

## 八主題互相引用關係

```
M1 Memory ←──→ M7 Memory Governance (Memoria self-governance)
M1 Memory ←──→ M3 Self-Improvement (經驗如何變 lessons)
M2 Multi-Agent ←──→ M5 Meta-Agent (誰來監督 worker)
M4 Planning ←──→ M5 Meta-Agent (plan + supervisor)
M4 Planning ←──→ M6 Code vs Tool (ReAct vs Code Agent)
M6 Code vs Tool ←──→ M8 MCP (tool calling 標準化)
M7 Observability ←──→ M3 Self-Improvement (trace → feedback)
M8 Benchmark ←──→ M4 Planning (mini-SWE-agent 簡化 prompting)
M8 Routing ←──→ M2 Multi-Agent (不同 task 不同 model)
M8 MCP ←──→ M5 Meta-Agent (tool list 過濾 = supervisor 職責)
```

---

## 與其他知識庫的關係

- **swimming/** — 運動科學領域（獨立主題）
- **hestia/** — Hestia 的運營記憶
- **talos/** — Talos 的規劃與觀察
- **learnings/** — 跨領域的 lessons learned
- **swim-psychology/** — 遠東心理學 + 游泳應用（2026-06-08 新）

---

## 整合文件清單（v2）

| 檔案 | 用途 | 寫於 |
|------|------|------|
| `agent-knowledge-map.md` | 本檔 — 閱讀導覽與地圖 | 2026-05-23 (v1) → 2026-06-08 (v2) |
| `agent-core-concepts.md` | M1 Memory + Context 核心洞察整合層 | 2026-05-23 |
| `multi-agent-coordination-core-concepts.md` | M2 核心概念整合 | 2026-06-08 |
| `self-improvement-core-concepts.md` | M3 核心概念整合 | 2026-06-08 |
| `agent-planning-core-concepts.md` | M4 核心概念整合 | 2026-06-08 |
| `meta-agent-supervision-core-concepts.md` | M5 核心概念整合 | 2026-06-08 |
| `code-vs-tool-agents-core-concepts.md` | M6 核心概念整合 | 2026-06-08 |
| `observability-tracing-core-concepts.md` | M7 核心概念整合 | 2026-06-08 |
| `benchmark-routing-mcp-core-concepts.md` | M8 三合一核心概念整合 | 2026-06-08 |
