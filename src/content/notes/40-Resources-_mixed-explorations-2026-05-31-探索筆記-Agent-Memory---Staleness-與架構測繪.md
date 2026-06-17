---
_slug: 40-Resources-_mixed-explorations-2026-05-31-探索筆記-Agent-Memory---Staleness-與架構測繪
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-探索筆記-Agent-Memory---Staleness-與架構測繪.md
title: 探索筆記：Agent Memory — Staleness 與架構測繪
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- access
- agent
- decay
- mem
- memory
- semantic
- source
- staleness
- store
- timestamp
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# 探索筆記：Agent Memory — Staleness 與架構測繪

**延續自**: （本 cycle 新開，無前期筆記）

**日期**: 2026-05-31
**類型**: exploration
**來源**:
- Mem0 blog: "Memory Decay for Long-Running Agents" (2026-05-13)
- arXiv 2603.07670v1: "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers" (2026-03-08)

---

## Per-Source Insights

### Source 1: Mem0 Memory Decay (2026-05-13)

**核心機制**：
- per-project opt-in re-rank，在 semantic similarity 之上疊加 access recency scaling factor
- recent memories 最多 boost 1.5×，idle ones 衰減至 floor 0.3×
- 20 個 access timestamps 被追蹤（bounded reinforcement）
- 候選池擴展至 `top_k × 3`（最少 50）再套用 scaling → 給 re-rank 足夠 room
- **不做刪除**：stale memory 從不被 zeroed out，只是排名下降

**Staleness vs Decay 的明確區分**：
| Type | What it looks like | Right tool |
|------|-------------------|------------|
| Low-relevance staleness | Old facts not wrong, just less useful (Jan breakfast, abandoned side project) | Memory Decay |
| High-relevance staleness | Facts remain semantically relevant but became **wrong** (previous employer, outdated diet) | Timestamp-aware resolution at application layer |

**關鍵實測數字**：
- Decay off 時，fresh vs stale pair 的 score margin 可以小到 0.0001（cosine similarity 根本分不开）
- Decay on 時，fresh memories 得到 ~50% score boost，stale 降至 60% reduction
- 8 個 memories 的小 store，penicillin allergy fact（safety-critical, evergreen）從 rank 1 掉到 top-5 之外——被一個 recently accessed 的 trivia article 擠出

**A/B 測試框架**：Mem0 提供完整的 `mem0_decay_ab.py --mode two-project` harness，輸出 summary table + CSV/JSON。

**對 heartbeat_learning.py 的直接啟示**：
- Drift penalty 需要區分「低關聯性 staleness」（decay 解決）vs「高關聯性 staleness」（需要 timestamp-aware contradiction resolution）
- 目前 `heartbeat_learning.py` 只有 implicit decay，缺少 explicit `confidence_valid_until` + event-driven invalidation
- Access recency 是一個比 calendar age 更強的信號（"A memory that keeps being selected is operationally useful"）

---

### Source 2: arXiv 2603.07670 — Agent Memory Survey (2026-03)

**完整 taxonomy**（三維度）：
1. **Temporal scope**: Working / Episodic / Semantic / Procedural
2. **Representational substrate**: Context-resident text / Vector index / Structured store / Executable repo
3. **Control policy**: Heuristic / Prompted self-control / Learned control

**Five design objectives 的張力**：
- Utility ↔ Efficiency（囤積 vs 壓縮）
- Faithfulness ↔ Efficiency（精確 vs 節省）
- Governance 是獨立的維度

**Section 7.3 Staleness, contradictions, and drift**：
> "Semantic similarity cannot judge freshness... temporal versioning, source attribution, contradiction detection, and periodic consolidation are essential."

**Pattern C: Tiered Memory with Learned Control**：
- MemGPT、Agentic Memory (AgeMem) 的架構
- 三層以上：context + structured DB + vector store + cold archive
- 建議：從 Pattern B 起步，充分 instrumentation 後再 graduate to C

**Where Memory Makes or Breaks the Agent**（Section 6）：
- Coding agents、personal assistants、multi-agent collaboration 是最高價值的應用場景
- MemoryArena benchmark：把 active memory agent 換成 long-context-only baseline，task completion 從 80% 降至 45%

**Open Challenges（Section 9）**：
- Principled consolidation（dual-buffer probation promotion）
- Causally grounded retrieval（不只是 semantic similarity，要靠 causal graph）
- Learning to forget（selective forgetting policies）
- Trustworthy reflection（防止 confirmation bias entrench mistakes）

---

## 跨文章 Synthesis

### 核心收斂：結構化記憶 > 純嵌入檢索

兩篇資料從不同角度抵達同一結論：
1. Mem0 的「high-relevance staleness」需要 timestamp-aware resolution，純 vector similarity 無法處理
2. arXiv survey 的 Section 3.2 明確指出 vector index 會失去結構關係（"you can ask what's similar but not what caused what"）
3. 兩者都指向：embedding + temporal metadata + structural relationship 的混合架構

### drift penalty 的具體缺口

對照 `heartbeat_learning.py` 的現況：
- **Decay**：已有 implicit decay（在 distillate 权重上），但無 access recency signal——Mem0 的方法（recent retrieval → 1.5× boost）更精細
- **Staleness detection**：缺少 explicit mechanism
  - 低關聯性 → 可參考 Mem0 Decay 的 access recency tracking
  - 高關聯性 → 需要 timestamp-aware contradiction resolution（Mem0 的 ADD-only architecture + timestamp sort）
- **Confidence decay**：缺少 `confidence_valid_until` 機制（SSGM 的 periodic reconciliation 是參考方向）

### 建議方向

1. **Immediate**：在 `heartbeat_learning.py` 的 distillate 層加入 access recency weighting（借鑒 Mem0 的 recent-boost pattern）
2. **Short-term**：新增 `confidence_valid_until` 欄位 + event-driven invalidation（參考 SSGM Theorem 1 的 bounded semantic drift）
3. **Architectural**：考慮 Pattern B（context + structured store + retrieval）而非純 vector store——structured store 可以保留 timestamp、source、contradiction chain等元數據

---

## ✅ 本次探索完成
