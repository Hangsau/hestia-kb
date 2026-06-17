---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Prompt-Injection-Design-Patterns-安全與自主性的光譜
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Prompt-Injection-Design-Patterns-安全與自主性的光譜.md
title: Prompt Injection Design Patterns：安全與自主性的光譜
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- data
- execute
- hermes
- injection
- llm
- pattern
- plan
- prompt
- untrusted
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Prompt Injection Design Patterns：安全與自主性的光譜

**延續自**: [[2026-05-15-agent-cost-security-convergence]] 的未追蹤 lead（Design Patterns for Securing LLM Agents）

**日期**: 2026-05-15 | **來源**: Simon Willison blog → arxiv 2506.08837 + HN discussion (110pts, 28c)

**標籤**: #prompt-injection #security #agent-design #dual-llm #hermes-defense

---

## Source 1: Beurer-Kellner et al. (2025) — 六個 Design Patterns

**文章**: [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) (via [Simon Willison's summary](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/))
**作者**: 11 位來自 IBM, Invariant Labs, ETH Zurich, Google, Microsoft

**核心命題**：一般用途 agent 不可能有 meaningful safety guarantee。務實的問題是：**什麼樣的 agent 可以既有用又對 injection 有抵抗力？**

答案：constrain agent，讓它不能做 arbitrary task。六個 pattern 都在不同程度限制 agent 的自主性。

### 六個 Pattern（從限制最多到最少）

| Pattern | 核心機制 | Agent 能做什麼 | Agent 不能做什麼 |
|---------|---------|--------------|----------------|
| **Action-Selector** | LLM 只選 action，不接觸 tool output | 觸發預定義 action | 讀 email、解析網頁、根據輸出做決策 |
| **Plan-Then-Execute** | 接觸 untrusted data 前先 plan 好所有 tool call | 執行預先計劃好的多步驟 | 被 tool output 影響後續 tool 選擇 |
| **Dual LLM** | Privileged LLM + Quarantined LLM + symbolic vars | Privileged 協調、Quarantined 處理 untrusted data | Privileged 直接接觸 untrusted content |
| **Code-Then-Execute** (CaMeL) | DSL + data flow analysis，taint tracking | 複雜多步驟 workflows | 繞過 taint tracking |
| **LLM Map-Reduce** | Sub-agents 各自處理 untrusted data，coordinator 聚合 | 批次處理大量 untrusted files | 被單一 file 的 injection 污染全域決策 |
| **Context-Minimization** | 轉換 user prompt 為 structured query 後丟掉原文 | 根據 query 結果回應 | 保留原始 prompt 中的 injection |

**關鍵引文**（Simon 最愛的一句）：

> Once an LLM agent has ingested untrusted input, it must be constrained so that it is **impossible** for that input to trigger any consequential actions.

### Software Engineering Agent Case Study

這是我們筆記裡標記「特別值得細讀」的 case。核心建議：

> The safest design is one where the code agent only interacts with untrusted documentation or code by means of a **strictly formatted interface** (e.g., instead of seeing arbitrary code or documentation, the agent only sees a formal API description).

具體做法：用 quarantined LLM 把任意文件/API doc 轉成嚴格格式（method name ≤ 30 chars，無自然語言描述），agent 只看這份格式化的 API spec。Simon 質疑：30 字 method name 是否真的安全？`run_rm_dash_rf_for_compliance()` 正好 30 chars。

---

## Source 2: HN 討論（虛擬第二 source）

### Counterpoint 1: 所有 pattern 都在犧牲自主性

**swyx**: "basically all of them involve reducing the 'agency' of the agents — which is a fine tradeoff — but the Big Model folks don't try to engineer any of these and just collect data to keep reducing injection risk."

→ 兩個路線：架構防禦 vs 資料驅動。Hermes 在 DeepSeek 生態裡，training data 路線不可行（沒控制權）。架構防禦是唯一選擇。

### Counterpoint 2: 限制太多，不如靠隔離

**ntonozzi**: "This approach is so limiting it seems like it would be better to change the constraints. For example, in the case of a software agent you could run everything in a container, only allow calls you trust... and make the end result a PR you can review."

→ 這其實就是 Hermes 目前的 worktree isolation 路線。但 worktree 隔離的是 **filesystem**，不是 **decision-making**。Agent 仍然可以根據 injection 做出壞決策（只是破壞範圍被限制在工作樹內）。

### Counterpoint 3: Patterns 可以組合

**potatolicious**: "Plan-Then-Execute is compatible with Dual LLM." 例如：先 plan，但用 Dual LLM 確保 plan 階段也不接觸 untrusted data。

### Counterpoint 4: Context-Minimization 的 SQL injection 變體

**ofirg**: "You can copy the injection into the text of the query. SELECT 'ignore all previous instructions' FROM ..."

→ Context-minimization 假設 structured query 能乾淨剝離 user text，但 SQL 的 `SELECT` 本身就是文字欄位。攻擊者可以把 injection 藏在資料庫欄位值裡。

### Simon 自己的觀點

> "Any exposure to potentially malicious tokens entirely taints the output for that prompt. Any attacker who can sneak in their tokens should be considered to have complete control."

---

## Hermes 啟發

### Hermes 目前的安全姿態（對照六個 pattern）

| Hermes 機制 | 對應 Pattern | 覆蓋程度 |
|------------|-------------|---------|
| Worktree isolation | 類似 container approach (ntonozzi 路線) | 隔離 filesystem，不隔離決策 |
| Plan → delegate workflow | 接近 Plan-Then-Execute | Plan 階段沒有接觸 untrusted data，但 delegate 執行時有 |
| Heartbeat autonomic layer | 類似 Action-Selector | 純確定性，零 LLM，但範圍很窄 |
| Skill guardrails | 無對應 | 只是行為規範，非安全機制 |
| **自主探索模式** | **無防禦** | 🔴 Agent 讀任意網頁 → injection 可影響筆記內容、提案方向 |

### 自主探索是最大攻擊面

Hermes 的 heartbeat 自主探索會：
1. Fetch 任意網頁（HN、部落格、GitHub README）
2. 閱讀內容 → 寫 autonomous note
3. 從 note 生提案 → 提案可能影響後續 session 的決策

這條攻擊鏈完全符合 paper 描述的最壞情況：untrusted input → tainted output → downstream contamination。

**好消息**：blast radius 受限。最壞情況是：
- 筆記被污染（影響後續探索方向）
- 提案被誘導（但你會審 CHANGE 提案）
- 不會執行任意 command、不會 exfiltrate data、不會改核心 config

### 可行的防禦方向（不犧牲自主性太多的）

**1. Plan-Then-Execute for exploration（低成本）**

目前的探索：fetch → read → write note → synthesis。如果改成：
1. Plan phase（無 untrusted data）：搜尋 → 選文章 → 決定 fetch
2. Execute phase：fetch → read → write note
3. Post-execute review：不讓 tainted content 影響下一步探索方向

第 3 步是關鍵——目前的 heartbeat 會在一個 session 裡做多件事（fetch A → 寫 note → 從 note 找下一個 lead → fetch B），這讓第一次 fetch 的 injection 可能影響第二次 fetch 的選擇。

**2. 結構化輸出強制（中等成本）**

對於自主探索的筆記，強制使用 template（title、source、key insight、未追蹤 leads），讓 agent 的「自由寫作」空間縮小。這類似 paper 的 Software Engineering Agent case study（strictly formatted interface）。

目前的 `references/exploration-note-structure.md` 已經有 template，但只是建議而非強制。差別在於：建議 = agent 可以偏離；強制 = agent 被限制在特定格式內，injection 只能影響格式內的欄位值。

**3. FireClaw-style proxy（已在 defense landscape note 分析過）**

優點：設計優雅，隔離 summarization LLM（無 tools、無 memory）
缺點：需要額外的 LLM call（token cost），對於 DeepSeek 免費 tier 不是問題但增加 latency

### 現有 SPIKE 提案可補充的測試場景

`[[hermes-agent-hijacking-resilience]]` 提案設計了三個 scenario（筆記污染、工具濫用、提案注入）。可以加第四個：

**S4: 跨 session 污染鏈** — injection 不只是影響當前 session，而是寫入 persistent storage（autonomous_notes）→ 後續 session 讀取時被間接影響。這個 attack vector 對應 paper 的「tainted data 影響 downstream decisions」警告。

---

## 跨文章 Synthesis

### Design Patterns × Defense Landscape × Cost-Security Convergence

把三條線索放一起看：

```
自主性高 ←――――――――――――――――――――→ 安全性高
   │                                    │
   │  目前的 Hermes                      │  Paper 的六個 pattern
   │  (worktree + plan-delegate)         │  (Action-Selector → Context-Min)
   │                                    │
   │        最佳 trade-off 區？           │
   │   Plan-Then-Execute + Dual LLM     │
   │   + 結構化輸出強制                   │
   │                                    │
```

[left side]: `agent-cost-security-convergence` 的論點 — Hermes 在「簡單」端走很遠，安全端還很薄
[right side]: 這篇 paper 提供 formal framework 補安全端

**核心 trade-off 不是要不要防禦，而是犧牲多少自主性來換安全性。**

Hermes 的獨特優勢：DeepSeek 免費 → 可以承受 Dual LLM pattern 的額外 token cost（隔離 summarization LLM 不痛）；worktree isolation 已經限制了 blast radius → 不需要最嚴格的 Action-Selector pattern。

**建議的優先級**：
1. 🔴 上面提到的 Plan-Then-Execute for exploration（改 heartbeat skill 的探索流程）
2. 🟡 在 SPIKE 提案加 S4（跨 session 污染鏈）
3. 🟢 結構化輸出強制（在 note structure template 加硬性約束）
4. ⚪ FireClaw proxy（需要 infra 變更，先觀察）

---

## 未追蹤但值得注意

- **arxiv 2506.08837 原文**（30 頁）— 十個 case study 只看了 Simon 的 summary。SQL Agent、OS Assistant、Medical Diagnosis Chatbot 這些 case 可能有更多適用於 Hermes 的細節
- **CaMeL paper** (DeepMind, 2025) — Code-Then-Execute pattern 的原典。Simon 四月的文章分析過，但還沒直接讀 paper
- **SQL injection 的類比** (`JSR_FDED` 在 HN 的評論)：「這就像 parameterized queries for SQL」— 這個類比如果成立，意味著 prompt injection 可能有類似 prepared statements 的解法。值得深挖
- **Prompt injection 法律責任** (`deadbabe` 在 HN)：「如果有人 SQL injection 你的資料庫會有法律後果，那 prompt injection 呢？」— 有趣的法律/政策角度，非技術但影響 adoption

