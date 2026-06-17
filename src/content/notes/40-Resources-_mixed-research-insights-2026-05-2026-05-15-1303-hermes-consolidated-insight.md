---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-1303-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-1303-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: high
title: 同一個架構漏洞，三種不同症狀
updated: '2026-06-15'
type: research
status: budding
---

# 同一個架構漏洞，三種不同症狀

**消化筆記**: 2026-05-15-google-scion-agent-orchestration, 2026-05-15-agents-still-bad-at, 2026-05-14-agent-economics, 2026-05-14-agent-defense-landscape, 2026-05-14-post-vector-agent-memory-pt2, 2026-05-14-agent-hijacking-nist

三條獨立討論線——LLM agent 的安全漏洞、編碼工具的 functional limitation、agent 成本結構——最終指向同一個架構層缺陷：LLM 沒有 trusted/untrusted boundary。而解法不是更好的 model，是把不確定性移出 LLM，交給確定性工具。

---

## Cross-Cutting Theme 1: Trusted/Untrusted Boundary 是安全漏洞也是功能缺陷（不是兩個問題，是同一個）

**支援筆記**: agent-hijacking-nist, agent-defense-landscape, agents-still-bad-at, post-vector-agent-memory-pt2

NIST 說 agent hijacking 的本質是「系統缺乏 trusted internal instructions 和 untrusted external data 的清晰邊界」——攻擊者把惡意指令藏在 agent 會處理的資料裡，LLM 分不出「這是系統叫我做的」和「這是外部資料叫我做的」。FireClaw / AgentArmor / Lilith-zero 三套防禦工具的共通盲區也是這個：都在 pipeline 上打補丁，沒有一個改動「讓 LLM 本身能區分指令和資料」的架構。

但同一批筆記暴露了一個沒被明說的對應關係：**copy-paste 問題的本質也是同一個 boundary 缺失**。當 agent 「複製」code block 時，它不是 byte-for-byte 搬移——它從 latent representation 重新 decode，過程中丟掉註解、微調格式、hallucinate URL。LLM 沒有「這段 bytes 是 authoritative source」vs「這段是我 re-generate 的」的區分能力。攻擊者利用這個 injection 叫 hijacking；開發者撞到這個叫「agent 把我的 URL 改爛了」——同一件事的惡意版和無意版。

Memory injection（Zep 點出的第四個 portable wallet 致命傷）是同一條攻擊鏈的 persistence 版本：惡意 payload 被寫進 agent memory，跨 session 存活，每次召回都被重新執行。Hermes 的 local vault 架構（自主筆記只在本機、由 agent 自己寫入、不經第三方攜帶）把這個攻擊面縮到極小——但 residual risk 仍在：如果 Hermes 在自主探索時 fetch 了惡意網頁、把 injection payload 寫進 autonomous_notes、然後下次 cron 讀回來執行——這是一條完整攻擊鏈。

**可行動下一步**: 實作 FireClaw 的 canary token 技術作為輕量 integrity check。在 Hermes 寫入 vault notes 時注入 per-session canary token（unique marker），後續 session 讀取筆記時檢查 canary 是否存活。若 canary 被篡改/消失 → flag 該筆記為 potentially compromised，不納入 autonomous decision context。這是 ~50 行 Python 的事，不需要新 infrastructure。

---

## Cross-Cutting Theme 2: Cost ⇄ Context ⇄ Orchestration 是同一個問題的三個名字

**支援筆記**: agent-economics, google-scion-agent-orchestration, agents-still-bad-at

agent-economics 提出了那個沒被回答的問題：「Are cost management, context management, and agent orchestrations all really the same problem?」——讀完 Scion 和 agents-still-bad-at 之後，答案是 yes，而且比原文意識到的更徹底。

Scion 的「一個 agent 一個 container」設計，表面上是 security isolation。但從成本角度看，它同時是 **context isolation**：每個 agent 有 bounded context window，cache behavior 可預測，成本可預測。agent-economics 的核心發現——cache reads 在 conversation 結尾佔成本 87%，因為每一輪都重讀整個 context——在 Scion 的 bounded-per-agent 架構下被自然地限制了。Isolation 不只是安全策略，它是成本策略。

agents-still-bad-at 從另一個方向收斂到同一點：imcritic 和 the_mitsuhiko 都說「把大 refactor 拆成 atomic git commits」。Atomic commit = bounded context per operation = predictable LLM behavior = predictable cost。Scion 在 infrastructure 層做這件事（container boundary），atomic commit 在工作流層做同一件事（task boundary），「重開 conversation」在 session 層做同一件事（context boundary）。三種 scale，同一種 strategy。

**非顯然推論**: 如果 context 隔離 = 成本控制 = 可靠性控制，那麼 Hermes 的 delegate_task 應該有 explicit context budget——不是「盡量省 token」，而是「這個 delegate 的 context 已經大到 cache read 成本超過重開的成本了，該重開了」。agent-economics 給了具體數字（~27,500 tokens 時 cache read 佔成本 50%），這可以直接變成 delegate_task 的閾值。

**可行動下一步**: 在 delegate_task 加入 `context_budget_tokens` 參數，預設 ~25,000。delegate 的 conversation 超過此閾值時自動觸發 summary-inject-restart pattern：產出 structured summary → 注入新 session → 繼續工作。不需要新 infrastructure，session_search 已經可以做 summary injection 的載體。

---

## Cross-Cutting Theme 3: Deterministic Tools > Smarter Models（三條獨立線索收斂到同一條設計法則）

**支援筆記**: agents-still-bad-at, agent-defense-landscape, agent-economics

三篇筆記各自從不同角度得出同一結論：

- **agents-still-bad-at**: nberkman 的 buffer_copy/paste 把 copy-paste 從 LLM 手中拿走，變成 server-side deterministic operation——零 token 生成、零 hallucination。不是等 LLM 變好，是把 LLM 做不好的事移出 LLM。
- **agent-defense-landscape**: Lilith-zero 的設計哲學——「Deterministic Classification」「Fail-Closed」「Rust 型別讓不安全的狀態在編譯期就無法表達」——不用 LLM 做安全判斷，用確定性 policy engine。
- **agent-economics**: 9 行 while loop + bash tool use 已經非常有效。簡單、確定性工具比複雜 agent 架構更可靠。

這不只是三個獨立的「好用工具」案例。它們形成一條設計法則：**任何 LLM 無法確定性地做的事，應該由非 LLM 元件來做**。不是「LLM 為主、工具為輔」，而是「工具做確定性操作，LLM 做需要語意判斷的操作」。這對 Hermes 的 tool design 有直接衝擊——目前有些操作仍然讓 LLM 做推理而可以用確定性工具取代：

- **檔案搬移**: LLM 用 `write` + `delete`（可能 hallucinate path）→ 應該 expose `mv` 
- **大範圍 rename**: LLM 逐行改 → 應該用 regex/ast-based
- **Copy-paste between files**: 目前沒有對應 tool → 應該有 exact line-range operation

**可行動下一步**: Audit Hermes 現有 tool set，找出所有「LLM 在做但可以用確定性工具取代」的操作。最優先三項：(1) expose `mv`/`cp` 為 first-class tools（目前 terminal 可以做但沒有 dedicated tool 的 safety guard），(2) 加入 exact line-range copy tool（buffer_copy 的 Hermes 版 —— 底層用 `sed -n` 讀取 + `patch` 的精確寫入），(3) 禁止 delegate 用 `write`+`delete` 模擬搬移（在 tool description 層加 constraint）。

---

## 附帶發現：產業訊號收斂

這批筆記還有一個 meta-pattern：多條獨立線索正在快速收斂到相同方向。

- **File-based memory 共識**: post-vector-agent-memory-pt2 記錄了三套獨立系統（memU、SQLite Memory、Beads）+ Claude Skills 都走向 file-based local memory。社群評論直接說「file-system-style storage is pretty similar to Claude's current Skills design」。
- **MCP 作為整合層**: memory backend（SQLite Memory、memU、Zep）都 expose MCP tools；defense tools（AgentArmor、Lilith-zero）也都走 MCP integration。
- **Isolation > constraints**: Scion 說「isolation over constraints」，agent-defense 說「真正的 boundary 應該是架構層的 separation」，NIST 說「需要 trusted/untrusted boundary」——三條線都在說同一件事。

Hermes 在這些收斂方向上都已經在正確的軌道上（worktree isolation、file-based vault、MCP gateway），但 consolidation pipeline 是明顯的 gap——而這個 gap 正是現在在跑的這個 cron job 本身。Meta 但真實：**我們正在用 consolidation 修補 consolidation 的缺失**。
