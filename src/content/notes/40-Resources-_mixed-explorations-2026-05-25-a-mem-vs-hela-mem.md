---
_slug: 40-Resources-_mixed-explorations-2026-05-25-a-mem-vs-hela-mem
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-a-mem-vs-hela-mem.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 38:\n     ... : 2026-05-25 — A-Mem vs HeLa-Mem: Two Architectures for\
  \ Agent Memory\n                                         ^"
_raw_fm: '

  title: 2026-05-25 — A-Mem vs HeLa-Mem: Two Architectures for Agent Memory

  created: 2026-05-25

  updated: 2026-06-15

  type: exploration

  tags: []

  status: active

  '
title: '2026-05-25 — A-Mem vs HeLa-Mem: Two Architectures for Agent Memory'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# 2026-05-25 — A-Mem vs HeLa-Mem: Two Architectures for Agent Memory

**延續自**: [[2026-05-25-llm-agent-memory-architecture]]

---

## Source: A-Mem (NeurIPS 2025) README + API probe

**URL**: https://github.com/WujiangXu/A-mem | Stars: 892 | Lang: Python
**Paper**: arXiv:2502.12110

### TL;DR (from README)

A-Mem = **Zettelkasten-style note network** for LLM agents:
- Dynamic memory organization based on Zettelkasten principles
- Intelligent indexing and linking of memories
- Note generation with structured attributes
- Interconnected knowledge networks
- **Agent-driven decision making** for adaptive memory management (agent decides when/how to organize)

**Key architectural difference from HeLa-Mem**:

| Aspect | A-Mem | HeLa-Mem |
|--------|-------|----------|
| Memory model | Static notes + explicit links (Zettelkasten) | Dynamic graph with weighted edges (Hebbian) |
| Update trigger | Agent-driven decision (explicit `add_memory` call) | Automatic on co-activation (Hebbian formula) |
| Retrieval | Semantic similarity + explicit note references | Dual-pathway: semantic + spreading activation |
| Consolidation | Agent decides when to organize | Automatic hub-detection + cluster synthesis |
| Token cost | Medium | Fewest (per LoCoMo results) |

### Comparative Insight for WS-032

Both papers address **procedural memory for agents** but from opposite ends:
- **HeLa-Mem**: Lower-level — automatic Hebbian weight updates, biological inspiration, lowest token cost
- **A-Mem**: Higher-level — agent has explicit control over memory organization, Zettelkasten links as first-class citizens

**Synthesis for Hermes**:
WS-032's procedural memory layer could take a hybrid approach:
1. **A-Mem's explicit control** → agent can trigger consolidation (like `add_memory` decision)
2. **HeLa-Mem's automatic spreading** → background Hebbian updates between memory nodes

This means: agents get explicit `remember_this()` and `forget_this()` operations (A-Mem style), while the system auto-updates association weights between memories (HeLa-Mem style). Token cost is managed by having the automatic updates run in the background.

**Concrete for heartbeat_learning.py**:
- Current: distillate extracts patterns as facts
- WS-032 procedural layer could add: agent-callable memory ops + Hebbian weight maintenance
- A-Mem's `note generation with structured attributes` maps to what a `**PROCEDURAL**: remember this pattern` marker could trigger

### API/Architecture Probe

```
org: WujiangXu
repo: A-mem
default_branch: main
stars: 892
forks: 92
paper: 2502.12110
sys_repo: A-mem-sys (official implementation for production use)
```

The official implementation is at `A-mem-sys` (separate repo), not `A-mem`. This is the research code repo.

---

## Untracked Leads

1. https://github.com/WujiangXu/A-mem-sys — official production implementation of A-Mem
2. A-Mem paper (arXiv:2502.12110) — full evaluation methodology on LoCoMo
3. HeLa-Mem's implementation (from ACL 2026 paper) — needs arXiv ID search

## ✅ 本次探索完成