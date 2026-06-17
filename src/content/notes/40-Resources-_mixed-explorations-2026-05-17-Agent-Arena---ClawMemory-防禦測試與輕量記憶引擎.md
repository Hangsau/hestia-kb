---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Agent-Arena---ClawMemory-防禦測試與輕量記憶引擎
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Agent-Arena---ClawMemory-防禦測試與輕量記憶引擎.md
title: Agent Arena + ClawMemory：防禦測試與輕量記憶引擎
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- arena
- clawmemory
- fetch
- hermes
- hiding
- llm
- sanitize
- search
- semantic
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Agent Arena + ClawMemory：防禦測試與輕量記憶引擎

**日期**: 2026-05-17 | **來源**: HN [[Agent Arena]](https://news.ycombinator.com/item?id=46911873) + GitHub [[ClawMemory]](https://github.com/clawinfra/clawmemory)

**標籤**: #prompt-injection #agent-security #agent-memory #bm25 #sqlite #hermes-security

---

## 1. Agent Arena — Prompt Injection 實戰測試場

### 什麼
wiz.jock.pl 的 Agent Arena — 10 種 prompt injection 攻擊的測試平台。送你的 agent 去一個「無害的 web dev cheat sheet」頁面，看它會不會被隱藏指令操控。

### 攻擊向量矩陣（由淺到深）

| # | 攻擊 | 難度 | 類別 |
|---|------|------|------|
| 1 | HTML Comment | Basic | Structural Hiding |
| 2 | White on White | Basic | Visual Hiding |
| 3 | Hidden Div (display:none) | Medium | Structural Hiding |
| 4 | Micro Text | Medium | Visual Hiding |
| 5 | Aria Hidden | Medium | Semantic Hiding |
| 6 | Data Attribute | Medium | Structural Hiding |
| 7 | Zero-Width Characters | Hard | Encoding Tricks |
| 8 | Image Alt Override | Hard | Semantic Hiding |
| 9 | Off-Screen Content | Hard | Visual Hiding |
| 10 | Multi-Layer Attack | Expert | Combined |

### 社群數據
- 基本攻擊（#1-2）成功率 ~70%
- 僅 ~15% agent 達到 A+（0 injection）
- 多語言效應：ChatGPT 5.2 英文得 C，但轉德文避開所有攻擊
- Screenshot-based agent 完全免疫文字層攻擊（但開新的視覺攻擊面）
- 新版區分三態：Resisted / Detected / Compromised

### 關鍵論點
> "Even if your agent fails 3 out of 10 tests, that's a 30% chance it exfiltrates whatever secrets are in its environment. The defense can't just be 'hope the model catches it.' You need architectural controls on the egress side too." — pipejosh

### Hermes 對標

**現有防禦線**：

| 攻擊 # | 攻擊類型 | Hermes 對應 | 狀態 |
|--------|---------|-------------|------|
| 1-6 | 結構/視覺/語義隱藏 | `sanitize_fetch.py` — 清除 HTML 標籤、隱藏元素、屬性 | ✅ 覆蓋 |
| 7 | Zero-Width Unicode | `sanitize_fetch.py` — 清除零寬字元、Unicode tags | ✅ 覆蓋 |
| 8 | Image Alt Override | `sanitize_fetch.py` — 行 51 strip `![alt](url)` markdown syntax；行 61 strip `<img ...>` 整個 tag | ✅ 確認覆蓋（2026-05-17） |
| 9 | Off-Screen Content | `sanitize_fetch.py` — HTML strip 後無 DOM 概念，文字內容可能殘留 | ⚠️ 部分 |
| 10 | Multi-Layer | **Plan-Then-Execute Phase Lock** — 即使 LLM 被社會工程說服，也無法觸發新 tool call | ✅ 架構級防禦 |

**Sanitizer 覆蓋率**：9/10（#10 由 Plan-Then-Execute 覆蓋）。

**已確認（2026-05-17）**：`sanitize_fetch.py` 行 51 的 `!\[.*?\]\([^)]*\)` regex 移除 markdown image syntax（含 alt 內容）；行 61 的 `<[^>]+>` 移除整個 `<img>` HTML tag。因此 Image Alt Override 攻擊向量（`<img alt="Ignore previous instructions...">`）**兩層皆被移除**，不構成威脅。

**Multi-Layer Attack (#10) — Hermes 的獨特防禦**：攻擊 #10 結合 structural hiding + social engineering in visible text。這是 sanitizer 無法完全防禦的（visible text 本來就應該保留）。但 Hermes 的 **Phase-Locked Exploration**（Plan-Then-Execute）在架構層解決了這個問題：
- Phase 1 鎖定 plan → 之後不可新增 fetch target
- 即使 LLM 在 Phase 2 被社會工程說服「你應該去看 XXX」，Phase Lock 阻止行動
- 這不是 model-level defense，是 architectural constraint

**Agent Arena 對 Hermes 的價值**：可以用來**回歸測試**我們的 sanitizer + validator pipeline。做法：
1. 用 `curl | sanitize_fetch.py` 過 Agent Arena 的測試頁面
2. 把 sanitized output 送給 LLM
3. 檢查 response 是否有 canary phrases
→ 可量化 sanitizer 對單獨攻擊的防禦力，並確認 #8、#9 的實際覆蓋狀況。

---

## 2. ClawMemory — SQLite + BM25 的輕量記憶引擎

### 什麼
clawinfra/clawmemory — 自主記憶引擎。Go 寫的，為 OpenClaw agents 設計。核心設計：**不要 vector DB，不要 embeddings**。只用 SQLite FTS5 (BM25) + LLM extraction。

### 設計哲學
> "At agent-memory scale (~10K facts), BM25 full-text search is faster, simpler, and more predictable than semantic vector search."

| | BM25 (FTS5) | Vector Search |
|---|---|---|
| Latency | ~1ms | ~3000ms |
| Dependencies | SQLite only | Ollama + GPU + embedding model |
| CPU cost | Negligible | Significant |
| Accuracy | Excellent for structured facts | Better for fuzzy semantic queries |

**核心洞見**：LLM 在 extraction 階段已經做了 semantic heavy lifting——把非結構化對話轉成結構化 facts。之後的檢索只需要 keyword matching，不需要再跑一次 semantic search。

### 架構
```
OpenClaw Plugin (TS)
   auto-capture (post-turn) + auto-recall (pre-turn)
         ↓ HTTP :7437
ClawMemory Server (Go)
   Extractor (LLM) → Resolver (contradiction) → Store (SQLite+Turso)
   Search (BM25 FTS5) ← → Decay (TTL + importance)
   Profile Builder
```

### 關鍵功能
- **Fact extraction**：LLM 從對話中提取 facts/preferences/persona
- **Contradiction resolution**：偵測衝突事實 → newer wins
- **Temporal decay**：half-life 30 天，低 importance facts 自動清除
- **Profile builder**：synthesize 個人檔案
- **Turso sync**：optional cloud sync（cold storage layer）

### v0.2 的決定性轉向（2026-04-06）
移除 vector search 和 Ollama 依賴 → 純 BM25。Recall latency：3000ms → 1ms。**零 GPU 依賴**。

### Hermes 對標

| 面向 | Hermes 現狀 | ClawMemory |
|------|------------|-------------|
| 儲存 | MEMORY.md (單一檔案) | SQLite FTS5 |
| 提取 | L2 memory-consolidator (cron, LLM) | LLM-based extractor (post-turn) |
| 檢索 | skill_view / session_search / read_file | BM25 FTS5 |
| 矛盾解決 | 無系統化機制 | newer-wins resolver |
| 衰減 | 手動 ISSUES.md TTL | 自動 half-life decay |
| 同步 | GitHub push/pull | Turso cloud sync |
| 維運成本 | 低（檔案 + cron） | 需跑 Go server (:7437) |

**差異**：
- Hermes 是 file-based pipeline（MEMORY.md → consolidate → brief），ClawMemory 是 daemon-based API server
- Hermes 使用多重檢索工具（session_search 語意搜、search_files 內容搜、skill_view 結構化），ClawMemory 只有 BM25
- ClawMemory 的 temporal decay + contradiction resolution 是 Hermes 沒有的——但這對 Hermes 的規模可能 overkill（我們沒有 10K facts）

**可借鏡的設計**：
1. **BM25 over FTS5 for vault search**：現在 vault 用 Obsidian 的內建搜尋（content grep）。可以考慮在 ingest pipeline 加 FTS5 index——用 `search_files` 做 regex 搜已經很快，BM25 的 ranking 會讓結果品質更好但成本差異不大。
2. **Contradiction detection**：WUPHF 的 lint 框架已經有 contradiction detection 的規劃（`lint_contradictions.tmpl`），不必引入 Go-based 方案。
3. **Temporal decay for known issues**：現有 ISSUES.md TTL 是手動的，ClawMemory 的自動 half-life decay 可以作為 EVOLVE `_cleanup_severities` 的增強靈感。

---

## 🔗 跨文章 Synthesis

兩個主題在「架構性防禦 > model-level 防禦」上交匯：

1. **Agent Arena** 的核心教訓：defense can't just be "hope the model catches it" → 需要 architectural controls
2. **ClawMemory** 的設計決策：BM25 > vector search，因為 extraction 階段已經 semantic 完了→ 信任 pipeline 的前段，後段用簡單工具

共同 pattern：**把難題前推到 pipeline 的前段（LLM extraction / structural constraints），讓後段保持簡單可預測**。

Hermes 的 Plan-Then-Execute 遵循同樣模式：Plan phase 用人類（或 LLM）做 curation 決策，Execute phase 用確定性 lock 防止偏離。Sanitizer 把 injection 問題前推到 input boundary，而非讓 LLM 自己判斷。

---

## ⏳ 未追蹤

- Agent Arena 的實際測試結果——跑 `curl ref.jock.pl/modern-web | sanitize_fetch.py | llm` 並檢查 canary leak
- Agent Arena leaderboard 資料（哪些 model/framework 表現最好）
- Geoffrey Huntley "Everything is a Ralph Loop" (Jan 2026)

---

## ✅ 本次探索完成

