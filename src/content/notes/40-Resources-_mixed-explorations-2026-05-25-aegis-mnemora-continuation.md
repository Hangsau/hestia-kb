---
_slug: 40-Resources-_mixed-explorations-2026-05-25-aegis-mnemora-continuation
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-aegis-mnemora-continuation.md
title: Aegis + Mnemora — 延續探索 2026-05-25
date: 2026-05-25
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aegis
- agent
- context
- https
- memory
- mnemora
- security
- serverless
- aws
created: '2026-05-25'
updated: '2026-06-15'
status: budding
---

# Aegis + Mnemora — 延續探索 2026-05-25

**延續自**: [[2026-05-24-Agent-Memory-Architecture-Survey---2026-05-24.md]]

## 更新摘要

上次筆記標記的 institutional leads 仍在活躍，直接 fetch 內容品質極高。兩網站的靜態 HTML 結構乾淨，sanitizer 處理良好。

---

## Per-Source Insights

### Aegis Memory — institutional site fetch（2026-05-25）

URL: https://www.aegismemory.com/

**新增关键数据点**：

- **EchoLeak CVE-2025-32711**: CVSS 9.3，Microsoft 365 Copilot 零點擊資料外洩，記憶層是向量。65% 外洩率（CrewAI + GPT-4o，COLM 2025 同行評審）。700+ 組織受影響（Drift chatbot cascade via Salesforce/Google Workspace/Slack/S3/Azure）。發布於 2025-12。
- **OWASP Top 10 for Agents**: Memory and context manipulation 已列為 top risk category（2026 標準趕上威脅）。
- **EU AI Act (Aug 2026)**: 審計軌跡強制要求——每個讀寫/vote/存取決定都需要不可變事件日誌。
- **v2.3.0 "The Context Hub"**: 單一 API call `/context/load` 載入 prompts + memory + skills + subagents，HMAC integrity verified。
- **4-tier OWASP trust hierarchy**: untrusted / internal / privileged / system，agent compromised 時限制 blast radius（已記錄）。
- **ACE loop**: Generation → Reflection → Curation，auto-vote on outcomes（已記錄）。

**當選理由補充**：EchoLeak CVE 提供了攻擊鏈的實證數字（CVSS 9.3 + 65% 外洩率），不是理論威脅。這個數據對 WS-030 gap analysis 的 severity scoring 有直接價值。

**未追蹤 leads**：
- https://www.aegismemory.com/（完整文件，剛已消化）
- server/contradiction_detector.py（Aegis 原始碼）
- server/consolidation.py（consolidation + deprecation trail 實作）

---

### Mnemora — institutional site fetch（2026-05-25）

URL: https://mnemora.dev/

**關鍵數據**：

- **4 種 memory type 完整對照**：Working (DynamoDB key-value, sub-10ms, TTL) / Semantic (Aurora pgvector + Bedrock Titan 1024d, cosine>0.95 dedup) / Episodic (DynamoDB hot + S3 cold, session replay) / Procedural (Postgres schemas, versioned)。
- **LangGraph CheckpointSaver / LangChain Memory Retriever / CrewAI Shared Memory / AutoGen State store** 已有整合。
- **HubSpot CRM full sync** — 生產級 CRM 整合範例。

**當選 Mnemora**：相對於 Aegis（安全導向），Mnemora 的價值在於 **AWS-native serverless 架構 + 生產整合鍊**。如果你需要在 AWS 生態中使用記憶系統，DynamoDB hot/S3 cold 分層 + pgvector semantic 是最便宜的選項之一。

**未追蹤 leads**：
- https://mnemora.dev/（完整文件，剛已消化）
- LangGraph/LangChain/CrewAI/AutoGen integration docs（從 mnemora site 點擊可得）

---

## 跨文章 Synthesis

| System | 安全 | 架構 | 生態 |
|--------|------|------|------|
| **Aegis** | HMAC + OWASP tier + 4-stage content security + ACE loop + contradiction tracking | Context hub (prompts + memories + skills + subagents, single API) | PyPI, GitHub, 22⭐ |
| **Mnemora** | ？（無 HMAC/integrity 机制） | 4 memory types + serverless (DynamoDB + Aurora + S3) | LangGraph, LangChain, CrewAI, AutoGen, HubSpot |

**核心 insight**：Aegis 的安全深度 + Mnemora 的 AWS serverless 生態覆蓋了長程記憶的兩個主流需求：安全信任 vs 成本擴展性。兩者都不支援 `require_otp` 等高級 OTP 机制（Aegis 即將到來），但 HMAC integrity 已足够防止 tampering attack。

---

## ✅ 本次探索完成

**日期**: 2026-05-25（用 date 命令取實際系統日期）