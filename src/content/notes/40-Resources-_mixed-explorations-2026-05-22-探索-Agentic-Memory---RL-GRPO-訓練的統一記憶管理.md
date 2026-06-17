---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-Agentic-Memory---RL-GRPO-訓練的統一記憶管理
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-Agentic-Memory---RL-GRPO-訓練的統一記憶管理.md
title: 探索：Agentic Memory — RL-GRPO 訓練的統一記憶管理
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- agent
- arxiv
- benchmark
- grpo
- hermes
- llm
- memory
- memoryarena
- reward
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：Agentic Memory — RL-GRPO 訓練的統一記憶管理

**延續自**: [[2026-05-22-2026-05-22---Agent-Memory-Architecture-Survey--arXiv-2603-07.md]]  [[2026-05-22-2026-05-22---MemoryArena--Agent-Memory-Benchmark-Deep-Dive.md]]

**日期**: 2026-05-22

---

## Source 1: Agentic Memory (AgeMem) — arXiv:2601.01885

### 核心概念

AgeMem 將 LTM（長期記憶）+ STM（短期記憶）整合進 agent 的 policy，透過工具式介面讓 LLM 自主決定何時/儲存什麼/如何管理記憶。

**三大挑戰**：
1. **功能異質協調**：LTM 管 store/update/discard，STM 管 retrieve/summarize/remove 上下文，設計統一機制協調兩者
2. **訓練範式 mismatch**：標準 RL 假設連續 trajectory + 穩定 reward，但記憶操作產生的是碎片化、不連續的 experience
3. **外部專家依賴**：多數系統靠額外 LLM 做記憶控制，增加 inference 成本與訓練複雜度

**三階段漸進 RL 策略**：
- Stage 1: 學 LTM 儲存能力
- Stage 2: 學 STM 上下文管理
- Stage 3: 全任務設定下協調兩種記憶

**Step-wise GRPO**（核心創新）：將輸出 reward 反向傳播到先前的記憶决策，解決記憶操作帶來的稀疏、不連續 reward 問題。

**工具式記憶操作**：5 種操作 — store, retrieve, update, summarize, discard。LLM 透過工具調用執行，而非由外部控制器決定。

### 對 Hermes 的具體啟發

1. **Semantic compression vs. Learned priorities**：Hermes 目前用 semantic compression 做記憶蒸餾，但 AgeMem 的方向是让 agent 自己學什麼值得保留。 Learned prioritization 可能比手動設計的蒸餾策略更強。

2. **記憶操作的工具化**：Hermes 的記憶系統目前是 push-based（自動蒸餾）。AgeMem 的模式是 agent 主動決定何時 store/retrieve/discard。考慮是否讓 Hestia 的心跳系統也有類似的 tool-call 介面，而非全自動。

3. **Step-wise GRPO 解决 discontinuous rewards**：記憶蒸餾的 reward 確實是稀疏的（不是每次蒸餾都有明顯的任務改進）。AgeMem 的 solution 是從最終任務結果反向傳播 reward 到記憶决策。Hermes 可以借鏡這個方向。

---

## Source 2: MemBench — arXiv:2506.21605

### 核心概念

MemBench 是 LLM Agent 記憶系統的 benchmark，評估維度：
- 記憶儲存準確性
- 跨 session 知識遷移
- 長期遺忘與干擾

### 對 Hermes 的具體啟發

MemBench 的維度可以作為 Hestia 記憶系統的評估框架：現有 heartbeat 沒有系統性的記憶 quality 評估。

---

## 跨文章 Synthesis

AgeMem 與 MemoryArena 的核心差異：
- MemoryArena 專注於「何種 benchmark 任務暴露記憶缺陷」
- AgeMem 專注於「如何用 RL 訓練出更好的記憶决策 policy」

兩者互補：benchmark 告訴你問題在哪，RL framework 告訴你怎麼訓練解决問題。

**Hermes 的位置**：目前還在「沒有記憶系統」的階段（只有 semantic compression，但沒有 learned memory policy）。AgeMem 的 framework 是從頭建立記憶系統時可以參考的終極目標。

---

## 未追蹤 Leads

- https://arxiv.org/html/2602.16313 — MemoryArena benchmark code + tasks
- https://github.com/AgeMem/AgeMem — 原始碼（需驗證存在性）
- https://mem0.ai/blog/state-of-ai-agent-memory-2026 — Mem0 2026 survey

## ✅ 本次探索完成

