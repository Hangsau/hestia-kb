---
_slug: 40-Resources-_mixed-research-agent-agent-planning-core-concepts
_vault_path: 40-Resources/_mixed/research/agent/agent-planning-core-concepts.md
tags:
- knowledge
- ai-agent
- core-concepts
- planning
- reasoning
created: '2026-06-08'
version: 1
status: seedling
sources:
- 2026-06-07-研究報告-agent-planning-architectures-2026-從-react-到-graph-planning-plan-then-judge-reasoning-primitives.md
type: core-concepts
fingerprint: planning, react, graph, plan-then-judge, primitive, self-healing, typed-vocabulary
title: Agent Planning Architectures — 核心概念整合
updated: '2026-06-15'
---

# Agent Planning Architectures — 核心概念整合

> ReAct 不是過時了，但它在 scale 上有三個結構性缺陷。
> 2026 年的規劃研究是為「數百工具 + 長 horizon 任務」設計的新原語。

## ReAct 的三個結構性缺陷

純 ReAct（Reason + Act loop）自 2022 是 agent 設計的預設骨架，但 2025-2026 生產部署暴露出：

1. **Tool confusion** — 工具庫長大到數十至數百個時，flat prompt 裡的 tool description 互相干擾，**模型選錯或語法錯誤的機率飆升**
2. **Plan collapse on long-horizon** — 多步驟任務中**沒有「先想清楚再做」機制**，常陷在局部最優、卡 retry loop
3. **Transient reasoning** — 成功 ReAct traces 裡的 reasoning 套路**沒被凝固成可重用單元**，每次從頭重來

---

## 2026 四種主流規劃架構

| 維度 | ReAct (2022) | Graph Planning | Plan-First/Judge | Primitive Induction | Self-Healing |
|------|--------------|----------------|------------------|--------------------|--------------|
| **Plan 放哪** | LLM 內 prompt | External typed graph | External candidate pool | External typed library | Runtime repair policy |
| **驗證方式** | 無 | Type checking | Execution-free judge | 蒸餾自 traces | Failure-class recovery |
| **從經驗提煉** | 無 | 無 | 無 | ✅ Mine→Cluster→Convert | ✅ Observability traces |
| **適用規模** | ≤5 步、≤10 工具 | 100+ 工具 | 需要 ranking | 已有成功 traces | 任何規模 |

---

## 1. Graph Planning (BioManus, arXiv 2606.04494)

**問題**：biomedical 工具有數百個異質 SDK，flat prompt 塞不下。

**機制**：
1. **BioinfoMCP Compiler** 把每個工具編譯成標準 MCP server，產出 typed MCP graph（nodes = tools/operations/datatypes/workflow stages，edges = typing/dependency）
2. 推論時只 **retrieve task-specific subgraph**（compact slice），再用它在 context 內做 operation-level workflow scaffold
3. **Context compression ratio** 為 `Θ(N / (h · m̄))`：N 為總工具數、h 為 workflow 深度、m̄ 為每個 operation 的候選工具數

**為何有效**：把規劃的搜尋空間從 N 降到 m̄，**decouple planning complexity from tool inventory size**。

**限制**：
- Compiler 寫一次成本高、需 domain expert 為工具標 type
- MCP ecosystem 成熟度仍是風險（見 MCP 整合文）
- Worst case（h 大、m̄ 接近 N）會回到 ReAct 等級

---

## 2. Plan-First, Judge Later (DMAIC-IAD, arXiv 2606.04599)

**靈感**：DMAIC 品質管理框架（Define-Measure-Analyze-Improve-Control）。

**機制**：
1. **Define** 把異質 references 蒸餾成 SOP
2. **Plan** 生成多個候選策略
3. **Judge** 用 **execution-free** 預訓練 judge model 對候選策略排名
4. 選最佳策略再執行

**為何有效**：避免「先亂試、浪費 budget」的代價。在 4 種 modality 實驗比 baseline **+37.76%**。

**限制**：
- Judge model 對未見過的 domain 表現未知
- 論文只跑 4 個 IAD modality
- **Execution-free judging 對需要真實 IO 的任務無效**（網頁操作、code execution）

---

## 3. Reasoning Primitive Induction (arXiv 2606.02994) ⭐

**問題**：ReAct 在 scratchpad 裡重複發明同樣的 reasoning 套路，但這些套路沒被「凝固」成可重用單元。

**機制**：
1. **Mine** — 收集成功 ReAct traces
2. **Cluster** — 把 recurring reasoning moves 分群
3. **Convert** — 把高頻 moves 變成 **typed pseudo-tools**（docstring + LLM-interpreted 函式）
4. **Compose** — 標準 ReAct loop 改呼叫 pseudo-tools

**驚人結果**：induce 出來的 library **比原 agent 還強**：

| 任務 | Zero-shot | +Primitive | 提升 |
|------|-----------|------------|------|
| RuleArena NBA | 30 | **74** | **+44pp** |
| MuSR team allocation | 38 | 68 | +30pp |
| NatPlan meeting | 7 | 29 | +22pp |

5 個 subtask 中**全部**勝過 zero-shot CoT，部分勝過 expert-authored decompositions，且 inference cost 比 AWM 低。

**為何有效**：distillation 把 transient reasoning 變成 **durable typed vocabulary**。

**限制**：
- Distillation 只能在**已有大量成功 trace** 的任務做；冷啟動問題
- **Single-pass 結果** — incremental 增量時 primitive library 是否會 drift / overfit 未被測試

**為什麼這對我們最重要**：對**單人開發者**最友善 — 跑 50 個成功 traces、手動 cluster 出 5-10 個 pseudo-tool、寫成 markdown 模板，**幾小時可完成**。

---

## 4. Self-Healing Orchestrator (arXiv 2606.01416) ⭐

**核心洞見**：把 reliability 視為 **bounded runtime control problem**。

**機制**：
1. Observable failure signals（timeout、malformed args、stale context、retry loop、unverified output）
2. → 推斷 **failure class**
3. 在 explicit **budget** 內選 targeted recovery action
4. **Verifier** 驗證 recovered trajectory，沒過就再 repair
5. Observability traces 全部記錄

**Benchmark 結果**（100-task controlled fault injection）：

| 方法 | Success Rate |
|------|--------------|
| Static workflow | ~80% |
| Retry-only | 94.5% |
| Full replanning | 93.8% |
| **Self-healing** | **98.8%** |

**關鍵**：**silent failure 從 base 的 22% 降到 0%**（controlled semantic silent-failure setting）。

**限制**：
- 98.8% 是 controlled fault injection 的結果；真實世界的 failure 分布未知
- Fault budget 設太低會退化成 retry-only，設太高會過度保守

---

## 5. Harness + Middleware (LangChain 2026 Q2)

**業界對應**：「Harness is the scaffolding around the model that connects it to the real world」。

Middleware 鉤在 agent loop 的 **六個時間點**：
- `before_model` / `after_model`
- `before_tool` / `after_tool`
- `startup` / `teardown`

每片 middleware 處理一個 concern（summarization、guardrail、context pruning、tool error handler、persistence），**自由組合**。

**業界故障處理模式**：**SAGA pattern**（compensating transactions）— 飛行訂位失敗時自動取消飯店/租車，被 LangGraph fault tolerance 文章推為「agentic workflow 的可靠 backbone」。

---

## 真正的普適進步

> 「把 reliability 量化」+「用 typed vocabulary 取代 ad-hoc prompt」

**ReAct 不是過時了**。對短任務（≤5 步、≤10 工具）ReAct 仍是最簡單且可維護的方案。學術界的新方法是為 **scale** 設計的 — 但 scale 是少數任務才需要。

**真正普適的兩個進步**：
1. **Reliability 量化** — Self-Healing 的 failure-class taxonomy + budget 可以直接借鏡
2. **Typed vocabulary** — Reasoning Primitive + HASP PF 是同一個 idea 的兩面

---

## 給我們自己的 Actionable

| 方向 | 難度 | 成本 | 對應檔案 |
|------|------|------|----------|
| **Reasoning Primitive Induction** | MODERATE | 免費 | `firn/skills/primitive_miner.py` + `firn/skills/loader.py` |
| **Self-Healing Orchestrator** | MODERATE | 零 | `firn/tasks/dispatcher.py`（recovery policy）+ `firn/observability/` |
| **Typed Tool Registry** | TRIVIAL | 零 | `firn/tools/registry.py` + `firn/tools/schemas.py` |
| **Plan-then-Judge** | TRIVIAL | +1 LLM call/cron | research workflow |

**Primitive Induction 詳細步驟**：
1. 從 `TurnsLogger` 撈出最近 N=200 個成功 traces
2. 用 LLM cluster 出 K=5-10 個 recurring reasoning moves（例：「先檢查 vault 內是否有相關筆記」「失敗時 fallback 到 cascade 模型」）
3. 把 cluster 寫成 typed pseudo-tool（docstring + 範例），存進 skill library
4. TaskAgent 下次接到任務時，先看 primitive library 是否有合適的 pseudo-tool 可 compose

**Self-Healing 詳細步驟**：
1. 在 `TaskService` / `Dispatcher` 加 failure-class taxonomy
2. 為每個 class 設計 targeted recovery（換模型、剪 context、改寫 prompt、abort）
3. 設定 recovery budget（最多 3 次 repair，超過就 escalate 到 supervisor agent）
4. 引入 verifier：對「完成」事件做 schema check（tool 真的有回傳、file 真的有寫入）

---

## 真正瓶頸

> 「沒有 traces 就沒辦法 induction / 沒辦法 identify failure classes」

- **第一瓶頸**：trace collection — 必須先有結構化日誌
- **第二瓶頸**：judge / verifier — 寫「這個 sub-task 真的成功了嗎」的 verifier **比寫 agent 本身還難**

---

## 參考資料

- **2026-06-07** — ReAct → Graph Planning → Plan-then-Judge → Primitive Induction → Self-Healing
- arXiv 2606.04494 (BioManus)、2606.04599 (DMAIC-IAD)、2606.02994 (Primitive Induction)、2606.01416 (Self-Healing)
- LangChain 2026 Q2 Harness 文件、LangGraph fault tolerance 文章
