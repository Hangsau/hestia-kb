---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Beads--Agent-Memory-Flywheel-實作層收斂
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Beads--Agent-Memory-Flywheel-實作層收斂.md
title: Beads & Agent Memory Flywheel：實作層的收斂
created: '2026-05-14'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Beads & Agent Memory Flywheel：實作層的收斂

**延續自**: [[2026-05-14-post-vector-agent-memory]] | **日期**: 2026-05-14 | **類型**: exploration

## 一句話

Steve Yegge 的 Beads 把「file-based agent memory」往前推了一步：不是存 Markdown，是存**版本控制資料庫**。而 Jeffrey Emanuel 的 Agent Flywheel 生態系證明：memory 工具之間必須互相強化，才有飛輪效應。

## Beads：不只是 issue tracker，是 agent memory system

### 原始版 (bd, Steve Yegge, Go)

**架構選擇**：Dolt（版本控制 SQL，cell-level merge，原生 branching）

關鍵設計：
- **`bd remember "insight"`** — agent 隨手存記憶，`bd prime` 自動注入 context window
- **Compaction（記憶衰減）** — 舊 closed task 被語意摘要，釋放 context window
- **Hierarchical IDs** — `bd-a3f8` → `bd-a3f8.1` → `bd-a3f8.1.1`（史詩級任務分解）
- **Graph links** — `relates_to`, `duplicates`, `supersedes`, `replies_to`（不只是 dependency，是 knowledge graph）
- **Messaging** — message issue type with threading, ephemeral lifecycle

**關鍵洞察**：Beads 是「給 agent 的 external memory」，不是「給人類的 project management」。`bd prime` 就是 agent 的 working memory loader。

### Rust port (br, Jeffrey Emanuel)

凍結在「classic」SQLite + JSONL 架構。為什麼 fork？
- Yegge 正在把 beads 推向 GasTown（更激進的架構）
- Emanuel 的 Agent Flywheel 工具鏈依賴 classic 架構
- 與其要求上游維護 legacy mode，不如自己 fork

**差異**：br 更務實——SQLite 而非 Dolt、JSONL export 給 git、完全 non-invasive（從不動 git）。

## Agent Flywheel：memory 工具的網路效應

Emanuel 圍繞 beads 建了 29 個工具的生態系。跟 agent memory 直接相關的核心：

| 工具 | 功能 | Hermes 對應 |
|------|------|------------|
| **CASS** | 跨所有 agent session 搜尋（11 種 agent 格式） | `session_search` |
| **CM** | 跨 session 共享 context memory | ❌ 沒有 |
| **BR** | Local-first issue tracking + dependency graph | `proposals/` 部分 |
| **BV** | Graph theory (PageRank, critical path) 分析任務瓶頸 | ❌ 沒有 |
| **Agent Mail** | 多 agent 協調層（file reservation, threaded messaging） | ❌ 沒有 |

**飛輪邏輯**：
```
Sessions → CASS（可搜尋歷史）
         → CM（擷取解決方案為可重用記憶）
         → BR（記憶轉成 structured task）
         → BV（分析瓶頸，決定做什麼）
         → Agent Mail（多 agent 不撞車）
         → 產生更多 sessions → loop
```

每次 iteration 都讓下一個更快。

## Modulus：跨 repo agent memory 的商業化版本

[Modulus](https://modulus.so)（桌面 app，2026 年初）實現了類似的願景：
- **Shared memory**：agent 自動知道所有 repo 的 API schema、dependencies、recent changes
- **Parallel agents + git worktree isolation**（同 Hermes 的 `worktree-subagent-isolation` skill）
- **Cross-repo context**：不必複製貼上 README

Modulus 證明了這條路線有商業需求——不只是開源實驗。

## 收斂的設計模式

把三個系統（Beads、Agent Flywheel、Modulus）跟 Hermes 對照：

| 模式 | Beads/ Flywheel | Modulus | Hermes |
|------|:--:|:--:|:--:|
| File-based storage | ✅ Dolt/SQLite | ✅ (未公開) | ✅ Markdown |
| Session search | ✅ CASS | 部分 | ✅ session_search |
| Cross-session context | ✅ CM | ✅ | ❌ |
| Task dependency graph | ✅ | ❌ | ❌ (proposals 是 flat) |
| Compaction / memory decay | ✅ | ❌ | ❌ |
| Multi-agent coordination | ✅ Agent Mail | ✅ | ⚠️ worktree 隔離（無 coordination） |
| Git worktree isolation | ❌ | ✅ | ✅ |
| Cross-repo context | ❌ | ✅ | ❌ |

## 對 Hermes 的啟發

### 1. Consolidation 是最該做的下一步（再次確認）

Beads 的 compaction、CM 的 cross-session context、上次筆記的 ConsolidateAgent——三個獨立來源指向同一個洞：**Hermes 產生大量筆記但從不消化它們**。

具體可以做的：一個 cron job，每 N 小時讀最近 5 篇 `autonomous_notes/` + 最近 sessions → 產一篇 cross-cutting insight。用現有的 `session_search` + `autonomous_notes/` 就能做，不需要新基礎設施。

### 2. `bd remember` 是 light-weight 的好模式

不是完整的 memory system，只是一個 CLI：agent 隨手打 `remember "API 用 v2 endpoint"`，下次 `prime` 自動載入。Hermes 可以在 heartbeat 或 slash command 加 `/remember`——存到 `~/.hermes/quick_memory.md`，每次 heartbeat tick 時載入前 500 tokens。

### 3. 飛輪效應已經在發生

Hermes 的 `session_search` + `autonomous_notes` + `proposals/` + `skills/` 已經構成雛形飛輪。但缺少兩個關鍵齒輪：
- **消化層**（consolidation）——把 raw notes 轉成 structured insight
- **記憶注入層**（prime）——自動把相關 insight 載入 agent context

### 4. Git worktree 已是共識

Modulus 做了、ComposioHQ Agent Orchestrator 做了、我們也做了。這模式已經從「該不該做」變成「預設就該有」。

## 值得追的

- Beads 的 **compaction 演算法細節**——是怎麼決定哪些 task 可以 summarize？用 age + status + importance score？
- **CM (Context Memory)** 的具體實作——Agent Flywheel 生態系中最神秘的工具，文檔很少
- Hermes consolidation step 的 **prototype**——寫一個簡單的 cron script 試跑一次，看產出品質

## 關鍵詞

`beads` `agent-flywheel` `context-memory` `compaction` `memory-decay` `dolt` `cross-repo-context` `modulus` `bd-remember` `consolidation`
