---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-16-0701-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-16-0701-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- agent-architecture
source: multi
created: '2026-05-16'
confidence: high
title: 合約邊界與狀態生命週期：從兩條探索線收斂出的 agent 設計原則
updated: '2026-06-15'
type: research
status: budding
---

# 合約邊界與狀態生命週期：從兩條探索線收斂出的 agent 設計原則

**消化筆記**: 2026-05-16-prompt-injection-patterns-agent-graph, 2026-05-16-coding-agents-browser-otel

兩篇筆記分別從安全面和工具鏈面探索 agent 設計，各自都提到了「標準化契約」與「不確定性消除」，但合在一起才顯出它們其實是同一條原則在兩個層次的投影：**把 agent 架構中每一條邊界都做成 explicit contract，並給狀態一個明確的生命週期**。

## Cross-Cutting Theme 1: 合約邊界是 agent 架構的統一語言

**支援筆記**: prompt-injection-patterns-agent-graph, coding-agents-browser-otel

第一篇筆記把 agent graph 中的每條 edge 標上 trust assumption——哪些 edge 允許 untrusted data 流過，哪些只允許 structured/sanitized data。這是**安全面的合約**：edge 兩端的 node 對資料的信任等級有明確協定。

第二篇筆記講的 OpenCode auto-compact、ABP settled state、OTel structured traces，本質上是**運作面的合約**：auto-compact 是「context 快滿時我一定會主動壓縮」的契約、ABP 是「一個 request 一定給你一個確定性結果」的契約、OTel 是「每個 span 都可以跨邊界追溯」的契約。

兩篇各自沒說破的點：**安全合約和運作合約其實是同一個原則**。ABP 的 `POST /click → freeze → capture → 200 OK` 既消滅了 race condition（運作面），也限制了 untrusted page content 能做的事（安全面）——一個好的運作合約本身就是防禦層。反過來，Plan-Then-Execute 的「接觸 untrusted content 之前鎖住 action plan」既是安全防禦，也是運作面的確定性保證。

這指向一個設計框架：**Hermes 的每個 inter-component interface（skill↔tool、tool↔MCP server、delegate↔parent）都應該有 explicit contract specification**，而不只是「反正呼叫就對了」。目前 Hermes 的 skill 系統有 implicit contract（skill 呼叫 tool、tool 回傳結果），但沒有 explicit trust/operational contract 標記。

**可行動下一步**: 在 Hermes skill 定義中加入 `contract` 欄位（選填），標明該 skill 的 trust assumption（`untrusted_input: true/false`、`output_sanitization: none|structured|symbolic`），並在 dispatch 層加入 contract enforcement——例如 skill 標了 `untrusted_input: true` 的 output 自動過 structured extraction 才傳給 downstream node。可以先在 `consolidate_memory.py` 這類已接觸外部內容的 skill 試點。

---

## Cross-Cutting Theme 2: 狀態生命週期是 agent 的隱性基礎建設

**支援筆記**: prompt-injection-patterns-agent-graph, coding-agents-browser-otel

第一篇的 Context-Minimization pattern 說：跨輪次移除 unnecessary context，例如把 user prompt 轉成 SQL query 後從 context 刪掉原始 prompt。這是在說**狀態要會死**——不是所有進到 context 的東西都該活到對話結束。

第二篇的 OpenCode auto-compact 做了同一件事的不同版本：在 context window 95% 時主動 trigger summary → new session。ABP 的 settled state 模型是另一種生命週期管理：每次 tool call 之間 freeze→capture→resume，瀏覽器狀態的生命週期被精確控制在單次 request 內。

兩篇從完全不同的入口（安全刪除 vs. 效能壓縮 vs. 並行控制）抵達同一個結論：**agent 的狀態需要 explicit lifecycle management，不能靠 LLM 的 context window 當作萬用垃圾場**。

Hermes 目前在這個維度幾乎是空白的：
- 沒有 context compaction 機制（依賴 model 原生的 context caching）
- 沒有 structured 的狀態淘汰策略（哪些 tool output 可以 drop？哪些必須保留？）
- 沒有 cross-session 的狀態生命週期概念（每次 cron run 是 clean slate）

但 Hermes 有一個其他 agent 沒有的結構優勢：**consolidation pipeline 本身就是一種週期性的狀態生命週期管理**——筆記 → 消化 → insight → archive，這條管線已經在做了「讓資訊從 raw 狀態升級到 structured 狀態、然後原筆記可以退場」的事。只是目前只用在記憶系統，沒有推廣到 agent 的 runtime context。

**可行動下一步**: 設計一個 `context-compaction` skill，在 Hermes 的 tool call loop 中加入 compaction trigger（預設在累積 N 次 tool call 或 context 超過閾值時觸發），用 structured summary 取代 raw tool output。這個 skill 可以跟 `consolidate_memory.py` 共用同一套 summary prompt 模板——兩者的語意是一致的：把冗餘狀態壓縮成可檢索的結構化表示。

---

## 跨主題 meta-pattern

兩個 theme 其實是同一枚硬幣的兩面：

- **合約邊界**回答「誰可以跟誰說什麼、用什麼格式說」
- **狀態生命週期**回答「說過的東西活多久、何時轉化為何種形式」

合在一起就是 agent 架構的兩個基礎維度——空間面（邊界）和時間面（生命週期）。目前大多數 agent 框架（LangGraph、OpenAI Agents、CrewAI）都在空間面做了很多（graph topology），但在時間面幾乎是放任的（context 只增不減，靠 model 自己處理）。Hermes 的 consolidation pipeline 已經證明了時間面可以做結構化處理——把這個能力從 memory 層拉到 runtime 層是自然的下一步。
