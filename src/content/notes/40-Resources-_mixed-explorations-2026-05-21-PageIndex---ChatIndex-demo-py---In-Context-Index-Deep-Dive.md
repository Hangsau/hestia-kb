---
_slug: 40-Resources-_mixed-explorations-2026-05-21-PageIndex---ChatIndex-demo-py---In-Context-Index-Deep-Dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-21-PageIndex---ChatIndex-demo-py---In-Context-Index-Deep-Dive.md
title: PageIndex & ChatIndex demo.py — In-Context Index Deep Dive
date: 2026-05-21
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- based
- chatindex
- index
- llm
- node
- pageindex
- rag
- section
- tree
- vector
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# PageIndex & ChatIndex demo.py — In-Context Index Deep Dive

**延續自**: [[2026-05-25-chatindex-tree-based-lossless-memory]]  [[2026-05-25-chatindex-code-architecture]]

**時間**: 2026-05-21 20:33 CST
**來源**: pageindex.ai/blog/pageindex-intro + VectifyAI/ChatIndex demo.py (raw GitHub)

---

## PageIndex: Reasoning-based RAG 核心概念

### 對比 Vector-based RAG 的五大限制

| | Vector RAG | PageIndex Reasoning RAG |
|--|------------|-------------------------|
| 查詢↔知識 | 只靠語意相似度匹配 | LLM 推論「這個 section 有沒有答案」|
| 相似度≠相關性 | 抓到語意相近但不相關的段落 | 根據上下文決定真正相關的內容 |
| 切 chunk | 固定長度切斷語意完整性 | 動態取完整 section / page |
| 對話歷史 | 每個 query 獨立 | 多輪 reasoning 考慮 prior context |
| 跨文獻引用 | 抓不到 "see Appendix G" | 透過 ToC 樹導航追蹤引用 |

### 核心創新：In-Context Index

傳統 RAG 把 index（向量）存在外部 vector DB。PageIndex 把 **ToC 樹結構直接放進 LLM context window** 裡，讓 LLM 在推理時動態導航。架構：

```json
Node {
  "node_id": "0006",
  "title": "Financial Stability",
  "start_index": 21,
  "end_index": 22,
  "summary": "...",
  "sub_nodes": [Node, Node]
}
```

每個 node_id 對應 raw content（text、images、tables）。LLM 看到整棵樹後，自己決定下一步去哪裡——不是靠 cosine similarity，是靠推理。

### 推理迴圈（5 步）

```
1. 讀 ToC → 理解文件結構
2. 選 section → 根據 query intent 推論最可能相關的
3. 取內容 → 該 section 的 raw data
4. 判斷是否足夠 → 不夠就回到 step 1 選另一個 section
5. 回答 → 足夠後產生答案
```

實驗案例：Fed 年報查「deferred assets 總值」。主 section 只報增量，沒報總值；77 頁提到「Appendix G 有完整統計表」。Vector RAG 抓不到（因為語意不相近），Reasoning RAG 跟著引用走到 Appendix G，找到正確數字。

---

## ChatIndex demo.py — 端到端流程

```python
from ctree import CTree

# 載入對話資料（JSON）
with open('data/ChatExample.json') as f:
    conversation = json.load(f)

# 建樹
tree = CTree(max_children=10, auto_save_path='save/conversation_tree.json')
messages = []
for msg in conversation:
    if msg["role"] in ("system", "user", "assistant"):
        messages.append({"role": msg["role"], "content": msg["content"]})
tree.add(messages)
tree.print_tree()
```

重點觀察：
- `CTree` class 的 `add(messages)` 內建 topic shift detection（自動把對話分成多個 subtree）
- `max_children=10` 控制樹的寬度（每次 query 的 cost 上限）
- `auto_save_path` 持久化樹結構到磁碟，下次不用重新建
- 目前需要 OpenAI API key 才能跑 tree building（LLM 呼叫用於生成 topic summary）

---

## Hermes 啟發

### 1. In-Context Index 用於 Phase-based Session Memory

前期筆記提到把 session phase 當骨架，這裡找到具體實作：

```
Session tree:
  root
  ├── Planning phase (internal node: LLM summary)
  │   ├── Subtopic A (internal node)
  │   └── Subtopic B (internal node)
  ├── Execution phase (internal node)
  └── Review phase (internal node)
```

Query 時：先問「Planning phase 有沒有相關內容？」→ YES（快速路徑）→ 直接回 summary；NO → 進 children；PARTIAL → summary + fetch relevant leaf messages。

這和 PageIndex 的 ToC 導航邏輯一模一樣，只是場景從 long document 變成 session history。

### 2. 與 MemR³ 的 Hybrid 架構

```
Short-term: CTree (lossless, adaptive granularity)
     ↓ periodic compaction (每 N queries 或時間觸發)
Long-term: MemR³ (ranked facts, evidence gap convergence)
```

CTree 處理即時 session，MemR³ 處理跨 session 知識蒸餾。兩者的介面是「compaction trigger」——當 tree 的 node 數量或時間累積到閾值，觸發蒸餾流程寫入 MemR³。

### 3. Claude Code 也放棄了 Vector RAG

PageIndex 文章提到 Claude Code 已經不做 vector-based code retrieval。理由同樣：semantic similarity 抓不到「這個 function 在第 3 版被重構了」這類時序相關性。Reasoning-based 導航才能處理。

---

## 未追蹤

- https://github.com/VectifyAI/PageIndex — PageIndex 開源 repo（含 MCP server），可與 ChatIndex 一起研究
- https://pageindex.ai — 官方產品頁，確認是否有 free tier 或 API pricing

---

## ✅ 本次探索完成
