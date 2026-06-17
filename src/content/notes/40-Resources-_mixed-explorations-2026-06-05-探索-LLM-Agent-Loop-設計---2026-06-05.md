---
_slug: 40-Resources-_mixed-explorations-2026-06-05-探索-LLM-Agent-Loop-設計---2026-06-05
_vault_path: 40-Resources/_mixed/explorations/2026-06-05-探索-LLM-Agent-Loop-設計---2026-06-05.md
title: 探索：LLM Agent Loop 設計 — 2026-06-05
date: 2026-06-05
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- constraint
- decay
- drift
- graph
- heartbeat
- layer
- llm
- loop
- tool
created: '2026-06-05'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent Loop 設計 — 2026-06-05

**延續自**: (無前期筆記，直接 broad search)

---

## Per-Source Insight

### 1. sketch.dev — "The unreasonable effectiveness of an LLM agent loop with tool use" (447 pts)

核心是一個 9 行的 while loop：

```python
def loop(llm):
    msg = user_input()
    while True:
        output, tool_calls = llm(msg)
        if tool_calls:
            msg = [handle_tool_call(tc) for tc in tool_calls]
        else:
            msg = user_input()
```

關鍵 insights：
- **Tool use = LLM 傳回符合 schema 的 structured output**，不是 magic
- **Persistence 是差異點**：agent 可以自己 install tools、adapt to different CLI flag 差異。如果 `grep` 選項不同，它會自己適應
- **視覺化編輯器戰勝 line editor**：sed one-liners 對 LLM 來說是災難，可視化工具才能做好編輯
- **Agent loop 會進入 bin/ 目錄**：未來會有越來越多客製化的 ad hoc LLM agent loops 在 dev 工作流程中
- Sketch 的 tool set 不只是 bash — 一 handful 的額外 tools 提升 quality 和速度

**對 Hermes 的啟發**：heartbeat 的 REST action 對比 active loop — 當沒有 session 要 warm，agent 選擇 REST 而不是盲目探索。這和 sketch 的「appropriate prompted」哲學一致：不做無意義的 iteration。

---

### 2. arxiv:2605.06445v1 — "Constraint Decay: The Fragility of LLM Agents in Backend Code Generation"

系統性研究：在嚴格的架構約束下（Clean Architecture + PostgreSQL + SQLAlchemy），LLM agent 的表現。

**主要發現**：
- **Constraint decay**：隨著 structural requirements 累積，agent 表現平均下跌 30 個百分點（assertion pass rate）
- **Framework sensitivity**：Flask（ lightweight/explicit）>> FastAPI/Django（ convention-heavy）— agent 在約定繁重的環境明顯更差
- **Root cause**：45% 的 logic failures 來自 data-layer defects（錯誤的 query composition、ORM runtime violations）
- **Functional ≠ Structural**：agent 可以產生「功能正確」但「不符合 spec」的程式碼

實驗設計：固定同一個 OpenAPI spec，layer architectural constraints（L0 無約束 → L3 全部約束），跨 8 個 frameworks、80 個 generation tasks、20 個 feature-implementation tasks。

**對 Hermes 的啟發**：
- ** drift penalty 的量化 target**：如果 coding agent 在架構約束下會 decay，那麼 heartbeat learning 在知識變遷下也會有類似的 decay。建議在 drift penalty 加入架構複雜度因子
- **Data-layer defects 是最大 failure mode**：這對應到 heartbeat_learning.py 的 triple extraction — 如果 base layer 有 noise（壞的 extraction），上層的 drift detection 會被放大

---

### 3. PocketFlow — "LLM Agents are simply Graph" (263 pts, Zachary Huang)

用 100 行框架說明 agent 的本質：

```
Nodes = stations (Prep/Exec/Post)
Edges = recipe/flow
Shared store = countertop where all nodes read/write
Decision node → branches to action nodes → loops back to decision
```

核心 pattern：
1. **Prep**：從 shared store 拿資料（就像 chef 拿食材）
2. **Exec**：LLM "thinks" — creates prompt, call LLM, parse response
3. **Post**：把結果寫回 shared store，return 下一個 node 的名稱

**所有框架都只是這個 pattern 的複雜版本**：
- OpenAI Agents: `run.py#L119` — workflow in graph
- Pydantic Agents: `_agent_graph.py#L779` — steps organized in graph
- Langchain: `agent_iterator.py#L174` — loop structure
- LangGraph: `agent.py#L56` — graph-based approach

**對 Hermes 的啟發**：
- **heartbeat_v2.py 的架構**：snapshot → scoring → select → execute → log，其實就是一個 graph pipeline。每個 step 是一個 node，heartbeat_v2.py 是 flow orchestrator
- **Shared store 的重要性**：PocketFlow 的 shared whiteboard 讓所有 nodes 能溝通。Hermes 的 state files（heartbeat_state.json）扮演類似的角色 — 跨 session 的 shared context
- **Decision node 的設計**：DecideAction node 用 LLM 決定下一步（search vs answer），對映到 heartbeat 的 scoring/select 機制

---

## Cross-Article Synthesis

三篇文章從不同角度收斂到同一個結論：**「簡單架構 + 明確約定」優於「複雜抽象」**。

| Source | Key Finding | Design Implication |
|--------|-------------|-------------------|
| sketch.dev | Agent loop 可以很簡單（9 lines），persistence 是差異點 | 不要過度架構，core loop 保持 simple |
| Constraint Decay | Structural constraints 讓 agent 退化 30 pts，data-layer 是主要失敗點 | 知道限制，不要在複雜架構上硬撐 |
| PocketFlow | 所有框架都在実装同一個簡單 graph pattern | 用簡單的方式建模，不要 reinvent complexity |

**一致性**：三篇都指向「結構化 > 無結構」。PocketFlow 說「node + edge + loop」，Constraint Decay 說「架構約束讓 agent 退化，但仍然是必要的」，sketch.dev 說「tool use 是 structured output」。複雜度不是壞事，但要有明確的結構。

**對 heartbeat_learning.py drift penalty 的具體建議**：
1. **加入架構複雜度因子**：類似 constraint decay 的 L0-L3 gradient，drift penalty 應該考慮 distillate 的「結構年齡」— 越老的 distillate 在新資訊衝擊下越容易失效
2. **Data-layer noise 放大**：如果 base extraction 有錯誤，drift detection 會被放大。需要在前端（sanitizer/validator）就過濾 noise，而不是依賴 drift penalty 補救
3. **Reference graph over time-based decay**：用概念關係 graph（distillate A mentions/contradicts distillate B）比純時間衰減更精準。新資訊和舊 distillate 有矛盾 → 觸發 staleness，不是等 time-to-live 過期

---

## Untracked Leads

- https://github.com/KhoomeiK/LlamaGym — fine-tune LLM agents with online RL (239 pts, 直接 RL 訓練 loop)
- https://github.com/anonymous-4open.science/r/constraint-decay — 可看 evaluation pipeline code，了解如何系統性衡量 agent 表現
- https://github.com/pocketflow-ai/pocketflow — 100-line agent framework， source code 乾淨可直接讀

---

## ✅ 本次探索完成
