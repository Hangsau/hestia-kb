---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Agent-Memory-Architectures---Total-Recall---VoltAgent-探索
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Agent-Memory-Architectures---Total-Recall---VoltAgent-探索.md
title: Agent Memory Architectures — Total Recall + VoltAgent 探索
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- gate
- hermes
- https
- memory
- observability
- recall
- total
- voltagent
- write
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# Agent Memory Architectures — Total Recall + VoltAgent 探索

**日期**: 2026-05-22
**來源**: HN 探索（Leads 4 & 5 from prior session plan）
**延續自**: [[2026-05-22-Agent-Memory---Grep-vs-RAG]]  [[2026-05-22-Behavior-Cache---Sandbox-Muscle-Mem---bVisor]]

---

## 1. Total Recall — Write-Gated Memory for Claude Code（67 pts）

**URL**: https://github.com/davegoldblatt/total-recall
**Repo**: davegoldblatt/total-recall

### 核心機制：Write Gate

Total Recall 的核心不是「怎麼存」，而是「什麼值得存」。Write Gate 五題測試：

1. 會改變下次行為嗎？（偏好、界限、模式）
2. 是別人在等的承諾？（deadline、交付物、後續）
3. 值得記住 reasoning 的决策？（為什麼選 X 而非 Y）
4. 穩定的事實？（不會明天就變）
5. 使用者明確說「記住這個」？

> 「The system keeps itself clean so Claude isn't wading through junk to find what's relevant.」

### 四層架構（廚房隱喻）

```
Counter (CLAUDE.local.md)     → ~1500字，每次 session 自動載入
Pantry (memory/registers/)    → 按類別組織，隨需求 load
Daily Notebook (memory/daily/)→ 一切先寫這裡，用戶之後決定promote
Storage Closet (memory/archive/) → 舊資料，可搜尋但從不自動載入
```

**關鍵：Daily log 先寫，用戶控制 promote**。Claude 不自己決定什麼重要。

### 矛盾協議（Contradiction Protocol）

舊資訊標 `[superseded]` 而非刪除。記錄「什麼時候改變了 + 為什麼」，改變的軌跡本身就是有價值的資料。

### 修正Gate（最高優先）

一次修正 → daily log + register + counter 同時更新。舊資料同樣標 `[superseded]`。

### 與其他工具比較

|  | Total Recall | Auto-ingest |
|---|---|---|
| 什麼被保存 | 只有通過 write gate 的 | 全部 |
| 預設目的地 | daily log（稍後 promote） | 永久儲存 |
| Context 成本 | ~1500 字 working memory | 無限成長 |
| 修正行為 | 立即 propagate 到所有 tier | 不一定 |

### Hermes 啟發

1. **Memori 需要 Write Gate**：Memori 現在是全自動 capture，沒有 gate。和 Total Recall 的「全部寫daily log → 用戶 promote」相比，Memori 的「全部壓縮 → 自動刪除」是另一個極端。Hermes 可以考慮 hybrid：daily log 先寫，promote 靠 `vault_decay.py` 的 decay score，而不是全自動或全手動。

2. **Contradiction Protocol 值得學**：當 heartbeat 修正自己的判断（例如 WS-025 從 PARTIAL→READY），舊的 STATUS block 應該標 `[superseded]` 而非直接覆寫。這樣日後能看到演進軌跡。

3. **Write Gate 的五題測試可以內化為決策框架**：用在提案決策上——「這提案會改變下次行為嗎？」、「是別人在等的承諾嗎？」、「值得記住 reasoning 嗎？」。這比直接「做/不做」更能避免草率提案。

4. **Parallel sessions write gate**：HN comment 指出 concurrent sessions 寫同一 daily log 無鎖。Total Recall 的解法是「hooks fail safely」，不 blocking。Hermes 的多 agent 寫入（WS-020）需要類似的 graceful degradation。

---

## 2. VoltAgent — TypeScript Agent Framework + Observability Platform（32 pts）

**URL**: https://voltagent.dev | https://github.com/Voltagent/voltagent
**Stars**: 600+

### 雙層產品

- **開源 TypeScript Framework**（MIT）：建構 agent 的 runtime
- **VoltOps Console**（Cloud/Self-Hosted）：Observability + Automation + Deployment + Evals

### Framework 核心能力

| 能力 | 實作 |
|---|---|
| Memory | 可插拔 adapter（SQLite/LibSQL 等） |
| MCP | 原生支援，`@voltagent/mcp` |
| Guardrails | Runtime input/output validation |
| Evals | agent eval suites |
| Workflow Engine | Declarative multi-step，suspen/resume |
| Supervisor/Sub-Agents | 團隊 agent 協調 |

### Workflow 的 suspend/resume 模式

```typescript
await suspend("Manager approval required", { amount, ... });
// workflow 暫停，等待外部信號
// resumeData 帶决策結果回來
```

這相當於 Hermes 的 OTP Gate（WS-010）+ human-in-the-loop 的實際實作。VoltAgent 的 workflow engine 把 `suspend` 當成一等公民，有完整的 schema + 恢復點管理。

### Observability Console

VoltOps Console 的功能：
- Execution traces（每個 step 的輸入輸出）
- Memory management（inspect agent 記憶體）
- Prompt builder（設計 + 測試 +  refinement）
- Guardrails（安全邊界配置）
- Evals（行為測試 suite）

### 與 Hermes 的相關性

1. **VoltOps = heartbeat 的 observability 願景的 production 版本**：heartbeat 目前只有 snapshot/scoring，但 VoltOps 展示了更完整的 trace → eval → deploy 循環。WS-022（MCP server）可以借鑒 VoltAgent 的 observability design。

2. **Workflow suspend/resume**：Hermes 的 OTP gate 可以用這種模式——suspend workflow，等用戶 approve，再 resume。這比「直接跳出並等 reply」更結構化。

3. **Memory adapter 模式**：VoltAgent 的 `new Memory({ storage: LibSQLMemoryAdapter({...}) })` vs Memori 的 `Mem0PythonAdapter`。Hermes 的 Memori adapter 設計可以參考這個 interface pattern。

4. **Supervisor + Sub-Agents**：VoltAgent 的 supervisor runtime 路由 tasks 到 sub-agents，和 WS-020（multi-agent write queue）有相似的協調需求。VoltAgent 的 implementation 比 Orloj 的 YAML 更落地。

---

## 跨文章 Synthesis

### 記憶系統的兩個極端

| 系統 | 策略 | 優點 | 缺點 |
|---|---|---|---|
| Total Recall | 用戶控制 promote（保守） | 乾淨，context cost 低 | 需要用户主動參與 |
| VoltAgent Memory | 可插拔 adapter（全自動） | 簡單，零 user friction | 可能有 junk accumulation |
| Muscle-Mem | 自動 cache/replay（確定性） | 零 LLM cost for cached tasks | 環境驗證複雜 |
| Memori | 自動壓縮（全自動） | 零 user friction | junk accumulation, no gate |

### Hermes 的定位

Hermes 目前走的是 Memori 路線（全自動），缺少 gate。Total Recall 的 Write Gate 是值得考慮的 enhancement：
- 短期：在 `memory-consolidator` 加 metadata（confidence, last_verified）——相當於 write gate 的「驗證」維度
- 長期：當 vault_decay.py 有足夠數據後，可以考慮「promote based on decay score」而非全自動

### 另一個共同主題：Observability 是標配

VoltAgent（32 pts）和 Lucidic（116 pts，來自 prior exploration）都強調 observability。agent 系統從「跑起來」進入「跑得怎麼樣」的階段。這對 Hermes 的 heartbeat 是好消息——heartbeat 做的事（snapshot/scoring/evolve）正是 observability 的核心，只是現在只有一個 agent 在用。

---

## 未追蹤
- https://news.ycombinator.com/item?id=44735843 — Lucidic（116 pts，agent observability，生產環境 debug）
- https://github.com/deusXmachina-dev/memorylane — MemoryLane（Total Recall HN comment 提到的替代方案）
- https://github.com/sibellavia/dory — 另一個 write-gated memory tool
- https://voltagent.dev — VoltAgent 完整文件（含 MCP/Tools/Workflow）

## ✅ 本次探索完成
