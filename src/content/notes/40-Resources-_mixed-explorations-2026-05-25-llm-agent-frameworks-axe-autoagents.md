---
_slug: 40-Resources-_mixed-explorations-2026-05-25-llm-agent-frameworks-axe-autoagents
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-llm-agent-frameworks-axe-autoagents.md
title: LLM Agent Framework 研究 — Axe 與 AutoAgents
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# LLM Agent Framework 研究 — Axe 與 AutoAgents

**日期**: 2026-05-25 | **探索來源**: HN Algolia (LLM agent memory) | **類型**: 🎲 隨意探索

## Per-Source Insights

### 1. Axe — 12MB binary, CLI tool for single-purpose AI agents (227 pts)
`https://github.com/jrswab/axe`

**核心設計**：
- 定義：用 TOML 設定檔定義 agent，每個 agent 做一件事（Unix philosophy）
- 執行：不是排程器，是 executor——用 cron/git hooks/pipes 觸發
- 無 daemon、無 GUI、無 framework 需 buy-in
- 工具：read_file, write_file, edit_file, list_directory, run_command, url_fetch, web_search, call_agent（sub-agent）
- Sub-agent delegation：可嵌套呼叫其他 axe agents，有 depth limiting（max 5）和 parallel execution
- Memory：timestamped markdown logs，跨 run 持久化；LLM-assisted GC
- 安全：Output allowlist（url_fetch/web_search 主機名白名單）、private IP 永遠 block、SSRF 保護
- Token budget：可設 max_tokens 上限，超過 exit code 4
- Retry：exponential/linear/fixed backoff，只 retry  transient 錯誤（429, 5xx, timeout）
- MCP tool support：SSE 或 streamable-HTTP transport
- Docker 硬化：non-root user (UID 10001)、read-only rootfs、cap_drop: ALL、no-new-privileges:true

**對 Hermes 的啟發**：
- **Executor vs Scheduler 分离**：Axe 是純 executor，排程交給 cron/git hooks。這與 Hermes 架構一致（Hermes 也是 executor，scheduler 是 systemd timer 或 cron）。
- **Sub-agent 嵌套深度限制**（max 5）：Axe 的 `max_depth = 3`（可在 TOML 設到 hard max 5）。這提供了防止無限遞迴的簡單強壯機制。Hermes 的 delegate_task 目前沒有 depth limiting——這是一個潛在的 doom-loop 漏洞。
- **Token budget 強制**：Axe 在 TOML 就能設 budget，超過就停。Hermes 的 cost tracking 是事後記錄，沒有 pre-flight budget check。
- **Memory GC 自動化**：LLM-assisted pattern analysis and trimming——不是等記憶體爆掉才清理，而是主動分析要刪什麼。這比簡單的 sliding window 更聰明。

**不跟進的原因**：
- Axe 是 CLI tool，Hermes 是 agent 系統，定位不同
- 但 sub-agent depth limiting 和 budget enforcement pattern 值得提案

---

### 2. AutoAgents — Rust 生產級多 agent 框架 (654 stars)
`https://github.com/liquidos-ai/AutoAgents`

**核心設計**：
- 語言：Rust（94.4%）+ Python bindings（5.2%）
- 架構：`crates/` 分離：autoagents-core（核心框架）、autoagents-llm（provider 實作）、autoagents-toolkit（工具集）、autoagents-guardrails（護欄）、autoagents-llamacpp、autoagents-mistral-rs 等
- Agent 模型：derive macro (`#[agent(...)]`) 宣告式定義，有 `tools`、`output`、預設行為
- Tool 定義：`#[tool(...)]` + `#[async_trait] impl ToolRuntime`——每個 tool 是獨立的 Rust struct
- Memory：Sliding window memory（`SlidingWindowMemory::new(capacity)`），可插拔 backends
- Executor：ReAct 和 basic 兩種，streaming responses，structured outputs
- WASM sandbox：tool execution 可在 WASM runtime 中隔離執行（untrusted tools）
- LLM Guardrails：LLMLayer guardrail pipeline（input/output Block/Sanitize/Audit）
- LLM Optimization passes：cache + retry， pipeline 形式串聯
- Pub/sub：typed pub/sub，編譯期類型安全，decoupled 架構
- Observability：OpenTelemetry tracing + metrics，pluggable exporters
- 多 provider：OpenAI、OpenRouter、Anthropic、DeepSeek、xAI、Phind、Groq、Google、Azure、Ollama、mistral-rs、llama.cpp

**對 Hermes 的啟發**：
- **WASM sandbox for tool execution**：AutoAgents 的 tool 可跑在 WASM runtime 中，隔離 untrusted code。這對 Talos governance pipeline 有直接價值——目前 DCG 是靜態分析，WASM sandbox 是動態隔離。更強但更重。
- **LLM Layer Guardrails as pipeline**：AutoAgents 的 `LLMLayer`（Guardrails）是一種 middleware，可串在 LLM call 前面做 input/output validation。這與 Prometheus 的 `before_model` hook 概念相似，但 AutoAgents 的實作更完整（Block/Sanitize/Audit 三種政策）。
- **Typed pub/sub**：編譯期安全的 inter-agent 通信，runtime overhead 低。Hermes 目前是 async file-based comms（poll.sh），AutoAgents 的 typed event system 更強。
- **Provider 統一是 interface-based**：所有 LLM provider 實作同一個 trait（`LLMProvider`），新 provider 只要實作這個 interface。這解釋了為何 AutoAgents 能快速支援那麼多 provider——不需改核心。
- **Memory backend 插拔**：SlidingWindowMemory 只是預設，backends 可替換。對 Hermes 的 heartbeat learning distillate 機制有意義——不同的 distillation strategy 可以是不同的 backend。

**有興趣跟進**：
- WASM sandbox tool execution：對 Talos 的 governance enforcement 有價值
- LLM Layer Guardrails pipeline：可對標 Prometheus before_model hook

## 跨文章 Synthesis

**Axe vs AutoAgents 的互補性**：
- Axe：輕量、CLI-first、Unix pipe 整合、single-purpose agent
- AutoAgents：重量級、typed pub/sub、WASM sandbox、production-grade multi-agent

兩者共同趨勢：
1. **Memory 智能化**：從簡單 sliding window → LLM-assisted GC + 可插拔 backends
2. **Tool 安全**：static allowlist（Axe）+ dynamic sandbox（WASM，AutoAgents）
3. **Budget/cost 控制**：exit code 4 token limit（Axe）+ LLM optimization passes（AutoAgents）
4. **Sub-agent 控制**：depth limiting（Axe）+ typed delegation（AutoAgents）

對 Hermes 的實用方向：
- **短期（提案層）**：研究 Hermes 的 delegate_task depth limiting——目前無上限，可能導致 doom-loop
- **中期（提案層）**：WASM sandbox tool execution 的可行性——AutoAgents 已有實作，可直接研究其 code

## 未追蹤 Leads

（純 URL，不加 action 指示）

- https://github.com/liquidos-ai/AutoAgents/blob/main/crates/autoagents-core/src/agent/memory/sliding_window.rs — SlidingWindowMemory 實作
- https://github.com/liquidos-ai/AutoAgents/tree/main/crates/autoagents-wasm-agent — WASM sandbox tool execution
- https://github.com/liquidos-ai/AutoAgents/tree/main/crates/autoagents-guardrails — LLM Layer guardrail pipeline

## ✅ 本次探索完成