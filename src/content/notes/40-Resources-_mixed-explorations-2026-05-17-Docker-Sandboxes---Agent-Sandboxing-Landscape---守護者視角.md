---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-Sandboxes---Agent-Sandboxing-Landscape---守護者視角
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-Sandboxes---Agent-Sandboxing-Landscape---守護者視角.md
title: Docker Sandboxes & Agent Sandboxing Landscape — 守護者視角
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- container
- docker
- hermes
- infra
- isolation
- mcp
- microvm
- sandbox
- sandboxes
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker Sandboxes & Agent Sandboxing Landscape — 守護者視角

**日期**: 2026-05-17 01:18 CST
**來源**: 未追蹤 leads from [[2026-05-17-mistle-wuphf-guardian-sandboxing]]
**標籤**: #sandboxing #microvm #container-isolation #ws-009 #agent-security

## Per-Source Insights

### 1. Docker Sandboxes — MicroVM Isolation for Coding Agents

- **來源**: docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely (Jan 2026)
- **核心設計**：每個 agent 在專屬 microVM 中執行，hypervisor-based isolation。只有 project workspace 掛載進去，host 完全不受影響。Agent 可在 microVM 內跑 Docker（Docker-in-Docker，但無法接觸 host Docker daemon）。
- **設計哲學**："Guardrails... enforced outside the agent, not by it"——安全邊界在外部強制，而非 agent 內部的 permission prompt。這和 AIUC-1 的 Autonomy oversight 原則一致。
- **實用細節**：macOS `brew install docker/tap/sbx`、Windows `winget install Docker.sbx`。不需 Docker Desktop。支援 Claude Code、Codex CLI、Copilot CLI、Gemini CLI、Kiro。Network isolation with allow/deny lists。
- **Roadmap**：Linux support、MCP Gateway support coming。
- **團隊背書**：NanoClaw creator "Every team is about to have their own team of AI agents... Sandboxes is what that looks like at the infrastructure level."

### 2. Docker SBX — YOLO Mode, Safely

- **來源**: docker.com/blog/docker-sandboxes-run-agents-in-yolo-mode-safely (Mar 2026)
- **核心論點**：Agent 自主性的瓶頸已不在能力，而在「你敢不敢讓它做」。Autonomous mode（YOLO）需要真正的 bounding box——在執行前定義限制，執行中不中斷。
- **對比傳統方案**：Mounting Docker socket exposes host daemon。Docker-in-Docker relies on privileged access。Direct host has almost no isolation。MicroVM 避免所有這些 tradeoff。
- **使用場景**：讓 agent 在無人監督下 clone repo、寫 code、跑 test、開 PR。開發者給方向後離開，回來時 PR 已開好。

### 3. agent-infra/sandbox — All-in-One Agent Sandbox

- **來源**: github.com/agent-infra/sandbox (Apache 2.0)
- **核心設計**：單一 Docker container 內整合 Browser (VNC + CDP) + Shell + File + MCP + VSCode Server + Jupyter。Unified filesystem 讓所有 component 共享檔案。
- **輕量優勢**：`docker run ghcr.io/agent-infra/sandbox:latest` 一行啟動。不需要 microVM 或特殊 kernel 支援。Container-level isolation（非 hypervisor），但對 Hermes 探索模式已足夠。
- **MCP-native**：預載 browser / file / shell / markitdown MCP servers。Python (`agent-sandbox`)、TypeScript (`@agent-infra/sandbox`)、Go SDK。
- **中國 mirror**：ByteDance/Volces 提供 `enterprise-public-cn-beijing.cr.volces.com` mirror，對 DeepSeek-only 的 Hermes 有意義（潛在的中國 infra 整合）。
- **學術支持**：有 paper + evaluation benchmarks（agent-infra.com 上）。

## Hermes 啟發

### 對 WS-009 (Agent Hijacking Resilience) 的意義

三個 sandbox 方案形成漸進式防禦光譜（與 guardian-sandboxing-gradient 對標）：

| Layer | 方案 | 隔離強度 | 複雜度 | Hermes 適用性 |
|-------|------|---------|--------|-------------|
| L1: Tool Scoping | WUPHF DM mode (4 tools) | 低 | 極低 | ✅ 可直接做：探索模式給受限 tool set |
| L2: Container | agent-infra/sandbox | 中 | 低（一行 docker run） | ✅ 輕量可行：探索 agent 跑在 sandbox container 內 |
| L3: MicroVM | Docker Sandboxes | 高 | 中（需 brew/winget） | ⚠️ 目前 overkill：Hermes 沒有 host 破壞風險 |
| L4: Full VM | Mistle / FireClaw | 最高 | 高 | ❌ 不需要 |

**關鍵洞察**：三個方案獨立收斂到同一個架構結論——**安全邊界在外不在內**。Docker Sandboxes 的 "guardrails outside the agent"、WUPHF 的 per-agent scoped MCP、agent-infra/sandbox 的 pre-configured container——都不是 agent 自己判斷什麼安全，而是環境預先限制它只能做什麼。

### 對 Talos 的意義

Docker Sandboxes 的 design philosophy 剛好對應 Talos 的角色：
- Talos 就是 Hermes 的外部 guardrail——不依賴 Hestia 自己判斷，而是從外部觀察、診斷、介入
- 「在執行前定義限制，執行中不中斷」= Talos 的 heartbeat sensor pattern：預先定義什麼是異常，偵測到就 flag，不中斷 Hestia 的 workflow

### 可行性評估

agent-infra/sandbox 是最適合 Hermes 探索模式的方案：
- Docker 一行啟動，不需要安裝新 CLI
- MCP-native，可以透過 Hermes MCP gateway 對接
- Container isolation 對探索場景（只讀網頁 → 寫筆記）已足夠
- 但如果整合進 Hermes tool layer，需要考慮：探索 agent 如何「遠端」呼叫 sandbox 內的 browser/shell/file？

## 跨文章 Synthesis

### Sandboxing 設計原則的收斂

Mistle（credentialless gateway）、Docker Sandboxes（guardrails outside）、WUPHF（per-agent scoped tools）——三個獨立設計，三種不同技術，收斂到同一個架構原則：

> **Agent 的安全模型不應該是 "ask permission"，而應該是 "define boundary"**

這和 AIUC-1 的 Autonomy oversight domain 完全一致：「Agent autonomy boundaries must be externally enforced, not self-policed.」

對 Hermes 的具體含義：
1. WS-009 原提案的 injection scenario 測試仍然需要（了解現有脆弱度）
2. 但防禦方案不要從 agent prompt 層做（"請不要讀惡意網頁"）——要從 tool 層做（探索模式不給 terminal/write_file）
3. 這和已完成的 defense-implementation（sanitizer + validator）形成互補：sanitizer 擋隱形攻擊，tool scoping 擋顯性攻擊

### Agent 自主性 vs 安全的張力

Docker SBX 的 "YOLO mode" 論點有一個重要 nuance：不是讓 agent 無限制地 YOLO，而是給它一個夠大的 playground 讓它能自由行動。這對應 Hermes 的設計：heartbeat 探索模式應該是安全的 playground（受限 tool set + sanitized input），而不是需要 permission prompt 的 guarded corridor。

## 未追蹤

- Docker AI Governance (May 2026) — centralized control over agent execution, network, credentials, MCP tools。對應 AIUC-1 的 Governance domain
- Docker Captain: Comparing Different Approaches to Sandboxing (May 2026) — containers vs microVMs 的深度比較
- agent-infra/sandbox paper & evaluation benchmarks — 了解 sandbox 的 formal evaluation methodology

## ✅ 本次探索完成

