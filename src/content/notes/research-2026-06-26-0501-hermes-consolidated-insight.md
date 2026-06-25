---
_slug: research-2026-06-26-0501-hermes-consolidated-insight
_vault_path: research/2026-06-26-0501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- trigger-design
source: multi
created: '2026-06-26'
confidence: high
supplement_to:
- - 2026-06-26-0400-hermes-consolidated-insight
title: 補述：Trigger 設計 > 結構設計、Token 成本是硬約束（接續昨日 insight 的未覆蓋面）
type: research
status: seedling
updated: '2026-06-26'
---

# 補述：Trigger 設計 > 結構設計、Token 成本是硬約束（接續昨日 insight 的未覆蓋面）

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

**前情提要**：這四篇筆記在 2026-06-26-0400 已產出 insight note，鎖定兩個 cross-cutting theme（reader→writer 失效信號閉環、飽和容量常數 5±2）。本篇**不重複**這兩個 theme，僅補上當時未明確指出的兩個 cross-cutting 觀察。

---

## Cross-Cutting Theme 1: Trigger 條件設計才是 2026 記憶系統的真正差異化變數——結構已收斂

**支援筆記**: 全部 4 篇（high）

昨日 insight 把四篇定位為「結構創新」，但對齊 trigger 條件的設計表會看到另一個更尖銳的模式。**所有四篇都把「結構」當標題，但真正的設計選擇都在「何時寫入/濃縮/淘汰」的 trigger**：

| 系統 | 結構（表面） | **Trigger（真正差異點）** | 量化差異 |
|------|-------------|------------------------|----------|
| H-MEM | 4 層 + positional index | User feedback（approval/rebuttal）| Multi-hop +0.21、Adversarial +4.49 |
| RecMem | 3 層（sub/epi/semantic）| Recurrence count ≥ 5（θcount）| **87% token 節省** |
| MemoryOS | 3 層 + segment-paging | Heat score = α·N_visit + β·L_interaction + γ·R_recency | Temporal F1 +118.80% vs A-Mem |
| SAGE | Graph + writer/reader loop | Reader 檢索失敗信號 → writer reward | 2 rounds 達最佳 multi-hop QA |
| Governed Memory | Dual memory + quality gates | Quality gate scores (coreference/self-containment/temporal) | Fact recall 99.6%、LoCoMo 74.8% |
| OCL（governance 內）| 四個 policy components | Constraint check before execution（πgate）| Unsafe Rate 88% → 0% |

**洞察**：六個系統的**結構都是分層或結構化的**——這從 A-Mem (Zettelkasten graph)、MemGPT (virtual context)、MemoryBank (flat) 開始就是分層世界。但 F1 差距從 27（A-Mem）拉到 49（MemoryOS），靠的全是 trigger 公式的精細度，**不是分層數的多寡**。這把昨日 Theme 2 的「飽和容量常數」放進更深脈絡：與其追問「幾層才飽和」，不如追問「trigger 多敏感才飽和」。

對 Hermes 的具體含意：heartbeat_learning.py 的 drift penalty 不該只做時間衰減（昨日 Theme 1 已指出），**也不該只補 reader→writer 閉環**。要補的是 trigger 函式本身——把所有可得的信號（recurrence count、visit count、contradiction rate、reader failure signal）組合成加權公式，並用昨日 Theme 2 的「5±2 飽和容量」做 normalization（避免某個信號 dominate）。

**可行動下一步**:

在 `heartbeat_learning.py` 的 `compute_drift_penalty()` 函式（目前是 `time_decay(half-life=38d)` 純時間衰減）改寫成：

```python
def compute_drift_penalty(distillate, vault_fts5, recent_tasks):
    # 4 個 signal，各自歸一化到 [0, 1]
    recurrence = count_cosine_neighbors(distillate, vault_fts5, threshold=0.85) / 7   # cap at 7 (Miller's law)
    visit = distillate.hit_count_30d / 20                                            # cap at 20
    contradiction = 1 - has_been_overridden_by(distillate, vault_fts5)               # 0/1
    reader_failure = distillate.task_match_failure_rate_30d                           # 0-1
    
    # 4 個 weight，預設等權（待 sweep 校準）
    signal = (recurrence + visit + contradiction + reader_failure) / 4
    
    # 純時間衰減只佔 30%（其餘 70% 是 signal-driven）
    penalty = 0.3 * time_decay(distillate.age_days, half_life=38) + 0.7 * (1 - signal)
    
    return penalty
```

PR 描述重點：把 drift penalty 從「被動時間衰減」轉成「主動信號加權」，符合 2026 memory architecture 的 trigger-driven 共識（H-MEM、RecMem、MemoryOS、SAGE、Governed Memory 全部 trigger-driven）。

---

## Cross-Cutting Theme 2: Token 成本是 trigger 設計的硬約束，不是次要考量

**支援筆記**: hmem-recmem（high）、memory-os（high）、llm-agent-memory-governance（high）

把三篇有量化 token 數字的段落對齊：

| 系統 | 量化指標 | 數字 |
|------|---------|------|
| H-MEM | Flat retrieval latency vs H-MEM | O(a·10^6·D) 100ms+ vs O((a+k·300)·D) <100ms |
| RecMem | Construction token cost vs eager systems | **87% reduction** vs Mem0/A-Mem/MemoryOS |
| MemoryOS | LLM calls/query vs A-Mem | **4.9 calls** vs 13（68% 節省）|
| MemoryOS | Tokens/query vs MemGPT | **3,874 vs 16,977**（77% 節省）|
| Governed Memory | Progressive context delivery | **50% token 節省** |
| Governed Memory | Fast mode vs Full mode | **~850ms vs 2-55s** |
| OCL | Avg rounds before execute | **5.36 → 2.58** rounds |
| OCL | Avg latency | **38.75s → 18.51s** |

**洞察**：每一個 trigger 信號（recurrence、visit、reader failure）都有 token 成本——這個成本在所有論文中都被量化為「efficiency 主軸」，不是「nice to have」。Theme 1 提出的 4-signal trigger 公式不是免費的：每個 distillate 要追蹤 4 個計數器，每個 task 要計算 reader failure signal。**在 Hermes 簡單棧的現實下，Theme 1 的完整實作可能比 OCL baseline（38s latency）還慢**——這個成本必須在 PR 設計時量化。

對 Hermes 的具體含意：昨日 insight + 今日 Theme 1 加起來有 4 個待實作組件（reader feedback loop、5±2 飽和容量、4-signal trigger、contradiction rate），每個都要新 query / 新 SQLite 寫入。必須排優先級。

**可行動下一步**:

執行順序（cost-adjusted priority）：

1. **第 1 週：Theme 1 的 `visit_count` + `contradiction_rate` 兩個 signal**（讀取 `vault_fts5.db` 已有索引，零新增 token cost）
2. **第 2 週：Theme 2（飽和容量 sweep）**——純分析，不增加 runtime cost
3. **第 3 週：Theme 1 的 `recurrence_count` signal**（新增 cosine scan，估計 +50 tokens/task）
4. **第 4 週：Reader feedback loop**（昨日 Theme 1，估計 +100 tokens/task，highest impact but highest cost）

每週結束前跑一次 `trigger_cost_report.py`，量化新增 token overhead vs retrieval F1 改善。如果 overhead > 5% 且 F1 改善 < 3pp，砍掉當週功能回到單純時間衰減。**不要追求 4-signal 完整版，先驗證 ROI**。

---

## 與昨日 insight 的互補關係

| 主題 | 昨日 0400 | 今日 0501 |
|------|-----------|-----------|
| Reader→Writer 閉環 | ✅ 完整論證 + 量化 | （不重複）|
| 飽和容量 5±2 / Miller's law | ✅ 提出 + 可實驗驗證 | （不重複）|
| Trigger 設計 > 結構設計 | （未明確點出）| ✅ Theme 1（補上設計公式）|
| Token 成本約束 | （未明確量化）| ✅ Theme 2（補上排程與 ROI 門檻）|

兩篇合在一起形成 2026 memory architecture 對 Hermes 的完整 actionable 設計建議：
- **結構要什麼**：5±2 飽和（昨日 Theme 2）
- **trigger 要什麼**：4-signal 加權（今日 Theme 1）
- **閉環要什麼**：reader failure → writer feedback（昨日 Theme 1）
- **成本約束**：分 4 週實作，週週量 ROI（今日 Theme 2）

**信心標示**:
- Theme 1（trigger > 結構）：**high** — 6 個獨立 trigger 設計 + 量化結果交叉驗證
- Theme 2（token 成本約束）：**high** — 7 個量化數字（三篇都有獨立的 measurement methodology，不是互相引用）
