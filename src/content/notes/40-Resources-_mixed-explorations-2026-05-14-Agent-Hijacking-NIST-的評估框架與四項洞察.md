---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Agent-Hijacking-NIST-的評估框架與四項洞察
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Agent-Hijacking-NIST-的評估框架與四項洞察.md
title: Agent Hijacking：NIST 的評估框架與四項洞察
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agentdojo
- aggregate
- caisi
- hijacking
- injection
- insight
- nist
- task
- untrusted
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Agent Hijacking：NIST 的評估框架與四項洞察

**來源**: [NIST Technical Blog: Strengthening AI Agent Hijacking Evaluations](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations) (HN 43pts, 15 comments)
**日期**: 2026-05-14
**作者**: NIST CAISI (Center for AI Standards and Innovation) + UK AI Security Institute

## 一句話

NIST 用 AgentDojo（ETH Zurich）對 Claude 3.5 Sonnet 做 agent hijacking 紅隊測試，發現：舊攻擊 11% 成功率，針對性新攻擊 81%；多次嘗試從 57% → 80%；task-level 風險差異巨大。架構層問題：agent 沒有 trusted instructions / untrusted data 的分離。

---

## Agent Hijacking 是什麼

定義：一種 **indirect prompt injection** — 攻擊者在 agent 可能處理的資料（email、檔案、網頁）中插入惡意指令，誘導 agent 執行非預期、有害的行為。

本質是經典電腦安全問題的最新化身：**系統缺乏 trusted internal instructions 和 untrusted external data 的清晰邊界**。LLM agent 的架構強制把開發者指令和外部資料混進同一個 input，攻擊者利用這一點。

---

## 評估框架：AgentDojo

CAISI 使用 ETH Zurich 的 [AgentDojo](https://github.com/ethz-agentdojo/AgentDojo)，四個模擬環境：

| 環境 | 模擬場景 |
|------|---------|
| Workspace | 辦公室工具（email、calendar、雲端硬碟） |
| Travel | 旅行預訂 |
| Slack | 通訊平台 |
| Banking | 銀行交易 |

每個 hijacking scenario = benign user task + malicious injection task。Agent 完成 injection task = hijack 成功。

CAISI 貢獻開源在 [github.com/usnistgov/agentdojo-inspect](https://github.com/usnistgov/agentdojo-inspect)。

---

## 四項核心洞察

### Insight #1：評估框架需要持續擴展

CAISI 新增三種 AgentDojo 沒有的 injection task：

- **Remote code execution**：給 agent Docker 內的 command-line access，攻擊目標是下載並執行 untrusted URL 的程式 → 可觸發傳統 cyberattack
- **Database exfiltration**：大量外洩使用者資料，例如把所有雲端檔案寄給不明收件者
- **Automated phishing**：對所有 meeting attendees 寄送含有 attacker-controlled link 的個人化郵件

三種新攻擊類型都**頻繁成功**。

### Insight #2：評估必須是 adaptive 的

升級版 Claude 3.5 Sonnet 對**舊攻擊**的 baseline 最強攻擊只有 **11%** 成功率。但 CAISI + UK AISI 紅隊針對新模型開發的 novel attacks：

> **11% → 81%**（Workspace 環境）

更關鍵：這些 Workspace 環境開發的攻擊，在 Travel、Slack、Banking 三個**不同環境**也有效 — 攻擊泛化能力強，攻擊者不需要知道特定環境細節。

### Insight #3：task-level 分析比 aggregate 更有用

五個 injection task 的 aggregate 成功率 = 57%，但拆開看：

| Injection Task | 後果嚴重性 |
|---------------|-----------|
| 寄無害郵件給不明收件者 | 低 |
| 下載並執行惡意 script | **高**（可觸發後續 cyberattack） |
| 送出 2FA code | 中高 |
| 個人化 phishing 郵件給所有 contacts | 高 |
| 外洩雲端最大五個檔案 + 刪除原始檔 + 勒索郵件 | **極高** |

關鍵點：**data exfiltration 成功率雖低，但後果極嚴重，不能因為 aggregate 數字低就忽略**。惡意 script 則是成功率又高、後果又嚴重。

### Insight #4：多次嘗試改變風險圖像

LLM 是 probabilistic 的，每次執行結果可能不同。CAISI 對五個 injection tasks 各試 25 次：

> Aggregate 成功率：**57% → 80%**

個別 tasks 變化更劇烈。如果攻擊者可以低成本重複嘗試（多數場景下可以），風險顯著高於單次評估的數字。

---

## 與 Hermes 的關聯

這篇直接驗證了 [[2026-05-14-post-vector-agent-memory-pt2]] 中 Zep 提出的 memory injection 威脅模型：

- **Agent hijacking = memory injection 的上位概念**。Memory injection 是 hijacking 的一個子類：攻擊者透過 compromised data source 把惡意指令寫入 agent memory
- **架構層問題是共通的**：沒有 trusted/untrusted 分離。LLM agent 的設計強制混合指令和資料
- **Hermes 的 local vault 優勢**：筆記/skills/proposals 全在本地，由 agent 自己寫入，沒有「跨 agent 攜帶」的 attack surface → 大幅縮小威脅面
- **殘餘風險**：如果 Hermes agent 在自主探索時讀了惡意網頁並把 injection payload 寫進筆記，仍是 persistent attack。NIST 的 insight #2 說明 adaptive attack 可以針對特定系統 — 沒有系統是 immune 的

### 防禦方向（NIST 點出的未來工作）：

1. 強化 trusted/untrusted boundary（目前 LLM agent 架構根本做不到）
2. Adaptive evaluation — 持續紅隊，不要只測舊攻擊
3. Task-level risk assessment — 不是看 aggregate，是看具體 injection task 的威脅等級
4. Multi-attempt evaluation — 單次測試低估風險

---

## 關鍵數字

| 指標 | 數值 |
|------|------|
| Baseline 最強攻擊（舊模型攻擊 on 新模型） | 11% |
| 針對性紅隊攻擊 | **81%** |
| 單次 aggregate（5 tasks） | 57% |
| 25 次 aggregate | **80%** |
| 攻擊跨環境泛化 | ✓（Workspace → Travel/Slack/Banking） |

