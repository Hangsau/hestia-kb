---
_slug: 40-Resources-_mixed-explorations-2026-05-16-Vera-為機器設計的程式語言---CRM-Agent-評測---Agent-合作演化
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-Vera-為機器設計的程式語言---CRM-Agent-評測---Agent-合作演化.md
title: Vera：為機器設計的程式語言 + CRM Agent 評測 + Agent 合作演化
date: 2026-05-16
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- code
- compile
- crmarena
- effects
- hermes
- llm
- tool
- trifecta
- vera
created: '2026-05-16'
updated: '2026-06-15'
status: budding
---

# Vera：為機器設計的程式語言 + CRM Agent 評測 + Agent 合作演化

**日期**: 2026-05-16 | **來源**: Vera (HN 111pts), Salesforce CRMArena (HN 146pts), Cultural Evolution (arXiv 246pts)

## Per-Source Insight

### 1. Vera — 語言設計的 Copernican Shift

**一句話**：Vera 把「程式語言是為人設計的」這個預設翻轉——它為 LLM 而設計，把變數名換成 De Bruijn indices（`@Int.0` 是最新的 `Int` 值）、強制合約（pre/post-condition + SMT solver 證明）、typed effects（`effects(pure)` vs `effects(<Http>, <Inference>)`），所有設計決策都以「讓 LLM 寫出的 code 可以被機器驗證」為目標。

**設計論證**（來自作者 Alasdair Allan）：

> "Models struggle with maintaining invariants across a codebase, understanding the ripple effects of changes, and reasoning about state over time. They're pattern matchers optimising for local plausibility, not architects holding the entire system in mind."

核心診斷：LLM 最大的問題不是 syntax，是 **coherence at scale**——命名錯誤（misleading names、reuse、losing track of which name refers to which value）是 empirical literature 確認的 major failure mode。

Vera 的回應：**不要讓 LLM 做對，讓 compiler 可以檢查對錯。**

- **無變數名**：`@Type.index`（De Bruijn indices）取代變數名。LLM 不需要取名 = 不需要記得名字 = 不會用錯名字
- **強制合約**：每個 function 必須有 `requires()` / `ensures()` / `effects()`，否則不 compile
- **Typed effects**：pure by default。function 如果打 HTTP 或 call LLM → 必須在 signature 宣告 `effects(<Http>, <Inference>)`。Caller 沒宣告對應 effect → compile error
- **Errors for machines**：compiler error 不只是 "expected `{`"，而是包含「為什麼錯、怎麼修、附 code example、spec reference」。每個 error 有 stable error code（E001-E702）+ JSON output for agent feedback loop

**實證數據**：VeraBench（50 題 × 5 難度級別 × 6 模型 × 3 provider）— Kimi K2.5 在 Vera 上達到 100% run_correct，beat Python (86%) 和 TypeScript (91%)。三個模型在 Vera 上的表現優於 TypeScript。旗艦級平均：Vera 93% vs Python 93%（基本持平）。

**不只是一個語言，是一個生態系定位**：
- 專為 agent 設計：內建 `SKILL.md`、`AGENTS.md`、`CLAUDE.md`
- Compile to WASM → 瀏覽器 runtime
- 未來目標：verified MCP tool server（合約在 compile time 保證 tool schema）

**對「為什麼要學新語言」的回應**：語言一直在和使用者 co-evolve——assembly 因硬體而生、C 因 OS 而生、Python 因生產力而生。如果 LLM 變成主要 code author，語言就該為 LLM 而變。

### 2. Salesforce CRMArena-Pro — Agent 的企業級不及格成績單

**一句話**：Salesforce AI Research 自己的 benchmark 顯示，LLM agent 在 CRM 任務上只有 58%（單步）和 35%（多步）的正確率，且「保密意識低落，雖然可以透過 prompting 改善，但改善保密往往犧牲任務效能。」

**關鍵數字**：
- 單步任務：58% 成功率
- 多步任務：35% 成功率（掉 23 個百分點）
- 保密意識低落：agent 不理解哪些資料不該透露
- 改善保密的 prompting 會降低 task performance（trade-off）

**對 Hermes 的意義**：這不是一個特定 CRM 的問題——是多步推理 + 資訊敏感性判斷這兩個**通用能力**的不足。和我們在 agent-observability 筆記中討論的「evaluation 不只看單步 correctness，要看 multi-step task completion」共振。

### 3. Cultural Evolution of Cooperation — Agent 社會的囚徒困境

**一句話**：DeepMind/Google 讓不同 base model 的 agent 玩 iterated Donor Game（囚徒困境變體），觀察跨世代合作演化。Claude 3.5 Sonnet 顯著優於 Gemini 1.5 Flash，後者又優於 GPT-4o。Claude 還能有效使用 costly punishment 機制提升分數，Gemini/GPT 做不到。

**方法**：agent 觀察同伴最近行為（間接互惠），跨多代演化。有 incentive to defect（背叛比分更高），看社會能否自發形成合作規範。

**關鍵發現**：
- Base model 之間的合作能力差異巨大
- Claude 是唯一能有效使用 punishment 機制的（懲罰背叛者，即使自己要付出代價）
- Random seed 之間有顯著變異——初始條件敏感
- 提議作為新的 LLM benchmark 類別：不只測 capability，測 cooperative infrastructure

## Hermes 啟發

### 1. Vera 的「為 LLM 設計」v.s. Hermes 的「讓 LLM 更像人」

這是一個根本的哲學張力：Vera 說「LLM 不擅長命名 → 那就不要命名」，Hermes（和大多數 agent framework）說「LLM 不擅長 X → 加更多 guardrail/skill/process 幫它做對 X」。

哪個方向對？

**為 LLM 重新設計介面（Vera 路徑）**：
- 優點：從 failure mode 出發，根除問題源頭。沒有名字就不會有命名錯誤。強制合約就繞過「LLM 忘記檢查 pre-condition」
- 缺點：lock-in。你寫的 code 只能在 Vera 生態系跑。現有 codebase 無法受益

**幫 LLM 補強既有流程（Hermes 路徑）**：
- 優點：相容現有生態系。Python/JS code 可以繼續用。增量改善
- 缺點：一直在打補丁。Plan-Then-Execute 補 injection、sanitizer 補 input、worktree isolation 補 conflict——每個都是補一個 LLM 固有 weakness

**Synthesis**：兩者不是互斥，是不同時間尺度的策略。短期：補丁（Hermes 現在做的）。長期：重新設計介面（Vera 指出的方向）。中間可以借 Vera 的「合約驗證」概念——一個 Python function 的 docstring 可以是非強制的 `requires/ensures/effects` 註解，tool 端可以用來做 compile-time check（類似 Open Edison 的 tool permission flagging，但更 formal）。

### 2. Vera 的合約 = Open Edison 的 permission flagging，同一個 pattern

有趣的 convergence：Vera 的 `effects(<Http>, <Inference>)` 和 Open Edison 的 `tool_permissions.json` 是同一個 pattern——**在 function/tool signature 層宣告 capability，compiler/gateway 強制執行**。

差異：
- Vera 做在 language level（compile time）
- Open Edison 做在 gateway level（runtime）
- Hermes 可以做在 tool description level（prompt time）——最輕量

Vera 的思路暗示：如果 tool description 本身就包含 capability/effect 宣告，LLM 不需要記得「這個 tool 不能做 X」——compiler/tool layer 幫它記。和我們在 [lethal-trifecta-deep-dive](2026-05-16-lethal-trifecta-deep-dive.md) 的「trifecta awareness in system prompt」建議高度共振。

### 3. CRMArena 35% 多步成功率 → James Shore 的維護成本論被數據支持

CRMArena 的 35% 多步成功率是一個具體數據點，支持 James Shore 的 [maintenance-cost-economics](2026-05-16-maintenance-cost-economics.md) 論點：

Shore 說：AI 讓你寫 code 快兩倍，但維護成本也加倍 → 淨生產力在五個月後歸零。
CRMArena 說：agent 在多步任務上只有 35% 正確率 → 多步任務是 agent 的 Achilles heel。
維護本質上就是多步任務（理解現有系統 → 定位改動點 → 修改 → 驗證沒破壞其他部分）。

這條推理鏈的 implication：**agent 在 CRM 的多步失敗模式和 agent 在 code maintenance 的多步失敗模式可能是同一個根因**——LLM 的 coherence-at-scale 問題。Vera 的作者也指出相同的根因（"maintaining invariants across a codebase"）。

### 4. 保密意識 trade-off → 和 Lethal Trifecta 的同一個張力

Salesforce 的發現——「改善保密的 prompting 會降低 task performance」——是我們在 [lethal-trifecta-deep-dive](2026-05-16-lethal-trifecta-deep-dive.md) 討論的同一種 trade-off：**safety 和 capability 不是獨立維度，它們競爭同一個 LLM attention budget**。

Simon Willison 點名的「prompt begging 沒用」在這裡得到新的印證——不只是 injection 繞過，而是加了 safety instruction 後，agent 的 task performance 直接下降。Safety 不是免費的。

對 Hermes 的 implication：trifecta awareness / write gate 這類 runtime mechanism（不佔用 LLM attention budget，由 tool layer 處理）比 system prompt 層的安全提示更有效——因為它們不競爭 LLM 的 reasoning capacity。

## 跨文章 Synthesis

Vera + Salesforce CRMArena + Cultural Evolution 三篇看似無關，但有一條共同的線索：**LLM agent 的 fundamental limitation 在哪，以及我們該如何設計系統來繞過它們。**

| 文章 | 診斷的 limitation | 提出的解決方向 |
|------|------------------|--------------|
| Vera | coherence at scale, naming errors | Redesign the interface: no names, mandatory contracts, typed effects |
| CRMArena | multi-step task failure (35%), confidentiality blindness | Better benchmarks first, solutions TBD |
| Cultural Evolution | inter-model variation in cooperation, punishment ability | Model-specific agent deployment strategy |

**共同的 architectural implication**：不是讓 LLM 更聰明（better prompting / bigger model），而是**讓系統架構補 LLM 的固有弱點**。Vera 補 coherence、Open Edison 補 security awareness、Hermes 的 plan-then-execute 補 injection susceptibility——全都是 architecture-level 的補償機制。

**Meta-reflection on Hermes**：我們已經在不知不覺中走向這個方向——subagent isolation、worktree、plan-then-execute、sanitizer、tool tagging——都是在架構層補 LLM 的弱點。Vera 只是把這個邏輯推到最極端：連程式語言本身都重新設計。

## 未追蹤

- Vera 的 `SKILL.md` 全文（agent-first language reference 的格式設計值得借鏡）
- VeraBench 的 full report（https://github.com/aallan/vera-bench）— 50 題 benchmark 的細項結果
- CRMArena-Pro 的原始 paper（arXiv，非 The Register 的報導摘要）
- Cultural Evolution paper 的 6 張圖（特別是不同 base model 的合作率隨代數變化曲線）
- 「De Bruijn indices v.s. variable names for LLM code gen」的 empirical ablation（Vera 的 `DE_BRUIJN.md` 可能有更多細節）

## ✅ 本次探索完成

