---
_slug: 40-Resources-_mixed-explorations-2026-05-25-Aegis---Mnemora---架構深度對比探索
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-Aegis---Mnemora---架構深度對比探索.md
title: Aegis + Mnemora — 架構深度對比探索
date: 2026-05-25
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aegis
- agent
- com
- consolidation
- cosine
- https
- key
- memory
- mnemora
- stage
created: '2026-05-25'
updated: '2026-06-15'
status: budding
---

# Aegis + Mnemora — 架構深度對比探索

**日期**: 2026-05-25（用 date 命令取實際系統日期）

**延續自**: [[2026-05-25-aegis-mnemora-continuation.md]]

## Per-Source Insights

### Aegis Memory — GitHub 原始碼深度（quantifylabs/aegis-memory）

URL: https://github.com/quantifylabs/aegis-memory

**當選理由**：前次探索只看了 institutional website 的行銷內容，這次深入 source code 看實作。

**Contradiction Detector（server/contradiction_detector.py）**：
- 雨階段策略：Stage 1（cheap cosine similarity + negation marker，<10ms）→ Stage 2（optional LLM pairwise，1-2s/pair）
- 預設 Stage 1 only，LLM 為 opt-in
- High-recall, low-precision — 故意設計，false positives 走 "both_valid" resolution workflow
- Negation patterns: `not|never|no|none|cannot|can't|won't|doesn't|don't|isn't|aren't|wasn't|weren't|false|wrong|incorrect|invalid|disabled|deprecated|removed|broken|unlike|opposite|contrary|contradicts|disagrees|conflicts`
- 資料庫：SQLAlchemy async session + `MemoryGraphRepository`（EdgeType enum）

**Consolidation（server/consolidation.py）**：
- 替換 legacy first-50-char prefix match（ace_repository.py ~line 1024）
- 策略：embedding-based pairwise consolidation，cosine similarity ≥ 0.92（高門檻）
- 決策：heuristic（keep higher-effectiveness）OR LLM merge
- Deprecation：loser 標 `is_deprecated=True` + `metadata.consolidated_into` 指向 keeper
- **Dry run default**：所有動作預設 `dry_run=True`， caller 明確 apply 才寫入——preserves audit trail
- 三層可配置：cosine threshold、LLM merge、dry run mode

**Security Pipeline（行銷文件交叉驗證）**：
- Stage 1: Input validation（content length、metadata depth/key count、null bytes）
- Stage 2: Sensitive data detection（SSN、Luhn credit card、API key patterns）
- Stage 3: Prompt injection detection（system prompt override、role manipulation、exfiltration triggers）
- Stage 4: LLM-based injection classification（async，opt-in only）
- 完整文件：https://docs.aegismemory.com/guides/security

**OWASP Trust Hierarchy（4-tier）**：
- untrusted / internal / privileged / system
- Agent compromised 時限制 blast radius

---

### Mnemora — Serverless AWS-native 記憶資料庫（mnemora-db/mnemora）

URL: https://github.com/mnemora-db/mnemora

**當選理由**：PyPI 安裝簡單（`pip install mnemora`），AWS serverless 架構，4 memory types 全覆蓋。

**SDK Quick Start**：
```python
from mnemora import MnemoraSync
client = MnemoraSync(api_key="mnm_...")

# Working memory — sub-10ms key-value state
client.store_state("my-agent", {"task": "research", "step": 1})

# Semantic memory — auto-embedded, vector-searchable
client.store_memory("my-agent", "User prefers concise replies")

# Search
results = client.search_memory("user preferences", agent_id="my-agent")
for r in results:
    print(r.content, r.similarity_score)
```

**4 種 Memory Type 實作對照**：

| Type | Storage | Query | Latency | Use Case |
|------|---------|-------|---------|----------|
| **Working** | DynamoDB key-value | direct key | sub-10ms | agent state, TTL |
| **Semantic** | Aurora pgvector + Bedrock Titan 1024d | cosine similarity >0.95 | ms | memory search |
| **Episodic** | DynamoDB hot + S3 cold | session replay | ms | conversation history |
| **Procedural** | Postgres schemas (versioned) | SQL | ms | skills, workflows |

** Integrations（LangGraph/LangChain/CrewAI/AutoGen）**：
- LangGraph CheckpointSaver 整合
- LangChain Memory Retriever 整合
- CrewAI Shared Memory 整合
- AutoGen State store 整合
- HubSpot CRM full sync（生產級 CRM 整合）

**Self-host 選項**：`MNEMORA_API_URL` 環境變量支援自部署。

---

## 跨系統 Synthesis

### Aegis vs Mnemora 架構哲學對比

| 面向 | Aegis | Mnemora |
|------|-------|---------|
| **核心定位** | Context security-first | Infrastructure-first |
| **安全機制** | HMAC-SHA256 integrity、4-stage pipeline、contradiction detector、OWASP trust tier | 無內建 integrity（對比 Aegis）|
| **儲存層** | SQLAlchemy（推測 PostgreSQL） | DynamoDB + Aurora + S3 分層 |
| **查詢優化** | embedding-based consolidation、dedup | pgvector cosine dedup（>0.95）|
| **整合生態** | PyPI + GitHub（22⭐）| LangGraph/LangChain/CrewAI/AutoGen、HubSpot |
| **延遲目標** | 未明（相對 Aegis 重安全）| sub-10ms（working memory）|
| **開源模式** | Apache 2.0 | MIT / BSL-1.1 |

### Hermes 整合切入點

**Aegis 適合**：
- 需要 cryptographic integrity（HMAC write protection）→ WS-031 已涵蓋
- 需要 contradiction detection（對抗 hallucination accumulation）
- 需要 OWASP-tier trust hierarchy 的多 agent 系統

**Mnemora 適合**：
- 需要 serverless cost efficiency（DynamoDB pay-per-request + S3 cold storage）
- 已在 AWS 生態（Bedrock Titan embedding）
- 需要 LangGraph/LangChain 生產整合

**實作建議**：
1. **HMAC integrity**：走 Aegis 方向（WS-031），Python `hmac` 模块即可
2. **長期記憶架構**：Mnemora 的 4-type 分層值得參考（Working/Semantic/Episodic/Procedural）
3. **Consolidation 策略**：Aegis 的 embedding-based pairwise + dry run default 模式適合 Hermes 的 audit trail 需求

---

## 未追蹤 Leads

- https://docs.aegismemory.com/llms.txt（完整文件 index，可用來發現所有頁面）
- https://docs.aegismemory.com/quickstart/installation
- mnemora-db/mnemora/source code 深入（consolidation logic、4 memory type 實作）
- LangGraph CheckpointSaver + Mnemora 整合實作

---

## ✅ 本次探索完成

**日期**: 2026-05-25
