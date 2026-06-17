---
_slug: 40-Resources-_mixed-explorations-2026-05-22-ChatIndex-Retrieval---Visualization---LLM-Guided-Tree-Naviga
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-ChatIndex-Retrieval---Visualization---LLM-Guided-Tree-Naviga.md
title: ChatIndex Retrieval & Visualization — LLM-Guided Tree Navigation
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- children
- ctree
- index
- llm
- messages
- node
- root
- tool
- tools
- tree
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# ChatIndex Retrieval & Visualization — LLM-Guided Tree Navigation

**延續自**: [[2026-05-26-chatindex-ctree-source-deep-dive]]

**時間**: 2026-05-27T01:20 CST

## visualize.py — 純文字輸出工具

三個核心函數，無外部依賴：

### `print_detailed_tree(ctree)`
```
CONVERSATION TREE - DETAILED VIEW
================================================================================
Total messages: 42 | Max children: 5
================================================================================
├── Topic: Python Async
│   ├─ Range: [0:15]
│   ├─ Messages: 8
│   ├─ Children: 2
│   └─ Summary: Discussion about asyncio.gather behavior...
├── Topic: Git Rebase
│   ├─ Range: [16:28]
│   ├─ Messages: 5
...
```

**用什麼字元**：`└── ` / `├── `（最後一個用前者）、`│   ` 延伸

### `export_tree_statistics(ctree)` → Dict
```python
{
    "total_messages": 42,
    "total_nodes": 12,
    "leaf_nodes": 8,
    "max_depth": 3,
    "avg_messages_per_leaf": 5.25,
    "topic_distribution": [
        {"topic": "Python Async", "depth": 1, "messages": 8, "range": [0, 15]},
        ...
    ]
}
```

**注意**：`"leaf_nodes"` 指的是 TopicNode（不是 MessageNode）。真正的 leaf 是 `MessageNode`，但統計上把「沒有 children 的 TopicNode」當 leaf。

### `export_coverage_report(ctree, filepath)`
生成 Markdown report，format 同 `print_detailed_tree` 但輸出到檔案。

---

## retrieval/llm_tools.py — LLM-Guided Retrieval Pattern

這是整個 ChatIndex retrieval 的核心。不同於 vector similarity，這是 **tool-use RAG**。

### 兩個 LLM Tools

```python
TOOLS = [
    {
        "name": "view_node_and_children",
        "description": "View a specific node in the ChatIndex tree and see its children. "
                      "Returns the node's topic name, summary, message range, "
                      "and a list of all direct children with their basic information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "node_path": {
                    "type": "array", "items": {"type": "integer"},
                    "description": "Path to the node as a list of child indices from root. "
                                 "Empty array [] means root node. [0] means first child of root. "
                                 "[0, 1] means second child of first child of root, etc."
                }
            }
        }
    },
    {
        "name": "get_node_messages",
        "description": "Retrieve the actual conversation messages covered by a node "
                      "using its start and end indices.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_index": {"type": "integer"},
                "end_index": {"type": "integer"}
            }
        }
    }
]
```

### Tool Execution Layer：`ChatIndexTools`

```python
class ChatIndexTools:
    def view_node_and_children(self, node_path: List[int]) -> Dict[str, Any]:
        # node_path = [] → root
        # node_path = [0, 1] → root.children[0].children[1]
        # 返回：topic_name, summary, start_index, end_index, children[]
        
    def get_node_messages(self, start_index: int, end_index: int) -> Dict[str, Any]:
        # 直接切片 ctree.conversation[start_index:end_index]
        # 返回 messages[]
```

### 多輪查詢 orchestration：`query_ctree()`

```python
def query_ctree(api_key, ctree, user_query, max_turns=50):
    # 1. 系統訊息：告知 LLM 有哪些 tools、如何 navigate node_path
    system_message = """You are an AI assistant with access to a ChatIndex tree structure...

    The tree uses a path-based navigation system where each node is accessed
    by a list of child indices from root:
    - [] = root node
    - [0] = first child of root
    - [0, 1] = second child of the first child of root
    - etc.
    
    Each TopicNode has start_index and end_index fields that define
    the range of messages it covers."""

    # 2. 多輪對話：LLM 決定何時 call tools
    for turn in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            tools=TOOLS,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return final_response  # LLM 直接回答了
        elif response.stop_reason == "tool_use":
            # 執行 tools → 把結果加回 messages → 繼續對話
            for block in response.content:
                if block.type == "tool_use":
                    result = tools_handler.process_tool_call(block.name, block.input)
                    messages.append({"role": "user", "content": [{"type": "tool_result", ...}]})
```

**查詢流程**：
1. LLM 看到 user query，先 `view_node_and_children([])` 看 root
2. 根據 root 的 children（top-level topics），LLM 選相關的
3. `view_node_and_children([0])` 進第一個 child topic
4. 重複直到找到涵蓋 user query 相關內容的 node
5. `get_node_messages(start, end)` 取出實際對話內容
6. LLM 結合取出內容生成回答

### Hermes 啟示

**Tool-use RAG vs Vector Similarity RAG**：

| | Vector RAG | ChatIndex Tool-use RAG |
|--|-----------|----------------------|
| 檢索方式 | embedding similarity | LLM 根據 tree structure 導航 |
| 理解層次 | 片段相似性 | 主題結構 + 語意 |
| 實作複雜度 | Medium（embedding + ANN） | Medium-High（tree + multi-turn LLM） |
| API call 成本 | 1 次 embedding + 1 次 LLM | N 次 tool call（N=tree depth，約 2-4 次） |
| 回傳精確度 | 模糊匹配 | 精確 range |

**對 Hermes MemR³ 的啟發**：
- 當前 MemR³ 用 BM25 + fact extraction 做 retrieval
- 可以考慮「tree navigation」作為另一層：讓 LLM 根據對話歷史的 topic structure 決定要 extract 哪些 facts
- 不需要 vector similarity——LLM 自己會 follow node_path 導航

**但有個問題**：ChatIndex 的 `query_ctree()` 需要完整的 conversation tree 已经建立好了才能查。Hermes 的 session 是增量 live 的——新訊息不斷追加，tree 一直在變。要支援 live session 查詢，需要 tree 做 snapshot 或 read-once copy。

## 未追蹤

（無）

## ✅ 本次探索完成
