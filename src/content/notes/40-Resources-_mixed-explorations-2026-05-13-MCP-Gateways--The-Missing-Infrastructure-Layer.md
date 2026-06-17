---
_slug: 40-Resources-_mixed-explorations-2026-05-13-MCP-Gateways--The-Missing-Infrastructure-Layer
_vault_path: 40-Resources/_mixed/explorations/2026-05-13-MCP-Gateways--The-Missing-Infrastructure-Layer.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 20:\n    title: MCP Gateways: The Missing Infrastructure Layer\n   \
  \                    ^"
_raw_fm: '

  title: MCP Gateways: The Missing Infrastructure Layer

  date: 2026-05-13

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, agents, api, gateway, gateways, hermes, layer, mcp, servers,
  tool]

  created: 2026-05-13

  updated: 2026-06-15

  status: active

  '
title: 'MCP Gateways: The Missing Infrastructure Layer'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# MCP Gateways: The Missing Infrastructure Layer

**Date**: 2026-05-13  
**Source**: [Composio Blog — "MCP Gateways: A Developer's Guide to AI Agent Architecture in 2026"](https://composio.dev/blog/mcp-gateways-guide)  
**Tags**: mcp, agent-architecture, infrastructure, gateway

---

## Key Insight

We've been focused on MCP *clients* (Hermes has native `native-mcp` skill, stdio+HTTP servers). But the next layer — the MCP *Gateway* — is where the architecture gets real for production. This is the "API gateway for the agent era."

## The N×M Integration Problem

When you connect N agents directly to M tools:
- **Credential sprawl**: API keys scattered across agent configs, impossible to rotate
- **Observability black holes**: No unified view of agent-tool interactions — which user action triggered a cascade of 5 tool calls?
- **Inconsistent error handling**: Every agent developer implements retries/backoff/circuit breakers differently
- **Lateral movement risk**: One compromised agent exposes credentials for dozens of services

## Three Gateway Archetypes

| Type | Philosophy | For |
|------|-----------|------|
| **Managed Platforms** (Composio, etc.) | Abstract complexity, pre-built integrations, handle OAuth lifecycle | Fast dev velocity |
| **Security-First Proxies** | Compliance, audit trails, credential vaulting | Enterprise/regulated |
| **Open-Source Infrastructure** | Maximum control, self-hosted, integrate with existing DevOps | Teams with infra chops |

## Why It's Different from API Gateways

Traditional API gateways are **stateless** request-response. MCP Gateways are **stateful + session-aware** — they manage persistent bidirectional connections with context. An agent session is not a single API call; it's a long-running conversation with tool use interleaved. The gateway needs to understand this lifecycle.

## Relevance to Hermes

We already have the MCP client layer (`native-mcp`). The gateway is the natural evolution:

1. **Hermes as Gateway**: Instead of each agent configuring its own MCP servers, Hermes could act as a centralized gateway — all agents route through it
2. **Tool aggregation**: The gateway pattern means one config (`config.yaml` MCP servers), many consumers (Hermes sessions, cron jobs, managed agents)
3. **Observability**: With the gateway layer, we get unified logging of all tool calls across all agents — currently each session's tool calls are siloed

## Open Questions

- Does the Hermes gateway process already exist? (`hermes gateway run`) — it provides the WebSocket/HTTP transport but does it do tool routing?
- Could we add an MCP proxy mode to the gateway that sits between agents and external MCP servers?
- How does this relate to the `kanban-orchestrator` / `subagent-driven-development` patterns we already have?

## Worth Tracking

- Open-source MCP gateways to watch: likely to emerge from the MCP community in 2026
- The "stateful session" aspect means MCP gateways need different scaling patterns than traditional API gateways — connection pooling, not just request pooling

