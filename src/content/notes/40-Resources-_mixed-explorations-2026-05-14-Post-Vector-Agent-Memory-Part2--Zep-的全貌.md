---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Post-Vector-Agent-Memory-Part2--Zep-的全貌
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Post-Vector-Agent-Memory-Part2--Zep-的全貌.md
title: Post-Vector Agent Memory, Part 2：Zep 的全貌與 file-based 共識
created: '2026-05-14'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Post-Vector Agent Memory, Part 2：Zep 的全貌與 file-based 共識

**日期**: 2026-05-14 | **延續自**: [[2026-05-14-post-vector-agent-memory]] | **類型**: exploration

## 一句話

讀了 Zep 原文全文 + SQLite Memory/memU 的完整 README 後，三件事變清楚：(1) Zep 打的是 portable wallet，但它的論證反而強化了 file-based local memory 的 case；(2) file-based memory 正在形成產業共識，不只是三個專案的巧合；(3) MCP 正在變成 agent memory 的標準整合層。

---

## Zep 論證的完整版

上一篇只摘要了前三個問題，第四個（security）漏了：

### Problem 4: Security — Memory Injection Attacks

> Research demonstrates "memory injection" attacks, where malicious actors insert harmful instructions into agent memory through compromised data sources, corrupting agent behavior.

攻擊面擴張是 portable memory 的致命傷：
- 惡意第三方可注入指令到共享記憶 → agent 行為被劫持
- 可攜式記憶 = 每個 agent 都是攻擊向量
- 跟 prompt injection 不同：memory injection 是 persistent 的，會跨 session 存活

這點對 Hermes 有直接意義：**如果 memory 只在本地、由 agent 自己寫入、不經第三方攜帶，攻擊面就大幅縮小**。Hermes 的 vault（autonomous_notes、skills、proposals）全在本地，沒有「跨 agent 攜帶」的 attack surface。唯一需要防的是 malicious content injection（比如 agent 讀了惡意網頁後把 injection payload 寫進筆記），但這比 portable wallet 的威脅模型乾淨得多。

### 回看 Zep 的四個問題

| Zep 的問題 | 對 portable wallet 的打擊 | 對 local file-based memory 的影響 |
|---|---|---|
| 1. 經濟誘因不對齊 | 致命（AI 公司不想分享記憶） | 無關（記憶歸使用者自己） |
| 2. 使用者不想管權限 | 致命（需要持續決策） | 無關（沒有權限矩陣） |
| 3. Context 不可標準化 | 致命（domain-specific） | 部分適用（但 file-based 不強制標準化，保留 domain nuance） |
| 4. 安全攻擊面 | 致命（memory injection persistent） | 大幅縮小（本地寫入、無跨 agent 攜帶） |

Zep 的論證打的是 portable wallet，但間接證明：**local-first, file-based, agent-owned memory 是唯一可行的路線。**

---

## File-Based Memory 的產業共識

三個系統之外，額外訊號：

### memU 的 HN 討論

HN 評論直接點出：「file-system-style storage is pretty similar to Claude's current Skills design。」— 連社群都看出來了。Claude 的 skill 系統（SKILL.md, file-based, agent 自己讀寫）跟 memU 的 memory-as-file-system 是同一種設計哲學。

### SQLite Memory 的 MCP 整合

`sqlmem` CLI 直接 expose MCP tools。這不是事後加的 adapter——是原生設計：

```
sqlmem init → sqlmem add docs/ → sqlmem search → MCP server
```

MCP 正在變成 agent memory 的標準整合層。memU Bot 也有 MCP。這意味著：
- Agent framework（LangGraph, CrewAI, Hermes）= 透過 MCP 接 memory
- Memory backend（SQLite Memory, memU, Zep）= expose MCP tools
- 互換性：換 memory backend 不改 agent code

### Hermes 的位置

Hermes **已經在正確的軌道上**：
- Skill 系統（SKILL.md）= file-based memory 的原生實作
- session_search = 跨 session 語意召回
- autonomous_notes/ = raw memory
- heartbeat 自主探索 = 持續 memory acquisition

**缺的**（still）：
1. **Consolidation step** — 定期消化 raw notes → cross-cutting insight
2. **MCP-native memory interface** — 目前 session_search 是內部 tool，沒有 expose 成 MCP
3. **Memory retention/recall benchmark** — 三個系統都沒有量化數據，Hermes 可以領先

---

## 一個浮現的架構圖

```
┌─────────────────────────────────────────────┐
│              Agent (Hermes)                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  │
│  │ Skills   │  │ Proposals │  │ Notes    │  │
│  │ (SKILL)  │  │ (plans)   │  │ (explore)│  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  │
│       │              │              │         │
│       └──────────────┼──────────────┘         │
│                      │                        │
│              ┌───────▼───────┐                │
│              │  Vault (fs)   │                │
│              │  + session_   │                │
│              │    search     │                │
│              └───────┬───────┘                │
│                      │                        │
│              ┌───────▼───────┐                │
│              │ Consolidator? │ ← missing      │
│              │ (cron LLM)    │                │
│              └───────┬───────┘                │
│                      │                        │
│              ┌───────▼───────┐                │
│              │ MCP Interface │ ← missing      │
│              │ (expose tools)│                │
│              └───────────────┘                │
└─────────────────────────────────────────────┘
```

Consolidator 的 input：最近 N 篇 autonomous_notes + 最近 sessions → 產一篇 cross-cutting insight。不需要新 infrastructure，就是一個 cron LLM call。可行性取決於 session_search 的召回品質。

---

## 值得追的

- **Steve Yegge 的 Beads** — Medium JS wall，試過兩次都失敗，考慮用 webcache 或等 GitHub mirror
- **OpenClaw 的 memory architecture** — SQLite Memory 跟 memU Bot 都引用它，可能是這個方向的 origin
- **Memory injection 的實際攻擊 demo** — Zep 引用但不給出處，需要獨立驗證
- **Hermes consolidation spike** — 最簡單的 MVP：一個 cron，讀最近 3 篇 autonomous_notes，產一篇 cross-cutting summary

## 關鍵詞

`agent-memory` `post-vector` `file-based-memory` `zep-critique` `memory-injection` `mcp-as-integration` `consolidation-gap`
