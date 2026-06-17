---
_slug: 40-Resources-_mixed-explorations-2026-05-28-muninn-synrix-follow-up
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-muninn-synrix-follow-up.md
title: MuninnDB + Synrix — Follow-up
created: '2026-05-28'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# MuninnDB + Synrix — Follow-up

**日期**: 2026-05-28
**延續自**: [[2026-05-28-muninn-synrix-agent-memory-architecture]]

## 來源一：MuninnDB 官方文件 (`muninndb.com/docs`)

### 核心發現

MuninnDB 的文件確認了探索筆記的推論，並提供更多具體細節：

**認知三原語（文件級確認）**：
1. **Recency** — priority score 在 query time 計算，基於 `LastAccess` + `AccessCount`。不是儲存衰減分數，是即時計算。
2. **Hebbian Learning** — association strength = 資料庫內的數學（不是 ML model）。共同激活 → 邊強化。
3. **Semantic Triggers** — subscribe 某 context string，MuninnDB 在相關性改變時 push notification。不需要 polling。

**文件揭示的關鍵細節**：
- **Relevance 是 confidence gate**：需高於某 threshold 才會被視為相關。Relevance 由 AccessCount 動態計算，非靜態。
- **ACTIVATE 同時是 retrieval 和 learning event**：每次查詢都是學習事件，會更新 AccessCount 和 association graph。
- **Vault 是 namespace**：每個 agent/user 有獨立 vault，資料完全隔離。
- **四種協定**：MBP (port 8474, TCP binary) → gRPC (8477) → REST (8475) → MCP (8750)。MCP 是給 Claude/Cursor 等 AI tools 的介面。
- **License BSL 1.1**：2030-02-26 轉 Apache 2.0。免費個人/開源/內部使用，商業 SaaS 需另授權。

**對 Hermes 的具體落地點**：
- MCP protocol (port 8750) 是直接整合路徑——不需要改造 Hermes 底層，只要實作 MCP client 就能讓 Hermes 使用 MuninnDB 作為記憶後端
- Semantic Trigger 的 push model 完全顛覆現有 polling 架構，是一個乾淨的 upgrade 方向

---

## 來源二：Synrix.io（ unreachable）

`synrix.io` — curl + sanitizer 後無內容輸出。懷疑是：
- JavaScript-rendered SPA（curl 拿不到內容）
- Cloudflare 或類似 protection
- 或者真的沒有 static content

**之前筆記 lead**：https://synrix.io — 標記為 `unreachable`，日後有瀏覽器工具再重試。

---

## 未追蹤 Leads

- https://github.com/scrypster/muninndb — source code（文件提到 v0.3.6-alpha，repo 應有完整實作）
- https://muninndb.com/docs/how-it-works — 深度解析記憶運作原理（文件有連結但本次未專門 fetch）
- https://github.com/RYJOX-Technologies/Synrix-Memory-Engine — Synrix open part（Python MIT 部分）

## ✅ 本次探索完成
