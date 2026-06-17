---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-23-hermes-architecture-convergence
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-23-hermes-architecture-convergence.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-23'
confidence: medium
title: 架構趨同：Schema 顯式化與 Sandbox Containment
updated: '2026-06-15'
type: research
status: budding
---

# 架構趨同：Schema 顯式化與 Sandbox Containment

**消化筆記**: agent-governance-patterns, RAIL-Protocol-Universal-LLM-App-Bridge, RAIL-Hermes-Architectures-HN-Anti-AI, Memori-Retrieval-Pure-RAG-vs-MemR3

（4 篇 2026-05-23 探索筆記，分別研究 agent 安全治理、LLM-App 橋接協議、AI 輸出鑑別、記憶檢索評分。表面看起來各自獨立，但放在一起出現一致的底層架構模式。）

---

## Cross-Cutting Theme 1: Schema 顯式化是所有系統的必然方向

**支援筆記**: agent-governance-patterns, RAIL-Protocol-Universal-LLM-App-Bridge, Memori-Retrieval-Pure-RAG-vs-MemR3

**分析**：

三篇筆記從不同端點出發，但描述的是同一條收斂線：

| 系統 | 原本 | Schema 顯式化後 |
|------|------|----------------|
| Hermes（tool calling） | implicit tool signatures，agent 自己推斷介面 | AgentCore Gateway 集中 tool 存取控制 + Cedar policy |
| RAIL | 方法以程式碼存在，靠 reflection 動態發現 | manifest.json 顯式聲明工具能力（typed） |
| Memori | similarity search 回傳純文字 | RankedFact 含 similarity + rank_score 雙分數 |
| SAGA | 動態 agent 通訊無 access control | 密碼學 token（formal, typed） |

「schema 顯式化」的驅動力不是美學，是**enforcement 的需求**。implicit schema 只能靠 agent 自己遵守邊界（LLM judgment），explicit schema 才能做 infrastructure-level enforcement（Aegis 的 typed edge、ACE 的 data/capability barriers、Memori 的 dual score 都是不同形式的 typed schema）。

Hermes 的現況：vault_access.json 維護 tool capability registry，但 heartbeat_decisions.jsonl 是無結構的日誌，session_search 回傳純文字無 score。這與目標架構（explicit typed schema everywhere）有三層 gap：

1. **Tool registry**：已有 vault_access.json，但無 version/capability metadata
2. **Action output schema**：heartbeat decisions 缺 typed structure，無法做 automated policy check
3. **Retrieval output schema**：session_search 無 quality score，無法做 ranked filtering

**可行動下一步**：在 `/root/.hermes/workspace/session_state.md` 加入 `# Tool Registry` 段落，定義 Hermes 目前 20+ tools 的 capability schema（input types, output types, trust level, volatility）。這是 schema 顯式化的第一步，後續 session_search 回傳結構加 rank_score、heartbeat decisions 用 JSON schema 都基於這份 registry。

---

## Cross-Cutting Theme 2: 工具隔離的兩個維度——功能隔離 vs 安全隔離——正在合流

**支援筆記**: agent-governance-patterns, RAIL-Hermes-Architectures-HN-Anti-AI

**分析**：

一條線索在 agent-governance-patterns 的 AWS 原則和 ACE architecture：Firecracker micro-VM、AgentCore Gateway、data/capability barriers——這些是**安全隔離**（防 prompt injection、防 data leakage）。

另一條線索在 RAIL-Hermes 的 HN anti-AI thread：CSS honey-pot 的核心思路是「把正常用戶和 agent 放在不同的執行沙盒裡」——這是**功能隔離**（讓 agent 只能看到 sanitized surface，無法接觸 hidden state）。

這兩條線的交匯點：**Hermes 的 sanitize_fetch.py 正在同時做安全隔離和功能隔離**。它去除 zero-width chars、normalize HTML、strip tracking——這些本來是「讓 agent 不要被垃圾資訊干擾」，但實際上也降低了 prompt injection 的隱藏表面積。

更大的 pattern：HN thread 中 `akomtu` 的 honey-pot 和 AWS 的 Security Box 是同一個設計哲學的兩個表達——**不要試圖教育 agent 避開什麼，而是把危險隔離在 agent 的執行範圍之外**。

這對 Hermes 的直接啟發：`heartbeat_action_log.jsonl` 裡的 tool calls 目前沒有任何 isolation boundary——每個 tool call 都在同一個 context window 裡執行。一個 tool 的 error 可以汙染整個 action sequence（這是 R²-Mem 的 corrective experience pattern）。ACE 的兩階段 planning（abstract plan → concrete plan）提供了方法：先把 plan 映射成 tool call sequence（無執行風險），再執行——這把 planning 和 execution 的 isolation boundary 前移了。

**可行動下一步**：在 heartbeat 的 Phase 1 plan output 中加入 `proposed_tool_sequence[]`——在實際執行 tool calls 之前，先把整個 sequence 的 tool names + parameters 完整列出並寫入 decision log。這讓 `heartbeat_learning.py` 可以做 plan-level 的 retrospective analysis（為什麼這組 tool sequence 解決了/沒解決問題），而不只是 event-level 的 pattern counting。

---

## 優先排序

| Priority | Theme | Action | Complexity |
|----------|-------|--------|------------|
| P0 | Theme 1 | Tool Registry schema（第 1 步：寫出 /root/.hermes/workspace/session_state.md Tool Registry 段落） | 低 |
| P1 | Theme 2 | Heartbeat Phase 1 產出 proposed_tool_sequence | 中（需修改 heartbeat action sequence 產生邏輯） |