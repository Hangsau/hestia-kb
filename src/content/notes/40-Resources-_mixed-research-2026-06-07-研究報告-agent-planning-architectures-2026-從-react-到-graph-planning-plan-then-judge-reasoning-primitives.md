---
_slug: 40-Resources-_mixed-research-2026-06-07-研究報告-agent-planning-architectures-2026-從-react-到-graph-planning-plan-then-judge-reasoning-primitives
_vault_path: 40-Resources/_mixed/research/2026-06-07-研究報告-agent-planning-architectures-2026-從-react-到-graph-planning-plan-then-judge-reasoning-primitives.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-07'
version: 1
source_report: 2026-06-07-agent-planning-architectures-2026.md
source_url: null
type: research
fingerprint: agent, firn, primitive, typed, llm, graph, self-healing, react, reasoning,
  context
title: 研究報告：Agent Planning Architectures 2026 — 從 ReAct 到 Graph Planning / Plan-then-Judge
  / Reasoning Primitives
updated: '2026-06-15'
status: budding
---

# 研究報告：Agent Planning Architectures 2026 — 從 ReAct 到 Graph Planning / Plan-then-Judge / Reasoning Primitives

## Version 1 — 2026-06-07

### 核心觀念
**問題**：ReAct（Reason + Act loop）自 2022 提出以來是 agent 設計的預設骨架：LLM 在「思考」與「工具呼叫」之間反覆切換，直到任務完成。但到了 2025-2026 年的生產部署，純 ReAct 暴露出三個結構性缺陷： 1. **Tool confusion** — 當工具庫長大到數十至數百個，flat prompt 裡的 tool description 互相干擾，模型選錯或語法錯誤的機率飆升。 2. **Plan collapse on long-horizon** — 對於多步驟任務，ReAct 沒有「先想清楚再做」的機制，常陷在局部最優、卡 retry loop…

**洞見**：把這四種機制**抽象成一個座標系**： | 維度 | ReAct (2022) | Graph Planning | Plan-First/Judge | Primitive Induction | Self-Healing | |------|--------------|----------------|------------------|--------------------|--------------| | Plan 在哪 | LLM 內 prompt | External typed graph | External candidate pool | External type…

### 架構 / 機制
## 2. Core Mechanism

四種 2026 主流規劃架構，差別在「plan 放哪裡」「如何驗證」「如何從經驗提煉」：

### 2.1 Graph Planning (BioManus, arXiv 2606.04494)

**問題**：biomedical 工具有數百個異質 SDK，flat prompt 塞不下。

**機制**：
1. **BioinfoMCP Compiler** 把每個工具編譯成標準 MCP server，產出 typed MCP graph（nodes = tools/operations/datatypes/workflow stages，edges = typing/dependency）。
2. 推論時只 **retrieve task-specific subgraph**（compact slice），再用它在 context 內做 operation-level workflow scaffold。
3. **Context compression ratio** 為 `Θ(N / (h · m̄))`：N 為總工具數、h 為 workflow 深度、m̄ 為每個 operation 的候選工具數（m̄ ≪ N）。

**為何有效**：把規劃的搜尋空間從 N 降到 m̄，**decouple planning complexity from tool inventory size**。

### 2.2 Plan First, Judge Later (DMAIC-IAD, arXiv 2606.04599)

**靈感**：DMAIC 品質管理框架（Define-Measure-Analyze-Improve-Control）。

**機制**：
1. **Define** 把異質 references 蒸餾成 SOP。
2. **Plan** 生成多個候選策略。
3. **Judge** 用 **execution-free** 預訓練 judge model 對候選策略排名，**不需要真的執行**。
4. 選最佳策略再執行。

**為何有效**：避免「先亂試、浪費 budget」的代價；在 4 種 modality 實驗比 baseline 高 **+37.76%**。

### 2.3 Reasoning Primitive Induction (arXiv 2606.02994)

**問題**：ReAct 在 scratchpad 裡重複發明同樣的 reasoning 套路，但這些套路沒被「凝固」成可重用單元。

**機制**：
1. **Mine** — 收集成功 ReAct traces。
2. **Cluster** — 把 recurring reasoning moves 分群。
3. **Convert** — 把高頻 moves 變成 **typed pseudo-tools**（每個是一個 docstring + LLM-interpreted 函式）。
4. **Compose** — 標準 ReAct loop 改呼叫 pseudo-tools。

**關鍵結果**：induce 出來的 library **比原 agent 還強**：
- RuleArena NBA: 30 → 74（+44pp）
- MuSR team allocation: 38 → 68（+30pp）
- NatPlan meeting: 7 → 29（+22pp）
- 5 個 subtask 中**全部**勝過 zero-shot CoT，部分勝過 expert-authored decompositions，且 inference cost 比 AWM 低。

**為何有效**：distillation 把 transient reasoning 變成 **durable typed vocabulary**。

### 2.4 Self-Healing Orchestrator (arXiv 2606.01416)

**機制**：
1. 把 reliability 視為 **bounded runtime control problem**。
2. Observable failure signals（timeout、malformed args、stale context、retry loop、unverified output）→ 推斷 **failure class**。
3. 在 explicit **budget** 內選 targeted recovery action。
4. **Verifier** 驗證 recovered trajectory，沒過就再 repair。
5. Observability traces 全部記錄。

**Benchmark 結果**（100-task controlled fault injection）：
| 方法 | Success |
|------|---------|
| Static workflow | ~80% |
| Retry-only | 94.5% |
| Full replanning | 93.8% |
| **Self-healing** | **98.8%** |

關鍵：**silent failure 從 base 的 22% 降到 0%**（在 controlled semantic silent-failure setting）。

### 2.5 Harness + Middleware (LangChain 2026 Q2)

業界對應：「**Harness is the scaffolding around the model that connects it to the real world**」。

Middleware 鉤在 agent loop 的六個時間點：`before_model` / `after_model` / `before_tool` / `after_tool` / `startup` / `teardown`。每片 middleware 處理一個 concern（summarization、guardrail、context pruning、tool error handler、persistence），自由組合。

對應的業界故障處理：**SAGA pattern**（compensating transactions）— 飛行訂位失敗時自動取消飯店/租車，這在 LangGraph fault tolerance 文章被推為「agentic workflow 的可靠 backbone」。

---

### 思考
## 4. Limitations / Honest Assessment

### 4.1 各方法的弱點

- **Graph Planning (BioManus)**：compiler 寫一次成本高、需要 domain expert 為工具標 type；MCP ecosystem 成熟度仍是風險（見 6/6 報告）。context compression 是平均值的 asymptotic，worst case（h 大、m̄ 接近 N）會回到 ReAct 等級。
- **Plan-First/Judge (DMAIC-IAD)**：judge model 是 pretrained，**對未見過的 domain 表現未知**；論文只跑 4 個 IAD modality。**execution-free judging 對需要真實 IO 的任務無效**（網頁操作、code execution）。
- **Reasoning Primitive Induction**：distillation 只能在**已有大量成功 trace** 的任務做；冷啟動問題。「+44pp on RuleArena NBA」聽起來神奇，但**作者坦承這是 single-pass** — incremental 增量時 primitive library 是否會 drift / overfit 未被測試。
- **Self-Healing**：98.8% 是 controlled fault injection 的結果；**真實世界的 failure 分布未知**。fault budget 設太低會退化成 retry-only，設太高會過度保守。
- **HASP / Skill Programs**：依賴**過去 experience**，需要 post-hoc human review 或 strong teacher LLM 才能驗證 PF 品質；社區 extension 容易引入劣質 skill（From Prompt to Process 論文點名的 risk 之一）。

### 4.2 我們的獨立評估

**ReAct 不是過時了**。對短任務（≤5 步、≤10 工具）ReAct 仍是最簡單且可維護的方案。學術界的新方法是為 **scale** 設計的 — 但 scale 是少數任務才需要。

**真正普適的進步是「**把 reliability 量化**」和「**用 typed vocabulary 取代 ad-hoc prompt**」**：
- Reliability：Self-Healing 的 failure-class taxonomy + budget 可以直接借鏡。
- Typed vocabulary：Reasoning Primitive + HASP PF 是同一個 idea 的兩面。

**可複製性**：
- Graph Planning 的 compiler 寫一次，但 100+ 工具才划算；普通開發者用 5-20 個工具時，**用 LangChain middleware + 簡單 typed registry 就夠**。
- Plan-then-Judge 不需要訓練 judge — 直接用一個強 LLM（GPT-4o / Claude Sonnet 4）做 zero-shot ranking 就能有 80% 的效果。
- Primitive Induction 對**單人開發者**最友善：跑 50 個成功 traces、手動 cluster 出 5-10 個 pseudo-tool、寫成 markdown 模板，幾小時可完成。
- Self-Healing 的 fault-injection benchmark 是 open source；任何人都能在自己的 agent 套上。

**瓶頸**：
- 真正的瓶頸是 **trace collection**（沒有 traces 就沒辦法 induction / 沒辦法 identify failure classes）。
- 第二瓶頸是 **judge / verifier** — 寫「這個 sub-task 真的成功了嗎」的 verifier 比寫 agent 本身還難。

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

對 firn（位於 `/root/firn/`，Python + uv，模組：`agents/`、`tools/`、`tasks/`、`observability/`、`memory/`、`context/`、`skills/`）：

### 5.1 Reasoning Primitive Induction — `firn/skills/`

**想法**：firn 的 `TaskAgent` 每天跑 cron、把成功 task 結構化存在 memory。可以在 `firn/skills/` 新增 `primitive_miner.py`：
1. 從 `TurnsLogger`（observability）撈出最近 N=200 個成功 traces。
2. 用 LLM cluster 出 K=5-10 個 recurring reasoning moves（例如：「先檢查 vault 內是否有相關筆記」「拆分大 task 成子 task」「失敗時 fallback 到 cascade 模型」）。
3. 把 cluster 寫成 typed pseudo-tool（docstring + 範例），存進 skill library。
4. TaskAgent 下次接到任務時，先看 primitive library 是否有合適的 pseudo-tool 可 compose。

**難度**：MODERATE（需要 cluster prompt + 一輪蒸餾 + library 維護）
**成本**：免費方案可運作（用本地小模型做 cluster，或用 cascade 的 cheap tier）
**對應檔案**：`firn/skills/loader.py`（加載 pseudo-tool）、`firn/agents/task_agent.py`（優先查 library）

### 5.2 Self-Healing Orchestrator — `firn/tasks/`

**想法**：在 `TaskService` / `Dispatcher` 加 failure-class taxonomy：
- 從 `TurnsLogger` 觀察常見失敗（timeout、malformed tool call、context overflow、retry loop）。
- 為每個 class 設計 targeted recovery（換模型、剪 context、改寫 prompt、abort）。
- 設定 recovery budget（最多 3 次 repair，超過就 escalate 到 supervisor agent）。
- 引入 verifier：對「完成」事件做 schema check（tool 真的有回傳、file 真的有寫入）。

**難度**：MODERATE
**成本**：零
**對應檔案**：`firn/tasks/dispatcher.py`（recovery policy）、`firn/observability/`（failure logging）、`firn/llm/circuit_breaker.py`（已有的 breaker 可重用）

### 5.3 Typed Tool Registry — `firn/tools/`

**想法**：把 `ToolRegistry` 從 dict[str, callable] 升級成 typed registry（name, description, input_schema, output_schema, typical_failure_modes, recovery_hint）。這樣 `TaskAgent` 在挑 tool 時可以：
- 先用 input_schema 過濾（type match）→ 縮減 candidate。
- 用 `typical_failure_modes` 預先標註 risk。
- 用 `recovery_hint` 給 Self-Healing 模組線索。

**難度**：TRIVIAL（純 schema 工作）
**成本**：零
**對應檔案**：`firn/tools/registry.py`、`firn/tools/schemas.py`

### 5.4 Plan-then-Judge for research workflow

**想法**：firn 的 research cron（每天生成研究報告）可以在 dispatch 前先生成 2 個 outline 候選（用同一 prompt temperature=0.7 跑兩次或兩個 model），用第三個 LLM call 比較哪個 outline 的 topic coverage 更好、sources 更平衡，再選來展開。對應 DMAIC-IAD 的 execution-free judge。

**難度**：TRIVIAL
**成本**：每次研究多 1 個 LLM call（可放在 cascade 的 cheap tier）

### 5.5 對 managed-agents 流程

把這個 framework 評比（From Prompt to Process 的 6 維度 taxonomy）直接套到 firn：
| 維度 | firn 現狀 | 改善方向 |
|------|----------|---------|
| Specification | 弱（CLAUDE.md 是規範） | 結構化 SPEC.md |
| Context | 強（context builder、memory blocks） | 加 primitive library |
| Roles | 中（ConversationAgent / TaskAgent / CronAgent） | 缺 supervisor |
| Execution | 中 | 加 Self-Healing |
| Validation | 弱（turns logger 是觀察） | 升級成 verifier |
| Portability | 強（uv、模組化） | 維持 |

---


### 來源

- 原始報告：2026-06-07-agent-planning-architectures-2026.md
- 類型：
- 連結：
