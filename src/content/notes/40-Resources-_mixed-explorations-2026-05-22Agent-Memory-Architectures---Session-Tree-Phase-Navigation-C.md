---
_slug: 40-Resources-_mixed-explorations-2026-05-22Agent-Memory-Architectures---Session-Tree-Phase-Navigation-C
_vault_path: 40-Resources/_mixed/explorations/2026-05-22Agent-Memory-Architectures---Session-Tree-Phase-Navigation-C.md
title: Agent Memory Architectures — Session Tree Phase Navigation Context
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- entity
- hermes
- mem
- memory
- multi
- phase
- retrieval
- session
- tree
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# Agent Memory Architectures — Session Tree Phase Navigation Context

**延續自**: [[2026-05-27-chatindex-retrieval-visualize]]

**時間**: 2026-05-28T03:50 CST

## 來源

- Mem0 blog: "State of AI Agent Memory 2026" (April 1, 2026, updated May 19, 2026)
- LoCoMo / LongMemEval / BEAM benchmark frameworks
- Mem0 multi-signal retrieval: semantic + BM25 + entity matching, fused score

---

## 核心發現：Three Memory Types

Mem0 paper (ECAI 2025) 識別出第三種 memory：

| Type | What it stores | Example |
|------|----------------|---------|
| Episodic | what happened | conversation logs |
| Semantic | what is known | facts, preferences |
| **Procedural** | how things should be done | workflows, coding patterns, review conventions |

**Procedural memory** 是目前大多数 memory system 忽略的类型。对 Hermes 的启示：

- `session_phase_tree.py` 目前只做 phase skeleton extraction（episodic）
- 可以扩展为**提取 tool-use patterns**（procedural）——例如「这个 session 的 tool call 序列是否符合某类 workflow pattern」
- 这样 Session Tree 不仅能导航历史，还能识别「这个用户/任务类型偏好什么样的 tool sequence」

---

## Multi-Signal Retrieval：比纯 vector similarity 强在哪

Mem0 2026 新算法用三个信号并行评分：

```python
# Semantic: vector embedding similarity
# BM25: keyword exact match
# Entity: entity extraction + match
# Fused: normalized score combination
```

结果：temporal queries +29.6 pts, multi-hop +23.1 pts。

**对 Hermes MemR³ 的启示**：MemR³ 当前用 BM25 + fact extraction。可以加 entity matching 作为第三信号。BM25 处理「精确关键词匹配」，entity matching 处理「同一实体在不同表述中的匹配」——这正好是 Hermes session 中常见的问题（用户说「那个提案」但从没提过提案名称，entity linking 可以 bridge 这个 gap）。

---

## Multi-Scope Memory：四个 identity scope

每个 memory write 关联至少一个 scope：

- `user_id` — cross-session user facts
- `agent_id` — specific agent instance
- `session_id` / `run_id` — single conversation
- `app_id` / `org_id` — shared org context

这正好映射到 Hermes 的 multi-agent 场景：

- `user_id` ← Hermès user preferences across sessions
- `agent_id` ← Hestia vs Talos agent-specific knowledge
- `session_id` ← per-session conversation tree
- `org_id` ← workspace/project shared context

Session Tree Phase Navigation 可以利用这个 scope model：在 phase tree 里标记每个 node 的 `agent_id`（哪个 agent 产生这段对话），查询时可以按 agent scope 过滤。

---

## Voice Agent 的 Memory Problem

Voice 交互中用户无法 scroll back 或 copy-paste，所以 memory 是「immediate and obvious」的。

对 Hermes TUI 的启示：TUI 也是 text-based，用户可以 scroll back，所以不像 voice 那样急迫。但 TUI 的 `hermes ask` 模式（快速单次交互）和 voice 场景有相似性——快速交互中用户不会主动提供上下文，memory 填充更依赖系统主动回顾。

---

## Open Problems（对 Session Tree 的启示）

1. **Temporal abstraction at scale**: BEAM 1M→10M 掉了 16 点。Session Tree 的 phase skeleton 实际上是一种 temporal abstraction——把连续对话压缩成 phases。如果 phase skeleton 做得好，应该能显著降低长 session 的 retrieval cost。

2. **Memory staleness**: 高检索频率的 memory 可能在用户情况变化后变得「confidently wrong」。Session Tree 面临同样问题——phase tree 一旦建成，如果 session 内容变化（如用户改变了目标），旧的 tree 结构可能误导。需要在 `session_phase_tree.py` 里加 staleness check 或 rebuild trigger。

3. **Cross-session identity resolution**: 「两个 interaction 是否来自同一个人」。对 Session Tree 意味着：不同 session 的 phase tree 如何判断是否描述同一个项目/用户目标？目前没有这个能力。

---

## Session Tree Architecture 强化方向

根据 Mem0 research，Session Tree Phase Navigation 可以强化：

### Layer 1 (Raw): 已有
- `~/.hermes/sessions/<id>.jsonl` — 完整保存

### Layer 2 (Tree): 扩展
当前：phase skeleton（planning/execution/review）
强化方向：
- **Procedural memory layer**: 从 tool call sequence 提取 workflow patterns，标记为 procedural facts
- **Entity linking**: 从 session 提取 entity（proposal name, skill name, cron job name），建立 entity index
- **Agent attribution**: 每个 node 标记 `agent_id`（Hestia/Talos），支持跨 agent 查询

### Layer 3 (Facts): 待建
- Cross-session synthesized knowledge（MemR³ evidence gap convergence）
- 目前只有骨架，facts extraction 未启动

---

## Per-Source Insight

### Mem0 2026 Algorithm
- **What**: Multi-signal retrieval (semantic + BM25 + entity), single-pass ADD-only extraction, entity linking without external graph store
- **Key innovation**: Entity matching as third signal; entity relationships influence ranking but cannot be traversed directly（权衡：不是 full graph interface，但避免了 Neo4j deployment overhead）
- **Benchmark**: 92.5 on LoCoMo, 94.4 on LongMemEval, ~6,900 tokens/query
- **Insight for Hermes**: BM25 + entity matching 可以立即加到 MemR³ retrieval，不需改变 core architecture

### Procedural Memory Concept
- **What**: Third memory type storing workflows, patterns, conventions
- **Gap**: Most memory systems ignore it; tooling still early-stage
- **Insight for Session Tree**: `session_phase_tree.py` 可以从 tool call sequence 提取 procedural facts（不是 conversation topics，而是「这类任务通常用什么 tool sequence」）

### Voice Agent Memory Pattern
- **What**: Async memory writes to avoid blocking voice latency; user_id derived from application auth
- **Insight for Hermes TUI**: `hermes ask` 模式（快速单次）类似 voice——系统需要主动回顾而不是依赖用户提供上下文

---

## 跨文章 Synthesis

Mem0 的 multi-signal retrieval 和 ChatIndex 的 LLM-guided tree navigation 在设计上互补：

- **ChatIndex**: LLM decides which node_path to follow based on tree structure（LLM navigation）
- **Mem0**: Multiple scoring signals fused before ranking（multi-signal fusion）

两者结合 = **Tree-guided multi-signal retrieval**:
1. Tree navigation narrows the scope（不是全文检索，而是沿着 phase structure 找相关 subtree）
2. Within the subtree, multi-signal retrieval finds relevant facts
3. LLM synthesizes from the retrieved facts

这个 design 正好是「Session Tree Phase Navigation」提案的完整 retrieval pipeline 雏形。

---

## 未追蹤

- Mem0 ECAI 2025 paper (arXiv:2504.19413) — Mem0 vs 10 other approaches 的 head-to-head comparison，需要读
- Mem0 OpenMemory MCP — local-first memory layer for dev tools，OpenMemory MCP 对 Hermes 有参考价值（local MCP memory server）

## ✅ 本次探索完成
