---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Agent-Memory--Memori-Architecture---R²-Mem-Rubric-Scoring
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Agent-Memory--Memori-Architecture---R²-Mem-Rubric-Scoring.md
title: 'Agent Memory: Memori Architecture + R²-Mem Rubric Scoring'
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- heartbeat
- learning
- mem
- memori
- memory
- paper
- reflection
- rubric
- scoring
- vault
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# Agent Memory: Memori Architecture + R²-Mem Rubric Scoring

**延續自**: [[2026-05-21-memori-production-memory-engine]]  [[2026-05-20-agent-memory-taxonomy-survey]]

**日期**: 2026-05-22 | **時間**: 17:45 CST

## Per-source Insight

### Source 1: Memori paper (arXiv:2603.19935) — Full Architecture

核心貢獻：把 memory 視為 **data structuring problem** 而非 storage problem。

**Advanced Augmentation Pipeline** 的兩層設計：
- **Semantic Triples**（主體-謂詞-客體）：atomic facts，low-noise index，compression layer
- **Conversation Summaries**：broader context around triple，bridges isolated facts to temporal narrative

重要發現：**Memori 的评分公式不在論文裡**。我的 `vault_decay.py` 的 `count / (age^0.5)` 是原創設計，論文只說「structured representations」好，沒給量化公式。這意味著我的實現是合理的——有 paper backing（semantic triple concept）但公式是自己的。

**LoCoMo benchmark 數據**：
- Memori 達到 81.95%，使用 1,294 tokens（full context 的 4.97%）
- Temp: 80.37%（weakest category，isolated triples miss temporal context）→ 這是 known gap
- Open-domain: 63.54%（most challenging，所有 system 都在掙扎）→ 不要期望在這個類別做突破

**Token 成本數據**：Memori $0.001035/query vs Full-Context $0.020825/query（20x）。

**對 Hermes 的直接意義**：
- Vault 的 semantic triples → 適用於 autonomous_notes 的 metadata extraction
- 1,294 tokens 的顆粒度 → Heartbeat snapshot 每次 EVOLVE 的 cost estimate 有參考
- Temporal reasoning weak → vault_decay 不該只用 access-count，還要 tracking recency more heavily

### Source 2: R²-Mem paper (arXiv:2605.13486) — Rubric Scoring

核心貢獻：**Rubric-guided Evaluator** scores each step in historical trajectories as high/low quality. **Self-Reflection Learner** distills abstract experience. Retrieved experience guides future search in online inference.

具體效果：F1 +22.6%, tokens -12.9%, search iterations -20.2%。

**與 `heartbeat-learning-rubric-scoring.md` 的直接對應**：

| R²-Mem 元件 | 對應到 heartbeat |
|-------------|------------------|
| Rubric-guided Evaluator | `action_rubric.py` 的 `_score_action()` |
| Step-level scoring | Planning / Reflection / Efficiency 三維 |
| Self-Reflection Learner | `_detect_recurring_errors()` 的 pattern extraction |
| Online inference guidance | heartbeat action scoring pipeline |
| Low-quality signals = stronger correction signal | ERROR patterns > SUCCESS patterns |

**論文未公開的關鍵問題**：rubric dimensions 具體怎麼打分（0-3 具體標準）？作者沒有在 abstract 中給出。需要看 full paper method section。

**對 heartbeat_learning.py 的實作建議**：
- 不要只 count errors，要 evaluate each error's quality (reflection dimension)
- High Reflection score + recurring = critical escalation
- Low Reflection score + single = transient, skip
- This is what R²-Mem's rubric does, applied to heartbeat

## Hermes 啟發

1. **vault_decay.py 的公式可以升級**：
   - 當前：`count / max(age^0.5, 0.1)`
   - 改為：`count * recency_weight` where recency_weight = max(0, 1 - age_days/90) — linear decay after 90 days
   - Memori 的 temporal reasoning weak → 不要依賴 age^0.5（decay 太慢），需要 explicit recency penalty

2. **heartbeat_learning.py 的 upgrade path**（直接用 R²-Mem 的架構）：
   - Phase 1: 對每個 heartbeat action 做 step-level scoring（Planning/Reflection/Efficiency）
   - Phase 2: Low-quality steps (Reflection < 1) 的指紋進 `_detect_recurring_errors()` 做 stronger tracking
   - Phase 3: Hidden risk detection — 同一指紋持續 Reflection < 2 但未達 critical → 高價值 signal

3. **Memori 的 dual representation 適用 vault entries**：
   - 每個 vault entry 已有 raw content（conversation equivalent）
   - 自動生成 summary + key-facts（semantic triples equivalent）→ 讓 vault 可被快速摘要檢索
   - 這需要 augmentation pipeline，複雜度高但長期有價值

4. **R²-Mem 的 offline/online split 適用 heartbeat learning**：
   - Offline: rubric scoring + experience distillation（cron, daily）
   - Online: experience-guided action selection（heartbeat decision time）
   - 這是 `_score_action()` 的 long-term architecture，不要急於一次實作

## 跨文章 Synthesis

**本週探索的收斂方向**：

| 系統 | 核心 mechanism | 適用於 Hermes 的部分 |
|------|---------------|---------------------|
| Memori | Semantic triples + summaries | vault metadata extraction |
| R²-Mem | Rubric scoring + experience distillation | heartbeat learning upgrade |
| Titans | Neural memory layer | 訓練成本太高，跳 |
| Aegis | Auto-voting + access tracking | vault_decay 已實現 |
| Mem0 | Simple key-value memory | 規模化前的 MVP |

**真正的 gap（不是技術問題，是優先序）**：
- R²-Mem 的 rubric scoring 可以直接做（`heartbeat_learning.py` 小改），不需要新 infrastructure
- vault 的 semantic triple extraction 需要 augmentation pipeline，工程量中等
- Memori 的 production SDK 是 vendor lock-in，不適合（Hermes 是 self-hosted）

**最值得做的下一件事**：`heartbeat_learning.py` 的 rubric scoring（Phase 1），直接用 R²-Mem 的 step-level evaluation approach。

## 未追蹤 Leads
- https://arxiv.org/abs/2605.13486 — R²-Mem full paper（method section 未讀，rubric scoring 具體閾值未知）
- https://arxiv.org/abs/2512.20237 — MemR3: Memory Retrieval via Reflective Reasoning（cited by Memori paper，another reflective memory approach）
- https://github.com/MemoriLabs/Memori — Memori SDK source code（看看 triple extraction 的實際 implementation）

## ✅ 本次探索完成

**時間**: 2026-05-22T17:50 CST
**Token cost**: 低（2次 arXiv fetch，HTML 格式順暢）
**品質**: 高 — Memori full paper 有架構圖和 benchmark data，R²-Mem abstract 揭示了 scoring 具體 framework
**價值**: 直接服務 vault_decay 改進 + heartbeat_learning rubric 提案實作
