---
_slug: 40-Resources-_mixed-research-2026-05-28-0806-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-05-28-0806-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-28'
confidence: medium
title: Enforcement Layer + Bounded Memory = 完整的身心系統
updated: '2026-06-15'
type: research
status: budding
---

# Enforcement Layer + Bounded Memory = 完整的身心系統

**消化筆記**: 2026-05-26-cuga-runtime-governance, 2026-05-28-entelgia-aegis-memory

（兩篇跨時期探索結合：CUGA 的 runtime governance 五層執行機制，與 Entelgia/Aegis 的 bounded memory 原則，揭示了「記憶層 + 執行層」必須共同設計。）

## Cross-Cutting Theme 1: 三層迴圈模式（Generate → Reflect → Curation/Govern）在四個系統中獨立收斂

**支援筆記**: cuga-runtime-governance, entelgia-aegis-memory

（分析）

CUGA 的五層 runtime governance 可以化約為：
1. **Intent Guard** = 執行前的 Generate 過濾
2. **Playbook** = Generate + 塑形階段
3. **Tool Guide** = Reflect（tool description 附加 context）
4. **Tool Approval** = Curation（獨立把關，脫離 LLM loop）
5. **Output Formatter** = Curation（最後格式化過濾）

而 Aegis 的 ACE loop（Generation → Reflection → Curation）正是同一個模式的另一種命名。Entelgia 的 Observer Correction Loop（Observer → detects drift → corrective signal → memory update）則是同一個模式在記憶層的變體。

四個系統（Entelgia、CUGA、Aegis、加上之前調研的 Synrix/MuninnDB）獨立收斂到同一個三層迴圈，不是巧合——這是 agent 系統中"perception-action-feedback"在記憶與治理維度的必然結構。任何略過其中一層的設計（如「記憶多但沒有 governs」）都會導致系統失控。

**可行動下一步**: 在 `ws-028` 重新視覺化為三層迴圈圖（不再是線性的四 Phase），各層分別標註對應的現有實作：Intent Guard/Playbook（Policy Engine）/Tool Guide（policy_engine plugin）/Tool Approval（HITL gate）/Output Formatter。確認目前的實作缺口在哪一層。

---

## Cross-Cutting Theme 2: Pre-filter Before LLM 是成本與行為追蹤的共同瓶頸

**支援筆記**: cuga-runtime-governance, entelgia-aegis-memory

（分析）

Aegis 的 Stage 1 rule-based filter 聲稱节省 70% LLM distillation 成本——因為大多數 session 是「greeting + short query + one-liner response」，不需要浪費 LLM 做 distillate。

CUGA 的 Intent Guard 也是同一個精神的執行層版本：以 keyword + embedding similarity（threshold 0.65）在 LLM reasoning loop 之前截獲——"stop before the model even reasons about it"。

把這兩個想法合在一起得到一個 Hermes 具體的設計原則：**昂貴的 LLM 操作（distillate、reasoning、policy Evaluation）必須有便宜的先導篩選**，否則系統在「簡單請求海嘯」下会耗盡 budget。

目前 `heartbeat_learning.py` 的問題正是這個：每個 session 都跑 LLM distillation，不管內容複雜度。`otp_gate.py` 的 OTP human-in-the-loop 是對的工具，但只對高風險操作有效；對「大量簡單 session」的應對是缺失的。

**可行動下一步**: 在 `heartbeat_learning.py` 新增 session complexity heuristic：
```python
# Rule-based pre-filter — no LLM call needed
simple_indicators = ['thank', 'hello', 'hi ', 'bye', '/status', '/help']
if any(s in session_text.lower() for s in simple_indicators):
    return  # skip distillation
# else: proceed with LLM distillation
```
量化後記錄節約的 token 量，下個月的 cost report 可以看出效果。

---

## Cross-Cutting Theme 3: Policy 儲存從「靜態規則」走向「可查詢向量空間」是共同方向（Low，推測成分高）

**支援筆記**: cuga-runtime-governance, entelgia-aegis-memory

（分析）

CUGA 用 Milvus vector DB 儲存 policy，以 keyword/embedding/application/state/tool 動態匹配。Entelgia 的 memory promotion 也需要「哪些記憶值得記住」的向量表示。Aegis 的 contradiction detection 需要「哪些記憶互相矛盾」的向量空間。這三個需求合在一起指向同一個基礎設施需求：**可查詢的 embedding index**，不只是文件和 embedding 的簡單相似度搜索，而是可以附加 metadata（來源、時間、信任等級、矛盾標記）進行條件過濾。

目前 Hermes 的 FTS5 doc index 是文件級別的 embedding search，缺少這樣的元資料過濾能力。

**可行動下一步**: 探索將 `vault_access.json` 的 access log 結構轉化為簡單的 embedding metadata store——在 session_search 或 memory_inject 中新增「filter by time range + confidence threshold」的 lightweight 實作，不需要引進新 dependency，用既有的 jsonl + Python 即可。

---

## 已沉積資訊至系統地圖

- `maps/memory.md` — 新增：三層迴圈模式對應、pre-filter before LLM 原則、政策儲存的向量空間方向
- `maps/cron.md` — 建議：heartbeat_learning.py 的 complexity heuristic 可以在 cron 框架下直接實作

## 未跟蹤 Leads（見原筆記）

- https://github.com/cuga-project/cuga-agent — CUGA 開源 repo
- https://huggingface.co/datasets/ibm-research/BPO-Bench — BPO benchmark
