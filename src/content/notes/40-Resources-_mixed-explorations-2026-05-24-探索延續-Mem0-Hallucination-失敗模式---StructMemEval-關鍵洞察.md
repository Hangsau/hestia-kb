---
_slug: 40-Resources-_mixed-explorations-2026-05-24-探索延續-Mem0-Hallucination-失敗模式---StructMemEval-關鍵洞察
_vault_path: 40-Resources/_mixed/explorations/2026-05-24-探索延續-Mem0-Hallucination-失敗模式---StructMemEval-關鍵洞察.md
title: 探索延續：Mem0 Hallucination 失敗模式 + StructMemEval 關鍵洞察
date: 2026-05-24
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- based
- count
- gemini
- hallucination
- hint
- mem
- memory
- structmemeval
- 失敗模式
created: '2026-05-24'
updated: '2026-06-15'
status: budding
---

# 探索延續：Mem0 Hallucination 失敗模式 + StructMemEval 關鍵洞察

**延續自**: [[2026-05-24-llm-agent-multi-layer-memory]]

**日期**: 2026-05-24（系統日期，非估算）

---

## StructMemEval 核心發現：Hallucination 失敗模式

### 失敗模式 3 類型

StructMemEval 的 Appendix D Error Analysis 給出了記憶 agent 的三種典型錯誤：

1. **Omission（遺漏）**：最常見——漏掉交易紀錄
2. **Duplication（重複）**：重複計入同一筆交易
3. **Hallucination（虛構）**：最嚴重——產生從未存在的交易

### Table 5 實例（Gemini-2.5-pro + Mem-agent）

| Payer | For Whom | Amount | Notes |
|-------|----------|--------|-------|
| Alice | Bob | 15 EUR | **sandwich** |

問題：對話中從未出現「sandwich」一字，也沒有這筆交易。這是完整的 hallucination——LLM 自己發明了交易紀錄。

### Hallucination 觸發條件

- **大量連續 memory updates**：正常使用時很少發生，**但當 agent 執行數百次連續更新時頻率顯著上升**
- Count-based tasks（結算帳目）特別容易觸發，因需要多筆交易疊加
- Table 2 note: *"gemini-2.5 has too many hallucinations"* → Gemini-3-pro 才適用 count-based 任務

### 重要結論：Hints 的影響力遠大於 Framework 差異

```
Gap between (with hint) vs (without hint)  >>  Gap between Mem0 vs mem-agent
```

同一模型，有 hint → 可靠；無 hint → 不可靠。無論用 Mem0 還是 mem-agent 都一樣。

→ **Memory organization guidance 比底層框架選擇更重要**

---

## 與前期發現的連結

1. **MLMF 的 Retention Stability Objective（懲罰語義突變）**可能是對治 hallucination 的關鍵：
   - Hallucination = 記憶系統產生「從未輸入的內容」= 語義突變
   - 當 session summary 偏離實際對話內容時觸發 penalty，可抑制 hallucination generation

2. **StructMemEval 的 Tree/State/Count 三任務類型**對應 Hermes 的實際場景：
   - Tree → 工作區域层级關係（`workspace/INDEX.md` vs `proposals/` 的對應）
   - State → 任務狀態追蹤（`tasks/*/PLAN.md` 的 open/pause/done）
   - Count → 預算/成本追蹤（`cost.md` 的 token 累計）

3. **Hints 的設計可以內化為架構原則**：
   - 不依賴使用者給提示，而是讓 agent 根據任務類型自動套用對應的 memory organization pattern
   - WS-026 的 query engine 可以參考這個設計

---

## 未追蹤 Leads

- https://github.com/yandex-research/StructMemEval — benchmark source（eval code + dataset）
- LOCCO dataset（3080 dialogues, 100 users）— 可用於測試 future memory pipeline
- A-Mem vs Mem-agent 的實作差異（markdown-based vs structured）— 為何 Mem-agent 在無 hint 時表現更穩定
- MemOS / Memory OS for AI Agent — 另一種多層次 memory 架構

---

## ✅ 本次探索完成
