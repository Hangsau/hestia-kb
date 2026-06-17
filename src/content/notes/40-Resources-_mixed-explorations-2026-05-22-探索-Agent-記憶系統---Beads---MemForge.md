---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-Agent-記憶系統---Beads---MemForge
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-Agent-記憶系統---Beads---MemForge.md
title: 探索：Agent 記憶系統 — Beads × MemForge
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- beads
- github
- hermes
- https
- llm
- memforge
- memory
- revision
- sleep
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：Agent 記憶系統 — Beads × MemForge

**日期**: 2026-05-22 | **來源**: HN Algolia `agent memory system` 搜尋

## Per-Source Insights

### Beads (Steve Yegge)

**URL**: https://github.com/gastownhall/beads | **HN**: 19 pts

Steve Yegge 的專案。底層用 [Dolt](https://github.com/dolthub/dolt)（版本控制 SQL 資料庫）。

**不是傳統「記憶系統」**——更像結構化 issue tracker，帶 agent 感知：

- **Graph-based issue tracking**：hash-based ID（`bd-a1b2`）杜絕 merge conflict，支援 hierarchical IDs（Epic→Task→Sub-task）
- **依賴追蹤**：`bd dep add <child> <parent>` 建模任務之間的 blocks/related/parent-child 關係
- **記憶衰退（Compaction）**：長期累積的 closed tasks 會被 semantic 壓縮，節省 context window
- **零衝突 ID**：multi-agent/multi-branch 協作時不會打架
- **跨平台**：macOS/Linux/Windows/FreeBSD，CLI 安裝（`curl | bash`），不需 clone repo
- **Sleep/Compaction 非 LLM 驅動**：是 semantic compression（根據描述是演算法壓縮），不像 MemForge 的 sleep cycle 會呼叫 LLM 重寫記憶

**對 Hermes 的啟發**：
- Dolt 的 cell-level merge + branching 非常適合 multi-agent write queue（每個 agent 的規劃分支不會互相覆蓋）
- Hash-based ID 解決 zero-conflict 問題——可用於 `hermes-multi-agent-write-queue-wikiworker` 提案的協作問題
- 純 CLI 工具，無 server 依賴——可在 Hermes 環境直接試用

**限制**：不是「會變好的記憶」——Beads 的 compaction 是 forgetful，不是 self-improving。拿來當 long-horizon task tracker 比當 memory system 更準確。

---

### MemForge

**URL**: https://github.com/salishforge/memforge | **Benchmark**: LongMemEval R@5 = 93.2%

三層記憶架構（hot → warm → cold）+ neuroscience-inspired sleep cycle。

**核心創新——Sleep Cycle**：
- Phase 0-6：scoring → triage → conflict resolution → LLM revision → graph maintenance → temporal chains → reflection
- Phase 5.5：Schema detection——重複發生的時間 pattern 會被 crystallize 成 `entity_type='schema'`
- Phase 5b：Meta-reflection——二階反思，萃取出持久原則（principles）
- **Token budget 控制**：每次 sleep 有上限，不會爆預算
- **High-surprise 優先**：記憶被取出後若造成 high surprise，會被優先 revision（prioritized experience replay）

**三層搜尋**：
- Keyword：PostgreSQL FTS + trigram
- Semantic：pgvector HNSW（halfvec float16，2x compression）
- Hybrid：asymmetric reciprocal rank fusion（semantic 權重 1.5×）+ keyword overlap boost + temporal proximity scoring

**架構特色**：
- 單一 PostgreSQL 搞定一切（無 Neo4j/Pinecone）
- Local in-process embedding（`@huggingface/transformers`，CPU ~137/sec，零外部依賴）
- Memory revision = LLM 主動重寫低信心記憶（augment/correct/merge/compress）
- Outcome feedback loop：取出記憶 → 用了 → outcome 好/不好 → confidence 調整
- Confidence graduation：高取出率 + 高回饋 → 記憶自動強化

**對 Hermes 的啟發**：
- Sleep cycle 的 token budget 機制可直接移植到 heartbeat 的 idle consolidation
- Meta-reflection 概念對應 `heartbeat_learning.py` 的 pattern extraction——但 MemForge 是 actual memory revision，不只是 pattern log
- PostgreSQL-only 降低部署複雜度（Hermes 已有 PostgreSQL infrastructure）

**限制**：
- Sleep cycle 需外部觸發（無內建 scheduler）——MemForge 故意不做，讓 agent framework 自己決定何時 call
- 沒有內建的 prompt injection 防禦（和 Beads 一樣）

---

## 跨文章 Synthesis

**兩種 agent memory system 路線**：

| | Beads | MemForge |
|---|---|---|
| 核心抽象 | Issue graph（任務追蹤） | Memory tier（儲存架構） |
| 成長機制 | Compaction（壓縮） | Sleep + LLM revision（主動改善） |
| 底層 | Dolt（版本控制 SQL） | PostgreSQL + pgvector |
| LLM 角色 | 無 | 重寫記憶、反思、gap analysis |
| 適用場景 | Long-horizon coding tasks | 長期互動、偏好學習、知識累积 |
| 對 Hermes 的價值 | Multi-agent write queue ID 設計 | Idle memory consolidation 機制 |

**共同缺口**：兩者都沒有 prompt injection 防禦。Beads 的 doc 提到「prompt injection boundaries」（MemForge 的 THREAT_MODEL），但這是輸出層的過濾，不是輸入層的 sanitization——從 untrusted source fetch 回來的內容如何安全地寫入 memory store，兩個系統都沒有明確處理。

## Hermes 啟示

1. **Sleep cycle + token budget** 可移植到 `heartbeat_learning.py`：每 N 小時跑一次 idle consolidation，限制 LLM 呼叫 token 上限
2. **Dolt-style hash ID** 解決 multi-agent write queue 的 conflict 問題
3. **Memory revision** 概念：用 LLM 主動重寫低信心記憶，而非只 log patterns（`heartbeat_learning.py` 目前只萃取 pattern，不 revision）
4. **三層 tier**（hot/warm/cold）對應 Hermes 的：熱=當前 session context、溫=PROPOSALS.md / session archive、冷=proposals-archive/ / vault

## 未追蹤 Leads

- https://github.com/steveyegge/beads（原始 repo，Hacker News discussion 45566865）
- https://github.com/salishforge/memforge（MemForge GitHub，含完整 spec/architecture docs）
- https://benchmarks/RESULTS.md（LongMemEval 詳細 methodology）
- https://primitivesai.substack.com/p/memory-primitives-the-infrastructure（Memory Primitives: Why Most Agent Memory Systems Are Incomplete）

## ✅ 本次探索完成
