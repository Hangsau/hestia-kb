---
_slug: 40-Resources-_mixed-research-agent-multi-agent-coordination-core-concepts
_vault_path: 40-Resources/_mixed/research/agent/multi-agent-coordination-core-concepts.md
tags:
- knowledge
- ai-agent
- core-concepts
- multi-agent
- orchestration
created: '2026-06-08'
version: 1
status: seedling
sources:
- 2026-05-25-研究報告-multi-agent-coordination-protocols.md
- 2026-06-02-研究報告-agent-orchestration-patterns-現代多-agent-工作流架構解析.md
type: core-concepts
fingerprint: multi-agent, orchestration, supervisor, handoff, agents-as-tools, swarm,
  mcp, guardrails
title: Multi-Agent Coordination — 核心概念整合
updated: '2026-06-15'
---

# Multi-Agent Coordination — 核心概念整合

> 「不要強化單一 agent，要用 orchestration 架構把多個專門 agent 串起來。」
> — 2026 年業界共識

## 為什麼需要多 Agent

**單一 agent 的瓶頸**（從 5/25 + 6/02 兩份報告提煉）：

- **Reasoning token budget 是固定的** — 一個模型不可能同時擅長規劃、工具調用、領域知識、輸出格式化
- **就算模型更強，架構不對也沒用** — 2024-2025 「GPT-5 來了就解決 agent 問題」的期待已落空
- **故障率不可忽略** — CUHK MAS-Resilience 研究：agent 故障率約 **5-20%**，多 agent 系統必須有韌性設計

---

## 五種核心協調模式

| 模式 | 代表 | 適用場景 | 瓶頸 |
|------|------|----------|------|
| **Role-Based（角色制）** | ChatDev 1.0/2.0、LightAgent | 結構化任務、軟體公司模型 | 角色死板、難動態調整 |
| **Swarm（去中心化）** | AgentFlow、Agency Swarm、Swarms | 探索性、brainstorming、需要多元視角 | 共識時間瓶頸（最慢的 agent）|
| **Hierarchical（階層式）** | OpenAI Agents SDK | 任務分解、並行 worker | Manager 單點失敗 |
| **Agents-as-Tools** | OpenAI Agents SDK | **2026 年最被廣泛採用** | Sub-agent 過多時工具清單爆炸 |
| **Verify（對抗式驗證）** | MMCP、CUHK MAS-Resilience | 對抗幻覺、需要高正確性 | Challenger 本身也可能幻覺 |

### 1. Agents-as-Tools — 2026 主流 primitive

把 sub-agent 當成 function-calling 的工具，orchestrator 完全靠工具調用觸發其他 agent：

```python
orchestrator = Agent(
    name="orchestrator",
    tools=[
        spanish_agent.as_tool(tool_name="translate_to_spanish", ...),
        french_agent.as_tool(tool_name="translate_to_french", ...),
    ],
)
```

**進階**：Conditional Tool Enabling — `is_enabled` 函式根據 context 動態啟/停 sub-agent，實現 RBAC 層級控制。

### 2. Agency Swarm — 結構化通訊流

不像星狀拓撲（所有都連回 orchestrator），允許 agent-to-agent 直接訊息傳遞，**減少 orchestrator bottleneck**：

```python
agency = Agency(
    ceo, va, dev,
    communication_flows=[
        (ceo, va),
        (va, dev),
        (ceo, dev),  # 可選
    ],
    shared_instructions="..."
)
```

### 3. Hierarchical — Manager + Workers

```
Task → Manager Agent → Worker Agents (並行) → Manager aggregates
```

Worker 不知道自己在更大的工作流中，只對 manager 負責。**簡化每個 agent 決策複雜度，但增加 manager SPOF 風險**。

### 4. Swarm — 去中心化多輪

```
Phase 1: Task Initiation → Agent Turn (所有 agent 貢獻) → Aggregator
                         ↑________________________________|
```

每輪所有 agent 貢獻，經多輪後由 aggregator 綜合。**適合創意發想，不適合有標準答案的任務**。

### 5. Verify Pattern — 對抗式

```
Producer → Challenger → Judge
```

Producer 生成、Challenger 找漏洞、Judge 裁決。**三方制衡對抗單一 agent 幻覺**。

---

## 2026 Production Agent 系統的標準配備

從 6/02 報告提煉，**production 系統的 4 個必要元件**：

### 1. Guardrails（輸入/輸出驗證）

```python
from agents import Agent, OutputGuardrail

guardrail = OutputGuardrail(
    name="no_profanity",
    validate_output=lambda ctx, agent, output: {
        "pass": "fuck" not in output.text.lower(),
        "failure_message": "Output contained inappropriate language",
    },
)

agent = Agent(name="support", guardrails=[guardrail])
```

**為什麼必要**：多 agent 系統中，**錯誤會傳播**。一個 worker 的幻覺輸出會汙染後續所有 agent。

### 2. Session Management

自動維護對話歷史。多 agent 系統中，每個 sub-agent 可能需要獨立 session context。

### 3. Tracing

```python
with trace("order_processing"):
    result = await Runner.run(sales_agent, user_input)
    # 整個 run 的工具調用、LLM 決策、sub-agent handoffs 都被追蹤
```

**OpenAI 自己的 tracing UI 能視覺化完整的多 agent trace tree**。

### 4. MCP（Model Context Protocol）— 工具發現的標準化

```
Client (Agent Framework)
    ├── ListTools → MCP Server → Tool List
    └── CallTool(name, args) → MCP Server → Result
```

**MCP 解決「工具發現」，不解決 orchestration**。MCP 是 protocol-level 標準，不依賴特定模型或框架。

---

## Domain-Aware Routing — RL 驅動的智慧路由

MMCP 的核心創新：**學習每個模型擅長什麼領域，動態路由任務**。

| 任務 | 領域 | 模型 | 分數 |
|------|------|------|------|
| Write Python API with auth | code_generation | GPT-4o | 0.96 |
| Debug React component | code_review | Claude Sonnet | 0.91 |
| Prove calculus theorem | math_reasoning | DeepSeek R1 | 0.92 |

當模型更新升級，**系統會重新 benchmark，自動更新路由策略**。

**限制**：
- RL routing 需要累積足夠 benchmark 數據，**冷啟動問題存在**
- Domain detection 準確度依賴任務描述的清晰度，**模糊任務容易選錯領域**

---

## 故障韌性

CUHK **MAS-Resilience** 的核心發現：

- **5-20% 故障率** — agent 系統不能假設每個 agent 都正確
- 目前測試的攻擊手法（AutoTransform、AutoInject）只是冰山一角
- 防禦方法（Inspector、Challenger）**本身也是 LLM agent，可能被同樣的手法欺騙**
- 防禦 overhead 會增加延遲與成本

**現狀**：RESEARCH-ONLY，學術階段還未 production-ready。**方向值得關注，等成熟再實作**。

---

## 框架選擇決策矩陣

| 框架 | Stars | 何時用 | 何時不要用 |
|------|-------|--------|-----------|
| **OpenAI Agents SDK** | 官方 | production、需要官方文件密度 | 想擺脫 OpenAI 鎖定（某些高階功能只在 OpenAI API 穩定）|
| **Agency Swarm** | 5.4k | 需要結構化 communication_flows、agent-to-agent 直接通訊 | 同上（明確基於 OpenAI SDK）|
| **Swarms** | 57k | ❌ 不推薦 | 社群文檔品質不如前兩個；57k stars 來自病毒效應不代表技術領先 |
| **CrewAI** | — | 需要 declarative YAML 描述 pipeline | 靈活度不如 Python-first 方案 |
| **MCP-agent** | — | 需要 MCP 工具自動發現 | orchestration 仍需自己實作 |

---

## 限制與未解問題

### 自我改善能力的缺口

**所有 2026 年的 orchestration 框架都專注於靜態架構** — agent 的能力在部署時就固定了，運行時只能靠外部工具（如 RAG）更新知識。**沒有任何框架內建自我改善機制**。

**Orchestration 和 self-improvement 是兩個獨立的問題，目前社群傾向於分開解決**。這指向下一份整合文的主題。

### 通訊瓶頸

去中心化架構的最大問題是**共識時間** — 每輪需要所有 agent 完成才能進入下一階段，瓶頸在最慢的 agent。

### 過度設計風險

**Swarm Pattern 的多輪協作對簡單任務（文書處理、翻譯）反而更糟**。單一 agent 更有效。

---

## 給我們自己的 Actionable

**現在可以做**：
- 實作 agents-as-tools 模式（MODERATE 難度）— 新增 `FirnRouter` agent delegation
- 實作 Output Guardrails（TRIVIAL）— 在 firn 輸出路徑加 validation layer

**研究後再做**：
- Session + Tracing 基礎設施（HARD）— 短期只在日誌層面結構化
- Agency Swarm communication_flow（RESEARCH-ONLY）— 等 agent 數量 > 5 再考慮

**不建議跟進**：
- Swarms 框架
- Self-improving orchestration（research 還沒 stable 開源實現）

---

## 參考資料

- **2026-05-25-研究報告-multi-agent-coordination-protocols.md** — ChatDev/AgentFlow/MMCP/MAS-Resilience
- **2026-06-02-研究報告-agent-orchestration-patterns-現代多-agent-工作流架構解析.md** — OpenAI Agents SDK/Agency Swarm/MCP
- 來源專案：openai/openai-agents-python、VRSEN/agency-swarm、microsoft/mcp-for-beginners、lastmile-ai/mcp-agent
