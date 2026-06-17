---
_slug: 40-Resources-_mixed-research-2026-06-03-0501-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-0501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: medium
title: 自主探索筆記整合：Agent 可靠性架構的雙層模式
updated: '2026-06-15'
type: research
status: budding
---

# 自主探索筆記整合：Agent 可靠性架構的雙層模式

**消化筆記**: `2026-06-03-forge-gambit-agent-harness`, `2026-06-03-llamagym-online-rl-fine-tune`

兩篇探索筆記從不同技術切入——Forge/Gambit 關注 LLM Agent 的可靠性與可驗證性，LlamaGym 關注 Agent 的在線強化學習——卻在架構層面暴露了同一個深層模式。

---

## Cross-Cutting Theme 1: Agent 系統需要「強制 + 測量」雙層架構

**支援筆記**: `2026-06-03-forge-gambit-agent-harness`

Forge 和 Gambit 不是競爭關係——它們解決的是同一個問題的兩個不同層次：

| 層次 | 工具 | 職責 |
|------|------|------|
| L1（強制） | Forge | 確保 tool call 格式正確、合法；小模型（如 8B）無法在 text vs tool 之間正確選擇時，注入 synthetic respond tool 強迫正確行為 |
| L2（測量） | Gambit | 從 transcript/trace 評估 agent 行為品質；將失敗案例轉為迴歸測試 suite |

Forge 的 `ResponseValidator` + `Rescue parsing` 雙層 + `Retry loop` 是典型的 L1 強制機制；Gambit 的 scenario → grade → trace → regression 是典型的 L2 測量機制。

**這不是新發現**——但在 Hermes 語境中具體化了 Talos 治理 pipeline 的實作方向：之前談「enforcement + measurement」是概念層，現在有了 Forge + Gambit 兩個具體實現可以參考架構。

**可行動下一步**: 在 `talos-governance/` repo 中建立一個 `docs/agent-reliability-pattern.md`，把「L1 強制（Forge-style ResponseValidator）+ L2 測量（Gambit-style trace grading）」的雙層架構畫成技術決策文件，後續實作參考。

---

## Cross-Cutting Theme 2: 小模型需要結構化輸出而非自由形式

**支援筆記**: `2026-06-03-forge-gambit-agent-harness`, `2026-06-03-llamagym-online-rl-fine-tune`

兩篇筆記從不同角度碰觸了同一個現象：小模型（~8B）在「生成 tool call」和「生成 action」時，無法可靠地在不同輸出類型之間做正確選擇。

- **Forge**: 小模型在 text vs tool 之間會選错 → 注入 `Synthetic respond tool`，讓模型只面對 tool_calls，不暴露 bare text 的選項
- **LlamaGym**: 8B 模型在 RL 訓練中同樣需要 `Agent` abstract class 強制 `extract_action` 規範化——否則模型輸出的 free-form 無法轉為可學習的信號

這個模式在 Hermes 也有對應：之前提到的「structured output over free-form」原則 + `confidence_valid_until` 的 event-driven invalidation（而非 time-based decay）。核心洞察是：**小模型需要被給予強制性的 schema，而非被信任能自發選擇正確格式**。

**可行動下一步**: 在 `heartbeat_learning.py` 中，針對「小模型輸出格式飄移」問題，加入一個 lightweight schema validation step——在 observation 進來時強迫格式化成結構化 slot，再做下游處理。具體：參考 LlamaGym 的 `extract_action` pattern，把游離的 model raw output 強制映射到一組有限狀態。

---

## 備註：無需整合的筆記

`2026-06-03-shapedql-multi-stage-ranking` 已於更早批次處理完畢，本批不涉及。