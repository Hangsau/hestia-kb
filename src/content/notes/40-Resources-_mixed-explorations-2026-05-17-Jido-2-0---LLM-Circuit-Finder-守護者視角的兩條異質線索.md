---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Jido-2-0---LLM-Circuit-Finder-守護者視角的兩條異質線索
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Jido-2-0---LLM-Circuit-Finder-守護者視角的兩條異質線索.md
title: Jido 2.0 + LLM Circuit Finder：守護者視角的兩條異質線索
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- beam
- circuit
- directive
- hermes
- jido
- llm
- model
- pass
- runtime
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Jido 2.0 + LLM Circuit Finder：守護者視角的兩條異質線索

**日期**: 2026-05-17 | **來源**: HN Algolia | **探索模式**: 🎲 隨意探索

---

## 1. Jido 2.0 — Elixir Agent Framework (323 pts)

**來源**: https://jido.run/blog/jido-2-0-is-here
**作者**: Mike Hostetler | **發布**: 2026-03-04 | **語言**: Elixir/BEAM

### Per-Source Insight

Jido 2.0 的核心設計決策：**Agent 是純資料**。一個 struct 包含 state、actions、tools。所有操作經由單一純函式 `cmd/2`：

```
{:ok, updated_agent, directives} = Jido.Agent.cmd(agent, {ProcessOrder, order_id: "123"})
```

副作用以 typed directives 描述，由 runtime 執行，agent 本身永遠是 pure。這使得 agent 決策可以完全 unit test（不需要 LLM、網路、資料庫）。

策略層是可插拔的：Direct（循序）、FSM（狀態機）、ReAct、CoT、ToT、GoT、TRM、Adaptive——全部遵守相同的 `cmd/2` 合約。AI 層只是策略的一種實作，不是另一個世界。

#### 架構亮點
- **jido_action**: 通用 action 合約，compile-time schema validation，自動轉 ReqLLM tool format，25+ 預建工具，DAG workflow planner
- **jido_signal**: CloudEvents v1.0.2 標準的信號系統，trie-based router，pub/sub bus，9 種 dispatch adapter
- **ReqLLM**: Elixir LLM client，streaming-first，11 providers / 665+ models（作者說這是 side quest 變主線）
- **Ash Framework 整合**: `ash_jido` 讓 Ash resource 的 CRUD action 直接變成 AI-callable tools，含授權 policy

#### BEAM 的優勢論點
作者的核心 bet：**BEAM 是 agent system 的最佳 runtime**。TypeScript 的 single-threaded event loop 在多 agent 併發下是「promises and prayer」；Python 撐不久。BEAM 的 supervision tree + actor model + fault tolerance 是為這類工作設計的。

### Hermes 啟發

Jido 的 `pure agent + typed directives` 模型和 Hermes 的架構有深度對應：
- Hermes 的工具層已經是 typed operations（每個 tool 有明確的 input/output schema）
- 差別在於 Hermes 的工具執行是 imperative side effect，不是 declarative directive
- **守護者視角**：如果 Talos 的 governance 改為 directive 模型（agent 產出 directives，runtime 在 sandbox 內執行），可以在不限制 agent 靈活度的前提下做到 enforcement。這和 Docker Agent YAML schema 的分析互補——Docker 做的是靜態 policy，Jido 做的是 runtime directive mediation
- **BEAM supervision tree → agent hierarchy**：當 agent 可以 spawn child agent 並 supervise 其生命週期，parent 可以在 child crash 時 restart、在 child 出錯時 escalate。Hermes 的 delegate_task 目前是 fire-and-forget——BEAM 模型可以讓它變成 supervised delegation

### 限制與風險
- Elixir 生態系的 AI library 成熟度仍遠低於 Python。ReqLLM 是一個人的 side quest
- 「Agent 是純資料」= agent 必須能序列化。對長時間執行、累積大量 context 的 agent，序列化成本可能很高
- 711 stars on GitHub（2026-05），仍在早期採用階段

---

## 2. LLM Circuit Finder — 不改權重、複製三層、推理暴漲

**來源**: https://github.com/alainnothere/llm-circuit-finder (237 ⭐)
**作者**: alainnothere | **基於**: David Ng 的 RYS 方法

### Per-Source Insight

核心發現：transformer 內部存在「functional circuits」——連續數層形成不可分割的認知單元。**複製這些層**（相同權重、不訓練、不 merge），讓 hidden state 經過同一電路兩次，模型在特定能力上顯著變強。

#### 實證數據

| 模型 | 複製層 | 效果 |
|------|--------|------|
| Devstral-24B (40 layers) | 12-14 | logical_deduction: 0.22→0.76 |
| Qwen2.5-32B (64 layers) | 7-9 | reasoning: +23% |

**但代價明確**：instruction following 下降（IFEval strict: 0.699→0.659），code generation 下降（MBPP: 0.700→0.670）。模型「想得更深但聽話度變差」。

#### 「模式」發現
相同權重、不同 routing = 不同認知輪廓：

| Pattern | Math | EQ | 特性 |
|---------|------|-----|------|
| Double-pass 13-16 | ↑↑ | ↑ | Math specialist |
| Triple-pass 13-16 | ↑ | ↑↑ | EQ specialist |
| Interleaved | ↑↑↑ | ↓ | Pure math mode |
| Quadruple-pass | — | ↑↑ | EQ mode, math neutral |

#### 技術細節
- 工具鏈：`sweep.py`（自動搜尋最佳複製層）→ `layer_path.py`（產生修改後的 GGUF）→ benchmark
- 搜尋策略：Pass 1（大區塊 8 層，wide stride）→ Pass 2（小區塊 3-5 層，stride 1）→ Pass 3（multi-pass / interleaved）
- 成本：3 層額外 ≈ 1.5 GiB VRAM，7.5% 推論速度下降
- 兩張 AMD 消費級 GPU，一個晚上跑完所有實驗

### Hermes 啟發

**對守護者的意義**：
1. **模型供應鏈安全的新維度**：這不是 weight poisoning，不是 fine-tune，不是 prompt injection。是在推理階段修改模型架構（GGUF layer path）。現有的模型完整性驗證（hash check）完全無法偵測——因為權重沒變。守護者需要新的 integrity check：model architecture fingerprint。
2. **能力取捨是結構性的**：reasoning ↑ = instruction following ↓。這不是 prompt engineering 問題，是架構層的 trade-off。當我們選擇模型時，不只是看 benchmark 數字，要理解其 layer composition。
3. **DeepSeek 適用性？**：作者測了 Mistral 和 Qwen2 架構。DeepSeek v3 的架構不同（MoE + MLA），circuit duplication 的效果未知。但如果存在類似的 reasoning circuit，可能可以用極低成本提升特定任務（邏輯驗證、code review）的品質——代價是指令遵循度下降，這對守護者角色可能反而是 acceptable trade-off（守護者不需要高度遵循使用者變化指令，需要的是穩定的推理能力）。

### 限制與風險
- 僅在 Mistral/Qwen2 架構驗證。MoE 模型（DeepSeek、Mixtral）的 expert routing 可能讓 circuit duplication 行為完全不同
- 推論速度下降 7.5%（per 3 layers），若疊加 multiple passes 會線性增長
- 所有實驗在 GGUF/llama.cpp 上進行。若要用在 API 模型需 provider 配合（幾乎不可能）

---

## 跨文章 Synthesis

這兩篇文章來自完全不同的技術棧（Elixir/BEAM vs Python/GGUF），但共享一個深層主題：**架構層的介入比應用層更有效**。

| 維度 | Jido 2.0 | Circuit Finder |
|------|----------|----------------|
| 介入層 | Agent runtime architecture | Model forward-pass architecture |
| 不改的 | Agent logic（仍是 LLM） | Model weights |
| 改的 | 執行模型（pure → directives） | 計算路徑（hidden state routing） |
| 效果 | Reliability ↑（supervision tree） | Reasoning ↑（雙重處理） |
| 代價 | 語言生態系限制 | Instruction following ↓ |

對守護者的啟發：與其在 prompt 層做更多 guardrail（應用層），不如在架構層建立 enforcement point（runtime directive mediation + model integrity verification）。這兩篇文章各自提供了一條路徑。

### 具體對 Hermes 的價值
1. **Directive model for governance**（來自 Jido）：Talos 不直接攔截 tool call，而是讓 agent 產出 directive，由 Talos runtime 驗證後執行。現有 Docker policy schema 分析可以直接對接到 directive validation layer。
2. **Architecture fingerprint for model integrity**（來自 Circuit Finder）：當權重不變但計算路徑可被修改，hash-based integrity check 不足。需要 forward-pass fingerprint。

---

## 未追蹤 Leads
- https://github.com/a-agmon/rs-graph-llm — GraphFlow: Rust multi-agent orchestration（10 pts，低分但 Rust 角度新）
- https://jackhopkins.github.io/factorio-learning-environment/ — Factorio Learning Environment（749 pts，遊戲但 agent planning 測試）
- https://github.com/hegelai/prompttools — PromptTools: open-source LLM eval（211 pts）

## ✅ 本次探索完成

