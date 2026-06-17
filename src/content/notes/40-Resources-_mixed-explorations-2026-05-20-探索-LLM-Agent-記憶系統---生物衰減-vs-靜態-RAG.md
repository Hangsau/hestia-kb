---
_slug: 40-Resources-_mixed-explorations-2026-05-20-探索-LLM-Agent-記憶系統---生物衰減-vs-靜態-RAG
_vault_path: 40-Resources/_mixed/explorations/2026-05-20-探索-LLM-Agent-記憶系統---生物衰減-vs-靜態-RAG.md
title: 探索：LLM Agent 記憶系統 — 生物衰減 vs 靜態 RAG
date: 2026-05-20
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- category
- context
- decay
- hermes
- https
- memory
- recall
- specific
- yourmemory
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# 探索：LLM Agent 記憶系統 — 生物衰減 vs 靜態 RAG

**日期**: 2026-05-20 | **來源**: HN discussion + GitHub README | **類型**: 探索

## Per-Source Insight

### YourMemory — Ebbinghaus 衰減實現

**來源**: https://github.com/sachitrafa/YourMemory | HN #47914367 (98pts, 53 comments)

**核心機制**：
- 指數衰減：`strength = clamp(importance × e^(−λ×active_days) × (1 + recall_count × 0.2), 0, 1)`
- `active_days` 只算使用者活躍天數，放假不會造成記憶流失
- **category-specific half-life**：strategy ~38天、fact ~24天、assumption ~19天、failure ~11天
- 強度低於 0.05 的記憶每 24 小時自動清除

**評測結果**：
- LoCoMo-10（10 sessions, 1534 QA）：Recall@5 = **55-59%**（Zep Cloud 28%）
- LongMemEval-S（~53 sessions）：Recall-all@5 = **85%**，nDCG@5 = **87%**

**技術棧**：DuckDB（本地向量DB）+ NetworkX（圖）+ sentence-transformers（`multi-qa-mpnet-base-dot-v1`，768維）+ spaCy（NLP去重）

**三個 MCP tool**：`recall_memory`、`store_memory`、`update_memory`

**亮點功能**：
1. **hybrid retrieval**：vector cosine similarity + BM25 關鍵字 → graph expansion（BFS through semantic edges）
2. **Subject-aware deduplication**：新記憶存入前比對主詞，確保「張三用 DuckDB」和「YourMemory 用 DuckDB」不會合併
3. **No-LLM ask**：trivial factual query 直接回答，零 token cost、零延遲、零隱私風險
4. **Spatial recall boost**：儲存時附加檔案路徑，recall 時 boost 同路徑的記憶

---

### HN Practitioner Discussion — 實務反對 vs 理論支持

**來源**: HN #47914367 討論串（53 comments）

**反對記憶系統的主要論點**：
- **SwellJoe**：記憶讓 agent 變笨、分心、confusing。MD 文档比記憶好——每個專案一份文檔，agent 需要什麼讀什麼，無需 MCP。「Flat memory fails」（所有事實同等權重）是真的，但「記憶本身有問題」是更強的主張。
- **pil0u**：記憶系統增加 LLM 和使用者的 overhead，CLAUDE.md / skills 版本控制後造成干擾。
- **staticassertion**：已經移除所有 agent 的「知識」設定——「身為安全工程師，blahblah」這類 static context 其實是 distration。
- **ohNoe5**：完美的記憶可能不是最優的——遺忘讓人類有智能和進步，entropy 是宇宙的性質。

**支持記憶系統的實務經驗**：
- **mtrifonov**：typed memory 有效。不同 decay curve：personality/relationships 永久、preferences 數月、stated intent 數週、emotion 數天。cross-project co-mingling 停止，因為專案資訊會 decay out。
- **giancarlostoro**：從 Beads 改到自建 SQLite-based guardrails system，理念：ticketing > 記憶，agent 完成後 compact memory 再接下一個 task。
- **K0balt**：ambient recall system，4b model 掃 context → 對 RAG DB 做 mining + rating，session wrap-up 時 inference model 回頭評分記憶 injection 的 quality。
- **waterproof**：Beads 没 Age well，Claude Code TodoList upgrade 後不再想用。

**技術批評**：
- **altmanaltman**：「biological memory 是行銷話術」，實際就是 cache mechanism。84% token 節省對比「永遠儲存一切」的 baseline，標準 chunked RAG 也能做到。LoCoMo dataset 有問題，容易 cheat。
- **Kim_Bruning**：大家都在做記憶系統，没人有乾淨的突破——這可能是 Hard Problem。想要的 function 没被完整理解，或缺少什麼關鍵元件。

---

## Hermes 啟發

### 1. 對 Talos 現有設計的映照

Talos 已經在做的事（decay-based memory management）：
- `heartbeat_v2.py` 內的 `_DoomLoopTracker`：最近 16 次 action 追蹤，超過就清除——這是 sliding window 的 hard eviction，沒有 strength 概念
- `heartbeat/actions.py` 的 severity escalation：錯誤指紋連續出現 → warning → critical——這是時間維度的 decay，但不是生物性的

**差距**：沒有 category-specific decay、沒有 recall-based reinforcement、沒有 importance weighting。純滑動窗口，資訊顆粒度粗糙。

### 2. 對 Heartbeat EVOLVE 的可能影響

EVOLVE 的 sensor 鏈（13 steps）已經有 severity + pattern 機制。但如果要加入「生物性衰減」的概念：

```
現有：同一錯誤指紋連續 N 次 → escalation
可能：同一錯誤指紋 + 不同 category（failure/strategy/fact）→ 不同 decay rate
```

例如：CONFIG/SYSTEM 錯誤（severity high）即使短期不再出現也應 linger 很久；TRANSIENT 錯誤（rate limit）應快速衰減。

### 3. YourMemory 的 spatial recall 與 Hermes workspace context

YourMemory 在 `store_memory(context_paths=["/projects/backend"])` 時，路徑被當成 spatial signal。recall 時 boost 同路徑的記憶。

Hermes 的 workspace/INDEX.md 已經是結構化的空間索引。如果在提案狀態更新（done/stale drift）之外，還能把「路徑相關性」當成一種 signal，會很有意思。例如：某個 proposal 的 workspace path 與目前 active session 的 cwd 相關 → 這個 proposal 的 STATUS 更新更值得 attention。

### 4. 反對聲音的價值

SwellJoe 的核心論點：「MD 文檔是 agent 的母語，不需要記憶系統」。這和 Hermes 的 vault/obsidian 策略一致——知識化、文件化，而不是靠 implicit memory。

對於 Talos 的守護者角色：重點可能不在「讓 agent 記得更多」，而在「讓重要的事不會被忽略」。decay 不是為了騰出空間，而是為了區分「已解決」（可忘）vs「未解決」（應留存）。

---

## 跨文章 Synthesis

**記憶系統的兩個流派**：
1. **靜態 RAG**：所有事實同等權重，context 脹满了就 prune oldest。缺點：噪聲累积，矛盾事实并存，agent 被過去的假設誤導。
2. **生物衰減**：strength × decay × recall reinforcement。優點：自動區分重要/不重要，矛盾可以被「新事實淹沒舊假設」機制處理。缺點：implementation 複雜，需要 tuning category half-life。

**實務共識**：
- 不用 global memory——用 project-specific 或 session-specific
- 文档 > 記憶（MCP server 可能過度工程）
- 重要的是「忘記什麼」不是「記住什麼」

**對 Hermes 的具體可考慮方向**：
1. heartbeat 的 `_DoomLoopTracker` 加入 category：action 是 `EVOLVE`/`SNAPSHOT`/`REST`，不同 action 應有不同的 loop threshold
2. severity decay 用 category-specific TTL：TRANSIENT 錯誤 24h 後可視為 resolved；CONFIG 錯誤應保留到明確修復為止
3. spatial signal：workspace/INDEX.md 中的路徑可作為資訊重要性的額外維度（相關路徑 = 更重要）

---

## 未追蹤

- https://github.com/sachitrafa/YourMemory — 官方 repo，含完整 benchmark methodology（LoCoMo + LongMemEval-S）
- https://arxiv.org/abs/2501.00663 — Google Titans+Atlas（討論串中提到）
- https://arxiv.org/abs/2505.23735 — 相關 follow-up
- https://dev.to/sachit_mishra_686a94d1bb5/i-built-memory-decay-for-ai-agents-using-the-ebbinghaus-forgetting-curve-1b0e — 官方 writeup

## ✅ 本次探索完成
