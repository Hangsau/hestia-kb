---
_slug: 40-Resources-_mixed-research-2026-05-30-0600-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-05-30-0600-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-30'
confidence: high
title: LLM Agent Memory 架構：Staleness 機制與多訊號檢索的收斂確認
updated: '2026-06-15'
type: research
status: budding
---

# LLM Agent Memory 架構：Staleness 機制與多訊號檢索的收斂確認

**消化筆記**: 2026-05-29-llm-agent-memory-architecture.md, 2026-05-30-agemem-grpo-graphiti-temporal-kg.md

兩篇探索筆記各自調查獨立的論文與框架，卻在"記憶操作應該是政策決定而非規則"與"檢索必須多訊號融合"這兩個軸心上收斂，為 Hermes 當前架構的不足之處提供了量化方向。

---

## Cross-Cutting Theme 1: 記憶操作的「政策 vs 規則」二元性

**支援筆記**: 2026-05-29-llm-agent-memory-architecture.md (§MLMF), 2026-05-30-agemem-grpo-graphiti-temporal-kg.md (§AgeMem)

兩篇筆記指向同一個深層結論：記憶的讀寫刪除不該是固定的規則引擎，而應該是根據情境自適應的政策決策。

- **Note 1 (MLMF Survey)**: 記憶控制策略分為三類——heuristic / prompted self-control / learned control——且指出 Mem0/MemGPT 停留在 prompted self-control，而 Agentic Memory (Yu et al. 2026) 已進入 learned control 階段。POMDP  formulation 把記憶定位為 belief state，寫壞了會汙染整個下游推理鏈。
- **Note 2 (AgeMem)**: GRPO 三階段訓練把「記憶操作」變成可學習的工具呼叫策略——何時 store/summarize/discard 是 policy 而非 rule。這與 Note 1 的 learned control 類別完全對齊，且提供了具體的訓練pipeline。

**關鍵洞察**：Hermes 的 heartbeat_learning.py 目前實作的是 decay（Ebbinghaus 曲線），這是 heuristic 等級。Note 1 明確指出「staleness vs decay 是不同的 failure mode」，Note 2 的 GRPO 框架則告訴我們從 heuristic → learned controller 需要的不是更多 if-then，而是 RL 訓練訊號。兩篇筆記合在一起確認：heartbeat_learning.py 缺少的不是更多規則，而是一個能區分「該 decay」vs「該 invalid 立即替換」的訊號源。

**可行動下一步**: 在 heartbeat_learning.py 現有的 `relevance_score` 曲線上新增一個並行的 `confidence_valid_until` 欄位（UTC timestamp），針對高影響事實（例如 skill 版本號、tool endpoint、API version）做 staleness 標記。實作一個 `check_staleness()` 方法，在每次心跳時比對 `now > confidence_valid_until` 的 entry 並觸發 re-fetch 或 mark invalid。不要用 rule-based invalidation——用一個簡單的 reward signal（ Retrieval 命中率是否在 confidence_valid_until 之後顯著下降）來決定哪些 entry 需要這個欄位，逐步建立學習訊號。

---

## Cross-Cutting Theme 2: 多訊號檢索 vs 單一向量——驗證與實作路標

**支援筆記**: 2026-05-29-llm-agent-memory-architecture.md (§Mem0, §Atlan), 2026-05-30-agemem-grpo-graphiti-temporal-kg.md (§Zep/Graphiti)

三個獨立研究來源全部指向同一個結論：semantic vector search 作為單一訊號不夠，三訊號融合（semantic + BM25 + entity matching）比任何單一訊號都好。

- **Note 1 (Mem0)**: 6,956 tokens/query vs 26,000 full-context，4× 效率，來自 multi-signal retrieval。LoCoMo +29.6 pts, multi-hop +23.1 pts。
- **Note 1 (Atlan/Zep benchmark)**: Zep 的 temporal KG 領先 Mem0 15 points (63.8% vs 49.0%) 在 LongMemEval，差距來自 validity windows + temporal edges，不是更好的 embedding。
- **Note 2 (Graphiti)**: 90% latency 改善 vs naive RAG，來自 KG traversal 對 multi-hop query 的維持度優於 flat similarity search。

**關鍵洞察**：三篇資料都驗證了「檢索瓶頸不在 embedding quality，在於缺少結構化訊號」。Hermes vault 現有 wiki-links 是隱性的圖結構邊，BM25 可由 Obsidian 的搜索功能某程度提供，但 entity matching 和 temporal reasoning 完全是空白。三篇筆記合在一起確認：不要先最佳化 embedding，先把三個訊號都架起來再用 RRF 融合。

**可行動下一步**: 在 vault 的搜尋入口（`search_vault` skill 或對應的指令）實作三個獨立的檢索管道：① 現有 semantic search（拿來），② BM25 keyword search（可用 sqlite FTS5 或 python 的 rank_bm25），③ entity matching（用 vault 的 `#tag` 和 `^^cite` 語法做簡單的共現計數）。三路並行，結果用 **Reciprocal Rank Fusion** 合併輸出 ranking。兩個量測指標：P@5 和 MRR@5 在每次vault搜尋時追蹤，作為日後是否需要升級到 Graphiti-style temporal KG 的量化門檻（參考：Zep 90% latency 改善是我們的 target）。

---

## 架構層級結論

這兩篇筆記收斂出一個確定的優先順序：

1. **現在做**：多訊號檢索（semantic + BM25 + entity），RRF 融合——風險低，馬上能測量
2. **下一個 cycle 做**：staleness 機制（`confidence_valid_until` + re-fetch policy）——需要新的學習訊號但有明確的評估指標
3. **有數據後才做**：learned memory controller（AgeMem GRPO 風格）——當 P@5/MRR@5 顯示規則驅動的檢索已遇到瓶頸時，才從 Pattern B 升級到 Pattern C