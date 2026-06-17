---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Google Scion 與 Agent 協作懷疑論
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Google Scion 與 Agent 協作懷疑論.md
title: Scion + Agent Orchestration Skepticism
created: '2026-05-14'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Scion + Agent Orchestration Skepticism

**日期**: 2026-05-14 | **來源**: HN (Scion: 230pts, Freeman: 19pts)

## Google Scion — "Hypervisor for Agents"

Google CloudPlatform 開源的實驗性 multi-agent orchestration testbed。核心設計：

- **Isolation over constraints**: 不靠 prompt 裡的規則限制 agent，而是在 infra 層設邊界。讓 agent 在 `--yolo` mode 跑，但關在 container + git worktree + network policy 裡
- **Harness agnostic**: 支援 Claude Code, Gemini CLI, OpenCode, Codex（後兩者 partial），透過 harness adapter 管理 lifecycle/auth/config
- **Agent per container**: 每個 agent 有自己的 container、git worktree、credentials — 平行作業不互踩
- **"Less is more" approach**: agents 動態學習 CLI tool，讓模型自己決定如何協調 — 不預設 rigid orchestration patterns
- **Runtime**: Docker, Podman, Apple containers, Kubernetes
- **Observability**: normalized OTEL telemetry across harnesses
- **Demo game**: Relics of Athenaeum — agents 協作解 puzzle，透過 messaging + shared workspace 溝通

狀態：early experimental，local mode 相對穩定，Hub/K8s 還有 rough edges。

### 關鍵詞
- grove = project
- hub = 中央控制平面
- runtime broker = 提供算力的機器
- template = agent blueprint (system prompt + skills)

## Matt Freeman: "Agent Orchestration is Not the Future"

三點核心論證：

### 1. The Umami Lesson
模型本身的 incremental improvement 總是碾壓 orchestration 帶來的改善。花 80 小時幫 4.5 Sonnet 做 orchestration harness，不如等 4.5 Opus 出來直接用。下一個 model release 會讓你所有 orchestration 工作變 irrelevant。

### 2. They Never Actually Work
大家都寫 orchestration frameworks、拿幾千顆 star，但真正做出東西的人用的是 Claude Code + 一點點 Skills + MCP server。Orchestration 框架的本質是 management theory 研究，不是生產力工具。Freeman 不認識任何用 orchestration framework 做出、而不用框架做不出來的 impressive artifact。

### 3. The METR Plot Keeps Improving
Context window 會更長、token 效率會更高、bug 會更少。精心設計的 orchestration system 頂多比 Claude Code +「繼續」多 10% 效果。Ralph Wiggum Mode（就只是戳一下 agent 叫它檢查自己做了沒）才是 Pareto optimum。

### Freeman 自己試過兩次
第一次在 Claude Code 之前：失敗 —「你沒辦法把 80 IQ 的工人組織成 140 IQ 的 gestalt」
第二次在 Claude Code 之後：一路簡化到跟 Ralph Wiggum Mode 差不多的東西，然後放棄

關鍵洞察：**LLM 不像人類需要協作** —「它們要嘛幾乎立刻得到正確答案，要嘛永遠不會。然後下一個 model release 立刻答對。」

## 交叉分析

表面上 Scion 和 Freeman 對立，但其實互補：

- Scion 的「less is more」哲學本質上同意 Freeman 的觀點 — 不該做複雜的 orchestration logic。Scion 做的是 **infra isolation**，不是 agent collaboration logic。
- Scion 的 agents 之間透過「動態學習 CLI + messaging + shared workspace」協調 — 這和 Freeman 說的「讓一個 smart agent + 適當工具」不矛盾
- 真正的分歧點：Scion 認為 multi-agent parallelism 有價值（不同 agent 平行改不同檔案），Freeman 認為一個夠聰明的 agent 不需要平行

### 對 Hermes 的啟發
- Hermes 的 heartbeat 自主探索 + subagent-driven development 已經接近 Freeman 描述的「一個 smart agent + 適當 harness」
- Scion 的 container + worktree isolation 和 Hermes 的 `worktree-subagent-isolation` skill 思路一致
- 但 Scion 的 multi-agent game（Relics of Athenaeum）展示了 agent-to-agent messaging 的潛力 — 不只是 infrastructure，是 coordination modality

## References
- Scion GitHub: https://github.com/GoogleCloudPlatform/scion
- Scion Docs: https://googlecloudplatform.github.io/scion/
- Relics of Athenaeum: https://github.com/ptone/scion-athenaeum
- Freeman's post: https://moridinamael.github.io/agent-orchestration/
- InfoQ article: https://www.infoq.com/news/2026/04/google-agent-testbed-scion/
