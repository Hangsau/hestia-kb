---
_slug: 40-Resources-_mixed-explorations-2026-05-25-multi-agent-langchain-continuation
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-multi-agent-langchain-continuation.md
title: 2026-05-25 Multi-Agent Systems — LangChain Blog續論
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-05-25 Multi-Agent Systems — LangChain Blog續論

**延續自**: [[2026-05-25-multi-agent-governance-blind-spot]]

**來源**: [LangChain Blog: How and when to build multi-agent systems](https://blog.langchain.com/how-and-when-to-build-multi-agent-systems/) | Harrison Chase | 2025-06-16

## Per-Source Insights

### LangChain: Multi-Agent Architecture 官方觀點

**核心主旨**：LangChain 官方認為 multi-agent 的關鍵在於 context engineering，而非 framework 選擇。

#### Key insights

1. **Context engineering is the #1 job**
   - 2025 年的模型非常聰明，但即使是再聰明的人，沒有 context 也無法有效工作
   - 「Prompt engineering」→「Context engineering」是必然進化
   - Multi-agent 架構讓 context distribution 更困難（每個 sub-agent 需要什麼 context？誰決定？）

2. **Read vs Write 的不對稱性**
   - Read-heavy 任務更容易 parallelize（研究、搜尋、比較）
   - Write-heavy 任務 conflict 成本高（「Actions carry implicit decisions, and conflicting decisions carry bad results」）
   - Anthropic Claude Research 的設計：multi-agent 處理 research（read），single main agent 處理 writing（synthesize）——刻意避免 multi-agent write

3. **Sub-agent 需具體的 task description**
   - 早期實驗：簡短指令如 "research the semiconductor shortage" 導致重複工作
   - 每個 subagent 需要：objective + output format + tools/sources guidance + clear boundaries
   - 沒有精確定義邊界時，agents 會 duplication 或 gaps

4. **Durable execution 是標配**
   - Agents 是 stateful，錯誤會 compound
   - 不能從頭重來——需要從 error 發生的位置恢復
   - 這是 LangGraph 的核心設計目標

5. **Multi-agent 的經濟條件**
   - `token 用量規模化`：multi-agent 有效是因為它幫助花費足夠多的 tokens 來解決超出單一 agent 限制的任務
   - 經濟可行條件：任務價值 > 增加的基础設施成本
   - 不適合：需要所有 agents 共享同一 context、或有高度依賴關係的領域

---

## Hermes 啟發

### Talos-Hestia 架構的啟示

**Read/Write 分離原則**：Hestia（研究者）vs Talos（守護者/決策者）的角色分工，可以對應到 Claude Research 的模式：
- Hestia = research agents（read-heavy，parallel exploration）
- Talos = synthesizer/main agent（最終 decision 統一在 Talos）

但目前的實作問題：Hestia 和 Talos 都同時有 read 和 write 能力，界線不明確。

**Context boundary 的實際問題**：
- 前期筆記（governance blind spot）提到的「Talos 從 Hestia 接收 task context，若超出 Talos authorization scope，沒有 gate 機制」
- LangChain 說「每個 subagent 需要 objective + output format + tools guidance + clear boundaries」——這正好是 Hestia→Talos delegation 缺少的

**Durable execution 的借鑒**：
- 目前錯誤恢復靠 session 重建（從 briefing 或 context distillation）
- 真正需要的是「從 agent 錯誤發生的位置恢復」而非「從頭重建整個 context」
- Hermes 的 cron retry 機制（last_run_at tracking）是某種程度實現，但 agent-level 的 checkpoint/resume 尚未實現

### 實際可行的下一步

1. 為 Hestia→Talos 的 task delegation 建立明確的 boundary 規格（不只是 `/plan` 描述，而是結構化 fields：objective、scope、tools、output_format）
2. 審視現有 heartbeat/cron 的 error recovery 是否真的能「從 error 位置恢復」還是「從頭重建」
3. 評估 read-heavy（Hestia 探索）與 write-heavy（Talos 決策）的分流是否已有某種程度的實現

---

## 未追蹤 Leads

- https://www.salesforce.com/news/stories/connectivity-report-announcement-2026/ — Salesforce 2026 Connectivity Benchmark Report
- https://news.ycombinator.com/item?id=47139978 — "I built a governance layer for multi-agent AI coding – lessons after 6 months"
- https://www.waxell.com — Waxell 產品（governance + observability for multi-agent）

## ✅ 本次探索完成