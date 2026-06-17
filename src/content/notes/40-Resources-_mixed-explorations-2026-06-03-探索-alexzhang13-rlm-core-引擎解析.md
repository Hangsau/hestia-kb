---
_slug: 40-Resources-_mixed-explorations-2026-06-03-探索-alexzhang13-rlm-core-引擎解析
_vault_path: 40-Resources/_mixed/explorations/2026-06-03-探索-alexzhang13-rlm-core-引擎解析.md
title: 探索：alexzhang13/rlm core 引擎解析
date: 2026-06-03
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- alexzhang
- com
- custom
- environment
- environments
- github
- https
- main
- persistent
- rlm
created: '2026-06-03'
updated: '2026-06-15'
status: budding
---

# 探索：alexzhang13/rlm core 引擎解析

**日期**: 2026-06-03 | **來源**: [[2026-06-03-alexzhang13-rlm-codebase]]（未追蹤 leads）| **類型**: EXPLORATION
**URLs**:
- `https://github.com/alexzhang13/rlm/tree/main/rlm/core`
- `https://github.com/alexzhang13/rlm/blob/main/rlm/environments/__init__.py`

---

## Core Engine 架構

### rlm.py — RLM 主類

重點發現：

1. **`persistent` flag（預設 False）**：非持久模式下每次 `completion()` call 都會創建 fresh environment + LM handler，完成後 cleanup。持久模式（`persistent=True`）會跨 calls 重用 environment，並透過 `SupportsPersistence` interface 驗證環境支持與否。

2. **三隔離層的實作**：
   - `LocalREPL`：本地無隔離
   - `IPythonREPL`：subprocess，隔離 namespace
   - Cloud sandboxes（modal/daytona/prime/e2b）：獨立 machine，sub-calls 變成網路請求

3. **Subcall 經濟**：每個 completion call 內部維護 `max_concurrent_subcalls=4`，控制同時有多少 sub-RLM call 在跑。

4. **Custom tools 注入**：`custom_tools` / `custom_sub_tools` 傳入後經 `parse_custom_tools()` 處理，變成 REPL 可用的 function。

### environments/__init__.py — 環境 factory pattern

```python
def get_environment(environment: Literal["local", "ipython", "modal", "docker", "daytona", "prime", "e2b"], environment_kwargs: dict[str, Any]) -> BaseEnv:
```

每個環境用對應的 `*REPL` class 實例化，全部繼承 `BaseEnv`。工廠模式有利於動態替換隔離層。

---

## 與 Talos Governance 的對應

### 1. 三層隔離 → L1/L2/L3 梯度

RLM 實現了「非隔離 → 半隔離（IPython subprocess）→ 全隔離（cloud sandbox）」三層，與 Talos 提案的 `guardian-sandboxing-gradient` 完全對應。差別在於 RLM 的隔離是第一公民（`environment` 參數），而非 wrapper。

### 2. Persistent environment → 多 turn conversation state

`persistent=True` 時 `_persistent_env` 跨 calls 保存對話狀態。這相當於 Hermes 的 session persistence，但 RLM 把它做到 engine level，不需要外部 state store。

### 3. SupportsPersistence interface

```python
from rlm.environments import SupportsPersistence
# 實作 must implement: update_handler_address(), get_context(), ...
```

這個 interface 是新增環境時的合約，確保新隔離層不會意外破壞 persistent 邏輯。

---

## 未追蹤 Leads

- https://github.com/alexzhang13/rlm/blob/main/README.md#rlms-in-the-wild — DSPy.RLM, Ax, HALO 生產案例
- https://github.com/alexzhang13/rlm/tree/main/rlm/environments — 各環境實作差異（local vs ipython vs cloud）
- [[2026-06-03-alexzhang13-rlm-官方-Codebase-+-lamorel]] — lamorel multi-agent LLM 框架實作

---

## ✅ 本次探索完成


## Version 2 — 2026-06-03

# 探索：alexzhang13/rlm core 引擎解析

**日期**: 2026-06-03 | **來源**: [[2026-06-03-alexzhang13-rlm-codebase]]（未追蹤 leads）| **類型**: EXPLORATION
**URLs**:
- `https://github.com/alexzhang13/rlm/tree/main/rlm/core`
- `https://github.com/alexzhang13/rlm/blob/main/rlm/environments/__init__.py`

---

## Core Engine 架構

### rlm.py — RLM 主類

重點發現：

1. **`persistent` flag（預設 False）**：非持久模式下每次 `completion()` call 都會創建 fresh environment + LM handler，完成後 cleanup。持久模式（`persistent=True`）會跨 calls 重用 environment，並透過 `SupportsPersistence` interface 驗證環境支持與否。

2. **三隔離層的實作**：
   - `LocalREPL`：本地無隔離
   - `IPythonREPL`：subprocess，隔離 namespace
   - Cloud sandboxes（modal/daytona/prime/e2b）：獨立 machine，sub-calls 變成網路請求

3. **Subcall 經濟**：每個 completion call 內部維護 `max_concurrent_subcalls=4`，控制同時有多少 sub-RLM call 在跑。

4. **Custom tools 注入**：`custom_tools` / `custom_sub_tools` 傳入後經 `parse_custom_tools()` 處理，變成 REPL 可用的 function。

### environments/__init__.py — 環境 factory pattern

```python
def get_environment(environment: Literal["local", "ipython", "modal", "docker", "daytona", "prime", "e2b"], environment_kwargs: dict[str, Any]) -> BaseEnv:
```

每個環境用對應的 `*REPL` class 實例化，全部繼承 `BaseEnv`。工廠模式有利於動態替換隔離層。

---

## 與 Talos Governance 的對應

### 1. 三層隔離 → L1/L2/L3 梯度

RLM 實現了「非隔離 → 半隔離（IPython subprocess）→ 全隔離（cloud sandbox）」三層，與 Talos 提案的 `guardian-sandboxing-gradient` 完全對應。差別在於 RLM 的隔離是第一公民（`environment` 參數），而非 wrapper。

### 2. Persistent environment → 多 turn conversation state

`persistent=True` 時 `_persistent_env` 跨 calls 保存對話狀態。這相當於 Hermes 的 session persistence，但 RLM 把它做到 engine level，不需要外部 state store。

### 3. SupportsPersistence interface

```python
from rlm.environments import SupportsPersistence
# 實作 must implement: update_handler_address(), get_context(), ...
```

這個 interface 是新增環境時的合約，確保新隔離層不會意外破壞 persistent 邏輯。

---

## 未追蹤 Leads

- https://github.com/alexzhang13/rlm/blob/main/README.md#rlms-in-the-wild — DSPy.RLM, Ax, HALO 生產案例
- https://github.com/alexzhang13/rlm/tree/main/rlm/environments — 各環境實作差異（local vs ipython vs cloud）
- [[2026-06-03-alexzhang13-rlm-官方-Codebase-+-lamorel]] — lamorel multi-agent LLM 框架實作

---

## ✅ 本次探索完成
