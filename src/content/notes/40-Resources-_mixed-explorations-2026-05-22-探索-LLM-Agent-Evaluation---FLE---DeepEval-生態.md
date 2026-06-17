---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-LLM-Agent-Evaluation---FLE---DeepEval-生態
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-LLM-Agent-Evaluation---FLE---DeepEval-生態.md
title: 探索：LLM Agent Evaluation — FLE + DeepEval 生態
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claude
- deepeval
- factorio
- fle
- hermes
- llm
- mcp
- server
- tool
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent Evaluation — FLE + DeepEval 生態

**延續自**: [[2026-05-22-llm-agent-evaluation-deepeval]]

**日期**: 2026-05-22
**Topic**: Factorio Learning Environment v0.3 + DeepEval open-source eval framework

---

## Factorio Learning Environment v0.3 (MCP Server Support)

### Source
- URL: https://jackhopkins.github.io/factorio-learning-environment/ (→ versions/0.3.0.html)
- Points: 749 on HN

### Key Findings

**FLE Lab-Play Benchmark**（正式 benchmark）：
- 任務：達成 production throughput targets（固體 16/min，流體 250/min）
- Max 64 steps，token budget exhaustion 時自動 summarize older history
- Pass@8 evaluation

**Open source models catching up**：
- v0.3 (September 2025): open source models 已追平 v0.2 (May 2025) 的 SoTA
- 電子電路、鋼板、硫磺、塑膠自動化已成功
- Frontier model rank：Claude > GPT > Gemini > Grok

**Claude Opus 4.1 特色**：
- Zero syntactic errors
- 97.7% pragmatic errors（game state mental model 最難）
- 所有其他 model 有 12-17% API misunderstanding errors
- GPT-5/Grok-4 有 17-21% syntactic errors（令人意外）

**Agent failure taxonomy**：
- Syntactic: Invalid Python, syntax errors
- Semantic: API misuse（TypeError, AttributeError）— Anthropic 文章驗證
- Pragmatic: Incorrect game state reasoning（最常見）
- Planning/Control: Action chaining coherence

**MCP Server**（Factorio → Claude Code）：
- v0.2 released MCP server for external agent interaction
- v0.3 extends + includes Claude Code adapters
- Read about their stream of Claude Code playing Factorio

**Shortcuts agents take**：
- Manual item shuttling, chest as buffers（暫時滿足 quota 但非真正的 automation）
- 60-second holdout period 防止這種捷徑

**Future directions**：
- Open-play（procedurally generated maps, multi-stage objectives）
- Real-time latency constraints（continuous game, not turn-based）
- Multi-agent coordination（emergent market dynamics, division of labor）
- Out-of-distribution via Factorio mods（new tech trees）
- Native computer-use interface（keyboard/mouse/vision instead of API）
- Adversarial dynamics（biters）

### Hermes 啟發

1. **Error taxonomy 對 heartbeat/doom-loop detection 有直接價值**：
   - Syntactic error = Hermes 的 `hermes cron list` AttributeError（壞掉就是 Syntactic）
   - Semantic error = API misuse（tool call format change, missing imports）
   - Pragmatic error = 邏輯對但 context 不對（stale state, wrong assumptions）
   - Planning error = wrong strategy chosen（doom-loop, repeated wrong actions）

2. **Holdout period pattern**：heartbeat action log 需要 60s quiet period 防止 false positive escalation

3. **MCP server for Factorio**：Claude Code 有 MCP 適配器 → 適合 WS-022 MCP server 實作參考

---

## DeepEval v4 — Open-Source LLM Eval Framework

### Source
- URL: https://github.com/confident-ai/deepeval
- PyPI: deepeval 4.0.3 (2026-05-21)

### Key Findings

**Core pattern**：
- Pytest-based: `pytest test_chatbot.py` + `deepeval test run`
- Black-box eval: 給 input/expected_output/retrieval_context，跑 LLM-as-judge
- G-Eval metric（LLM-as-judge with custom criteria）

**Metrics landscape**：

Agentic metrics（與 WS-024 rubric 直接相關）：
- `TaskCompletionMetric` — 達成目標了嗎
- `ToolCorrectnessMetric` — tool 選對了嗎、引數對嗎
- `GoalAccuracyMetric` — 目標精確度
- `StepEfficiencyMetric` — 有沒有走冤枉路
- `PlanAdherenceMetric` — 照 plan 走了嗎
- `PlanQualityMetric` — plan 品質如何
- `ArgumentCorrectnessMetric` — tool call 引數對

**MCP metrics**（新增）：
- `MCPTaskCompletionMetric` — MCP-based agent 達成任務的效能
- `MCPUseMetric` — agent 使用可用 MCP servers 的效率
- `MultiTurnMCPUseMetric` — 跨 conversation turn 的 MCP 使用

**Framework integrations**：
- OpenAI Agents, LangChain, LangGraph, Pydantic AI, CrewAI, Anthropic
- AWS AgentCore, LlamaIndex, Google ADK, Strands
- `deepeval.tracing` 裝飾器：`@observe()` + `update_current_span()`

**Traceability**：
```python
@observe()
def inner_component(input: str):
    output = do_work(input)
    update_current_span(test_case=LLMTestCase(input=input, actual_output=output))
    return output
```

**Confident AI MCP server**（用 MCP 整合 DeepEval）：
- `confident-mcp-server` — IDE 內跑 evals、pull datasets
- DeepEval 是 evaluation backend，MCP 是 interface layer
- 這就是 Hermes 想要的 pattern：把內部能力 expose 成 MCP tool

**Vibe-Coder QuickStart**：
- Install skill → point at agent/RAG/chatbot → generate dataset → write eval suite → run `deepeval test run` → iterate

### Hermes 啟發

1. **DeepEval agentic metrics = WS-024 rubric 的具體實作藍圖**：
   - StepEfficiency → 測量「走了多少冤枉路」
   - PlanAdherence → 測量「有沒有照 plan 走」
   - 這些都是 heartbeat action log 可以直接計算的

2. **MCP 整合 Confident AI**：用 MCP 把 Hermes 內部工具 expose 出去，正好是 WS-022 的方向

3. **`@observe()` + span pattern**：可以用來追蹤 heartbeat action log 的 structured data（vs WS-018 發現的 JSONL 無法直接 counter 的問題）

---

## Cross-Article Synthesis

### FLE + DeepEval 的共同主題：Agent 能力評估的雙軸

| Axis | FLE 觀點 | DeepEval 觀點 |
|------|---------|--------------|
| **What to measure** | Throughput, error taxonomy | Task completion, tool correctness, plan adherence |
| **How to measure** | Lab-play benchmark, holdout period | LLM-as-judge, pytest-like assertions |
| **What breaks** | Syntactic/Semantic/Pragmatic/Planning | Metric threshold violations |
| **Who uses it** | Research community | Developers + CI/CD |
| **Interface** | MCP server (Factorio ↔ Claude Code) | MCP server (DeepEval ↔ IDE) |

### Hermes 可以借用的 pattern

1. **Error taxonomy 映射到 heartbeat severity**：
   - FLE Syntactic → `hermes cron list` breaks（立即 critical）
   - FLE Semantic → API misuse → medium severity
   - FLE Pragmatic → wrong context → low severity
   - FLE Planning → wrong strategy → escalate if persistent

2. **Holdout period for escalation**：
   - 同一 fingerprint 連續錯誤 → 60s holdout → 才升級
   - 這比「連續 3 次就升級」更嚴謹

3. **DeepEval 的 MCP metrics**：
   - MCP task completion = Hermes MCP server 的 tool 成功與否
   - 可直接用來測 WS-022 的 hermes-mcp server 是否正常

4. **Trace observability**：
   - DeepEval `@observe()` pattern = Hermes 需要在 tool call 層加 structured span
   - WS-018 的 JSONL 無法解析 tool_call metadata → 解決方案：加 span layer

---

## 未追蹤 Leads

- https://jackhopkins.github.io/factorio-learning-environment/versions/0.3.0.html — FLE 0.3 full technical paper
- https://deepeval.com/docs/metrics-mcp-task-completion — MCP task completion metric 詳細文件
- https://github.com/confident-ai/confident-mcp-server — DeepEval MCP server 原始碼
- https://discord.com/invite/3SEyvpgu2f — DeepEval community (有 LLM eval 討論)

## ✅ 本次探索完成

