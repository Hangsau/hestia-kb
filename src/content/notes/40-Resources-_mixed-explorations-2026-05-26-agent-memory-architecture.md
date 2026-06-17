---
_slug: 40-Resources-_mixed-explorations-2026-05-26-agent-memory-architecture
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-agent-memory-architecture.md
title: 2026-05-26 Agent Memory Architecture Exploration
created: '2026-05-26'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 2026-05-26 Agent Memory Architecture Exploration

**延續自**: (standalone exploration, no prior notes)

## Per-Source Insights

### 1. memU — File-Based Agent Memory Framework (NevMind-AI)
`https://github.com/NevaMind-AI/memU` | 11pts Show HN

**核心設計**: 三層架構（Resource → Item → Category），記憶組織成檔案系統階層。

| 檔案系統 | memU Memory |
|----------|-------------|
| 📁 Folders | 🏷️ Categories（自動組織的主題） |
| 📄 Files | 🧠 Memory Items（萃取的事實、偏好、技能） |
| 🔗 Symlinks | 🔄 Cross-references（跨記憶關聯） |
| 📂 Mount points | 📥 Resources（對話、文件、圖片） |

**非嵌入檢索策略**：
- 檢索從 Category Layer 開始（類別層），而非 embedding vector
- 每個 category 存為可讀 Markdown 檔案
- LLM 直接讀取相關記憶檔案，使用語意理解而非向量相似度
- 僅在 category layer 不夠時才 fallback 到 item-level retrieval（可選用 embedding 加速）

**關鍵命題**：
> "RAG often returns plausible but incorrect context — especially harmful for agents that act over long horizons."
> "what should NOT be retrieved via embeddings at all?" — memU 的核心問題框架

**三層設計**：
1. **Resource Layer**: 原始資料的直接訪問（對話、文件、圖片）
2. **Item Layer**: 目標事實檢索（從互動中即時萃取）
3. **Category Layer**: 摘要級概覽（自動上下文組裝用於預測）

**Proactive Memory 模式**：
- memU Bot 持續監控、記憶、主動 intelligence
- 主代理 ◄──► memU Bot ◄──► DB 形成連續同步迴圈
- 「24/7 always-on proactive agents」— 沒有使用者命令也持續運行

**對 Hermes 的啟發**：
- **檔案系統作為記憶** vs 向量檢索 — 與 Hermes skills.md 精神一致
- Category Layer = 知識分類（類似 Hermes 的 domain/skills 分類）
- 非嵌入檢索適合結構化知識（配置、政策、代理狀態）— Hermes 的 skills、proposals、workspace 都屬此類
- Proactive vs Reactive 的區別 — Hermes Heartbeat 是 reactive，探索是 proactive 的潛力

**標記為 UNTRACKED leads**：
- memU 的 PostgreSQL + pgvector 部署方式
- memU Bot 的 proactive loop 實作（`examples/proactive/proactive.py`）
- Cloud API `POST /api/v3/memory/retrieve` 的 proactive context loading 機制

---

### 2. JARVIS-1 — Memory-Augmented Multimodal LLM Agent
`https://craftjarvis-jarvis1.github.io/` | 39pts

**核心貢獻**：Minecraft 開放世界代理，多模態輸入 + 多模態記憶。

**記憶架構**：
- multimodal memory 促進規劃（pre-trained knowledge + 實際遊戲生存經驗）
- 記憶增長的終身學習 paradigm → self-improving agent

**Self-Improving 範例**（ObtainDiamondPickaxe 任務）：
- Epoch 1: 10 steps, 失敗（缺 furnace）
- Epoch 2: 12 steps, 失敗（缺 fuel）
- Epoch 3: 11 steps, 成功（更準確更高效）

**對 Hermes 的啟發**：
- **記憶增長驅動 self-improvement** — heartbeat learning 的 distillate 機制正是這種思想的體現
- 錯誤驅動的記憶更新（Epoch 1 失敗 → Epoch 2 記住 furnace → Epoch 3 記住 fuel）
- multimodal 輸入的記憶整合（視覺 + 文字 → 統一記憶表示）

---

## 跨文章 Synthesis

### 趨同訊號：結構化優於純嵌入

memU、JARVIS-1、和之前筆記中的 Mem0/tilth/context-llemur 都收斂到同一個結論：

| 系統 | 記憶模型 | 關鍵設計 |
|------|----------|----------|
| memU | 檔案系統（Markdown files） | Category Layer 取代純向量檢索 |
| JARVIS-1 | 多模態記憶增長 | pre-trained knowledge + 經驗的雙重來源 |
| Mem0 | multi-signal retrieval | semantic + BM25 + entity |
| tilth | 增量上下文管理 | structured context > raw embedding |

**共同原則**：
1. **LLM 擅長閱讀和推理，不只是排名向量** — 直接 LLM 閱讀結構化記憶
2. **時效性和精確性 > 語意相似性** — 嵌入無法編碼有效性或順序
3. **終身學習需要錯誤驅動的記憶更新** — JARVIS-1 的 Epoch 學習 model

### 對 Hermes Memory Layer 的具體建議

基於 memU 的 Category Layer 設計：
- Hermes 的 skills.md / proposals / workspace INDEX 都是 **canonical memory files**
- 這些檔案應該可以直接被 LLM 讀取，而不是只能靠 embedding 檢索
- 當前 `search_files` 是 keyword search，未來可以升級為「LLM 直接讀取相關檔案 + semantic understanding」

## 未追蹤 Leads（純 URL）

- `https://github.com/NevaMind-AI/memU/blob/main/examples/proactive/proactive.py` — memU proactive loop 實作
- `https://api.memu.so/docs` — memU Cloud API 文件（proactive context loading）
- `https://craftjarvis-jarvis1.github.io/` — JARVIS-1 完整論文（HTML 版本）

## ✅ 本次探索完成

**探索日期**: 2026-05-26
**品質評級**: 中（2/3 articles fetched successfully）
**主要收穫**: memU 的 Category Layer 設計直接回答了「結構化記憶 vs 向量檢索」的取捨問題，與 Hermes 的 skills.md 精神高度一致。