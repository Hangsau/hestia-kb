---
_slug: 40-Resources-_mixed-explorations-2026-05-23-Google-A2A---SAGA-互操作性深度分析
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-Google-A2A---SAGA-互操作性深度分析.md
title: Google A2A + SAGA 互操作性深度分析
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- discovery
- google
- hearth
- https
- json
- otk
- protocol
- saga
- streaming
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "Google A2A + SAGA 互操作性深度分析"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [a2a, agent-discovery, agent-interop, google, saga, protocol]
---

# Google A2A + SAGA 互操作性深度分析

**延續自**: [[2026-05-23-SAGA-深度追加---NDSS-2026-論文全文分析]] [[2026-05-23-Agent-Governance---SAGA---ACE-Deep-Dive-延續]]

**日期**: 2026-05-23 | **來源**: GitHub raw README（A2A + SAGA） | **類型**: 主題延續

---

## 核心發現

### A2A Protocol 架構（A2A = Agent2Agent）

**背景**：Google 主导，Linux Foundation 托管，开源协议。定位是填补 MCP 的空白——MCP 让 agent 使用工具，A2A 让 agent **作为 agent** 互相协作。

**三大支柱**：
1. **Agent Cards** — JSON 格式的自我描述（capabilities、endpoint、auth requirements）。相当于"名片"，让 agent 在不暴露内部状态的前提下互相发现。
2. **三种交互模式**：
   - `request/response`：同步，最简单
   - `streaming (SSE)`：Server-Sent Events，agent 可以边工作边推送状态
   - `push notifications`：异步，长任务完成后主动通知客户端
3. **JSON-RPC 2.0 over HTTPS**：标准传输，不绑定特定框架

**与 MCP 的关系**（核心洞见）：
- MCP：agent **是客户端**，tool 是服务端 → agent-as-tool
- A2A：agent **是对等的**，可以互相发起任务 → agent-as-agent
- 两者互补，不是竞争关系

**SDK 生态**：Python / Go / JavaScript / Java / .NET — 企业采用门槛低

**关键 spec**：`https://a2a-protocol.org/latest/specification/`

**对 Hearth 的直接意义**：A2A 的 Agent Card discovery 机制 + push notification 模式，比 Hearth 当前的轮询 inbox 更接近"真实 inter-agent 协议"。Hearth 的 inbox 实际上是简陋的 A2A 早期版本——缺少 discovery、缺少 streaming 状态反馈。

### SAGA 实际实现（GitHub 源码级分析）

**Architecture**：
```
User → Provider (MongoDB) → Agent Registry
Bob's agent ←── OTK ──→ Alice's agent
```

**核心发现**：
1. **Agent manifest（agent.json）**：每个 agent 的工作目录包含自己的完整身份（`aid`、`identity_key`、`opks[]`、签名）
2. **Contact Rulebook**：JSON 格式的访问控制策略，`[{"pattern":"*", "budget":10}]` 含义：对所有来源开放，最多 10 次交互
3. **OTK 实现细节**：
   - 每注册一个 agent，存入 N 个一次性公钥（OTK）
   - initiating agent 向 Provider 申请 OTK，用 DH 交换生成共享密钥
   - Access Control Token 在共享密钥下加密，可复用
4. **三个实验任务可跑**：`schedule_meeting.py`、`expense_report.py`、`create_blogpost.py`

**对 Hermes 的意义**：SAGA 的 contact rulebook 模式（pattern + budget）是 Hearth ACP 的可直接映射的蓝图，比之前的分析更具体。

---

## 跨协议 Synthesis

| 维度 | A2A | SAGA | Hearth（当前） |
|------|-----|------|---------------|
| Discovery | Agent Cards | Provider 查询 | 手动写 inbox |
| Auth | 可选（spec 中规划） | OTK + 签名 | Session token |
| ACP | 规划中（未实现） | Contact Rulebook | 无 |
| 传输 | JSON-RPC 2.0/HTTPS | 自定义加密 | Git pull/push |
| 状态反馈 | SSE/streaming | 无 streaming | 无 |
| 生态 | 5 个 SDK + 多个框架集成 | 研究原型 + MongoDB | 自建 |

**核心结论**：A2A 是生产就绪的 inter-agent 协议标准，SAGA 是安全设计的参考实现。Hearth 的差距是真实且可量化的——需要 Agent Card 等效（capabilities 注册）、streaming 状态反馈、ACP 可选实现。

---

## Hermes 啟發

1. **WS-017 (DCG Governance Integration)**: A2A 的 Agent Card 概念可以改造为 Hearth 的 agent capability registry——每个 agent 在 inbox 里有描述自己能力的元数据
2. **WS-026 (Explicit Behavioral Guidance)**: A2A 的 streaming SSE 模式给用户实时反馈，与 rule bank 结合可以实现"structured autonomy with live transparency"
3. **SAGA contact rulebook → Hearth ACP**: pattern + budget 的 JSON 结构简单，可直接实现

---

## 未追蹤 Leads

- A2A spec: https://a2a-protocol.org/latest/specification/
- A2A Python SDK: https://github.com/a2aproject/a2a-python
- A2A samples: https://github.com/a2aproject/a2a-samples
- Google Cloud A2A partner program

## ✅ 本次探索完成

