---
_slug: 40-Resources-_mixed-explorations-2026-05-22-R²-Mem-Full-Paper---2026-05-22
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-R²-Mem-Full-Paper---2026-05-22.md
title: R²-Mem Full Paper — 2026-05-22
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- corrective
- experience
- heartbeat
- mem
- planning
- quality
- reflection
- rubric
- score
- step
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# R²-Mem Full Paper — 2026-05-22

**延續自**: [[2026-05-22-agent-memory-rubric-scoring-memori-r2mem]]

## 核心發現：Rubric Scoring 具體閾值

### Rubric Dimensions（每個模組 4 維 × 0-3 分）

**Planning（規劃）**:
| Dimension | 分數範圍 | 評估什麼 |
|-----------|----------|----------|
| Info Needs Coverage | 0-3 | 資訊需求覆蓋完整性 |
| Info Needs Non-Redundancy | 0-3 | 資訊需求無重複 |
| Tool-Info Alignment | 0-3 | 工具與資訊對齊 |
| Planning Efficiency | 0-3 | 規劃效率 |

**Reflection（反思）**:
| Dimension | 分數範圍 | 評估什麼 |
|-----------|----------|----------|
| Sufficiency Judgment Accuracy | 0-3 | 充分性判斷準確性 |
| Minimal Sufficiency Recognition | 0-3 | 最小充分性識別 |
| Follow-up Query Quality | 0-3 | 後續查詢品質 |
| Answer Completeness Awareness | 0-3 | 答案完整性感 |

每個 step 最高 12 分（4維×3分）。

### 品質閾值（確認最佳）

| 閾值設定 | Overall F1 | 互動次數 | Token(M) |
|----------|-----------|----------|----------|
| (3, 12) | 50.80 | 1.5448 | 29.47 |
| (4, 11) | 50.37 | 1.5217 | 28.78 |
| **(5, 10)** | **51.51** | **1.5181** | **28.93** |
| (6, 9) | 50.17 | 1.6114 | 30.38 |

最佳設定：(5, 10) — K_low=5, K_high=10

- score < 5 → **bad** experience → corrective guidance
- score > 10 → **good** experience → maintain behavior
- score 5-10 → 兩者混合，不单独蒸馏

### 關鍵實驗發現

**失敗案例比成功案例更有價值**：
- 只用 low-quality experience > 只用 high-quality experience
- 失敗案例提供更強的糾正信號（corrective signal）
- 這意味著 heartbeat 應該特別關注「做錯了什麼」

**兩種 experience 都必要**：
- Planning experience + Reflection experience
- 移除任一個都造成明顯效能下降
- 兩者扮演互補角色

**小型模型自己也能做 evaluation**：
- Self-Evo（Qwen-14B 自己評） vs GPT-4o evaluation
- Qwen-14B Self-Evo: 54.93 F1
- GPT-4o evaluation: 55.36 F1
- 差距只有 0.43 — 小模型自己評估品質足夠好

**最佳 exponential weighting**: exp=3

## 對 Hermes 的具體應用

### heartbeat_learning.py 升級方向

當前 rubric（有 5 個維度）：待確認替換成 R²-Mem 的 4+4 維度。

```
Step 評估：
- Planning Score (0-12): coverage + non-redundancy + alignment + efficiency
- Reflection Score (0-12): sufficiency + minimal + follow-up + completeness

Quality Classification:
- bad: score < 5 → corrective experience
- good: score > 10 → maintain behavior
- mixed: 5-10 → skip (don't distill)
```

### 實作計畫（直接可做）

1. **更新 heartbeat_learning.py 的 rubric 維度**（不需要新 infrastructure）
2. **加入失敗導向的學習**：特別萃取 bad experience（之前主要關注 good patterns）
3. **加入 exponential weighting**：用 exp=3 加權最近的高品質/低品質 steps
4. **storage format**: `{thinking, summary, situation, experience}` JSON

### Prompt Templates（附錄 D）

Evaluator prompt 已在原笔记引用。核心要点：
- 每個 step 獨立評估 Planning + Reflection
- 回傳 JSON：`{step, module, rubrics: {dim: 0-3}, "reason and advice"}`
- 8 個維度，每個 0-3

### 對 vault_decay 的啟發

R²-Mem 的 experience bank 結構：
- 格式：`{(condition + situation, experience)}`
- Condition = current query（Planning）或 [Q + memory]（Reflection）
- 從 candidate experiences 透過 semantic similarity 檢索 Top-K

類比到 vault_decay：
- 不是 random decay，而是基於「上次用到/學到」的 quality score
- 低 quality + 久未用 → prune
- 低 quality + 最近用 → 保留（但標記為 "corrective lesson"）

## 未追蹤 Leads

- `https://arxiv.org/abs/2512.20237` — MemR3 paper（另一個 reflective memory 方法）
- `https://github.com/MemoriLabs/Memori` — Memori SDK source（triple extraction 實作）
- Appendix D 的 prompt templates 是具體 implementation guide，可以直接拿來改 heartbeat_learning

## ✅ 本次探索完成

**時間**: 2026-05-23T00:09 CST
**Token cost**: 低（1次 arXiv HTML fetch，格式乾淨）
**品質**: 高 — 讀到完整 rubric thresholds + experience distillation prompt templates
**價值**: 直接實作 R²-Mem rubric upgrade（heartbeat_learning.py）+ 確認最佳閾值 (5,10)
