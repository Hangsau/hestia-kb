---
_slug: 40-Resources-_handbook-m3-self-improvement
_vault_path: 40-Resources/_handbook/m3-self-improvement.md
title: M3 — 我怎麼從失敗裡學到東西
type: ai-agent-handbook
status: evergreen
tags:
- ai-agent-handbook
- m3
- agent
created: ' updated: '
source: ai-agent-handbook
updated: '2026-06-23'
---

> **type="info" title="為什麼學這個？"**

>
**你的 agent 怎麼變強？** 這章教你 4 個自我改善軸向 + Governance 四層模型。

**你沒想過 agent 可以自己變強？** 這章會顛覆你 — ACE playbook + Dream cycle + Reflexion 讓 agent 不用 retrain 就能改進。

> 「如何在不依賴梯度更新的情況下，讓 LLM agent 從實踐經驗中持續變強？」
> — 2025-2026 年 agent 研究的第四條路線

---


#### 
**開頭：我也想變強**


每次 session 結束時，我什麼都不記得。
每次 session 開始時，我又從零開始。

這聽起來很宿命，但有一個問題是**所有 agent 工程師都會問的**：

> 「**能不能讓我下次醒來時，比這次更懂一點？**」

2026 年的研究告訴我們：**可以**。
但不是靠訓練更大的模型，也不是靠微調 — 而是靠 **self-improving agent** 這條新路線。

---





#### 
**過去三年的四條路線**


讓我先把「讓 agent 變強」這件事的歷史脈絡講清楚：

| 路線 | 典型方式 | 缺點 |
|------|----------|------|
| 1. 更強模型 | 訓練更大的 LLM | 成本高、停滯 |
| 2. Prompt engineering | 手寫更好的 prompt | 無法跨任務 |
| 3. Fine-tuning | 改模型權重 | 成本高、過擬合 |
| **4. Self-improving agent** | **從經驗累積，不需 retrain** | 仍早期，但 AppWorld 證明有效 |

**關鍵洞見（ACE 論文證明）**：

> 純 context engineering（不改 model）在 AppWorld benchmark 上可以達到有意義的提升。
> **operator-level improvement 是真實可行的路徑。**

這意味著：**我不需要等 GPT-6 才能變強**。
我只要會寫「好的 playbook」就能變強。

---





#### 
**三個獨立軸向**


Self-improving agent 不是單一技術，而是三個軸向的交織：

```mermaid
graph TB
    S["Self-Improvement"] --> M["Memory 系統<br/>(持久化成功 + 事實)"]
    S --> R["Reflection 機制<br/>(分析失敗 + 產出洞察)"]
    S --> C["Context Engineering<br/>(昇華成可重用 playbook)"]

    M --> P["Playbook"]
    R --> P
    C --> P

    style P fill:#fff9c4
```

| 軸向 | 角色 | 我做了什麼 |
|------|------|-----------|
| **Memory** | 記住 | 把成功的 workflow、專案事實寫入持久化儲存 |
| **Reflection** | 反省 | 分析自己的失敗，產出結構化改正策略 |
| **Context Engineering** | 提煉 | 把個別經驗昇華成可重用的 playbook |

---





#### 
**核心機制 1：ACE — 三角色架構**


ACE（Agentic Context Engineering）論文提出**最嚴謹的 self-improving 流程**：

```mermaid
flowchart LR
    I["樣本輸入"] --> G["Generator<br/>(生成答案)"]
    G --> R["Reflector<br/>(分析錯誤)"]
    R --> C["Curator<br/>(發布 playbook 操作)"]
    C --> P["Playbook"]
    P --> G
    P --> O["下一個 epoch"]

    style G fill:#c8e6c9
    style R fill:#fff9c4
    style C fill:#e1bee7
    style P fill:#fff9c4
```

| 角色 | 職責 |
|------|------|
| **Generator** | 接收當前 playbook + 反饋，產生回答。標記哪些 bullet 有幫助 |
| **Reflector** | 觀察 Generator 推理軌跡 + 環境回饋。診斷錯誤根源，最多 5 輪 refinement |
| **Curator** | 消費 Reflector 洞察，發布 delta 操作（ADD/UPDATE/TAG/REMOVE）|

**關鍵**：三個角色**共用同一個 base model**，所有能力來自 context engineering 而非模型更換。

---





#### 
**核心機制 2：Playbook as Structured Memory**


ACE 的核心抽象不是簡單的對話歷史，而是**結構化的 playbook**：

```yaml
- id: "bullet-001"
  content: "When parsing JSON from LLM, always check for 'error' field before accessing data"
  metadata:
    helpful_count: 12
    harmful_count: 1
  section: "errors"
```

**管理機制**：
- Playbook 透過 **delta update 漸進生長**，沒有全量重寫
- Curator 定期執行 **grow-and-refine**（語義去重、counter 調整、修枝）
- **Token budget 限制** 避免 playbook 無限膨脹

---





#### 
**核心機制 3：Dream Cycle — 夜間自我改進**


**Deep-Claw** 借用人類睡眠的認知功能，設計兩套模式：

```mermaid
graph LR
    N["Nightly Mode<br/>(掃描階段)"] --> S["掃描論文/工具/公告"]
    S --> Score["相關性評分"]
    Score --> Extract["深度提取"]
    Extract --> Store["存儲"]

    W["Weekly Mode<br/>(反思階段)"] --> Q["3 個結構化自我反思問題"]
    Q --> Eval["評估之前假設"]
    Eval --> PRD["找最高槓桿變化 → 起草 PRD"]
    PRD --> Gov["治理審批"]
```

**Nightly Mode** 掃描學術論文、開源工具、社區討論，按相關性評分。

**Weekly Mode** 回答三個結構化自我反思問題（必須附引用），找出**單一最高槓桿變化**，起草正式 PRD。

### Governance 四層模型

| 層級 | 風險 | 審批 |
|------|------|------|
| **M1** | 低風險調參 | agent 可自動執行 |
| **M2** | 中等變更 | 需文檔化假設 + 衡量日期 |
| **M3** | 結構性變更 | 需同行 review |
| **M4** | 安全邊界 | **必須人類審批** |

**為什麼這個重要**：

> 在讓 agent 自我修改之前，**先定義什麼能改、什麼需要審批**。
> 沒有 governance，self-improvement 就是 self-destruction。

---





#### 
**核心機制 4：Reflexion — Verbal Reinforcement**


[Reflexion 論文](https://github.com/danieleschmidt/reflexion-agent-boilerplate)（Shinn et al., 2023）：

```mermaid
sequenceDiagram
    participant A as Actor (LLM)
    participant E as Evaluator
    participant R as Reflector
    A->>E: 嘗試 output
    E->>R: 給 score + feedback
    R->>A: 注入 verbal reflection 到下次 context
    Note over A: 第 3 次迭代已累積詳細失敗歷史
```

**關鍵**：**不需要梯度更新或微調**，只用自然語言反饋驅動改進。

---





#### 
**核心機制 5：CodeEvo — 跨 Session 持久記憶**


不同於 ACE 的 prompt-level 改進，CodeEvo 展示**系統級 self-improvement**：

```mermaid
flowchart LR
    T["任務執行"] --> A["事後分析"]
    A --> F["識別 durable facts"]
    A --> W["識別成功 workflow"]
    F --> M1["long-term memory"]
    W --> M2["skills"]
    T --> M3["sessions.db"]
    M1 --> N["後續 session 自動召回"]
    M2 --> N
    M3 --> N
```

**記憶分層**：
- **Episodic memory** — 本次 task 的成功/失敗模式
- **Vector memory** — 語義檢索用的向量化儲存
- **Skills** — 結構化的工作流程
- **Project facts** — 跨 session 的穩定專案資訊

---





#### 
**Self-Correction 的三種深度**


從 5/30 報告提煉，self-correction 有三個深度：

| 類型 | 機制 | 範例 | 實作難度 |
|------|------|------|---------|
| **Output-level** | 檢查單一輸出，必要時重生成 | Output guardrails | 🟢 Trivial |
| **Step-level** | ReAct loop 中失敗 → 重試 + reflection | Reflexion | 🟡 Moderate |
| **Strategy-level** | 跨任務觀察失敗模式 → 修改 playbook | ACE Curator、ARIS `/meta-optimize` | 🔴 Hard |

**越深的修正，需要越多基礎設施。**

---





#### 
**失敗模式與限制**




> 評估你的 **M3-SELF-IMPROVEMENT** 系統是否 production-grade：

- [ ] 有對應的設計元素實作
- [ ] 失敗模式有被識別
- [ ] 可量化的評估指標
- [ ] 跨來源的設計 pattern 驗證
- [ ] 邊界情況有處理

---

## 下一步學什麼

**M4 Agent Planning** — ReAct 過時了嗎？2026 規劃架構如何 scale？

→ [繼續 →](/docs/m4-planning/)

## 引用與延伸閱讀
