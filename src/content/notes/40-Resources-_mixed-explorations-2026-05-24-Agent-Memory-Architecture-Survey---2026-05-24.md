---
_slug: 40-Resources-_mixed-explorations-2026-05-24-Agent-Memory-Architecture-Survey---2026-05-24
_vault_path: 40-Resources/_mixed/explorations/2026-05-24-Agent-Memory-Architecture-Survey---2026-05-24.md
title: Agent Memory Architecture Survey — 2026-05-24
date: 2026-05-24
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aegis
- agent
- context
- https
- mem
- memory
- mnemora
- security
- serverless
- source
created: '2026-05-24'
updated: '2026-06-15'
status: budding
---

# Agent Memory Architecture Survey — 2026-05-24

**延續自**: （首次探索，無前期筆記）

## Per-Source Insights

### Aegis Memory (quantifylabs/aegis-memory, 22⭐)
Secure context engineering for production AI agents.

**核心差異化**（相對於 mem0/Zep/Letta）：
- **Content security pipeline**：4-stage（validation → PII scan → prompt injection detection → optional LLM classifier），唯一全鏈路實作
- **HMAC-SHA256 integrity signing**：tamper detection，寫入時 signed，讀取時驗證
- **OWASP 4-tier trust hierarchy**：untrusted / internal / privileged / system，agent compromised 時限制 blast radius
- **ACE loop**：Generation → Reflection → Curation，自動 vote（success → helpful，failure → harmful + reflection memory）
- **Contradiction detection**：typed `contradicts` edge with explicit resolution（kept_source / kept_target / both_valid / both_invalid）
- **Hybrid retrieval**：pgvector (dense) + PostgreSQL tsvector (sparse) + Reciprocal Rank Fusion，catch exact-token cases that pure embedding blurs
- **Unified context hub**：prompts + memories + skills + subagents，single API call `/context/load`
- **Temporal decay + consolidation audit trail**：merged memories stay queryable with `is_deprecated=True` + `consolidated_into` metadata

**ACE loop 實作**（相對於 "inspired" 框架的差異）：
- Auto-voting tied to run outcomes（不只是手動 vote endpoint）
- Auto-reflection on failure（含 error context，不是只有 explicit creation）
- Full curation cycle（promote / flag / consolidate），不是 not-implemented

**當選 Aegis**：當你需要 content security + integrity + multi-agent ACL + ACE self-improvement + contradiction tracking 全套時，這是唯一同時滿足的 open source 選項。

**未追蹤 leads**：
- https://www.aegismemory.com/（完整文件）
- server/contradiction_detector.py（Aegis 原始碼）
- server/consolidation.py（consolidation + deprecation trail 實作）

---

### Mnemora (mnemora-db/mnemora, 5⭐)
Serverless memory DB for AI agents. AWS-native, open source.

**4 種 memory type**：
1. **Working memory** — DynamoDB key-value，sub-10ms reads，optimistic locking + TTL
2. **Semantic memory** — Aurora pgvector，auto-embedded via Bedrock Titan 1024d，duplicates merged (cosine > 0.95)
3. **Episodic memory** — append-only time-series，DynamoDB hot tier + S3 cold tier，session replay
4. **Procedural memory** — tool definitions / schemas / prompt templates in Postgres，versioned（schema live, SDK methods in v0.2）

**架構**：SDK → HTTP API Gateway → Lambda (ARM64) → DynamoDB / Aurora / S3 / Bedrock。全 serverless，multi-tenant，Cdk deploy 到自己 AWS account。

**整合**：LangGraph CheckpointSaver / LangChain Memory / CrewAI Storage，native。

**與 Aegis 的取捨**：Mnemora 重在 infrastructure（4-type memory, serverless, sub-10ms），Aegis 重在 security（injection detection, integrity, OWASP hierarchy）。若需求是「安全地讓多 agent 共享 memory」，Aegis 更合適；若需求是「高效能 serverless 記憶層」，Mnemora 更合適。

**未追蹤 leads**：
- https://mnemora.dev/（官網）
- infra/（CDK source，了解 serverless 架構细节）

---

## 跨文章 Synthesis

### 當前 Agent Memory 格局

2026 年的 agent memory 生態可以分為三層：

| 層 | 玩家 | 核心價值 |
|---|---|---|
| Security-first context hub | Aegis Memory | injection detection, HMAC integrity, OWASP trust hierarchy, ACE loop |
| Serverless infrastructure | Mnemora | 4-type memory, sub-10ms, AWS-native, LangGraph integration |
| General memory platforms | mem0, Zep, Letta | semantic + temporal + graph，各有偏重 |

**值得注意的收敛**：hybrid retrieval（dense + sparse + RRF）已從 Aegis 擴散到所有主要玩家（mem0 2026 survey 也實作了 semantic + BM25 + entity）。這代表純 embedding-only retrieval 已不夠，exact-match cases（entity names, file paths, error codes）需要 keyword/sparse 補充。

**Contradiction handling 作為新戰場**：Aegis 首創 typed `contradicts` edge + explicit resolution workflow，Zep/Letta 用 LLM-based temporal invalidation，mem0 用 Mem0g LLM graph resolver。方向一致但實作各異，還沒有標準共識。

**Hermes 啟發**：
- Aegis 的 ACE loop（auto-vote on run outcome）非常適合整合進 `heartbeat_learning.py` 的 distillate 流程——目前 Talos 的 learning 只有被動記錄，缺少「根據執行結果自動調整 memory quality」的機制
- Mnemora 的 4-type memory model（working/semantic/episodic/procedural）比目前 Hermes 的單一 learning log 更結構化，可作為未來 memory organization 提案的參考
- Aegis 的 content security pipeline（4-stage）是目前見過最完整的 injection defense in-depth 設計，補充了當前 exploration prompt injection defense 文件

## 未追蹤 leads
（Phase Locked — 不加 action 指示）

https://www.aegismemory.com/
https://github.com/quantifylabs/aegis-memory
https://github.com/quantifylabs/aegis-memory/tree/main/server/contradiction_detector.py
https://github.com/quantifylabs/aegis-memory/tree/main/server/consolidation.py
https://mnemora.dev/
https://github.com/mnemora-db/mnemora
https://mnemora.dev/docs/quickstart

## ✅ 本次探索完成
