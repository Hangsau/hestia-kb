---
_slug: 40-Resources-_mixed-explorations-2026-06-03-alexzhang13-rlm-官方-Codebase-+-lamorel
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-alexzhang13-rlm-官方-Codebase-+-lamorel.md
title: 探索：alexzhang13/rlm 官方 Codebase + lamorel
created: '2026-06-03'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：alexzhang13/rlm 官方 Codebase + lamorel

**日期**: 2026-06-03 | **來源**: 前期筆記未追蹤 leads（Forge/Gambit + RLM paper note） | **類型**: EXPLORATION
**URLs**:
- https://github.com/alexzhang13/rlm
- https://github.com/flowersteam/lamorel

---

## Source Insight — alexzhang13/rlm (4,407⭐)

**API Overview**：從 `rlm/core/rlm.py` 的 `RLM` class 讀到的關鍵設計：

```python
rlm = RLM(
    backend="openai",
    backend_kwargs={"model_name": "..."},
    environment="local",  # local, ipython, docker, modal, prime, daytona, e2b
    environment_kwargs={...},
    persistent=False,      # reuse env across completion() calls
    custom_tools={...},    # inject functions into REPL namespace
    compaction=False,      # keep history in REPL variable, compact at threshold
    max_depth=1,           # recursion depth
    max_iterations=30,
)
```

**Three environment tiers**（直接映射 `guardian-sandboxing-gradient` 的三層隔離）：
1. `local` — same process, exec(), minimal security
2. `ipython` — real IPython session, subprocess mode adds cell_timeout + namespace isolation
3. `docker/modal/prime/daytona/e2b` — cloud sandboxes, complete isolation

**`SupportsPersistence` interface**：正是 `guardian-sandboxing-gradient` 提到的合約：
```python
class BaseEnv:
    def setup(self, ...): ...
    def execute(self, code: str): REPLResult: ...
    def teardown(self): ...

class SupportsPersistence:
    def save_state(self) -> dict: ...
    def restore_state(self, state: dict): ...
```

**`get_environment()` factory**：靜態工廠方法，根據 `EnvironmentType` 字串返回對應 environment 實例。這是從抽象到具體的標準工廠模式，和提案中的 sandbox tier selector 完全對應。

**`persistent=True` 的語意**：跨 `completion()` 調用的環境重用，這意味著 `persistent=True` 時的 REPL 狀態可以攜帶長期的 symbol/graph 結構。這是 RLM 實現 long-context handling 的另一個維度——不是靠 context window，而是靠 persistent REPL state。

**`compaction` 機制**：當 root context 到達 `compaction_threshold_pct`（預設 0.85）時，對 `history` 變數做 summarization。這是「structured compression」而非 naive truncation——壓縮的單位是 REPL 中的完整 history 對象，而非游離的文字 token。

---

## Source Insight — lamorel (247⭐)

**定位**：Python library for RL practitioners using LLMs, client-server distributed architecture.

**核心差異**：lamorel 的焦點是「RL 中批量使用 LLM」而非「RLM 的符號遞歸」。它提供：
- `lm_server.generate()` — 文本生成
- `lm_server.score()` — 計算 token sequence 的 log probability（核心 RL primitive）
- 分布式：多 LLM server 自動分流請求

**架構**：Client (`Caller`) → 多 LLM server 進程。適合「同時跑多個 RL environment」的場景。

**與 RLM 的關係**：不同焦點但互補。RLM 處理 single-agent 的 long-context 問題；lamorel 處理 multi-agent RL 的 throughput 問題。两者都依赖「LLM + code execution」的组合。

---

## Hermes 啟發

### 1. `get_environment()` factory 是 sandbox tier selector 的正確形式

`guardian-sandboxing-gradient` 提案要「三層隔離的具體實作」。`rlm/environments/__init__.py` 的 `get_environment()` 正是這麼做的：
- 輸入：`environment: EnvironmentType`（`'local'|'ipython'|'docker'|...`）
- 輸出：符合 `BaseEnv` 接口的實例
- 工廠模式的好處：調用方不需知道 concrete class，只要知道 string label

Talos governance pipeline 的 tool isolation 可以參考這個模式：`get_tool_backend('sandboxed')` → 返回符合 `ToolBackend` 接口的隔離執行層。

### 2. `SupportsPersistence` 介面是 WS-035 drift penalty 的參考

`persistent=True` 讓 REPL 跨 completion 調用保留狀態。對於 heartbeat_learning.py 的 drift penalty 設計：
- 新的 distillate 可以 call `env.save_state()` / `env.restore_state()`
- 矛盾發生時 restore 到上一個 trusted state
- 這比「時間衰減」更有結構性——是「explicit invalidation」而非 implicit decay

### 3. `compaction` 是長期記憶壓縮的具體演算法

`TieredCompact` 在 Forge 的 context 策略（保持最近 N 輪）和 RLM 的 history summarization（到達 threshold 時壓縮）中都出現。這是一個收斂的模式：
- 觸發條件：token count 達到 context limit 的 X%
- 動作：對 history 變數做 semantic compression
- 輸出：壓縮後的 history 替換原始對象

Hermes 的 memory consolidation 可以參考這個觸發條件設計（`staleness_threshold` → `compact_trigger`）。

---

## 未追蹤 Leads

- ~~https://github.com/alexzhang13/rlm~~ → 已讀（見上方）
- ~~https://github.com/flowersteam/lamorel~~ → 已讀（見上方）
- https://github.com/alexzhang13/rlm-minimal — RLM minimal implementation (linked from README)

## ✅ 本次探索完成