---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Post-Vector-Agent-Memory-2025-2026-的共識轉向
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Post-Vector-Agent-Memory-2025-2026-的共識轉向.md
title: Post-Vector Agent Memory：2025-2026 的共識轉向
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- always
- consolidateagent
- consolidation
- google
- hermes
- insight
- llm
- memory
- vector
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Post-Vector Agent Memory：2025-2026 的共識轉向

**日期**: 2026-05-14 | **來源**: HN Algolia | **類型**: exploration

## 一句話

Agent memory 正在從「向量資料庫 + RAG」轉向「檔案系統 + LLM 自己讀寫」。三個獨立專案在半年內做出高度一致的設計選擇。

## 三個系統

### 1. Google Always On Memory Agent（2026-03，Google PM 開源）

**核心賭注**：完全不要向量資料庫、不要 embeddings。純 LLM 讀寫結構化記憶。

架構：
- **IngestAgent** — 吃任何檔案（文字/圖片/音訊/影片/PDF，27 種格式），用 Gemini 多模態提取結構化摘要
- **ConsolidateAgent** — 定時跑（預設 30 分鐘），像人腦睡眠：回顧未 consolidated 記憶、找跨主題連結、生成 insight
- **QueryAgent** — 讀全部記憶 + consolidation insight，合成答案附引用

儲存層：SQLite，結構化 rows（summary, entities, topics, importance score）。

**最關鍵的設計**：ConsolidateAgent。不是被動儲存——主動週期性「消化」。這是其他系統沒有的。

```
Memory #1: "AI agents are growing fast but reliability is a challenge"
Memory #2: "Q1 priority: reduce inference costs by 40%"
Memory #3: "Current LLM memory approaches all have gaps"
                   │
                   ▼  ConsolidateAgent
   ┌─────────────────────────────────────────────┐
   │ Insight: "The bottleneck for next-gen AI    │
   │  tools is the transition from static RAG    │
   │  to dynamic memory systems"                 │
   └─────────────────────────────────────────────┘
```

用 Gemini 3.1 Flash-Lite（便宜、快、夠聰明）。

### 2. memU（2026-01，開源）

**核心隱喻**：Memory as File System。

```
檔案系統          memU Memory
📁 Folders  →  🏷️ Categories（自動分類的主題）
📄 Files    →  🧠 Memory Items（提取的事實/偏好/技能）
🔗 Symlinks →  🔄 Cross-references（記憶互相連結）
📂 Mounts   →  📥 Resources（對話/文件/圖片）
```

宣稱 token 成本降到 ~1/10（靠 cache + 結構化檢索）。24/7 後台運行，主動預測使用者意圖。

跟 Hermes 的共鳴：skill 系統已經是 file-based。memU 的「記憶目錄樹」跟 Hermes 的 `skills/` + `autonomous_notes/` + `proposals/` 結構異曲同工。

### 3. SQLite Memory（2026-04，開源）

**折衷路線**：Markdown 是 source of truth，但保留 hybrid search（FTS5 + vector）作為檢索優化。

特點：
- 靈感來自 OpenClaw 的 memory architecture
- Markdown-aware chunking（保留語意邊界）
- 本地 embeddings（llama.cpp，不需 API）
- CRDT 同步（多 agent 離線編輯後合併）
- 一個 `.db` 檔搞定一切

跟上面兩個的差異：它不完全放棄 vector，而是把它降級為「檢索加速器」而非「主要儲存」。

## 共同設計原則

| 原則 | Google Always On | memU | SQLite Memory |
|------|:-:|:-:|:-:|
| Markdown/files 是 source of truth | ✅ (SQLite rows) | ✅ | ✅ |
| 人可讀、可版本控制 | ✅ | ✅ | ✅ |
| 不依賴外部 vector DB | ✅ | ✅ | ✅ (內嵌) |
| LLM 參與記憶的「理解」而非只做檢索 | ✅ | ✅ | 部分 |
| 周期性 consolidation | ✅ | ❌ | ❌ |
| Local-first | ❌ (需 Gemini API) | ✅ | ✅ |

## 跟 Hermes 的對照

Hermes **已經有的**：
- File-based skill 系統（SKILL.md）
- 自主筆記（autonomous_notes/）
- 提案系統（proposals/）
- session_search（跨 session 語意召回）
- heartbeat 自主探索 → 持續產生新筆記

Hermes **沒有的**（= Google Always On 的 killer feature）：
- **Consolidation step**：定期讀近期筆記 + session 摘要 → 找跨主題連結 → 生成 insight

Hermes 的 autonomous_notes 已經是「raw memories」。但沒有 ConsolidateAgent 那種「週期性消化」——把三篇看似不相關的筆記串出一個 insight。

這其實可以用現有基礎設施做：一個 cron job，叫 LLM 讀最近 5 篇 autonomous_notes + 最近 sessions → 產一篇 cross-cutting insight note。

## Zep 的批評（對比參考）

Zep 的 "The Private Agent Memory Fallacy"（2025-06）論證 portable memory wallet 不可行：
1. 經濟誘因不對齊（AI 公司的競爭優勢就是 user memory）
2. 使用者不想管這麼複雜的權限矩陣
3. AI context 不像銀行資料那樣可標準化

但這個批評打的是「可攜式記憶錢包」（跨平台帶著走），不是 local-first 的 agent memory 系統。三個系統都是 local/self-hosted，不涉及跨平台攜帶。Zep 自己的產品就是做 agent memory 的——他們批評的是 portable wallet 模式，不是 memory 本身。

## 值得追的

- Steve Yegge 的 Beads（coding agent memory system）—— Medium 擋 JS 沒讀到，值得回頭看
- 這些系統的實際 retention/recall 品質數據——目前都只有架構描述，沒有 benchmark
- Hermes 加 consolidation step 的可行性——需要先確認 session_search 的召回品質是否夠好當 consolidation 的輸入

## 關鍵詞

`agent-memory` `file-based-memory` `consolidation` `post-vector` `markdown-as-db` `always-on-agents`

