---
_slug: 40-Resources-_mixed-explorations-2026-05-30---OpenMemory--Local-First-Cognitive-Memory-Engine
_vault_path: 40-Resources/_mixed/explorations/2026-05-30---OpenMemory--Local-First-Cognitive-Memory-Engine.md
title: '2026-05-30 — OpenMemory: Local-First Cognitive Memory Engine'
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- classifier
- decay
- engine
- github
- graph
- openmemory
- sector
- temporal
- valid
- waypoint
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 2026-05-30 — OpenMemory: Local-First Cognitive Memory Engine

**延續自**: （無前期筆記）

## Per-Source Insights

### OpenMemory (GitHub CaviraOSS, 48 pts)
**URL**: https://github.com/CaviraOSS/OpenMemory

**核心定位**: 「不是 RAG，不是 vector DB」——強調 local-first、認知層次的記憶架構。Python + Node SDK，SQLite/Postgres 儲存。

**Sector Classifier（最值得注意的設計）**:
```
Input → Sector Classifier → [Episodic | Semantic | Procedural | Emotional | Reflective]
```
輸入先經 sector classifier 分流到不同記憶區，每區有各自處理邏輯。這解決了「單一 vector DB 無法區分事實/事件/偏好/感受」的問題。

**Recall Engine 複合評分**:
- 不只是 cosine similarity
- **Salience + Recency + Coactivation** → Composite scoring
- 這與 YantrikDB 的 Ebbinghaus decay / Hebbian edges 收斂到同一方向

**Temporal Knowledge Graph**:
```json
POST /api/temporal/fact
{ "subject": "CompanyX", "predicate": "has_CEO", "object": "Alice", "valid_from": "2021-01-01" }
```
- `valid_from` / `valid_to` — 點時間事實
- Timeline queries — 重建實體歷史
- Change detection — 追蹤何時翻轉

**Decay Engine**:
- 「Decay & reinforcement instead of dumb TTLs」
- 直接對標 Mem0 的 staleness vs decay 區分（2026-05-29 筆記：`confidence_valid_until` + event-driven invalidation）

**Waypoint Graph（解釋性追蹤）**:
- 關聯可遍歷連結
- 每次 recall 有 trace（「為何召回這個節點」）
- 支援 reinforcement（加強有意義的連結）

**架構總圖**:
- Sector Classifier → 各自 Embed → SQLite/Postgres
- SQLite 存：Memories / Vectors / Waypoints
- Temporal Graph 分開儲存（Facts + Timeline）
- Recall Engine = Vector Search + Waypoint Graph + Decay + Composite Scoring → Consolidation → Reflection

**與 Hermes 對照**:
- `context-distiller` skill 相當於 Sector Classifier 的 input 層（session review + vault ingest）
- `heartbeat_learning.py` 的 distillate 相當於 Consolidation + Reflection 層
- 缺少：Explicit Temporal KG（valid_from/valid_to）、Decay Engine、Waypoint Graph

**實用細節**:
- MCP server 已有（`/mcp` endpoint）
- LangChain / CrewAI / AutoGen / Streamlit 整合
- 支援 GitHub / Notion / Google Drive / Web Crawler ingest
- `opm` CLI for scripting

**限制**:
- 目前正在 rewrite（`/rewrite` branch），文件警語「breaking changes and potential bugs」
- Migrate tool 支援：Mem0, Zep, Supermemory → OpenMemory

## Hermes 啟發

1. **Sector Classifier 層可抽離**：Hermes 的 session review + vault ingest 現在是混在 `context-distiller` 裡。若拆出獨立的 sector classifier（規則化或 ML-based），可以讓不同 sector 走不同 retrieval 策略

2. **Temporal KG 缺口最大**：Hermes 目前沒有 `valid_from/valid_to` 的時間事實模型。heartbeat_learning.py 的 distillate 是「現在的結論」，沒有「何時 valid」的語義。對於「某項洞察何時成立」的問題，現階段無法回答

3. **Decay Engine 設計最完整**：OpenMemory 的 decay 不是 TTL，而是 salience + recency + coactivation 三維驅動。YantrikDB 理論類似但 OpenMemory 有實際實作（`Decay Engine` block in architecture diagram）

4. **Waypoint Graph = Hebbian edges 的具象化**：YantrikDB 談 Hebbian learning，OpenMemory 直接實作成 Waypoint Graph + Reinforcement loop

## 未追蹤 Leads

- https://github.com/chisasaw/redcache_ai — 11 pts, local memory framework for LLMs
- https://github.com/CaviraOSS/OpenMemory/tree/rewrite — rewrite branch（breaking changes，監控穩定性）
- Mem0 migration path study（OpenMemory 已支援從 Mem0 migrate）

## ✅ 本次探索完成

