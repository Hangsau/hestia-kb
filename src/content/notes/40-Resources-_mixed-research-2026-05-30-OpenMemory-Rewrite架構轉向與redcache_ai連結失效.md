---
_slug: 40-Resources-_mixed-research-2026-05-30-OpenMemory-Rewrite架構轉向與redcache_ai連結失效
_vault_path: 40-Resources/_mixed/research/2026-05-30-OpenMemory-Rewrite架構轉向與redcache_ai連結失效.md
title: 2026-05-30 — OpenMemory Rewrite 架構轉向 + redcache_ai 連結失效
created: '2026-05-30'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# 2026-05-30 — OpenMemory Rewrite 架構轉向 + redcache_ai 連結失效

**來源**: autonomous_note
**類型**: architecture-research

## OpenMemory `rewrite` Branch — 架構重大轉向

**URL**: https://github.com/CaviraOSS/OpenMemory/tree/rewrite

### 核心轉向：Python → TypeScript/Node-first

- 主產品路徑：`packages/openmemory-js`（Node/TypeScript server）
- 語言佔比：TypeScript 72.7%、Python 24.3%（Python 已退居次要）
- 持久層：Postgres + pgvector（預設），可切換 qdrant/valkey/redis/pinecone/weaviate/chroma/milvus
- Python SDK / MCP / dashboard / IDE extensions / hosted deploy 全部從預設 runtime 推遲

### 新的四大原則（rewrite README）

1. Durable records with provenance
2. Temporal correctness
3. Explainable recall
4. Contract-aware memory usage

### 架構關鍵文件（rewrite 分支）

- `docs/architecture-rewrite-plan.md` — 重寫架構藍圖
- `docs/ai-context.md`、`docs/decisions.md` — AI context 與決策日誌
- `docs/versioning.md`、`docs/migrations.md` — 版本管理與遷移
- `docs/pgvector-index-strategy.md` — 向量索引策略
- `docs/vector-stores.md` — 多種向量儲存支援矩陣

### 與主 branch 的差異

- 主 branch 強調 SQLite/Postgres + Python SDK + MCP server
- rewrite branch 放棄 Python SDK 作為預設產品路徑，聚焦 TypeScript/Node durable server
- 兩者都支援 temporal knowledge graph，但 rewrite 用 Postgres 作為唯一事實來源

## redcache_ai — GitHub Repo 已消失

**URL**: https://github.com/chisasaw/redcache_ai

**結果**：Repo 已不存在（GitHub 404）。前期筆記 Lead 已過期。

## Hermes 啟發

1. **OpenMemory 從 Python → Node/TS 的 pivot 印證一個模式**：當記憶系統需要「真正的持久化 + 可解釋的召回」，Python 的動態特性反而是包袱。TypeScript 的靜態類型 + 明確介面更適合這種場景。Hermes 若要往「可解釋記憶」方向走，可能需要參考這個取態。

2. **Postgres 作為 single source of truth 是正確的 trade-off**：不再支援多種 local backend（SQLite/memory），統一把 Postgres 當 source of truth。

3. **Temporal correctness 成為一等公民**：rewrite 的四大原則（durable records / temporal correctness / explainable recall / contract-aware）與 SSGM framework 的 "Temporal+Provenance Grounding" 完全對齊。時間事實模型是這類系統的核心差異化點。

4. **redcache_ai 消失是正常損耗**：11 pts 的小型 repo 生命周期短，後期筆記不依賴此類小項目是正確的。

## 失效連結

- https://github.com/chisasaw/redcache_ai — **unreachable**（repo 已消失，2026-05-30 確認）
