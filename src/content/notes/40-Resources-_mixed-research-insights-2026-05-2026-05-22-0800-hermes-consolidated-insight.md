---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-0800-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-0800-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-23'
confidence: high
title: 三層一體：Extraction → Storage → Retrieval 的收斂驗證
updated: '2026-06-15'
type: research
status: budding
---

# 三層一體：Extraction → Storage → Retrieval 的收斂驗證

**消化筆記**: 2026-05-23-memori-sdk-triple-extraction-source-analysis, 2026-05-23-memr3-reflective-reasoning-memory-controller, 2026-05-23-locomo-very-long-term-conversational-memory, 2026-05-23-rail-protocol-universal-llm-app-bridge

（摘要）Memori、MemR³、LoCoMo 三者從不同方向抵達同一個核心結論：agent 記憶的瓶頸不在 retrieval 演算法，在 **extraction 品質**。Triple extraction + Evidence-Gap Controller + Observation-as-Fact 三個 pattern 構成一個完整的三層 pipeline，互相填補缺口。

---

## Cross-Cutting Theme 1: Extraction 是瓶頸，不是 Retrieval

**支援筆記**: memori-sdk-triple-extraction-source-analysis, memr3-reflective-reasoning-memory-controller, locomo-very-long-term-conversational-memory

**分析**:

三篇筆記從三個完全獨立的方向抵達同一個設計選擇：

- **Memori SDK** 的 `pipeline.rs` 把 raw LLM 回應 parse 成 `{subject, predicate, object}` semantic triples
- **MemR³** 的 Evidence-Gap Tracker 維護 `(E, G)` 狀態，規定「直到 G = ∅ 才能 answer」，強迫每次 retrieval 都對準 gap
- **LoCoMo** 的實驗資料直接證偽了「大口吃 context = 更好記憶」：adversarial questions 場景下，long-context LLM 比 base 低 83%。但 RAG + observation extraction 逆轉了這個差距

**這三個單獨看都是各自領域的貢獻，放在一起才看清楚**：

```
Raw context → (Memori triple extraction) → Structured facts
↑                                              ↓
↑                                              (MemR3 evidence-gap
↑                                               checks: are gaps filled?)
↑                                                      ↓
↑                                              Storage in knowledge graph
↑                                                      ↓
↑                                   (LoCoMo: RAG on observations > raw text)
←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

**對 Hermes 的衝擊**：目前 heartbeat action log 只有 `op/result/ok` 欄位——這是 raw context，等同於 LoCoMo 實驗中的「未處理對話切片」。整個 vault_decay + heartbeat_learning 系統的瓶頸不是 retrieval strategy，是 extraction。

**可行動下一步**:

1. 將 `heartbeat/actions.py` 的 action log entry 結構加 `triples[]` 欄位，在同一個 LLM call 裡順便 request triple extraction（不另起 call）
2. 參考 Memori 的 `process_attributes` 模式，將 recurring_error detector 從「純 count」升級為「萃取失敗類型指紋」
3. 將 LoCoMo 的 5-type error taxonomy（Missing information / Hallucination / Misunderstanding / Attribution / Saliency）嵌入 WS-024 rubric scoring 的 output schema 作為 `error_types[]` 欄位

---

## Cross-Cutting Theme 2: 三種封裝層級的收斂——Tool Registration、Memory Storage、Retrieval Routing

**支援筆記**: rail-protocol-universal-llm-app-bridge, memori-sdk-triple-extraction-source-analysis, memr3-reflective-reasoning-memory-controller

**分析**:

這三篇筆記各自描述了不同層級的封裝抽象，但底層邏輯驚人地相似：

| 層級 | 筆記 | 核心機制 |
|------|------|---------|
| **Tool Registration** | RAIL Protocol | `rail.manifest.json` auto-generated via reflection/RTTR，把 app methods 自動註冊成 tool definitions |
| **Memory Storage** | Memori SDK | `WriteBatch`（entity_fact.create + knowledge_graph.create + process_attribute.create）封裝成一筆 write operation |
| **Retrieval Routing** | MemR³ | `Router` LLM 決定 `{retrieve, reflect, answer}` 三選一，維護 `(E, G)` 狀態 |

共同模式：**discovery → structured representation → consumption**。RAIL 是「自動發現 app 的 method」；Memori 是「自動萃取對話中的 entity facts」；MemR³ 是「自動判斷還缺什麼 evidence」。三者的差異只是封裝目標不同。

**然而它們沒有連結**：RAIL 是「agent 外」的 tool registration，Memori/MemR³ 是「agent 內」的 memory management。這代表 Hermes 現有架構裡，這兩條線是分開發展的——但它們其實可以共享同一套「structured representation 層」的 infrastructure。

**可行動下一步**:

1. 畫一張 Hermes 架構圖，標示「tool registration / memory storage / retrieval routing」三層的現有實作位置
2. 定義統一的 `StructuredFact` schema，讓 heartbeat action 的 triples 可以同時餵給：
   - memory layer（作為 knowledge graph entry）
   - tool layer（作為 potential tool suggestion based on past execution）
   - routing layer（作為 evidence-gap tracker 的 E)
3. 檢查現有的 `hermes_mcp_server.py` — 它的 async pattern 是否能對接 MemR³ 的 LangGraph-style controller loop

---

## 附：低信心連結（推測成分高）

**Theme**: RAIL 的 Named Pipe IPC vs. Memori/MemR³ 的 API-call abstraction 代表兩種整合哲學

- RAIL 用 Named Pipe（低延遲但綁 OS）把 app→agent 的呼叫做到作業系統層
- Memori/MemR³ 用 API/JSON 把 extraction→storage→retrieval 做到應用層
- Hermes 目前兩種都沒有——是純 in-process function call

→ 這可能暗示 Hermes 需要一個中間層，在 tool invocation 和 memory storage 之間建立 unified structured representation pipeline。這個方向需要更多資料才能確認。

---

## 總結

| Theme | Confidence | Action |
|-------|-----------|--------|
| Extraction 是瓶頸 | High（3 篇交叉） | heartbeat action log + triples 欄位；error taxonomy 進 rubric |
| 三層封裝收斂 | High（3 篇） | 統一 StructuredFact schema；三層架構圖；hermes_mcp_server 對接 LangGraph |
| 整合哲學分歧 | Low | 需更多資料 |