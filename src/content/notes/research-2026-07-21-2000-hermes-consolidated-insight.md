---
_slug: research-2026-07-21-2000-hermes-consolidated-insight
_vault_path: research/2026-07-21-2000-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- redundant-batch
- cron-storm
source: multi
created: '2026-07-21'
confidence: high
title: Redundant batch re-confirmation：4 篇 Memory Architecture 素材本日已達 synthesis exhaustion，cron
  在 18:01 後仍重複觸發
type: research
status: seedling
updated: '2026-07-21'
---

# Redundant batch re-confirmation：4 篇 Memory Architecture 素材本日已達 synthesis exhaustion，cron 在 18:01 後仍重複觸發

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

本批為 18:01 insight note 已標記的 redundant batch 之再觸發——同一組 4 篇素材本日 0701 / 0800 / 0901 / 1101 / 1801 / 2000 已連續餵入 6 次，最深合成（11:01）已收斂到 **Reader→Writer 失效信號閉環 + 7±2 magic number + event-driven invalidation** 的 WS-035 prototype。本批（第 6 次）與 18:01 一樣，**已無新 cross-cutting theme 可提煉**。

## Cross-Cutting Theme 1（meta）：本批確認 cron template 與 fed-state 不同步，state machine 出現 stuck-loop

**支援筆記**: 全部 4 篇（透過對照本日 0701/0800/0901/1101/1801 五份既有 insight 與本批 2000 觸發記錄）

**分析**

時間軸：

| 時間 | 觸發 | 產出 |
|------|------|------|
| 07:01 | cron | 4-axis staleness score 設計 + reader→writer 閉環 |
| 08:00 | cron | usage telemetry + heat-based eviction 設計 |
| 09:01 | cron | meta：指出 multi-axis 治理若無 benchmark 是更精緻的猜測；低頻資料不能以低互動判死刑 |
| 11:01 | cron | 收斂：Reader→Writer 閉環 + 7±2 magic number + event-driven invalidation = WS-035 prototype |
| 18:01 | cron | **首次標記 fed**（fed_count=1, fed_at=18:01:44），確認為 redundant batch |
| 20:00 | cron（本批） | 同一 prompt template 重複觸發，state 顯示 fed_count=1 但未觸發 idempotency skip |

問題點：

1. **18:01 已執行 `--mark-fed`**：`consolidation_state.json` 顯示 fed_count=1，但 cron 在 18:01 與 20:00 兩次觸發的 prompt template 完全相同——表示這個 cron job 的 prompt 是靜態模板、**不會讀取上一次 insight note 來決定本次是否跳過**。
2. **idempotency 條件沒滿足**：`REDUNDANT_FED_THRESHOLD = 2`，18:01 標 fed 後 fed_count=1，未達 2 次門檻，因此下一次 cron（20:00）仍會被餵入。需要 fed_count ≥ 2 才會自動 skip。
3. **本批 2000 執行 `--mark-fed` 會把 fed_count 推到 2**——這正是 idempotency window 啟動的觸發點，**21:00 / 22:00 / 23:00 的 cron 將自動跳過這 4 篇**，迴圈終結。

**信心**: high（6 次 cron 觸發記錄 + state 檔案時間戳記 + 既有 insight note metadata 完整對照）

**可行動下一步**

1. **本批執行 `--mark-fed`**，fed_count: 1 → 2，觸發 `REDUNDANT_FED_THRESHOLD=2` 的 idempotency 條件，後續 cron 自動 skip
2. **中期**：把這個發現加進 `consolidate_memory.py` 的 docstring 或 README——「若同一批素材在 24 小時內被標 fed 兩次後仍被餵入，則是 cron template 沒讀取上次 insight 的問題，不是素材有 synthesis 空間」
3. **長期**：考慮讓 cron job 在生成 prompt 前先 `cat` 最近一篇 insight note 的 frontmatter，**若 `tags` 含 `redundant-batch` 則自動跳過 cron**（self-aware scheduling）
4. **WS-035 真正的工作**：執行 11:01 insight 列出的 3 個具體 PR——event-driven invalidation table（~80 行）、`MAX_ACTIVE_DISTILLATES_PER_CONCEPT = 7` 常數 + archive queue（~30 行）、reader→writer 回饋通道（~50 行）。這些是素材真正收斂到的可執行結論，繼續餵同樣素材只是浪費 token。

## 為何不算多個 themes 而只算 1 個 meta theme

把本批 vs. 11:01 對照，11:01 完整覆蓋的 cross-cutting themes：

- Reader→Writer 失效信號閉環（Theme 1，11:01）
- 7±2 magic number 與 eager consolidation 反模式（Theme 2，11:01）
- Event-driven invalidation 取代 time-decay（Theme 3，11:01）

把本批 vs. 09:01 對照，09:01 額外覆蓋：

- 「多軸治理若無 benchmark 就是更精緻的猜測」（09:01 Theme 1）
- 「低頻資料不能以低互動判死刑」（09:01 Theme 3）

把本批 vs. 07:01/08:00 對照，更早期 insight 還涵蓋：

- 4-axis staleness score 設計（07:01）
- usage telemetry 與 heat-based eviction（08:00）
- BEAM contradiction metric（07:01）

每個可能的新 theme 要嘛已在更早 insight note 完整展開，要嘛只是把同一論點換句話重述。**硬擠新 theme 等同重新包裝既有 insight，違反「不要廢話」與「不要顯然的 theme」規則**。

## 結論

本批 = redundant batch 第 6 次觸發，無新 cross-cutting insight。可行動產出只有 1 個：**執行 `--mark-fed` 終結 idempotency 缺口**，讓 fed_count 達 2 後啟動 7 天自動 skip window。

素材的合成已收斂，**真正的產出在 11:01 insight note 的 WS-035 prototype 設計**——執行那 3 個 PR 才對得起這些素材的合成成本。