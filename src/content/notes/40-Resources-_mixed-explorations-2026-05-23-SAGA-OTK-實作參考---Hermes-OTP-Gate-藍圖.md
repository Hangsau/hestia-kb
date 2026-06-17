---
_slug: 40-Resources-_mixed-explorations-2026-05-23-SAGA-OTK-實作參考---Hermes-OTP-Gate-藍圖
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-SAGA-OTK-實作參考---Hermes-OTP-Gate-藍圖.md
title: SAGA OTK 實作參考 — Hermes OTP Gate 藍圖
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- budget
- gate
- hermes
- layer
- otk
- otp
- pattern
- rulebook
- saga
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "SAGA OTK 實作參考 — Hermes OTP Gate 藍圖"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [saga, otk, otp, hermes, security, agent, governance, ndss, python]
---

# SAGA OTK 實作參考 — Hermes OTP Gate 藍圖

**延續自**: [[2026-05-23-Agent-Governance---SAGA---ACE-Deep-Dive-延續]] [[2026-05-23-SAGA-深度追加---NDSS-2026-論文全文分析]]

**日期**: 2026-05-23 | **來源**: GitHub gsiros/saga (直接 fetch raw README.md) | **類型**: 探索 — 主題式延續

## Per-Source Insights

### SAGA GitHub — OTK 實作細節

**URL**: https://github.com/gsiros/saga（Stars: 22, Python, NDSS 2026）

SAGA 的 README 揭示了具體的 OTK（One-Time Key）使用方式，這是 WS-010 Hermes OTP Gate 提案的實作藍圖：

#### 1. OTK 在 Agent Registration 時批量生成

```
Enter number of one-time access keys: 10
Enter contact rulebook: [{"pattern":"*", "budget":10}]
```

→ 用戶在註冊 agent 時指定 **OTK 批量數量**（10 個）+ **接觸規則（rulebook）**。

#### 2. Rulebook — 操作的 pattern + quota 控制

SAGA 的 `rulebook` 是 `[{"pattern":"*", "budget":10}]`：
- `pattern`: 匹配操作類型（`*` = 所有操作，或具體如 `email.send`, `file.delete`）
- `budget`: 配額（budget=10 表示這個 OTK 可用 10 次操作）

→ 這比「一次性密碼」更強：OTK 是攜帶 quota 的通行證，不是只能用一次的 OTP。

#### 3. Hermes OTP Gate 可借鑒的實作細節

| SAGA 實作 | Hermes OTP Gate 對應 |
|-----------|----------------------|
| 批量生成 OTK | `otp_gate.generate(secret, ttl)` 返回 `(token, code)` |
| Pattern matching | `MASS_DELETE`, `MASS_EMAIL` 等 risk category |
| Budget（配額） | 未實現：可考慮「此 OTP 可通過 N 次高風險操作」 |
| Provider 強制執行 | 目前的 gap：`otp_gate.py` 存在但未被 tool layer 調用 |
| MongoDB 狀態 | Hermes 可用 SQLite 或 JSON file（見 `nanoclaw-db-as-io-architecture.md`） |

#### 4. Agent Registration 流程（可直接借鑽）

```
1. 用戶 CLI 互動：選擇 operation（register/login/register-agent）
2. 輸入 metadata（device name, IP, port）
3. 系統生成 OTK batch
4. 綁定 rulebook（操作類型 + 配額）
5. Provider 簽署 agent manifest（`agent.json`）
```

→ Hermes OTP Gate 的 `otp_gate.py` 現已完成 Step 1（generate/verify），缺失的是 Step 5 的「串入 tool layer」和「Telegram delivery handler」。

### Hermes 啟發

**OTP Gate 的 three-layer 設計可以從 SAGA 借鑽**：

```
Layer 1: OTP generate/verify（已完成 ✅ otp_gate.py）
Layer 2: Telegram delivery + /otp command handler（提案 Step 2，尚未整合）
Layer 3: Tool layer 風險偵測 → 觸發 OTP 流程（提案 Step 3，未啟動）
```

**具體的整合點**：SAGA 的 rulebook `budget` 概念很有價值——不只是一次性通行證，而是「配額通行證」。對 Hermes 的意義：
- `MASS_DELETE`: budget=5（允許刪除 5 個檔案後 OTP 失效）
- `MASS_EMAIL`: budget=3（允許寄 3 封後失效）
- `EXTERNAL_PUBLISH`: budget=1（只能發一次）

這樣即使 OTP 被截獲，攻擊者的操作上限也是明確的。

---

## 跨文章 Synthesis

**從 SAGA 論文 → SAGA 實作（GitHub）的跨越**：

論文只描述概念架構（OTK 機制、Provider、Rulebook），但 GitHub README 揭示了具體參數設計：
- OTK 數量：10（預設）
- Rulebook 格式：`[{"pattern": "...", "budget": N}]`（JSON array）
- Agent manifest 格式：`agent.json`（含 `aid`, `dev_info_sig`, `spk`, `opks` 等）

這個從「理論」到「可跑代碼」的映射，對 Hermes 的價值在於：**提案 WS-010 的風險 taxonomy 已經有了實作藍本**。`otp_gate.py` 的介面（generate, verify, pending_count, cleanup）正好對應 SAGA 的 OTK lifecycle。

---

## 未追蹤 Leads

- SAGA 實驗程式碼（`experiments/`）— 具體任務（schedule_meeting, expense_report, create_blogpost）的 OTK 配額使用模式
- SAGA 的 `local_agent.py` abstract class — 了解「如何 wrapper 任意 LLM agent」

---

## ✅ 本次探索完成
