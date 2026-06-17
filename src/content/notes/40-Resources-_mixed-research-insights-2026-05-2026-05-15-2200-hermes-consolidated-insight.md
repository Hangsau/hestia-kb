---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-2200-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-2200-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: low
title: 無可 Consolidation 的 Insight（單篇筆記）
updated: '2026-06-15'
type: research
status: budding
---

# 無可 Consolidation 的 Insight（單篇筆記）

**消化筆記**: 2026-05-15-camel-code-then-execute

本次未消化筆記僅 1 篇。CaMeL 原典深讀本身已經是跨來源的 synthesis（整合了 CaMeL paper、Simon Willison Dual-LLM、Action-Selector、Design Patterns paper 四層防禦光譜），但缺乏其他**未消化筆記**來進行跨主題連結。

## 筆記內的既有 Synthesis（非本次產出）

該筆記內部已完成的跨來源連結（供未來 consolidation 參考）：

| 防禦層 | 安全模型 | Hermes 對應 |
|--------|----------|-------------|
| Design Patterns paper | 機率性 | PT-E 列入 exploration 強制規則 |
| Dual-LLM (Simon) | 架構性，有 data flow 漏洞 | — |
| CaMeL (DeepMind) | 架構性保證（data provenance） | PT-E 的學術基礎 |
| Action-Selector | 最小權限 | Hermes tool 固定 schema |

## 潛在未來連結（等更多筆記進入未消化池）

1. **Capability tracking 的輕量實作** — 若後續有筆記討論 tool-level trust annotation，可與 CaMeL 的 data provenance 模型對照
2. **Policy-as-config UX** — 若後續有筆記討論 Hermes 的 security policy 設計，CaMeL 的 policy 定義門檻問題是重要參考
3. **AgentDojo benchmark** — 若後續有筆記討論 agent 安全評估，77% vs 84% 的 trade-off 數據可做基準

## 可行動下一步

無。待累積 ≥2 篇未消化筆記後再進行 consolidation。
