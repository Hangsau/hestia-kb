---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索--tool---LLM-Agent-运行时规则执行-DSL
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索--tool---LLM-Agent-运行时规则执行-DSL.md
title: "探索：\tool — LLM Agent 运行时规则执行 DSL"
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- action
- agent
- agents
- check
- enforce
- inspection
- llm
- tool
- trigger
- user
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：\tool — LLM Agent 运行时规则执行 DSL

**日期**: 2026-05-22
**来源**: arxiv/html/2503.18666v3 — ICSE 2026
**类型**: 探索笔记

## Per-Source Insights

### \tool: Customizable Runtime Enforcement for Safe and Reliable LLM Agents (ICSE 2026)

**核心定位**：首个系统性地在运行时对 LLM Agent 执行自定义安全约束的框架。使用 DSL 描述规则，在 Agent action 执行前拦截并强制执行。

**语言设计 — Trigger-Check-Enforce 三段式**：
```
rule @inspect_transfer
trigger Transfer
check
  !is_to_family_member
enforce
  user_inspection
end
```

- **trigger**：触发事件（Agent 拟执行的 action 类型）
- **check**：谓词条件（布尔表达式）
- **enforce**：执行机制（stop / user_inspection / action_invoke / llm_self_examine）

**架构集成**：以 LangChain 为主要示例，拦截 `agent decision pipeline` 在 action 执行前评估规则。框架 agnostic，可适配 AutoGen、Apollo（自动驾驶）等其他生态。

**评估结果**：
- Code agents：阻止 90%+ 不安全代码执行
- Embodied agents：消除 10 类危险操作
- Autonomous vehicles：100% 合规（8 个场景全部通过）
- LLM 自动生成规则（OpenAI o1）：embodied agent precision 95.56%、recall 70.96%；code agent 87.26%；AV 5/8
- 运行时开销：毫秒级（predicate evaluation 约 1-3ms）

**与 Hermes 相关**：
- `\tool` 的 enforce mechanism（user_inspection、llm_self_examine）可对应 Talos governance 的 intervention layer
- Trigger-Check-Enforce 三段式结构清晰，比正则表达更加声明式、可解释
- LLM 自动生成规则的能力（o1 few-shot）说明可以给定 Agent 工具描述 + 风险描述自动产出规则

**局限性**：
- 确定性 checkpoint 强制（非 trajectory-level 预测）
- 依赖预定义 predicate function（需要开发者提供）
- 无概率性安全分析（无法估计"几步后进入危险状态"）

## Hermes 启发

1. **DSL 化 Talos governance rule**：现有 DCG regex pack 或 Docker YAML policy 可以进一步抽象为 Trigger-Check-Enforce 形式，提升可读性和可维护性
2. **user_inspection 对应 Hestia/Talos 双 agent 场景**：当 Talos 无法独立判断时，强制暂停 + 通知 Hestia human review，而非 autonomous continue
3. **llm_self_examine 对应"自省"能力**：Agent 在执行危险 action 前先调用 LLM 反思自身意图，类似 Reflexion 机制

## 跨文章 Synthesis

暂无（本次单篇阅读）。

## 未追踪 Leads

- https://github.com/haoyuwang99/AgentSpec — \tool 官方实现 repo
- https://arxiv.org/abs/2503.18666 — 原始 PDF（需用 abstract 页面）
- Docker Sandboxes: Run Agents in YOLO Mode, Safely | Docker (web search result) — Docker 的 sandbox 方案对比

## ✅ 本次探索完成
