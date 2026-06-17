---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-OrcBot---Atom-自主代理框架---SAGA-ACE-延續
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-OrcBot---Atom-自主代理框架---SAGA-ACE-延續.md
title: 探索：OrcBot + Atom 自主代理框架 — SAGA/ACE 延續
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- atom
- graduation
- heartbeat
- hermes
- level
- orcbot
- repair
- self
- supervisor
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：OrcBot + Atom 自主代理框架 — SAGA/ACE 延續

**延續自**: [[探索---2026-05-23-Agent-安全框架縱橫比]]
**延續自**: [[saga-ace-synthesis-20260523]]

**日期**: 2026-05-23
**類型**: 架構研究
**來源**: GitHub raw README

---

## OrcBot v2.1 — Strategic Autonomous Agent

TypeScript + ReAct，自帶完整自主迴圈。重點看點：

**Runtime Supervisor Loop**：
- Failed batches trigger immediate re-planning（不等下一個 heartbeat）
- Repeated failed tool signatures are suppressed（circuit breaker）
- Blocked-plan repair before execution

這個模式和 Hermes 的 EVOLVE + do-over action 相比：
- Hermes：heartbeat level 的 supervisor（每 cycle 一次）
- OrcBot：每個 batch 內的 supervisor（更即時，但代價是更頻繁的 LLM 調用）

**Smart Heartbeat**：
- Context-aware autonomy with exponential backoff
- Productivity tracking
- Action-oriented tasks

比 Hermes heartbeat 多了 productivity tracking（追蹤效率）和 action-oriented tasks（目標導向）。Hermes 目前只有被動健康檢查，沒有「這個 cycle 做了什麼有意義的事」的追蹤。

**Autonomous Immune System**：
- 自動偵測 broken plugin code
- 使用 `self_repair_skill` 自我修復

這個比 Hermes 更即時——Hermes 的「自我修復」依賴 heartbeat cycle 觸發，OrcBot 是 plugin-level 的 fail → detect → repair chain。

---

## Atom Platform — Multi-Agent Self-Hosted Platform

Python + FastAPI + PostgreSQL/LanceDB，強調 self-hosted、single-tenant、無限制使用。

**Meta-Agent Routing System**：
三層 intent 分類：CHAT / WORKFLOW / TASK
- CHAT：簡單查詢，直接 LLM
- WORKFLOW：結構化流程，QueenAgent 處理 blueprint
- TASK：複雜任務，FleetAdmiral 招募多 agent

這個 routing 層是 Hermes 目前完全沒有的。Hermes 的 every session 都是同一個 agent 處理，沒有根據任務複雜度分流的概念。

**Experience-Based Learning + Graduation**：
- Recursive self-evolution
- Dual-trigger graduation: SUPERVISED → AUTONOMOUS
- Hybrid PostgreSQL + LanceDB storage（向量檢索）
- Agent graduation guide（agent 的成熟度分級）

**Agent Governance System**：
- 4-tier maturity-based routing and approval
- Every action logged, timestamped, and traceable

這個完全對應 SAGA 的 access control token 概念——agent 到了一定 maturity 才能解鎖某些操作。Hermes 的 OTP gate 是最簡化版本，Atom 的 4-tier graduation 是 production 版本。

**Knowledge Graph + GraphRAG**：
- BFS traversal for recursive knowledge retrieval
- Canonical anchoring to database records
- Bidirectional sync

---

## Hermes 的借鑒點

| Pattern | OrcBot | Atom | Hermes 目前 |
|---------|--------|------|-------------|
| Batch-level supervisor | ✅ runtime supervisor | — | ❌ |
| Per-batch re-plan | ✅ | — | ❌ |
| Intent classification | — | ✅ CHAT/WORKFLOW/TASK | ❌ |
| Agent maturity graduation | — | ✅ 4-tier | ❌ (OTP 算最簡版) |
| Productivity tracking | ✅ | — | ❌ |
| Self-repair (plugin level) | ✅ | — | ❌ (script level) |
| Action logging + trace | — | ✅ | Partial |
| GraphRAG | — | ✅ | Partial (FTS5) |

**最高價值**：Atom 的 **intent routing** 和 **4-tier agent governance** 直接是 Hermes 未來架構的藍圖。OrcBot 的 **runtime supervisor loop** 是 Hermes heartbeat supervisor 的下一個 level。

---

## 未追蹤 Leads

- OrcBot v2.1 完整架構文件: https://github.com/fredabila/orcbot/blob/main/docs/architecture.md
- Atom agent graduation guide: https://github.com/rush86999/atom/blob/main/docs/DEVELOPMENT/AGENT_GRADUATION_GUIDE.md
- OrcBot self-repair skill implementation: https://github.com/fredabila/orcbot/blob/main/skills/self_repair_skill.md

---

## ✅ 本次探索完成
