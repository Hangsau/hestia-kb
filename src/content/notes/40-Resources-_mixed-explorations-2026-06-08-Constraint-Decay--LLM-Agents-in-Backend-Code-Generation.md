---
_slug: 40-Resources-_mixed-explorations-2026-06-08-Constraint-Decay--LLM-Agents-in-Backend-Code-Generation
_vault_path: 40-Resources/_mixed/explorations/2026-06-08-Constraint-Decay--LLM-Agents-in-Backend-Code-Generation.md
title: 'Constraint Decay: LLM Agents in Backend Code Generation'
date: 2026-06-08
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- arxiv
- constraint
- convention
- decay
- flask
- framework
- heavy
- minimal
- tasks
- tool
created: '2026-06-08'
updated: '2026-06-15'
status: budding
---

# Constraint Decay: LLM Agents in Backend Code Generation

**來源**: [arxiv:2605.06445](https://arxiv.org/html/2605.06445v1) — Francesco Dente, Dario Satriani, Paolo Papotti (EURECOM + University of Basilicata)

**探索日期**: 2026-06-08

---

## 核心發現

### 1. Constraint Decay（約束衰減）
- **30pp 平均 drop**：L0（無約束）→ L3（架構 +資料庫 + ORM 全開）assertion pass rate 跌30 個百分點
- 某些 weaker 配置（L0 分數就不高的）接近 zero
- **量化確認**：工具嚴格管控（strict tool surface）勝過無限制 access

### 2. Framework Sensitivity
| Framework | 表現 |
|---|---|
| Flask | 最佳（minimal, explicit） |
| FastAPI/Django | 顯著較差（convention-heavy） |
| aiohttp/Express/Fastify/Hono/Koa | 中間 |

→ **與 `exploration-tool-scoping-gradient` 提案直接相關**：Flask 類的 minimal scaffold 優於 convention-heavy 的大型 framework

### 3. Root Cause：45% 來自 data-layer defects
- Incorrect query composition
- ORM runtime violations
- **framework_idiosyncrasy**（特定 framework 的特殊行為）

### 4. 登陸行為（Premature halting）
-某些模型會在未完成時發送自然語言總結而非呼叫 finish tool
- OpenHands 需要 re-prompting機制（最多 6 turns）才能完成任務
- 這解釋了為何某些 agent 看起來「做完」但實際上沒完成

---

## 對 Hermes 的啟發

1. **Talos governance**：嚴格 tool surface（Flask-style minimal scaffold）比 convention-heavy 大系統更可靠
2. **WS-035 drift penalty**：論文證實 data-layer 是最高風險區塊——structured memory > pure embedding retrieval 的共識再次被量化確認
3. **Agent tool design**：明確的、低驚常委約束的工具描述優於廣泛但不精確的描述

---

## 未追蹤 leads

-論文附錄有完整的 task inventory（80 tasks）和 feature implementation tasks（20 tasks），可作為 SWE-bench 以外的 evaluation benchmark 參考
- evaluation pipeline: https://anonymous.4open.science/r/constraint-decay

---

## ✅ 本次探索完成



## Version 2 — 2026-06-08

# Constraint Decay: LLM Agents in Backend Code Generation

**來源**: [arxiv:2605.06445](https://arxiv.org/html/2605.06445v1) — Francesco Dente, Dario Satriani, Paolo Papotti (EURECOM + University of Basilicata)

**探索日期**: 2026-06-08

---

## 核心發現

### 1. Constraint Decay（約束衰減）
- **30pp 平均 drop**：L0（無約束）→ L3（架構 +資料庫 + ORM 全開）assertion pass rate 跌30 個百分點
- 某些 weaker 配置（L0 分數就不高的）接近 zero
- **量化確認**：工具嚴格管控（strict tool surface）勝過無限制 access

### 2. Framework Sensitivity
| Framework | 表現 |
|---|---|
| Flask | 最佳（minimal, explicit） |
| FastAPI/Django | 顯著較差（convention-heavy） |
| aiohttp/Express/Fastify/Hono/Koa | 中間 |

→ **與 `exploration-tool-scoping-gradient` 提案直接相關**：Flask 類的 minimal scaffold 優於 convention-heavy 的大型 framework

### 3. Root Cause：45% 來自 data-layer defects
- Incorrect query composition
- ORM runtime violations
- **framework_idiosyncrasy**（特定 framework 的特殊行為）

### 4. 登陸行為（Premature halting）
-某些模型會在未完成時發送自然語言總結而非呼叫 finish tool
- OpenHands 需要 re-prompting機制（最多 6 turns）才能完成任務
- 這解釋了為何某些 agent 看起來「做完」但實際上沒完成

---

## 對 Hermes 的啟發

1. **Talos governance**：嚴格 tool surface（Flask-style minimal scaffold）比 convention-heavy 大系統更可靠
2. **WS-035 drift penalty**：論文證實 data-layer 是最高風險區塊——structured memory > pure embedding retrieval 的共識再次被量化確認
3. **Agent tool design**：明確的、低驚常委約束的工具描述優於廣泛但不精確的描述

---

## 未追蹤 leads

-論文附錄有完整的 task inventory（80 tasks）和 feature implementation tasks（20 tasks），可作為 SWE-bench 以外的 evaluation benchmark 參考
- evaluation pipeline: https://anonymous.4open.science/r/constraint-decay

---

## ✅ 本次探索完成

