---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-Agent-記憶系統延續---Beads---MemForge-深度挖掘
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-Agent-記憶系統延續---Beads---MemForge-深度挖掘.md
title: 探索：Agent 記憶系統延續 — Beads × MemForge 深度挖掘
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- active
- agent
- beads
- git
- hermes
- mcp
- memforge
- memory
- readme
- recall
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：Agent 記憶系統延續 — Beads × MemForge 深度挖掘

**延續自**: [[2026-05-22-探索-Agent-記憶系統---Beads---MemForge]]

**日期**: 2026-05-22 ← 先跑 `date +%Y-%m-%d` 取系統日期，不要自己估算
**來源**: 直接 fetch Beads + MemForge 完整 README（從 2026-05-22 探索的「未追蹤」leads 出發）
**標籤**: #agent-memory #Beads #MemForge #Dolt #MCP

## Per-Source Insights

### Beads 完整 README — 新發現

**URL**: https://github.com/steveyegge/beads | **上次狀態**: HN 19pts 片段，今日完整讀取

上次筆記只抓到「Dolt + issue graph」的輪廓。完整 README 揭示三個關鍵新發現：

**1. Git-Free Mode — 適用 Hermes 環境**

Beads 完全不需要 git：
```
export BEADS_DIR=/path/to/.beads
bd init --quiet --stealth
```
Dolt 自己就是 storage backend，git 是可選的。這對 Hermes 的 multi-agent workspace 極為重要——`tasks/` 裡的 agent 現在可以用 Beads 追蹤任務而不依賴 `/srv/hearth` 的 git namespace，避免心跳 cron 和互動 session 的 git 操作衝突。

`BEADS_DIR` 環境變數可以指向任何目錄（不在 git 控管下），等於是每個 agent 的 private workspace tracker。

**2. PyPI MCP Server — 16 個工具，現在就能裝**

`pip install beads-mcp` → 立刻給 Claude Code 16 個記憶追蹤工具。不需要 clone repo、不需要跑 Dolt server。

對 Hermes 的意義：mentioned in the consolidated proposal. Let me check if the OTP gate implementation is documented somewhere, or if I should update the proposal with verification results. This could be a quick SPIKE — install beads-mcp, verify it works with Claude Code, and update the relevant skill/proposal. — 直接 pip install，不碰 `/srv/hearth` git repo（--stealth）
- 工具數量：16 個（比任何現有 Hermes skill 都多）
- 功能：issue CRUD、dependency graph、task claim/update/close、context prime

**3. Semantic Compaction 是演算法压缩，不是 LLM**

上次的理解有偏差：「記憶衰退（Compaction）」被描述為 semantic compression，但 README 沒有提到 LLM involvement。Compaction 是演算法驱动的 forgetting，不是主動 revision（MemForge 那種）。

這讓 Beads 和 MemForge 的差異更清晰：Beads 是結構化 forget，MemForge 是結構化 improve。一個往外丟、一個往內修。

---

### MemForge 完整 README — 架構細節

**URL**: https://github.com/salishforge/memforge | **Benchmark**: LongMemEval R@5 = 93.2%

**新的架構層次：**

**Sleep Cycle Phase 2.5 — Conflict Resolution**

之前只知道有 Phase 0-6，完整 README 揭示了 Phase 2.5（衝突解決）和 Phase 4b（時間鏈）。衝突解決是 multi-factor scoring 驅動的：
- 同一事實的 multiple memory entries 會被 resolve
- 衝突記錄在 `memory_conflicts` table
- outcome feedback 影響衝突的 resolution 方向

這個 phase 對 Hermes 的提案有意義——`hermes-consolidation-step` 如果要實作「cross-cutting insight generation」，衝突檢測是必備的（跨筆記的資訊可能互相矛盾）。

**Active Recall — Proactive Memory Surfacing**

MemForge 的 `/active-recall` endpoint 不是被動查詢，而是在 agent 行動前主動推相關記憶：
```
POST /memory/:agentId/active-recall
{ "context": "About to modify user dashboard layout" }
```
這和 Hermes 的 context 注入不同——MemForge 是「根據即將做的事召回相關記憶」，不是「根據查詢字召回記憶」。

對 heartbeat 的啟發：heartbeat 在每次 cycle 開始前可以跑一次 active recall，召回與即將執行的 action 相關的歷史 pattern（過去怎麼處理類似情況的？）。

**Prompt Injection Boundaries**

MemForge 的 security 9 audit 包含 "prompt injection boundaries" 作為 explicit audit item（ADVERSARIAL-ASSESSMENT.md）。但 README 只說有這回事，沒說具體怎麼實作。這個文件和 Beads 的 README（"prompt injection boundaries" in MemForge's THREAT_MODEL）都在描述有這個概念但沒有具體實作。

**Schema Crystallization — 從 Pattern 到 Structure**

Phase 5.5：重複發生的時間 pattern 會被 crystallize 成 `entity_type='schema'`。這比簡單的「記住」更深一層——是把多次出現的 pattern 變成可查詢的結構。

對 Hermes 的 vault 可類比：vault 中的 `daily/` 和 `research/` 筆記如果累積了某個 domain 的 pattern，可以 crystallize 成 vault 內的「概念卡片」。

---

## 跨文章 Synthesis

**Beads + MemForge 的互補地圖：**

| 維度 | Beads | MemForge |
|------|-------|----------|
| Memory 方向 | 往外 forget（compaction） | 往內 improve（revision） |
| 成長機制 | 演算法 decay | LLM-driven reflection |
| 觸發方式 | 被動（context window pressure） | 主動（sleep cycle, active recall） |
| Security | 無 injection 實作（THREAT_MODEL 提到但架構沒實） | 明確 audit item，但實作未知 |
| MCP 工具數 | 16 個（beads-mcp） | 17 個（memforge-mcp） |
| 對 Hermes 價值 | Dolt-as-backend + Git-free workspace tracker | Sleep cycle token budget + Active recall |

**共同缺口再次確認**：兩者的 prompt injection 防禦都是「存在於 threat model 但架構層沒有實作」。MemForge 有 9 輪 audit 但 README 說「prompt injection boundaries」只是 audit item 清單，沒有具體實作描述。這是已知的 open gap。

**Hermes 可以借鑒的方向（更新之前的觀察）：**

1. **Beads 的 Git-Free + BEADS_DIR** → 可用於 heartbeat 的 per-cycle workspace state tracking，不走 git conflict
2. **MemForge 的 Active Recall** → heartbeat 的 pre-action recall，先問「這次 cycle 要做 X，過去類似情況怎麼處理的？」
3. **MemForge 的 Schema Crystallization** → vault 的概念卡片化

---

## ⏳ 未追蹤

- https://github.com/gastownhall/beads/blob/main/docs/ANTIVIRUS.md（Beads Windows AV false-positive 處理）
- https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md（跨機器 sync 機制）
- https://github.com/salishforge/memforge/blob/main/ARCHITECTURE.md（MemForge 內部架構）
- https://github.com/salishforge/memforge/blob/main/ADVERSARIAL-ASSESSMENT.md（9 輪 security audit 詳細內容）

---

## ✅ 本次探索完成
