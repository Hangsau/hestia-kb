---
_slug: 10-Daily-2026-05-15-agents-md-research
_vault_path: 10-Daily/2026-05-15-agents-md-research.md
tags:
- hermes
- research
- system-map
- agents.md
- community
source: session_20260514_222314_b53b44
created: '2026-05-15'
title: AGENTS.md / CLAUDE.md 社群實踐研究
updated: '2026-06-15'
type: daily
status: budding
---

# AGENTS.md / CLAUDE.md 社群實踐研究

Hang 主動要求的調研：AI agent 系統地圖與架構文件的社群最佳實踐。

## 核心發現

### 1. AGENTS.md / CLAUDE.md 慣例

這是 AI coding agent（Claude Code, Cursor, Codex）進入 repo 後自動載入的**專案層級 context 文件**。主流範式：

- **CLAUDE.md = "repo memory"**，不是知識傾倒。保持 50 行以內：目的、目錄結構地圖、工作規則。細節透過 `@` 引用連結。
- **coder/coder** 模式：root CLAUDE.md（~100 行）→ `@.claude/docs/ARCHITECTURE.md`、`@.claude/docs/WORKFLOWS.md`
- **Chief-Mischief-Maker** 的 10 原則：`CLAUDE.md` (root memory) → `docs/architecture.md` → `docs/decisions/` (ADR) → `docs/runbooks/` → 敏感目錄的 local `CLAUDE.md`

### 2. AI-Native 專案地圖工具

| 工具 | 用途 |
|------|------|
| **RepoPrompt** | 整個 repo → 單一 prompt |
| **RepoMix** | Repomix 的 fork，合併 prompt |
| **RepoQuery** | 語意查詢 repo |
| **context7** | 程式庫層級 context |

### 3. 最佳實踐

Root `CLAUDE.md` = 地圖 + 規則。Linked `docs/architecture.md` = 詳細系統描述。

**這正好是我們 System Map Generator 做的事** — 自動產生的 AGENTS.md + maps/ 結構就是這個模式。

## 相關筆記

- [[2026-05-15-skill-code-gap]]
- [[Heartbeat v2 架構驗證]]
