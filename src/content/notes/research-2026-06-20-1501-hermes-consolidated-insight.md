---
_slug: research-2026-06-20-1501-hermes-consolidated-insight
_vault_path: research/2026-06-20-1501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-20'
confidence: high
title: 2026-06 記憶系統四論文收斂：三個非顯然的 cross-cutting 模式
type: research
status: seedling
updated: '2026-06-20'
---

# 2026-06 記憶系統四論文收斂：三個非顯然的 cross-cutting 模式

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇筆記都在解決 LLM agent 的 long-term memory 問題，但各自從不同切入點出發（H-MEM/RecMem 從架構、MemoryOS 從 OS 啟發、SAGE 從 graph feedback、Memory Governance 從企業部署）。把它們並排後浮現三個單篇看不到的模式。

## Cross-Cutting Theme 1: 「triggered, not eager」是 2026 記憶系統的新共識

**支援筆記**: hmem-recmem, memory-os, sage, memory-governance（全部 4 篇）

每一篇都在某個維度上反對「每件事都立刻做」的 eager 設計：

- **H-MEM**：user feedback 是 trigger，不是每個 turn 都 consolidation
- **RecMem**：consolidation 只在 recurrence count 達 θcount 時觸發（87% token 節省）
- **MemoryOS**：STM→MTM→LPM 三層用 FIFO 與 heat score 控管蒸發，**不是** all-into-LPM
- **SAGE**：writer 是 policy-based，決定「何時寫、如何寫」— 非被動接收
- **Governed Memory**：routing 分 fast mode（~850ms，無 LLM）vs full mode（~2-55s）— 預設是 cheap path

共同的底層假設：**eager design 浪費 token、膨脹 state、無 critical signal**。每篇都提出各自的觸發條件，但收斂到同一個原則——cost 必須由 signal 強度證成。

**可行動下一步**: 在 `consolidate_memory.py` 本身的 distillate routing 上引入「trigger threshold」。目前 consolidate 是定時掃描（每日），可改為：
1. 維護 lightweight hit counter（每個 distillate 被任何 retrieval query 命中次數）
2. 連續 N 天 hit count = 0 的 distillate 才進入 candidates
3. candidates 中只有 `last_modified_age > X` 且 `hit_count = 0` 才實際 consolidate
預期 token 節省可比照 RecMem 的 50–87% 區間。

## Cross-Cutting Theme 2: Schema/Structure > Raw Embedding — 四種「structure-enforced retrieval」是同一招的四種變體

**支援筆記**: hmem-recmem, memory-os, sage, memory-governance（4 篇）

單純 cosine similarity over flat embedding 是 2024–2025 的 baseline，每篇 2026 paper 都明確否定這個基底：

| 系統 | 用什麼「structure」取代純 embedding |
|------|-------------------------------------|
| H-MEM | Positional index encoding（discrete pointer, 四層 hierarchy） |
| MemoryOS | Segment + Page（OS-style 分段分頁，語意分群 + Jaccard keyword overlap） |
| SAGE | Entity-Relation-Triple graph + GFM propagation |
| Governed Memory | Typed schema-enforced properties + open-set atomic facts（dual model） |

注意每種 structure 都不是「額外加上去」的 metadata — 它們是 **retrieval 路徑本身**。H-MEM 的 index pointer 直接路由到 episode；MemoryOS 的 segment ID 決定 retrieve 哪個 page；SAGE 的 triple 是 query 的起點；Governed Memory 的 schema 是 fast-path routing 的 key。

**可行動下一步**: 盤點 `obsidian-vault/` 與 `~/.hermes/vault_fts5.db` 的 retrieval 是否仍以純 embedding similarity 為主。若是：
1. 在 vault frontmatter 強制加 `type:` 欄位（distillate / source / reference / insight）
2. consolidate_memory.py 的 retrieval 先用 `type` filter 縮範圍，再做 FTS5 BM25
3. 預期：FTS5 已是 ranking-based（BM25），加入 type filter 是 zero-cost 的 structure layer

## Cross-Cutting Theme 3: Reader→Writer 反饋閉環是「staleness detection」的唯一解

**支援筆記**: sage（最明確）, memory-os（implicit）, memory-governance（reflection-bounded）, hmem-recmem（weakest）

四篇都觸及「記憶何時該被標記 stale」的問題，但只有 SAGE 把 reader→writer 反饋做成 explicit loop。其他三篇是 implicit：

- **SAGE**：Reader 檢索失敗 → Writer 收到 signal → 改善寫入結構
- **MemoryOS**：Heat = `N_visit`（reader 行為）→ eviction（writer-side 動作）— 隱性反饋
- **Governed Memory**：Reflection-Bounded Retrieval — LLM judge evidence completeness → targeted follow-up queries（reader 內部的 self-correction，不是 writer）
- **H-MEM/RecMem**：user feedback 是最弱的反饋（passive observation，不是 active signal）

關鍵洞察：**staleness 不能只靠 time-based decay**。四篇中任何一篇用 pure time decay 的（如 RecMem 的 conscious→semantic 過渡無 time-based trigger）效果都不及有 reader signal 的。

這個 pattern 對 `heartbeat_learning.py` 的 drift penalty 設計是直接 actionable — 但各篇都各說各話，沒有共識的 signal schema。

**可行動下一步**: 設計 minimal viable reader→writer signal schema。在 `consolidate_memory.py` 加一個 `--feedback` 模式：
1. 每次 consolidation 掃描時記錄 `distillate_id → last_retrieval_hit_date`
2. 若 `now - last_hit > threshold`（預設 60 天），emit feedback event 到 stderr log
3. writer 端的下次 consolidation 看到 feedback event 後，優先重新評估該 distillate（重新蒸餾 or 標記 stale）
4. 不改既有 heartbeat_learning.py，先做 standalone prototype 驗證 signal 是否 actionable（30 天後回顧 hit rate）

---

## 信心標示

- **Theme 1（triggered > eager）**: high — 4 篇全部明確支持，無反例
- **Theme 2（structure > flat embedding）**: high — 4 篇全部明確反對 flat-only retrieval
- **Theme 3（reader→writer feedback）**: medium — SAGE 最強證據，其他三篇是 implicit pattern；推測成分存在但 actionable
