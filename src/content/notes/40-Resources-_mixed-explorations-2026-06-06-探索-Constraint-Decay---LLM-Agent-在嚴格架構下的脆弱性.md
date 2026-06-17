---
_slug: 40-Resources-_mixed-explorations-2026-06-06-探索-Constraint-Decay---LLM-Agent-在嚴格架構下的脆弱性
_vault_path: 40-Resources/_mixed/explorations/2026-06-06-探索-Constraint-Decay---LLM-Agent-在嚴格架構下的脆弱性.md
title: 探索：Constraint Decay — LLM Agent 在嚴格架構下的脆弱性
date: 2026-06-06
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- architecture
- clean
- composition
- constraint
- layer
- llm
- openhands
- orm
- query
created: '2026-06-06'
updated: '2026-06-15'
status: budding
---

# 探索：Constraint Decay — LLM Agent 在嚴格架構下的脆弱性

**日期**: 2026-06-06
**來源**: arxiv:2605.06445v1 (Francesco Dente et al., EURECOM + University of Basilicata)

---

## 核心發現

### Constraint Decay Phenomenon

系統性研究：當 LLM agent 被要求在嚴格結構約束下生成後端系統時（Clean Architecture + PostgreSQL + ORM），效能平均下跌 **30 pp**（assertion pass rate）。

```
L0（無結構約束）→ L3（架構+資料庫+ORM）:
- 最佳配置（OpenHands + MiniMax-M2.5）: 95.6% → 78.6% (-17 pp)
- 最差配置（OpenHands + Qwen3-Coder-Next）: 73.0% → 27.6% (-45.5 pp)
- 8 個 capable 配置平均: -30 pp（相對損失 40% baseline）
```

### 約束維度分析（Marginal Effect）

| 約束 | Avg Δ (pp) |
|------|-----------|
| PostgreSQL | -19.3 ± 2.5 |
| Clean Architecture | -9.1 ± 1.6 |
| SQLite | -14.3 ± 2.5 |
| SQLAlchemy/Sequelize | -1.5 / -0.6（幾乎無影響）|

**資料庫約束是最主要的效能殺手**（-19.3 pp），幾乎是 Clean Architecture 的兩倍。

### Framework Sensitivity

相同 API 合約下，框架選擇造成顯著差異：
- **Flask**（lightweight/explicit）>> **FastAPI/Django**（convention-heavy）
- Agent 在 convention-heavy 環境表現明顯更差

這呼應了 sketch.dev 的 insight：「sed one-liners 對 LLM 來說是災難」——約束越重，agent 越容易崩潰。

### Root Cause: Data-Layer Defects

45% 的邏輯失敗來自資料層：
- 錯誤的 query composition
- ORM runtime violations

這直接解釋了為何架構約束比 ORM 約束更嚴重——ORM 約束反而讓 agent 更清楚該怎麼做（降低 ambiguity）。

---

## 對 Hermes 的啟發

### 1. Tool Scoping Gradient（與 WS-036/AGT 相關）

約束衰減證實：**minimal explicit tooling > comprehensive implicit tooling**。當 agent 的工具集過於龐大（implicit conventions），效能會因為「選項過多但不知道哪個是對的」而下降。

→ 驗證了 `exploration-tool-scoping-gradient` 提案的方向：限制工具集到 4-6 個核心工具，比完整工具集更有效。

### 2. Agent Memory 的 Data-Layer 重要性

45% 的失敗來自資料層——意味著 agent 的記憶系統如果只處理「事實檢索」（Mem0 pattern）而忽視「查詢策略」（query composition）與「runtime 驗證」，會繼承相同的失敗模式。

→ heartbeat_learning.py 的 drift penalty 應關注 **retrieval-layer staleness + query composition consistency**，而非純時間衰減。

### 3. Governance 的代價

Orloj 的 `ToolPermission` + `ToolApproval` 與本研究的發現互補：當 agent 工具集受到嚴格約束（fail closed），效能反而更穩定。代價是增加的審批流程。

→ Talos governance pipeline 選擇「限制工具集」而非「監控所有工具」的正確性獲得實證支持。

---

## 未追蹤 Leads

- arxiv:2605.06445v1 附錄的 agent scaffolds（Mini-SWE-Agent, OpenHands）調整細節
- RealWorld Conduit API 的 benchmark tasks（80 greenfield + 20 feature-implementation）

## ✅ 本次探索完成
