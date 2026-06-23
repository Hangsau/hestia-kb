---
_slug: 40-Resources-_mixed-explorations-2026-05-25-multi-agent-when-to-build-langchain
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-multi-agent-when-to-build-langchain.md
title: '2026-05-25 Multi-Agent Systems: When to Build (LangChain)'
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-05-25 Multi-Agent Systems: When to Build (LangChain)

**來源**: [LangChain Blog: How and when to build multi-agent systems](https://blog.langchain.com/how-and-when-to-build-multi-agent-systems/) | 2026-05-25

**延續自**: [[2026-05-25-multi-agent-governance-blind-spot]]

## Per-Source Insights

### LangChain: When to Build Multi-Agent Systems

**核心命題**: 標題看似反對，但其實與 Anthropic/Cognition 的文章互補，形成統一路徑。

**兩大原則**:

1. **Context engineering is critical**
   - "Prompt engineering" → "Context engineering" 是下一層次：動態、自動化、框架層級的上下文管理
   - Multi-agent 讓每個 sub-agent 有 appropriate context **更難**（不是更容易）
   - Anthropic 的 case：原本簡單指令如 "research the semiconductor shortage" 導致 subagent 重複工作、模糊分工
   - 修復：每個 subagent 需要客製化的 task description（objective + output format + tools + task boundaries）

2. **Read-heavy systems are easier than write-heavy**
   - Read actions 更可並行；write actions 有 conflicted decision 問題
   - Anthropic 的寫作（synthesize 成報告）故意給 single main agent，not parallelized
   - **Conflicting writes → bad results** — 這是 Waxell "Unbounded delegation depth" 的另一面

**Anthropic 經驗數據**（直接引用）:
> "Multi-agent research systems excel especially for breadth-first queries that involve pursuing multiple independent directions simultaneously."
> "Multi-agent systems work mainly because they help spend enough tokens to solve the problem."
> "For economic viability, multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance."

**LangGraph 定位**: low-level orchestration framework，no hidden prompts，no enforced "cognitive architectures" — 給 developer full control 做 context engineering。

---

## Hermes 啟發

**對 Talos-Hestia 雙 agent 架構的修正**:

Waxell 指出 delegation boundary 是治理盲點。LangChain 補充：這個盲點在 **read-heavy, breadth-first** 工作負載下特別容易處理（Talos 做 research/diagnostics 是 read-heavy）。但當 Hestia 委派 Talos 去做會**寫入**的動作（修改檔案、commit、發送外部請求），conflicted write 風險就出現了。

目前 Hestia→Talos 的 task delegation 沒有區分 read/write 性質，沒有 scope boundary for writes。

**具體缺口**:
1. **Context scope 對 write tasks 更嚴格**：Talos 收到 "commit this fix" 和 Talos 自己决定 "我要 commit" 是不同的授權 context，後者缺少 scope constraint
2. **Cost ceiling 對 write tasks 影響更大**：一次錯誤的 write（刪除、覆寫）比一千次 read 代價高得多
3. **Audit trail 對 write tasks 更關鍵**：delegation handoff 的 context 需要 capture，才能在錯誤 write 後做 chain of custody

**與 Waxell 敘述的對照**:

| Gap（來自 Waxell）| LangChain 修復方向 |
|---|---|
| Context scope leakage | 每個 subagent task description 需要具體邊界（objective + output format + tools） |
| Unbounded delegation depth | Read-heavy first；write tasks 需要 single agent ownership |
| Broken audit trail | Full production tracing（LangSmith 之類的 tooling） |

---

## 跨文章 Synthesis

三篇文章（Cognition、Anthropic、LangChain）+ Waxell 構成完整的 Multi-Agent Decision Framework：

1. **不要輕易 build multi-agent**（Cognition）——因為 context engineering 很難
2. **Build 適合的 multi-agent**（Anthropic/LangChain）——read-heavy、breadth-first、high-value tasks
3. **Govern multi-agent**（Waxell）——delegation boundary enforcement、audit trail、cost cascade

對 Hermes 的意義：Talos-Hestia 是 sibling agents，不完全等同 Orchestrator-Subagent 關係，但 governance 缺口相同。當前 Hestia→Talos 委派缺乏：
- 明確的 read/write task 分類
- Write task 的 scope constraint（單一 agent ownership）
- Delegation handoff 的 context capture

---

## 未追蹤 Leads

- https://cognition.ai/blog/dont-build-multi-agents — Cognition 的「不要 Build」文章，與 LangChain 的「視角互補」聲稱對立，但實際上 Harrison 說它們 share common insights
- https://www.anthropic.com/engineering/built-multi-agent-research-system — Anthropic 官方 multi-agent research system 完整描述（含影片/圖表）
- https://smith.langchain.com — LangSmith（agent debugging + observability），與 Hermes 的 heartbeat observability 方向類似

## ✅ 本次探索完成