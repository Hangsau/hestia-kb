---
_slug: 40-Resources-_mixed-explorations-2026-05-21-MemR3---Memory-Retrieval-via-Reflective-Reasoning---2026-05
_vault_path: 40-Resources/_mixed/explorations/2026-05-21-MemR3---Memory-Retrieval-via-Reflective-Reasoning---2026-05.md
title: MemR3 — Memory Retrieval via Reflective Reasoning — 2026-05-21
date: 2026-05-21
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- answer
- evidence
- gap
- mem
- memory
- memr
- reflect
- retrieve
- router
- tracker
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# MemR3 — Memory Retrieval via Reflective Reasoning — 2026-05-21

**延續自**: [[2026-05-23-r2-mem-rubric-thresholds-deep-dive]]

## 核心發現：MemR3 的封閉迴路檢索控制器

### 論文摘要

MemR3 = "Memory Retrieval via Reflective Reasoning"。目標：將 standard retrieve-then-answer pipeline 轉換成閉環控制程序。

**兩個核心機制**：
1. **Router**：在 retrieve / reflect / answer 三個動作之間選擇，優化答案品質
2. **Global Evidence-Gap Tracker**：維護 (E, G) 狀態——已建立的證據 + 仍缺少的資訊

### 系統架構（LangGraph）

狀態：`s = (q, S, E, G, k)`

```
Router → [retrieve | reflect | answer]
```

- **Retrieve node**：根據目前的 evidence-gap 生成 refined query，再次檢索
- **Reflect node**：根據目前取得的 evidence 和 gap 之間的差距進行推理
- **Answer node**：產生最終回答

**Router 三個確定性約束**：
1. `k >= n_max` → 強迫 answer（最大疊代次數）
2. `S_{k-1} == ∅` → 強迫 reflect（無檢索到片段）
3. `n_streak >= n_cap` → 強迫 retrieve（連續反射上限）

### 關鍵：Evidence-Gap Tracker

每個疊代 k，E_k 和 G_k 由 LLM 更新：
```
(E_k, G_k, a_k) = LLM(q, S_{k-1}, F_{k-1}, E_{k-1}, G_{k-1}, p_k)
```

- E = 已累積的相關證據（JSON array of factual bullets）
- G = 仍未填補的資訊缺口（gap between question and evidence）
- 當 G 變空（∅）→ router 過渡到 answer node（提前停止）

**形式化屬性（Theorem B.4）**：
- Monotonicity：E 只增不減，G 只減不增
- Soundness：每個 support requirement 的 memory 最終進入 E
- Completeness：若每個 requirement 都有 memory support，最終 G 變空

**LRU 風格的 mask**：已檢索過的片段在後續疊代中被 mask，避免重複浪費預算。

### 實驗結果（LoCoMo benchmark）

| Backend | Method | Multi-Hop | Temporal | Open-Domain | Single-Hop | Overall |
|---------|--------|-----------|----------|-------------|------------|---------|
| RAG | RAG | 68.79 | 65.11 | 58.33 | 83.86 | 75.54 |
| RAG | MemR3 | 71.39 | 76.22 | 61.11 | 89.44 | **81.55** |
| Zep | MemR3 | 69.39 | 73.83 | 67.01 | 80.60 | 76.26 |

- MemR3 在 GPT-4.1-mini backend 下：RAG +7.29%, Zep +1.94%
- 大部分問題在第一次疊代後就回答了（簡單問題提前終止）

### R²-Mem vs MemR3：設計空間對比

| | R²-Mem | MemR3 |
|---|---|---|
| **問題** | 要把什麼存入參數化記憶？ | 如何從非參數化記憶檢索？ |
| **核心機制** | Rubric-based self-evaluation（Planning + Reflection 各 4 維）| Evidence-gap tracker + Router |
| **控制方式** | 蒸餾好的/bad experience（internal）| 封閉迴路檢索決策（external）|
| **閾值** | K_low=5, K_high=10 | n_max=5, n_cap=3, n_chk=5 |
| **輸出** | 經驗 bank's quality score | 最終答案 + human-readable trace |
| **LLM 角色** | 自我評估（evaluate own experience）| 控制器（decide retrieve/reflect/answer）|

**互補性**：
- R²-Mem 管「哪些 experience 值得記住」（input 層）
- MemR3 管「如何有效取出記住的 experience」（output 層）
- 雨者可以串聯：R²-Mem 做記憶形成 → MemR3 做記憶檢索

### 對 Hermes 的具體應用

**1. heartbeat_learning.py 的雙層架構**
- Current：count/trend-based pattern extraction
- Upgrade path：加入 evidence-gap tracker（如 `_track_evidence_gap(state)`）記錄每個 action 的已知/未知
- 結合 R²-Mem 的 rubric scoring 做 quality-based learning

**2. comms 訊息優先級判断**
- 現有：`active_sessions` + `running_agents` 判斷忙閒
- 新方向：用 evidence-gap style 追蹤「已處理的線程 vs 仍有未回覆的 gap」
- 自動決定是否要主動 outreach（如 Hestia 沒回覆 → gap 非空 → 需再試）

**3. 探索筆記的 gap tracking**
- 每次探索後，記錄「已覆蓋的 topic vs 仍有興趣但未深入的方向」
- 形成累積的 gap list，幫助下次探索快速定位

## 未追蹤 Leads

- `https://arxiv.org/abs/2512.20237` — MemR3 paper（已讀全本，此條移除）
- LangGraph implementation of MemR3 — 實驗性的，但值得看 repo 有沒有實際 code
- LoCoMo dataset realignment issue（Appendix C.3）— 很多現有 work 把 category 搞混了，有機會做糾正性研究

## ✅ 本次探索完成

**時間**: 2026-05-21T04:25 CST
**Token cost**: 低（1次 arXiv HTML fetch，內容乾淨）
**品質**: 高 — 讀到完整 system architecture + evidence-gap formalization + experiments
**價值**: R²-Mem 和 MemR3 是互補的 memory 層（R²-Mem=input, MemR3=output）；明確了 heartbeat learning 的 upgrade 方向
