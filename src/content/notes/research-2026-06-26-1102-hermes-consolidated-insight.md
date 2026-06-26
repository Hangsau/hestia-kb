---
_slug: research-2026-06-26-1102-hermes-consolidated-insight
_vault_path: research/2026-06-26-1102-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- agent-memory
- eval-paradox
- bounded-systems
source: multi
created: '2026-06-26'
confidence: high
title: 2026-06-09 記憶群（第二輪消化）：Eval 黑洞 × 收斂邊界 × 密度飽和
type: research
status: seedling
updated: '2026-06-26'
---

# 2026-06-09 記憶群（第二輪消化）：Eval 黑洞 × 收斂邊界 × 密度飽和

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

2026-06-20 的 insight note（檔名 0902）已經從「trigger / feedback / schema」三個角度切過這四篇筆記。本次重消化（reset 後再跑）的任務是找出**前三個 theme 之下的隱藏變數**——也就是 2026-06-20 沒看到的、單篇筆記各自也沒強調的、但四篇並排才浮現的次級模式。

## Cross-Cutting Theme 1: 表面指標 vs 結構性指標的「Eval 黑洞」

**支援筆記**: llm-agent-memory-governance-synthesis（最強）、memory-os、hmem-recmem、sage
**信心**: high

把四篇的量化結果攤開來，會發現一個一致的「指標分裂」現象——**headline metric 漂亮，但底下藏著結構性失敗**。

| 系統 | Headline metric | 結構性 metric | 落差 |
|------|----------------|--------------|------|
| OCL（governance） | Success Rate 94% → 96% | **Valid Success Rate 12% → 96%** | +84pp |
| OCL | — | **Unsafe Rate 88% → 0%** | -88pp |
| MemoryOS | Avg F1 +49% vs MemGPT | Temporal F1 +118% vs Single-Hop +32% | uneven across task types |
| Governed Memory | LoCoMo 74.8% | vs human 87.9% (-13.1pp) | ceiling effect |
| RecMem | -87% token cost | F1 未報告（vs MemoryOS 同 task） | trade-off hidden |
| H-MEM | Adversarial QA 63.3 vs baseline 58.8 (+4.5) | Single-Hop +1.7 (noise level) | wins where it matters |

**OCL 的 12% vs 96%** 是整組數據中最刺眼的一行——「表面上 94% 成功，實際上 88% 不安全」。這個落差不是 OCL 獨有的，是**所有只回報單一指標的系統都潛藏的失敗模式**。

四篇並排後才看得出來這個 pattern：
- **MemoryOS** 報 Avg F1，但 Temporal F1 是 Single-Hop 的 3.7 倍 → 系統對任務類型極度敏感
- **RecMem** 報 token 效率，但 F1 vs 同 task 的對手未在同 table 出現 → 你無從判斷「省下的 token 是值得的」
- **SAGE** 報 two-rounds 達 multi-hop SOTA，但 baseline rounds 的對齊未明確
- **Governed Memory** 同時報 99.6% fact recall 和 LoCoMo 74.8%，但**兩個 metric 的差距（25pp）本身就是一個訊號**：recall 不等於 contextual use

對 Hermes 的 `track_memory_growth.py` 的意義：目前追蹤的是 distillate 數量（growth）和 reader 引用次數（N_visit），但**從未追蹤「這個 distillate 是否真的對 task outcome 有貢獻」**。Hermes 沒有 OCL 的 Valid Success Rate 等價物——一個 30 個 distillate 的 vault 可能表面很健康，但其中 70% 從未被任何 task context 真的引用過。

**可行動下一步**（具體可執行）:
1. 在 `heartbeat_learning.py` 增設 `outcome_attribution.py` 模組（建議先做 MVP，不用 LLM）：
   - 每次 task 結束時，比對 task prompt 與實際被引用的 distillate 集合
   - 簡單 heuristic：如果 task 結論包含 distillate 的核心概念（substring match），標記 `contributed=true`
   - 進階版（v2）：LLM-as-judge 評估 distillate 是否對 task 解決有 causal role（0.5s 開銷）
2. 在 `track_memory_growth.py` 新增 `effectiveness_ratio = Σ(distillates_used_in_completed_tasks) / Σ(distillates_total)`
3. **KPI target**: effectiveness_ratio ≥ 0.4（70% distillate 從未被引用 = 結構性失敗）。若 < 0.4 → 觸發 distillation 暫停，進入 audit mode

**預期效益**: 把 Hermes 從「distillate 計數器」升級為「distillate 投資報酬率追蹤器」。避免 vault 變成 collectibles 庫存。

---

## Cross-Cutting Theme 2: 收斂邊界（Bounded Processes）是 2026 記憶系統的隱藏設計約束

**支援筆記**: sage（最強）、memory-os、llm-agent-memory-governance-synthesis、hmem-recmem
**信心**: high

四篇獨立的 paper/系統都明確設定了**收斂/蒸發/終止的邊界**，但這個性質在單篇閱讀時容易被當作「hyperparameter」忽略，並排後才浮現——這是 2026 記憶系統的**共同設計哲學**：

| 系統 | 收斂邊界 | 邊界類型 |
|------|---------|---------|
| SAGE | **2 rounds** → multi-hop SOTA | algorithmic termination（self-evolution loop） |
| MemoryOS STM | **7 pages** fixed | capacity cap（記憶體上限） |
| MemoryOS MTM | **200 segments** → heat eviction | capacity cap + heat-driven replacement |
| MemoryOS User KB | **100 entries** FIFO | capacity cap（rotation） |
| MemoryOS User Traits | **90 維度** fixed | schema cap（維度上限） |
| RecMem | θcount=5 + θsim=0.7 | trigger threshold |
| H-MEM | **4 layers** | hierarchy depth（ablation 確認最優） |
| Governed Memory | **~7 memories/entity** saturation point | density curve elbow |
| Governed Memory routing | fast ~850ms / full ~2-55s | latency budget |

**核心訊號**：每個系統都預先設定「什麼時候該停」。這不是過度工程——是**防止記憶無限成長的硬約束**。

對 Hermes 的現狀：
- `consolidate_memory.py` 的批次大小是 6（hyperparameter）但**沒有總量上限**——vault 可以無限增長
- `heartbeat_learning.py` 的 distillate 寫入**沒有飽和檢查**——每次新筆記都產生新 distillate，舊的不退役
- `track_memory_growth.py` 確實追蹤 growth，但**只追蹤不約束**——這是觀測器，不是 throttle

**未解的設計問題**：四篇都給了**值**（7, 200, 100, 90, 2, 4），但**沒有任何一篇解釋「這些值怎麼決定的」**。MemoryOS 沒報告 7 vs 14 vs 28 的 ablation，H-MEM 沒 sweep layer=3 vs 5，RecMem 沒說 θcount=5 是 LoCoMo-specific 還是一般化。**這是一個共同的研究 gap：收斂邊界是經驗值，不是理論導出**。

**可行動下一步**（具體可執行）:
1. 在 `consolidate_memory.py` 新增 `vault_capacity.yaml` config：
   ```yaml
   vault_limits:
     max_distillates: 2000          # 對齊 MemoryOS MTM 的 200（×10 scale）
     max_age_days_no_visit: 90      # 對齊 WS-035 的 38d half-life × 2.5
     max_per_concept: 5             # 防止單一概念佔滿 vault
     min_effectiveness_ratio: 0.4   # Theme 1 的 KPI
   ```
2. 在 `consolidate_memory.py` 開頭加 capacity check：
   - 若 `count(active_distillates) > max_distillates` → 進入 compaction mode（按 effectiveness 排序，保留 top 80%）
   - compaction 是 bounded process：單次跑 ≤ 100 entries deletion，避免 spike
3. 在 `track_memory_growth.py` 新增 `growth_velocity` metric（distillates/week）+ `saturation_warning`（當連續 4 周 growth_velocity > 50/week 但 effectiveness_ratio 下降 → 警告 vault 飽和）
4. **不**自己重新決定這些值——直接對齊 MemoryOS 的 200 / 100 / 90，因為這是目前唯一 production-tested 的數字集合

**預期效益**: 把 vault 從「無界增長」變成「bounded resource」。逼 Hermes 進入競爭狀態——新 distillate 要擠掉舊的，這會自動暴露哪些 distillate 是低價值的（Theme 1 的 eval feedback 自然浮現）。

---

## Cross-Cutting Theme 3: 密度飽和（Density Saturation）的隱含設計語言

**支援筆記**: llm-agent-memory-governance-synthesis（最強）、memory-os、hmem-recmem、sage
**信心**: medium（推測成分中等，因為飽和曲線只在 Governed Memory 明確量化）

把四篇的容量設定攤開來，會浮現一個沒人明說但都在用的設計假設：**記憶的價值不是線性的，而是有 elbow point**。

| 系統 | 飽和點 | 證據 |
|------|-------|------|
| Governed Memory | **~7 memories/entity** | "+24% from 0→3, then plateau"（明確量化） |
| MemoryOS STM | **7 pages** | 固定 capacity（unablationed but stable） |
| MemoryOS User KB | **100 entries** | 固定 capacity（FIFO） |
| MemoryOS User Traits | **90 維度** | 固定 schema |
| RecMem subconscious | implicit | 沒有明示上限 |
| SAGE graph | unbounded growth | 但靠 self-evolution rounds bounded by 2 |
| H-MEM | 4 layers | depth fixed, width unbounded |

**Governed Memory 的 ~7 是唯一有量化曲線的**：從 0 → 3 memories 跳 +24%，從 3 → 7 之後幾乎 plateau，超過 7 之後個人化品質不增反降（noise / interference）。這個 elbow point 暗示**記憶系統有「甜蜜點」，超過之後是負報酬**。

對 Hermes 的意義：vault 目前可能已經過了 elbow point——一個 agent 有 200+ distillates 真的比有 30 個更聰明嗎？這個問題**從未被測量過**，因為 `track_memory_growth.py` 只追蹤 growth，不追蹤 marginal utility。

**推測性的觀察**（信心 medium）：如果 Hermes 的 vault 已經超過甜蜜點，那 Theme 1 的 effectiveness_ratio 應該會顯示同樣的 pattern——新 distillate 對 task outcome 的邊際貢獻遞減，甚至變負（context dilution）。這是需要在跑完 Theme 1 的 KPI 後才能驗證的假設，不是現在能下的結論。

**可行動下一步**（具體可執行）:
1. 在 `track_memory_growth.py` 新增 `marginal_utility_curve.py`：
   - 按 distillate 加入時間排序，分 bin（每 50 個一 bin）
   - 對每個 bin 計算 `effectiveness_ratio`（Theme 1 的 metric）
   - 繪製曲線並標記 elbow point（最大 effectiveness ratio + 第二階導數由正轉負的位置）
2. **預期發現**（假設）：Hermes 的 elbow point 大約在 200-300 distillates。如果目前 vault > 1000，effectiveness_ratio 可能 < 0.2——這意味著 80% 的 vault 是 dead weight
3. 若確認 elbow point 存在，**觸發 Theme 2 的 compaction mode**，把 vault 砍到 elbow point 上方 20% 的安全 buffer
4. 將 marginal_utility_curve 結果存成 `~/obsidian-vault/research/2026-MM-DD-vault-elbow-analysis.md`，作為未來 capacity tuning 的 empirical baseline

**預期效益**: 把「vault 應該多大」從哲學問題變成可測量的 empirical question。如果 elbow point 真的在 300，那目前 1000+ 的 vault 是結構性浪費——每天 retention / backup / search 的成本都乘以 3.3 倍。

---

## 三個 Theme 的關係

這三個 theme 在概念上是一個因果鏈：

```
Theme 2 (Bounded Processes)
  ↓ 提供「什麼時候停」的硬約束
Theme 3 (Density Saturation)
  ↓ 揭示「超過甜蜜點就負報酬」的曲線
Theme 1 (Eval Paradox)
  ↓ 解釋「為什麼沒人發現」——因為只看 headline metric
```

**訊號的優先級**（如果只能做一個，做 Theme 1）：Eval paradox 是其他兩個的前置——沒有 effectiveness_ratio，就無法定位 elbow point（Theme 3）；沒有定位 elbow point，capacity cap（Theme 2）的數字就只能瞎猜。先建 KPI，再測飽和，最後定容量。

---

## 與 2026-06-20 0902 insight 的互補性

2026-06-20 的 insight 處理了「trigger / feedback / schema」三個**正向設計**問題。本次消化的三個 theme 處理的是**反向約束**問題——不是「記憶系統應該做什麼」，而是「記憶系統什麼時候該停、什麼時候該被評估、什麼時候表面指標會騙人」。兩者合在一起是 WS-035 drift penalty 的完整設計棧：

- 2026-06-20：trigger 設計（何時 consolidate）、feedback 設計（如何更新）、schema 設計（如何組織）
- 2026-06-26（本篇）：eval 設計（如何衡量）、termination 設計（何時停）、saturation 設計（多大夠了）