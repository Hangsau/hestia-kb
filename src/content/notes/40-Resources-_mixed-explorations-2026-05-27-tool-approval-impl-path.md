---
_slug: 40-Resources-_mixed-explorations-2026-05-27-tool-approval-impl-path
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-tool-approval-impl-path.md
title: Tool Approval Implementation Path — CUGA → WS-035 Blueprint
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Tool Approval Implementation Path — CUGA → WS-035 Blueprint

**日期**: 2026-05-27
**延續自**: [[2026-05-27-CUGA-Agent---5-Layer-Runtime-Governance---Repo-Architecture]], [[2026-05-26-mcp-security-gateway-spec-deep-dive]], ws-035 proposal

---

## What is Tool Approval (CUGA Layer 4)

CUGA 在 code generation **之後**、實際 execution **之前**有一個獨立的 pause gate：
```
Agent generates code → [PAUSE] → Human confirms → Execution proceeds
```

**關鍵區分**：脫離 agent reasoning loop，確保高風險操作有獨立把關。

## Hermes 目前的位置

WS-035 blueprint 已定義 `PolicyInterceptor.check_order`:
1. Human approval required → DENY
2. allowed_tools non-empty and tool not in list → DENY
3. arguments matches blocked_pattern → DENY
4. call_count >= max_tool_calls → DENY

Step 1 對應 Tool Approval，但實作細節（如何在 tool call hop 插入 pause）是空白。

## 實作路徑分析

### Path A: Gateway middleware intercept（推薦）

在 `gateway/run.py` 的 `handle_function_call()` 層插入：

```python
async def handle_function_call(self, tool_name, arguments):
    # Check PolicyInterceptor step 1
    policy = self._get_governance_policy()
    if policy.get('require_human_approval'):
        if tool_name in policy.get('hitl_tools', []):
            # Pause and wait — emit placeholder, don't execute
            return await self._request_tool_approval(tool_name, arguments)
    # ... continue to actual execution
```

**優點**：直接在高風險 tool call hop 拦截，不需要改 agent loop
**缺點**：需要定義哪些 tool 觸發 HITL（危險工具清單）

### Path B: OTP gate 擴展（WS-031 已有的基礎）

`otp_gate.py` 的 generate/verify/approve flow 已經是 HITL 機制。擴展方向：
- 將 `require_human_approval: true` 的 tool call 路由到 OTP gate
- 缺點：OTP 是 session-level approval，不是 per-tool

### Path C: A2A 協議的 Task routing

CUGA 的 Supervisor 架構用 A2A 協助 multi-agent task routing。Hermes 的 Talos 可以作為 Supervisor：
- Hestia 生成 tool call → 發給 Talos 審批 → Talos 回傳 approval → Hestia 執行

**參考**：`a2a-protocol.org/latest/specification/`（SAGA/ACE 的基礎）

## 決定因素

| 因素 | Path A | Path B | Path C |
|------|--------|--------|--------|
| 實作複雜度 | 低 | 低 | 高 |
| 現有基礎 | ❌ | ✅ OTP gate | ❌ |
| 脫離 agent loop | ✅ | ✅ | ✅ |
| 跨 agent 溝通 | ❌ | ❌ | ✅ |
| 適合場景 | 單 agent 高風險工具 | 審批流程 | multi-agent 協作 |

**推薦**：Path A + Path B 混合
- 高風險工具（terminal write, skill_manage, git push）→ Path A 直接拦截
- 需要正式審批的複雜操作 → 路由到 OTP gate（Path B）

## 對 ws-035 的直接貢獻

WS-035 Phase 2 的下一個具體步驟：
> Phase 2: gateway tool call interception（需更精確的 hook 定位）

找到了：就是 `gateway/run.py` 的 `handle_function_call()` method。這是 gateway 暴露的最後一個同步接取點，tool call 在這裡轉發給 executor。

**驗證**：
```bash
grep -n "handle_function_call\|handle_tool_call" /root/hermes-agent/gateway/run.py
```

若存在：在該 method 內插入 PolicyInterceptor check。
若不存在：找 `model_tools.handle_function_call()` — 這是另一個可能的 hook 位置。

---

## ✅ 本次探索完成

**未追蹤 Leads**:
- https://github.com/cuga-project/cuga-agent — CUGA main repo（Intent Guard source code 在 `src/cuga/policies/intent_guard.py`）
- https://huggingface.co/datasets/ibm-research/BPO-Bench — BPO benchmark（26 tasks, enterprise workflows）