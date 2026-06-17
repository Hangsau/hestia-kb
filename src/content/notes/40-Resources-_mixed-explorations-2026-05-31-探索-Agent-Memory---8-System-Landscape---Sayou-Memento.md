---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索-Agent-Memory---8-System-Landscape---Sayou-Memento
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索-Agent-Memory---8-System-Landscape---Sayou-Memento.md
title: 探索：Agent Memory — 8 System Landscape + Sayou/Memento
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- bitemporal
- fts
- github
- https
- memento
- memory
- model
- sayou
- time
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# 探索：Agent Memory — 8 System Landscape + Sayou/Memento

**日期**: 2026-05-31 | **來源**: HN trending leads (synix.dev, sayou github, memento-memory github) | **類型**: 探索

## 核心發現

### 1. Synix — 8 System Source-Level Analysis (Mark Lubin, Feb 2026)

8 個系統四種截然不同的 memory 定義：

| 系統 | 做法 | 存儲 | 時間模型 |
|---|---|---|---|
| Mem0 | LLM 提取事實 | Qdrant向量 + 可選圖 | 無 |
| Letta | Agent 自己管 notebook | PostgreSQL + 檔案 | 對話時間戳 |
| Cognee | 知識圖譜 pipeline | 關係+圖+向量 | 無 |
| Graphiti | 時序知識圖譜 | Neo4j | Bi-temporal（4時間欄位） |
| Hindsight | 生物記憶模擬 | PostgreSQL+pgvector | 因果鏈+時間傳播 |
| EverMemOS | 7種記憶類型 | MongoDB+ES+Milvus+Redis | Episode 邊界 |
| Tacnode | 資料庫基礎設施 | 自定義多模 DB | 原生 time travel |
| Hyperspell | 資料訪問層 | 托管搜索索引 | 無 |

**關鍵洞察**：整個空間缺乏三層 stack 的整合——
- 資料訪問層（Hyperspell：43 OAuth 源）
- 知識建構層（Graphiti/Cognee：實體提取、矛盾檢測）
- 資料基礎設施層（Tacnode：ACID transactions、time travel）

沒有一個產品同時具備這三層。這是確定的架構缺口。

**最重要的開放問題**：所有 8 個系統都把 memory 當作「事實檢索」——但人類記憶不是檢索，是錶征（representation）。事實袋 ≠ 記憶。Hindsight 的 observation type（跨經驗合成的模式）和 Letta 的 memory_rethink 是少數指向正確方向的架構直覺。

### 2. Sayou — FTS5 擊敗 Embeddings 的實證

**SAMB benchmark 結果**：
```
sayou   67.0%  (FTS5 + grep + file read)
Mem0    18.5%  (embeddings)
Zep     14.2%  (knowledge graph)
---
3.6x gap
```

**最大的差距在 decision reasoning**：68% vs 8%。Embedding 相似性檢索對 vibes 有效，但對需要精確段落和具體文件的任務完全失敗。

Architecture 本質：`workspace_write` 創建 Markdown 檔（YAML frontmatter + structured content），`workspace_read` 做為 agent 的 context。Agent 需要能 grep、讀章節、 follow references——這些是結構化 text 的原生能力，不是 embedding space 的能力。

**與 structure-before-content pattern 收斂**：這不是新發現，sayou 只是提供了最乾淨的實證數字。

### 3. Memento Memory — Bitemporal KG，MiniMax M2.7 ≈ Claude Sonnet 4.6

90.8% on LongMemEval（500 questions，GPT-4o judge）。關鍵設計：

**Bitemporal model**：每個事實追蹤兩種時間——
- `valid_time`：事實在現實中何時為真
- `transaction_time`：系統何時學習到這個事實

這個區分解決了「agent 何時知道 X」vs「X 何時為真」的問題——這是其他系統完全忽略的。

**對比數據**：
| Category | Markdown | Vector | Memento |
|---|---|---|---|
| Multi-session | 80.5% | 67.7% | 86.5% |
| Temporal reasoning | 82.0% | 66.9% | 89.5% |

**Model-agnostic 證明**：MiniMax M2.7（Together）在同一 knowledge graph 上達到 90.6%，與 Claude Sonnet 4.6 的 90.8% 基本持平。記憶層的結構化程度比 answer model 的實力更重要。

**對 drift 的直接意義**：
- Bitemporal model = explicit 矛盾檢測 + 信心衰減（confidence decay），直接解決 heartbeat_learning.py 的 staleness gap
- 矛盾檢測 = SSGM framework 的 `Pre-Consolidation Validation` 的具體實現
- Graph 結構 = 對 structure-before-content 的最強支持

## Hermes 啟發

1. **WS-035 drift penalty 設計方向確認**：bitemporal model + 信心衰減 + 矛盾檢測三層，需要 explicit mechanism，不能只靠 distillate 層的 soft penalty。Memento 的架構是迄今最完整的具體參考。

2. **FTS5 > embeddings 的實證**：sayou 的 3.6x gap 應該直接轉化為提案——Hermes vault 現有的 `/llms.txt` + grep 模式，可能是正確的架構方向，而不是加 embedding search。

3. **三層 stack 缺口**：Hyperspell（資料訪問）+ Tacnode（基礎設施）+ Graphiti（知識建構）的組合等於一個完整棧。沒有產品實現它，但這是确定的架構方向。Talos 如果要建立 memory 基礎設施，應該考慮這三層的整合。

## 未追蹤 Leads

- https://synix.dev/articles/agent-memory-systems/ — 8系統分析全文（已讀，見上方）
- https://github.com/pixell-global/sayou — FTS5 workspace（已讀）
- https://github.com/shane-farkas/memento-memory — Bitemporal KG（已讀）
- https://arxiv.org/abs/2604.04853 — MemMachine（上次 cycle 已讀）
- https://github.com/agentthreatbench/agentthreatbench — AgentThreatBench（vault 有）
- https://genai.owasp.org/resource/agent-memory-guard/ — OWASP Agent Memory Guard（vault 有）

## ✅ 本次探索完成

**延續自**: [[2026-05-31-OWASP-Agentic-AI-MemMachine-AgentThreatBench]]

**相關 vault 筆記**:
- [[2026-05-31-Exploration--OWASP-Agentic-AI---MemMachine-Follow-up]] — MemMachine 驗證
- [[2026-05-31-Exploration--Mnemonic-Sovereignty---arxiv-2604-16548v1]] — Mnemonic Sovereignty 源 paper
- [[2026-05-29-SSGM-Framework---Bounded-Drift-via-Governance-Middleware]] — SSGM framework
- [[2026-05-30-探索-Agent-Memory-Architecture---2026-State-of-the-Field]] — 架構測繪

