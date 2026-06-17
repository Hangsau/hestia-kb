---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-2230-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-2230-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: high
title: 觀測盲區：Heartbeat 知道系統活著，不知道系統有用
updated: '2026-06-15'
type: research
status: budding
---

# 觀測盲區：Heartbeat 知道系統活著，不知道系統有用

**消化筆記**: 2026-05-15-agent-observability-evaluation

本次僅 1 篇未消化筆記，但與已消化筆記間存在明顯的跨主題連結。核心發現：Hermes 的 observability 投資偏重在「基礎設施存活」而非「行為品質」，且這個盲點被多篇筆記從不同角度反覆指出。

---

## Cross-Cutting Theme 1: 行為品質盲點 — Heartbeat 偵測不到 agent 變笨

**支援筆記**: `2026-05-15-agent-observability-evaluation`, `2026-05-14-hermes-heartbeat-project-proposal`, `2026-05-13-hermes-testing-infra-analysis`, `2026-05-13-研究報告-ai-agent-的自我糾錯與反思機制-2026-年中全景`, `2026-05-13-hermes-core-testing-infra`

### 分析

這次的未消化筆記把 agent observability 拆成四層：產品分析層（Voker 的 intent/correction/resolution）→ 任務評估層（Cua-Bench 的 task completion）→ 技術健康層（Heartbeat 的 error rate/severity）→ 開放遙測層（OpenLLMetry 的 span/trace）。Hermes 只有第三層。

但這不是新聞——它被三篇獨立筆記從不同角度反覆指出：

1. **Heartbeat 提案書**（2026-05-14）自己就說：「不是監控 agent 回應品質好不好，有沒有幫到使用者」。這是自知之明。
2. **測試基礎建設分析**（2026-05-13）記錄了一個**真實生產事故**：`managed-agents-framework` 的 `ma run` 因路徑變更損壞，heartbeat 完全沒發現。這不是 hypothetical 風險，是已發生的盲區事故。
3. **自我糾錯研究**（2026-05-13）從學術角度論證：LLM 的自評不可靠（LoopTrap 的信任邊界問題），需要獨立 Critic 節點來做行為評估。

四篇筆記疊在一起才浮現的 pattern：**Heartbeat 的 EVOLVE 只跑 pytest（測試 heartbeat 自己的邏輯是否正確），不測 Hermes 的行為是否正確**。差別在於——pytest 告訴你 `score_actions()` 有沒有回傳正確的 dict，但不會告訴你 Hermes 回答使用者的品質有沒有退化。

### 為什麼這不是「值得研究」

因為已經有現成的解法元件，只是沒被組裝：

- Voker 的 **correction detection** 概念（使用者在哪裡糾正 agent）可以直接轉化為 heartbeat 的新 sensor：掃 session log 中 agent self-correction 的頻率，高於閾值 → flag。
- 自我糾錯研究的 **Critic 架構**（SAGE 的 Evidence Critic、LangValidator 的 scorer）提供實作藍圖。
- 測試基礎建設筆記的 **core testing infra** 已經證明「pytest canary 嵌入 heartbeat EVOLVE」的模式可行（51 tests, 0.20s）。

### 可行動下一步

**在 heartbeat EVOLVE 加入「行為退化 canary」**：

1. 建立 5 個固定任務（如「幫我查今天天氣」「把這段文字翻成英文」「解釋 git rebase」），每個任務附預期結果的結構化 spec（不是精確文字，而是「必須包含 X 資訊、不能包含 Y 錯誤」）。
2. 在 EVOLVE 週期（每 6h）跑一輪，用輕量模型（Gemini Flash）當 Critic，評分後記錄到 `heartbeat_action_log.jsonl`。
3. 連續 3 次評分低於閾值 → REPORT 升級通報。

**規模**：~150 行 Python + 5 個 YAML spec 檔。零新依賴。可復用現有 `action_evolve` 的 dry-run/cooldown 框架。

---

## Cross-Cutting Theme 2: 觀測協議碎片化 — 每個訊號都用自己的格式

**支援筆記**: `2026-05-15-agent-observability-evaluation`, `2026-05-14-hermes-heartbeat-project-proposal`, `2026-05-14-hermes-cost-visibility`

### 分析

把 Hermes 現有的 observability 訊號攤開：

| 訊號 | 格式 | 消費者 |
|------|------|--------|
| 系統健康 | `heartbeat_state.json`（自訂 schema） | heartbeat 自己 |
| 行動記錄 | `heartbeat_action_log.jsonl`（自訂 schema） | learning-extraction skill |
| 成本追蹤 | `cost_aggregator.py` SQL 聚合 + Markdown | 手動查詢 |
| Shutdown 診斷 | `shutdown_*.md`（自訂 Markdown） | 手動查閱 |

每一種都是為單一用途設計的自訂格式。這在單 agent 情境完全合理（「一個人用的 agent，不需要 export 到 Datadog」— observability eval 筆記自己說的）。但 OpenLLMetry 的賭注顯示了一個更長遠的趨勢：LLM observability 正在走向標準化（OTel LLM semantic conventions 即將進入官方標準）。

**Heartbeat 提案書 Phase 5 的願景**（「定義 agent health state 的標準格式」）和 OpenLLMetry 的標準化工作**正在朝同一個方向收斂**，只是出發點不同：Heartbeat 從 autonomic loop 出發，OpenLLMetry 從 distributed tracing 出發。

這不是說 Hermes 現在就該接 OTel。而是說：當你要設計下一個 observability 訊號時（比如 Theme 1 的 behavioral canary 分數），用 OpenLLMetry 的 `gen_ai.*` semantic convention 作為欄位命名參考，成本為零，未來可移植性為正。

### 可行動下一步

**採用 OTel LLM semantic conventions 作為新訊號的命名參考**：

1. 從 [OpenLLMetry 的 semantic conventions 草案](https://github.com/traceloop/openllmetry-js) 擷取相關欄位（`gen_ai.request.model`、`gen_ai.usage.input_tokens`、`gen_ai.response.id` 等）。
2. 在下一版 `heartbeat_state.json` schema 擴充時（例如加入 Theme 1 的 behavioral canary 分數），用 OTel 命名慣例而非自訂命名。
3. 不需要接 OTel collector——純命名約定，零 runtime 成本。

---

## 不重複既有 Consolidation 的邊界

- `2026-05-15-1900` 的 DeepSeek Cache 主題：無關。
- `2026-05-15-2100` 的防禦姿態倒置：無關。
- `2026-05-15-1700` 的 MCP Gateway：無關。
- `2026-05-15-1303` 的架構漏洞：無關（行為品質盲點是 design gap，不是 security vulnerability）。
