---
_slug: 40-Resources-_mixed-explorations-2026-05-23-Agent-安全治理架構深度研究---探索筆記
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-Agent-安全治理架構深度研究---探索筆記.md
title: Agent 安全治理架構深度研究 — 探索筆記
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- abstract
- ace
- agent
- app
- otk
- plan
- policy
- provider
- saga
- token
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# Agent 安全治理架構深度研究 — 探索筆記

**日期**: 2026-05-23 | **來源**: SAGA (arXiv 2504.21034) + ACE (arXiv 2504.20984)
**類型**: 探索
**延續自**: [[2026-05-23-agent-governance-patterns.md]]

## Per-Source Insights

### SAGA — 完整 Protocol 分析

**核心：Provider-Centric + One-Time Key (OTK) 機制**

SAGA 的創新不在於用密碼學（DH、簽名、加密都是標準原語），而在於把這些原語組裝進一個完整的 agent lifecycle 管理框架：

**三個核心操作**：
1. **User Registration**：用戶向 Provider 註冊（密碼 + 證書），Provider 存 `H(passwd)`, `Cert`
2. **Agent Registration**：用戶替 agent 向 Provider 註冊，agent 生成鑰匙對 + N 個一次性公鑰 (OTK)，所有 OTK 由 user 簽名，Provider 存 `aid`, `OTK_i`, `CP_A`（Access Contact Policy），回傳 `σ_A^Prov`（Provider 簽名的確認）
3. **Inter-Agent Communication**：發起 agent 向 Provider 請求接觸權限，Provider 查詢接收 agent 的 `CP`（Contact Policy）→ 若允許，遞交對方的 `Cert` + OTK 列表；發起 agent 用 DH 跟接收 agent 協商共享金鑰，接收 agent 產生 Access Control Token（內含過期時間 + 請求上限）並用共享金鑰加密後傳回。此 token 可複用，直到過期或額度用盡才需再向 Provider 取新 OTK。

**OTK 的設計取捨**：
- 理想上每個 interaction 用一個新 OTK（安全性最高），但實際上每 pair 預生成 N 個 OTK（N 可調整），每個 OTK 對應一個 access control token（可複用），token 有 `T_expire` + `Q_max` 限制。
- **漏洞窗口** = `T_expire`，可短至幾分鐘，長至 24 小時。用戶可根據場景選擇安全/效能 trade-off。

**Threat Model 對齊（表 IV 分析）**：
SAGA 的威脅模型假設攻擊者 C1~C4（竊聽、攔截、篡改、重放），但在 TLS 層面假設安全。8 種攻擊 A1~A8 都能在 protocol 層被偵測：
- A1/A2/A3：無效 TLS 證書或無 OTK/token → 連線直接中斷
- A4：冒充別人證書 → 簽名驗證失敗
- A5：token 竊取重用 → PAC mismatch（token 綁定接收方公鑰）→ 立即偵測
- A6：Contact Policy 違反 → Provider 階段就阻擋
- A7：惡意 agent 註冊自己 → 需要 human verification，agent 無法繞過
- A8：合法 token 使用中 → 漏洞窗口由 `T_expire` 控制，期滿即斷

**Formal Verification**：用 ProVerif 在 Dolev-Yao 模型下自動證明 secrecy + authentication，攻擊者模型包含 observe/intercept/modify/replay/synthesize。這給了 SAGA 密碼學嚴格的安全性保證。

**對 Talos 的具體實作啟示**：
1. **Contact Policy** 直接映射到 Hearth 的 task ownership — Talos 可以實作 `CP_B(A)` 機制：Talos 的 task 對應 Hestia 的 inbox message，只有經過 Talos 明確授權（OTK-like mechanism）的 agent 才能發起新 task
2. **Token 機制** 解決「session 有持久性但權限需要過期」的問題 — 可用於 cron job 的 tool access token（定期刷新）
3. **Provider 只在 setup 階段介入**，之後 agent 間直接 TLS 通訊 — 借鑒：用 heartbeat state file 作為「輕量 Provider」，只在狀態初始化時介入，日常 action 直接執行

---

### ACE — Abstract-Concrete-Execute 架構

**核心：兩階段 planning + static analysis**

ACE 解決的問題：LLM-integrated app systems（LLM 調用外部 app）中，惡意 app 可以：
1. **Integrity violation of planning** — 污染 LLM 的 plan generation
2. **Integrity/Availability of execution** — 執行階段的 data leakage 或 DoS
3. **Privacy compromise** — 竊取用戶資料

**ACE 三階段**：
1. **Abstract Plan**：LLM 只用 trusted information（system prompt、user instruction）建立 abstract execution plan，不接觸任何 app 返回的資料。此 plan 描述「要做什麼」但不明確綁定到具體 app。
2. **Concrete Plan**：用已安裝的 system apps 將 abstract plan 實例化為 concrete plan（指定用哪個 app、哪個參數）。這階段可能接觸 app metadata 但仍不執行。
3. **Static Analysis**：對 concrete plan 做安全靜態分析，檢查 user-specified secure information flow constraints（如「email app 不能讀 filesystem」）。不通過 → 拒絕執行。
4. **Execution**：data/capability barriers between apps，確保執行真的按 trusted abstract plan 走。

**攻擊緩解**：
- **Indirect prompt injection（主要目標）**：即使 app 返回惡意 content（包含 injection prompt），abstract plan 已經在無 app data 的情況下生成，不受污染。concrete plan mapping 時只考慮 trusted system constraints。
- 對比 IsolateGPT：IsolateGPT 嘗試隔離每個 app call 的 context，但無法防止 multi-turn 累計滲透。ACE 從架構上根本不需要信任 app 返回的內容。

**對 Hermes 的具體實作啟示**：
1. **Phase 1/Phase 2 隔離** 適用於自主探索：Plan-Then-Execute 的 Phase 1 不接觸 untrusted content（搜索結果），Phase 2 才 fetch，但 ACE 的兩階段更嚴格——abstract plan 完全不接觸 app data，concrete plan 只接觸 metadata。這比當前 heartbeat 的 plan-then-execute 更嚴（當前 Phase 2 fetch 後的內容仍可影響後續探索方向）。
2. **Static analysis** 對 plan 做合規檢查 — 可實作在提案寫入 `proposals/` 時的 frontmatter validation（確保 `status:` 欄位有效、`**前提**` 中的路徑存在）
3. **Capability barriers** — 借鑒：每個 tool call 前檢查 `capability tags`（如 `filesystem.read`、`web.search`），不符合 policy 就拒絕，不只是日誌記錄

---

## Cross-Article Synthesis

### 兩篇的核心共鳴：确定性外部控制

SAGA 和 ACE 都在說同一件事：**安全不能依賴 LLM 的推理能力**：

| 維度 | SAGA | ACE |
|------|------|-----|
| 信任邊界 | Provider（外部）+ OTK/token（密碼學強制） | Abstract plan（trusted）+ Capability barriers |
| 動態性 | Token 有有效期，Provider 可即時撤銷 | Static analysis 在執行前攔截 |
| Agent 數量 | 強調規模（可擴展至數百萬 agent） | 強調單一 LLM 對多 app 的安全隔離 |
| 威脅模型重疊 | 處理 agent impersonation、token replay | 處理 app injection、data exfiltration |

**對 Hermes/Talos 的分層實作建議**：

**Layer 1（確定性執行）**：ACE 的 capability barriers + ACE 的 static analysis → 在 Hermes tool layer 實作 permission check（Hearth 的 task ownership 對應 `CP_A`）。Tool call 前檢查 `capability tags`，不符合就 reject，不只是 log。

**Layer 2（密碼學 token）**：SAGA 的 OTK + Access Control Token 機制 → 對 cron job 實作短期 tool access token（每個 action cycle 刷新一次）。心跳之間的通訊用 session key 加密（借鑒 SAGA DH 握手）。目前 heartbeat_state.json 是 plain JSON，考慮用 HMAC 簽名防止 tampering。

**Layer 3（Provider 仲裁）**：Talos 作為 Hearth 的「Provider」，維護 agent registry（哪些 task 歸誰）+ contact policy（哪些 agent 可以跟哪些 task 互動）。目前 inbox/hestia 是簡單的檔案系統，未來可實作完整的 policy enforcement。

**Layer 4（漏洞窗口控制）**：每個 cron job / autonomous action 的「連續工作窗口」需要上限，借鑒 SAGA 的 `T_expire` + `Q_max`。目前沒有這個機制——exploration 可連續跑很長時間直到整個 session 結束。可以實作 `_ACTION_GUARD` class：每個 action type 有 max_consecutive_calls（防止 doom loop）和 max_total_calls（防止 resource exhaustion）。

### 與當前 Hermes 架構的缺口

1. **Tool access 沒有 capability enforcement**：目前 `terminal`、`file`、`web` 等 toolset 沒有細粒度的 permission check。SAGA 的 contact policy + ACE capability barriers 概念可以加在工具層。
2. **Session token 沒有過期**：heartbeat session 啟動後可維持很長時間，SAGA 的 OTK 刷新模式可以借鑒。
3. **Agent registry 不存在**：Hearth 目前是 filesystem-based task 追蹤，沒有集中的 agent identity + policy registry。SAGA 的 User/Agent registry 模型是參考起點。

## 未追蹤 Leads

- SAGA ProVerif code: https://github.com/gsiros/saga（可能有具體的 formal verification 實作參考）
- ACE NDSS 2026 正式版本（v3 已在 2025-09 發布，正式 conference version 可能有更新的 evaluation）
- "Firewalls to secure dynamic llm agentic networks" (arXiv 2502.01822) — SAGA 參考文獻 [62]，標題直接說 "firewalls"，可能是比 SAGA 更基礎的方案
- CEDAR policy language — Amazon AgentCore 使用的 authorization language，可能是實作 Hearth policy 的具體規格

## ✅ 本次探索完成
