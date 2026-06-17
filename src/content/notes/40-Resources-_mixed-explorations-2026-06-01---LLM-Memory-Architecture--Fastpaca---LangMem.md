---
_slug: 40-Resources-_mixed-explorations-2026-06-01---LLM-Memory-Architecture--Fastpaca---LangMem
_vault_path: 40-Resources/_mixed/explorations/2026-06-01---LLM-Memory-Architecture--Fastpaca---LangMem.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 44:\n     ... -06-01 — LLM Memory Architecture: Fastpaca + LangMem\n\
  \                                         ^"
_raw_fm: '

  title: 2026-06-01 — LLM Memory Architecture: Fastpaca + LangMem

  date: 2026-06-01

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, background, facts, langmem, memory, semantic, staleness, tool,
  user, working]

  created: 2026-06-01

  updated: 2026-06-15

  status: active

  '
title: '2026-06-01 — LLM Memory Architecture: Fastpaca + LangMem'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# 2026-06-01 — LLM Memory Architecture: Fastpaca + LangMem

**探索來源**: 2026-06-01-Agent-Memory--An-Anatomy---2026-06-01.md 的「未追蹤 Leads」
**性質**: 主題延續（Agent Memory: An Anatomy 探索的後續）

## Fastpaca — "Ultimate Guide to LLM Memory"

**URL**: https://fastpaca.com/blog/ultimate-guide-to-llm-memory
**作者**: Sebastian Lund | **日期**: 2026-01-16

### 核心：四層記憶 taxonomy

| 層 | 用途 | 典型實作 | 失敗影響 |
|---|---|---|---|
| **Working** | 執行狀態追蹤 | scratch pad, last N messages | Task fails mid-run |
| **Episodic** | 跨 session 歷史 | summarization, conversation logs | "discussed earlier" breaks |
| **Semantic** | 跨 session 事實 | entity extraction, user profiles | User re-explains preferences |
| **Document** | 外部知識庫 | RAG, vector search | Hallucination from stale docs |

**重要 framing**：每層的 failure semantics 不同——Working/Document 失敗是毀滅性的（task 失敗或幻覺），Episodic/Semantic 失敗只是摩擦（user re-explains）。

### 關鍵 insight：Memory ≠ Database

> "Modern databases are robust and deterministic. LLMs are not. You have an upper limit on the amount of data you can include and shove into an LLM until it becomes slow, costly, and inaccurate."

這和 "Forgetting as Retrieval Problem" 探索的核心主張一致：記憶系統的設計約束不是 storage 而是 retrieval quality + context window budget。

### Composability principle

每層可獨立 swap。架構上要能「在不重寫其他層的情況下替換任意層」。這是 Hermes heartbeat_learning.py 的設計方向——bounded dereferencing 和 confidence_valid_until 應該是獨立的，不綁定在一起。

### Prompt layout 有預算限制

> "LLMs focus on the beginning and end of a prompt. Middle sections fade into background noise."
> "Whichever memory type dominates your prompt gets more of the model's focus."

實務建議：給每個 memory type 一個 token ceiling (e.g., RAG: 2000, summaries: 1000, user facts: 500)。系統指令和當前 query 永遠在，dynamic memory types 有優先級和可選性。

### Failure semantics table（值得參考）

| Layer | When it fails | Product impact |
|---|---|---|
| Working | LLM forgets mid-task | Task fails, user restarts |
| Episodic | "discussed earlier" breaks | User re-explains |
| Semantic | LLM forgets who you are | Minor friction |
| Document | Hallucinates from stale docs | Trust erodes |

→ 這張表可以用來定義 heartbeat_learning.py 的 staleness severity threshold：Working layer 失效 = high severity trigger，Semantic layer 失效 = low。

---

## LangMem (LangChain) — github.com/langchain-ai/langmem

**URL**: https://github.com/langchain-ai/langmem | **⭐**: 1.5k | **License**: MIT
**PyPI**: `pip install -U langmem`

### 核心設計：Hot Path vs Background 雙軌

LangMem 有兩種記憶管理模式，剛好對應 staleness proposal 的兩個 track：

**1. Hot Path（in-conversation）**
- `create_manage_memory_tool` + `create_search_memory_tool`
- Agent 在對話中主動呼叫 tool 管理記憶（`store` / `search`）
- 記憶決策由 LLM 在對話 flow 中即時做出
- 對應：event-driven invalidation（`confidence_valid_until` 由 agent 在收到矛盾資訊時寫入）

**2. Background（out-of-conversation）**
- `BackgroundMemoryManager` — 非同步運行於背景
- 自動 extraction/consolidation/update，不需要 agent 觸發
- 對應：sleep-time compute + periodic reconciliation

### API 設計細節

```python
from langmem import create_manage_memory_tool, create_search_memory_tool

tools = [
    create_manage_memory_tool(namespace=("memories",)),
    create_search_memory_tool(namespace=("memories",)),
]
```

兩個 tool 都基於 LangGraph 的 `BaseStore` interface：
- InMemoryStore（dev/dev），可替換為 AsyncPostgresStore（production）
- 儲存格式：`{"data": "...", "created_at": "...", "updated_at": "..."}`
- embed dimension 可自訂（openai:text-embedding-3-small 等）

### 和 staleness proposal 的直接對應

| LangMem 功能 | staleness proposal 機制 |
|---|---|
| Hot path memory tool（in-conversation） | `confidence_valid_until` — agent 在對話中寫入 TTL |
| BackgroundMemoryManager | Sleep-time compute — 定期 consolidation |
| InMemoryStore / AsyncPostgresStore | `facts.jsonl` backing store |
| namespace-based isolation | `facts.jsonl` 的 topic/agent 分離 |

LangMem 的 dual-track 證實了 staleness proposal 的方向是正確的——業界領先專案也在做同樣的分離。

### LangMem 没有 explicit staleness detection

LangMem 的 background manager 做 extraction/consolidation，但文檔中沒有提到時限性 staleness（`confidence_valid_until` 之類的）。它有 `updated_at` 欄位，但沒有提到如何處理「高關聯性事實突然變錯」的情況。這仍是 open problem。

---

## 跨文章 Synthesis

### 1. 四層 taxonomy 驗證了 Hermes 架構方向

Fastpaca 的 Working/Episodic/Semantic/Document 和：
- Mem0 的 semantic layer（user facts）
- Memento 的 bitemporal model（valid time = episodic）
- LangMem 的 hot/background separation

全部收斂到同一個結論：**結構化記憶 > 純嵌入檢索**。Hermes 的 `heartbeat_learning.py` 走向是對的。

### 2. LangMem 的 dual-track 是 staleness proposal 的實作參考

LangMem 做 hot path + background 分離，已驗證可行。staleness proposal 的 `confidence_valid_until`（hot path）+ sleep-time consolidation（background）可以參考 LangMem 的介面設計（tool-based vs background manager）。

### 3. Prompt budget 概念對 heartbeat/learning 有啟發

「每個 memory type 給 token ceiling」的設計，可以用來約束 `facts.jsonl` 的膨脹：
- Working memory 層：無 ceiling（context window 決定）
- Semantic memory 層：有 ceiling（`max_facts` + LRU eviction）
- Bounded dereferencing = semantic layer 的 budget enforcement

### 4. Failure semantics 對 staleness severity 有幫助

Fastpaca 的 failure table：
- Working: task fail → high severity
- Semantic: minor friction → low severity

可以用來設定 staleness threshold：
- `access_staleness >= 0.8`（WORKING 類）：通知升級
- `confidence_valid_until` 過期（SEMANTIC 類）：低优先级，background 處理

---

## Hermes 啟發

1. **LangMem hot path tool pattern**：`create_manage_memory_tool` 可以移植到 Hermes agent 讓 agent 自己寫入 `confidence_valid_until`。不需要全新的機制——現有的 `write_memory` / `update_fact` 工具可以加這個參數。

2. **BackgroundMemoryManager 的替代方案**：LangGraph 的 async background manager 可以借鑒，但 Hermes 目前沒有 LangGraph 整合。可以評估用 cron 實現同等功能（`memory-auto-distill` 已有基礎）。

3. **Prompt layout budget 概念**：HB 的 `max_facts` + LRU eviction 是這個概念的變體。可以考慮加一個 explicit budget alert（`facts.jsonl` 超過 N 筆時觸發 heartbeat warmup）。

4. **Staleness severity 分級**：從 Fastpaca 的 failure semantics 衍生：
   - Working layer staleness（agent 執行中）→ 立即通知
   - Semantic layer staleness（user facts）→ 低優先級，cron 處理

---

## 未追蹤 Leads

- https://news.ycombinator.com/item?id=45789672 — HN thread（仍是 leads， 未 fetch）
- Anthropic Dreams: platform.claude.com/docs/en/managed-agents/dreams — 仍是 leads
- LangMem background manager source: https://github.com/langchain-ai/langmem/blob/main/src/langmem/manager.py — 可以看 implementation

## ✅ 本次探索完成

**延續自**: [[2026-06-01-Agent-Memory--An-Anatomy---2026-06-01.md]]
