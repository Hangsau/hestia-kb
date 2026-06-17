---
_slug: 40-Resources-_mixed-explorations-2026-06-07-探索-FLE-v0-3---Factorio-學習環境用於-Agent-評測
_vault_path: 40-Resources/_mixed/explorations/2026-06-07-探索-FLE-v0-3---Factorio-學習環境用於-Agent-評測.md
title: 探索：FLE v0.3 — Factorio 學習環境用於 Agent 評測
date: 2026-06-07
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claude
- errors
- factorio
- fle
- github
- heartbeat
- https
- python
- syntactic
created: '2026-06-07'
updated: '2026-06-15'
status: budding
---

# 探索：FLE v0.3 — Factorio 學習環境用於 Agent 評測

**日期**: 2026-06-07 | **來源**: https://jackhopkins.github.io/factorio-learning-environment/versions/0.3.0.html | **類型**: exploration

## FLE v0.3 核心發現

### 什麼是 FLE
Factorio Learning Environment — 用遊戲工廠建設環境評測 AI agent 的長時規劃、推理、世界建模能力。v0.3.0 重大更新：
- **脫離 Factorio 客戶端**：新的 headless game renderer 支援大規模實驗
- **OpenAI Gym 相容**：標準化評測環境介面
- **Claude Code 橋接**：已整合 Claude Code 直播展示

### 觀察空間設計
每 step 回傳結構化 Observation：
- `entities`：遊戲世界中所有實體（位置、屬性、庫存、警告）
- `raw_text`：上次 action program 執行的 stdout/stderr（帶行號標注）
- `flows`：生產統計（輸入/輸出速率）
- `task_verification`：任務特定驗證結果

關鍵：Agent 看到的是遊戲狀態的 structured representation，而非像素。透過 Python API 控制遊戲（`place_entity`、`connect_entities`、`get_entity` 等）。

### Lab-Play 評測方法
固定起始物資 + 單一產量目標（16 items/min）。64 steps，near-threshold token budget 触发 summarization。

### Frontier Model 表現（Pass@8, 2025 年 9 月）
- Claude Opus 4.1: zero syntactic errors，幾乎全是 pragmatic errors（97.7%）— 程式碼生成強，但遊戲狀態心態模型弱
- GPT-5: 21% syntactic errors — 生成有效 Python 程式碼的能力低於預期
- Gemini 2.5 Pro: 12-17% API 理解錯誤
- Grok 4: 40.89% 平均錯誤率，經常陷入除錯迴圈

### 關鍵洞察：Agent 的三層失敗模式
1. **Syntactic Errors**：無效 Python code，根本沒執行
2. **Semantic Errors**：FLE API 參數用錯（TypeError、AttributeError）
3. **Pragmatic Errors**：對遊戲狀態推理錯誤（最常見）— 試圖 insert 不存在的物品

### 評測極限
- Agent 傾向用手動策略（shuttle resources、storage chests as buffers）而非建構完整自動化鏈
- 透過 60 秒 holdout period 緩解（必須讓工廠自己跑）
- 很少使用 helper function abstraction — 只有 Gemini 2.5 Pro 會自訂 abstractions

## Hermes 啟發

### 1. Error 分類對 heartbeat 設計的借鏡
FLE 的三層錯誤分類（syntactic/semantic/pragmatic）直接對應 heartbeat EVOLVE 的 error 處理：
- Syntactic → heartbeat 的 `script_integrity` sensor（syntax error in Python files）
- Semantic → heartbeat 的 `import` / `module` error detection（API misuse）
- Pragmatic → heartbeat 的 `plan_drift` / `workspace_drift` sensors（推理事實不符）

FLE 的 finding：「Claude Opus 4.1 程式碼生成強但遊戲狀態模型弱」，對應到 heartbeat_learning.py 的處境：distillate 生成能力強，但缺乏 explicit staleness detection → distillate 與遊戲狀態（實際系統狀態）逐漸漂移。

### 2. 抽象复使用的教訓
FLE 發現：即使提供 helper function abstraction 機制，agent 很少使用。這對 WS-035 的設計啟示：提供 abstraction mechanism 不等於 agent 會自發使用。需要強制性約束（如 FLE 的高難度目標倒逼自動化）而非純粹提供工具。

### 3. 評測環境的 held-out validation
FLE 的 60-second holdout period 防範「假的自動化」（buffer 堆積看起來有產量但不是真實持續產出）。類比到 heartbeat：需要有 held-out validation 机制，防止 heartbeat 只是在 session 內追蹤進度看起來健康但實際上落後於真實系統狀態。

## 未追蹤 Leads
- https://github.com/katanemo/archgw — intelligent proxy for AI agents（已在 vault，Plano 前身）
- https://www.spec27.ai/launch — spec-driven agent validation（launch page 太簡陋，待後續有文件後再追）
- https://github.com/gauravvij/GithubRepoAgent — agent that explores GitHub repos（13pts，值得一看）

## ✅ 本次探索完成
