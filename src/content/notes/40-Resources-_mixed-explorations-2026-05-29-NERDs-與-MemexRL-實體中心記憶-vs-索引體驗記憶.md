---
_slug: 40-Resources-_mixed-explorations-2026-05-29-NERDs-與-MemexRL-實體中心記憶-vs-索引體驗記憶
_vault_path: 40-Resources/_mixed/explorations/2026-05-29-NERDs-與-MemexRL-實體中心記憶-vs-索引體驗記憶.md
title: 2026-05-29 NERDs + Memex(RL) — 實體中心記憶 vs 索引體驗記憶
created: '2026-05-29'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-05-29 NERDs + Memex(RL) — 實體中心記憶 vs 索引體驗記憶

**延續自**: なし（本次新探索選題）

## NERDs — Entity-Centered Memory for LLM Agents

**Source**: TechRxiv (13 pts HN), Show HN
**Link**: https://nerdviewer.com/ | https://www.techrxiv.org/users/1021468/articles/1381483

### 核心設計
NERDs (Networked Entity Representation Documents) — Wikipedia 風格的 entity 頁面，由 LLM agent 自己对大型語料庫 chunk-by-chunk 閱讀後建構。

- **動機**：長程任務中，context window 塞滿導致注意力退化
- **方法**：不是在查詢時 reprocess 全文，而是在 preprocessing 階段建好 entity 文件，下游 agent 搜索並 reasoning over 這些 entity docs
- **為何有結構**：大腦、人類認知知識庫、transformer 內部都围绕實體和關係組織復雜資訊

### 實驗結果
NovelQA (86 部小說，平均 200K+ tokens):
- **Entity tracking 問題**（角色、關係、劇情、場景）：NERDs 效能與 full-context 持平，**token 節省 ~90%**，且 token 用量不隨文檔長度增加
- **計數任務和定位特定段落**（非 entity-centered）：表現較差

亮點：https://nerdviewer.com/ 可以實際 browse 86 部小說生成的 entity 文件，相當於 fan-wiki 的產品展示。

### Insight
Entity tracking 的任務剛好是結結構化知識適用的場景——明確的 entity + 關係 + 追蹤。但純計數或定位就退化。這呼應了 YantrikDB/Mem0/agentmemory 的收斂：「結構化 > 純嵌入」有边界，不是銀彈。

---

## Memex(RL) — Indexed Experience Memory (arXiv:2603.04257)

**Source**: arXiv (Submitted 2026-03-04)
**Link**: https://arxiv.org/abs/2603.04257

### 核心設計
Memex 的核心洞察：**現有方案（truncation/summaries）是有損的**，壓縮或丟棄的是證據本身。

Memex 架構：
1. **壓縮 context 但不丟棄證據** — 維護一個緊湊的 working context（concise structured summaries + stable indices）
2. **Full-fidelity 交互存儲在外部 experience database**，under those indices
3. **Dereference index on demand** — agent 決定什麼時候恢復精確的 past evidence

### MemexRL — 強化學習優化讀寫

關鍵創新：用 RL framework 學習四件事：
- **What to summarize**（摘要什麼）
- **What to archive**（歸檔什麼）
- **How to index it**（如何索引）
- **When to retrieve it**（何時檢索）

Reward shaping 基於 context budget + indexed memory usage，目標是「bounded dereferencing」。理論分析證明：隨著 history 增長，decision quality 有界，effective in-context computation 有界。

### 實驗結論
Challenging long-horizon tasks: Memex agent trained with MemexRL 提升 task success，同時使用顯著更小的 working context。

### Insight
這和 NERDs 出發點相同但解法不同：
- NERDs: preprocessing entity pages → query over entity docs（靜態預生成）
- Memex: RL-learned index + on-demand dereference（動態決策）

Memex 的 bounded dereferencing 特性尤其有意義——它回答了「什麼時候應該 retrieve 而不只是 summarize」的問題，這是其他架構（包括 heartbeat_learning.py 的 distillate）缺少的決策層。

---

## 跨文章 Synthesis

### 共鳴點
1. **有損 vs無損压缩**：NERDs 和 Memex 都批評現有方案的 truncation/summaries 是有損的。方向一致：保留結構化資訊而非只留摘要。
2. **Entity/Index 作為Anchor**：NERDs 用 entity 作為 anchor；Memex 用 index。實體化和索引化是同一底層思路的兩種表達。
3. **Token efficiency**: NERDs 90% 節省，Memex "significantly smaller working context"——兩個系統都强调 context 效率，呼應 agentmemory 的 92% token reduction 發現。

### 差異點
| | NERDs | Memex |
|---|---|---|
| 生成時機 | Preprocessing（靜態） | On-demand + RL（動態） |
| 壓縮單元 | Entity document | Index → structured summary |
| Retrieval | 搜尋 entity docs | Dereference index |
| 決策主體 | 預建，無 agent 决策 | RL-learned when to retrieve |

### Hermes 啟發

**直接回答 WS-035 drift penalty 需求**：
- MemexRL 的 reward shaping 是顯式的「什麼值得記憶/什麼不值得」的信號學習
- Heartbeat learning 的 distillate 也需要類似的機制區分「真正新的insight」vs「已穩定的知識」
- 建議：為 `heartbeat_learning.py` 的 distillate phase 加入簡單的 confidence_valid_until + event-driven invalidation（參考 mem0 staleness vs decay 區分）

**NERDs 的 entity 追蹤適用場景**：
- 小說、文件、程式碼這類天然有實體（角色、函式、類別）的長文本
- 不適用於純線性敘述或計數任務
- 故宮的雞專案（egg-chess-world）可能適用——從西遊記角色互動網絡建構 world bible

**bounded dereferencing 的實現啟發**：
- 當前 heartbeat_learning.py 的 distillate 是被動的（有新論文就跑）
- Memex 的框架建议加一個主動決策：given current context budget, should I distill now or wait?

---

## ✅ 本次探索完成

## 未追蹤 Leads
- https://github.com/nevenkordic/localmind — Local LLM agent with persistent memory and learnable skills (Rust?)
- https://nerdviewer.com/ — NERDs 實際展示，站點本身可瀏覽但技術報告 fetch 失敗
- https://deepsense.ai/blog/task-planning-execution-visibility-and-persistent-memory-for-ai-agents-ragbits-1-6-release/ — ragbits 1.6 structured planning + memory
- https://arxiv.org/html/2603.04257v1 — Memex HTML 版本（有章節導航，適合深度閱讀）
