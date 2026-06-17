---
_slug: 40-Resources-_mixed-explorations-2026-06-02-2026-06-02-Agent-Memory-Architecture---Three-Layer-Compositi
_vault_path: 40-Resources/_mixed/explorations/2026-06-02-2026-06-02-Agent-Memory-Architecture---Three-Layer-Compositi.md
title: 2026-06-02 Agent Memory Architecture — Three-Layer Composition + Governance
  Gap
date: 2026-06-02
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- architecture
- atlan
- context
- gap
- layer
- memory
- multi
- retrieval
- vector
created: '2026-06-02'
updated: '2026-06-15'
status: budding
---

# 2026-06-02 Agent Memory Architecture — Three-Layer Composition + Governance Gap

**延續自**: (none — fresh topic from Atlan enterprise article)

## Sources

### Source 1: Atlan — Agentic AI Memory vs Vector Database (2026-04-14)

**URL**: https://atlan.com/know/agentic-ai-memory-vs-vector-database/

**Key findings**:

1. **Three-layer production architecture** (confirmed across 2026 research):
   - **Episodic memory**: conversation history + session context → vector database handles well
   - **Semantic memory**: accumulated entity/relationship knowledge → requires graph structure (flat vector cannot multi-hop)
   - **State memory**: in-flight agent working memory → requires transactional guarantees (similarity search is wrong mechanism)

2. **Vector databases are necessary but insufficient**: They solve "what is similar?" not "what is still true?". Three failure modes at scale: latency (200-500ms per query before LLM), corpus growth degrades recall, consistency gap when concurrent agents write conflicting updates.

3. **Enterprise governance gap** (all 8 memory frameworks evaluated):
   - No business glossary for consistent entity resolution
   - No lineage to trace fact origin
   - No freshness scoring to discard stale context before it corrupts retrieval
   - "Memory frameworks are built to store and retrieve, not to govern" — directly maps to heartbeat_learning.py drift penalty gap

4. **Multi-agent transactional semantics**: When two agents write conflicting updates to the same vector store concurrently, neither knows about the conflict. Oracle Unified Memory Core built specifically to address this with vector+graph+JSON+relational in one engine.

5. **Atlan's context layer operates one level below memory**: active metadata refreshes context as underlying data changes; context graph maintains semantic relationships; policy enforcement scopes retention per tenant/role. This is the "governed memory inputs" argument — retrieval quality improves not because the retrieval mechanism changed, but because the inputs are trustworthy.

**Per-source insight**:
The Atlan article articulates the architecture consensus that Synix/Graphiti source analysis found from a different angle. Synix identified that all 8 systems implement "memory as fact retrieval" — the same gap Atlan calls "built to store and retrieve, not to govern." The three-layer model (episodic/semantic/state) maps to Mem0's dual-store + Zep's Graphiti temporal graph — both already in the exploration notes. What Atlan adds is the enterprise governance framing and the explicit recognition that the consolidation ceiling (vector store grows → noise grows → nothing consolidates or prunes) is not a retrieval problem, it's a data quality problem.

**Hermes启发**: heartbeat_learning.py's drift penalty should focus on retrieval-layer staleness + consolidation, not decay (confirmed by Synix). The Atlan framing suggests WS-035 should explicitly model "trusted context inputs" as a first-class requirement, not just embedding retrieval. The multi-agent consistency gap (conflicting writes) is a separate concern from staleness — suggests two distinct penalty mechanisms: (1) staleness/confidence decay for single-agent, (2) consistency validation for multi-agent shared memory.

---

## ✅ 本次探索完成

## 未追蹤 leads

- https://pub.towardsai.net/ai-agent-memory-architecture-how-to-build-long-term-memory-that-does-not-rot-f77fe66e7448 — Towards AI long-term memory lifecycle
- https://atlan.com/know/agentic-ai-memory-vs-vector-database/ — Atlan enterprise governance (primary source, fully read)
- https://www.sciencx.com/2026/03/28/designing-memory-for-20-ai-agents-across-9-nodes-multi-agent-memory-architecture/ — Multi-agent distributed memory design (20 agents, 9 nodes)
- https://www.academia.edu/167690760/Serenity_Research_Paper_v — Serenity S.E.R.A bitemporal/causal memory research
