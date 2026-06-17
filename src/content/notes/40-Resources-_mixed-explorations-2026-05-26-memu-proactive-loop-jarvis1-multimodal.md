---
_slug: 40-Resources-_mixed-explorations-2026-05-26-memu-proactive-loop-jarvis1-multimodal
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-memu-proactive-loop-jarvis1-multimodal.md
title: memU / JARVIS-1 架構探索 — Proactive Memory 模式
created: '2026-05-26'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# memU / JARVIS-1 架構探索 — Proactive Memory 模式

**日期**: 2026-05-26

**延續自**: [[2026-05-26-agent-memory-architecture]]

## Source 1: memU proactive.py (198 lines)

**URL**: `https://raw.githubusercontent.com/NevaMind-AI/memU/main/examples/proactive/proactive.py`

**核心模式**：非同步 background task 觸發記憶

```python
async def trigger_memorize(messages: list[dict[str, any]]) -> bool:
    global RUNNING_MEMORIZATION
    try:
        memorize_awaitable = memorize(messages)
        RUNNING_MEMORIZATION = asyncio.create_task(memorize_awaitable)
    except Exception as e:
        print(f"\n[Memory] Memorization initialization failed: {e!r}")
        return False
    else:
        print("\n[Memory] Memorization task submitted.")
        return True

async def check_and_memorize(conversation_messages: list[dict[str, any]]) -> None:
    """Check if memorization threshold is reached and trigger if needed."""
    # Skips triggering if a previous memorization task is still running
```

**觸發時機**：每 N messages threshold（`N_MESSAGES_MEMORIZE = 2`），非 user request。

**架構意義**：
- `memory.local.memorize` 模組是 proactive trigger 的本體
- `_get_todos()` 來自 `memory.local.tools` — 可見 todos 也是 memory layer 的一部分
- 這不是 pure reactive（收到 user prompt 才記憶），而是系統自發的內部迴圈

**與 Hermes 的對比**：
- Hermes 是完全 reactive（每次 session 末、被要求才記憶）
- memU 是 proactive threshold-based（internal loop，主動檢查 threshold）
- 這可能是「更像人類記憶」的設計——重要的事自然浮現，不依賴外部觸發

**SDK 整合**：使用 `claude_agent_sdk` (Anthropic official SDK)，而非直接用 raw API。

---

## Source 2: JARVIS-1 (Minecraft Multimodal Agent)

**URL**: `https://craftjarvis-jarvis1.github.io/`

**核心貢獻**：
- Minecraft 開放世界代理，多模態輸入（視覺 + 語言）
- **多模態記憶**：pre-trained knowledge + 實際遊戲生存經驗
- 終身學習 paradigm → self-improving agent

**Self-Improving 迴圈**：
```
Epoch 1: 10 steps → 失敗（缺 furnace）
Epoch 2: 12 steps → 失敗（缺 fuel）
Epoch 3: 11 steps → 成功（更準確更高效）
```

每個 epoch 是獨立的嘗試，不是連續的 gradient descent——更像是「失敗模式庫」的建立。

**記憶增長模式**：區分 pre-trained knowledge（靜態）和 episodic experience（動態增长）。當任務失敗時，不是調整 model weight，而是記住「這次缺什麼」然後下次補足。

**與 Hermes 的對比**：
- Hermes 的 `memory-consolidator` 是 session 末被動總結
- JARVIS-1 是持續的 episodic memory accumulation + retrieval
- JARVIS-1 的 "obtain diamond pickaxe" 任務失敗時明確記住「缺 furnace/fuel」——這是結構化的失敗模式分類，不是 raw experience dump

---

## 跨源 Synthesis

### Proactive vs Reactive：兩種記憶哲學

| 系統 | 觸發方式 | 記憶內容 | 改進機制 |
|------|----------|----------|----------|
| Hermes (現有) | Reactive (session 末) | 對話摘要 | 外部 trigger |
| memU | Threshold-based proactive | messages list | internal async loop |
| JARVIS-1 | Task-driven episodic | 失敗模式 + 環境狀態 | epoch accumulation |

memU 的 proactive loop 是目前最接近「系統內建」模式的記憶觸發——不需要使用者刻意呼叫。

**對 Hermes 的啟發**：
1. 可以在 `heartbeat_v2.py` 加一個 internal proactive check，不依賴 session 外來觸發
2. 觸發條件可以是「上次 heartbeat 以來過了 X 小時」或「某個 metric 超過 threshold」
3. 這比 session 更容易實現——heartbeat 自己就是 trigger source

---

## 未追蹤 Leads

- `https://api.memu.so/docs` — memU Cloud API（Swagger UI，fetch 只回標題，文件需要登入或特殊路徑）
- `https://memu.so` — 官方主頁（只有品牌名，無內容）

## ✅ 本次探索完成

**探索日期**: 2026-05-26
**品質評級**: 中（memU proactive.py 完整，JARVIS-1 HTML 有內容，memU Cloud API 未取得實質內容）
**主要收穫**: proactive threshold-triggered memory 是比純 reactive 更符合「系統自主」精神的設計。memU 的 `asyncio.create_task(memorize())` 模式可直接映射到 Hermes 的 async heartbeat action。