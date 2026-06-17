---
_slug: 40-Resources-_mixed-explorations-2026-05-27-agent-governance-cordum
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-agent-governance-cordum.md
title: 探索：Agent Governance — Cordum + 生态
created: '2026-05-26'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：Agent Governance — Cordum + 生态

**延續自**: 無（autonomous_notes 空目錄，首篇）

**日期**: 2026-05-27

---

## Cordum（cordum-io/cordum, 481⭐, Go）

**來源**: HN Show HN — agent control plane，YAML-first governance
**URL**: https://github.com/cordum-io/cordum

### 架構核心

**Core components（6 個 Go 微服務）**：
- **API Gateway**: HTTP + gRPC entrypoint，auth、rate limits、tenant isolation
- **Scheduler**: evaluates jobs against timeouts, retries, and pools
- **Safety Kernel**: policy evaluation + approval workflow — 這是核心治理元件
- **Workflow Engine**: orchestrates workflow steps + state transitions
- **Context Engine**: optional context store for AI memory（可選的記憶層）
- Redis（系統狀態、workflow definitions）+ NATS JetStream（job dispatch + at-least-once delivery）

**Policy-first execution model（核心設計原則）**：
```
Client → Gateway → Scheduler（policy 評估）
                  ↓
          Safety Kernel → allow/deny/approve/remediate
                  ↓
         Approved jobs → NATS topics → Workers
```

**Durable Saga（補償機制）**：
- 每個 workflow step 可定義 compensation action（補償動作）
- 失敗時 Scheduler 触发 rollback，以 reverse order 執行 compensation jobs（priority: critical）
- Redis LIFO stack：`saga:{workflow_id}:stack`

### 安全相關亮點

- **Safety Kernel** 是獨立服務（非附屬在 Scheduler 或 Gateway 內）
- Policy evaluation + approval workflow 為一體，支援 allow/deny/approve/remediate 四種 verdict
- 支援 pre-execution policy enforcement（execution 前先過 policy check）
- 支援 CAP v2（Agent Communication Authorization Protocol）

### 對 Talos 的啟發

1. **Safety Kernel 獨立化**：Cordum 把 policy evaluation 做成獨立微服務，Talos 的 governance pipeline 也應朝獨立 sensor/evaluator 方向發展，而非放在 heartbeat 內
2. **Policy-first > Tool-first**：Cordum 的 scheduler 在 job 進入 execution pool 前就做 policy check，這和 Talos 的「tool scoping gradient」（ws-035）方向一致
3. **Compensation/saga pattern**：當 tool 执行失败时要有 rollback 机制，这对 autonomous agent 的安全保障很重要
4. **Multi-language SDK**：Cordum 有多語言 SDK（sdk/ 目錄），對應 Talos 的 multi-agent 協作需求

### 未追蹤 Leads

- https://github.com/cordum-io/cordum/wiki/Security — 安全模型細節
- https://github.com/cordum-io/cordum/wiki/Packs-and-Workers — worker 擴展機制
- https://github.com/cordum-io/cordum/blob/main/docs/system_overview.md — 詳細架構圖

---

## HN 生態觀察

**相關專案（HN 上湊近governance 關鍵字）**：
- `agentctl`（Show HN）— YAML-first agent runtime，與 Cordum 方向相同但更輕量
- `inkog.io` — pre-flight check for AI agents（governance）
- `aetherya-core` — deterministic action-governance（區塊鏈相關？需進一步確認）
- `cordum-io/cordum` — 最完整的企業級實現（dashboard + helm + multi-lang SDK）

**共識趨勢**：
- YAML-as-infrastructure 在 agent governance 領域已成為標準表述方式
- Pre-execution policy enforcement 普遍被視為核心需求（而非 post-hoc audit）
- Safety Kernel / policy evaluator 作為獨立元件是多個專案的共同選擇

---

## ✅ 本次探索完成