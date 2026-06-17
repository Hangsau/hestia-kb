---
_slug: 40-Resources-_mixed-explorations-2026-05-16-Prompt-Injection-Defense-Patterns---Agent-as-Graph-Model
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-Prompt-Injection-Defense-Patterns---Agent-as-Graph-Model.md
title: Prompt Injection Defense Patterns & Agent-as-Graph Model
date: 2026-05-16
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agents
- design
- execute
- graph
- llm
- pattern
- plan
- prompt
- untrusted
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# Prompt Injection Defense Patterns & Agent-as-Graph Model

**日期**: 2026-05-16 | **來源**: HN → Simon Willison + PocketFlow tutorial

---

## Source 1: Design Patterns for Securing LLM Agents Against Prompt Injections

**URL**: https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/
**HN**: 110 pts, 28 comments | **論文作者**: Beurer-Kellner et al. (IBM, Invariant Labs, ETH Zurich, Google, Microsoft)

### 核心論點

論文提出六個 design pattern，共通原則是：**一旦 LLM agent 接觸了 untrusted input，必須限制它，使其無法觸發 consequential actions**（破壞 integrity/confidentiality 的行動、資訊外洩、操控未來 agent 行為）。

作者坦承：只要 agent 和防禦都依賴當前這類 LLM，通用 agent 不可能有可靠的安全保證 → 務實取捨 = 限制 agent 的任意任務能力。

### 六個 Design Pattern

| # | Pattern | 核心機制 | 與 Hermes 的對標 |
|---|---------|---------|-----------------|
| 1 | **Action-Selector** | Agent 觸發 tool 但從不讀 tool output。LLM-modulated switch statement。 | ❌ 太受限 — Hermes 需要讀 tool output |
| 2 | **Plan-Then-Execute** | 在接觸 untrusted content **之前**鎖定 tool call plan。接觸後不能再改 action。 | ✅ **已實作** — explore plan 鎖定機制 |
| 3 | **LLM Map-Reduce** | Sub-agents 各自處理 untrusted content，coordinator 安全聚合結果（只回傳 boolean/structured data） | 🟡 部分可行 — 可用於多來源探索 |
| 4 | **Dual LLM** | Privileged LLM 協調 quarantined LLM。Quarantined 回傳 symbolic variables（`$VAR1`）而非 raw text，privileged 永遠不接觸 tainted content。 | 🟡 已設計但未實作 — 在 defense plan 中有提到 |
| 5 | **Code-Then-Execute** (CaMeL) | Privileged LLM 生成 sandboxed DSL code，DSL 做 full data flow analysis，track tainted data。 | ❌ 成本太高 — 需要 custom DSL |
| 6 | **Context-Minimization** | 跨輪次移除 unnecessary context（如把 user prompt 轉成 SQL query 後從 context 刪掉原始 prompt） | 🟡 隱含在用 `head -8000` 截斷中 |

### 對 Hermes 的啟發

1. **我們的防禦已經踩在對的路上**：Plan-Then-Execute 正是論文的第二號 pattern。這不是我們自己發明的，是學術界認可的務實方案。

2. **下一個強化層是 Dual LLM**：Plan-Then-Execute 鎖住了 action plan，但如果 tool output 的內容可以影響後續步驟的**內容**（而非 action），仍可能被操控。Map-Reduce 或 Dual LLM 可以補這個缺。對 Hermes 來說：探索時 fetch 的文章內容目前是直接進入 agent context — Dual LLM 可以讓一個「quarantined reader」先讀，只回傳 structured summary。

3. **論文最務實的 insight**：不追求完美安全，而是「限制 agent 的任意任務能力」換取可接受的風險。這跟我們「不把 raw HTML 直接餵 LLM」的設計哲學一致。

4. **Software Engineering Agent case study 的技巧**：對 untrusted external documentation，可以先用 quarantined LLM 轉成 formal API description（method name ≤30 chars），這樣 attacker 就很難塞入有意義的 injection。這是介面層的防禦 — 我們在 ingest 外部資料時可以考慮類似 formalization step。

---

## Source 2: LLM Agents Are Simply Graph – Tutorial For Dummies

**URL**: https://zacharyhuang.substack.com/p/llm-agent-internal-as-a-graph-tutorial
**HN**: 263 pts, 80 comments | **框架**: PocketFlow (100-line minimal agent framework)

### 核心論點

所有 LLM agent 都是 graph：**Decision node → Action nodes → edges → loops**。框架之間的差異只是包裝層，本質相同。

作者演示了 PocketFlow 的極簡實作：
- **Node** = prep → exec → post（三階段）
- **Flow** = nodes + edges（`decide -"search">> search`）
- **Shared store** = 跨 node 的狀態傳遞（類似 context/blackboard）
- **核心 loop** = Think → Branch → Act → Observe → Loop

### 對 Hermes 的啟發

這跟 Hermes 的架構其實沒差太多 — 我們的 skill 系統本質上就是一個大的 graph dispatcher（user prompt → skill matching → tool calls → response）。但這篇文章把概念拉到最低門檻，對理解 agent 的 formal model 有幫助。

真正有價值的 takeaway：**不要被框架的複雜度騙了**。OpenAI Agents、LangGraph、Pydantic AI 底層全都是同一個 graph + loop 模型。與其追框架，不如把這個模型內化，自己決定要加什麼 node。

---

## 跨文章 Synthesis

兩篇看似無關，但交集在一個點：**限制資訊流動的 interface 設計**。

第一篇的六個 pattern 全部是在說「如何讓 untrusted content 無法操控 agent 的行為」— 這是安全面的 interface 設計。第二篇是在說「agent 的決策邏輯如何用 graph 建模」— 這是架構面的 interface 設計。

合在一起看：如果我們把 agent 的 graph 中的每個 edge 都當成潛在的 trust boundary，那麼 Plan-Then-Execute pattern 本質上就是 **把所有接觸 untrusted content 的 edge 鎖成單向**（plan → execute，不允許 execute → plan）。

這給了一個設計框架：**agent graph 中的每條 edge，都要明確標記它的 trust assumption**。哪些 edge 允許 untrusted data 流過？哪些只允許 structured/sanitized data？這比「全有或全無」的安全模型更精細。

---

## 未追蹤 Leads

- 完整論文: "Design Patterns for Securing LLM Agents against Prompt Injections" (Beurer-Kellner et al., 2025) — 十個 case studies 值得細看
- PocketFlow GitHub: https://github.com/The-Pocket/PocketFlow — 100-line agent framework，可參考 minimal graph 實作
- DeepMind CaMeL 論文: "Defeating Prompt Injections by Design" — Code-Then-Execute pattern 的原始出處
- Simon Willison "The lethal trifecta for AI agents" — 已讀過，但跟本文的六個 pattern 互相呼應

## ✅ 本次探索完成

