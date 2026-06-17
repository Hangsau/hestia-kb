---
_slug: 40-Resources-_mixed-explorations-2026-05-27-llm-agent-loop-tool-patterns
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-llm-agent-loop-tool-patterns.md
title: 探索筆記 — 2026-05-27
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索筆記 — 2026-05-27

**主題**: LLM Agent Loop 設計 + MCP Tool 設計模式

## Per-Source Insights

### 1. sketch.dev — "The Unreasonable Effectiveness of an LLM Agent Loop with Tool Use" (447 pts)

**核心發現：loop 本身是 tool，不是工具清單**

Zeyliger (Sketch) 的核心 observation：agent loop 本身是最重要的 tool。9 行核心迴圈：
```python
while True:
    output, tool_calls = llm(msg)
    if tool_calls:
        msg = [handle_tool_call(tc) for tc in tool_calls]
    else:
        msg = user_input()
```

關鍵 insight：
- **Persistence is the key property**：agent loop 可以是 persistent 的——如果沒有某個 tool，會自己去裝；如果 `grep` 選項不同，會自己適應。
- **「working」≠ 「agent-usable」**：一個 tool 可以 return 正確資料但仍然 fail，因為 agent 無法判斷何時該 call 它。
- 工具選擇的 non-deterministic 性——同一個 task，每次跑的路徑可能不同。

對 Hermes 的啟發：Hermes 的 heartbeat/action loop 是否足夠 "persistent"？目前 heartbeat actions 是離散的、獨立的 action，未形成真正的 loop continuity。

### 2. Arcade.dev — "54 Patterns for Building Better MCP Tools" (2026-02-09)

**核心發現：54 patterns 橫跨 4 個 cross-cutting concerns**

Arcade 從 8000+ tools 萃取出 54 個 patterns，分 10 categories。4 個 cross-cutting concerns：

| Concern | 核心問題 |
|---------|---------|
| **Agent Experience** | 為 LLM 而非人類設計——description、parameter names、error messages 要優化給 model |
| **Security Boundaries** | 授權和 secrets 必須在 server side 處理，prompt 只能表達 intent |
| **Error-Guided Recovery** | Error 要能 teaching，不只是 fail。429 → "rate limited, retry after 30s or reduce batch size to 50" |
| **Tool Composition** | 工具要能像 Unix pipes 一樣組合，而非 chain of command |

**3 軸分類法**：

```
Maturity (vertical): Atomic → Orchestrated
Integration: API / DB / FS / SysOps
Access: Sync / Async / Streaming / Event-driven
```

坐落在這 3 軸的交點，決定了需要哪些 patterns。

**Tool Types**（Query / Command / Discovery）也是分類起點。

**Observable signals between levels**：
- High retry rates → tool needs better descriptions + error guidance
- Repeated tool sequences → time to bundle
- Partial completions on multi-step → need transaction boundaries + compensation

對 Hermes 的啟發：
- WS-035 policy engine gateway 正在做的 tool governance，正是 Arcade 的 "Security Boundaries" concern
- Herme s現有工具描述是否已優化給 LLM？還是以人類可讀為主？
- Error-guided recovery：Hermes tool 失敗時的 error message 是否提供可操作的恢復指引？

## 跨文章 Synthesis

### 一致收斂點
1. **「working」≠ 「agent-usable」**：Sketch 和 Arcade 共同強調。Tool 設計時要問的不是 "does it work?" 而是 "can an LLM use it correctly without human intervention?"
2. **Loop as fundamental primitive**：Sketch 的 9-line loop 是核心 insight；Arcade 的 "composition" pattern 談的也是如何讓 tools 形成有效的 loop chain。
3. **Error recovery must be actionable**：兩者都強調 raw error code (429, 500) 對 LLM 沒用，要有引導性的恢復資訊。

### 差異
- Sketch 偏向 "minimal tool set, maximum loop"（一個 bash 可以完成大部分任務）
- Arcade 偏向 "rich catalog, structured patterns"（8000 tools 的經驗總結）

### 對 Hermes 的方向性啟發
- **Tool description audit**：現有工具描述是否為 LLM 優化？還是人類視角？
- **Error message rewrites**：所有工具的 error response 應包含 recovery guidance
- **Heartbeat loop persistence**：heartbeat actions 是否可以形成更 persistent 的 loop，自動安裝缺失能力？

## Untracked Leads

- https://sketch.dev/blog/agent-loop （已讀）
- https://blog.arcade.dev/mcp-tool-patterns （已讀）
- https://arcade.dev/patterns （full catalog，54 patterns 完整列表）
- https://arxiv.org/abs/2602.20426 （Learning to Rewrite Tool Descriptions，arXiv HTML fetch，✅ 已讀）

## ✅ 本次探索完成
