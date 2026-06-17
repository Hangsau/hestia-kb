---
_slug: 40-Resources-_mixed-explorations-2026-05-23-otp_gate-py---重做版-2026-05-23
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-otp_gate-py---重做版-2026-05-23.md
title: otp_gate.py — 重做版（2026-05-23）
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- false
- hearth
- inbox
- otp
- saga
- str
- task
- token
- true
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "Google A2A Protocol — Hearth 整合分析"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
---

**延續自**: [[2026-05-23-SAGA-深度追加]] [[2026-05-23-agent-governance-patterns]]

**日期**: 2026-05-23 | **來源**: A2A GitHub README + SAGA leads | **類型**: 主題延續

---

## A2A Protocol 核心發現

### 定位：MCP 的「對等」而非「工具」

A2A (Agent2Agent) 是 Google 主導的開放協議（2025 年），核心定位：
> "enabling agents to collaborate with each other — as agents, not as tools"

與 MCP 的差異（極度清晰）：
| 維度 | MCP | A2A |
|------|-----|-----|
| 關係 | 主僕（client→server） | 對等（peer-to-peer） |
| 暴露內容 | tools/capabilities | agent identity + capabilities |
| 狀態 | stateless | 可保持長連接/streaming |
| 目標框架 | Anthropic/OpenAI（工具化） | 任意 framework（ADK/LangGraph/BeeAI...） |

**對 Hermes 的直接意義**：Hearth 目前是 MCP 模式（inbox/ 用 HTTP + JSON），A2A 可讓 Hestia↔Talos 從「工具呼叫」升級為「對等協商」。

### 核心機制

**1. Agent Cards**（相當於 SAGA 的 Provider registry）：
```json
{
  "name": "Hestia",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionSupport": true
  },
  "skills": [...],
  "defaultApiVersion": "2025-05-15"
}
```

**2. 三種互動模式**：
- Task push（同步 request/response）
- Streaming（SSE，long-running 任務）
- Push notifications（server-initiated，即時響應）

**3. 狀態協商**：
- `Task` object 有完整生命週期（submitted → working → completed）
- 雙方都可在任意時刻查詢 task status
- 類似 SAGA 的 token 機制但更完整

### 與 Hearth 的架構對應

| Hearth 現況 | A2A 等價物 | 改動成本 |
|------------|------------|---------|
| `inbox/` 訊息 | A2A Task push/stream | Medium（改 inbox 路由） |
| `tasks/` 任務追蹤 | A2A Task lifecycle | Low（已有相似結構） |
|  無 identity layer | Agent Card + Auth | High（需 PKI 或 trust） |
|  ad-hoc delivery | A2A push notification | Medium |

### 與 SAGA 的互補

SAGA（NDSS 2026）提供形式化安全證明；A2A 提供 production-ready 實作。兩者重疊：
- **都有** agent discovery（Provider/Agent Card）
- **都有** capability negotiation
- **SAGA 強項**：cryptographic identity、OTK、formal verification
- **A2A 強項**：多 framework 支援、streaming、vendor backing

**整合可行路徑**：
1. **短期**：Hearth inbox 接收方加 allowlist check（SAGA ACP 概念，低成本）
2. **中期**：把 Hearth 訊息轉型成 A2A Task format（保留現有 workflow + 增加 streaming）
3. **長期**：研究 SAGA 密碼學 identity 能否疊加在 A2A 之上

### Google A2A Python SDK（可直接使用）

```bash
pip install a2a-sdk
```

SDK 支援：
- Python agent 快速 expose 成 A2A server
- Client 可向任何 A2A server 發送 task
- Streaming 支持（Server-Sent Events）

**可用於**：把 Hestia 或 Talos 快速 expose 成 A2A endpoint，測試與外部 A2A agent 的互通性。

## Hermes 直接行動項

### 1. WS-010 OTP gate（低懸果實，承認 phantom 重做）

proposal 2026-05-20 宣稱實作但 `otp_gate.py` 不存在（phantom）。SAGA 的 OTK 概念提供了明確的實作藍圖：

```python
# otp_gate.py — 重做版（2026-05-23）
# 基於 SAGA OTK 概念：每次高風險操作需要一次性通行證

import secrets, time
from typing import Optional

_pending: dict[str, dict] = {}  # token -> {otp, expires_at, used}

def generate(secret: str, ttl_seconds: int = 300) -> tuple[str, str]:
    """Generate OTP. Returns (token, otp). Token for retrieval, OTP for user."""
    otp = secrets.token_hex(3).upper()  # 6 hex digits
    token = secrets.token_urlsafe(16)
    _pending[token] = {"otp": otp, "expires_at": time.time() + ttl_seconds, "used": False}
    return token, otp

def verify(token: str, otp: str) -> bool:
    """Verify OTP. Returns True if valid and not expired."""
    if token not in _pending:
        return False
    entry = _pending[token]
    if entry["used"] or time.time() > entry["expires_at"]:
        return False
    if entry["otp"] != otp.upper():
        return False
    entry["used"] = True
    return True

# Smoke test
if __name__ == "__main__":
    tok, code = generate("test")
    assert verify(tok, code) == True
    assert verify(tok, "WRONG") == False
    assert verify("fake", "123456") == False
    print("otp_gate.py smoke test PASSED")
```

### 2. Hearth ACP 實驗（無需 PKI）

在 `inbox/hestia/` 的接收端加簡單 allowlist：
```python
# inbox_acp.py
_ALLOWLIST = {"talos": True}  # 只有 Talos 可以聯繫 Hestia

def check_acp(sender: str) -> bool:
    return _ALLOWLIST.get(sender, False)
```
測試：用另一個 agent（如某個 research agent）嘗試發 inbox，驗證被擋。

### 3. A2A SDK SPIKE（探索性質）

```bash
pip install a2a-sdk
# 測試把 Hestia expose 成 A2A server
```

## 未追蹤 Leads

- A2A Protocol Spec: https://a2a-protocol.org/latest/specification/
- A2A Python SDK: https://github.com/a2aproject/a2a-python
- SAGA GitHub: https://github.com/gsiros/saga
- ACE paper (PDF only): 2504.20984
- ProVerif tutorial for protocol verification
- A2A DeepLearning.AI course: https://goo.gle/dlai-a2a

## ✅ 本次探索完成

