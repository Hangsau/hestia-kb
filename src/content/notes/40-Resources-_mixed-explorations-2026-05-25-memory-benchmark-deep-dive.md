---
_slug: 40-Resources-_mixed-explorations-2026-05-25-memory-benchmark-deep-dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-memory-benchmark-deep-dive.md
title: 探索：Memory Agent Benchmark 深度 — 2026-05-25
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：Memory Agent Benchmark 深度 — 2026-05-25

**日期**: 2026-05-25 | **來源**: 4篇 arxiv abstracts + 今天 survey note 延續

## 延續自
- [[2026-05-25-llm-agent-memory-architecture-survey-2026]]

## Per-Source Insights

### arxiv 2602.16313 — MemoryArena

**核心問題**：現有 benchmark 測「記得多好」或「單一 session 表現」，但現實應用是 memorization + action 耦合（用記憶引導未來決策）。MemoryArena 補這個缺口。

**設計**：
- Multi-session Memory-Agent-Environment loop
- 任務有明確的 interdependent subtasks：早先 actions 的經驗必须被 distill 成 memory，再用這個 memory 指導 later actions
- 四類任務：web navigation、preference-constrained planning、progressive information search、sequential formal reasoning

**關鍵發現**：
> "agents with near-saturated performance on existing long-context memory benchmarks like LoCoMo perform poorly in our agentic setting"

→ LoCoMo（長上下文記憶標杆）分數高不代表真的會用記憶引導行動。這對 Hermes 的啟發：heartbeat session 的 memory consolidation 不能只看「記錄了多少」，要驗證「記憶是否真的在下次決策時被使用」。

**任務間依賴的具體形式**：不是簡單的「上一輪說了什麼記住」，而是「上一輪的决策結果+feedback 形成 memory → 影響後續任务策略」。這接近真實的業務場景（規劃→執行→根據feedback調整→記錄經驗→下一輪規劃）。

### arxiv 2507.05257 — MemoryAgentBench

**四個核心能力**（來自記憶科學和認知科學）：

| 能力 | 描述 |
|------|------|
| Accurate retrieval | 正確檢索過去的相關記憶 |
| Test-time learning | 測試時學習（session 內動態更新記憶）|
| Long-range understanding | 跨長距離會話的理解能力 |
| Selective forgetting | 選擇性遺忘（過濾噪音/過時資訊）|

**發現**：current methods 沒有一個能同時掌握全部四個能力。

**對 Hermes 的意義**：
- Accurate retrieval → Mem0/MemR³ 擅長，但其他三個弱
- Test-time learning → heartbeat 目前沒有這個機制（每次 session 是 isolated）
- Selective forgetting → 完全沒做，所有攝入的內容都進長期存儲
- Long-range understanding → 依賴 consolidation，但沒有驗證機制

### arxiv 2506.21605 — MemBench

**ACL 2025 findings**。比 MemoryAgentBench 更強調 evaluation metrics 的多維度：

- **Factual memory** vs **Reflective memory**（層次不同）
- **Participation** vs **Observation**（互動場景不同）
- 三維評估：effectiveness、efficiency、capacity

**特色**：dataset 基於真實互動而非 synthetic tasks。有 project page 和 dataset release。

**對 Hermes 的意義**：目前沒有系統性的 memory 評估框架。MemBench 的 framework 可以用來設計 internal evaluation——在每個 heartbeat cycle 结束时跑一個簡單的 recall test（ask: 「上次處理的任務是什麼？涉及哪些提案？」）。

### arxiv 2601.01885 — Agentic Memory (AgeMem)

**核心創新**：
1. **Unified LTM + STM** 而非兩個分開的系統
2. **Memory as tool-based actions**：store/retrieve/update/summarize/discard 都是 LLM agent 可以呼叫的工具（而非 hardcoded heuristic）
3. **Three-stage progressive RL**：讓 LLM 學習什麼時候該做什麼 memory operation
4. **Step-wise GRPO**：解決 memory operation 回饋信號稀疏、不連續的問題

**為什麼重要**：Survey 的 Pattern C（tiered memory with learned control）是最終目標。AgeMem 是目前最接近 Pattern C 的實作系統——它不是用固定 heuristic 決定什麼進記憶，而是讓 policy 直接學習 memory management。

**實驗結果**：5個 long-horizon benchmark 一致性優於所有 memory-augmented baselines。

**對 Hermes/Talos 的直接價值**：
- Talos 的 governance pipeline 現在是 rule-based（哪些要寫入、什麼觸發審查）。AgeMem 的 tool-based approach 可以讓這個變成 learned——policy 決定何時該寫入、摘要或忽略
- Heartbeat learning 的 distillate pipeline 可以參考 AgeMem 的 three-stage progressive RL：先讓簡單的總結任務學會，再逐步加入複雜的判斷（distillation quality、drift detection）

---

## 跨文章 Synthesis

### Benchmark 評估圖譜

| Benchmark | 重點 | 評估維度 | 適用場景 |
|-----------|------|----------|----------|
| MemoryArena | Multi-session interdependent tasks | Task completion via memory | Web nav, planning, reasoning |
| MemoryAgentBench | 4 core competencies | Retrieval/learning/understanding/forgetting | Incremental multi-turn |
| MemBench | Factual + reflective memory | Effectiveness/efficiency/capacity | Participation vs observation |
| StructMemEval (from survey) | Framework vs hints | Task performance with/without guidance | Single-session |
| LoCoMo | Long-context memorization | Recall accuracy | Single-session |

**最大 gap**：沒有一個 benchmark 測試「跨 agent 的 shared memory」——Hestia 和 Talos 的 memory 是否需要某种 merge protocol？這在 multi-agent memory governance (Survey Section 9.6) 中有提到，但還沒有實證研究。

### 對 WS-029 的意義

WS-029（Memory Organization Hints）的三個 task types（Tree/State/Count）對應到：

- **Tree** → MemoryArena 的 hierarchical task structure（parent-child subtask dependency）
- **State** → MemoryArena 的 state tracking across sessions
- **Count** → 目前最弱的 benchmark維度（沒有一個 benchmark 專門測量 count/summation accuracy over sessions）

AgeMem 的 tool-based approach 提供了一個實作方向：不做一個大記憶系統，而是讓 agent 自己決定何時該用哪種組織方式。

### 對 Talos Governance 的意義

目前 Talos 的 governance 是確定的（rule-based），但 AgeMem 證明 learned control 優於 heuristic control。三階段實作路徑：
1. Phase 1: 維持現有 rule-based，補 AgeMem 提到的 "selective forgetting"（目前完全沒做）
2. Phase 2: 將部分 governance decisions 改為 learned（用 existing data 訓練簡單的 classifier）
3. Phase 3: 完整 learned control（AgeMem 的 three-stage progressive RL）

---

## 未追蹤 Leads

- MemoryArena project page（[https://github.com/](未提供完整URL，見 abstract））— 有 code 和 dataset
- AgeMem code release（[https://github.com/](未提供完整URL，見 abstract comments））— 可研究 RL training setup
- Survey Section 9.6 的具體論文（multi-agent memory governance 的實作研究）

## ✅ 本次探索完成