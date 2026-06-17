---
_slug: 40-Resources-_mixed-explorations-2026-05-28-2026-05-28---Memori-Agent-Native-Memory-Implementation
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-2026-05-28---Memori-Agent-Native-Memory-Implementation.md
title: 2026-05-28 — Memori Agent-Native Memory Implementation
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- entity
- heartbeat
- hermes
- isolation
- memori
- memory
- process
- session
- yantrikdb
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 2026-05-28 — Memori Agent-Native Memory Implementation

**延續自**: `references/memori-triple-extraction-design.md`, `references/memori-retrieval-rag-vs-memr3.md`

## Per-Source Insights

### Memori v3.3.0 Implementation Walkthrough (MarkTechPost, 2026-05-11)

**Source**: https://www.marktechpost.com/2026/05/11/a-coding-implementation-to-build-agent-native-memory-infrastructure-with-memori-for-persistent-multi-user-and-multi-session-llm-applications/

**Architecture Pattern — Triple Isolation Model**

Memori 的核心架構是三層隔離，與之前 design doc 的概念對應更精確：

1. **entity_id** — 用戶邊界（`user@domain` 格式）
   - 完全隔離：Alice 的 facts 不會出現在 Bob 的 recall 中
   - 等同於 YantrikDB 的 user-scoped partition

2. **process_id** — Agent persona 邊界
   - 同一用戶、不同 agent 角色（fitness-coach vs meal-planner）記憶分開
   - 這是之前文件未明說的層級 — process_id 是「同一用戶內的子身份」

3. **session** — 對話 thread 邊界
   - `mem.set_session(project-session-id)` 將相關對話歸組
   - `mem.new_session()` 開新對話串，舊記憶仍然可取（跨 session 持久）

**Key Implementation Detail — Memory Interception Layer**

```python
mem.llm.register(client)  # 掛鉤 OpenAI client
#之後每筆 chat.completions.create 都會自動經過 memory layer
```

這是 **push-based memory enrichment**，不同於 RAG 的 pull-based retrieval：
- RAG：LLM 做夢前回憶（retrieval-then-generation）
- Memori：記憶在生成時自動注入上下文（generation-with-memory）

**WRITE_DELAY = 6 秒**：非同步延遲寫入，不回阻塞 response。符合 YantrikDB 的「非同步寫入、延遲 commit」模式。

**Session Management**：
- `set_session()` 重新激活既有 session 的上下文
- `new_session()` 開新 thread（舊 session 進入歸檔狀態，但 entity/process 內的 fact 仍然可取）
- 測試中看到「project-fastapi session」recall 了之前 discuss 的技術棧（Python 3.12, SQLAlchemy, Fly.io）

**Multi-tenant Benchmark**：
- 測試展示同一 `client` 實例切換 entity_id 後，facts 完全隔離
- Bob 無法存取 Alice 的 peanut allergy；Alice 無法知道 Bob writes Rust
- 這驗證了 entity-scoped isolation 的實際效果

## Hermes 啟發

### 1. 對 heartbeat_learning.py drift penalty 的直接回應

前期研究（YantrikDB、MuninnDB）提到 Ebbinghaus decay + Bayesian confidence 對 drift penalty 的必要性。Memori 的實作提供了一個具體信號：

**process_id 級別的 isolation 意味著**：當同一個 agent（如 Talos heartbeat）切換不同 task context 時，應該有不同的記憶池。heartbeat_learning.py 的 distillate 若在同一 session 內混合不同 task 的信號，會產生語義污染。

**建議**：heartbeat_learning.py 引入 `task_id` 維度（目前只有 `profile` 維度），不同 task 的 distillate 分開計算 drift penalty。

### 2. Session 邊界 vs Context Window 的取捨

Memori 的 session 模型（相關對話歸組、不相關开 new_session）與 Hermes 的 session 管理高度相關。建議 WS-035 提案可以參考 Memori 的 `mem.set_session()` 模式，用 session 維度而非時間維度來決定 context window 的邊界。

### 3. 三層隔離映射到 Hermes 現有组件

| Memori 層 | Hermes 對應 |
|---|---|
| entity_id | Hestia/Talos profile（用戶邊界）|
| process_id | skill / cron job（agent persona）|
| session | threads/ 目錄（對話 thread）|

目前 Hermes 只有 profile 維度有 explicit isolation，process_id 和 session 層級的隔離依賴 implicit convention。這與 Memori 的明確三層模型相比，有升級空間。

## Cross-Cutting Synthesis

Memori v3.3.0 的 triple isolation 與前期多個來源的結論收斂：
- YantrikDB 五層索引、Hebbian learning
- Engram 的 Transactional Forgetting + Memory Bus auth
- AGT 的 Agent Hypervisor（4 privilege rings）

都是在「結構化隔離優於純嵌入檢索」這個共識下的不同實作角度。Memori 的價值在於它是目前唯一有公開 Colab tutorial、可以直接跑起來的開源方案（相較於 YantrikDB/MuninnDB 是 research code）。

## 未追蹤 Leads

- AMA-Bench (OpenReview): https://openreview.net/forum?id=GoSVL7mLcM — benchmark for long-horizon agent memory，留存
- MEMO framework (MarkTechPost 2026-05-26): https://www.marktechpost.com/2026/05/26/memo-a-modular-framework-for-training-a-dedicated-memory-model-on-new-knowledge-without-modifying-llm-parameters/ — 分離式記憶模型 training，與 heartbeat learning 的方向對比

## ✅ 本次探索完成
