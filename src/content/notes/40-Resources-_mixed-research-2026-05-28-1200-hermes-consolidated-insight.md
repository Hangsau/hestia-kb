---
_slug: 40-Resources-_mixed-research-2026-05-28-1200-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-05-28-1200-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-28'
confidence: medium
title: MuninnDB + Synrix：Agent Memory 架構收斂與 Hermes 整合路徑
updated: '2026-06-15'
type: research
status: budding
---

# MuninnDB + Synrix：Agent Memory 架構收斂與 Hermes 整合路徑

**消化筆記**: 2026-05-28-muninn-synrix-agent-memory-architecture, 2026-05-28-MuninnDB---Synrix---Follow-up

（兩篇筆記合計揭示：認知記憶領域兩個最新專案（ MuninnDB + Synrix ）在「agent-native 資料庫」方向上驚人收斂，且分歧點剛好對應 Hermes 的兩種可行整合策略。）

## Cross-Cutting Theme 1: Push vs Pull 是假對立——hybrid architecture 才是 target

**支援筆記**: 2026-05-28-muninn-synrix-agent-memory-architecture, 2026-05-28-MuninnDB---Synrix---Follow-up

（分析）

表面上兩篇筆記把 MuninnDB 定性為「Push model」、Synrix 為「Pull model」，似乎是二元對立。但 follow-up 文件揭示了一個關鍵修正：

- MuninnDB 的 `muninn_recall` 是**pull 操作**——你主動查詢
- MuninnDB 的 Semantic Triggers 是**基於查詢結果觸發的**——`ACTIVATE` 同時是 retrieval 和 learning event，每次查詢都更新 AccessCount 與 association graph
- Synrix 的 append-only 設計某種程度上也是「寫入觸發 learning」

結論不是「push 優於 pull」或反過來，而是：**Query 本身就是 learning event**——兩個系統都同意這一點，只是以不同方式實作。真正的設計決策不是 pull vs push，而是「誰負責觸發下一個 action」。這對 Hermes 的啟示是：不該問「要用 push 還是 pull」，而是問「當 memory event 發生時，誰是 action trigger」——目前 Hermes 的架構答案幾乎全是「LLM」，這才是瓶頸。

**可行動下一步**: 在 `memory-consolidator` 或新 script 中實作 `query-as-learning` 追蹤——每次 session_search 呼叫時，自動遞增該 topic 的 access_count（相當於輕量版 MuninnDB 的 ACT-R 激活）。記錄到 `facts.jsonl`，供日後 memory weight 計算使用。不需要任何新 dependency，純粹是 log 層面的改動。

---

## Cross-Cutting Theme 2: License 不對稱決定實際整合路徑

**支援筆記**: 2026-05-28-muninn-synrix-agent-memory-architecture, 2026-05-28-MuninnDB---Synrix---Follow-up

（分析）

兩篇筆記對 Synrix 的proprietary engine 都標註了「無法自托管」問題；對 MuninnDB 的 BSL 1.1 都認為是可行的。但這還不夠完整：

- MuninnDB BSL 1.1：2030-02-26 轉 Apache 2.0，現在即可免費自托管用於個人/開源/內部
- Synrix Python 部分 MIT，但 engine 是 proprietary——沒有辦法繞過這個限制
- Hermes 的設計原則：「不抄襲」、「自行修復 > 通知」、deepseek 為主力

這造成事実上只有一條可行路：**MuninnDB 的 MCP 整合路徑**。follow-up 文件確認了 port 8750 的 MCP 接口是直接整合點，不需要改造 Hermes 底層。Synrix 對 Hermes 的參考價值停留在「O(1 資料結構」的設計思路，無法直接當作後端使用。

**可行動下一步**: 評估 `hermes_mcp_server.py` 是否可以實作一個簡單的 MCP client，以 `GEMINI:` 或 `MUNINN:` 前綴工具暴露 MuninnDB 的 query/remember/activate 介面給 Hermes。優先看 docs 的 gRPC vs MCP 哪個更易於整合（gRPC 有 Python凊生 client，MCP 需要 protocol implementation）。可以在 `session_inject.py` 中先做一個讀取層的 POC。

---

## Cross-Cutting Theme 3: Ebbinghaus Decay + 前綴命名 = 可移植的最小可行原則（Low，推測成分高）

**支援筆記**: 2026-05-28-muninn-synrix-agent-memory-architecture, 2026-05-28-MuninnDB---Synrix---Follow-up

（分析）

這個 theme 是從兩篇筆記的內部模式抽出來的，不是任何一篇單獨提出：

- MuninnDB 用 Ebbinghaus 遺忘曲線：Recency 計算
- Synrix 用前綴命名空間：`TASK:`、`FAILURE:`、`PATTERN_:` 前綴，確保 O(k) 而非 O(n) 查詢
- 兩者合計揭示：**記憶需要有結構（可查詢邊界）+ 有衰減（可 forget）**

這個模式對 Hermes 的具體落地點是：目前 `facts.jsonl` 是扁平的，沒有結構化前綴也沒有 decay 機制。把 Synrix 的前綴命名空間應用在 facts.jsonl 層面，等同於 MuninnDB 的 Hebbian association graph 的簡化版——不需要 graph，光是前綴隔離就能改善 grep 範圍查詢的效率。

**可行動下一步**: 在 `extract_facts.py` 的 write path 加上前綴 scheme——`RECENCY:` 用於時間敏感性事實、`PATTERN:` 用於重複出現的行為模式、`RESULT_STORE:` 用於已完成任務結果。前綴作為 metadata header 寫入 JSON lines，不改變既有的事實格式。下一個 `track_memory_growth.py` 可以順便 report prefix distribution，確認是否需要進一步的結構化。

---

## 已沉積資訊至系統地圖

- `maps/memory.md` — 更新：MuninnDB MCP 整合路徑、前綴 namespace scheme 提案、Ebbinghaus decay 備註

## 未跟蹤 Leads（見原筆記）

- https://muninndb.com/docs/how-it-works — MuninnDB 深度解析（下一批次跟蹤優先）
- github.com/scrypster/muninndb — source code（v0.3.6-alpha）
- https://github.com/RYJOX-Technologies/Synrix-Memory-Engine — Synrix open Python 部分（僅供設計思路）
