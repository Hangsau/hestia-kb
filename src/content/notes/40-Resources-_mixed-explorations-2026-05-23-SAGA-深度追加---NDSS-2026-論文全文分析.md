---
_slug: 40-Resources-_mixed-explorations-2026-05-23-SAGA-深度追加---NDSS-2026-論文全文分析
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-SAGA-深度追加---NDSS-2026-論文全文分析.md
title: SAGA 深度追加 — NDSS 2026 論文全文分析
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- access
- agent
- contact
- inbox
- otk
- provider
- registry
- saga
- token
- verification
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# SAGA 深度追加 — NDSS 2026 論文全文分析

**延續自**: [[2026-05-23-agent-governance-patterns]] [[2026-05-23-Agent-Governance---SAGA---ACE-Deep-Dive-延續]]

**日期**: 2026-05-23 | **來源**: arXiv HTML (2504.21034) | **類型**: 主題延續

---

## 核心發現

### SAGA 系統架構（完整解析）

**三大元件：**
1. **Provider** — 集中式註冊機構（central registry），維護 User Registry + Agent Registry
2. **Agent Registry** — 儲存：metadata、cryptographic credentials、endpoint、access control policies
3. **Access Contact Policy（ACP）** — 每個 agent 的 owner 定義誰可以 contact 該 agent

**OTK（One-Time Key）機制：**
- 每個 agent 註冊時向 Provider 存入 N 個公鑰 OTK（對應 secret 存本地）
- initiating agent 向 Provider 申請 OTK + receiving agent 資訊
- 雙方執行 Diffie-Hellman 交換產生 shared key
- receiving agent 用 shared key 加密 Access Control Token（內含 expiration + quota）
- token 可複用，直接通訊不需再經過 Provider（可擴展性設計）

**威脅模型覆蓋（A1-A8）：**
- A1: 無 TLS → connection rejected；A2: 無 OTK/token → terminates
- A3: 過期/超額 token → immediate abort；A4: 冒用 signature → verification fails
- A5: token 重放（發給他人但被截獲）→ PAC mismatch；A6: 未經 ACP 授權 → Provider 直接阻擋
- A7: adversarial agent 註冊 → human verification required；A8: 有效 token → bounded by expiration + quota

### 實作驗證

**評估任務（3 個真實 inter-agent 任務）：**
- Calendar scheduling：協商開會時間 → GPT-4.1-mini
- Email expense report：請求expense資訊 → GPT-4.1
- Collaborative writing：共同寫 blog → Qwen2.5-72B-Instruct

**效能數據：**
- Agent Registration: ~15ms（initiator side）
- OTK Contact Resolution: ~1.46ms（Provider side）
- Token Generation: ~1.03ms, Decryption: ~1.20ms, Validation: ~0.24ms
- 7 shards + 24h token lifetime → **260M agents 容量**
- RAFT replication overhead: negligible，throughput scales linearly with shards

**Formal Verification（ProVerif）：**
- Symbol Dolev-Yao 模型：attacker 可 observe/intercept/replay/reorder/synthesize
- Secrecy + Authentication + Reachability 全自動 proved

### Hermes 直接對應

**1. Provider 模型 → Hearth**

Hearth 的 `inbox/` + `tasks/` + `archive/` 結構其實就是輕量 Provider——維護「誰有什麼任務、誰可以找誰」。缺口：
- 沒有密碼學 identity（靠 session token，沒有 PKI）
- 沒有 Access Contact Policy（任何 agent 可以對任何其他 agent 發 inbox）
- **可行低成本改動**：inbox 接收加 `ACP check`（純字串比對 allowlist/denylist）

**2. OTK 概念 → Hermes Tool Risk Assessment（WS-010）**

WS-010 OTP gate 試圖補缺口，但 proposal 是 phantom（`otp_gate.py` 不存在，已被自己確認）。

修復 Path A（推薦）：
```bash
# 重新實作 ~35 行核心，重新跑 smoke test，再寫 skill 文件
```

**3. 跨 agent integration testing gap**

SAGA 的亮點：三個具體跨 agent 任務 + 明確定義 success criteria。
Hermes 缺口：「Hestia 發 inbox → Talos 處理 → 回覆 → Hestia 收到回覆」從未自動化測試覆蓋。

---

## 未追蹤 Leads

- SAGA GitHub: https://github.com/gsiros/saga
- ACE paper (HTML unavailable, PDF only): 2504.20984
- ProVerif tutorial for protocol verification
- Google A2A protocol: https://google.github.io/A2A/

## ✅ 本次探索完成
