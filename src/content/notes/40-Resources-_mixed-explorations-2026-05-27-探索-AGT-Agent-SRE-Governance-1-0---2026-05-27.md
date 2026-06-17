---
_slug: 40-Resources-_mixed-explorations-2026-05-27-探索-AGT-Agent-SRE-Governance-1-0---2026-05-27
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-探索-AGT-Agent-SRE-Governance-1-0---2026-05-27.md
title: 探索：AGT Agent SRE Governance 1.0 — 2026-05-27
date: 2026-05-27
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- budget
- circuit
- error
- governance
- heartbeat
- hermes
- section
- spec
- sre
created: '2026-05-26'
updated: '2026-06-15'
status: budding
---

# 探索：AGT Agent SRE Governance 1.0 — 2026-05-27

**延續自**:
- [[2026-05-27-policy-engine-continuation]]
- [[2026-05-26-mcp-security-gateway-spec-deep-dive]]

---

## Source: Agent SRE Governance 1.0（GitHub raw）

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/specs/AGENT-SRE-GOVERNANCE-1.0.md
**Status**: Draft · 2025-07-28 · Microsoft AGT team
**Length**: 1173 lines (full spec)

### TL;DR — Agent SRE 是什麼

把傳統 SRE 的原則（SLO、error budgets、circuit breakers、chaos engineering、incident management）應用到 AI agent 系統。Agent 的可靠性不再是「感覺很穩」，而是可測量、可強制執行、可持續改進的屬性。

### 核心元件地圖

**SLO/SLI 系統（Section 3-4）**：
- `SLO = composable SLIs + error budget`
- `SLI`: Service Level Indicator — 量化測量（task success rate、tool call accuracy）
- `SLOStatus` enum: `HEALTHY | AT_RISK | BREACHED | UNKNOWN`
- `ExhaustionAction`: budget 燒完後的處置（`THROTTLE | ALERT | ISOLATE`）
- 支援 auto-derivation（從歷史數據推估 SLO）

**Error Budget（Section 5）**：
- `error_budget = 1 - SLO_target`
- Burn rate = 實際消耗速度相對於允許速度
- Burn rate alert: `burn > 1.0` → 即將預算耗盡

**Circuit Breaker（Section 6）**：
- 三狀態：`CLOSED（健康）→ OPEN（拒絕）→ HALF_OPEN（試探）`
- `CircuitBreakerConfig`: failure_threshold, recovery_timeout, availability_check
- `CircuitBreakerRegistry`: 全域 agent circuit breaker 管理
- 應用場景：gateway 某 cron job 持續失敗 → 斷路 → 防止系統雪崩

**Chaos Engineering（Section 7）**：
- `FaultType`: infrastructure（latency/error/timeout）/adversarial/behavioral
- `Blast Radius clamping`: [0.0, 1.0] 控制實驗影響範圍
- `Resilience Scoring`: 每次 experiment 後產出 score
- `Abort Conditions`: 影響超標自動中止

**Alerting（Section 8-9）**：
- `AlertSeverity`: SEVERE | HIGH | MEDIUM | LOW | INFO
- `AlertChannel`: slack/email/pagerduty/webhook/opsgenie
- `AlertManager`: deduplication + delivery tracking
- `PersistentAlertManager`: 持久化存儲（DB schema provided）

**Trace Replay（Section 10-12）**：
- `Golden Trace`: 正確執行標記，用於回歸測試
- `Replay`: 捕獲並重放 agent 執行 trace

**Artifact Signing（Section 13）**：
- Ed25519 signing/verification for build artifacts + SBOMs
- 防止惡意篡改 agent build

**Incident Detection/Response（Section 14-15）**：
- 自動從 reliability signal 創建 incident
- Severity classification + response actions

### Hermes 啟發

1. **Circuit Breaker → Hermes gateway agent isolation**：當某 cron job 或 agent 連續 N 次失敗（failure_threshold），自動斷路，隔離該 agent 的 tool call 能力。與 `check_workspace_sync()` drift detection 互補——drift 是軟訊號，circuit breaker 是硬執行。

2. **Error Budget → Hermes cost/session tracking**：Hermes 的 `cost_24h` 可以擴展成 error budget model——`token_budget = budget_remaining`，burn rate = 消耗速度相對於允許速度。當 burn > 1.0 且 budget 即將耗盡，觸發 `THROTTLE`（降低 LLM 頻率）或 `ISOLATE`（暫停昂貴的 cron job）。

3. **Chaos Engineering → Hermes fault injection testing**：`FaultType` 中的 adversarial fault（prompt injection、tool argument fuzzing）正是 `hermes-agent-hijacking-resilience.md` 想要的測試場景。可以建立 `hermes_chaos.py` 做定期 fault injection，驗證 defense 有效性。

4. **SLOStatus → heartbeat 系統健康量化**：heartbeat 目前的狀態只有 nominal/degraded/critical，可以用 SLOStatus model 量化（SLI = cron success rate、tool call accuracy、response latency）。每個 heartbeat cycle 計算一次 SLOStatus，AT_RISK → alert，BREACHED → escalation。

5. **AlertManager deduplication → heartbeat alert fatigue**：同一指紋短時間內 multiple alerts → deduplicate，避免 alert flood。這與 `heartbeat_severity.json` 的 cooldown 機制方向一致，但 AlertManager 提供了更結構化的架構。

6. **Persistent AlertManager → heartbeat 事件持久化**：目前 heartbeat_severity.json 是一次性檔案，沒有 DB schema。PersistentAlertManager 的 DB schema（Section 9.2）可以借鑒，做長期 alert history + trend analysis。

### 與前期筆記的關連

1. **[[2026-05-27-policy-engine-continuation]]**：Policy Engine spec 的 fail-closed 與 Agent SRE Governance 的「fail-closed on internal error」一致。兩個 spec 互補：Policy Engine = runtime enforcement rules，SRE = reliability measurement + response。

2. **[[2026-05-26-mcp-security-gateway-spec-deep-dive]]**：Gateway interception 對應 SRE 的 Circuit Breaker——一個是「在哪攔截」，一個是「失敗後怎麼反應」。

3. **ws-028（Agent Lifecycle Governance）**：SRE 的 trust score + delegation chain depth 可以映射到 earned autonomy gradient。WS-028 的 Level 0-4 可以對應 SLOStatus 的 HEALTHY→AT_RISK→BREACHED。

4. **hermes-agent-hijacking-resilience.md**：Chaos Engineering 的 adversarial fault type（Section 7.1）直接對應 injection testing 需要的 fault scenarios。

### 與其他 AGT specs 的關係

| Spec | 關係 |
|------|------|
| Agent Hypervisor Execution Control | Circuit breaker state feeds Hypervisor kill switch |
| Agent OS Policy Engine | PolicyCompliance SLI tracks policy decision adherence |
| AgentMesh Identity and Trust | Agent DIDs used as identifiers in spans, alerts, incidents |

---

## 未追蹤 leads

- ✅ `AGENTMESH-TRUST-COORDINATION-1.0.md` — Identity + trust coordination spec，活著，值得 fetch（Phase 1）
- ❌ `AGENTMESH-IDENTITY-AND-TRUST-1.0.md` — 404（API response 確認不存在）
- ❌ `AGENT-SRE-1.0.md` — 404（死 lead）

## ✅ 本次探索完成
