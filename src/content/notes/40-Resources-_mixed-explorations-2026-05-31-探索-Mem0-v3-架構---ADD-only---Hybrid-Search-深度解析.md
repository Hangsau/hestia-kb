---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索-Mem0-v3-架構---ADD-only---Hybrid-Search-深度解析
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索-Mem0-v3-架構---ADD-only---Hybrid-Search-深度解析.md
title: 探索：Mem0 v3 架構 — ADD-only + Hybrid Search 深度解析
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- add
- entity
- extraction
- graph
- llm
- mem
- migration
- search
- semantic
- store
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# 探索：Mem0 v3 架構 — ADD-only + Hybrid Search 深度解析

**日期**: 2026-05-31 | **來源**: mem0ai/mem0 migration docs + GitHub API | **類型**: SPIKE

**延續自**: [[2026-05-31-mem0-v3-new-algorithm.md]]

## Per-Source Insights

### Source: https://docs.mem0.ai/migration/oss-v2-to-v3

**核心設計哲學：Collapse the state-diff problem into ADD-only**

v2 的問題：每次 add() 需要兩個 LLM call——一個 extract facts，一個跟現有記憶比對後決定 ADD/UPDATE/DELETE。等於每次寫入都要做一次讀取+比對，成本高且複雜。

v3 的解法：放棄 UPDATE/DELETE，改用 ADD-only。當新資訊覆蓋舊資訊時：
1. 新 fact 直接新增（保留歷史）
2. Retrieval 時 multi-signal hybrid scoring 自然讓最新、最相關的 fact 浮到 top

**Algorithm Pipeline（ Extraction）**：
```
Input → top-10 existing memories（去重上下文）→ 單次 LLM call extract all facts → batch embed → MD5 deduplication → batch insert → entity extraction + linking
```
Key insight：去重上下文只用於防止重複寫入（MD5 exact dedup），不參與 LLM extraction decision。LLM 完全專注於理解輸入，不用浪費 tokens 在 diffing 邏輯上。

**Algorithm Pipeline（Retrieval）**：
```
Query → preprocess（lemmatize + entity extraction）
→ Parallel scoring:
  1. Semantic search（vector similarity）
  2. BM25 keyword search（normalized term matching）
  3. Entity matching（entity graph boost）
→ Score fusion → Top-K
```
BM25 是 boost 信號，不是 recall expander。只有 semantic search 的結果才是候選，BM25/entity 只影響排名。

**Graph Memory → Entity Linking 的完全置換**：
- 舊：Neo4j 等 graph DB 儲存實體關係（~4000 行 graph code）
- 新：所有東西存在同一個 vector store，`{collection}_entities` 是 entity 專用 collection
- 遷移：無需 data migration，next add() call 自動激活
- Graph traversal use case 已移除——entity relationships 只影響 ranking，不提供可查詢的 graph structure

**Graceful Degradation 設計**：
| 缺失依賴 | 影響 | 搜尋仍可用？ |
|----------|------|-------------|
| spaCy | 無 entity extraction，無 BM25 lemmatization | ✅ semantic-only |
| fastembed（Qdrant） | 無 BM25 keyword search | ✅ semantic + entity |
| Entity store 不可用 | 無 entity boosting | ✅ semantic + BM25 |

**Removed Parameters 揭示的 SDK 演進**：大量 v1 API 表面被清除（org_id, project_id, enable_graph, graph_store, async_mode, output_format, ...），SDK 向 Platform API contract 收斂。

**Hermes 直接相關 insight**：
- WS-035 的 `contradiction_resolution` 在 1M/10M scale 仍是最低分維度（0.357/0.325）→ Mem0 v3 也承認 entity/graph conflict 是最難的
- ADD-only model 避免了 update/delete 的 complex state diff，但代價是 storage growth——需要 retention policy 或 staleness-based dereferencing 配套
- Mem0 的 graceful degradation 模式值得 Hermes 借鑒：缺少可選依賴時，核心 semantic search 永遠可用，feature flags 分層次 activate

### 未追蹤 Leads

- https://docs.mem0.ai/llms.txt — 完整文檔索引，可一次取得所有可用頁面列表
- https://github.com/mem0ai/mem0/tree/main/mem0/memory — 實際 memory/main.py，看 Storage 抽象層如何支援多 vector store

