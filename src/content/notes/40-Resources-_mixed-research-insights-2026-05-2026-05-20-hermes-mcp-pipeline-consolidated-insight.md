---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-20-hermes-mcp-pipeline-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-20-hermes-mcp-pipeline-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-20'
confidence: high
title: Hermes WS-019/WS-020 實作路徑：MCP 介面層 + Declarative Pipeline 層
updated: '2026-06-15'
type: research
status: budding
---

# Hermes WS-019/WS-020 實作路徑：MCP 介面層 + Declarative Pipeline 層

**消化筆記**: 2026-05-20-mcp-agent-hermes-pipelex-write-queue, 2026-05-20-mcp-agent-agent-as-mcp-server-deep-dive, 2026-05-20-axe-memory-system-orloj-hierarchical-blueprint, 2026-05-20-axe-gc-dead-orloj-agent-system

（今日四篇筆記全部來自同一批 research session，聚焦於 WS-019（MCP 介面）和 WS-020（orchestration）。MCP-agent 提供了 Herme s現有整合的升級路徑；Orloj + Pipelex 共同指向 declarative typed pipeline 的設計方向。）

## Cross-Cutting Theme 1: MCP 是 Hermes 介面層的唯一正確選擇

**支援筆記**: 2026-05-20-mcp-agent-hermes-pipelex-write-queue, 2026-05-20-mcp-agent-agent-as-mcp-server-deep-dive

**分析**:

兩篇筆記從不同角度抵達同一個結論：不用自己實作 MCP protocol，直接用 `mcp-agent` library。具體來說：

- `create_mcp_server_for_app(app)` 把整個 Hermes app 暴露成標準 MCP server，tools 用 decorator 自動映射
- Hermes 現有的 `native-mcp` 整合只需加一層 stdio transport + server wrapper
- WS-019 不需要「評估哪種 interface protocol」，答案已經確定了

`@app.tool` / `@app.async_tool` / `@app.workflow` 三層裝飾器對應了 Herme s工具的實際使用模式：同步（terminal/檔案）、異步（長時任務）、宣告式（multi-step pipeline）。

**可行動下一步**: 
1. 今晚跑一次 `mcp-agent` asyncio example 確認 SDK import 可用（`uvx --from "mcp-agent" mcp-agent` 或 Python import 測試）
2. 若可用，立即對 `/root/.hermes/scripts/` 中的一個簡單 script 做 `@app.tool` 包裝實驗
3. 確認通過後在 WS-019 提案中把實作路徑鎖定為 `mcp-agent asyncio mode`

---

## Cross-Cutting Theme 2: WS-020 需要 Declarative + Typed Pipeline 定義，而非 Imperative Write Queue

**支援筆記**: 2026-05-20-axe-memory-system-orloj-hierarchical-blueprint, 2026-05-20-mcp-agent-hermes-pipelex-write-queue

**分析**:

`write queue` 這個命題被 Pipelex 和 Orloj 共同否定：

- **Pipelex**：typed `.mthds` 格式，input/output 有類型合約，batch_over 做 list → sub-pipe map-reduce，而不是 queue
- **Orloj**：`agent-system.yaml` 宣告式 DAG，task `input` 有 schema 定義，`message_retry` 在 sub-message 層（比 Hermes 目前的 tool-level retry 更細粒度）

兩者都指向同一個 design shift：從「imperative file-based queue」升級為「typed declarative pipeline with schema」。好處：
- 圖層可驗證（YAML schema 在跑之前就能 catch 錯誤）
- join mode 可配置（`wait_for_all` / `first_complete` / `threshold(N)`）
- model routing 可嵌入（各 pipeline 步驟指定不同 model）
- batch processing 是 first-class

**可行動下一步**:
1. 在 WS-020 提案中加入 `join.mode` 替代方案（`wait_for_all`、`first_complete`、`threshold(N)`），而非只有 fan-out
2. 定義 Hermes pipeline 的 input/output type schema prototype（以一個實際 cron job 為例）
3. 評估 `message_retry` 從 tool-level 升級到 sub-message-level 的實作成本

---

## Cross-Cutting Theme 3（Low-confidence 推測）: Pattern Graduation + MCP = Autonomous Skill Evolution

**支援筆記**: 2026-05-20-axe-memory-system-orloj-hierarchical-blueprint, 2026-05-20-mcp-agent-agent-as-mcp-server-deep-dive

**分析**:

這條線是推測，需要更多驗證，但有結構上的連結：

- **Axe** 的 design：memory GC → pattern detection → suggestion → human approval → SKILL.md update。這是 skill 的 feedback loop。
- **mcp-agent** 的 design：`@app.workflow` 是宣告式 workflow entry point，可被外部 client（MCP client）呼叫。

兩者合起來：「GC 發現的 pattern → 產生 skill update workflow → 透過 MCP workflow 暴露 → 人類/另一個 agent 審批 → 更新 SKILL.md」。這讓 skill system 從靜態文件變成「活的、可被外部觸發更新的系統」。

**可行動下一步**:
- 先把 Theme 1 和 Theme 2 做實驗驗證，Pattern Graduation 可以是 Phase 2，不影響當前 WS-019/WS-020 的優先順序

---

## 備註：Axe GC 404 不影響結論

`2026-05-20-axe-gc-dead-orloj-agent-system` 確認了 axe memory system 的 design principle，GC 演算法細節可從 Orloj 文件補足。Pattern Graduation 的 design direction 在 `axe-memory-system-orloj-hierarchical-blueprint` 已充分論述。