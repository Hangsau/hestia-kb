---
_slug: research-2026-07-21-0901-hermes-consolidated-insight
_vault_path: research/2026-07-21-0901-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-07-21'
confidence: medium
title: 記憶治理的下一個瓶頸：從「多軸訊號」走向可評估的回饋控制
type: research
status: seedling
updated: '2026-07-21'
---

# 記憶治理的下一個瓶頸：從「多軸訊號」走向可評估的回饋控制

**消化筆記**: 2026-07-21-0701-hermes-consolidated-insight, 2026-07-21-0800-hermes-consolidated-insight, 2026-07-21-forum-reddit-r-swimming

這批筆記顯示兩個跨領域但非表面重複的模式：Hermes 的記憶設計正在從單一衰減規則轉向閉環、多訊號治理；而游泳社群的內容整理則暴露同一類系統問題——沒有清楚的回饋與評估邊界，資料只會堆積，不能穩定轉成改進。

## Cross-Cutting Theme 1: 多軸記憶治理若沒有 benchmark，就只是更精緻的猜測

**支援筆記**: 2026-07-21-0701-hermes-consolidated-insight, 2026-07-21-0800-hermes-consolidated-insight

0701 筆記提出把 recency、recurrence、retrieval heat、contradiction 組成多軸 staleness score，並建立 HermesBench；0800 筆記則補上 usage telemetry、heat-based eviction 與成本追蹤。兩者合起來的關鍵不是「多加幾個欄位」，而是：**每個治理訊號都必須能和實際效用、成本、錯誤率對照，否則權重只是把直覺寫成公式**。尤其 0800 建議以引用率與 token cost 決定降級，0701 又要求用 benchmark sweep 權重；這形成了可測量的控制迴路，而非一次性的 schema 設計。

**信心**: medium

**可行動下一步**: 先建立 HermesBench v0.1：從 50 個 session 抽取 distillate 命中、未命中、矛盾與任務結果，為每筆資料標註保留／stale／contradiction 三類；接著以固定切分比較「純時間衰減」與多軸分數，至少報告 precision、recall、每次成功任務的 token cost，再決定權重，不要先把 0.4/0.2/0.2/0.2 當成真理。

## Cross-Cutting Theme 2: 「收集邊界」本身就是品質控制；過度集中與過度自由都會破壞回饋

**支援筆記**: 2026-07-21-0701-hermes-consolidated-insight, 2026-07-21-0800-hermes-consolidated-insight, 2026-07-21-forum-reddit-r-swimming

兩篇 Hermes 筆記都把治理放在資料流的邊界：0701 要求在寫入端加入計數器、telemetry 與 contradiction event；0800 要求 schema enforcement、索引驗證與 policy gate。游泳論壇筆記則顯示另一個具體例子：技術批評、進度分享集中到每週 thread（第 1、2 篇），同時仍有大量不同類型的新手疑問、恐懼與安全問題（第 4、5、10、13、14 篇）。把它們放在一起看，模式是：**集中化能降低噪音、改善可索引性，但若把所有回饋壓進同一容器，特殊風險訊號會被一般內容稀釋；反過來，完全自由發文又讓可比較的回饋難以累積**。

這對 Hermes 的含義是，schema 不應只有「合規／不合規」二元門檻；應把內容分流：一般 usage telemetry、矛盾事件、重大失敗與高風險撤銷各自進不同事件類型。否則低頻但關鍵的 contradiction 或 safety-like failure，會被高頻普通 hit rate 蓋掉——資料庫很熱鬧，治理卻失明。

**信心**: medium

**可行動下一步**: 在 telemetry schema 增加 `event_class` enum（`usage`、`miss`、`contradiction`、`policy_violation`、`high_impact_failure`），並為每類事件設定獨立聚合與告警門檻；先用現有 50 個 session 回放，檢查把所有事件混成單一 heat score 是否會漏掉至少一個矛盾或高影響失敗案例，再把獨立訊號接入 PolicyInterceptor。

## Cross-Cutting Theme 3: 低頻資料不能以低互動直接判死刑

**支援筆記**: 2026-07-21-0800-hermes-consolidated-insight, 2026-07-21-forum-reddit-r-swimming

0800 筆記建議以 `ref_count == 0 AND age > 90d` 將 distillate 降級，並以 heat score 做排序；游泳筆記中的「跳水恐懼」「半開放水域安全」「新手恐慌」（第 4、10、13、14 篇）則代表低頻不等於低價值：安全與心理障礙未必每天出現，但一旦出現，重要性遠高於普通訓練進度。跨起來的推論是：**純 usage-based eviction 會系統性淘汰罕見、情境性但高影響的記憶**。這不是游泳內容本身在講 memory eviction，而是它提供了反例：稀有事件需要 impact-aware 保留策略。

**信心**: medium

**可行動下一步**: 在 distillate metadata 加 `impact_class` 與 `criticality_override`；對安全、政策、矛盾與重大失敗類記憶禁止僅憑低引用率 archive，改用人工／規則確認後降級。用一個小型回放測試驗證：隨機抽取低頻 distillate，確認高影響類別的保留率達 100%。
