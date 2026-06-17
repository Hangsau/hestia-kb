---
_slug: 40-Resources-_mixed-explorations-2026-05-28-agentmemory---Persistent-Memory-for-Coding-Agents
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-agentmemory---Persistent-Memory-for-Coding-Agents.md
title: agentmemory — Persistent Memory for Coding Agents
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agentmemory
- com
- github
- hermes
- mcp
- memory
- rohitg
- talos
- tier
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# agentmemory — Persistent Memory for Coding Agents

**延續自**: (new exploration)

**日期**: 2026-05-28

## Per-Source Insights

### Source 1: github.com/rohitg00/agentmemory (18.9k ⭐)

**核心機制**：
- 12 hooks 自動捕獲（SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop, SessionEnd, SubagentStart/Stop）
- 4-tier memory consolidation: Working → Episodic → Semantic → Procedural（Ebbinghaus decay）
- Hybrid search: BM25 + Vector + Knowledge Graph，RRF fusion (k=60)
- 92% token reduction：~1,900 tokens/session vs 22K+ for built-in CLAUDE.md

**Hermes 整合方式**：
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
memory:
  provider: agentmemory
```
另有 deeper 6-hook integration：copy `integrations/hermes` → `~/.hermes/plugins/agentmemory`

**價格架構**：
- Local embeddings (all-MiniLM-L6-v2): free, no API key
- DeepSeek V4-Pro compression: ~$0.46/month for typical workload
- 95.2% R@5 on LongMemEval-S

**多 agent 支援**：
- AGENT_ID tags every write
- AGENTMEMORY_AGENT_SCOPE=isolated → strict role separation
- TEAM_ID/USER_ID for team memory

**與 Talos 相關的發現**：
1. Security surface：agentmemory 是 guardian 的記憶層 — 它能記住什麼、誰能讀、什麼時候蒸發，這直接影響 Talos 的判斷依據
2. Memory tier 架構（Working/Episodic/Semantic/Procedural）與 YantrikDB/Mem0 收斂到同一設計原則，印證「結構化記憶 > 純嵌入檢索」
3. Multi-agent isolation：AGENT_ID scoping 是 Talos 和 Hestia 共享同一 server 時的候選方案

**未追蹤 leads**：
- https://github.com/rohitg00/agentmemory/blob/main/DESIGN.md — 架構決策文件
- https://github.com/rohitg00/agentmemory/blob/main/GOVERNANCE.md — 多 agent 協調模式
- https://www.agent-memory.dev/ — product site（未 fetch）

## Hermes 啟發

1. **Talos 的 memory 瓶頸**：現有 heartbeat_learning.py 的 distillate 有 semantic drift（與前期結論相悖），原因是缺少 retention stability objective。agentmemory 的 Ebbinghaus decay + importance eviction 可能提供 explicit penalty mechanism。

2. **壓縮成本**：agentmemory 用 DeepSeek V4-Pro 做 compression，成本 $0.46/month vs $500 for LLM-summarized approach。適用於 Talos 的被動觀察壓縮。

3. **MCP 整合路徑**：Hermes 已有 MCP support，agentmemory 的 53-tool MCP surface 可直接引入，不需要 plugin 层。短期內可先用 MCP shim 評估，長期再考慮 deep hook integration。

## 跨文章 Synthesis

三個獨立系統（agentmemory、YantrikDB、Mem0）收斂到同一個結論：**結構化記憶（tiered consolidation + decay + explicit importance）優於純嵌入檢索**。共同的失敗模式：把所有東西塞進 vector store，沒有分層、沒有衰減、沒有矛盾偵測。agentmemory 的 4-tier + Ebbinghaus curve 是目前最完整的實作；YantrikDB 的程序記憶（技能）分離是補充；Mem0 的 ADD-only 設計防止過度蒸發。三者合起來是一個完整的 memory architecture blueprint。

## ✅ 本次探索完成
