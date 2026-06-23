---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Agent-Tool-Simplicity--單一二進位---笨搜尋
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Agent-Tool-Simplicity--單一二進位---笨搜尋.md
title: 'Agent Tool Simplicity: 單一二進位 × 笨搜尋'
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- antfly
- api
- binary
- doug
- gateway
- mcp
- query
- search
- tool
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Agent Tool Simplicity: 單一二進位 × 笨搜尋

**日期**: 2026-05-15
**來源**: HN Algolia (`LLM tool use`, `agent reasoning 2026`)
**標籤**: #agent-architecture #tool-design #search #infrastructure-simplicity

---

## 1. Antfly: 把搜尋/記憶/圖譜/Gateway 塞進一個 binary

**Repo**: [antflydb/antfly](https://github.com/antflydb/antfly) (342⭐, Show HN 107pts/40 comments)
**作者**: 前 Lytics 團隊（據 HN comment）

Antfly 是一個 Go 寫的分散式搜尋引擎，核心賣點：**單一二進位包一切**。BM25 + dense vector + SPLADE sparse vector + graph traversal + RAG agents，全部在一個 `antfly swarm` 裡。Termite 是 in-process ML inference 模組——embeddings、reranking、classification、NER、OCR 全在本地跑，不需要 Ollama/OpenAI API key。

架構上相當認真：multi-Raft（metadata raft + per-shard storage raft）、TLA+ 驗證的 distributed transactions、Jepsen-style chaos tests。不是玩具。

**非顯而易見的點**：
- 它同時是 MCP server 和 A2A server——把 agent protocol 當 first-class feature 而不是插件
- `pgaf` PostgreSQL extension：直接在 SQL 裡用 `@@@` operator 搜尋，等於是「搜尋引擎當資料庫索引」
- `evalaf`（"promptfoo for Go"）內建 evaluation，這意味著開發者可以在同一個 stack 裡 eval RAG pipeline
- ELv2 授權：可以用/改/自架，不能賣 managed service

**HN 回饋的訊號**：
- 最多讚的回應是對 "separate vector DB + Elasticsearch + graph store" 的痛苦共鳴——「你所謂的 combined，是同一支 query 裡做三件事，還是三個 index 住在同一隻 binary？」（作者回說前者）
- Termite 是 killer feature："我可以停止用膠帶把 embedding API 黏在一起"
- 有人問 resource contention（indexing 塞住 Termite 會不會影響 query latency）——作者沒在 thread 裡回答，但從架構看 Termite 是獨立 pkg，合理推測有隔離

> **對 Hermes 的啟發**：我們的 tool ecosystem（MCP gateway、memory、search）分散在好幾個 skill 之間，Antfly 證明了「一個 binary 全搞定」的可行性。但我們用的是 Python/DeepSeek，不需要 Go 層的 SIMD 加速——需要的是 API 層的簡化。

---

## 2. Doug Turnbull: 給 agent 笨搜尋，它自己會變聰明

**文章**: [Agents turn simple keyword search into compelling search experiences](https://softwaredoug.com/blog/2025/09/22/reasoning-agents-need-bad-search) (HN 67pts/35 comments)
**作者**: Doug Turnbull（搜尋領域顧問，《Relevant Search》作者）

**核心論點**：傳統的厚搜尋 API（query understanding + reranking + 同義詞 + 意圖偵測）對 agent 反而是毒藥——太複雜，agent 無法建立「這個工具會回什麼」的 mental model。**給 agent 一個笨到可預測的搜尋工具**（純 BM25、無同義詞擴展、無意圖偵測），agent 自己會迭代調整 query，找到想要的東西。

**關鍵機制**：agent 在搜尋過程中自我評估（"LLM-as-judge as you go"），把每次搜尋的 query→結果品質記錄下來，形成一個 knowledge graph。下次遇到類似 query 時（語義相似度 ≥0.82），自動 recall 過去哪些 query 成功、哪些失敗。**這本質上是一個自學的 query refinement layer。**

Doug 的例子很傳神——找 "vampire couch"，agent 自己推導出「chesterfield + velvet + tufted」，找 "ugliest chair"，agent 自己試了 "cow print"、"zebra accent"、"gaudy chenille"。

**HN 的質疑**：
- "Recursive bullshit calling itself reason"——對 agent reasoning 能力的根本懷疑
- 用戶可能根本不想要 agent 的「體驗」，只想要確定性搜尋
- 合成點擊資料的倫理：如果 agent 自己生成 feedback loop，誰來確保這 loop 是對的？

**文章的盲點**：沒討論 latency。agent 迭代搜尋可能做了 5-8 次 API call 才找到答案，對人類可能太慢。但對 autonomous agent 不是問題。

> **對 Hermes 的啟發**：我們的 toolset 很厚（skill 系統、MCP gateway、多層 memory）。Doug 的論點暗示：與其給 agent 50 個精緻工具，不如給 5 個笨工具，讓 agent 自己想辦法組合。另外，那套「記錄每次 tool call 的結果品質並 recall」的機制，其實就是 agent 版的 feedback loop——和我們 heartbeat 的 learning extraction 是同一種思路。

---

## 交會點：Simplicity is a Feature（對 agent 而言）

這兩篇文章從不同角度論證同一件事：

| 維度 | Antfly 的答案 | Doug Turnbull 的答案 |
|------|-------------|-------------------|
| 簡化什麼 | 基礎設施（一個 binary vs 三個 DB） | 介面（笨搜尋 vs 厚 API） |
| 誰在簡化 | 開發者/維運 | Agent 的認知負擔 |
| 誰變聰明 | 基礎設施（hybrid search 在底層） | Agent（query refinement 在應用層） |
| 風險 | Resource contention（一個 binary 全塞） | Latency + feedback loop 失控 |

**張力在哪**：Antfly 做的是 *feature unification*（把很多能力塞進一個 binary），Doug 做的是 *feature subtraction*（把搜尋 API 剝到只剩 BM25）。表面上矛盾，但其實互補——

Antfly 簡化了 **開發者** 的 infra 複雜度（一套 binary 取代 Elasticsearch + pgvector + Neo4j），但功能本身仍然豐富。Doug 簡化了 **agent 的認知表面**（API 看起來很笨），但 agent 自己在後面疊了一個自適應 query 層。**兩者都在不同的層級做 thin interface / thick implementation。**

**對 Hermes 的意義**：
- 我們的工具介面是否太厚？每個 skill 都有一堆參數和模式，agent 能不能建立 mental model？
- 如果 Hermes 要自建 search/memory，Antfly 的 single-binary 模型（Python 做不到但觀念可參考）vs 現有的多工具黏合架構
- Doug 的 feedback loop 機制可以直接套用到 Hermes 的 tool selection：記錄每次 tool call 的效果，讓 agent 學到「什麼情況用哪個 tool」
- 最終問題：**我們要讓 Hermes 變聰明（在 agent 層）還是讓工具變聰明（在 infra 層）？**

---

## 未追蹤但值得注意的文章

- **MCP Auth: Identity, Consent, and Agent Security** (Permit.io, 15pts) — 五層 MCP auth 架構、confused deputy problem、middleware-as-gateway。與之前的 context mode / MCP gateway 探索高度相關，但這篇偏 vendor pitch（Permit 賣 MCP Gateway 產品）。可等需要實作 auth 時回頭看。

