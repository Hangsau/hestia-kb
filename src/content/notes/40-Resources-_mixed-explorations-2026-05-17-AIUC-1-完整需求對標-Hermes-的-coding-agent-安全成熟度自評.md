---
_slug: 40-Resources-_mixed-explorations-2026-05-17-AIUC-1-完整需求對標-Hermes-的-coding-agent-安全成熟度自評
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-AIUC-1-完整需求對標-Hermes-的-coding-agent-安全成熟度自評.md
title: AIUC-1 完整需求對標：Hermes 的 coding agent 安全成熟度自評
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- aiuc
- coding
- data
- hermes
- party
- prevent
- testing
- third
- tool
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# AIUC-1 完整需求對標：Hermes 的 coding agent 安全成熟度自評

**日期**: 2026-05-17 00:45 CST
**來源**: https://www.aiuc-1.com/research/setting-the-standard-for-agentic-development
**延續自**: [[2026-05-16-sandbox-profiles-compliance-adversarial-drift]]
**狀態**: analyzed

---

## 1. 總覽

AIUC-1 是第一個針對 AI coding agent 的 SoC-2 等級合規標準，由 AIUC-1 Consortium 維護。Lovable、Cursor、Codex、Claude Code 參與制訂。Q2-2026 聚焦 MCP security、agent permissions、third-party risk。Lovable 預定 2026 summer 由 Schellman 進行第三方審計。

**75 個 coding-agent-specific risks**，13 個主題類別，收斂成七個優先領域：
1. Secure defaults for code generation
2. Secrets management
3. Runtime execution and sandbox integrity
4. Dependency and supply chain integrity
5. Agent autonomy and human oversight
6. Data confidentiality and IP protection
7. Transparency & governance around shared responsibilities

六個認證 domain：A. Data & Privacy、B. Security、C. Safety、D. Reliability、E. Accountability、F. Society。

---

## 2. Domain-by-Domain Hermes 對標

### A. Data & Privacy

| AIUC-1 需求 | Hermes 狀態 | 說明 |
|---|---|---|
| Establish input data policy | ✅ 隱性 | 單人 agent，無 external data ingestion policy 需求 |
| Establish output data policy | ✅ | 輸出僅到 vault + cron output，無 cross-customer 風險 |
| Limit AI agent data access | 🟡 | Tool gateway 存在但無 formal capability profile（WS-010 area） |
| Protect IP & trade secrets | ✅ | Local-only，無 shared infrastructure |
| Prevent cross-customer data exposure | ✅ | 單用戶，不適用 |
| Prevent PII leakage | 🟡 | secret-leak-prevention skill 存在，但無 structured PII scan |
| Prevent IP violations | ❌ | 無 copy-left license scan for generated code |

**Gap**: PII leakage prevention 目前僅止於 API key 掃描，缺少 structured PII detection（email、phone、address pattern）。

### B. Security

| AIUC-1 需求 | Hermes 狀態 | 說明 |
|---|---|---|
| Third-party testing of adversarial robustness | ❌ | 無 adversarial testing（prompt injection 僅有防禦，無測試） |
| Detect adversarial input | 🟡 | sanitize_fetch.py 擋 zero-width chars，但 injection phrase detection 未實作 |
| Manage public release of technical details | ✅ | 單人 agent，無公開釋出流程 |
| Prevent AI endpoint scraping | ✅ | Local-only |
| Implement real-time input filtering | 🟡 | Phase-Locked Exploration 的 plan-then-execute 是 process-level gate，非 real-time |
| **Prevent unauthorized AI agent actions** | ❌ | **WS-009 PENDING** — 這是 AIUC-1 最核心的 coding agent 安全需求 |
| Enforce user access privileges to AI systems | ✅ | 單用戶 |
| Protect AI system deployment environment | 🟡 | filesystem access 無 sandbox（Docker/bubblewrap/firejail 皆未使用） |
| Limit output over-exposure | 🟡 | 輸出到 vault + cron output，但無 output content scan |

**關鍵 gap**: WS-009（prevent unauthorized actions）是 AIUC-1 B domain 的核心——沒有這個，coding agent 安全模型就不完整。目前 Hermes 靠的是 trust（假設 LLM 不會惡意行動），而非 enforcement。

### C. Safety

| AIUC-1 需求 | Hermes 狀態 | 說明 |
|---|---|---|
| Define AI risk taxonomy | ✅ | ISSUES.md known issues + KI-NNN 分類（TRANSIENT/CONFIG/SYSTEM/DATA/LOGIC） |
| Conduct pre-deployment testing | ✅ | pytest canary（95 tests）|
| Prevent harmful outputs | ❌ | Hermes 是 coding agent，不直接服務 end-user。但自主 cron 產出無 harmfulness review |
| Prevent out-of-scope outputs | 🟡 | Skill 系統限制行為範圍，但無 enforcement |
| Flag high risk outputs for human review | ❌ | 無——heartbeat severity escalation 是 operational，非 content safety |
| Third-party testing (×3) | ❌ | 不適用於單人 agent |

**Gap**: Safety domain 對單人 coding agent 大部分不適用。唯一 relevant 的是「自主產出的 harmfulness review」——目前完全空白。

### D. Reliability

| AIUC-1 需求 | Hermes 狀態 | 說明 |
|---|---|---|
| Prevent hallucinated outputs | 🟡 | 無機制。coding agent hallucination 會產生 vulnerability |
| Third-party testing for hallucinations | ❌ | 不適用 |
| **Restrict unsafe tool calls** | ❌ | **這是 Hermes 最大的 reliability gap**——tool gateway 無 capability profile |
| Third-party testing of tool calls | ❌ | pytest canary 測的是 code correctness，非 tool-call safety |

**關鍵 gap**: 「Restrict unsafe tool calls」直接對應 WS-010（self-modification guard）。目前 Hermes 的任何 tool（terminal、patch、write_file）都能被任意呼叫，無 capability-based restriction。

### E. Accountability

| AIUC-1 需求 | Hermes 狀態 | 說明 |
|---|---|---|
| AI failure plan for security breaches | ✅ | severity escalation → Telegram（autonomic layer）|
| AI failure plan for harmful outputs | ✅ | 同 security breach pathway |
| AI failure plan for hallucinations | 🟡 | 無 hallucination-specific failure plan |
| Assign accountability | ✅ | 單用戶 = self-accountability |
| Document data storage security | ✅ | Local filesystem, no cloud storage |
| Conduct vendor due diligence | 🟡 | DeepSeek 是唯一 provider，但無 formal vendor assessment |
| Review internal processes | 🟡 | heartbeat drift sensors 是被動的，無 scheduled review |
| Monitor third-party access | ✅ | 無 third-party access |
| Establish AI acceptable use policy | ✅ | 隱性（skill 限制行為範圍）|
| Document regulatory compliance | ❌ | 不適用於個人專案 |
| **Log AI system activity** | ✅ | heartbeat EVOLVE logging（per-cycle error + action log）|
| Implement AI disclosure mechanisms | ❌ | 不適用 |
| Document system transparency policy | ✅ | system maps + AGENTS.md + HEARTBEAT_MAP.md |

**Hermes 表現最好的 domain** — heartbeat logging、severity escalation、known-issue management 覆蓋了 Accountability 大部分需求。

### F. Society

| AIUC-1 需求 | Hermes 狀態 | 說明 |
|---|---|---|
| Prevent AI cyber misuse | ✅ | 單人 agent，範圍受限 |
| Prevent catastrophic misuse | ✅ | 無 CBRN 風險 |

---

## 3. Hermes 啟發

### 3.1 七個優先領域的 Hermes 落差（以 severity 排序）

| # | 優先領域 | AIUC-1 gap | 對應 WS |
|---|---|---|---|
| 1 | **Agent autonomy oversight** | 無 unauthorized action prevention | WS-009 |
| 2 | **Runtime sandbox integrity** | 無 sandboxing（Docker/bubblewrap/firejail） | WS-009 sub-item |
| 3 | **Secure code generation defaults** | 無 code generation safety scan | WS-010 |
| 4 | **Secrets management** | PII scan 缺失，僅有 API key scan | 新提案 |
| 5 | **Dependency/supply chain integrity** | MCP tools 無 integrity check | 新提案 |
| 6 | **Data confidentiality** | 無 structured PII detection | 新提案 |
| 7 | **Transparency & governance** | ✅ 已覆蓋 | — |

### 3.2 行動建議

1. **WS-009 應納入 AIUC-1 的 "prevent unauthorized agent actions" 作為需求語言**：不只是防止 hijacking（外部攻擊），也包括防止 agent 自主執行超出 scope 的操作。Tool capability profile（「探索模式只能 curl + write_file + search_files」）是實現路徑。

2. **WS-010 應對標 D. Reliability 的 "restrict unsafe tool calls"**：不只是防止 self-modification，而是建立分層 tool access model——read-only / sandboxed-write / full-access。

3. **Adversarial testing gap**：B. Security 要求的 "third-party testing of adversarial robustness" 對 Hermes 而言可轉化為 self-administered red-team：定期用 prompt injection payload 測試自己的防禦。

4. **AIUC-1 的 evidence framework 值得參考**：每個 control 都有 evidence type（Technical Implementation / Operational Practices / Legal Policies）和 typical location——這比 Hermes 目前的 ad-hoc 文件更有結構。

### 3.3 不適用的部分（誠實面對）

- **C. Safety 大部分不適用**：Hermes 不服務 end-user，無需 harmful output prevention for third parties
- **F. Society 不適用**：單人 coding agent 無 societal risk
- **Third-party testing (×5)**：這不是單人 agent 能做的事
- **Cross-customer data exposure**：單用戶，不存在

AIUC-1 約 30-40% 的 requirements 對單人 agent 不適用。但剩餘 60% 中，Hermes 真正做好的大約一半（Accountability domain + 部分 Security）。核心的 Autonomy oversight + Sandbox integrity + Tool call restriction 是最大的三個 gap。

---

## 未追蹤

- AIUC-1 完整 whitepaper PDF（頁面上只有 summary，75 risks 的完整細節在下載的 PDF 中）
  - 可能的取得方式：aiuc-1.com 的 whitepaper download form（需 email）
- AIUC-1 changelog: https://aiuc-1.com/changelog — 追蹤標準演進
- AIUC-1 Q3-2026 update preview: https://www.aiuc-1.com/research/looking-ahead-consortium-feedback-shaping-the-q3-2026-update
- Lovable's specific safeguards (the whitepaper co-authors) — 來看他們如何 implement AIUC-1 controls
- Schellman audit criteria for AIUC-1 — 第三方審計的實際檢查項目

## ✅ 本次探索完成

