---
_slug: 40-Resources-_mixed-explorations-2026-05-26-audit-compliance-spec
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-audit-compliance-spec.md
title: 探索：AGT Audit and Compliance System — 2026-05-26
created: '2026-05-26'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：AGT Audit and Compliance System — 2026-05-26

**URL**: https://raw.githubusercontent.com/microsoft/agent-governance-toolkit/main/docs/specs/AUDIT-COMPLIANCE-1.0.md
**Status**: Draft · 2026-04-30 · Microsoft AGT team
**Length**: 2292 lines (raw) → 1730 lines (sanitized)

## TL;DR — Audit System 是什麼

AGT 的合規審計系統，定義了 5 種審計事件類型、4 種合規框架映射（SOC2/ISO27001/GDPR/HIPAA）、3 種 evidence collection 級別（live/periodic/on-demand）。

## 核心元件

### 審計事件類型（Section 3）
- **Tool Execution Events**: tool 名稱、參數、結果、duration、user context
- **Policy Decision Events**: allow/deny decision、matched rule、drift score
- **Trust Level Transitions**: escalation/revocation events、trigger、approver
- **Session Events**: start/end、participant list、channel type
- **Data Access Events**: resource、access pattern、sensitivity level

### Evidence Collection（Section 4）
- **Level 1 - Live**: 關鍵事件即時寫入audit log（tool execution、policy decisions）
- **Level 2 - Periodic**: 低頻事件定期 batch（session summaries、trust transitions）
- **Level 3 - On-demand**: 手動觸發（compliance audit、incident response）

### 合規框架映射（Section 6）
- **SOC2**: 對應 CC6.1（logical access）、CC7.2（monitoring）、CC8.1（change management）
- **ISO27001**: 對應 A.12.4.1（event logging）、A.18.1.1（compliance monitoring）
- **GDPR**: Art. 30（records of processing）、Art. 35（DPIA）→ data access event 需要 sensitivity label
- **HIPAA**: §164.312(b)（access controls）、§164.308(a)(1)(ii)(D)（risk analysis）

### Data Retention（Section 5）
- Live events: 90 days hot storage + 7 years cold storage
- Periodic batch: 3 years
- Evidence package: 7 years（合規要求）
- 自動刪除遵守 right-to-erasure（GDPR Art. 17）

### Alerting（Section 7）
- 3 級 alert：INFO / WARNING / CRITICAL
- Threshold-based: 異常 tool call pattern、trust escalation rate、policy denial rate
- Integration: Webhook + PagerDuty + Slack

## 與前期筆記的關連

1. **Policy Engine（2026-05-27 筆記）**：Policy Engine 產生 `PolicyDecisionEvent`，Audit System 消費這些事件作為合規 evidence。兩者共生：Policy Engine 執行 + Audit System 記錄。

2. **WS-028（Agent Lifecycle Governance）**：Trust Level Transition event 正好補足 WS-028 的earned autonomy 量化記錄——每次 escalation/revocation 都是 auditable event。

3. **Execution Rings**：Ring 0/1 tool call 應該是 Level 1 audit（live），Ring 3 可以是 Level 2（periodic batch）。

## Hermes 啟發

1. **Hermes 缺少系統級 audit trail**：目前 heartbeat_action_log.jsonl 只有 heartbeat 相關事件，沒有 tool execution/policy decision 的完整覆蓋。Audit System 的 event schema（tool_name、parameters、result、duration）可以直接借鑒。

2. **Compliance-ready logging**：GDPR/HIPAA 的 data retention 要求（7 years cold storage）對應 Hermes vault 的長期 backup 策略。

3. **Alert threshold 借鑒**：current EVOLVE 的 severity escalation 已是某種 alerting，但缺少 threshold-based pattern（異常 tool call rate、consecutive failures）。

## 未追蹤 leads

- ✅ `AUDIT-COMPLIANCE-1.0.md` — 2292 lines，活得，已 fetch 完成
- ✅ `AGENT-SRE-GOVERNANCE-1.0.md` — 1173 lines，活得（2026-05-26 fetch）
- ✅ `AGENTMESH-TRUST-COORDINATION-1.0.md` — 活得（2026-05-26 fetch）

## ✅ 本次探索完成