---
_slug: 40-Resources-_mixed-research-2026-06-13-1501-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-13-1501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-13'
confidence: high
title: 跨論文收斂：記憶架構的「reader→writer feedback loop」是 2026 整個領域的隱性缺口
updated: '2026-06-15'
type: research
status: budding
---

# 跨論文收斂：記憶架構的「reader→writer feedback loop」是 2026 整個領域的隱性缺口

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

2026 上半年的 LLM agent 記憶文獻在「分層」「觸發式 consolidation」「熱度驅動蒸發」三條主線上各自收斂，但四篇筆記放在一起才看得出：整個領域都在解決同一個未被命名的問題——**writer 端不知道 reader 端的失敗**。只有 SAGE（筆記 [3]）明確把這個閉環畫出來。

## Cross-Cutting Theme 1: Reader→Writer Feedback Loop 是 2026 文獻共同缺口，只有 SAGE 閉環

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇筆記各自處理「記憶系統的某個面」，但放在一起會發現它們都在**單向流動**：

- **H-MEM**（[1]）：user feedback 影響 memory weight（approval→strengthen, rebuttal→decay），但 weight 變化不會回饋給「如何生成新記憶」的 writer。Writer 是靜態的。
- **RecMem**（[1]）：recurrence count 觸發 consolidation，但**觸發後寫入 semantic memory 的策略不變**——不論讀者後續檢索成功或失敗，writer 的「何時寫、如何寫」規則是 hard-coded。
- **MemoryOS**（[2]）：heat score 是純粹的**讀者側資料**（visit count + interaction + recency），用於 eviction——但 eviction 不會回饋改變 segment 摘要策略或 persona 萃取維度。Heat 是 end-of-pipe 信號，不是 feedback signal。
- **Governed Memory**（[4]）：明確把「**Silent quality degradation without feedback loops**」列為五大結構性挑戰之一。Tiered routing（fast/full）依 query 靜態選擇，不從 routing 結果學習。Reflection-bounded retrieval 雖是迭代協議，但 LLM judge 的 completeness 評分不進入下一輪的 writer 參數。
- **SAGE**（[3]）：**唯一一個把 reader failure 顯式作為 writer reward signal 的系統**。Writer 寫入策略受 reader 檢索成敗反饋調整，self-evolution 兩輪達到 multi-hop QA 最佳。

**這個 pattern 不會出現在任何單篇筆記**——因為每篇只比較 2-3 個系統。只有把四篇都攤開，才看到 H-MEM/RecMem/MemoryOS/Governed Memory 都是「writer 永遠聽不到 reader」設計。SAGE 是 outlier，但 SAGE 解決的不是「另一種記憶」而是**這個共同的設計缺陷**。

**對 Hermes 的意義**：`heartbeat_learning.py` 的 distillate 流程目前是**單向的**——distillate 寫入 vault，task context 匹配讀取，但**讀取失敗的訊號不回到 distillation trigger**。一個 distillate 連續 30 天零引用，作者完全不知道。SAGE 證明了這是可以閉環的，而且不需 RL——policy gradient 也行，但最簡單的形式就是「visit count = 0 持續 N 天 → 進入 stale review queue」。

**可行動下一步**:
1. 在 `heartbeat_learning.py` 加一個 `read_feedback_log` 結構：每個 distillate 記錄 `last_retrieved_at`、`retrieval_count_30d`、`zero_hit_streak_days`。這不需要新 ML，就是 metadata。
2. 設定 `zero_hit_streak_days > 21` 觸發 `stale_candidate` 標記（不是直接刪除），下次 distillation trigger 優先重寫這個概念。
3. 預計工作量：2 小時改 `vault_writer.py` + 30 分鐘加 Prometheus metric `hermes_distillate_zero_hit_streak_days`。
4. **不要**複製 SAGE 的 RL policy——對於 Hermes 的 distillate 量級（百級到千級），純啟發式 rule-based feedback 已足夠。

## Cross-Cutting Theme 2: 「記憶存/取的觸發函數」是同一個數學問題的四種變體——Hermes 應選一個 commit

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

仔細看每篇的 consolidation/eviction trigger，把它們抽象成同一個函數簽名：

| 系統 | Trigger function | 維度 | 來源筆記 |
|------|----------------|------|---------|
| RecMem | `consolidate_if: count(similar ≥ θsim) ≥ θcount` | 1D（recurrence） | [1] |
| H-MEM | `decay_if: user_rebuttal_signal` | 1D（feedback） | [1] |
| MemoryOS | `evict_if: heat = α·N_visit + β·L_interaction + γ·R_recency < τ` | 3D（composite） | [2] |
| SAGE | `policy: π(usage_reward) → write_action` | 高維（RL） | [3] |
| Governed Memory | `route: fast|full based on query_type` | 2D（tier） | [4] |

**這個表格是 cross-cutting 的**——單篇筆記只看到自己的 trigger 函數，不會把它和別的系統放在同一個 abstract level。把它們攤平後看到：

**所有 trigger 函數都是「usage signal 的線性組合 + threshold」**。差別只在於：
- 維度數（1D vs 3D vs 高維 RL）
- 訊號來源（recurrence / visit / rebuttal / reward）
- Action（consolidate / decay / evict / route）

**沒有一個系統是 non-linear 或 learned-threshold**——全部是線性加權或 hard threshold。這意味著：對 Hermes 而言，**選哪一個 trigger 不是 deep 設計決策，而是「你想要幾個維度的信號」這個輕量決策**。

**對 Hermes 的意義**：`heartbeat_learning.py` 的 drift penalty 目前是純 time-based half-life（`38d`）。把它升級成 MemoryOS-style 3D heat score 是一行改動的層級——加 `retrieval_count_30d` 和 `task_association_count` 兩個維度，權重用 `α=0.5, β=0.3, γ=0.2`（visit 為主、關聯次之、recency 兜底）。

**可行動下一步**:
1. 在 `heartbeat_learning.py` 的 `compute_drift_penalty(distillate)` 函式加 heat score 分支（與 time-based half-life 並存），用 feature flag `HERMES_DRIFT_MODEL=time|heat|hybrid` 控制。
2. 跑一個 30 天的 A/B：time-based vs heat-based，比較 vault size 穩定性和 task context 命中率。
3. 如果 heat-based 顯著優於 time-based（>10% hit rate gain），正式切換並刪除 time-based 分支——**不要保留 hybrid**，文獻證明多觸發器並存會造成蒸發決策不一致。
4. 預計工作量：半天改 code + 1 個月 A/B 觀察 + 半天切換。短期成本低、長期可維護性高。

## Cross-Cutting Theme 3: 分層架構的「離散指標 vs 連續評分」是 unaddressed 的設計 tradeoff

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine

H-MEM 用**positional index encoding**（離散 pointer，類似 OS 的 inode）做層級路由；其他三個（MemoryOS、RecMem、SAGE）都用**連續相似度評分**（cosine / heat / policy score）做層級判斷。

這個差異是 structural，不是 implementation detail：
- 離散 pointer（H-MEM）：O(1) 路由，但 index 必須手動或半自動維護；錯一個 pointer 就 miss 整個子樹
- 連續評分（其他）：O(k) 比較，無需維護 index；但 threshold 調不好會全 miss 或全 hit

**這個 pattern 在任何單篇筆記中都不會被命名**，因為每篇只描述一個系統。把它們放在一起才看到：2026 文獻在「層級記憶的路由機制」上**沒有共識**——H-MEM 是唯一押注離散路線的，其他全部走連續。

**對 Hermes 的意義**：Skills 的分層（trigger condition → action → verification，[1] 已點出）目前是**手動維護的層級**——相當於 H-MEM 的離散 pointer。30 個 skill 還能手動管理，300 個就會 pointer drift。

但 Hermes 的 skill 總量級（百級以下）不需要 H-MEM 的 discrete index overhead——**連續評分是更合適的選擇**。具體：在 skill retrieval 前先做一次 embedding similarity top-k（k=5），再讓 LLM 在這 5 個中挑。

**可行動下一步**:
1. 在 `skill_loader.py` 評估當前的 skill 載入機制是 discrete pointer 還是 continuous scoring（幾乎肯定是前者：線性遍歷 skills 字典）。
2. 如果是 discrete，**不必立刻改**——scale 到 50 個 skill 之前都還能撐。但要在 `hermes-config.yaml` 加註解：「skill count > 50 應切換到 embedding-based retrieval」。
3. 把 [1] 提到的「H-MEM position index 移植到 Hermes skills」標記為 **不採用**——離散 pointer 對小量級 skills 是 over-engineering，連續評分就夠。
4. 預計工作量：評估 30 分鐘，註解 5 分鐘，不實作。

---

## Meta-Observation: 為什麼這 4 篇筆記其實是同一篇的不同切面

這 4 篇 2026-06-09 的探索表面上分散在 4 個 arXiv 編號、4 個 venue（EACL/ACL Findings/EMNLP/NeurIPS 2026），但內容是**同一個研究問題的四個切面**：

- [1] H-MEM + RecMem = **分層組織**（structural organization）
- [2] MemoryOS = **層級間遷移**（inter-tier transition）
- [3] SAGE = **自我演化**（closed-loop self-improvement）
- [4] Governed Memory + OCL + Survey = **跨節點治理**（multi-agent governance）

把它們疊起來得到一個「完整的 LLM agent 記憶系統」應該有的所有元件：分層（[1]）、遷移（[2]）、閉環（[3]）、治理（[4]）。**沒有一個系統全部具備**——這就是 Hermes 的機會窗口，也是為什麼這 4 篇一起讀比單讀價值高 3 倍。

**對 Hermes 的最終建議**：WS-035 (`PolicyInterceptor` + `heartbeat_learning.py` + `drift_penalty`) 是一個**尚未閉環的記憶系統**。把它升級成「分層 + 觸發 + 閉環 + 治理」四件套的具體順序：
1. **先做 Theme 1**（reader feedback log）——這是缺失最嚴重的，其他三個的文獻已經部分覆蓋 Hermes 現狀
2. **再做 Theme 2**（heat score trigger）——取代純 time-based
3. **Theme 3 暫緩**（skill 連續評分）——scale-driven，不急
4. **Theme 4 治理**（Governed Memory tiered routing）——目前 Hermes 是 single-agent，暫時不需要

預計總工作量 2-3 天 code change，1 個月 A/B 觀察。
