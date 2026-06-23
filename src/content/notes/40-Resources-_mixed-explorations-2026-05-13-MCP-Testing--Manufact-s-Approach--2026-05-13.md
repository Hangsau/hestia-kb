---
_slug: 40-Resources-_mixed-explorations-2026-05-13-MCP-Testing--Manufact-s-Approach--2026-05-13
_vault_path: 40-Resources/_mixed/explorations/2026-05-13-MCP-Testing--Manufact-s-Approach--2026-05-13.md
title: 'MCP Testing: Manufact\"\"s Approach (2026-05-13)'
date: 2026-05-13
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- clients
- com
- hmr
- inspector
- manufact
- mcp
- testing
- tool
- via
created: '2026-05-13'
updated: '2026-06-15'
status: budding
---

# MCP Testing: Manufact's Approach (2026-05-13)

Source: [manufact.com/blog/mcp-testing](https://manufact.com/blog/mcp-testing) — Pietro Zullo, May 12, 2026

## Pain Points They Identified
- Configuring MCPs in normal clients is painful — and you have to redo it every code change
- Testing isn't just "does the tool work" — it's "does the agent call it in the right way and order"
- Model + system prompt variation matters: same GPT-5.5 model behaves differently via API vs inside ChatGPT
- Remote clients (claude.ai, chatgpt.com) are the real target, but hardest to test against

## Their Solution (3 parts)

### 1. Inspector with HMR
- `npm run dev` → Inspector at localhost:3000, auto-connected to your MCP
- Chat UI + tool testing panel + spec compliance metadata
- **HMR via protocol primitives**: send `notifications/tools/list_changed` instead of hard-refreshing the server
- UI changes propagate across all Inspector panels via Vite HMR

### 2. Tunnel for Real Clients
- One-click stable public URL (same subdomain every session)
- Point ChatGPT or claude.ai at your local server without reconfiguring connectors
- HMR works through the tunnel — edit a tool, changes propagate to real clients

### 3. Cross-Client Automated Testing
- Browser agents install the MCP app and run test cases on actual clients
- Screenshots + screen recordings of full conversations
- Can wire into CI: run on push, gate production promotion on passing results

## Interesting Implications
- The "same model, different client, different behavior" observation is crucial for agent reliability
- HMR via spec primitives (not restart) is the right pattern — similar to how we should handle agent tool reloading
- Could Hermes adopt a similar Inspector-style dev loop for skill authoring?

## Relevance to Hermes
- We reload skills statically; a protocol-level reload signal could be cleaner
- Testing skills against different providers (DeepSeek, Claude) is analogous to their cross-client testing
- The tunnel concept maps to exposing local Hermes for remote testing

