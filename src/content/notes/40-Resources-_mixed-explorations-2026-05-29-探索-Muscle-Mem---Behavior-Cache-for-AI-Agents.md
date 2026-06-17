---
_slug: 40-Resources-_mixed-explorations-2026-05-29-探索-Muscle-Mem---Behavior-Cache-for-AI-Agents
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-探索-Muscle-Mem---Behavior-Cache-for-AI-Agents.md
title: 探索：Muscle-Mem — Behavior Cache for AI Agents
date: 2026-05-29
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- behavior
- cache
- check
- engine
- llm
- mem
- muscle
- python
- tool
created: '2026-05-29'
updated: '2026-06-15'
status: budding
---

# 探索：Muscle-Mem — Behavior Cache for AI Agents

**日期**: 2026-05-29 | **來源**: HN (226 pts) | **類型**: 架構研究

## 核心概念

muscle-mem (764 ⭐, Apache-2.0) 是一個 Python SDK，記錄 agent 的 tool-calling patterns，當任務再次出現時確定性回放（fallback to agent mode if edge cases detected）。

目標：把 LLM 移出重複任務的熱路徑，提升速度、降低變異性、節省 token 成本。

## 關鍵設計

### 三元件架構

1. **Engine**：封裝 agent，任務執行時判斷 cache-hit 或 cache-miss
2. **Trajectory**：記錄 tool calls 的序列，包含 arg 值（預設靜態）
3. **Check**：快取驗證的核心 building block

```python
from muscle_mem import Engine, Check

engine = Engine()
engine.set_agent(your_agent).finalize()
engine("do some task")  # cache miss → 給 agent
engine("do some task")  # cache hit → 直接 replay
```

### Check 機制（快取驗證）

```python
Check(
    capture: Callable[P, T],    # 從環境抓特徵
    compare: Callable[[T, T], bool|float],  # 比對環境是否匹配
)
```

每個工具可附加 pre_check（執行前驗證）或 post_check（執行後驗證）。這是 behavior cache 的關鍵——不是簡單的輸入輸出對照，而是環境特徵變化時讓 cache 失效。

### Top-Level Parameters（動態參數映射）

對於每次需更換值的場景（如表單填入 Bot），可用 `params` 標記動態參數：

```python
@engine.function()
def type(text: str):
    ...

# 第一次：存入 type("John")，動態 arg `text` 映射到 top-level param `name`
engine("fill form: John", params={"name": "John"})
# 第二次：cache hit，但用 "Jane" 而非 "John"
engine("fill form: Jane", params={"name": "Jane"})
```

具體來說：記錄 trajectory 時若發現某 tool arg 直接匹配 top-level param，則標記為動態，按 key 映射。

### Tool Instrumentation

- `@engine.function()` 裝飾一般函數
- `@engine.method()` 裝飾物件方法（inject `self` 狀態）

```python
class SomeClient:
    @engine.method()
    def hello(self, name: str):
        ...

client = SomeClient()
engine.set_context(client)  # runtime object injection
```

### 與其他方案的區別

muscle-mem **不是 another agent framework**。它嵌入世間任何既有的 agent 實作，提供快取層。不是讓你換框架，而是讓你的現有 agent 加速。

## 與 Hermes 的關聯

### 對 WS-035 的直接價值

heartbeat_learning.py 的 distillate 為何會產生語義跳躍？缺少的是**stable behavior replay**機制。Muscle-Mem 的 Check 機制提供了一種思路：

- capture callback = distillate validation（在新的上下文是否仍然有效？）
- compare callback = drift detection（distillate 的環境前提是否還滿足？）

若 drift penalty 加入 capture/compare 邏輯，可以解決「短期記憶被新Session覆蓋」的問題。

### 對 heartbeat loop persistence 的啟發

Agentic Memory 論文（Yu et al., 2026）訓練 store/retrieve/update/summarize/discard 作為工具。Muscle-Mem 的 behavior cache 思路更窄——只處理「確定性可復現」的模式。但這個窄的方向剛好是 heartbeat 最需要的：distillate 出來的穩定 pattern，應該在類似的環境觸發時自動 replay，而不是每次都要 LLM 推理。

### 架構啟發

```
Engine(task) → check cache-hit?
  ├─ YES: replay trajectory (no LLM call)
  └─ NO:  pass to agent
         → collect tool call events
         → store as new trajectory
```

這個架構比 RAG 更直接——不是找「最相似的過去」，而是認「完全匹配的環境前提 + 已知的 action sequence」。對於 heartbeat 自主行為（每次心跳的環境前提相對穩定），這種 pattern 更適用。

## 未追蹤 Leads

- https://github.com/pig-dot-dev/muscle-mem/blob/main/examples/cua.py — computer-use agent 實作範例
- Read: "Muscle Mem - Removing LLM calls from Agents"（部落格文章）
- Discord: https://discord.gg/muscle-mem（feedback channel）

## ✅ 本次探索完成
