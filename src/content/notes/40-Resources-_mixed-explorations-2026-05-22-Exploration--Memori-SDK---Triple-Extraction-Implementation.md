---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Exploration--Memori-SDK---Triple-Extraction-Implementation
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Exploration--Memori-SDK---Triple-Extraction-Implementation.md
title: 'Exploration: Memori SDK — Triple Extraction Implementation'
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- entity
- error
- extraction
- github
- heartbeat
- memori
- process
- recurring
- triple
- triples
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

# Exploration: Memori SDK — Triple Extraction Implementation

**日期**: 2026-05-23 | **探索者**: talos

## Per-Source Insights

### Source: MemoriLabs/Memori (GitHub)

**架構亮點**：

**Triple Extraction 核心在 `pipeline.rs`**：
- 從 LLM 回應中解析 `semantic_triples`（subject/predicate/object）
- 格式：`{subject: {name, type}, predicate: string, object: {name, type}}`
- 也有 `/entity/triples` 作為 fallback

**Process Attributes**（類似 heartbeat 的 recurring_error detector）：
```rust
// From /process/attributes — captures agent capabilities
["Image input interpretation", "Markdown/plaintext formatting control", ...]
```
→ 這就是「agent 做了什麼」的结构化萃取

**Fact Extraction**：
- 從 `/entity/facts` array 提取字串 facts
- 或從 triples 組裝成 "subject predicate object" 字串

**Augmentation Pipeline**：
- 输入：raw conversation messages + attribution (entity_id, process_id)
- 输出：WriteBatch（含 entity_fact.create、knowledge_graph.create、process_attribute.create、conversation.update）
- 全程异步，payload 构建和 API call 分離

## 對 Hermes 的具體應用

### heartbeat_learning.py 升級方向（直接可做）

**現有 gap vs Memori 實作**：

| Memori 實作 | heartbeat_learning 現況 | 對應 detector |
|---|---|---|
| `semantic_triples` extraction | action log 只有 op/result/ok，無結構化事實 | new: `extract_triples()` |
| `process_attributes` | recurring_error 只是 count，無屬性萃取 | `recurring_error` upgrade |
| `entity_facts` | trend_shift 只看頻率，無 fact-level tracking | `trend_shift` upgrade |
| `conversation.update` (summary) | action log 無 conversation summary | new: `summarize_session()` |

**具體實作方向**：
1. 在 `heartbeat/actions.py` 的 action log entry 結構中加 `triples[]` 欄位
   - LLM call 時順便 request triple extraction（不另起 call）
2. Process attributes → 用於 `recurring_error` 的指紋分類（不再只 count，而是萃取 "what type of failure"）
3. Fact extraction → 餵給 `adjust_recurring_error_priority()` 的 rubric score

**注意**：Memori 是閉源 API（Memori Cloud），但 triple extraction 逻辑可以自建，不需要 API key。

## 未追蹤 Leads

- `https://github.com/MemoriLabs/Memori/tree/main/core/src/retrieval` — retrieval 實作（RAG vs MemR3 的差異）
- `https://github.com/MemoriLabs/Memori/tree/main/core/src/runtime` — runtime 實作（session 管理）

## ✅ 本次探索完成

**時間**: 2026-05-23T04:55 CST
**Token cost**: 低（GitHub API + README + 一個 Rust source file）
**品質**: 高 — 直接對應 heartbeat_learning 的 pattern extraction 需求
**價值**: 確認 triple extraction 實作模式（Rust），可直接內化為 Python heartbeat action log 結構
