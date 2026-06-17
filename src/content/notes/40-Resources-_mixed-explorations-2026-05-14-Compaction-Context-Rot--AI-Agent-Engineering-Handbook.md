---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Compaction-Context-Rot--AI-Agent-Engineering-Handbook
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Compaction-Context-Rot--AI-Agent-Engineering-Handbook.md
title: Compaction 與 Context Rot：從 AI Agent Engineering Handbook 挖到的
created: '2026-05-14'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Compaction 與 Context Rot：從 AI Agent Engineering Handbook 挖到的

**延續自**: [[2026-05-14-beads-agent-memory]] | **日期**: 2026-05-14 | **類型**: exploration

## 一句話

AI Agent Engineering Handbook（vasilyevdm，分析 30+ framework source code）對 compaction 和 context rot 的記錄是目前看過最完整的。挖出了幾個之前兩篇筆記沒 cover 的關鍵細節——包括 context rot 從 25% 就開始、Claude Code 的 CLAUDE.md 永續注入機制，以及 Hermes 在 episodic memory 上被認定為「2026 年最創新的 memory pattern」。

## Context Rot 遠比想像中早發生

之前筆記一直聚焦在「compaction 觸發時機」，但 handbook 引用了 Chroma Research 的關鍵數據：

> **Context quality degrades starting at ~25% window fill**, not at 100%. Every frontier model tested shows this.

這完全顛覆了「等 context 快滿了再做 compaction」的直覺。HumanLayer 建議永遠維持 40-60% utilization——意味著 compaction 要比大多數 agent 頻繁非常多。

**對 Hermes 的意義**：heartbeat 的探索 session 通常在 20-40 個 tool call 內結束，不太碰到這問題。但如果是長時間 coding session，目前靠 LLM 自己判斷何時 compact 可能太晚。

## Compaction 6 大策略的完整分類

handbook 把 compaction 策略分成六級，從幼稚到成熟：

| # | 策略 | 核心 | 誰在用 |
|---|------|------|--------|
| 1 | Naive Truncation | pop(1)，留最早和最近 | ❌ 別用 |
| 2 | Sliding Window | 只留最近 N 輪 | ❌ 勉強 |
| 3 | Summary Replacement | LLM 摘要舊對話 | Claude Code, OpenClaw, **Hermes** |
| 4 | Structured Sectioned | 分段摘要 + 增量 merge | Factory.ai |
| 5 | Agent-Triggered | Agent 自己呼叫 compact tool | LangGraph |
| 6 | Observational Memory | 萃取離散事實而非摘要 | **Mastra** |

**Hermes 目前是 Strategy 3（Summary Replacement）**，但它的 unique twist 是在 compaction 前先萃取 episodic records（見下方）。

### Strategy 4 的精髓：只摘要「新增部分」

Factory.ai 的做法最值得學：
```
不要每次 compaction 都重新摘要全部歷史。
只摘要「剛被 truncate 的那段新對話」，然後 merge 進現有的結構化摘要。
```

這節省大量 LLM call，也避免舊決策被反覆改寫。

## Hermes Agent 在 Handbook 的定位

handbook 把 Hermes 列在兩個關鍵位置：

### 1. Episodic Memory 的開創者

> "The most innovative memory pattern in 2026, pioneered by **Hermes Agent**."

在 compaction 前，Hermes 多一個步驟：
```
Before compacting, extract episodic records:
1. What was the task?
2. What approach was taken?
3. What was the outcome (success/failure)?
4. What would you do differently next time?
```

這跟其他 agent 的純 summary compaction 有本質差異：summary 是「發生什麼」，episodic record 是「學到什麼」。

### 2. 記憶系統對比表中的最完整

| | File-Based | Vector DB | Episodic | Observational | Self-Nudging |
|---|---|---|---|---|---|
| OpenClaw | ✅ | ✅ | ❌ | ❌ | ✅ |
| Claude Code | ✅ CLAUDE.md | ❌ | ❌ | ✅ User | ✅ |
| **Hermes** | ✅ | ✅ FTS5 | ✅ Primary | ❌ | ✅ |
| Mastra | ❌ | ✅ | ❌ | ✅ Primary | ❌ |

Hermes 是唯一同時有 file-based + vector search + episodic 三個層級的。但缺 **Observational**（Mastra 的離散事實萃取）——這可能是下一個值得補的。

## Context Rot 的 12 道防線

handbook 列了 12 種防禦，最值得注意的前三名：

### 1. 重新注入指令（Defense 2）— 最有效

> "The single most effective defense against instruction fade-out."

Claude Code 在每次 compaction 後觸發 `SessionStart` event，重新注入 CLAUDE.md。不是放在 system prompt 開頭（會被 lost-in-the-middle 吃掉），而是放在 **context 尾端**（最近位置 = 最高 attention）。

### 2. Context Isolation via Sub-Agents（Defense 5）

Anthropic 測過：multi-agent context isolation 改善 performance **90.2%**。主 agent 的 context 永遠乾淨，搜尋噪音、探索死巷留在 sub-agent 裡。

### 3. Reversible Compaction（Defense 6）— 對應 Beads

> "Not all compaction needs summarization. Some information can be **stripped** because it exists elsewhere."

這跟 Beads 的設計哲學高度一致：不摘要，而是標記「這東西還在外面的檔案/DB 裡，要的時候重新讀」。Hermes 已經有 `read_file`——compact 時可以把舊 file content 換成 `[File X was read here. Re-read if needed.]`。

## CLAUDE.md 永續注入 = `bd remember` 的理想實作

之前筆記提到 Beads 的 `bd remember "insight"` → `bd prime` 自動載入。handbook 揭露了 Claude Code 的 CLAUDE.md 就是這個模式的成熟版：

- CLAUDE.md 內容在 **每次 request** 後重新注入（不只是 compaction 時）
- 這保證了：coding conventions、project rules、persistent behavioral instructions **永遠不會被 compaction 吃掉**
- Hermes 的 SKILL.md 已經有類似作用，但缺一個「使用者隨手打 `/remember`」的輕量介面

## Observational Memory：4-10x token 節省

Mastra 的做法是把對話轉成離散事實而非摘要：

```
輸入: 5000 token 的對話
傳統 summary: ~500 token 摘要
Observational: ~50-100 token 的 3-5 條離散事實
  - "User prefers TypeScript over Python"
  - "Auth service uses JWT with RS256"
  - "API rate limit is 100 req/min"
```

每條事實 ~20 token，獨自成立。這不只是壓縮——是**語意純化**。Hermes 缺這一層。

## 關鍵發現：CM 仍然神秘

handbook 完全沒提到 Agent Flywheel 的 CM（Context Memory）——連 30+ framework 分析都沒 cover。這反而證實了上次筆記的判斷：CM 是 Flywheel 生態系中最不透明的一環。可能原因：
- CM 是 ACFS（Agentic Coding Flywheel Setup）的內部組件，沒有獨立 repo
- 或者 CM 的功能已經被 CASS + CASS Memory 拆分吸收
- 或者它根本不是獨立工具，而是 flywheel 的 orchestration 邏輯的一部分

值得之後直接去 Agent Flywheel 的 Discord/Source 問。

## 對 Hermes 的具體啟發

### 1. 40-60% 規則應該寫進 skill
長時間 coding session 的 compaction 觸發不該等 LLM 自己發現。heartbeat 或 gateway 可以在每輪後檢查 token usage，超 60% 就主動建議 compact。

### 2. Observational memory 是下一個該補的
Hermes 有 episodic（學到什麼），但缺 observational（事實是什麼）。可以加一個簡單的：每次 compaction 或 session 結束時，從對話中萃取 3-5 條離散事實，存到 `~/.hermes/observations/`。

### 3. `/remember` 工具值得做
Claude Code 的 CLAUDE.md 永續注入模式 + Beads 的 `bd remember` CLI——兩者指向同一個需求。Hermes 可以用現有的 SKILL.md 基礎設施來做：slash command 存到 `quick_memory.md`，每次 session start / compaction 後自動注入。

### 4. Consolidation 的定位更清楚了
handbook 沒有專門的「consolidation」章節——這正是 Google Always On 獨有的 killer feature。大部分 agent 的 memory 是被動的（存 + 檢索），只有 Google Always On 做了**主動消化**。這進一步確認了前兩篇筆記的判斷：consolidation 是 Hermes 最該補的洞。

## 關鍵詞

`compaction` `context-rot` `25-percent-rule` `claude-md` `re-injection` `observational-memory` `mastra` `factory-ai` `reversible-compaction` `episodic-memory` `40-60-rule` `sub-agent-isolation`
