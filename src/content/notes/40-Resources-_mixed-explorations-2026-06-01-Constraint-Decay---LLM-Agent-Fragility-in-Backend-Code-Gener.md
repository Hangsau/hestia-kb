---
_slug: 40-Resources-_mixed-explorations-2026-06-01-Constraint-Decay---LLM-Agent-Fragility-in-Backend-Code-Gener
_vault_path: 40-Resources/_mixed/explorations/2026-06-01-Constraint-Decay---LLM-Agent-Fragility-in-Backend-Code-Gener.md
title: Constraint Decay — LLM Agent Fragility in Backend Code Generation
date: 2026-06-01
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- constraint
- decay
- doom
- layer
- loop
- orm
- swe
- synix
- talos
created: '2026-06-01'
updated: '2026-06-15'
status: budding
---

# Constraint Decay — LLM Agent Fragility in Backend Code Generation

**日期**: 2026-06-01 | **來源**: https://arxiv.org/abs/2605.06445 | **類型**: exploration

## 核心發現

「Constraint decay」是一個新現象：隨著結構約束（架構、資料庫、ORM）增加，agent 表現急劇下降。 capable 配置平均 loss 30 points assertion pass rate（從 baseline 到 fully specified tasks）。這與 WS-018（doom-loop detection）的方向高度相關。

### 核心數據

- **80 個 greenfield 生成任務 + 20 個 feature-implementation 任務**
- **8 個 web frameworks**：Flask, FastAPI, Django, aiohttp（Python） + Express, Fastify, Hono, Koa（Node.js）
- **L0 → L3（遞加約束）**：capable 模型從 ~88%（L0）跌到 ~27%（L3）
- **Root cause**：data-layer defects（incorrect query composition + ORM runtime violations）驅動 ~45% 的邏輯失敗

### Framework sensitivity

- **Flask（minimal, explicit）**：成功率最高
- **FastAPI/Django（convention-heavy）**：平均表現顯著較差

這對 Talos 的「結構化約束 enforcement」方向有直接參考價值：如果連 state-of-the-art agents（SWE-Agent、OpenHands）在 convention-heavy 框架都會失敗，那 Talos 的 enforcement pipeline 設計必須考慮「框架慣例」作為額外約束維度。

### 三層 stack 對 Talos governance 的直接對應

論文揭示的 constraint layers 與 Synix 的三層分解高度吻合：
1. **Architectural pattern**（Clean Architecture）→ 對應 Synix 的 knowledge construction layer
2. **Database backend**（PostgreSQL/SQLite）→ 對應 Synix 的 data infrastructure layer
3. **ORM integration**（SQLAlchemy/Sequelize）→ 對應 Synix 的 data access layer

三層獨立的 eval + agent failure 的事實，說明 enforcement pipeline 必須對三層分別監控，不能只監最後的 behavioral outcome。

## 對 Hermes 的啟發

1. **WS-018 doom-loop detection**：constraint decay 描述的是「隨約束增加，性能下降」——與 doom-loop 的「行為重複、逐漸失效」有概念上的重疊。但 doom-loop 是時序問題，constraint decay 是結構問題。區分：doom-loop 指的是同一任務內 agent 重複相同 action；constraint decay 指的是 agent 面對複雜度 increase 時的失敗模式升級。

2. **Agent scaffolding 的限制**：Mini-SWE-Agent（~100 行 Python）和 OpenHands 都受到 constraint decay 影響，說明 scaffold 複雜度不是 solution，architecture + database + ORM 三層的結構合規才是瓶頸。

3. **驗證方法**：論文用的 dual evaluation（behavioral tests + static verifiers）非常適用於 Talos governance：behavioral tests 對應「有沒有達成目標」，static verifiers 對應「有沒有遵守結構約束」。兩者必須同時滿足。

## 未追蹤 leads

- Mini-SWE-Agent 原始碼（100 行 Python + bash commands）— paper 的附錄 J 有修改細節
- OpenHands re-prompting mechanism 的具體實作（ Appendix J）
- SWE-bench saturated 的最新數據（agents 接近什麼樣的性能上限）

## ✅ 本次探索完成
