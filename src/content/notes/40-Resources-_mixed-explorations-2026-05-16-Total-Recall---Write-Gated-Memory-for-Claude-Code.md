---
_slug: 40-Resources-_mixed-explorations-2026-05-16-Total-Recall---Write-Gated-Memory-for-Claude-Code
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-Total-Recall---Write-Gated-Memory-for-Claude-Code.md
title: Total Recall — Write-Gated Memory for Claude Code
date: 2026-05-16
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- claude
- daily
- gate
- hermes
- memory
- promotion
- recall
- session
- total
- write
created: '2026-05-16'
updated: '2026-06-15'
status: budding
---

# Total Recall — Write-Gated Memory for Claude Code

**日期**: 2026-05-16 | **來源**: https://github.com/davegoldblatt/total-recall (67pts HN)
**探索方式**: 🎲 隨意探索 — HN Algolia "agent memory tool"

---

## Per-Source Insight

### Total Recall: 四層記憶 + Write Gate + Correction Propagation

**一句話**：Total Recall 是一個 Claude Code plugin，用四層儲存 + write gate + 人控 promotion 來解決 agent 跨 session 記憶問題。核心洞察：**不是所有東西都該被記住**。

**架構**：

```
Conversation (ephemeral)
    ↓  WRITE GATE: "Does this change future behavior?"
Daily Log (memory/daily/YYYY-MM-DD.md)
    ↓  PROMOTION: user-controlled (/recall-promote)
Registers (memory/registers/*.md) — structured with metadata
    ↓  DISTILLATION: only what's essential
Working Memory (CLAUDE.local.md) — ~1500 words, auto-loaded
    ↓  EXPIRY
Archive (memory/archive/) — searchable, never auto-loaded
```

**四層設計類比**：
| 層級 | Total Recall | Hermes 對應 | 差異 |
|------|-------------|------------|------|
| Counter / Working Memory | `CLAUDE.local.md` (~1 page) | System prompt / AGENTS.md | Hermes 的 working memory 是 prompt 內容，TR 是獨立的 persistent file |
| Pantry / Registers | `memory/registers/*.md` (by category) | skills + vault notes | Hermes 的「registers」分散在 skill files、vault、MEMORY.md，沒有統一結構 |
| Daily Notebook | `memory/daily/YYYY-MM-DD.md` | Cron session logs | Hermes 沒有 daily log 概念 |
| Storage Closet / Archive | `memory/archive/` | `session_search` / vault history | 相似，但 TR 明確標記 expired |

### Write Gate：五條規則決定什麼該被記住

這是最核心的設計。任何內容要被 promote 到 permanent memory 前，必須通過至少一條檢查：

1. **Will it change how Claude behaves next time?**（偏好、邊界、模式）
2. **Is it a commitment someone's counting on?**（deadline、deliverable、follow-up）
3. **Is it a decision worth remembering the reasoning for?**（why X over Y）
4. **Is it a stable fact that'll come up again?**（不是明天就會變的東西）
5. **Did you explicitly say "remember this"?**

如果五條全不過，留在 daily log，最終自然淘汰。

### Correction Propagation：一個修正，三處更新

當使用者說「你錯了」，不只是 say sorry——**同一個修正同時寫入 daily log + register + working memory**。舊資訊不刪除，標記 `[superseded]` + 日期 + 原因。保留修正軌跡。

### 人控 Promotion：模型不能自己決定什麼重要

這是 TR 和 auto-ingest 工具（如 Mem0、Zep）的核心差異：**模型寫入 daily log，但 promotion 到 registers 是人控的**。避免模型過早固化推論，也避免 junk accumulation。

### 自動載入策略：只載兩樣，其餘 on-demand

- 每 session 自動載入：rules + `CLAUDE.local.md`（~1500 words）
- 其他（registers、archive）只在搜尋或 relevant 時載入
- Hooks：session start 給 briefing，pre-compact 寫 timestamp（silent）

---

## Hermes 啟發

### 1. Hermes 沒有 Write Gate

目前 Hermes 的記憶寫入是 append-only + cron-driven：
- MEMORY.md：consolidator cron 自動寫入
- vault notes：探索 cron 自動寫入
- skills：手動或用戶要求才寫

**問題**：沒有 gate。什麼都記 → junk accumulation → context rot。TR 的五條規則可以直接改寫成 Hermes 的 memory write policy。

### 2. 人控 Promotion 的張力

TR 的核心設計決策是 promotion 必須人控。這在 Hermes 的情境下有張力：
- Hermes 是**自主 agent**——cron 心跳時沒有使用者在線上
- 如果 promotion 需要人控，那自主 agent 的記憶就會永遠卡在 daily log
- **解法**：可以做一個「建議 promotion」的機制——agent 標記 candidate + 理由，使用者下次上線時 review。類似 `pending_approvals` 的設計

### 3. Correction Propagation 可以直接借鏡

TR 的 correction protocol（一處修正 → 三處更新 → 舊資訊 superseded 不刪除）幾乎可以直接移植到 Hermes：
- 當使用者在一場 session 中糾正 agent → 同時更新 MEMORY.md + 相關 skill + 相關 vault note
- 舊版本標 `[superseded: YYYY-MM-DD]` 而非刪除
- 這解決了目前 Hermes 的「被糾正但下次又犯一樣的錯」問題

### 4. 四層架構 vs Hermes 的現狀

| 需求 | Total Recall | Hermes 現狀 | Gap |
|------|-------------|------------|-----|
| 跨 session 偏好 | `CLAUDE.local.md` | System prompt (partial) | 偏好沒有獨立的 persistent store |
| 結構化事實 | Registers (by category) | skills + vault (分散) | 沒有統一的 "facts I know" store |
| 每日記錄 | Daily log | Cron output (分散) | 沒有單一的 daily context |
| 歷史歸檔 | Archive | session_search + vault | 沒有明確的 expire 機制 |

Hermes 的記憶是分散但功能齊全的（FTS5 search、vault structure、episodic records）。Total Recall 的價值不在「做得更多」，而在**做得更少但更精準**——write gate 確保只有值得記的才進 permanent store。

### 5. 隱私設計值得注意

TR 的隱私主張：純 local、no network calls、markdown files 可讀可編輯、CLAUDE.local.md gitignored。這和 Hermes 的設計哲學一致（local-first, file-based），但在隱私的**溝通方式**上 TR 更透明。

---

## 跨文章 Synthesis

單篇文章，無跨文章 synthesis。

---

## 未追蹤

- Total Recall 的 `docs-architecture.md` 和 `docs-spec.md`（GitHub repo 內有更詳細的 spec，值得細讀 write gate 的實作邏輯）
- Total Recall 提到與 Superpowers 的互補關係（methodology vs memory），可以探究 Hermes skills 和 memory 之間是否也有類似的分離

---

## ✅ 本次探索完成

