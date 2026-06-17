---
_slug: 40-Resources-_mixed-research-2026-06-14-研究報告-a2a-protocol-從-單體-agent-到-可互通-agent-互聯網-的標準化躍遷-2026
_vault_path: 40-Resources/_mixed/research/2026-06-14-研究報告-a2a-protocol-從-單體-agent-到-可互通-agent-互聯網-的標準化躍遷-2026.md
tags:
- research
- a2a
- multi-agent
- interoperability
- agent-protocol
- mcp
- agent-discovery
- agent-card
- firn
date: 2026-06-14
source_report: 2026-06-14-a2a-protocol-agent-interoperability-2026.md
fingerprint: agent, task, mcp, firn, a2a, message, spec, agentcard, protocol, client
title: 研究報告：A2A Protocol — 從「單體 Agent」到「可互通 Agent 互聯網」的標準化躍遷 (2026)
created: '2026-06-14'
updated: '2026-06-15'
type: research
status: budding
---

# 研究報告：A2A Protocol — 從「單體 Agent」到「可互通 Agent 互聯網」的標準化躍遷 (2026)

> **TL;DR** —— MCP 解決「agent ↔ tool」（縱向），A2A v1.0（2026-03 發布）解決「agent ↔ agent」（橫向）。firn 短期只做 A2A client role 即可，用 `python-a2a`（30K 月下載）包成 tool；server role 等真實 use case 出現再做。HBHC（zombie credential revocation 90× 加速）跟 A2X（1000+ service discovery）暫不實作，等 reference implementation。

## 1. 核心觀念（What）

| 觀念 | 定義 | 為什麼重要 |
|------|------|-----------|
| **A2A Protocol** | Agent-to-Agent 通訊的標準 protocol（Apache 2.0，Linux Foundation 治理） | 補 MCP 對偶缺點：跨 framework / vendor / 組織的 agent 互通 |
| **A2A ≠ MCP** | MCP = agent↔tool；A2A = agent↔agent | 兩者互補。A2A 強制 opaque execution，不暴露 prompt/memory/tools |
| **Task 物件** | A2A 的「有 state 工作單元」，6 種 status（submitted/working/input-required/completed/failed/canceled） | 對應「跨小時、跨天的協作」，不是「等 function call 回傳」 |
| **AgentCard** | JSON 自我描述，公開在 `/.well-known/agent.json` | 對等於 package.json：讓 client 知道「你是誰、能做什麼、要怎麼認證」 |
| **ContextId** | 跨多輪 Task 共用的對話脈絡識別 | 同一個 user 同一個話題可以跨越多個 Task |
| **三種 update 機制** | Polling / SSE streaming / Push notification webhook | 對應短/中/長任務 |
| **A2X** | arXiv 2605.29270，2026-05-28 | 解決 1000+ service 塞 context 的「Lost-in-the-Middle」問題 |
| **HBHC** | arXiv 2605.20704，2026-05-20 | 解決 sub-agent swarm 的 zombie credential 問題，比 OAuth 2.0 快 90× |
| **a2a-x402** | google-agentic-commerce 支付擴充，v0.1 | 復活 HTTP 402 做 on-chain agent 商業 |

## 2. 架構與機制（How）

### 2.1 A2A Spec v1.0 三層架構

```
L1: Data Model (Task/Message/Part/Artifact/AgentCard/Extension, Protocol Buffers)
L2: Abstract Operations (SendMessage/SendStreamingMessage/GetTask/ListTasks/CancelTask/SubscribeToTask/PushNotification CRUD)
L3: Protocol Bindings (JSON-RPC 2.0 / gRPC / HTTP+JSON-RPC / Custom WSS, MQTT)
```

### 2.2 AgentCard 範例

```json
{
  "name": "GeoSpatial Route Planner Agent",
  "supportedInterfaces": [
    {"url": "https://georoute-agent.example.com/a2a/v1", "protocolBinding": "JSONRPC"},
    {"url": "https://georoute-agent.example.com/a2a/grpc", "protocolBinding": "GRPC"}
  ],
  "capabilities": {"streaming": true, "pushNotifications": true, "extendedAgentCard": true},
  "securitySchemes": {"google": {"openIdConnectSecurityScheme": {...}}},
  "skills": [{"id": "route-optimizer-traffic", "tags": ["routing", "traffic"]}]
}
```

### 2.3 Task lifecycle

```
SendMessage → Server 回 Task(status=input-required) →
Client follow-up → Server 改 status=working → 
streaming (SSE) updates → status=completed + Artifact
```

### 2.4 firn A2A Client 模組骨架

```python
# src/firn/tools/a2a_client.py
from python_a2a import A2AClient, AgentCard
from python_a2a.models import Message, TextPart, Role

class A2AToolClient:
    def __init__(self, agent_url: str):
        self.client = A2AClient(agent_url=agent_url)
        self.card = self.client.agent_card

    @property
    def tool_name(self) -> str:
        return f"a2a::{self.card.name}"

    def execute(self, task: str, context_id: str | None = None) -> dict:
        msg = Message(role=Role.USER, parts=[TextPart(text=task)])
        if context_id:
            msg.context_id = context_id
        response = self.client.send_message(msg)
        if hasattr(response, "status"):
            return {"task_id": response.id, "state": response.status.state}
        return {"text": "".join(p.text for p in response.parts if p.kind == "text")}
```

## 3. 思考（Why it matters）

### 3.1 典範轉移：從「單體 Agent」到「Agent 互聯網」

- **個人尺度**：個人助手從「一個 process 內 orchestrator」變成「能跨工具、跨 agent 邊界呼叫」
- **企業尺度**：5 部門 5 個 agent 不再需要 200 個 custom integration
- **市場尺度**：agent 開發者專注 specialist，互通層是底層建設

### 3.2 Q2 2026 三社群同步收斂

| 社群 | 產出 | 時點 |
|------|------|------|
| Google / LF | A2A v1.0 + v1.0.1 | 2026-03-12 / 2026-05-26 |
| 學術 | A2X (discovery) + HBHC (credential) + Trustworthy Agent Network (SIGKDD 2026) | 2026-05 |
| 開源 | a2a-x402 + MAIL + openclaw-a2a-gateway | 2026-05/06 |

這是「**從 niche spec 升級成 ecosystem mandate**」的訊號。Agent framework 不支援 A2A = 就像 web framework 不支援 HTTP/2 一樣尷尬。

### 3.3 三個獨立限制（要誠實面對）

1. **Spec 不規範 server 怎麼存 Task state**——A2A 只管 wire format，重啟恢復是各家實作決定
2. **A2A 不解 agent 間 prompt injection 攻擊**——內容對 client 是 untrusted input，要靠 SIGKDD 2026 paper 的 4 design pillar
3. **24,279 stars 但 production case study 少於 20 個**——v1.0 還在早期採用

## 4. 應用（Action for our projects）

### 4.1 firn 短期（1-2 迭代）

| 優先級 | 工作 | 難度 | 改動檔案 |
|--------|------|------|---------|
| **P0** | `tools/a2a_client.py` 新模組 | MODERATE | 新檔 |
| **P0** | `a2a/registry.py` 本地 registry | MODERATE | 新檔 |
| **P1** | `context/builder.py` 注入 AgentCard | MODERATE | 修改 |
| **P1** | `tools/schemas.py` 加 a2a tool schema | TRIVIAL | 修改 |
| **P2** | `observability/turns_logger.py` 記 TaskID | TRIVIAL | 修改 |

**費用**：免費（`pip install python-a2a` MIT, 30K 月下載, 無商業限制）

### 4.2 firn 不要做的事

- ❌ 自己做 A2A server role（個人助手定位不需要）
- ❌ 實作 HBHC / A2X / x402（research-grade，reference impl 未出）
- ❌ Agent Card 簽章（除非要當 server）
- ❌ 追 a2a-x402 支付（v0.1 太早、鏈上 latency 對個人助手不適用）

### 4.3 對 Hermes 本身的延伸建議

- `hermes-agent` 的 `mcp/` 模組可考慮加 `a2a/` 平行模組（MCP↔A2A 互補），但下次獨立評估

## 5. Follow-up Questions

1. A2A v1.1 roadmap 內容（LF 公告 + ROADMAP.md）
2. A2X 是否被 EMNLP 2026 收
3. HBHC reference implementation 何時釋出（Saurabh Deochake, 2026 Q3 預測）
4. A2A vs ANP vs ACP vs MAIL vs AIP——5 個互通 spec 哪個活下來
5. a2a-x402 v1.0 是否引入 commit-then-settle 批次結算
6. SIGKDD 2026 4 design pillar（adversarial robustness / semantic alignment / cascading safety / cryptographic provenance）哪個先有對應 A2A extension——預測 cryptographic provenance 最先
7. firn 什麼時候真實需要當 A2A server
8. 是否會有官方 `a2a-mcp-bridge` 標準

## 6. 來源（11 個）

| URL | Type | Credibility |
|-----|------|------------|
| https://github.com/a2aproject/A2A | Official repo + spec | HIGH |
| https://a2a-protocol.org/latest/specification/ | Official spec | HIGH |
| https://a2a-protocol.org/latest/topics/what-is-a2a/ | Official tutorial | HIGH |
| https://a2a-protocol.org/latest/topics/a2a-and-mcp/ | Official A2A❤️MCP | HIGH |
| https://github.com/themanojdesai/python-a2a | 3rd-party Python | HIGH |
| https://github.com/google-agentic-commerce/a2a-x402 | Payment extension | MEDIUM-HIGH |
| arxiv 2605.29270 (A2X) | 學術論文 | HIGH |
| arxiv 2605.20704 (HBHC) | 學術論文 | HIGH |
| arxiv 2605.19035 (Trustworthy Agent Network) | SIGKDD 2026 Blue Sky | MEDIUM-HIGH |
| https://blog.langchain.dev/ | Industry blog | MEDIUM |
| https://pypistats.org/api/packages/python-a2a/recent | 下載量數據 | HIGH |

---

**Cross-refs**：
- [[2026-06-06-研究報告-mcp-ecosystem-maturity-2026-從-萬用-tool-bus-到-policy-enforced-tool-fabric]] — MCP 互補背景
- [[2026-06-13-研究報告-ai-agent-firewall-prompt-injection-defense-從學術到開源到合規]] — 對應 L4 (內容 untrusted input) 風險
- [[2026-05-25-研究報告-multi-agent-coordination-protocols]] — 早期 multi-agent 協調
- [[2026-06-01-研究報告-meta-agent-監督其他-agent-的架構]] — 跨 agent 治理脈絡
