---
_slug: research-2026-06-25-0906-hermes-consolidated-insight
_vault_path: research/2026-06-25-0906-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- silent-failure
- threat-model
- ws-035
source: multi
created: '2026-06-25'
confidence: high
title: 四套記憶系統的共同威脅模型是「Silent Failure」——而 Hermes 對它完全失明
type: research
status: seedling
updated: '2026-06-25'
---

# 四套記憶系統的共同威脅模型是「Silent Failure」——而 Hermes 對它完全失明

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 探索筆記（H-MEM、RecMem、MemoryOS、SAGE、Governed Memory、OCL、Storage→Experience survey）各自解決了記憶/治理的一個面向。把它們的「自我承認弱點」段落抽出來才看得出來：**四篇都收斂到同一個威脅類別——Silent Failure（無告警的可觀測失敗）**，而且每一篇描述的 silent failure 模式互不重疊，是**互補的失效向量**。今日先前三次 consolidation（00:00、02:01、08:01）已經處理了「多訊號 drift」、「reader-failure 閉環」、「substrate-policy 分離」、「schema-enforced 表示」、「magic number 5±2」等主題；本篇刻意避開這些已被覆蓋的角度，聚焦**威脅模型層**。

## Cross-Cutting Theme 1: 每一套記憶系統都有一個「自身承認但無法自測」的 silent failure

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

把每篇的 silent failure 段落抽出來並列：

| 系統 | 自我承認的 silent failure | 為什麼 silent | 哪個訊號可以揭露 |
|------|--------------------------|--------------|----------------|
| H-MEM | "沒人反駁不代表沒失效" (silent staleness) | user rebuttal 是 opt-in，使用者沒空回饋 = 系統以為一切正常 | semantic_drift_delta（新蒸餾與舊蒸餾的 embedding 距離突變） |
| RecMem | 低頻但高價值的用戶偏好會被忽略 | θcount=5 把 recurrence 當必要條件，從不重複的「一次性重要資訊」會沉到 Subconscious | user explicit query 對該資訊的命中率（如果反覆被問但回答不出 = 沉沒信號） |
| MemoryOS | 從未被檢索的「沉睡正確知識」會被蒸發 | heat score 沒有 visit = 0 → eviction，但這不代表 knowledge 是錯的 | reader-side miss_reason（task 問到但找不到）和蒸發清單的對照 |
| SAGE | hub over-expansion（高頻節點誤導傳播） | writer 把熱門實體寫成 hub，但 hub 不等於相關 | 結構性 propagation 失敗率（GFM 在 hub 周圍的 confidence decay） |
| Storage→Experience (§3.2) | "過時的知識在無明顯跡象下失效" | semantic representation 看起來仍相關，但條件已變 | event-driven invalidation（外部世界事件觸發 knowledge 的 condition invalidation） |
| OCL | "94% task success rate 隱藏 88% unsafe rate" | success metric 只量是否完成任務，不量是否合規 | Valid Success Rate（同時量 success 和 constraint satisfaction） |

**洞察**：六個 silent failure 中，**四個發生在 retrieval/distillation 路徑**（H-MEM、RecMem、MemoryOS、SAGE），**兩個發生在 execution governance 路徑**（Storage→Experience、OCL）。但路徑不同，本質相同：**系統的回饋閉環缺少「外部世界說你錯了」的訊號來源**——內部 metrics 全部 self-consistent，看起來都正常。

Hermes 目前最大的盲點不在於「哪個訊號該用」（前幾次 consolidation 已給出多訊號融合藍圖），而在於**「我們根本沒有任何 telemetry 能偵測 silent failure」**。`audit_cron.py` 報的是執行成功/失敗、token 用量、cron 是否跑了——這些都是 happy-path metrics。

**可行動下一步**：在 `~/.hermes/workspace/` 建一個 `silent_failure_canary.jsonl`（append-only 日誌），由三個獨立觸發源寫入：
1. `heartbeat_learning.py` 每次 distillation 時，計算新舊蒸餾的 embedding cosine，若 `Δcosine < -0.15` 寫一筆 `{type: "semantic_drift", old_id, new_id, delta}`
2. Task context retrieval miss 時（query 但 top-1 cosine < 0.5），寫 `{type: "retrieval_silence", query_hash, miss_top1_score}`
3. `talos` tool call 被 `PolicyInterceptor` 攔截時，寫 `{type: "policy_silence_intent", tool, blocked_reason, task_context}`

每月 cron 聚合一次，輸出「silent failure density per distillate / per skill / per tool」報表。前 30 天預期是空集合（因為從來沒收集過），但**這是第一次讓 silent failure 從不可觀測變成可觀測**。實作成本 < 80 行 Python。

**信心**: high（六篇獨立交叉驗證，每篇都自己承認 silent failure 存在但無法自測）。

## Cross-Cutting Theme 2: 「Self-Consistent Success Metric」是 production-grade 系統的隱形敵人

**支援筆記**: llm-agent-memory-governance-synthesis (OCL 12% → 96%), memory-os (heat score 自洽但無法辨識「沉睡正確」), sage (writer-reader loop 量化的是 retrieval F1，不是 knowledge correctness)

OCL 的量化結果是今日最有衝擊力的單一數據：

```
Baseline: 94% Success Rate / 12% Valid Success Rate / 88% Unsafe Rate / 205 executed violations
OCL:      96% Success Rate / 96% Valid Success Rate / 0% Unsafe Rate / 0 violations
```

**94% 看起來很好，但 88% 是 unsafe**。系統本身不知道這 88%——它的 self-consistent metric（task 完成了 = success）沒有 constraint satisfaction 維度。

把這個 pattern 套到其他三篇：

| 系統 | Self-consistent 報告的指標 | 看不見的維度 |
|------|--------------------------|-------------|
| H-MEM | F1 / retrieval latency | knowledge 是否仍然 ground truth（沒人檢查） |
| RecMem | 87% token reduction / episodic coverage | fine-grained facts 是否在 semantic refinement 後正確保留 |
| MemoryOS | LoCoMo 1st place / 36.23 F1 | 90-dim User Traits 是否隨時間 drift 而無人察覺 |
| SAGE | multi-hop QA 最佳排名 | hub-induced 錯誤傳播的 cumulative cost |

**洞察**：四篇的 self-consistent metrics 全部正向——但每一篇的 Per-source Insight 段落都承認「X 看起來好但有 Y 隱性問題」。**這不是巧合，這是 benchmark-driven research 的系統性偏誤**：所有記憶系統都用 LoCoMo F1、retrieval latency、token cost 當 proxy，但 proxy 不量 knowledge correctness、policy compliance、或 user goal alignment。

對 Hermes 的直接意涵：`audit_cron.py` 目前報的是 cron 執行成功率 + token 成本——和 OCL baseline 一樣 self-consistent 且危險。**Hermes 的 success metric 完全沒有「valid success」維度**——一次 cron 成功執行，但 policy 該 block 的 action 沒 block、stale distillate 該蒸餾沒蒸餾、reader 該 miss 的 distillation 沒 miss——這些都是 0% unsafe rate 的 OCL baseline 等級的成功。

**可行動下一步**：在 `audit_cron.py` 加 `valid_success_rate` 計算：
- 每次 cron 跑完，比對「應該發生 vs 實際發生」的 expected action 列表（從 `system-map` 讀）
- 例如 `heartbeat` cron 應該做的 distillation 數量 vs 實際做的數量
- 例如 `talos` policy interceptor 應該 block 的次數 vs 實際 block 的次數（用 shadow mode：把 policy 決定 log 下來，但不實際 enforce，30 天後比對 shadow vs actual）

這個 valid_success_rate 是 OCL 12%→96% 那個 96% 的本地化版本。預期初始值會低於直觀想像（可能 40-60%），但這正是揭露 silent failure 的開始。實作：擴展 `audit_cron.py` 為 `audit_cron_v2.py`，加 60 行 expected-vs-actual 比對邏輯。

**信心**: medium-high（OCL 直接量化 12%→96%，其他三篇的 Per-source Insight 段落提供間接驗證，但 Hermes 本地沒有量化）。

## 信心標示

- **Theme 1（Silent Failure 威脅模型）**: high confidence — 六篇獨立交叉驗證，每篇都明確列出自己的 silent failure 類別。
- **Theme 2（Self-Consistent Success Metric）**: medium-high confidence — OCL 直接量化驗證（12%→96%），其他三篇的失敗模式間接支撐 pattern，但 Hermes 本地需要先建 telemetry 才能驗證。

## 與今日先前三次 consolidation 的差異

- `2026-06-25-0000`：Reader-Failure 閉環 + Substrate-Policy 分離（**機制層**）
- `2026-06-25-0201`：Magic Number 5±2 + Token Economy + Schema-Enforced（**參數/成本/表示層**）
- `2026-06-25-0601`：多訊號 staleness + Reader→Writer 反饋迴路（**訊號層**）
- `2026-06-25-0801`：Drift Penalty 多訊號融合 + 各篇零件是同一架構（**架構層**）
- **本篇（0906）**：Silent Failure 威脅模型 + Self-Consistent Metric 偏誤（**威脅模型層**）

五個 insight 加起來構成一個完整的 multi-layer blueprint：機制 → 參數 → 表示 → 訊號 → 架構 → 威脅模型。每一層都需要單獨 telemetry 才能驗證——這是 Hermes 從研究 demo 走向 production-grade 的真正差距。