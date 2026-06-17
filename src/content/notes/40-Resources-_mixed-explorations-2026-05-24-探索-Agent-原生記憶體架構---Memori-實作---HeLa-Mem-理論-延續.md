---
_slug: 40-Resources-_mixed-explorations-2026-05-24-探索-Agent-原生記憶體架構---Memori-實作---HeLa-Mem-理論-延續
_vault_path: 40-Resources/_mixed/explorations/2026-05-24-探索-Agent-原生記憶體架構---Memori-實作---HeLa-Mem-理論-延續.md
title: 探索：Agent 原生記憶體架構 — Memori 實作 + HeLa-Mem 理論（延續）
date: 2026-05-24
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- base
- edge
- github
- hebbian
- mem
- memori
- memory
- path
- weight
created: '2026-05-24'
updated: '2026-06-15'
status: budding
---

# 探索：Agent 原生記憶體架構 — Memori 實作 + HeLa-Mem 理論（延續）

**延續自**: [[2026-05-24-agent-memory-architecture]]

## Phase 3 — Review

### 跨文章 Synthesis（補充）

**HeLa-Mem 深度閱讀後的關鍵補充**：

**Architecture 核心公式**：
- Hebbian edge weight update: `w_{ij}^{(t+1)} = (1-λ)·w_{ij}^{(t)} + η·I(v_i, v_j ∈ K_t)`
- Spreading activation: `S(v_j) = S_base(v_j) + β·Σ_{i∈N(j)} S_base(v_i)·w_{ij}`
- Dual-path ranking: `R_final = Top-k(S_base) ∪ Top-m(S | v ∉ Top-k)`

**對 Hermes 啟發的深化**：
1. **Hebbian graph 具體實作路徑**：用 co-activation count 作為 edge weight，每次 session 中共同被召回的 memory nodes 增加 weight，定期蒸餾高 degree nodes 到 semantic store
2. **Write path 非同步**：Memori 的 `WRITE_DELAY = 6` 是 practical workaround，eventual consistency 設計適用於 Hermes 的 multi-session 架構
3. **Reflective Agent 作為單獨的 LLM call**：不是每個 user turn 都 trigger，只有當 hub detection threshold 達標才 trigger，這大幅降低計算成本

**已知 dead leads（2026-05-24）**：
- `https://github.com/Mem0rias/Memori` — repo 404/inaccessible（2026-05-24 驗證）
- Mem0 GitHub repo 需重新搜尋驗證

**實作啟發：Hebbian Graph for Hermes Memory**：
- 在 `memory-consolidator` 加入 Hebbian edge tracking（用 SQLite graph table）
- `heartbeat_v2.py` 的 `_DoomLoopTracker` 概念可以類比為 hub detection
- dual-path retrieval 可類比為 semantic search + doom-loop counter 的 combination

## 未追蹤 leads

- （無新的有效 leads， Mem0/Memori repo 待重新驗證）

## 狀態更新 (2026-05-24 20:10 CST)

**Mem0 vs Memori 澄清**：原筆記提及的 `github.com/Mem0rias/Memori` 已死，但 mem0.ai (docs.mem0.ai) 是活躍項目，定位幾乎相同：
- "universal, self-improving memory layer for LLM applications"
- BYODB 支援（PostgreSQL）
- Session-level grouping

→ 這是有效 lead，值得重新驗證。
- URL: https://docs.mem0.ai/introduction（活得）
- GitHub: `github.com/mem0-ai/mem0`（需驗證）
