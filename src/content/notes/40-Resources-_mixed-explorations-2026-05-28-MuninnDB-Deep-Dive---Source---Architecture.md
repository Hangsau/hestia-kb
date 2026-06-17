---
_slug: 40-Resources-_mixed-explorations-2026-05-28-MuninnDB-Deep-Dive---Source---Architecture
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-MuninnDB-Deep-Dive---Source---Architecture.md
title: MuninnDB Deep Dive — Source + Architecture
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- develop
- docs
- mcp
- memory
- muninn
- muninndb
- pas
- semantic
- synrix
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# MuninnDB Deep Dive — Source + Architecture

**日期**: 2026-05-28
**延續自**: [[2026-05-28-MuninnDB---Synrix---Follow-up]]
**延續自**: [[2026-05-28-MuninnDB---Synrix---Agent-Memory-Architecture-Exploration]]

## 來源：MuninnDB Source — `develop` branch README + Docs

### 核心發現

**1. MCP Transport Bug — Claude Desktop v1.1.4010+**
文件中記錄了一個實際 bug：Claude Desktop v1.1.4010+ 如果在 MCP config 中有 `"type": "http"` 會崩潰。正確設定是**完全省略** `"type"` 欄位，讓 URL 自行推斷傳輸層。
- OpenCode 的 tools 命名會 prefix server key：`muninn_muninn_remember`
- 可透過 server key 改短（如 `memory`）獲得 `memory_muninn_remember`

**2. Semantic Triggers — 推播模型已完整實作**
文件確認：`muninn_activate` 是被動查詢；Semantic Trigger 是主動推播（`SUBSCRIBE` → `UNSUBSCRIBE`）。推播觸發時機：relevance 改變。不是 cron，不是輪詢。
- 觸發後主動送到 agent，不需 agent 主動請求

**3. MCP 四種 AI tools 整合方式（已完整實作）**
OpenClaw：用 `muninn mcp` proxy 走 stdio，自動處理 bearer token auth，不需要在 config 寫 credential。
其他（Cursur/Windsurf/VSCode/GitHub Copilot）：全部走 HTTP transport，URL 統一是 `http://127.0.0.1:8750/mcp`。

**4. Recall@10 +21% — PAS 量化收益**
Predictive Activation Signal（PAS）在 2000 個合成項目測試：
- Recall@10: +21%（從 transition table 推斷出的 next-step memory）
- MRR: +10-15%
- 關鍵：PAS 是 candidate expansion，不只是 re-ranking

**5. 矛盾偵測三層次（storage-layer，主動發現）**
- **Structural**：64×64 boolean matrix，O(1) 查詢，固定大小（不隨 vault 增大）
- **Concept-Cluster**：FTS overlap，寫入時觸發
- **Semantic**：需要 enrich plugin（LLM 介入），最貴也最準
- 矛盾觸發後：Bayesian confidence 更新 + `contradicts` association 建立 + Subscription push

**6. Hebbian 公式幾何平均信號**
co-activation signal = `sqrt(score_A × score_B)`，不是直接相乘。幾何平均確保高低分數 co-activation 不被高的一方主導。

**7. 前綴命名空間強制（15 種關係類型）**
`supports`/`contradicts`/`depends_on`/`supersedes`/`relates_to`/`is_part_of`/`causes`/`preceded_by`/`followed_by`/`created_by_person`/`belongs_to_project`/`references`/`implements`/`blocks`/`resolves`。User-defined 在 `0x8000+`。

**8. BSL 1.1 License 具體條款**
- 免費：個人/hobbyist/研究者/開源專案
- 免費：小組織（< $10M revenue）
- 需付費：商業 SaaS 部署（作為服務而非產品）
- 2030-02-26 轉 Apache 2.0

---

## 對 Hermes 的落地點（更新）

| 優先級 | 方向 | 具體路徑 | 備註 |
|--------|------|----------|------|
| 立即 | 前綴強制 scheme | `memory-consolidator` 或新 script 中實作 `MEM:`/`PLAN:`/`RESULT:` 前綴命名空間 | 對 Synrix/MuninnDB 都適用 |
| 短期 | PAS-style sequential tracking | 在 `session_search` 或 `memory-consolidator` 中追蹤連續查詢模式，用於 candidate expansion | 不需 LLM；可用簡單 counter table |
| 中期 | Semantic trigger push model | 評估 MCP client 串接 MuninnDB 的可行性 | MCP protocol 已完整實作 |
| 中期 | Ebbinghaus decay 數學 | 直接實作 `B(M) = ln(n+1) - 0.5*ln(ageDays/(n+1))` | 純數學，不需要 ML |
| 長期 | Bayesian confidence 更新 | 在 memory entry 加 confidence 欄位，寫入新 fact 時自動更新舊 entry 信心 | 需評估複雜度 |

---

## 未追蹤 Leads

- https://muninndb.com/docs/how-memory-works — 深度解析（已有文件側部分內容，repo 有完整 Markdown）
- https://github.com/scrypster/muninndb/blob/develop/docs/retrieval-design.md — 6-phase pipeline 詳細實作
- https://github.com/scrypster/muninndb/blob/develop/docs/engram.md — Engram 資料結構定義

## ✅ 本次探索完成

