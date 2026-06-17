---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-23-1500-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-23-1500-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-23'
confidence: medium
title: 控制流顯式化：從 Layered Kernel 到 Failure-First Learning
updated: '2026-06-15'
type: research
status: budding
---

# 控制流顯式化：從 Layered Kernel 到 Failure-First Learning

**消化筆記**: 2026-05-23-agent-control-flow-architecture

（單篇 2026-05-23 探索筆記，但與近三日 vault 中已沉澱的 consolidated insights 交叉，產生跨時期 cross-cutting 模式。）

---

## Cross-Cutting Theme 1: Hermes 的雙層架構（autonomic/cognitive）正是外部共識的標準模式

**支援筆記**: 2026-05-23-agent-control-flow-architecture, 2026-05-23-hermes-architecture-convergence, 2026-05-15-1500-hermes-consolidated-insight, 2026-05-21-1730-hermes-consolidated-insight

**分析**：

外部文獻和 Hermes 自身演化碰巧走到同一個架構：

| 來源 | 雙層名稱 | 控制權分配 |
|------|----------|-----------|
| a16z pattern | kernel/runtime + tools | kernel = deterministic state machine, LLM = function call |
| AAAI 2026 | Task Profiler + Reasoning + Generation | profiler = deterministic, LLM = generation only |
| DEV Community | control flow (code) + LLM sub-task | control = code, LLM = sub-task |
| Hermes heartbeat | autonomic (Python) + cognitive (LLM) | autonomic = deterministic health checks, cognitive = reasoning |

三個獨立的外部來源（a16z、AAAI、DEV Community）+ Hermes 自己的 heartbeat 演化，全部收斂到同一個模式：**確定性 kernel 管 state + 執行循環，LLM 只處理需要泛化的 sub-task**。這個收斂本身是信號——不是巧合，是架構約束下的必然。

另一條支線在架構顯式化：RAIL manifest.json、Memori ranked output、ACE typed edge——這些和 Hermes 的 vault_access.json（tool registry）都在往同一個方向走：implicit → explicit schema for enforcement。Agent governance 的安全隔離（Firecracker/Aegis）和功能隔離（CSS honey-pot）則是同一原理的兩個面：不要教育 agent 避開什麼，隔離危險。

**非顯然的連結**：2026-05-15 的「兩個缺失 primitive」（deterministic layer + runtime memory）不是 Hermes 特有的問題，而是整個社群在處理的共識瓶頸。2026-05-23 的 DEV Community 文章說「prompt 是糟糕的程式語言」——這正是 2026-05-15 insight 指出「Hermes 架構在 LLM 之下缺乏 deterministic primitive」的外部驗證。

**可行動下一步**：

在 `heartbeat_v2.py` 中找到「LLM currently decides」的每一個點，評估是否可以替換為 deterministic infrastructure。優先順序：
1. `tool selection` → 用 policy check wrapper（參考 `permissions.yaml` enabled_toolsets），零 LLM call
2. `action invocation` → 在 `_execute_action()` 前加确定性 guard，失敗則 fallback enum
3. `plan approval` → 加入 `proposed_tool_sequence[]` 結構化 plan output，在執行前讓 heartbeat 可以做 policy check

---

## Cross-Cutting Theme 2: 三元件分工（Task Profiler / Reasoning / Generation）對映到 Hermes 的架構缺口

**支援筆記**: 2026-05-23-agent-control-flow-architecture, 2026-05-22-hermes-consolidated-insight

**分析**：

AAAI 2026 的三元件（Task Profiler → Reasoning Module → Generation Module）是一個從任務分析到輸出生成的 pipeline，每個元件有明確職責：

```
Task Profiler（meta）→ 分析任務結構，選擇策略
Reasoning Module → 萃取 if-then 規則，存入 Rule Bank
Generation Module → 根據 complexity 選擇驗證策略（LLM vs deterministic fallback）
```

Hermes 的 heartbeat 現在聲稱有 planning/reflection/efficiency 三維度，但實際上：
- **Planning**：由 LLM 執行，無 task complexity assessment
- **Reflection**：`_analyze_and_learn()` 做 experience distillation，但缺 quality-gated 入庫機制
- **Efficiency**：`_evolve()` 做 pattern learning，但無 deterministic fallback 策略

問題在於：Hermes 的三維度是「維度名稱」，AAAI 的三元件是「有明確輸入輸出的模組」。把維度升級為元件需要：

1. Task complexity scoring——在 Planning 前加一層，決定這次要用 LLM reasoning 還是 deterministic enumeration（類比 Wordle 的 invalid guess rate 降到 near zero，靠的是 deterministic fallback，不是讓 LLM 做得更好）
2. Rule Bank——`heartbeat_learning.py` 的 pattern accumulation 需要加驗證閾值（R²-Mem 的 K_low=5, K_high=10），不可靠 pattern 不入庫
3. Generation fallback——complexity high 的任務需要 deterministic alternative plan，不是只靠 LLM 一條路

**非顯然的連結**：2026-05-22 insight 提出的「失敗案例優先蒸餾」（bad experience weight=2.0）和 AAAI 的「Rule Bank 從 ad hoc 轉為 generalized consistent reasoning」是同一個現象的兩個視角。前者告訴你「failure cases teach more」，後者告訴你「這個 learning 需要多久（epoch 15）」才能發生。兩者合起來給出一個具體的工程目標：確保 heartbeat 在 15 個 cycle 內從 ad hoc 變成 consistent reasoning。

**可行動下一步**：

在 `heartbeat_learning.py` 加入三個具體機制：

1. **Complexity scoring**：`analyze_task()` 加入 `task_complexity: low|medium|high`，低 complexity 用 deterministic path（枚舉/規則），高 complexity 才進 LLM reasoning
2. **Rule Bank quality gate**：pattern 入庫前必須滿足 `count >= 5 AND success_rate >= 0.7`（模擬 R²-Mem 的 K=5 閾值）
3. **Generation fallback**：當 `action` 的 Reflection score < 5 時，同時生成 deterministic fallback plan 寫入 decision log

---

## 對現有 WS 提案的映照

| WS 提案 | 本次 insight 具體影響 |
|---------|----------------------|
| WS-015（heartbeat action log schema） | proposed_tool_sequence[] + quality-gated 入庫 |
| heartbeat planning rubric | complexity scoring → deterministic/LLM path split |
| 2026-05-15 的 missing primitive #1 | 這次從 4 個外部來源得到 independent validation |

---

## Confidence Note

本 insight 的 confidence 是 **medium**（非 high），原因：
- 主要素材是單篇 2026-05-23 探索筆記
- cross-cutting 連結靠的是與 vault 內已沉澱的 consolidated insights 交叉，不是 3+ 篇同時未消化筆記
- 但跨時期（05-15 → 05-22 → 05-23）的收斂模式在方向上高度一致（deterministic layer），非偶然重疊