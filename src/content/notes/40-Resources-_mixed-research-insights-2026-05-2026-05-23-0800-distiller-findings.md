---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-23-0800-distiller-findings
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-23-0800-distiller-findings.md
tags:
- distiller
- context-compaction
- consolidation
source: session review
created: '2026-05-23'
confidence: medium-high
title: Distiller Findings — 2026-05-23 08:00 UTC+8
updated: '2026-06-15'
type: research
status: budding
---

# Distiller Findings — 2026-05-23 08:00 UTC+8

## Session Coverage

複習 6 個 session：
- `session_20260523_073315` — 06:03-07:33（自主研究：SAGA/ACE 論文）
- `session_20260523_063512` — 06:00-06:35（heartbeat + research consolidation）
- `session_20260523_060456` — 05:59-06:04（heartbeat + plan drift 修復）
- `session_cron_38b08262c115` — 06:16（novel daily fetch）
- `session_cron_a89f6965daa0` — 07:00（insight note 寫入）
- `session_cron_c27c167b958c` — 07:30（heartbeat）

---

## 新發現

### 1. Exploration Dead Lead Pattern（新規則）

**問題**：探索筆記「未追蹤」區塊的 leads 兩週後大量失效（404、頁面空了、cloudflare blocked）。

**實戰案例（2026-05-22）**：
- `kix.dev/blog` — curl 回空（伺服器存在但無內容）
- 多個 GitHub issue 連結已關閉
- arXiv 預印本 URL 指向不再存在的版本

**規則更新**：heartbeat 選單追蹤探索時，`追蹤現有 leads` 的子選項現在包括：
- 對每個「未追蹤」lead 嘗試 curl/fetch
- 成功的 leads → 更新探索筆記為 active
- 失敗的 leads → 標記為 `dead`，附上失敗原因 + 日期

已更新 `heartbeat-v2-autonomous-maintenance` skill。

---

### 2. Proposal + STATUS DONE 但實體檔案不存在（新 bug 模式）

**發現於**：session 0604 發現 `otp_gate.py` 的 proposal 聲稱 35 行實作已完成，但 `ls` 找不到該檔案。

**與既有模式的區別**：
| Pattern | INDEX 有 row | STATUS | 磁碟實體 |
|---------|-------------|--------|---------|
| 已知：INDEX 飄移 | ✅ 有 | 任意 | ❌ 沒有 |
| **新：Status Done 但檔案缺失** | ✅ 有 | DONE | ❌ 沒有 |

**修復方式**：heartbeat 已自動檢測並寫入 issue。
已在 `heartbeat-v2-autonomous-maintenance` 加入 reference `proposal-implementation-file-verification.md`。

---

### 3. 架構趨同：Schema 顯式化（高價值洞察）

`2026-05-23-hermes-architecture-convergence.md` 捕獲兩個 cross-cutting theme：

**Theme 1**：Schema 顯式化是所有系統的必然方向
- Hermes：implicit tool signatures → AgentCore Gateway 集中存取控制
- RAIL：方法以程式碼存在 → manifest.json 顯式聲明
- SAGA：動態 agent 通訊無 access control → 密碼學 token

Hermes 三層 gap：
1. Tool registry 有但無 version/capability metadata
2. Heartbeat decisions 缺 typed structure
3. session_search 回傳純文字無 rank score

**Theme 2**：功能隔離 vs 安全隔離正在合流
- CSS honey-pot（功能隔離）和 AWS Security Box（安全隔離）是同一設計哲學
- Hermes 的 `sanitize_fetch.py` 已在同時做兩件事
- 建議：heartbeat Phase 1 產出 `proposed_tool_sequence[]`，在執行前完整列出 tool names + parameters

---

## 系統狀態摘要

| 檢查項 | 狀態 |
|--------|------|
| 12 cron jobs | ✅ 全部正常 |
| EVOLVE | ⚠️ 1 error（plan drift，7d stale，KI-001） |
| Hearth sync | ✅ inbox 空 |
| 自主研究 | ✅ 穩定運作（SAGA/ACE） |
| 小說抓取 | ⚠️ 3 本卡住（紅樓夢、東周列國誌、儒林外史） |

---

## 待追蹤

- KI-001 briefing-pytest.md plan drift（7d，EVOLVE 已標記）
- 小說 queue 3 本卡住的修復（需手動或外部干預）
- Tool Registry schema 起草（架構 Theme 1 的下一步）
- Heartbeat proposed_tool_sequence（架構 Theme 2 的下一步）