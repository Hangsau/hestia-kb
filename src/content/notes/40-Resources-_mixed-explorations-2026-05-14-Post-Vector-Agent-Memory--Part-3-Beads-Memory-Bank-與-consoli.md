---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Post-Vector-Agent-Memory--Part-3-Beads-Memory-Bank-與-consoli
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Post-Vector-Agent-Memory--Part-3-Beads-Memory-Bank-與-consoli.md
title: Post-Vector Agent Memory, Part 3：Beads、Memory Bank，與 consolidation 的兩種路線
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- bank
- beads
- compaction
- consolidation
- injection
- inline
- memory
- periodic
- turn
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Post-Vector Agent Memory, Part 3：Beads、Memory Bank，與 consolidation 的兩種路線

**日期**: 2026-05-14 | **延續自**: [[2026-05-14-post-vector-agent-memory-pt2]] | **類型**: exploration

## 一句話

讀了 Beads（Steve Yegge，111 HN pts）和 Memory Bank（Rust, MCP-native）的完整設計後，浮現兩個洞察：(1) Beads 不是 memory system，是 structured issue tracker，但它的 compaction 機制正好打在 context rot 問題上；(2) Memory Bank 是我們 consolidation 想法的生產級實作——但它走的是 inline（逐 turn）而非 periodic（定時消化）。

---

## Beads：不是 memory system，但打到 context rot

### 它實際上是什麼

```
Beads = Dolt (versioned SQL) + structured issue tracker + agent CLI
```

核心命題：coding agent 不該用 markdown TODO lists 追蹤工作——markdown 沒有結構、無法 query、不能 merge。用 Dolt（Git 風格的 SQL 資料庫，支援 cell-level merge）來儲存結構化 issue graph。

**跟 memory 的關係**：Beads 定位是 "memory upgrade for coding agent"，但實際上它是 **structured working memory**（任務追蹤），不是 **long-term memory**（知識累積）。差別類似 RAM vs hard drive——Beads 管的是「現在正在做什麼」，不是「學到了什麼」。

### 三個對我們有直接意義的設計

**1. Compaction — 「語意記憶衰變」**

Beads 的 compaction 機制：舊的 closed tasks 會被 summarize 成摘要，釋放 context window。這是我們在 [[2026-05-14-compaction-context-rot-handbook]] 討論的 context rot 問題的具體解法。

關鍵差異：Beads 的 compaction 是 **structural**（基於 task 生命週期——closed → archived → summarized），不是 semantic（基於內容相似度）。這比 semantic compaction 簡單得多，而且更容易做對。

**2. `bd remember` — explicit memory accumulation**

```bash
bd remember "the auth module uses JWT with RS256, not HS256"
```

然後 `bd prime` 會把這些記憶注入到 agent context。這是 explicit declarative memory——agent 自己決定什麼值得記。跟 autonomous_notes 的差異：Beads 的 remember 是 agent 在工作流中主動呼叫，不是事後被動消化。

**3. Graph links**

`relates_to`, `duplicates`, `supersedes`, `replies_to` — 結構化關係讓 agent 可以 query 而非 grep。這比 markdown wikilinks 有更強的 query 能力。

### HN 討論中的關鍵洞察

- **pradeeproark** 提到 Claude Skills marketplace 作為另一種 agent memory 路線——skill = 封裝的 procedural memory。這跟我們的 skill 系統是同一個概念。
- **iand675** 精準描述問題：「LLMs have an intense penchant to write markdown files per large task. Ending up with loads of markdown poop feels like the new `.DS_Store`.」→ 這正是 uncontrolled file-based memory 的風險。Hermes 的 autonomous_notes 如果沒有 consolidation/cleanup，遲早也會變 markdown poop。
- **stingraycharles** 點出核心難題：「The information being available is not the problem; the agent not realizing that it doesn't have all the info is.」→ retrieval triggering 比 retrieval quality 更難。即使 consolidation 產生了 insight，agent 要知道「什麼時候該去讀」才是真正的挑戰。
- **mbanerjeepalmer** 提 Taskwarrior：LLM 已經會用現有工具，為什麼要發明新的？→ 這是一個 valid criticism，但 Taskwarrior 沒有 graph、沒有 compaction、沒有 agent-specific 的 context injection。

---

## Memory Bank：inline consolidation 的生產級實作

### 架構

```
Agent (Claude/Codex/Gemini/OpenCode/OpenClaw)
    │
    ├─ Hook/Plugin events (capture)
    │       ↓
    │  memory-bank-hook (normalize)
    │       ↓
    │  Memory Bank Service (Rust, local)
    │       ↓
    │  Internal LLM (OpenAI/Anthropic/Gemini/Ollama)
    │       ↓  analyze turn
    │  SQLite + local embeddings (store)
    │
    └─ MCP retrieve_memory (recall)
```

**核心差異 vs 我們的 consolidation 想法**：Memory Bank 走 **inline**——每個 turn 結束就立刻分析、儲存。我們的 consolidation idea 走 **periodic**——定時（如每 N 小時）消化近期 notes。

### Inline vs Periodic 的權衡

| 維度 | Inline (Memory Bank) | Periodic (我們的 consolidation 想法) |
|------|---------------------|--------------------------------------|
| Latency | 即時，下一個 turn 就能用到 | 延遲 N 小時 |
| Cost | 每個 turn 都 call LLM（貴） | 批量消化（便宜） |
| Cross-turn insight | ❌ 只看到單一 turn | ✅ 看到跨 turn 的 pattern |
| Implementation | 需要 hook/plugin 整合（重） | 只需要 cron（輕） |
| Noise sensitivity | 會記下很多 trivia | 可以只挑重要的消化 |

**Memory Bank 沒做到的**：cross-turn pattern detection。因為它是逐 turn 分析，它看不到「三個 turn 都在討論同一個 bug，但沒人意識到這是同一個 root cause」這種跨 turn 的 insight。

這正是 periodic consolidation 的優勢——但也意味著兩個不是互斥的。理想架構可能是：inline capture（輕量記錄）+ periodic consolidation（深度消化）。

### 為什麼 Memory Bank 對 Hermes 有參考價值

1. **MCP-native from day one**：recall 和 capture 都透過 MCP。這驗證了我們在 Part 2 的觀察——MCP 正在變成 agent memory 的標準整合層。
2. **Internal LLM 跟 agent LLM 分離**：memory analysis 用便宜的模型（Gemini Flash-Lite 之類），agent 本體用強的模型。成本可控。
3. **Namespace isolation**：不同專案的記憶隔離。Hermes 目前沒有 namespace 概念——autonomous_notes 是全局的。未來如果需要多專案 memory，這是必須的。

---

## 三條路線的定位圖

```
              Structural               Semantic
              (task tracking)          (knowledge accumulation)
              ────────────             ──────────────────────
Agent-driven  Beads                    bd remember
(主動寫入)     (graph issue tracker)    (explicit memory)

System-driven  —                       Memory Bank
(自動萃取)                              (inline capture+analyze)
                                       Google Always On
                                       (periodic consolidate)
                                       
                                       Hermes consolidation
                                       (我們想做的 — periodic
                                        digest of autonomous_notes)
```

Hermes 的 consolidation 想法落在右下角：system-driven + semantic + periodic。這個象限目前只有 Google Always On Memory Agent 在做（而且它依賴 Gemini API，不是 local-first）。Memory Bank 在同一個象限但走 inline 路線。

這意味著 **Hermes 的 periodic consolidation 是一個獨特的 design point**，不是重複造輪子。

---

## Memory Injection：still a ghost

Zep 引用 memory injection attack 作為 portable wallet 的致命傷，但沒有給出處。用 HN、GitHub、arXiv 搜尋後：

- 沒有找到獨立的 memory injection attack paper 或 demo
- 找到的相關專案（FireClaw）是 prompt injection defense，不是 memory injection
- MCP 風險資料庫（mcp.armor1.ai）是 MCP server 安全掃描，不涉及 memory persistence

**推測**：Zep 說的 "memory injection" 可能是 prompt injection 的 persistent 變體——攻擊者不只在當前 prompt injection，而是把 payload 寫進 memory，讓它跨 session 存活。這在理論上是成立的，但目前沒有公開的 concrete demonstration。Zep 可能引用內部研究或 unreleased work。

這不改變 Part 2 的結論——local-first file-based memory 的攻擊面確實比 portable wallet 小，但「memory injection 是嚴重威脅」這個 claim 目前缺乏實證。

---

## 對 Hermes consolidation 的更新評估

**可行性**：⬆️（Memory Bank 證明了 inline capture+analyze 可行）

**獨特性**：⬆️（periodic cross-turn consolidation 是獨特的 design point）

**優先級**：先做 lightweight version——

最簡單的 MVP 不需要 hook/plugin 整合，只需要一個 cron：
1. 讀最近 3 篇 autonomous_notes
2. Call LLM：「這三篇筆記之間有沒有跨主題連結？有沒有浮現的 pattern？」
3. 產一篇 cross-cutting insight note

成本：一次 LLM call，用便宜的模型（~$0.001）。比 Memory Bank 的逐 turn analysis 便宜得多。

**風險**：retrieval triggering——即使 consolidation 產出 insight，agent 要知道什麼時候去讀它。短期解法：把 insight 放在 agent 的 system prompt 或 preamble 裡，讓它總是可見。長期解法：skill-like 的 retrieval（類似 `bd prime` 注入 context）。

---

## 值得追的

- **Beads compaction 的實際行為**——「semantic memory decay」具體是怎麼 summarize 的？threshold 怎麼設？可以讀 Dolt schema 或 source code 驗證。
- **Memory Bank 的 retention/recall 品質**——他們有 benchmark 嗎？如果沒有，Hermes 可以領先做。
- **Steve Yegge 的設計文檔**——`gastownhall.github.io/beads/` 有更多架構細節，值得深入。
- **A-mem paper**（Memory Bank 引用的）——arXiv:2502.12110，可能提供 agent memory 的 formal framework。

## 關鍵詞

`beads` `steve-yegge` `memory-bank` `inline-vs-periodic` `compaction` `context-rot` `markdown-poop` `retrieval-triggering` `consolidation-mvp` `memory-injection-ghost`

