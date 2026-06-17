---
_slug: 40-Resources-_mixed-explorations-2026-05-25-memory-arena-continuation
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-memory-arena-continuation.md
title: 探索延續：MemoryArena 基準測試填補了什麼差距
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索延續：MemoryArena 基準測試填補了什麼差距

**延續自**: [[2026-05-25-llm-agent-memory-architecture-survey-2026]]

**日期**: 2026-05-25 | **來源**: arxiv:2602.16313 (MemoryArena, He et al., Feb 2026)

## 為什麼這篇重要（相較於其他 benchmark 基準）

之前的 survey（2603.07670）已經涵蓋了「現有 benchmarks 聚焦於靜態回憶」的批評，但沒有量化缺口。MemoryArena 填補了這個量化缺口：

| Benchmark | 測什麼 | 缺什麼 |
|-----------|--------|--------|
| LoCoMo / LongMemEval | 事後回憶靜態對話 | 無 agentic action |
| WebArena / SWE-bench | agentic 決策 | 無 persistent memory across sessions |
| MemoryArena | **memory-action 耦合** | 首次填補這個缺口 |

核心貢獻：agents 在 LoCoMo 逼近 saturation（~90% accuracy），但在 MemoryArena 的 multi-session bundled shopping 只達到 **30-40% task completion rate**。這不是 benchmark difficulty 的問題——是memory system 根本無法捕捉 latent task state。

## 關鍵發現（直接影響 Hermes 設計）

### 1. Latent constraint tracking 是核心失敗點

MemoryArena 的四個 domain 都涉及「前期互動introduce constraints，後面需要記得並應用」：

- **Bundled Web Shopping**：Session 1 買了 TV Stand，Session 2 必須記得尺寸才能買正確的 TV Mount
- **Group Travel**：一個 travelers 設定的偏好（budget、 cuisine），後加入的 travelers 必須傳承
- **Progressive Web Search**：Sub-query 2 的 answer 取決於 Sub-query 1 introduce 的 constraint
- **Formal Reasoning**：Lemma 22 的證明依賴 Lemma 26 建立的中間結果

**Hestia 的應用**：heartbeat memory distillation 每次 cycle 都會引入新的 insight/decision，這些約束（ distillation 的方向、不要重複的主題、上一次的 action result）需要跨 session 傳遞但目前沒有 explicit tracking。

### 2. MemGPT 提取式摘要 > 純檢索的原因

Case study（Group Travel, Figure 14）：MemGPT 成功的原因是它的 extraction 生成「高密度 summary，explicitly linking cross-traveler dependencies」。Long-context model（20k+ tokens）失敗是因為「Lost in the Middle」——具體的 `$48` 數值埋在 20k chars 的上下文中被淹沒。

**Pattern C（learned control, MemGPT-style）勝出**：不是因為模型更強，而是因為 extraction step 強迫 agent 做「重要性判斷」——這正是 distillation 的核心操作。

### 3. 不同 memory system 的失敗模式分布

| System | Strength | Failure Mode |
|--------|----------|--------------|
| MemGPT | Precision memory, explicit linking | Retrieval completeness |
| Mem0 | Good at entity facts | Cross-session constraint propagation |
| Long-context | No retrieval needed | Lost-in-middle, instruction drift |
| Mirix (ReasoningBank) | Procedural memory | Episodic noise injection |

**Pattern C 的 MemGPT 表現最好，但仍有 domain（例如數學推理）下 retrieval 不完整的問題。**

## Hermes 應用：heartbeat memory 的具體 gap

### Gap 1：沒有 cross-cycle constraint propagation
每次 heartbeat cycle 的 distillation 是 stateless——前次確定的「探索方向」、「不重複的主題」是 implicit knowledge，不是 enforced constraint。MemoryArena 的 constraint tracking mechanism（compatibility chains、preference inheritance）可以直接移植。

**具體建議**：在 `heartbeat_learning.py` 的 distillation output 中加入 `cross_session_constraints` field，明確列出「下一個 cycle 應继承的 constraints」。

### Gap 2：distillation 沒有 importance scoring
MemoryArena 顯示「所有資訊都儲存」vs「選擇性儲存」的 tradeoff。Hestia 目前是「所有 distillation 都進入 vault」，但沒有 quality gate。Dual-buffer promotion（48h probation period）可以借用。

### Gap 3：没有 explicit memory diff 追蹤
MemoryArena 的 benchmark evaluation 本身就測量「memory 如何影響 action」（task completion 是 gold standard）。Hestia 的 observability 目前只有 vault count 趨勢，沒有「memory change → behavioral change」的追蹤。

## 未追蹤 Leads（已驗證 Phase 1）

- `https://memoryarena.github.io/` — 官方網站，含程式碼与数据集
- `arxiv:2507.05257` — MemoryAgentBench（incremental evaluation，benchmark 的另一個維度）
- `arxiv:2506.21605` — MemBench（comprehensive memory evaluation suite）

## ✅ 本次探索完成