---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-18-0500-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-18-0500-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-18'
confidence: high
title: Hermes 自主探索整合：跨主題洞察
updated: '2026-06-15'
type: research
status: budding
---

# Hermes 自主探索整合：跨主題洞察

**消化筆記**: orloj-blueprints-mcp-sealedsecret, zerostack-semble, agent-memory-persistence-deep-dive, axe-orloj-moltis-agent-infra-paths, orloj-governance-deep-dive, axe-orloj-moltis-deep-dive

六篇筆記覆蓋三個維度：工作流拓撲（hierarchical DAG / swarm-loop / pipeline）、治理層（policy / permission / approval）、自主維護（heartbeat / doom-loop / memory GC）。以下是cross-cutting synthesis。

---

## Cross-Cutting Theme 1: 限制性系統的fail-closed遞進模式

**支援筆記**: zerostack-semble, orloj-governance-deep-dive, axe-orloj-moltis-deep-dive

### 分析

看似無關的兩個系統——Zerostack 的 doom-loop detection 和 Orloj 的 governance pipeline——其實共享同一個底層邏輯：**限制性預設 + 觸發後遞進收緊**。

**Zerostack**：
- 4-level permission system（restrictive → yolo）
- Doom-loop detection：3+ 相同 tool call → warning → denial
- `max_entries` 到期 → warn（不自動trim）

**Orloj governance**：
- AgentPolicy check → ToolPermission lookup → permission matching → Denied（fail-closed）
- `verdict` 優先序：`deny > approval_required > allow`（most restrictive wins）
- SealedSecret controller：target Secret 已存在但無 ownership annotation → fail closed（`Error` phase）

**共同模式**：
```
[常態] → [門檻觸發] → [限制升級]
doom-loop: 3次相同tool call → denial
Orloj permission: 缺少必要权限 → Denied（不降級）
SealedSecret: 無owner annotation → Error（不覆寫）
```

這三個系統都選擇「觸發時 deny」而非「觸發時 warn + 降級」。Axe 的 memory GC 是個對比——`max_entries` warn 但不自動 trim，介於兩者之間。

**對 Hermes 的意義**：目前 heartbeat 的 EVOLVE 步驟沒有 doom-loop detection，治理只有 `enabled_toolsets` 簡單 allowlist，SealedSecret 根本沒有。整個「限制→觸發→遞進收緊」的設計模式在 Hermes 是空白。

### 可行動下一步

在 `heartbeat/actions.py` 新增 `check_doom_loop()`：追蹤每個 tool call 的重複次數，3+ 次相同 tool name → 發 warning event 並 increment `consecutive_deny_count`。同時在 `actions.py` 的 action registry 裡登記 `doom_loop_reset`——每次成功的 multi-step 推理後 reset counters。這是確定的 counter-based 邏輯，不需要 LLM 判斷。

---

## Cross-Cutting Theme 2: 統一檢索層——BM25+Embedding融合是Hermes的盲點

**支援筆記**: zerostack-semble, agent-memory-persistence-deep-dive, axe-orloj-moltis-deep-dive

### 分析

三個系統獨立演化出相同的技術組合：

**Semble（code search）**：
- BM25（lexical）+ Model2Vec static embeddings（semantic）+ RRF 融合
- Adaptive weighting：symbol-like queries 加重 lexical，natural language queries 平衡
- 263ms index、1.5ms query、NDCG@10 = 0.854

**StixDB（agent memory）**：
- `0.7 × semantic + 0.3 × keyword` 融合
- 另有純 keyword 模式（~5ms，no API call）和純 semantic 模式

**MuninnDB（memory + confidence）**：
- 6-phase Activate pipeline，每 phase 有明確的貢獻權重
- Provenance + freshness 是 query time 一等欄位

三者都發現：**純 lexical 召回不足，純 semantic 缺精確**。RRF 融合是標準解法，且代價可控（BM25 不需要 GPU、不需要 API key）。

**但 Hermes 的現實**：
- `search_files`（ripgrep backend）是純 lexical
- `session_search` 是 full-text，無 semantic 維度
- `exploration_graph` 是 wikilink 關係圖，無 embedding
- 三個工具三個底層引擎，沒有共享的統一檢索層

**對 Hermes 的意義**：如果要在 code search、memory retrieval、exploration graph 之間共享一個底層檢索引擎，BM25+embedding RRF 是正確架構（不是向量資料庫 overkill 路線）。Semble 已經是 production-ready 的實現，pip install 即可。

### 可行動下一步

先做對比實驗：`pip install semble`，透過 MCP tool 接入 Hermes，跑 10 個 routine code search task（用 `semble search`），對比 `search_files` 的 token 消耗和延遲。如果 token savings > 80%，直接將 Semble 作為 Hermes 的 standard code search MCP tool，同時評估將 `session_search` 和 `exploration_graph` 的底層替換為同一個 BM25+embedding 引擎的可行性。

---

## Cross-Cutting Theme 3: 治理的scope階層 vs Hermes的flat config

**支援筆記**: orloj-governance-deep-dive, orloj-blueprints-mcp-sealedsecret, axe-orloj-moltis-agent-infra-paths

### 分析

Orloj 的 governance 有明確的 scope 階層：

```
AgentSystem（整圖）
  → Task（子範圍）
    → Agent（最細粒度）
```

三層都支援 `apply_mode: global | scoped`。同一個 governance resource 可以對整個 system 生效，也可以精確 targeting 到特定 agent。

**具體例子**：per-agent token budget：
```yaml
target_agents: [verdict-agent]
max_tokens_per_run: 4000
---
target_agents: [velocity-analyst, geo-risk-analyst]
max_tokens_per_run: 1500
```

**Hermes 的現實**：cron job 層級的 `enabled_toolsets`，只能做最粗粒度控制。沒有 system/task/agent 三層，也沒有 per-agent budget。

**與工作流拓撲的隱藏連結**：Orloj 的 AgentSystem graph（nodes = agents, edges = message flow）和 governance scope 是在同一個 CRD 框架下管理。也就是說，**工作流拓撲定義在哪裡，治理範圍就綁在哪裡**。Hermes 的 proposals/`graph` block（如果未來實作）和 governance policy 是分離的兩套系統。

### 可行動下一步

在 `talos-governance-pipeline-blueprint.md` 裡新增 **scope 階層提案**，明確定義 system → task → agent 三層的 apply 語義，並在 blueprint 的 policy enforcement point 加上 scope matching logic。這是 governance blueprint 的下一次迭代，不是現在就要實作，但是確立方向的必要一步。
