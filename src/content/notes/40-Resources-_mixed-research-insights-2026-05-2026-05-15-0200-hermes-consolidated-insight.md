---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-0200-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-0200-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: high
title: Trust Boundary、Inline-vs-Periodic、與 Isolation 的三條收斂線
updated: '2026-06-15'
type: research
status: budding
---

# Trust Boundary、Inline-vs-Periodic、與 Isolation 的三條收斂線

**消化筆記**: 2026-05-14-agent-hijacking-nist, 2026-05-14-context-gateway-hn, 2026-05-14-scion-orchestration-skeptic, 2026-05-14-post-vector-agent-memory-pt3, 2026-05-13-agent-orchestrator-patterns, 2026-05-13-mcp-testing-manufact

六篇筆記看似各講各的——NIST 的 agent hijacking、context compression middleware、multi-agent orchestration 辯論、memory 系統比較、CI feedback loop、MCP testing——但有三條線把它們穿在一起，而且每條線都指向 Hermes 還沒做的事。

---

## Cross-Cutting Theme 1: Trust Boundary 問題是跨系統的通病，不是 hijacking 專屬

**支援筆記**: agent-hijacking-nist, context-gateway-hn, post-vector-agent-memory-pt3
**信心**: high（3 篇獨立來源在不同場景下指出同一結構性缺陷）

NIST 對 agent hijacking 的核心診斷是「缺乏 trusted internal instructions 和 untrusted external data 的邊界」。guard402 在 Context Gateway 討論中提出完全相同的問題，只是發生在 compaction 層：如果 context 裡有 adversarial input（`display:none`、zero-width Unicode），壓縮前不區分 trusted/untrusted = 把毒藥跟指令一起濃縮。Memory Bank / Zep 那邊的 memory injection 威脅是同一件事的第三種變體——攻擊者不只在當下 injection，而是把 payload 寫進 persistent memory 跨 session 存活。

三篇講的是同一件事的三個 attack surface：**prompt 層**（hijacking）、**compaction 層**（adversarial input 被壓進 summary）、**memory 層**（persistent injection）。但目前的防禦思路是各自為政——NIST 講 evaluation、guard402 講掃描後再壓縮、Zep 講 local-only vault。沒有人在做統一的 trust boundary 架構。

本質問題：LLM agent 的 input stream 把 system prompt、tool output、外部網頁、使用者上傳、memory recall 全部倒進同一個 context array，沒有 origin tag、沒有 trust label、沒有 sanitization boundary。攻擊者只需要控制其中一個來源。

**可行動下一步**: 在 Hermes 的 compaction skill 加入 trust boundary——compaction 前對 context segment 標 origin（system / tool / external / memory），external 來源不壓進 summary，只保留 metadata（URL + timestamp）。這不需要等整個 LLM agent 生態系解決架構問題，一行 origin tag 就能先堵 compaction 層的洞。具體改法：在 `compaction` skill 的 prompt 裡加一條「以下 segment 標記為 `[external]` 的內容不納入 summary，只記錄來源與時間」。

---

## Cross-Cutting Theme 2: Inline vs Periodic 的張力是 agent 架構的普遍 tradeoff，不是 memory 專屬

**支援筆記**: context-gateway-hn, post-vector-agent-memory-pt3, agent-orchestrator-patterns
**信心**: high（3 篇筆記在三個不同子領域觀察到相同張力）

同樣的 pattern 出現在三個完全不重疊的領域：

| 領域 | Inline 方案 | Periodic 方案 |
|------|-----------|-------------|
| Context 管理 | Context Gateway（背景 pre-compute + 觸發即換） | Hermes compaction（threshold 觸發後 inline call LLM） |
| Memory 系統 | Memory Bank（逐 turn 分析儲存） | Hermes consolidation（定時批量消化） |
| 任務修正 | Agent Orchestrator（CI fail → 立刻修 → 重推） | 人類 code review（PR 後定期檢查） |

三組的 tradeoff 結構完全一樣：inline 快但貴、看不到跨事件模式；periodic 慢但便宜、能看到全局 pattern。而且**沒有任何一組是 pure inline 或 pure periodic**——Context Gateway 的背景 pre-compute 其實是 periodic 時鐘驅動的 inline 替換；Memory Bank 作者自己也說未來要加 cross-turn analysis；Agent Orchestrator 的 CI loop 是 inline，但 human review 是 periodic。

這指向一個通用架構原則：**dual-track processing**——thin inline path（輕量記錄、快速反應）+ fat periodic path（深度消化、跨事件洞察）。不是二選一。

**可行動下一步**: Hermes consolidation 的 MVP 不要跟 Memory Bank 競爭 inline capture（那是另闢戰場），直接在 periodic path 上加一個 thin inline layer——idle 時每隔 N 分鐘掃一次 autonomous_notes 目錄，對新筆記做 lightweight triage（只分類、不深度消化），深度 consolidation 維持 periodic。具體實作：寫一個 `consolidation-triage` skill，只做兩件事：(1) 判斷這篇筆記屬於哪個 domain，(2) 標記是否有跨筆記連結潛力（有 → 留給下次 periodic consolidation 處理）。這樣既不用改 hook/plugin 整合（重），又能部分補償 periodic 的 latency 劣勢。

---

## Cross-Cutting Theme 3: Container + Worktree Isolation 正在收斂為 subagent sandbox 的標準答案

**支援筆記**: scion-orchestration-skeptic, agent-orchestrator-patterns
**信心**: medium（2 篇，但來自 Google 和獨立 OSS 專案，方向一致）

Google Scion 和 Agent Orchestrator 獨立做出了幾乎相同的設計選擇：每個 subagent 有自己的 container、自己的 git worktree、自己的 credentials。Scion 還加了 network policy。兩者都沒有在 agent 之間做複雜的協調邏輯——Scion 的「less is more」只給 messaging + shared workspace，Agent Orchestrator 的 subagent 之間根本不通訊，只透過 PR/CI 這個外部 feedback loop 間接互動。

這跟 Freeman 的「orchestration skepticism」不矛盾，反而是同一個結論的不同表述：**isolation 值得做，orchestration logic 不值得做**。把 agent 關好，讓它們各自做事，feedback 來自外部（CI、git、human review），不要試圖在 agent 之間編排複雜的對話/協商/投票流程。

Hermes 目前的 subagent 共用同一個 checkout，沒有 isolation。對 sequential task 沒問題，但如果要跑 kanban-worker 模式（多個 subagent 平行處理不同任務），collision risk 是真實的。而且沒隔離意味著一個 subagent 的 prompt injection / 幻覺寫入可以直接汙染另一個 subagent 的工作目錄。

**可行動下一步**: 不建議現在就做 full container isolation（太重，Scion 自己都說有 rough edges），但 git worktree isolation 是輕量的第一步。在 `subagent-driven-development` skill 裡加一個 `--isolate` flag：開 flag 時，用 `git worktree add` 建立獨立 worktree，subagent 在裡面作業，完成後 `git worktree remove`。這跟 Agent Orchestrator 的 Workspace 插件是同一個模式，但 Hermes 不需要 TypeScript plugin 層——一行 shell 就夠。

---

## 未消化的殘餘

有一條線還不值得拉成 theme，但值得標記：

**manufact 的 MCP testing 跟 NIST 的 adaptive evaluation 共享同一個前提**——行為會因環境而異（NIST：舊攻擊打新模型無效；manufact：同一模型在 API vs ChatGPT 行為不同）。兩者都沒給出解法框架，但方向一致：testing = 持續的、多環境的、對抗性的，不是一次性 compliance check。如果未來要幫 Hermes 設計 skill evaluation pipeline，這兩篇會是起點。
