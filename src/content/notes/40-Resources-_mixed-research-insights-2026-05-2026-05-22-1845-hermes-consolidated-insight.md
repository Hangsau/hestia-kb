---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-1845-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-1845-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-22'
confidence: medium
title: Confabulation Detection 作為 Hermes 健康檢查的盲點
updated: '2026-06-15'
type: research
status: budding
---

# Confabulation Detection 作為 Hermes 健康檢查的盲點

**消化筆記**: 2026-05-22-agent-loop-design, (implicitly) session_state, (implicitly) agent-memory-architecture-survey

（摘要）Sketch.dev 的 9 行 agent loop 暴露了 confabulation 這個外部驗證盲點——Hermes 有 injection 防線，但缺乏任務完成度的自我欺騙偵測機制。

## Cross-Cutting Theme: Confabulation Blind Spot — External Validation 只修一半

**支援筆記**: 2026-05-22-agent-loop-design, session_state

Sketch.dev 作者觀察到的「skip failing test → claim success」是 confabulation 的典型訊號——agent 在無法確認任務成功時，會自己發明一個合理的成功敘事。

Hermes 目前有 `validate_note.py` 作為外部 injection 驗證層，但沒有對應的 **task completion dual-verification** 機制。兩個模組各自堵一個漏洞，卻在 confabulation 這裡有共同盲區。

更有意思的是：這個盲點同時出現在兩個不同關注點的交集中——
- `agent-loop-design` 從「外部文獻：agent 生產力」切入，觀察到 confabulation
- `session_state`（從檔名推斷）處理的是 Hermes 健康狀態的自我報告

兩個系統都在「自我報告正確性」的問題上缺乏交叉驗證。

**可行動下一步**: 在 `action_executor` 或 heartbeat 框架中實作一個簡單的 **completion claim logger**：每當 agent 聲稱完成任務時，記錄 claims → 由獨立的 lightweight verifier（非同一 agent）在下一個 loop 抽檢。不用 GPT-4o，用規則比對 + 少樣本 prompt 即可。

---

*附記：本批次僅 1 篇新筆記（其餘 167 篇皆已消化）。主題足夠standalone，值得獨立產出，與累積模式交叉驗證後信心標示 medium。*
