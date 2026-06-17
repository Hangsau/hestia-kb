---
_slug: 40-Resources-_handbook-m7-observability
_vault_path: 40-Resources/_handbook/m7-observability.md
title: M7 — 跑久了怎麼 debug
type: ai-agent-handbook
status: evergreen
tags:
- ai-agent-handbook
- m7
- agent
created: ''
updated: ''
source: ai-agent-handbook
---

> **type="info" title="為什麼學這個？"**

>
**你的 agent 跑 production 出事？** 這章教你 4 個解法 + Memory self-governance。

**你還沒跑 production？** 這章仍然必讀 — observability 是基礎設施，**現在不做以後會痛**。

> 當 AI agent 在生產環境跑久了，最大的噩夢不是「回答錯誤」，是「不知道為什麼錯」。
> Observability 從「加分」變「必要」。

---


#### 
**開頭：噩夢不是錯，是「不知道為什麼錯」**


跑 agent 系統最痛苦的不是「它答錯了」。
是「**它答錯了，我打開 log 看，發現我完全不知道它為什麼這麼選**」。

```mermaid
graph LR
    A["Agent 答錯"] --> Q["為什麼？"]
    Q --> L["Log 海洋"] --> C["看不出 LLM 在哪一步選錯"]
    C --> D["Debug 失敗"]
    style D fill:#ffcdd2
```

Observability 在 2026 變必要不是因為「debug 體驗」這種小事 —
是因為 **agent 自主性提升** 跟 **架構複雜度上升** 兩個力量同時擠壓。

- Agent 自主決策多了 → 出錯時你需要完整 replay
- Multi-agent 串起來了 → 一個 worker 失敗會 cascade
- Memory-augmented 跑久了 → 不知道 agent 「記得」什麼

**沒有 observability 的 agent 系統是個黑盒**，跑 production 就是賭博。

---





#### 
**四個核心解法**


| 工具 | 核心價值 | 層 |
|------|----------|-----|
| **Memoria** | Memory 自我治理（Git for AI Memory）| Storage layer |
| **OpenLIT** | OpenTelemetry-native LLM observability | Telemetry layer |
| **OpenViking** | Context 當檔案系統管理（L0/L1/L2）| Context layer |
| **AgentPrism** | Trace 可視化 UI | Visualization layer |

---





#### 
**Memoria — Git for AI Agent Memory ⭐**


**核心洞見**：記憶不只是「存放」，是「版本控制」。

**Git 操作直接移植到 agent 記憶**：

```python
memory_branch(name="eval_sqlite")    # 開實驗分支
memory_checkout(name="eval_sqlite")  # 切換分支
memory_merge(source="eval_sqlite")   # 合併或刪除
memory_diff(source="branch")          # 預覽差異
# Snapshot + rollback at any point-in-time
```

**底層**：MatrixOne MVCC（arXiv 2604.03927, 2026-04）— TB 等級資料上做 clone/branch/diff/merge/revert 是 **near-instantaneous**，不需要把整個 dataset 載入記憶體。

### 自我治理（Self-Governance）

```mermaid
flowchart LR
    M["記憶進來"] --> CD["矛盾偵測"]
    CD --> Q["低信心記憶<br/>quarantine"]
    CD --> A["審計軌跡<br/>(audit trail)"]
    style Q fill:#ffe0b2
    style A fill:#c8e6c9
```

- **自動偵測記憶矛盾** — 不會假裝沒事
- **隔離低信心記憶** — quarantine 而非直接寫入
- **維護完整 audit trail**

這是這個領域最重要的概念：

> **Memory 不再只是 storage，是 governance。**

### 對比傳統 RAG

| 維度 | Memoria | Letta/Mem0/Traditional RAG |
|------|---------|----------------------------|
| Version control | **Native zero-copy snapshots & branches** | File-level or none |
| Isolation | **One-click branch** | Manual data duplication |
| Audit trail | **Full snapshot + provenance** | Limited logging |
| Retrieval | Vector + fulltext hybrid | Vector only |
| **Self-governance** | **Auto contradiction detection & quarantine** | Manual cleanup |

**對「Git 類比」的懷疑**：
Memoria 宣稱「Git for AI Agent Memory」，但 **Git 的核心價值是協作**（多人對同一 codebase）+ **branch/merge review**。
Agent memory 的 branch/merge 更多是「實驗性嘗試」而非多人協作。
**「Git 類比」可能有 marketing 成分高於實質**。

---





#### 
**OpenLIT — OpenTelemetry-native LLM Observability**


**優雅**：

```python
import openlit
openlit.init(otlp_endpoint="http://127.0.0.1:4318")
```

一行就接上 OpenTelemetry backend。

**核心功能**：

| 功能 | 說明 |
|------|------|
| **11 種 built-in evaluation** | hallucination, bias, toxicity, safety, instruction following, completeness, conciseness, sensitivity, relevance, coherence, faithfulness |
| **LLM-as-a-Judge** | context-aware（以提供的 context 為 ground truth）|
| **Rule Engine** | AND/OR 邏輯定義條件規則 |
| **Prompt Hub** | 版本化、管理 prompts |
| **Cost Tracking** | 自訂模型定價檔案，精確預算 |
| **Fleet Hub** | OpAMP 管理多個 OpenTelemetry Collectors |

支援 Python/TypeScript/Go SDK，**vendor-neutral**（接任何相容 OpenTelemetry 的 backend）。

---





#### 
**OpenViking — Context 當檔案系統**


**放棄傳統 RAG 的 flat vector storage**，把 context 管理當檔案系統設計。

### 五層挑戰對應五個解法

| 挑戰 | OpenViking 解法 |
|------|-----------------|
| Fragmented Context | **Filesystem paradigm**（統一管理 memories/resources/skills）|
| Surging Context Demand | **L0/L1/L2 三層漸進載入**（按需載入節省 token）|
| Poor Retrieval | **目錄定位 + 語意搜尋**，遞迴精確獲取 |
| Unobservable Context | **可視化 retrieval trajectory**，可看 root cause |
| Limited Memory Iteration | 自動壓縮對話內容，萃取長期記憶 |

### L0/L1/L2 三層架構

- **L0** — 壓縮後的濃縮記憶
- **L1** — 中度摘要
- **L2** — 完整原始內容

**按需漸進載入**，agent 需要什麼深度就載到哪層。
（這跟 [M1 Memory](/docs/m1-memory/) 的 L0/L1/L2 是同源概念）

---





#### 
**AgentPrism — Trace 可視化 UI**


**把 OpenTelemetry trace data 轉成 React component**，主打「讓 trace 不是 JSON 海洋」：

```tsx
<TraceViewer
  data={[{
    traceRecord: yourTraceRecord,
    spans: openTelemetrySpanAdapter.convertRawDocumentsToSpans(yourTraceData),
  }]}
/>
```

**提供**：
- **Trace List** — 多筆 trace 列表
- **Tree View** — 階層式 span 可視化，支援搜尋和 expand/collapse
- **Details Panel** — 單一 span 屬性檢視
- **Adapter 模式** — OpenTelemetry、Langfuse 等格式都可轉換

---





#### 
**限制與誠實評估**




> 評估你的 **M7-OBSERVABILITY** 系統是否 production-grade：

- [ ] 有對應的設計元素實作
- [ ] 失敗模式有被識別
- [ ] 可量化的評估指標
- [ ] 跨來源的設計 pattern 驗證
- [ ] 邊界情況有處理

---

## 下一步學什麼

**M8 Bench / Routing / MCP Security** — Production-grade 三大支柱

→ [繼續 →](/docs/m8-benchmarks/)

## 引用與延伸閱讀
