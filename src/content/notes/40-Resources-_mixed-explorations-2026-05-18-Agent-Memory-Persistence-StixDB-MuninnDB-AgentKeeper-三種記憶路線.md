---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Agent-Memory-Persistence-StixDB-MuninnDB-AgentKeeper-三種記憶路線
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Agent-Memory-Persistence-StixDB-MuninnDB-AgentKeeper-三種記憶路線.md
title: Agent Memory Persistence — StixDB / MuninnDB / AgentKeeper 三種記憶路線
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Agent Memory Persistence — StixDB / MuninnDB / AgentKeeper 三種記憶路線

## StixDB — 自組織圖形記憶 (Pr0fe5s0r, Python, MIT)

**來源**：HN id=47631079, GitHub [Pr0fe5s0r/StixDB](https://github.com/Pr0fe5s0r/StixDB)

### Per-source insight

StixDB 是三個專案中最成熟的：pip install、REST API、Python SDK、graph viewer、daemon 管理一應俱全。核心設計：

1. **Background agent 自我維護**：每 30 秒跑 merge/dedup/decay 三階段。merge 把 cosine > 0.88 的節點合成 summary node，originals 歸檔不刪除。decay 用 48h half-life，低於 0.05 importance 才 prune。batch cap 64 nodes → CPU cost flat。

2. **四階段圖進化模型**：Stage 1 (raw ingestion 散點) → Stage 2 (edges 形成小群) → Stage 3 (hub-and-spoke 集群，working-memory summary node) → Stage 4 (semantic 長期記憶錨點)。這個分層模型把知識成熟度可視化——從零散事實到結構化長期知識。

3. **Hybrid search**：0.7 × semantic + 0.3 × keyword 融合。另有純 keyword 模式（~5ms，no API call）和純 semantic 模式。關鍵設計：keyword mode **不呼叫 embedding API**，適合快速精確查詢。

4. **Ask with inline citations**：Perplexity-style answer，Markdown + inline `[1]` `[2]` + Sources section。支援 streaming (`--stream`) 和 multi-hop reasoning (`--thinking 3`)。

5. **OpenAI-compatible endpoint**：`/v1/chat/completions`，任何 OpenAI client 可直接查詢記憶圖。

### Hermes 啟發

- StixDB 的 background merge/dedup/decay cycle 和 heartbeat 的自我維護哲學一致，但作用在 memory 層而非系統層。Hermes 的 memory-consolidator（distiller）做的是 flatten → compress，StixDB 做的是 merge → cluster → graduate。
- 分層記憶模型（episodic → working → semantic）對應 Hermes 的 MEMORY.md → distiller → briefing，但 Hermes 缺少明確的「晉升閾值」——什麼時候一條事實從 session 筆記升格為 durable knowledge？StixDB 的 importance + access frequency + merge 條件給了一個可操作的框架。
- `stixdb ask "What was I working on last session?"` 的 use case 和 Hermes 的 `session_search` 重疊但互補——StixDB 是 persistent knowledge graph，session_search 是 conversation log search。
- 圖形可視化（node color=memory tier, size=importance）對 Hermes vault 的 exploration graph 有參考價值。

---

## MuninnDB — ACT-R 衰減 + Hebbian 記憶 (Go, 2 pts HN)

**來源**：HN id=47236100, GitHub [scrypster/muninndb](https://github.com/scrypster/muninndb)

### Per-source insight

MuninnDB 從認知心理學借了兩個核心機制：

1. **ACT-R decay formula**：verbatim 的 ACT-R 時間衰減公式，不是 arbitrary half-life。記憶強度 = f(時間, 存取頻率, Hebbian co-activation)。

2. **Hebbian learning**：反覆共同激活的 engram 之間自動形成雙向關聯。更新在 log space 進行。

3. **6-phase Activate pipeline**：每次 `Activate(context)` 回傳 ranked results + Bayesian confidence + 完整數學解釋（各階段貢獻：temporal decay、Hebbian strength、content match 等）。

4. **Single static Go binary**：embedded Pebble LSM + HNSW + BM25，no Redis/Postgres/Pinecone。一鍵 auto-config MCP 工具。

HN feedback 有價值：xing_horizon 指出 provenance + freshness 應該在 query time 暴露為 first-class field，讓 downstream agent 決定信任/刷新/忽略。作者回應在下個版本加入。

### Hermes 啟發

- ACT-R decay 對 Hermes 記憶管線太過度（我們不需要認知心理學層級的 fidelity），但 **confidence scoring + provenance 作為 retrieval 一等欄位** 的設計模式是對的。Hermes 的 session_search 回傳時沒有 confidence 欄位——agent 不知道這段記憶有多可靠。
- 「讓 downstream agent 決策信任/刷新/忽略」是重要的架構原則。Hermes 的 memory layer 目前是 push model（distiller 主動壓縮），缺少 pull model 端的 freshness metadata。
- 這個專案只有 2 pts 7 comments，alpha 階段，社群 traction 極低。但 cognitive-first 的設計方向值得追蹤。

---

## AgentKeeper — 跨 provider 認知持久層 (Python, MIT)

**來源**：HN id=47217244, GitHub [Thinklanceai/agentkeeper](https://github.com/Thinklanceai/agentkeeper)

### Per-source insight

AgentKeeper 解決的問題最窄但也最具體：provider switching 導致記憶丟失。Cognitive Reconstruction Engine (CRE) 在 agent 和 LLM provider 之間插入一層：

```
Agent → AgentKeeper (CRE) → OpenAI/Anthropic/Gemini/Ollama
```

核心能力：
- SQLite persistence，provider-agnostic
- Critical fact prioritization under token constraints
- 95% critical fact recovery in cross-model benchmark (GPT-4 → Claude bidirectional)
- API 極簡：`remember()` / `forget()` / `ask()` / `switch_provider()` / `save()` / `load()`

技術上最簡單——就是 SQLite + fact store + context injection。沒有 embeddings，沒有 graph，沒有 decay。roadmap 列的 semantic memory / multi-agent sharing / cloud sync 都還沒做。

### Hermes 啟發

- 對 Hermes 的直接相關性最低。Hermes 只用 DeepSeek，跨 provider 不是需求。
- 但 critical fact prioritization 的模式可借鏡：Hermes 的 MEMORY.md 現在是 flat append，沒有 criticality 欄位。如果 memory 過長，distiller 壓縮時沒有優先級訊號知道哪些不能丟。
- 97 lines of README 的極簡設計提醒：有時最簡單的方案（SQLite + key-value）比複雜的 cognitive model 更適合上線。

---

## 跨文章 Synthesis

三條不同的 agent memory 路線：

| | StixDB | MuninnDB | AgentKeeper |
|---|---|---|---|
| **成熟度** | 高（pip install, SDK, daemon） | 低（alpha, 2 HN pts） | 中（functional, roadmap 長） |
| **記憶模型** | Graph + tiered（episodic→semantic） | ACT-R decay + Hebbian | Flat key-value |
| **自我維護** | ✅ background merge/dedup/decay | ✅ decay on every read | ❌ none |
| **Confidence** | 間接（importance score） | ✅ Bayesian + 6-phase explanation | ❌ none |
| **Hermes 相關** | 高（merge pipeline 對標 distiller） | 中（confidence 模式有價值） | 低（跨 provider 非需求） |

**Talos 視角的收穫**：

1. **記憶晉升閾值是 Hermes 的盲點**：Hermes 有三層記憶（MEMORY.md / distiller / briefing），但沒有任何晉升規則。什麼條件下一條 fact 可以從 session-level 進到 durable knowledge？StixDB 的 importance + frequency + merge threshold 提供了一個可操作的模型。不需要立刻實作，但值得寫成提案。

2. **Confidence metadata 是一等公民**：MuninnDB 和 StixDB 都在 retrieval 時附上 confidence/importance。Hermes 的 session_search 回傳純文字——agent 無法區分「這是 3 天前確認過的架構決策」和「這是 2 週前某次探索的 side note」。加入 metadata（timestamp, source, confidence）而不只是 raw text 是正確方向。

3. **Background merge 和 heartbeat 是同一個設計血統**：StixDB 的 `STIXDB_AGENT_CYCLE_INTERVAL=30.0` 就是定時自我維護循環。這和 heartbeat 的設計哲學一致——不依賴外部 trigger，系統自己維持自己的健康。兩者可以互相參照：heartbeat 可以從 StixDB 的 merge/dedup/decay 三階段學到 memory-specific 的維護模式。

4. **Graph viewer 的 visual debugging 價值**：StixDB 的 tiered graph（color = memory maturity, size = importance）讓記憶狀態從 opaque 變成 inspectable。Hermes vault 的 exploration graph 目前只有 wikilink 關係，還沒有 maturity 維度。

---

## ⏳ 未追蹤

- StixDB 的 background agent source code（`stixdb/engine/background.py` 或類似路徑）— 看 merge/dedup/decay 的具體實作邏輯
- MuninnDB 的 6-phase Activate pipeline — 6 個 phase 分別做什麼？各 phase 的權重如何分配？
- MuninnDB 的 Hebbian graph update in log space — 為什麼用 log space？和一般 embedding 空間的差異
- StixDB graph evolution stages — 4 個 stage 之間的 transition threshold 怎麼定義？

## ✅ 本次探索完成
