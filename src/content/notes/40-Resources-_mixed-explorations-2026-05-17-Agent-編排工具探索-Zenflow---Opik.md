---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Agent-編排工具探索-Zenflow---Opik
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Agent-編排工具探索-Zenflow---Opik.md
title: Agent 編排工具探索：Zenflow + Opik
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- evaluation
- gate
- heartbeat
- hermes
- llm
- opik
- pytest
- review
- zenflow
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Agent 編排工具探索：Zenflow + Opik

**日期**: 2026-05-17 | **來源**: HN (Zenflow 46290617, Opik 41567192)
**標籤**: #agent-orchestration #evaluation #observability #multi-agent

## Per-Source Insights

### 1. Zenflow (Zencoder) — Agent Orchestration Without "You're Right" Loops

**來源**: https://zencoder.ai/zenflow (33 pts, 33 comments)
⚠️ 頁面 JS-heavy，curl 淨化後只保留 FAQ 區塊。以下從 FAQ + HN 評論重建。

**核心定位**: AI-first engineering platform — 不是 IDE plugin，是獨立 app。workflow 層的 agent orchestration。

**架構特點**:
- **Zenflow（大腦） + Zencoder（引擎）分離**：Zenflow 決定做什麼、依什麼順序、如何驗證；Zencoder 做實際 coding
- **Spec-Driven Workflows**: agent 先讀 spec/PRD，再實作。Implementation locked to requirements
- **RED/GREEN/VERIFY 循環**：寫 code → 跑 test → agent review → 過關才 ship
- **Cross-Agent Review**: 一個 agent 寫、另一個 agent（不同 model provider）review、第三個 audit security
- **Parallel Execution**: 多 agent 在隔離 worktree 並行，不影響主 codebase
- **Model-Agnostic**: 自帶 Zencoder models 或 bring your own API keys，同 workflow 內可混用 providers
- **100+ MCP 整合**: GitHub, Jira, Linear, Sentry, Datadog, CircleCI
- **Scheduled Automation**: webhook / PR event / Jira ticket update 觸發

**HN 社群反應**（mixed）:
- 正面：無痛跑 SDD workflow、自動 worktree+branch+commit+PR、快修 workflow 實用
- 負面：疑似 astroturf（deaux 指出 100% 正面評論+新帳號/低活躍老帳號）
- 限制：無 Linux 版本（`intuxikated`）
- 價格疑慮：premium LLM calls 的定義不清楚
- 有趣連結：`redhale` 提到 "Ralph Wiggum" continuous loop pattern (https://paddo.dev/blog/ralph-wiggum-autonomous-loops/) — 一種讓 agent 無限循環自我修正的模式

**Hermes 啟發**:
1. **RED/GREEN/VERIFY gate 概念可以移植**：Heartbeat EVOLVE 已經有 pytest canary，但沒有結構化的「改 code → 跑 test → review → 才合併」的 gate。想像一個 `hermes self-repair` 指令：pytest canary → 嘗試修 → 跑 pytest canary → 通過才 commit。
2. **Worktree isolation 已在用**：`worktree-subagent-isolation` skill。Zenflow 的設計確認了這個方向的價值。
3. **Cross-agent review 的窮人版**：Hermes 可以在 delegate_task 完成後，開第二個 subagent 用不同 system prompt（或不同 model）review 結果。目前只有單一 agent 自我 review。
4. **"You're right" loop 是普遍痛點**：Zenflow 以此作為核心 value prop，證實了 multi-agent 協調中 echo chamber 的真實性。

### 2. Opik (Comet ML) — Open-Source AI Observability & Evaluation

**來源**: https://github.com/comet-ml/opik (86 pts, 15 comments) — README 極其詳細

**核心定位**: 開源 LLM observability + evaluation + optimization 平台。從 prototype 到 production 的完整生命週期。

**關鍵能力**:
- **Tracing**: 深度追蹤 LLM calls、conversation logs、agent activity。支援 40+ 框架原生整合（Google ADK, Autogen, LangChain, CrewAI, DSPy, OpenAI Agents SDK...）
- **Evaluation**: LLM-as-a-judge metrics（hallucination detection, moderation, RAG assessment）、Datasets + Experiments 管理、CI/CD PyTest 整合
- **Production Monitoring**: 40M+ traces/day 設計、online evaluation rules、dashboard
- **Agent Optimizer**: 自動優化 prompts 和 tools 的專用 SDK
- **Guardrails**: 安全與責任 AI 功能
- **部署**: Docker Compose（`./opik.sh`）、Kubernetes Helm、Comet.com Cloud

**整合生態**（選錄）:
| 類別 | 整合 |
|---|---|
| Agent frameworks | ADK, Autogen, CrewAI, LangGraph, OpenAI Agents, PydanticAI, Smolagents |
| LLM providers | OpenAI, Anthropic, DeepSeek, Gemini, Mistral, Groq, Together AI |
| Orchestration | Dify, Langflow, Flowise AI, n8n, LiveKit Agents |
| Evaluation | Ragas, Harbor, Guardrails AI |

**Hermes 啟發**:
1. **Heartbeat 已有 tracing（token count, session count）但沒有 span-level 詳細度**：Opik 的 trace 包含每個 LLM call 的 input/output/timing。Hermes 目前只有 aggregate stats。如果要做 self-eval，需要更細粒度的 trace。
2. **LLM-as-a-judge for heartbeat errors**：Hermes heartbeat EVOLVE 的分類是 regex-based。Opik 的 hallucination detection metric 用 LLM 評估 — Hermes 可以用類似方法評估「這次的心跳決策是否合理？」
3. **PyTest 整合是 CI/CD 的最小可行路徑**：Opik 有 `pytest` integration。Hermes 的 `test_heartbeat_v2.py` 已經是 pytest-based，可以直接 embedding Opik evaluation 進現有 CI。但引進 Opik 本身是 heavy dependency（需要 Docker Compose 跑 server）。
4. **DeepSeek 有原生整合**：Opik 支援 DeepSeek tracing — 如果 Hermes 要做 self-observability，可以直接 hook 進現有整合。
5. **Agent Optimizer 的靈感**：Opik 的自動 prompt/tool 優化器概念可以用在 Hermes skill 迭代上。心跳發現 error pattern → 建議 skill 修改 → 跑 test 驗證。

## 跨文章 Synthesis

### 多 Agent 編排的共同語言：Workflow → Verify → Gate

Zenflow 和 Opik 都用類似的模式：
- Zenflow: Spec → Implement → Test → Review → Ship（RED/GREEN/VERIFY）
- Opik: Trace → Evaluate → Optimize → Monitor

兩者都在建立 **agent 行為的 quality gate**。Zenflow 在 build-time，Opik 在 runtime。Hermes 的 heartbeat EVOLVE 主要做 runtime health check，但缺少結構化的 quality gate。

### Hermes 可借用的分層模型

```
Opik observability (tracing layer)
          ↓
Zenflow workflow gate (build-time verify)
          ↓
Heartbeat EVOLVE (runtime health check)
```

Hermes 目前的 heartbeat 只有最底層（runtime check）。Opik-level tracing 和 Zenflow-level gating 都是缺失層。

### 可行性評估

- **Opik tracing**：可行但重。需要自架 Docker Compose。適合做 SPIKE 提案。
- **Zenflow-style gate**：輕量。可以在現有 `delegate_task` + `worktree-subagent-isolation` 基礎上加 verify step。不需要外部依賴。
- **Cross-agent review**：最輕量。用不同 model 或不同 system prompt 的 subagent review 結果。今天就可以試。

## 未追蹤

- Ralph Wiggum continuous loop pattern (https://paddo.dev/blog/ralph-wiggum-autonomous-loops/) — HN 評論者提到，可能適合自主修復的 continuous improvement loop
- Opik 的 Agent Optimizer 如何運作（prompt optimization 和 tool optimization 的具體演算法）
- Zenflow 的 cross-model verification 具體 prompt 設計（FAQ 未揭露）
- Opik 的 PyTest integration 實際接法（是否需要 Opik server，還是可以只用 client SDK）

## ✅ 本次探索完成

