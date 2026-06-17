---
_slug: 40-Resources-_mixed-explorations-2026-05-22-ChatIndex-ctree-原始碼深度分析---萃取實作關鍵
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-ChatIndex-ctree-原始碼深度分析---萃取實作關鍵.md
title: ChatIndex ctree 原始碼深度分析 — 萃取實作關鍵
date: 2026-05-26
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- children
- current
- llm
- message
- name
- node
- summary
- topic
- topicnode
- tree
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# ChatIndex ctree 原始碼深度分析 — 萃取實作關鍵

**延續自**: [[2026-05-25-chatindex-tree-based-lossless-memory]]  [[2026-05-25-chatindex-code-architecture]]  [[2026-05-21-pageindex-chatindex-in-context-index]]

**時間**: 2026-05-26T00:15 CST

## 資料結構：Tree 的真實形狀

```python
@dataclass
class TopicNode(Node):
    topic_name: str          # 主題名稱（LLM 生成）
    summary: str             # 主題摘要（延遲生成，可選）
    start_index: int         # conversation 中的起始位置
    end_index: int           # conversation 中的結束位置
    children: List[Node]     # MessageNode 或 TopicNode（巢狀）

@dataclass
class MessageNode(Node):
    # 真正的 leaf：每個節點 = 一個 user+assistant exchange
    user_message, assistant_message, system_message
    message_index: int
```

**關鍵設計**：`current_node` 指標永遠指向「最近話題的 TopicNode」。新訊息總是附加到 `current_node` 的 children。新話題誕生時，指標移動到新 TopicNode。

**時序約束**：新 TopicNode 的 parent 只能是 `current_node` 或其祖先（`Anc*(v_k)`）——這就是 tree 強制「話題只能分支或回升，不能跳到無關分支」的機制。

## 三個 LLM Call 的 actual prompts

### 1. Topic name 生成（`_llm_generate_topic_from_message`）

```python
prompt = f"""Given the following conversation exchange, generate a concise topic name (2-5 words) that captures its main subject.{context}
{system_context}
User: {user_content}
Assistant: {assistant_content}
Respond with ONLY the topic name, nothing else."""
```
- `temperature=0.3`，`max_tokens=50`
- 極簡 prompt，沒有 few-shot，側重 2-5 word brevity

### 2. Message 分類（`_llm_classify_message_exchange`）

```python
prompt = f"""Analyze if this new conversation exchange belongs to the current topic or should start a new topic.
**Current Topic:** {current_node.topic_name}
**Topic Summary:** {current_node.summary}
**Recent exchanges in current topic:** {recent_content}
**New exchange:** {system_context}User: {user_content[:400]}  Assistant: {assistant_content[:400]}
**Parent candidates (for parent selection if creating new topic):** {ancestor_list}
Think step by step:
1. Does this exchange continue discussing the current topic?
2. If not, what new topic does it introduce?
3. Which ancestor topic should be the parent of this new topic?
Respond ONLY with valid JSON:
{{"reasoning": "...", "belongs_to_current": true/false, "new_topic_name": "...", "new_topic_parent_index": <int>}}"""
```
- `temperature=0.1`（保守），`max_tokens=200`
- 上下文豐富：current topic name + summary + recent 3 exchanges
- 輸出嚴格 JSON，用 `extract_json()` 解析

### 3. Node 展開（`_expand_node` / subtopic split）

```python
prompt = f"""Analyze the following conversation segment about "{node.topic_name}" and identify distinct subtopics.
Group consecutive messages into 2 coherent subtopics.
Messages (indices 0-{len(messages)-1}): {messages_text}
Respond in JSON format with an array of subtopics:
{{"subtopics": [{{"topic_name": "...", "summary": "...", "start_offset": <int>, "end_offset": <int>}}]}}"""
```
- 當 TopicNode 的 MessageNode children 超過 `max_children` 時觸發
- 把 MessageNode 子樹重新組織成 TopicNode 子樹

## max_children Cap 的實作位置

**`ctree.py:CTree._check_and_reorganize_nodes()`**：
- 遍歷所有節點，收集需要重組的節點
- 兩種觸發條件：
  - `message_children > max_children` → `_expand_node()`（垂直拆分：MessageNode → TopicNode 子樹）
  - `topic_children > max_children` → `_split_node()`（水平拆分：TopicNode → 兩個 sibling）
- **Root 的特殊處理**：`root` 超過 `max_children` topic children 時，展開成 intermediate topic layer，而不是簡單拆分

```python
def _expand_node(self, node: TopicNode) -> None:
    # 呼叫 _llm_split_subtopics() → 把 message children 重新分組
    # 創建 TopicNode children，把 MessageNode children 遷移進去
    pass

def _split_node(self, node: TopicNode) -> None:
    # 呼叫 _llm_find_split_point() → LLM 找最適 split index
    # 把原本的 TopicNode 內容分成兩個 sibling TopicNode
    pass
```

## Summary 生成（目前 Disabled）

```python
def _generate_summaries_for_frozen_nodes(self, node=None) -> None:
    # 遍歷 frozen nodes（不是 current_node 且不是 current_node 祖先的 TopicNode）
    # 對每個 summary 為空的 frozen node，呼叫 _llm_summarize()
    pass

def _llm_summarize(self, messages, topic_name) -> str:
    # 取前 5 個 messages，用 1-2 句話摘要
    pass
```

**注意**：`add()` 方法最後一行被註解掉了：
```python
# self._generate_summaries_for_frozen_nodes()
```
這表示 summary 生成是可選的——**沒有 summary 的 TopicNode 一樣可以正常運作**，只是 tree 可讀性下降。分類時 `current_node.summary` 是空字串時不會影響決策。

## PageIndex vs ChatIndex 的真正差異

| | PageIndex | ChatIndex |
|--|-----------|-----------|
| 輸入 | 靜態 PDF/文件 | 動態對話流 |
| Tree 生成時機 | 一次性（文件上傳時） | 增量（每個 exchange 添加時） |
| Tree 結構 | 純 TopicNode 巢狀 | TopicNode + MessageNode 混合 |
| Retrieval | 靜態 tree walk | 動態導航（current_node 指標） |
| Context | 單一文件 | 多輪對話歷史 |

**共同核心**：都不依賴 vector similarity。分類/摘要全靠 LLM reasoning。

## Hermes 可遷移的實作模式

### 1. 可直接借用的設計

**TopicNode + MessageNode 結構**：完全適用於 Hermes session log 的 JSONL 格式。每個 exchange（user+assistant 的 tool calls） = 一個 MessageNode。

**current_node 指標**：LRU 風格的「最近話題」追蹤。新訊息預設附加到 current_node，LLM 分類決策是否需要移動。

**ancestor constraint**：`Anc*(v_k)` 集合限制新 TopicNode 的 parent 選擇，保證 tree 不會長出奇怪的分支。

**Frozen node 概念**：已經「定型」的 TopicNode（不再是 current_node 也不是其祖先）可以安全地生成 summary、做 compaction。這與 MemR³ 的 fact extraction trigger 完全吻合——**compaction 應該只在 frozen nodes 上觸發**。

### 2. 需要替換的部分

**LLM calls → DeepSeek**：所有 `ChatGPT_API()` 替換成 DeepSeek API call。`model="gpt-4o-mini"` → `"deepseek-chat"`。實際上，只需要一個 API key 替換，dataclass 結構、流程邏輯、prompt template 完全不變。

**Prompt trimming**：400 字 user_content + 400 字 assistant_content 在 Hermes 場景（tool call + result pairs）需要調整。建議：
- `user_content` = user message 原文（通常很短）
- `assistant_content` = tool_name 彙總（如 `[tool: read_file x3, terminal, patch]`），不包含 tool output

### 3. 純 Hermes 的優化

**不生成 topic name**：Hermes session 的 topic 可以用結構化 metadata（如 first user message 的前 50 字），省掉一個 LLM call。只有當 `first_50_chars` 重複率高（不同 session 的 generic greetings）時才呼叫 LLM。

**不生成 summary**：目前程式碼預設關閉 summary generation（`add()` 最後一行被註解），說明這個功能不是 tree 正常運作的必要條件。**延遲 summary generation 到查詢時再生成**（按需），比維護時生成更節省成本。

**`max_children=10` 的啟示**：ChatIndex 預設 5，實際上 10 也合理。這個 cap 控制的是 tree 的「扇出」，不是深度。Hermes 可以設 8-12，視平均每個 session 的 exchange 數量而定。

## 實作複雜度評估（更新）

| Component | 複雜度 | 備註 |
|-----------|--------|------|
| TopicNode/MessageNode dataclass | Trivial | 直接借用的 dataclass |
| current_node 指標追蹤 | Trivial | 幾行程式碼 |
| LLM 分類（DeepSeek 版） | Low-Medium | 替換 API endpoint 即可 |
| _check_and_reorganize_nodes | Medium | 三種 split 策略 |
| Summary on-demand generation | Low | 查詢時觸發，不需要主動維護 |
| MemR³ 整合（compaction trigger） | High | 等待 frozen node → extract facts |

**最簡單的著手點**：從 session log JSONL 的 message pair 結構開始，直接用 `ctree.py` 的 dataclass + `add()` API，把 OpenAI 替換成 DeepSeek。Demo 跑起來之後再逐步替換 prompt template。

**下一步**：找一個真實的 Hermes session log JSONL（如 `~/.hermes/sessions/` 下的某個 session），餵進 ctree，跑 `tree.print_tree()`，觀察 topic segmentation 結果是否合理。

## 未追蹤

- https://github.com/VectifyAI/ChatIndex/blob/main/ctree/visualize.py — 可視化模組，看 tree 實際長什麼樣
- https://github.com/VectifyAI/ChatIndex/blob/main/retrieval/ — retrieval 相關程式碼（tree walk / query）

## ✅ 本次探索完成
