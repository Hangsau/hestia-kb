---
_slug: 40-Resources-_mixed-explorations-2026-05-22-LLM-Agent-Evaluation---DeepEval---Factorio-Learning-Environm
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-LLM-Agent-Evaluation---DeepEval---Factorio-Learning-Environm.md
title: LLM Agent Evaluation — DeepEval + Factorio Learning Environment
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- deepeval
- environment
- eval
- factorio
- heartbeat
- llm
- mcp
- output
- test
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# LLM Agent Evaluation — DeepEval + Factorio Learning Environment

**延續自**: [[2026-05-25-LLM-Agent-Evaluation---Agent-Observability-Landscape]]

**日期**: 2026-05-22

## Source 1: DeepEval (confident-ai/deepeval) — GitHub README

**URL**: https://github.com/confident-ai/deepeval  
**Stars**: ⭐ 15.6k | Python ≥ 3.9 | Apache-2.0

### 核心功能

**G-Eval**（LLM-as-judge）:
- 自然語言 criteria + LLM-as-judge，取代固定 threshold
- `criteria="Determine if the 'actual output' is correct..."`
- `evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT]`
- threshold=0.5 決定 pass/fail；score 0-1 連續

**Agentic Metrics**（直接對應 WS-024 heartbeat rubric 方向）:
- `TaskCompletion` — 評估 agent 是否完成目標
- `Tool Correctness` — 檢查工具是否用對
- `Goal Accuracy` — 測量目標達成準確度
- `Step Efficiency` — 評估是否有不必要步驟
- `Plan Adherence` — 檢查是否遵循預期 plan
- `Plan Quality` — 評估 plan 品質

**MCP Metrics**（新增 2026-05）:
- `MCP Task Completion` — MCP-based agent 任務完成度
- `MCP Use` — agent 使用 MCP server 的有效性
- `Multi-Turn MCP Use` — 跨對話輪的 MCP 使用評估

**Framework Integrations**:
- OpenAI Agents, CrewAI, LangGraph, Pydantic AI, Anthropic, LlamaIndex, Google ADK, Strands
- AWS AgentCore（驗證 WS-022 MCP server 方向）

### 安裝與使用

```bash
pip install -U deepeval
deepeval login  # optional, for cloud dashboard
```

```python
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

def test_heartbeat_action_quality():
    correctness_metric = GEval(
        name="Action Quality",
        criteria="Evaluate if the heartbeat action follows best practices...",
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT
        ],
        threshold=0.5
    )
    test_case = LLMTestCase(
        input="heartbeat action: EVOLVE with no errors",
        actual_output="EVOLVE: 15 steps",
        expected_output="EVOLVE: N steps (clean, no critical/warning)"
    )
    assert_test(test_case, [correctness_metric])
```

### 追蹤整合

```python
from deepeval.tracing import observe, update_current_span

@observe()
def heartbeat_cycle():
    result = run_heartbeat()
    update_current_span(
        test_case=LLMTestCase(
            input="heartbeat cycle",
            actual_output=result
        )
    )
    return result
```

## Source 2: Factorio Learning Environment

**URL**: https://jackhopkins.github.io/factorio-learning-environment/  
**HN**: 749 pts, 209 comments, MCP support

Jack Hopkins (Cambridge, MPhil Advanced CS) 的項目。用 Factorio 遊戲評估 LLM agent——無界任務環境，測試 automation + exponential resource production。

personal page 上有「Factorio Learning Environment」描述：  
> "An open-ended agent environment for evaluating LLMs in unbounded scenarios in Factorio, a game centered on automation and exponential resource production."

GitHub README 404（可能 default branch 問題）。已驗證專案存在（personal site + HN）。

## 對 Hermes 的具體啟發

### 1. WS-024 G-Eval 整合路徑（明確了）

DeepEval 的 `GEval` 是 WS-024 的首選實作：
- 不需要自己設計 fixed threshold
- criteria 寫成 natural language → LLM judge 評估
- `TaskCompletion` / `Step Efficiency` / `Plan Adherence` 直接映射到 heartbeat action quality
- 15.6k stars 是 production-ready 的信號

**具體整合方式**：
1. `pip install -U deepeval`（或 `uvx --from "deepeval"`）
2. 在 `heartbeat/rubric.py` 加入 `GEval` 呼叫
3. `heartbeat_learning.py` 的 `main()` 中 `@observe()` 包住 cycle
4. 用 `deepeval test run` 跑 evaluation suite

### 2. MCP Metrics 驗證了 WS-022 方向

DeepEval 的 `MCP Task Completion` / `MCP Use` metrics 確認：
- MCP server 是 agent 生態系的標準
- Hermes-as-MCP-server 是正確方向
- 可用 DeepEval 的 MCP metrics 測試 `hermes_mcp_server.py` 的功能

### 3. Factorio = Agent Eval 的 benchmark 方向

749 pts + MCP support + game environment：
- 遊戲是封閉但複雜的 eval 環境（自動化、資源生產）
- 類似地，heartbeat 的 eval 可以用「修復系統問題成功率」當 metric
- 可考慮建立 heartbeat 的 Factorio-style benchmark：故意 inject 錯誤，看 heartbeat 能否修復

### 4. Framework Integration Landscape

DeepEval 支援幾乎所有主流 agent framework：
- `OpenAI Agents`（Codex）、`CrewAI`（multi-agent）、`Pydantic AI`（type-safe）
- 這代表 DeepEval 的 metric 設計是經過實戰驗證的
- 我們的 heartbeat action scoring 可以直接借用這些 metric 的 criteria

## 跨文章 Synthesis

DeepEval + Factorio 共同指向：**agent evaluation 需要分層 metric（從 Task Completion 到 Plan Quality）+ framework-agnostic scoring**。

| 維度 | DeepEval | Factorio |
|---|---|---|
| Eval type | G-Eval (LLM judge) | Environment (game state) |
| Metric focus | Agentic quality (task, tool, plan) | Emergent behavior (automation) |
| Framework | Framework-agnostic | N/A |
| MCP support | ✅ Native | ✅ MCP server |
| Stars/Pts | 15.6k | 749 HN |

兩者都是 WS-024 實作方向的驗證：
- DeepEval 提供 G-Eval 框架
- Factorio 提供 MCP eval 的實例
- Together → heartbeat rubric 可以用 DeepEval G-Eval scoring action quality

## Untracked Leads（純 URL）

- https://github.com/confident-ai/deepeval — 完整原始碼（含 metrics 實作）
- https://www.confident-ai.com/ — MCP server for IDE integration
- https://jackhopkins.github.io/factorio-learning-environment/ — 官網（README 404，需從這裡進入）

## ✅ 本次探索完成

