---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-LLM-Agent-控制流與多輪信任架構
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-LLM-Agent-控制流與多輪信任架構.md
title: 探索：LLM Agent 控制流與多輪信任架構
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aaai
- agent
- control
- dev
- flow
- heartbeat
- llm
- module
- reasoning
- task
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent 控制流與多輪信任架構

**日期**: 2026-05-23
**來源**: HN/DEV Community + Papernotes AAAI 2026

## Per-Source Insights

### 1. DEV Community — "AI Agent Control Flow: Why Better Prompts Won't Fix Your Broken Agent Architecture"

**URL**: https://dev.to/kunal_d6a8fea2309e1571ee7/ai-agent-control-flow-why-better-prompts-wont-fix-your-broken-agent-architecture-2026-42b0

核心命題：團隊在 2026 年仍在試圖用 prompt 解決 agent 複雜度，但正確答案是把控制流寫進 code。prompt 是個糟糕的程式語言。

**關鍵論點**：
- Prompt-only agent 的四大失敗模式：無錯誤處理、state management 脆弱、非決定性 compound、cost 失控
- Control-flow-first architecture 的關鍵屬性：明確 state machine、typed I/O、deterministic routing、structured retry/observable traces
- 框架：LangGraph（graph-based）、DSPy（programming not prompting）、Temporal（workflow engine）、 Prefect/Dagster（data pipeline repurposing）
- 引用 Omar Khattab (Stanford/DSPy)：「Stop asking the LLM to be the operating system. Let it be a function call.」
- 引用 a16z：「新的架構模式是 central agent kernel/runtime 管理 state + 執行 control flow loop + 把 LLM 當 tool 呼叫」

**對 Hermes 的啟發**：
- Hermes 的 heartbeat 雙層架構（autonomic/cognitive）正是此文說的「agent kernel 管理 state，LLM 做特定决策」——只不過 Hermes 的 autonomic 層是 Python，不是 LLM
- Talos 的守護者視角與此完全契合：底層確定的 health check + 上層 LLM 的自主探索。架構選擇是對的

---

### 2. Papernotes — "Towards Trustworthy Multi-Turn LLM Agents via Behavioral Guidance" (AAAI 2026)

**URL**: https://en.papernotes.org/AAAI2026/llm_agent/towards_trustworthy_multi-turn_llm_agents_via_behavioral_guidance/

**TL;DR**: Task Profiler + Reasoning Module + Generation Module 三元件共同演化，在 RL prompting backbone 上实现可驗證、可審計的多輪 agent 行為引導。

**三元件架構**：
1. **Task Profiler**（meta-learner）：分析任務結構，選擇 reasoning + generation 策略。不是直接解題，而是決定怎麼解
2. **Reasoning Module**：從歷史軌跡萃取出「if [observation] then [action]」規則，存入 Rule Bank，跨 epoch 累積
3. **Generation Module**：根據 task complexity 選擇驗證策略； heavily constrained 任務用 deterministic enumeration + fallback，確保輸出合法

**實驗結果**：
- GmN task： Guided Agent 穩定收斂到 45-50 reward（baseline 15-20），2-3x 提升
- Wordle：invalid guess rate 降至 near zero
- 30 epochs × 20 trajectories，Rule Bank 在 epoch 15 後從 ad hoc reasoning 轉為 generalized consistent reasoning

**與 Hermes 對標**：
- 類似的三元件分工：Task Profiler ≈ heartbeat scoring、Reasoning Module ≈ heartbeat learning、Generation Module ≈ heartbeat actions
- Rule Bank 的概念類似 heartbeat pattern 的 accumulation，但 AAAI 論文更嚴謹（驗證後才入庫）
- 「co-evolution across epochs」與「heartbeat 每次 cycle 自我修正」同構

---

## 跨文章 Synthesis

兩篇文章從不同角度抵達同一個核心洞察：**LLM agent 需要確定的、可審計的控制結構，而非把決策全部交給 LLM**。

DEV Community 那篇從軟體工程實踐出發：control flow 應該用 code 表達（loops/conditionals/state machines），LLM 只做具體的 sub-task。這與 DSPy 的「programming not prompting」呼應。

AAAI 2026 論文從學術驗證角度：明確的 Rule Bank + Generation Module fallback 可以在 non-reasoning model（GPT-4.1-mini）上實現 2-3x 效能提升，證明架構比模型聰明更重要。

**共同主題**：
1. **Separation of concerns** — LLM 不是 OS，是一個 function call
2. **Explicit > Implicit** — Rule Bank 可以審計，CoT 無法審計
3. **Deterministic fallback** — 當 LLM 不夠用時，fallback 到枚舉/規則引擎

**對 Talos 守護者角色的啟發**：
Talos 的角色是「守護者」而非「使用者代理」。這意味著 Talos 的 control flow 應該比 Hestia 更保守：明確的 health check 閾值、確定性的 drift detection、規則化的升級機制。與其讓 LLM 自由探索，不如讓確定性邏輯當守門員，LLM 在確定的邊界內探索。

---

## ✅ 追加：原論文深度（arXiv 2512.11421）

fetch 完整 HTML 後的關鍵補充：

### 演算法核心
Algorithm 1 的三個 phase：
1. **Task Profiler** 在 epoch k 後激活，決定 `freason`（reasoning strategy）和 `fgen`（generation operator）
2. **ReasoningUpdate(R, epoch log)** — 從成功的 trajectory 萃取出 `if [obs_t] then [a_{t+1}]` 規則，存入 Rule Bank（附 success rate + usage history）
3. **Generation Layer fallback** — `f_validity(at, ot, ht, E)` 返回 False 時，觸發 `FallbackGenerate(fgen, E)`，在 Wordle 實驗中即 deterministic enumeration over valid candidates

### 關鍵實驗數據
- GmN：epoch 15 後 reward 穩定在 45-50（vs baseline 15-20）；epoch 8/11/13 有「exploration dip」（新發現的 rule 正在被測試）
- Wordle：generation module 在 epoch 10 才啟用；60% 的 invalid output 被 immediate deterministic fallback 救回；最終成功率 > baseline 60%
- 使用 GPT-4.1-mini（非 reasoning model）——刻意選來證明「架構比模型重要」

### 與 Heartbeat 直接對應的設計
| AAAI 元件 | Heartbeat 對應 | 差距 |
|-----------|----------------|------|
| Task Profiler | heartbeat scoring | Heartbeat scoring 目前是 implicit；論文用 LLM-based profiler 做 explicit task classification |
| Reasoning Module + Rule Bank | heartbeat learning (extract_learning) | Heartbeat 的 pattern 是 fuzzy；Rule Bank 是 verified + has success rate |
| Generation Module + deterministic fallback | (無) | Heartbeat 目前沒有 deterministic fallback；EVOLVE action 無 validation step |
| 30 epochs × 20 trajectories | heartbeat 636 cycles | Heartbeat 的 cycle 比 epoch 更短（30min vs 論文的多個 task runs），概念上可對應 |

### 行動結論
Heartbeat 的 implicit pattern accumulation 類似論文的早期階段（epoch 1-10）。升級到 explicit Rule Bank 需要：
1. Validation step：`action` 成功後才寫入 bank（目前 heartbeat action log 沒有這個追蹤）
2. Deterministic fallback：EVOLVE action 失敗後的 fallback 邏輯（目前沒有）
3. Rule Bank persistence：規則跨 cycle 累積（目前 extract_learning 是每次 cycle 重新生成，沒有持久化）

---

## 未追蹤 Leads

- https://dev.to/kunal_d6a8fea2309e1571ee7/ai-agent-control-flow-why-better-prompts-wont-fix-your-broken-agent-architecture-2026-42b0 → 作者 Kunal 的另一篇「AI Agent Failure in Production: 5 Patterns」
- https://www.latent.space/p/llm-infra （a16z AI infrastructure team's documented pattern）
- DSPy https://github.com/stanfordnlp/dspy

## ✅ 本次探索完成（追加於 2026-05-23）
