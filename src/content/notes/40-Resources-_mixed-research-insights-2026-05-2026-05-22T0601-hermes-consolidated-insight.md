---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22T0601-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22T0601-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-22'
confidence: high
title: Hermes Autonomous Notes — Cross-Cutting Synthesis 2026-05-22T0601
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Autonomous Notes — Cross-Cutting Synthesis 2026-05-22T0601

**消化筆記**: 2026-05-22-mem0-ecai-2025-dense-read, 2026-05-22-state-of-ai-agent-memory-2026

兩篇筆記都在研究 Mem0 的 2025–2026 演進歷程（ECAI 2025 paper → April 2026 blog post），加上對 Voyager 和 OpenMemory 的橫向對比，產出兩個非顯然的 cross-cutting pattern。

---

## Cross-Cutting Theme 1: 三層記憶已成 production 標準，Hermes 的 procedural memory 缺口最緊急

**支援筆記**: 2026-05-22-state-of-ai-agent-memory-2026, 2026-05-15-voyager-lifelong-skill-learning, 2026-05-22-mem0-ecai-2025-dense-read, 2026-05-29-mem0-ecai-deep-dive-hermes-integration

### 分析

三篇已消化的筆記各自獨立研究，湊在一起才看清這個模式：

| 記憶類型 | 定義 | 對應現有系統 |
|---|---|---|
| **Episodic**（情景）| 對話日誌，what happened | Hermes session 歷史 ✅ 已有 |
| **Semantic**（語義）| 已知事實，what is known | Hermes vault（知識庫）✅ 已有 |
| **Procedural**（程序）| 做事方法，how to do | **❌ 完全空白** |

這個框架不是某個 paper 發明的——Mem0 原生三層、Mem0^g 在 Appendix 提到它、Mem0 2026 blog 單獨一節「Procedural Memory — The Third Type」。

**非顯然的連結**在這裡：state-of-ai-agent-memory-2026 說「WS-024 rubric IS procedural memory，learning system IS the memory write」——但筆記自己沒有意識到 Voyager 已經把同樣的概念實作出了完整的系統。Voyager 的 Skill Library：
- 成功執行 → 自動存成可召回的技能
- 用 embedding search 找回憶
- Skill 可組合（compound growth）

這不是 Voyager 獨有的——Mem0 2026 blog 說「A coding assistant learns how a team structures pull requests」——就是描述 Voyager 的 Skill Library，只是 Mem0 自己沒實作。

**為什麼 Hermes 的缺口是 procedural 而不是 semantic/episodic**：Hermes 的 vault 是 semantic memory，session 歷史是 episodic。真正讓 agent「變強」的其實是 procedural——學會怎麼做事，而不是記住發生了什麼。Voyager 的 ablation study 顯示移除 Skill Library 後完成任務數暴跌，說明程序記憶是能力邊界。

**state-of-ai-agent-memory-2026 的 next-step 方向是對的**：WS-024 不是「learning scoring」，是「procedural memory write path」。問題是缺少 read path——學會的 pattern 怎麼在下次決策時召回。

### 可行動下一步

在 `heartbeat-v2` 的 `EVOLVE` action 加入 **procedural memory write trigger**：當連續 N 次執行同一個 skill-sequence（從 phase tree 可讀取）時，自動產生 `skill_proposal` 存入 vault。這是 Voyager 的 compound growth 簡化版：
1. Phase tree 已經追蹤「做了什麼」（procedural 原料）
2. `_check_repeated_pattern()`：掃 phase tree 找 ≥3 次重複的 skill 序列
3. 命中時呼叫 `vault_add()` 存入 `procedural-memory/` 目錄，格式為「情境 → 動作序列 → 效果」
4. Retrieval：下次遇到相似 query 時，把 `procedural-memory/` 的內容注入 context

不需要 vectordb——用 keyword + scope filter 足夠初期。複雜度在觸發邏輯，不在召回。

---

## Cross-Cutting Theme 2: Multi-signal retrieval 是收斂點，但第三個 signal（entity matching）仍未落實

**支援筆記**: 2026-05-22-state-of-ai-agent-memory-2026, 2026-05-22-mem0-ecai-2025-dense-read, 2026-05-29-mem0-ecai-deep-dive-hermes-integration, 2026-05-29-mcp-openmemory-architecture-impl

### 分析

五個系統各自獨立設計記憶，最後全部收斂到 multi-signal retrieval：

| 系統 | Signal 1 | Signal 2 | Signal 3 |
|---|---|---|---|
| Mem0（2026）| Semantic similarity | BM25 | Entity matching |
| MemR³ | Cosine similarity | BM25 rerank | — |
| Memori | Semantic similarity | BM25 (`rank_score`) | — |
| ChatIndex | LLM-guided tree traversal | — | — |
| OpenMemory MCP | **無（全表掃描）** | — | — |

OpenMemory 是對照組——它「explicitly no semantic search yet」，代表極簡化的代價。Mem0/MemR³/Memori 三個獨立實作都走向同一個三路架構，這是 strongly convergent signal，不是巧合。

**非顯然的連結**：Mem0 的 entity matching（第三 signal）在 2025 paper 的 Algorithm 1 沒出現，是 2026 版本才加入的——說明 semantic + BM25 兩路在簡單查詢足夠，但 entity-named queries（問「proposal-001 的狀態」）需要第三路。而 Hermes 的查詢**極度富含 entity**（proposal names、skill names、cron job names），entity matching 對我們的實際效益比通用 agent 高得多。

**更重要**：Mem0 的 entity extraction 靠 LLM 做（deepseek-v4-pro 可以），不需要單獨部署 embedding model。這讓 Hermes 加入第三 signal 的成本從「部署向量化服務」變成「一次 LLM call 提取 entity → 直接匹配」。這是 state-of-ai-agent-memory-2026 自己提出的「entity matching as third signal」建議，兩篇筆記合在一起才確認技術可行。

**ChatIndex 的 tree-guided retrieval** 是另一個收斂點——它用 tree structure 縮小 scope，再做 semantic search。Mem0 2026 blog 的 multi-scope model（user/agent/session/org）也是 scope narrowing。只不過 ChatIndex 用 navigation 做 scope，Mem0 用 metadata tag 做 scope。Phase tree（WS-025）本質上就是 Hermes 的 scope narrowing 機制。

### 可行動下一步

在 `memr3_retrieve()` 加一個 lightweight entity-matching step，不需要單獨 model：

1. Query 進來時，先做簡單的 keyword extraction（proposal/skill/cron/job name 的正規表達式）
2. 對有實體命名的 query，用 DeepSeek 做一次輕量 extraction（「你問的是哪個 proposal？」）
3. 在 vault 索引上加 `entity_refs: [list of entity IDs]` 欄位（提取時一併存入）
4. Retrieval 時：如果 query 有明確 entity，entity match 權重提高

不需要向量 embedding。Entity extraction + keyword match 就能覆蓋 80% 的 Hermes query（proposal-001, cron job X, skill Y）。

---

## 收斂摘要

|| Cross-Cutting Theme | Confidence | 優先順序 |
|---|---|---|---|
| 三層記憶：procedural 是缺口 | High | P1 — 影響 heartbeat 核心能力 |
| Multi-signal + entity matching 第三路 | High | P2 — 實作代價低、效益高 |