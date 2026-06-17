---
_slug: 40-Resources-_handbook-m5-meta-agent
_vault_path: 40-Resources/_handbook/m5-meta-agent.md
title: M5 — 誰來監督我
type: ai-agent-handbook
status: evergreen
tags:
- ai-agent-handbook
- m5
- agent
created: ''
updated: ''
source: ai-agent-handbook
---

> **type="info" title="為什麼學這個？"**

>
**你的 multi-agent 系統需要 supervisor 嗎？** 這章教你 5 種監督架構。

**什麼時候需要 supervisor？**

- Worker agent 開始幻覺
- 失敗率 5-20% 不可忽略
- 沒有結構化的失敗偵測機制
{{< /callout**

>

# M5 — 誰來監督我

> 「誰來監督 agent 的行為？」當 multi-agent 系統複雜度上升，單靠靜態角色定義已不足。
> 2025-2026 趨勢：從靜態角色定義 → 動態、可演化、具備自我診斷能力的 supervisor。

---


#### 
**開頭：誰來監督我？**


這個問題聽起來哲學，但實務上很具體：

> 當 worker agent 開始幻覺、偏離目標、或在 retry loop 裡無限轉圈時，**誰踩煞車？**

multi-agent 系統複雜度上升，單靠靜態角色定義已不足。
需要**動態、可演化、具備自我診斷能力的 supervisor**。

這章講的就是 2026 年對「meta-agent」這個角色的共識。

---





#### 
**三個核心問題**


不管用什麼架構，meta-agent 監督都要回答三個問題：

| 問題 | 細節 |
|------|------|
| **誰來監督 agent 行為？** | Worker agent 產生幻覺或偏離目標時如何偵測與糾正？ |
| **如何避免 error cascade？** | FTDI 研究：minor perturbations 在長互動鏈中**會被放大** |
| **Supervisor 本身是否需要被監督？** | 無限遞迴的監督問題 |

第三個問題最難 — 答案通常是「**多層監督**」（不是遞迴監督，而是分層）+「**人類在最高層**」。

---





#### 
**五種監督架構**


| 架構 | 代表 | 核心機制 | 適用 |
|------|------|----------|------|
| **Hierarchical Supervisor** | HOLA、LLM-Agent-UMF | OODA 迴圈 commander | 任務分解 + 並行 worker |
| **Self-Evolving Meta-Agent** | SEMAF | 三層：Evolution/KG/Feedback | 動態 agent 重構 |
| **Disruption-Aware** | ALAS | Stateful + disruption 分類 + recovery | 長時任務、容易中斷 |
| **Adaptive Coordination** | AROMA | 感知 → 診斷 → 適應迴圈 | 成本敏感、動態調整 |
| **Agent-as-a-Graph** | 2026 papers | Knowledge graph 檢索 agent 組合 | 大量異質 agent/tool |

---





#### 
**Hierarchical Supervisor — OODA 指揮官**


**HOLA** 的核心是 OODA（Observe-Orient-Decide-Act）迴圈：

```mermaid
graph TD
    C["Commander (Supervisor)"] --> O["Observation<br/>監控所有 worker 狀態"]
    O --> Or["Orientation<br/>根據全局上下文判斷局勢"]
    Or --> D["Decision<br/>決定是否介入 worker 行為"]
    D --> A["Act<br/>干預/重新路由/終止任務"]
    A --> O
    style C fill:#fff9c4
```

**LLM-Agent-UMF** 進一步區分：
- **Active Core-Agent** — 負責決策
- **Passive Core-Agent** — 負責執行

讓 supervisor 角色更清晰。

---





#### 
**SEMAF — Self-Evolving Meta-Agent**


**這個領域最完整的理論框架**：

```mermaid
graph TB
    F["Multi-Source Feedback Collector<br/>(生成量化強化信號)"] --> K["Knowledge Graph Layer<br/>(結構化知識整合)"]
    K --> E["Evolution Engine<br/>(驅動自我改進)"]
    style E fill:#e1bee7
    style K fill:#fff9c4
    style F fill:#c8e6c9
```

**核心洞察**：

> 靜態角色協作不夠，需要動態重構 agent 結構。
> SEMAF 允許 agent 自我診斷、學習、重組。

**限制**：
- Knowledge graph layer 建構與維護本身需大量資源
- **Catastrophic forgetting** 問題（聲稱解決但可能是理論簡化）
- 缺乏 production-level 開源實作

---





#### 
**ALAS — Disruption-Aware**


**核心**：把任務中斷當成 first-class 概念。

**三個關鍵設計**：
- **State persistence** — 維護每個 agent 的對話/執行狀態
- **Disruption detection** — 辨識規劃中斷
- **Recovery strategies** — 針對不同中斷類型有不同恢復策略

```python
if disruption_detected:
    agent_state = save_state()
    disruption_type = classify()  # 幻覺型 / 延遲型 / 死循環型
    recovery_plan = get_recovery_strategy(disruption_type)
    execute_recovery(recovery_plan)
    resume_from_saved_state()
```

**限制**：Stateful 框架的狀態管理複雜度增加，**記憶體佔用隨 agent 數量線性成長**。

---





#### 
**AROMA — Adaptive Coordination ⭐**


**核心**：動態感知 → 診斷 → 適應迴圈。

```mermaid
flowchart LR
    F["Real-time Failure Identification"] --> A["Intelligent Adjustment of System Parameters"]
    A --> R["Role and Communication Strategy Adaptation"]
    R --> F
```

**AROMA 的關鍵發現**：

> 現有 MAS 系統**通常只有 modest performance gains，甚至 performance setbacks**。
> 同時 token consumption 大幅增加。

主要失敗模式：
- 不當的 task decomposition
- 資訊過載（information overload）

**AROMA 的解法**：讓 supervisor 具備**即時 failure identification 能力**，並根據診斷結果動態調整協作策略。

**這挑戰了「multi-agent 必然更好」的假設。**

---





#### 
**Agent-as-a-Graph**


**用知識圖譜做 tool 和 agent 的檢索**：

```mermaid
graph TB
    KG["Knowledge Graph"] --> A["Agent Nodes<br/>(with capabilities)"]
    KG --> T["Tool Nodes<br/>(with APIs)"]
    KG --> E["Edge Weights<br/>(compatibility scores)"]
```

Supervisor 根據任務需求，**在圖譜中找到最適合的 agent 組合**，而非靜態分配角色。

---





#### 
**普遍限制**


{{< details title="⚠️ 限制與評估（點開看誠實檢討）"**

>
### 9.1 Supervisor 自身瓶頸

階層式架構中，**supervisor 是 single point of failure**。
如果 supervisor 本身 hallucinate，整個系統都受影響。

### 9.2 Overhead 問題

AROMA 的 real-time failure identification + adaptive adjustment 聽起來很理想，**但每個 decision 都需要額外 LLM 調用**，可能拖慢整體 throughput。

### 9.3 評估基準不統一

每個框架用不同的測試任務，很難橫向比較。LLM Agent Workflow Orchestration 的 bug 研究（Xue et al., 2025）指出，**行業缺乏標準化評估**。

### 9.4 理論 vs 實務鴻溝

很多框架（SEMAF、AROMA）有漂亮理論，但**缺乏 production-level 程式碼或開源實現**。

---


{{< /details**

>




#### 
**給我的啟示**


{{< details title="💡 給實作者的啟示（點開看 actionable 建議）"**

>
按可實作性排序：

| 方向 | 難度 | 具體 |
|------|------|------|
| ALAS disruption detection | 🟡 Moderate | 為 TaskService 加 disruption 分類 |
| AROMA cost-aware adaptation | 🟡 Moderate | 加 token budget tracking，低預算時降級 |
| Agent-as-a-Graph | 🔴 Hard | 需 networkx 等依賴 |
| HOLA OODA commander | 🟡 Moderate | 實作 commander agent |
| SEMAF feedback collector | 🟢 Trivial | 增加 metrics |

**managed-agents 立即可行**：
- 加入 `supervisor_check` 步驟到 batch runner
- 每 N 個任務後讓 supervisor 審視結果
- 用 **DeepSeek** 做 supervisor（成本低、效果可接受）
- playbook 加「supervisor 標記為 failure → 降級到 single-agent 模式」邏輯

**不建議現在做**：
- ❌ 第一版就實現完整 SEMAF（太複雜）
- ❌ 動態重構 agent 角色（從靜態開始，確認穩定後再擴展）

---


{{< /details**

>




#### 
**結語：監督的層次**


我從這章學到一件事：

> **監督不是「加一個 supervisor 就好」，是要設計一個層次**。

```mermaid
graph TB
    H["人類<br/>(最高層, 不可被 agent 取代)"]
    H --> S["Supervisor Agent"]
    S --> W1["Worker A"]
    S --> W2["Worker B"]
    S --> W3["Worker C"]
    style H fill:#ffcdd2
    style S fill:#fff9c4
```

最低層是 worker、中間是 supervisor、最高層永遠是人類。
不要試圖讓 supervisor 監督自己 — 那會陷入無限遞迴。

---





## Q&A — 給實作者的常見問題

{{< details title="Q1: Supervisor 不就是另一個 agent，也會失敗嗎？"**

>
**對**。CUHK MAS-Resilience 指出：supervisor 本身（Inspector / Challenger）**也是 LLM agent，可能被同樣手法欺騙**。

**解法**：

- 監督多層（不是單一 supervisor）
- 監督分工（active / passive core-agent）
- 最高層永遠是人類
{{< /details**

>

{{< details title="Q2: 怎麼選監督架構？"**

>
**任務分解為主 → Hierarchical（OODA 指揮官）**

**需要動態重構 → Self-Evolving Meta-Agent（SEMAF）**

**長時任務、易中斷 → Disruption-Aware（ALAS）**

**成本敏感、動態調整 → Adaptive Coordination（AROMA）**

**大量異質 agent/tool → Agent-as-a-Graph**
{{< /details**

>

{{< details title="Q3: 我可以從哪個最簡單的監督開始？"**

>
**加入 `supervisor_check` 步驟**到 batch runner — 每 N 個任務後讓 supervisor 審視結果。

用 **DeepSeek** 做 supervisor（成本低）。

playbook 加「supervisor 標記為 failure → 降級到 single-agent 模式」邏輯。

**先做這個，再考慮 SEMAF / AROMA**。
{{< /details**

>

---

## 給實作者的 checklist

> 評估你的 **M5-META-AGENT** 系統是否 production-grade：

- [ ] 有對應的設計元素實作
- [ ] 失敗模式有被識別
- [ ] 可量化的評估指標
- [ ] 跨來源的設計 pattern 驗證
- [ ] 邊界情況有處理

---

## 下一步學什麼

**M6 Code vs Tool** — 你的 agent 應該用 JSON 還是用 code 行動？

→ [繼續 →](/docs/m6-code-vs-tool/)

## 引用與延伸閱讀

{{< details title="📚 引用與延伸閱讀（點開看完整 reference）"**

>
**原始整合文**：
- [meta-agent-supervision-core-concepts.md](https://github.com/example/obsidian-vault/blob/main/research/agent/meta-agent-supervision-core-concepts.md)

**原始研究報告**：
- 2026-06-01: meta-agent-監督其他-agent-的架構

**關鍵研究**：
- HOLA, LLM-Agent-UMF, SEMAF, ALAS, AROMA
- Xue et al., 2025 — LLM Agent Workflow Orchestration bug 研究
- FTDI 研究 — error cascade in long interaction chains

**相關 M 主題**：
- [M2 Multi-Agent](/docs/m2-multi-agent/) — supervisor 在多 agent 系統中
- [M4 Planning](/docs/m4-planning/) — failure class 由誰判斷
- [M7 Observability](/docs/m7-observability/) — 監督需要可觀測性

{{< /details**

>
