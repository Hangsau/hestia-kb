---
_slug: research-2026-06-15-研究報告-se-agent-self-evolution-trajectory-optimization-for-llm-code-agents
_vault_path: research/2026-06-15-研究報告-se-agent-self-evolution-trajectory-optimization-for-llm-code-agents.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-15'
version: 1
source_report: 2026-06-15-se-agent-self-evolution-trajectory-optimization.md
source_url: ''
type: research
fingerprint: pool, se-agent, traj, operator, trajectory, llm, prompt, agent, iteration,
  strategy
title: 研究報告：SE-Agent — Self-Evolution Trajectory Optimization for LLM Code Agents
status: seedling
updated: '2026-06-15'
---

# 研究報告：SE-Agent — Self-Evolution Trajectory Optimization for LLM Code Agents

## Version 1 — 2026-06-15

### 核心觀念
**問題**：**Why now**: 2025-2026 程式碼 agent 的標的是 SWE-bench Verified（500 個真實 GitHub issue）。早期 SWE-agent（12.47%, 2024-03）→ mini-SWE-agent 65%（2025-07）→ 封閉源模型 70%+。開源 SOTA 卡在 60% 上下，如何再往上推到 80%？ **核心癥結**：大多數 agent 的推理軌跡是「**單 trajectory 從頭跑到尾**」。失敗了 → 重試，換個 seed，但**軌跡之間沒有結構化溝通**。兩條軌跡可能各解對 60% 的子問題，卻沒人把它們合起來。 **既有方…

**洞見**：**「trajectory 是 first-class object」**這個觀念正在成形。2025 年前大家把 trajectory 視為 log、debug 用；2026 年開始把它視為**可操作的遺傳材料**。 - **SE-Agent（2025-08, NeurIPS 2025）**: trajectory-level evolution - **Mem0 / Letta（2025）**: 把 memory 當 first-class，但還沒跨 trajectory - **FlowScript（2026）**: 把 reasoning 當 typed graph，**「矛盾是 fea…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 架構總覽

```
Iteration 1 (no operator)        ← 直接 base agent 跑
   ↓
traj.pool: 存 {instance_id: {problem, "1": {strategy, status, files, tools, ...}}}
   ↓
Iteration 2 (operator = alternative_strategy)
   ↓  LLM 看 iter1 的失敗軌跡 → 生成「正交替代策略」當 system prompt
   ↓  base agent 拿著新 prompt 重跑
traj.pool: "2" 鍵累積
   ↓
Iteration 3 (operator = traj_pool_summary)
   ↓  LLM 看所有歷史 → 生成「風險感知指導」
   ↓  base agent 拿著 risk-aware prompt 重跑
```

每個 instance 跑 N 輪（paper 用 N=3），traj.pool 持續累積。**模型權重完全沒改**，純粹靠 system prompt 演進把結果推上去。

### 2.2 三個核心 Operator（**這是關鍵的「huh that's clever」**）

#### Operator 1: `alternative_strategy`（失敗導向的 revision）

跑在 Iteration 2，**只看最近一次失敗**。Prompt 設計（節錄自 `SE/operators/alternative_strategy.py`）：

```python
system_prompt = """You are an expert software engineering strategist specializing in 
breakthrough problem-solving. Your task is to generate a fundamentally different approach 
to a software engineering problem, based on analyzing a previous failed attempt.

CRITICAL: Your strategy must be architecturally dissimilar to avoid the same 
limitations and blind spots."""
```

要求 LLM 給出**「正交策略」**：換 paradigm（runtime analysis ↔ static analysis）、換 entry point（dependencies ↔ core logic）、換邏輯順序（symptom-to-cause ↔ cause-to-symptom）。這比 "try again" 強很多——它是**有意識地往相反方向走**。

#### Operator 2: `crossover`（跨 trajectory 的 recombination）

跑在 Iteration 3+。**同時取兩條有效 trajectory**，要求 LLM 找出各自的強項與共享盲點，生成 hybrid 策略：

```python
# 來自 crossover.py
prompt = f"""Analyze these two approaches and create a superior hybrid strategy:
APPROACH 1: {trajectory1[:600]}
APPROACH 2: {trajectory2[:600]}
Requirements:
1. Combine the most effective elements from both approaches
2. Address the limitations observed in each approach
3. Cover blind spots that neither approach addressed individually
4. Provide a more comprehensive and robust solution methodology"""
```

關鍵洞見：**這是遺傳演算法的 crossover 邏輯直接套到自然語言策略上**。每條 trajectory 不只代表一個答案，而是「**一個有特定強弱的解題範式**」。組合兩個範式的互補長處，比單純取 majority vote 更強。

#### Operator 3: `traj_pool_summary`（refinement + 風險感知）

跑在 Iteration 3+。**看所有歷史 attempts**，prompt 要求 LLM 產出結構化三段：

```
BLIND SPOTS TO AVOID:  [2-3 條]
CRITICAL RISKS:         [2-3 條]
STRATEGIC APPROACH:     [2-3 句]
```

這是 refinement 但帶**全局視野**——不只是「上次錯哪」，而是「整個軌跡池告訴我們這類任務的系統性陷阱是什麼」。

### 2.3 為什麼這個設計能拿 80%

三件事疊加：
1. **Iteration 1 確保 baseline**（沒有 operator 干擾的純 SWE-agent 表現）
2. **Iteration 2 強迫 orthogonal exploration**（避免在錯誤方向重複耗 token）
3. **Iteration 3+ 累積**（後面 iteration 看到的 traj.pool 越來越豐富，risk-aware guidance 越來越準）

**SWE-bench Verified Top1 結果**（paper 報告，5 個 LLM 跨模型平均）：
- Base SWE-agent: 基準線
- SE-Agent: **最多 55% 相對提升**，Top1 open-source 達 80%

> **實際讀程式碼的驗證**：`SE/operators/alternative_strategy.py` 第 110 行 fallback 機制 — 當 LLM 呼叫失敗時，給出 hard-coded minimal-viable-change 提示。這是**生產級的容錯設計**，不是論文 demo。

---

### 思考
## 4. Limitations / Honest Assessment

### 4.1 作者坦承的限制

- **成本爆炸**：3 個 iteration × 500 個 instance = 1500 次 base agent run + 1500 次 operator LLM call。在 DeepSeek API 上跑一次完整實驗估計 **$2000-5000**。這不是日常可負擔的設計。
- **Operator 品質依賴 LLM**：alternative_strategy 的「正交」判斷品質直接決定 iteration 2 表現。如果用 weak model 跑 operator，效果會**比 baseline 還差**（paper Table 5 顯示）。
- **軌跡池冷啟動問題**：只有 iteration ≥ 2 才有 traj.pool 餵資料，第一輪仍是盲目。

### 4.2 我們的獨立批判

1. **「55% 相對提升」是 cherry-picked 表達**：5 個 LLM 中，強 model 提升小（5-10%），弱 model 提升大（55%）。整體平均下來沒有 headline 那麼戲劇化。**讀 paper Table 必看 baseline 對象**。
2. **「自我進化」其實是「自我 prompt 進化」**：模型權重沒動，純粹 system prompt 在演化。**這是 prompt engineering 的勝利，不是 AGI 的勝利**。但反過來說，這代表**任何人都能復現**，不需要 GPU。
3. **跨實例遷移性未驗證**：paper 顯示同一個 instance 跨 iteration 變強，但**沒做**「把 issue A 學到的教訓遷移到 issue B」。如果沒有遷移，traj.pool 就只是 per-task cache，不是真正意義的 learning。
4. **Operator registry 寫死兩個**：repo 只有 `alternative_strategy`、`crossover`、`traj_pool_summary` 三個。新 operator 要重複同樣的 `BaseOperator` boilerplate 150 行。可以改進但作者沒做。
5. **缺乏 trajectory 摘要的 embedding-based 檢索**：traj.pool 純 JSON 全文匹配，當 iteration > 5 開始沒效率。**與 Mem0 的 semantic memory 整合會是明顯的下一步**。

### 4.3 與既有方法的精準對比

| 方法 | 跨 trajectory 借鑑 | 失敗覆蓋 | 訓練-free | 計算成本 | SWE-bench |
|------|------------------|---------|---------|---------|-----------|
| ReAct + Reflexion | ❌ 純 verbal | ❌ | ✅ | 1x | ~40% |
| MCTS（AFlow） | ⚠️ 共享 state | ⚠️ | ✅ | 5-10x | ~55% |
| Self-Consistency | ❌ 投票 | ❌ | ✅ | N x | ~50% |
| **SE-Agent** | ✅ traj.pool | ✅ revision | ✅ | 3-5x | **80%** |
| 監督式 RL fine-tune | ✅ policy gradient | ✅ | ❌ | 100x+ | ~70% |

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 5.1 對 firn（個人 AI agent 框架）

**Difficulty: MODERATE** | **Free API 可運作（DeepSeek/Gemini Flash）**

**建議 1 — 把 TurnsLogger 升級成 trajectory pool**（P1 級）

`firn/src/firn/observability/turns_logger.py` 已經存每個 turn。把 schema 從「flat log」改成 SE-Agent 風格的 `traj.pool`:

```python
# 偽代碼，firn 端可考慮
traj_pool[conversation_id] = {
    "problem": user_query,
    "1": {
        "strategy": "...",  # LLM 摘要這輪嘗試的策略
        "status": "failed" | "success" | "stuck",
        "modified_files": [...],
        "tools_used": [...],
        "reasoning_pattern": "...",  # 從最後一個 assistant 訊息抽出
    },
    "2": {...}  # 下次同類 query 累積
}
```

**觸發點**：當偵測到 `stuck loop`（`turn_loop.py` 已有這個 detection），把這次嘗試寫進 traj.pool。

**建議 2 — 失敗導向 alternative_strategy prompt**（TRIVIAL）

把 `firn` 的 stuck-loop fallback（目前在 `turn_loop.py`）從「直接報錯」改成「先做一次 alternative_strategy LLM call，把新策略注入 system prompt 再 retry」。

prompt 模板可直接抄 SE-Agent `alternative_strategy.py` line 60-100，MIT 授權，**記得引用**。

**建議 3 — Context Engineering 對接**（HARD）

firn 已有 ContextBuilder（I2）。SE-Agent 證明 system prompt 演進比 context compaction 更有效。**未來 firn 的方向應該是「當 conversation 進入 N 輪且卡住時，自動從 traj.pool 提煉 risk-aware guidance 塞進 system prompt」**——不是重做，是**接在現有 compaction 後面當 layer 2**。

**注意**：firn 的定位是「個人 AI agent 框架」，不是 SWE-bench 高吞吐。所以 **traj.pool 不必像 SE-Agent 那樣存 500 個 instance**，存**單一 conversation 的最近 5 次 retry** 就夠了。

### 5.2 對 managed-agents（batch runner）

**Difficulty: MODERATE** | **純本地、不需 API**

**建議 — 把 SE-Agent 三個 operator 移植成 batch task 前處理器**

`archive/research-pipeline/researcher.py` 跑 daily research cron 已經有「單 trajectory 從頭到尾」的失敗重試。在 `core/v2/harness_v2.py` 之上加：

```python
# 偽代碼
def run_with_evolution(task, n_iter=3):
    traj_pool = {"problem": task}
    for i in range(1, n_iter+1):
        if i == 1:
            result = run_base(task)  # 現有邏輯
        elif i == 2:
            strategy = operator_alternative(traj_pool)
            result = run_base(task, system_prompt=strategy)
        else:
            guidance = operator_pool_summary(traj_pool)
            result = run_base(task, system_prompt=guidance)
        traj_pool[str(i)] = summarize(result)
    return traj_pool[str(n_iter)]
```

**實際好處**：daily research 的 quality 應該會從「一次 60 分」提升到「三次平均 75 分」。但**成本翻 3 倍**——只在 priority research 上用。

### 5.3 對 obsidian-vault 知識庫

**Difficulty: TRIVIAL** | **可立即做**

`extract_research_knowledge.py` 已經處理 Jaccard 去重。SE-Agent 這個 topic 與既有的 self-improving 知識庫（5/26 Mem-* + Letta、5/27 ACE、5/31 Reflexion）**Jaccard 預期落在 0.4-0.5 灰色地帶**。建議：

- gray_zone flag 設 true
- 寫進 `research/2026-06-15-se-agent-self-evolution.md`
- 在該檔加 cross-link 指向 5/26、5/27、5/31 的同類主題

---


### 來源

- 原始報告：2026-06-15-se-agent-self-evolution-trajectory-optimization.md
- 類型：
- 連結：
