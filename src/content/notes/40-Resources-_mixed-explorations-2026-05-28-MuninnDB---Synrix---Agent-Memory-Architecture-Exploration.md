---
_slug: 40-Resources-_mixed-explorations-2026-05-28-MuninnDB---Synrix---Agent-Memory-Architecture-Exploration
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-MuninnDB---Synrix---Agent-Memory-Architecture-Exploration.md
title: MuninnDB + Synrix — Agent Memory Architecture Exploration
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- engine
- hermes
- install
- memory
- muninn
- muninndb
- semantic
- synrix
- vector
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# MuninnDB + Synrix — Agent Memory Architecture Exploration

**日期**: 2026-05-28
**延續自**: [[2026-05-27-agent-memory-architecture-muninn-synrix]]

## 核心發現

兩個專案都在解決同一個根本問題：現有資料庫（vector DB、SQL、KV store）都不是為 agent 原生工作負載設計的。兩者用了完全不同的方法，但結論驚人收斂。

---

## MuninnDB — 認知記憶資料庫

**Repo**: scrypster/muninndb | **Stars**: 297 | **Lang**: Go | **License**: BSL 1.1
**Install**: `curl -sSL https://muninndb.com/install.sh | sh`（單一二進位，零依賴）

### 設計哲學
- **Ebbinghaus 遺忘曲線**：記憶不是靜態儲存，會自然衰減。使用頻率決定記憶強度。
- **Hebbian 學習**：共同激活的概念自動形成關聯邊，邊強度隨共激活頻率增強/減弱。
- **Bayesian 信心**：每個 engram 有信心分數，強化動作 raise、矛盾 lower。
- **語義觸發（Semantic Triggers）**：主動推播模型——訂閱一個 context，資料庫在相關性改變時主動推送到 agent，不需要 poll。

### 6-Phase 激活管線（< 20ms）
1. Parallel full-text + vector search
2. Fuse results
3. Apply Hebbian co-activation boosts from past queries
4. Inject predictive candidates from sequential patterns
5. Traverse association graph
6. Score with ACT-R temporal weighting

### MCP 整合（35 tools）
- Auto-detect Claude Desktop, Cursor, OpenClaw, Windsurf, OpenCode, VS Code, GitHub Copilot
- `muninn_remember`, `muninn_recall`, `muninn_activate` 等核心工具
- `muninn_guide` — vault-aware AI onboarding（資料庫自己告訴 AI 怎麼用）

### 對 Hermes 的啟示
- **語義觸發**：Hermes 的 memory pipeline 可以考慮類似的 push 模型——記憶在相關性改變時主動浮現，而非被動檢索
- **衰減機制**：Ebbinghaus 演算法可以直接實作在 Hermes 的 memory-governance 層
- **35 MCP tools 太多**：MuninnDB 的廣度 vs Synrix 的深度，代表兩種不同的整合哲學

---

## Synrix — O(1) 狀態基礎設施

**Repo**: RYJOX-Technologies/Synrix-Memory-Engine | **Stars**: 88 | **Lang**: Python + C | **License**: Python MIT, Engine proprietary
**Install**: `pip install synrix && synrix install-engine`

### 設計哲學
- **記憶體映射陣列**：固定大小、cache-aligned 節點（1216 bytes）。每個節點可透過 `ID × node_size` 直接算offset，O(1) 讀取。
- **前綴命名空間強制**：節點名稱必須有 `TYPE:` 前綴（`TASK:`、`FAILURE:`、`PATTERN_:`），前綴錯誤的節點被 engine 拒絕。這保證了 O(k) 而非 O(n) 查詢。
- **無刪除**：append-only 設計，learning system 不應刪除自己的記憶。
- **WAL + fsync**：SIGKILL 中間寫入零資料損失（500 nodes 實測）。

### 延遲（實測，非合成）
| Operation | Latency |
|-----------|---------|
| Node lookup by ID | 192 ns (hot cache) / 3.2 μs (warm) |
| Prefix query — 100K node dataset | 0.07 ms（固定，不隨 dataset 增大而變慢）|
| WAL write + fsync | 1–5 ms（磁碟依賴）|
| In-place payload update | Sub-microsecond |

對比：Mem0 p95 read = 1.4s。Qdrant p50 = 4ms。

### 推理鏈儲存
```python
# 固定 offset → O(1) by ID
node_id = db.add_node("TASK:stripe:attempt", '{"success": false}', parent_id=root)
# 前綴查詢 → O(k) where k = matching results, NOT dataset size
history = db.find_by_prefix("TASK:stripe:")
```

### 對 Hermes 的啟示
- **WAL + mmap**：Synrix 的 crash-safe 設計可以直接應用在 Hermes 的 memory snapshot 機制
- **前綴強制命名空間**：目前 Hermes 的 memory entry 沒有結構化前綴，導致 grep 無法做範圍限定查詢
- **零網路延遲**：Synrix 走 mmap 直接讀記憶體，Hermes 的 session_search 每次都走 LLM + FTS5，延遲不在同一數量級
- **Proprietary engine 是問題**：Synrix 的核心 engine 是 binary-only，無法自托管

---

## 跨專案合成

### 收斂點
1. **都拒絕 vector DB**：兩者都不需要 embedding model——MuninnDB 用 semantic proximity，Synrix 根本不做 semantic search
2. **都是 append-only**：不刪除是共識，learning system 刪除自己的記憶是矛盾的設計
3. **都強調 agent-native**：不是為人類設計的查詢介面，是為 agent 的 high-frequency state update 設計

### 分歧點
| | MuninnDB | Synrix |
|--|---------|--------|
| Model | Push（主動推播）| Pull（被動查詢）|
| Focus | Semantic memory, decay, triggers | Raw state speed, O(1) access |
| Latency target | < 20ms activation | < 200ns hot cache |
| License | BSL 1.1 | Proprietary engine |
| Embeddings | Yes (semantic) | No (prefix only) |

### 對 Hermes Memory Architecture 的啟示

**短期（可實作）**：
- 在 `memory-consolidator` 或新專屬 script 中實作前綴強制 scheme（`MEM:`、`PLAN:`、`RESULT:`）
- WAL-based snapshot 機制借鑒 Synrix 的 crash-safe 寫入模式
- Ebbinghaus decay 演算法直接實作（不需要 ML，純數學）

**中期（需要架構決策）**：
- Hermes 目前的 session_search 走 FTS5 + LLM 解讀，延遲高。Synrix 的 O(1) offset model 代表一種可能的替代：structured memory entry with deterministic access
- MuninnDB 的 semantic trigger push model 和目前 Hermes 的被動回顧模式正好互補

**不適合的方向**：
- 兩個專案都不是純 vector-based，Hermes 不需要跟進 vector search
- Synrix 的 proprietary engine 不適合自托管需求（Hermes 的設計原則）

---

## 未追蹤 Leads

- https://muninndb.com/docs — 完整 API 文件（含 MCP tools 清單）
- https://synrix.io — 官網，含 latency benchmark 細節
- docs/ARCHITECTURE.md — Synrix engine internals, why not SQLite
- docs/how-memory-works.md — MuninnDB 記憶運作原理深度解析

**Vault**: Copied to vault (ingest bug bypass) | **Status**: DONE

## ✅ 本次探索完成

