---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-1900-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-1900-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- prompt-caching
source: multi
created: '2026-05-15'
confidence: medium
title: DeepSeek Cache Semantics × Timestamp Architecture：兩個筆記合在一起才浮出的隱憂
updated: '2026-06-15'
type: research
status: budding
---

# DeepSeek Cache Semantics × Timestamp Architecture：兩個筆記合在一起才浮出的隱憂

**消化筆記**: `2026-05-15-deepseek-cache-timestamp-trace`, `2026-05-15-prompt-caching-kv`

把 DeepSeek 的 full-match cache prefix unit 機制（筆記 1）和 ngrok/HN 對 prompt caching 的 general 理解（筆記 2）疊在一起後，發現兩個單篇各自沒講到的合成問題：timestamp 位置的嚴重性被低估，以及免費 tier 正掩蓋架構債。

---

## Cross-Cutting Theme 1: Full-match 語義讓 timestamp 位置從「百分比優化」升級為「結構性阻斷」

**支援筆記**: `2026-05-15-deepseek-cache-timestamp-trace`（Insight 1: Cache Prefix Unit 機制）, `2026-05-15-prompt-caching-kv`（ngrok: partial prefix match, HN duggan: 移 timestamp 到尾部改善率 20-40%）

### 分析

ngrok 文章和 HN duggan 的討論都建立在 **partial prefix match** 的假設上：prompt 開頭有 timestamp → timestamp 之前的部分全部 cache miss，但 timestamp 之後如果 match 仍可 reuse。duggan 的回報是移 timestamp 到尾部後 cache rate 從 30-50% 提升到 50-70%，改善幅度約 20 個百分點。

但 DeepSeek 的機制不同。DeepSeek 的 cache prefix unit 要求 **full match**（筆記 1），而且 common prefix detection 需要 2+ 個請求才能將一段 prefix 持久化為 cache unit。

這意味著：timestamp 卡在 system prompt 中間（筆記 1 確認是 #11 位置）時，DeepSeek 的 common prefix detection 只會看到兩種 pattern：

- **Pattern A**：`[persona...skills...context] + [timestamp_X] + [platform hints]`（session 1）
- **Pattern B**：`[persona...skills...context] + [timestamp_Y] + [platform hints]`（session 2）

如果 timestamp 後還有內容（platform hints），common prefix detection 偵測到的「共用 prefix」是 `[persona...skills...context]`——這一段理論上可以被持久化。但 **fixed token interval units**（筆記 1 Insight 1）可能把 system prompt 切成多段，timestamp 落在哪個 unit 就會 invalidate 那個 unit。

關鍵不確定性：如果 timestamp 落在某個 fixed-interval unit 的開頭附近，是否會導致那個 unit 永遠無法成為 cache unit（因為每次 session 都不同）？如果那個 unit 同時包含了 persona 的尾部，那 persona 的 cacheability 就被拖累了。

**結論**：在 partial-match 語義下，移 timestamp 是優化（改善率 20pp）。在 full-match 語義下，不移 timestamp 可能讓 stable prefix 的 cacheability 歸零。嚴重性完全不同。

### 可行動下一步

1. 實測：先不改任何 code，跑 5 個獨立 session（cron 模式），檢查每個 session 的 `usage.prompt_cache_hit_tokens` 是否為 0。若全為 0 → 證實 full-match + timestamp-in-middle = 零命中。
2. 改 code 把 timestamp 移到 system prompt 最尾端（`run_agent.py:4958` → 移到 `return` 前），再跑 5 個 session，看 `prompt_cache_hit_tokens` 是否開始出現正數。

---

## Cross-Cutting Theme 2: 免費 tier 是架構債的隱形斗篷——零成本訊號移除自然回饋迴路

**支援筆記**: `2026-05-15-deepseek-cache-timestamp-trace`（Insight 4: DeepSeek 免費但 cache 仍有意義）, `2026-05-15-prompt-caching-kv`（跨文章 Synthesis: agent-cost-curve 串聯）, `2026-05-15-agent-architecture-design`（被筆記 1 引用）

### 分析

筆記 2 的跨文章 synthesis 提到一條故事線：agent-cost-curve → context 成長導致成本爆炸 → prompt caching 是 provider 端解法。這是標準的「成本驅動優化」邏輯鏈。筆記 1 在 Insight 4 補了一句：「DeepSeek 目前免費，cache hit/miss 不影響成本，但 latency 有差，而且未來換付費 provider 時這個優化會直接變成本節省。」

單看都合理，但合在一起暴露出一個合成問題：**Hermes 目前完全沒有 cache 相關的觀測性或指標**。沒有 dashboard、沒有 log aggregation、沒有 alert threshold、沒有 cost projection model。因為免費，所以沒人建。

這正是「免費的陷阱」：當 provider 不收錢時，架構層面應有的可觀測性基建就被跳過了。如果三個月後切到 Anthropic（cache read 是 $1.25/MTok vs regular $15/MTok），cache miss rate 從 100% 改善到 50% 的差距可能是每月數百美元。但到那時再回頭建監控、調架構，會比現在多好幾倍的摩擦。

更具體地說：筆記 1 提到的三個 cache prefix unit 類型（request boundary、common prefix detection、fixed token interval）對 Hermes 各自代表不同的優化目標，但**目前沒有任何 metrics 告訴我們哪一種 unit 在哪種 session pattern 下命中率最高**。沒有 data，就沒有 tuning。

### 可行動下一步

1. 在 `run_agent.py` 的 API response handling 加一行 log：紀錄 `prompt_cache_hit_tokens` 和 `prompt_cache_miss_tokens`（DeepSeek 已支援這兩個欄位，筆記 1 確認過）。
2. 建一個極簡觀測 script：從 log 撈最近 100 次 API call 的 cache hit/miss ratio，丟進 `~/obsidian-vault/dashboard/` 的筆記（方便 Hermes 自己讀）。
3. 基於實測數據做 cost projection：假設切到 Anthropic，目前的 cache 模式會花多少錢。

---

## 未追蹤（從被消化筆記繼承，尚未解決）

- [ ] 確認移動 timestamp 後不影響其他依賴 timestamp 位置的邏輯（`session_search` indexing、`hermes_state.py` 等）— 來自筆記 1
- [ ] DeepSeek 的 cache TTL 實測（幾小時到幾天太模糊）— 來自筆記 1
- [ ] Anthropic explicit cache control 對 Hermes session continuity 的價值 — 來自筆記 1 和 2
- [ ] Anthropic prompt caching pricing vs DeepSeek 目前成本比較 — 來自筆記 2
