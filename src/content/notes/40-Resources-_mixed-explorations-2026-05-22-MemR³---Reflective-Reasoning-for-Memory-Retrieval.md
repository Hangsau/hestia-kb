---
_slug: 40-Resources-_mixed-explorations-2026-05-22-MemR³---Reflective-Reasoning-for-Memory-Retrieval
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-MemR³---Reflective-Reasoning-for-Memory-Retrieval.md
title: MemR³ — Reflective Reasoning for Memory Retrieval
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- action
- answer
- evidence
- gap
- gaps
- heartbeat
- learning
- memr
- reflect
- retrieval
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# MemR³ — Reflective Reasoning for Memory Retrieval

**時間**: 2026-05-23 05:45 CST
**來源**: arXiv:2512.20237 (full HTML, arxiv.org/html/2512.20237)
**品質**: 高 — 具體演算法 + 完整 prompt templates + evaluation
**主題**: 將 retrieval 從 open-loop 變成 closed-loop controller

## 核心架構

MemR³ 是 LangGraph-based 的 closed-loop memory retrieval controller：

```
query → Router → [Retrieve] → [Reflect] → [Answer]
              ↑__________________|
```

**兩大核心元件**:
1. **Router** — LLM 做決策：三個 action `{retrieve, reflect, answer}`
2. **Evidence-Gap Tracker** — 維護 state `(E, G)`：E=已知證據, G=仍缺少的資訊

```
(Eₖ, Gₖ, aₖ) = LLM(q, Sₖ₋₁, Fₖ₋₁, Eₖ₋₁, Gₖ₋₁, pₖ)
```
- E 是已建立的事實證據列表
- G 是阻礙完整回答的資訊缺口
- G = ∅ 時才能 answer，否則 retrieve 或 reflect

**Router 穩定性約束**（三個 deterministic rules）：
1. `k ≥ n_max` → 強制 answer（防止無窮 loop）
2. `Sₖ₋₁ = ∅` → 強制 reflect（沒有 retrieval 可用）
3. `n_streak ≥ n_cap` → 強制 retrieve（reflect 連續太多次）

**實驗設定**：n_chk=5 chunks/iteration, n_max=5 iterations（最終選擇）
- LoCoMo benchmark：MemR³ + RAG 提升 +7.29%，MemR³ + Zep 提升 +1.94%（GPT-4.1-mini backend）
- 大多數簡單問題在 1 iteration 內終止

## Hermes 啟發

### 對 heartbeat_learning.py 的直接應用

**現狀**：WS-024 的 rubric scoring 是「分類式」（low/medium/high quality）。MemR³ 的模式更適合 heartbeat learning：**狀態追蹤式**。

**具體建議**：
1. heartbeat action log 分析改為「what do we know vs. what are we missing」視角
2. 追蹤 `{evidence_patterns: [...], missing_signals: [...]}`
3. 只有當 `missing_signals` 收斂到空集合時，才做 proactive learning extraction（否則 continue collecting）

**Appendix A 的 prompt 模板可以直接用**：
```
# Evidence
{evidence_block}

# Gaps
{gap_block}

# INSTRUCTIONS:
1. Update evidence as JSON array of concise factual bullets
2. Update gaps: remove resolved items, add new missing specifics
3. If you produce a retrieval_query, make sure it differs from the previous
4. Decide the next action and return ONLY the JSON object
```

**對 WS-024 的修正**：
- rubric scoring（分類 low/medium/high）可以保留作為微觀信號
- 但上層 controller 應該用 evidence-gap 邏輯：先問「我們缺什麼？」→ 再問「這個 action 的 quality 是什麼？」
- 這比直接問「quality score = ?」更有方向性

### Evidence-Gap 應用於 heartbeat learning extraction

| 現狀（rubric 思路） | Evidence-Gap 思路 |
|---|---|
| 「這個 action quality = low」 | 「我們知道：action 有 loop pattern。我們不知道：是否為 doom-loop 或正常的 retry」 |
| 分類輸出 | 結構化 state 更新 |
| 靜態閾值 | 動態收斂條件 |

**具體實作路徑**：
- `heartbeat/action_analyzer.py` 輸出 `{"evidence": [...], "gaps": [...], "next_action": "extract/continue/wait"}`
- 收斂條件：`gaps = []` 且 `confidence > threshold` → extract learning
- 不收斂時持續 log action 供未來 pattern 分析

### 對其他提案的影響

- **WS-006** (Heartbeat v2.0) — evidence-gap tracker 可以是新的 learning extraction 驅動方式
- **WS-023** (Vault Decay) — 現有的 time-decay 是「被動 decay」，evidence-gap 思維可以做「主動 gap-filling」：每次 heartbeat 檢查「哪些 vault entries 有 evidence 可以強化，哪些 gaps 需要填補」

## 具體收穫：可直接內化的程式碼片段

**Appendix A.1 System Prompt**（generate node）：
- 輸出格式：JSON `{"evidence": [...], "gaps": [...], "decision": "retrieve|reflect|answer"}`
- 只有 `decision == "retrieve"` 時才需要 `retrieval_query`（且必須與前次不同）
- 只有 `decision == "answer"` 時才需要 `detailed_answer`
- 只有 `decision == "reflect"` 時才需要 `reasoning`

這個 schema 直接對應 heartbeat learning 的 action extraction prompt。

**Appendix B Theorem B.4（證據追蹤的數學性質）**：
- Monotonicity: evidence 只增不減，gaps 只減不增
- Soundness: 任何新進 evidence 必然來自某個 retrieved item
- Completeness: 當所有 required facts 都被支持時，G → ∅

→ 這個數學保證讓 heartbeat learning 的 gap-filling 有 formal correctness criteria。

## 未追蹤 Leads

- `https://arxiv.org/abs/2512.20237` — 即將讀的 full paper（已在讀）
- `https://github.com/MemoriLabs/Memori` — Memori SDK source（triple extraction Rust 實作）
- LangGraph integration — MemR³ 用 LangGraph；hermes_mcp_server.py 的 async pattern 可以對照

## ✅ 本次探索完成

**時間**: 2026-05-23 05:45 CST
**Token cost**: 低（1次 arXiv HTML fetch，12K chars）
**品質**: 高 — prompt templates + formal model + evaluation 齊備
**價值**: 從「rubric scoring」到「evidence-gap controller」的 framework shift，適用於 heartbeat learning 重構
