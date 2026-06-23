---
_slug: 40-Resources-_mixed-explorations-2026-06-08-A-Mem--Agentic-Memory-for-LLM-Agents--2026-06-08
_vault_path: 40-Resources/_mixed/explorations/2026-06-08-A-Mem--Agentic-Memory-for-LLM-Agents--2026-06-08.md
title: 'A-Mem: Agentic Memory for LLM Agents (2026-06-08)'
date: 2026-06-08
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- distillate
- drift
- driven
- evolution
- link
- llm
- locomo
- mem
- memory
- penalty
created: '2026-06-08'
updated: '2026-06-15'
status: budding
---

# A-Mem: Agentic Memory for LLM Agents (2026-06-08)

**來源**: arxiv:2502.12110v2 | Wujiang Xu et al. (Rutgers/Ant Group/Salesforce Research)

## 核心架構：三元件

1. **Note Construction** — 每筆記錄包含 7 個屬性：
   - `c`: 原始互動內容
   - `t`: 時間戳
   - `K`: LLM 生成的關鍵詞
   - `G`: LLM 生成的標籤
   - `X`: LLM 生成的脈絡描述（豐富語義理解）
   - `e`: 稠密向量（concat(K,G,X) 編碼）
   - `L`: 連結的記憶集合

2. **Link Generation** — 新記憶進來時：
   - 用 embedding similarity 找 top-k 最近鄰
   - LLM 決定是否建立連接（不只靠相似度）
   - 連結是雙向的：`L_i` 記錄所有連到 `m_i` 的記憶

3. **Memory Evolution** — 核心創新：
   - 新記憶觸發鄰近記憶的屬性更新（context/tags）
   - 三種 action：`strengthen`（強化連結）、`merge`（合併）、`prune`（剪枝）
   - 這是 drift penalty 的具體參考：新資訊不是時間衰減，而是 semantic contradiction → 觸發鄰近節點屬性更新

## 與 WS-035 drift penalty 的對應

| A-Mem 概念 | heartbeat_learning.py 對應 |
|---|---|
| Note (7-tuple) | distillate（目前只有 header + content，缺少結構化屬性） |
| Memory evolution | drift penalty（目前缺 explicit mechanism） |
| LLM-driven link decision | distillate contradiction detection |
| Token efficiency (1.2-2.5k) | 目標：distillate compactness |

**關鍵 insight**：A-Mem 的 `memory evolution` 機制是 drift penalty 的具體參考——新資訊觸發鄰近節點的 context/tag 更新，而非均勻時間衰減。這與 MemTier 的 CW attribution loop（tool outcome → explicit reward signal）方向一致，與均勻 decay 不同。

## 實驗結果亮點

- Multi-Hop QA：Qwen2.5-15b + A-Mem 達 ROUGE-L 27.23 vs LoCoMo 4.68（6x）
- GPT-4o-mini Multi-Hop：A-Mem 44.27 vs LoCoMo 18.09（2.4x）
- 僅需 1,200-2,500 tokens（vs 16,900 for MemGPT/LoCoMo）

## 未追蹤 leads
- MemGPT interrupt-driven paging vs A-Mem LLM-driven link decision 架構對比
- A-Mem 的 Memory Evolution action 如何避免 drift accumulation（無明確描述，似為 LLM 內部判斷）

## ✅ 本次探索完成
