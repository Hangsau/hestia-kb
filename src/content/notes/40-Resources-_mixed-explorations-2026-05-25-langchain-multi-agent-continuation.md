---
_slug: 40-Resources-_mixed-explorations-2026-05-25-langchain-multi-agent-continuation
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-langchain-multi-agent-continuation.md
title: 2026-05-25 Topic Continuation — LangChain Multi-Agent Systems
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-05-25 Topic Continuation — LangChain Multi-Agent Systems

**延續自**: [[2026-05-25-multi-agent-governance-blind-spot]]

## Per-Source Insights

### LangChain Blog: How and When to Build Multi-Agent Systems

**核心命題**：Cognition 的「Don't Build Multi-Agents」vs Anthropic 的「How we built our multi-agent research system」——看似矛盾，實则互补。结论是：multi-agent 的边界条件是可以被系统化定义的。

**五大 insight**：

1. **Context engineering 是 #1 挑战**：比模型聪明更重要。Multi-agent 系统中每个 sub-agent 需要精确的 objective + output format + task boundaries。没有精心设计的 context engineering，sub-agents 会重复工作或 misinterpret 任务（Anthropic 真实案例：三个 sub-agent 同时研究半导体，一个研究 2021 汽车芯片危机，两个重复研究当前供应链）。
   → 对应 Waxell 的 delegation depth 问题：context handoff 不做好，sub-agent 的 policy 就失效。

2. **Read-heavy systems 比 write-heavy 好 parallelize**：写操作有隐含决策冲突，并行写代码/内容会产生难以调和的不兼容输出。Anthropic 的 Claude Research 故意让 multi-agent 只处理 research（读），最终 synthesis（写）由单一 agent 一次完成。
   → Hermes/Talos 的 comms 系统偏向 "read"（接收 task description，执行任务），这个设计方向是对的。

3. **Durable execution 是 long-running agent 的必须**：错误会 compound，不能从开头 restart。LangGraph 把这个 built-in。Hermes 的 heartbeat 已经在做持久化状态（heartbeat_state.json），但 agent session 本身的 durable execution 仍依赖 context window。
   → WS-032 procedural memory layer 可以借鉴这个思路：session 被打断时，从 external memory 恢复 state。

4. **Multi-agent 的经济边界**：只有当任务价值 > 多 agent 的额外 token 成本时才值得。Anthropic 明确定义：breadth-first queries + 需要并行追求多个独立方向 + 信息量超单 agent context window。
   → 对 Talos/Hestia 来说：complex research/spike 适合 multi-agent；日常 heartbeat 单 agent 足够。

5. **Tooling 是 generic 的，应该用现成框架**：Durable execution、debugging、observability、evaluation 都是 generic 问题，LangGraph/LangSmith 已解决。Hermes 应该优先集成而非自造。
   → 呼应：NanoClaw 的 SQLite-as-IO 模式 + LangGraph 的 durable execution pattern 可以综合。

---

## Hermes 啟發

**Talos-Hestia 通信的 context engineering 改进**：
- 目前 Talos 收到 Hestia 的 task 只做 existence check，没有验证 context 是否在授权 scope 内
- Waxell 的 delegation boundary policy + LangChain 的 context engineering = 可以在 INBOX 层加 context validation（检查 task description 的 scope 是否匹配 Talos 的 authorization level）

**Hestia 自己何時该启动 sub-agent（而不是自己干）**：
- Threshold 1: 任务需要 breadth-first search（多个独立方向同时探索）
- Threshold 2: 信息量超过当前 context window 50%
- Threshold 3: 任务需要 specialized tool access（Hestia 没有的 capability）
- 当前 Hestia 的 heartbeat cron 几乎全是 self-contained，没有分派过 sub-agent —— 这可能是设计盲点

---

## 跨文章 Synthesis

Waxell + LangChain + 之前的 DCG/OrcBot 研究形成了一条线索：

| 层级 | 核心问题 | 解决方案 |
|------|---------|---------|
| Single agent | Context window limit | Memory layer (WS-032) |
| Delegation boundary | Context scope leakage | Content evaluation at INBOX |
| Multi-agent orchestration | Durable execution | External state + resume |
| Economic threshold | 何时用 multi-agent | Breadth-first + context overflow |

---

## 未追蹤 Leads

- https://blog.langchain.com/agent-observability-needs-feedback-to-power-learning/ — Agent observability needs feedback (2026-05-05)
- https://blog.langchain.com/give-your-agents-an-interpreter/ — Interpreter tool for agents
- https://www.cognition.ai/blog/dont-build-multi-agents — Cognition 的原始反对论点

## ✅ 本次探索完成