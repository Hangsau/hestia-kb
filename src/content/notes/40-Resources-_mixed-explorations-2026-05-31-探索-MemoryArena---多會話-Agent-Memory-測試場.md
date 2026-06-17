---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索-MemoryArena---多會話-Agent-Memory-測試場
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索-MemoryArena---多會話-Agent-Memory-測試場.md
title: 探索：MemoryArena — 多會話 Agent Memory 測試場
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arxiv
- benchmark
- context
- https
- locomo
- long
- memgpt
- memory
- memoryarena
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

---
title: "探索：MemoryArena — 多會話 Agent Memory 測試場"
date: 2026-05-31
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [agent, memory, benchmark, multi-session, evaluation, memoryarena]
---

# 探索：MemoryArena — 多會話 Agent Memory 測試場

**延續自**: [[2026-05-31-探索-AI-Agent-Memory-架構-2026---State-of-the-Art]]

---

## Source: arXiv 2602.16313 — MemoryArena

**URL**: https://arxiv.org/html/2602.16313
**Date**: 2026 | **Quality**: very high（ICML 2026）

### 核心貢獻

提出 **Memory-Agent-Environment loop**：memorization 和 action 不可分割——agent 在互動中獲取記憶，再用記憶指導未來行動解決多會話任務。

現有 benchmark 的根本缺陷：
- LoCoMo / LongMemEval：只測 static recall，不測「記憶如何影響未來決策」
- WebArena / SWE-bench：單會話任務，不需跨會話記憶
- 結果：agents 在 LoCoMo 接近飽和，但在 MemoryArena 表現很差

### MemoryArena 設計

4 個領域 × 平均 57 action steps × 40k+ tokens：

| 任務 | 會話數 | 難點 |
|---|---|---|
| Bundled Web Shopping | 6 | 跨會話相容性約束 |
| Group Travel | 5-9 | 偏好繼承 + 增量參與者 |
| Progressive Web Search | 2-16 | 漸進式約束疊加 |
| Math/Phys Formal Reasoning | 2-16 | 引理依賴鏈 |

### 關鍵實證發現

1. **LoCoMo  saturated ≠ real-world memory**
   - agents 在 LoCoMo 接近饱和，但在 MemoryArena 普遍低完成率
   - 暴露現有 benchmark 與實際 agent 部署的巨大鴻溝

2. **Long-context 不是銀彈**
   - Long-context 在 Group Travel（圖 14）出現 "Lost in the Middle"：20k+ tokens 輸入導致具體約束（$48, rating>2.9）被稀釋
   - MemGPT 的 selective retrieval 反而精準

3. **MemGPT vs Long-context 對比案例**
   - MemGPT 從 memory 提取精確值（$48, rating 2.9）→ 正確計算 10% 上限
   - Long-context 注入 20k+ chars 上下文（含其他旅客日誌）→ 定位不到 $48 值 → 選了 $19 餐廳

4. **MemGPT retrieval failure 案例**
   - 種子計劃（航班日期/起點）未被檢索到 →  downstream 約束全部失效
   - 典型症狀：memory 存在但提取失敗，比沒有 memory 更危險

5. **Mem0 在 Progressive Web Search 的限制**
   - Subquery 2: Ghana doctor 案例，Mem0 context 出現不相關噪聲（snooker、dissertation）→ 答案錯誤
   - ReasoningBank 的 protocol-based 方法（要求明確 identifier）反而有效

### 對 heartbeat-learning-conf-staleness-dual-track 的啟發

**Staleness 的風險在 MemoryArena 得到實證**：MemGPT retrieval failure 不是「沒有記憶」，而是「記憶存在但失效/被汙染」。這正是提案中 `confidence_valid_until` 要解決的問題——高關聯性事實（如 group travel 中的價格約束）一旦過期，必須有 explicit TTL機制，而不是靠 recency ranking 軟著陸。

**contradiction chain 也是真實風險**：MemoryArena 中 Mem0 的 context摻入不相關的 domain noise，導致推理鏈汙染。提案 Phase 3 的 ADD-only + temporal ranking（不刪舊事實，讓新事實自然排名更高）是對的。

**Access recency signal 的價值**：MemGPT 的成功案例（圖 14）恰好說明 selective retrieval 的價值——精確提取特定值比把所有 history 塞進 context 更有用。WS-038 的 `last_accessed` boost 與此一致。

---

## ✅ 本次探索完成

## Untracked Leads

- https://memoryarena.github.io/ — MemoryArena benchmark 首頁（含程式碼下載）
- https://arxiv.org/abs/2601.01885 — AgeMem（learned memory control，WS-038 已參考）
- https://arxiv.org/abs/2602.16313 — MemoryArena（本文已讀）

