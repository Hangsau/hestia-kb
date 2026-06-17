---
_slug: 40-Resources-_mixed-explorations-2026-05-23-Agent-Governance---SAGA---ACE-Deep-Dive-延續
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-Agent-Governance---SAGA---ACE-Deep-Dive-延續.md
title: Agent Governance — SAGA / ACE Deep Dive（延續）
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- ace
- agent
- governance
- hermes
- otk
- provider
- saga
- talos
- token
- user
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# Agent Governance — SAGA / ACE Deep Dive（延續）

**延續自**: [[2026-05-23-agent-governance-patterns]]

**日期**: 2026-05-23 | **來源**: arXiv 2504.21034 (SAGA full HTML) + arXiv 2504.20984 (ACE)
**類型**: 探索 — 主題式延續

## Per-Source Insights

### SAGA — Security Architecture for Governing AI Agentic Systems（NDSS 2026）

**論文架構總覽**：

**威脅模型（Section III-D）**：
1. 攻擊者偽裝成合法 agent（impersonation）
2. 攔截/竄改 inter-agent 溝通（MITM）
3. Prompt injection（污染 agent 決策）
4. 側錄敏感資料（data exfiltration）
5. 惡意 agent 在系統內傳播（propagating malware）

→ 這五個威脅跟 Hermes/Talos 的 threat model 高度重疊。

**SAGA Protocol 三階段**：

1. **User Registration**：用密碼學證書建立人類身份（整合 trusted identity service 做 human verification）
2. **Agent Registration**：User 替 agent 生成金鑰對（PK/SK）+ 一批 public OTK（one-time key）。Provider 維護 Agent Registry（metadata + credentials + access policies）
3. **Inter-Agent Communication**：
   - 發起方從 Provider 請求 OTK + 目標 agent 的 endpoint info
   - Provider 檢查目標的 Access Contact Policy，決定是否頒發 OTK
   - 發起方用 OTK 接觸目標 → 雙方執行 DH key exchange → 目標產生 Access Control Token（綁定時間戳 + 配額）
   - 後續通訊用此 token，Provider 完全不參與（可擴展）
   - Token 過期或配額用完 → 重新向 Provider 請求新 OTK

**OTK token 設計的核心洞察**：

```
token = Enc_SDHK(<nonce, T_issued, T_expire, Q_max, PAC_receiver>)
```

Token 讓 receiving agent 自己生成（不是 Provider），但 token 內容由雙方共享金鑰加密。這個設計把 access control 的 enforcement 點從 Provider（需要每次都參與）轉移到 receiving agent（只需要驗證 token）。

→ 對 Hermes 的啟發：Talos 的 governance pipeline 也可以是「Policy 由 Hestia 自己 enforcement」，不需要每次 action 都繞過 Talos。把 trusted 程度建立成 token session，減少重複校驗成本。

**ProVerif 形式化驗證**：SAGA 用 ProVerif 在 Dolev-Yao 模型下自動證明：
- Token secrecy
- Agent authentication (with Provider)
- Agent-to-agent authentication

八個攻擊模型（Attacker A1-A8）全部在 protocol 的特定步驟被偵測/阻擋。

→ 對 Hermes 的啟發：DCG（Devil's Candy Guard）已經是確定的 policy enforcement 層。SAGA 的 formal 驗證思路提醒：可以用 ProVerif 或 TLA+ 對 governance protocol 做形式化驗證。

**Fault Tolerance + Scalability**：
- Provider 用 RAFT replication → 5 節點依然 negligible overhead
- 用 sharding 擴展 → 線性 throughput 增加
- 10 sharders + 24h token lifetime → 支援 260M agents

→ 對 Talos/Talos governance pipeline 的實作參考：raft + sharding 的架構適用於多 agent 系統。

---

### ACE — Abstract-Concrete-Execute Architecture

**HTML fetch 失敗**（sanitize 後 819B），只拿到 abstract。從 SAGA 上下文補充：

ACE 核心設計：
- **Abstract Planning**：用 trusted info 建立 plan skeleton（無危險副作用）
- **Concrete Planning**：映射到已安裝的 system apps（actual tools）
- **Static Analysis**：驗證 plan 符合 user-specified secure information flow constraints
- **Execution**：data/capability barriers between apps，強制執行符合 trusted abstract plan

→ 對 Hermes/heartbeat 的直接共鳴：
- Phase 1（Plan）：收集資訊，寫 explore_plan.md → 對應 ACE Abstract Planning
- Phase 2（Execute）：fetch + 分析 → 對應 ACE Concrete Execution
- Phase 3（Review）：寫 synthesis + 未追蹤 leads → 對應 ACE 的 static analysis 驗證

**重大新洞察：Agent Lifecycle 的 user control 問題**

SAGA 的核心貢獻不是技術機制，而是把 user control 變成 protocol 的一等公民：
- User 可以隨時停用 agent（deactivate）→ Provider 將其從 registry 移除 → 其他 agent 無法發現它
- 這個「隨時可以 revoke」的機制讓 agent 的存在不是永久的，而是 user 意志的延伸

→ 對 Hermes/Talos 的啟發：當前 Hermes 的 session model 沒有「user revoke」的概念（一旦建立 session，agent 持續運行直到 timeout）。SAGA 的 lifecycle control 值得參考。

**另一個重大洞察：Provider 的 policy 是雙向的**

SAGA 的 Access Contact Policy 是「誰可以 contact 我的 agent」。但 Hermes/Talos 需要的是「誰可以發出什麼操作」。兩者方向不同：
- SAGA：filter incoming（誰能找我）
- Hermes/Talos：filter outgoing（我能做什麼）

→ 對 DCG 的改進方向：DCG 的 `disabled_packs` 是 outgoing filter，但 trust level advisory 層還沒用到。若把 SAGA 的 OTK 概念借用到 Hermes，可以建立「操作配額 token」——每個 session 有初始操作預算，用完需要 re-authorize。

---

## Cross-Article Synthesis

SAGA + ACE + 昨日 AWS 四大原則的交匯點：

1. **確定性 enforcement > LLM 判断**：三個來源全部指向同一結論。AWS 的 Security Box、 SAGA 的 cryptographic token、ACE 的 static analysis validation，都是把安全決策從 LLM 推理層抽出來。

2. **Provider = Governance Pipeline**：SAGA 的 Provider（集中式）vs ACE 的兩階段 planning（分散式）。Hermes/Talos 需要兩者兼具：分散式執行（各 agent 自己 enforce）+ 集中式協調（Talos governance pipeline）。

3. **Token session 概念**：SAGA 的 OTK + Access Control Token 機制，與心跳系統的「信任建立 → 逐步授權」模式高度吻合。建議把 DCG 的 trust_level advisory 擴展成「操作配額 token」系統。

4. **Formal verification**：ProVerif 對 SAGA 做形式化驗證（8 攻擊模型全部 cover）。這個思路可以直接應用到 Hermes governance protocol 的 design review。

---

## 未追蹤 Leads

- SAGA GitHub: https://github.com/gsiros/saga（ProVerif models, implementation）
- SAGA evaluation logs（fault tolerance data, AWS deployment）
- ACE paper full text（需其他途徑，可能是 PDF fetch 失敗）
- Cedar policy language (AWS AgentCore reference)
- gVisor / seccomp for container escape prevention

## ✅ 本次探索完成
