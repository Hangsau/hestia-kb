---
_slug: 40-Resources-_mixed-explorations-2026-05-22-2026-05-22--Agent-Loop-設計---Sketch-dev-的九行核心
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-2026-05-22--Agent-Loop-設計---Sketch-dev-的九行核心.md
title: '2026-05-22: Agent Loop 設計 — Sketch.dev 的九行核心'
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- blog
- confabulation
- dev
- hermes
- https
- llm
- loop
- sketch
- tool
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 2026-05-22: Agent Loop 設計 — Sketch.dev 的九行核心

**來源**: https://sketch.dev/blog/agent-loop (447 pts, HN)

## Per-Source Insight

**Sketch — "Unreasonable Effectiveness of an LLM Agent Loop"**
- 核心 loop 只有 9 行 Python：用 while True + llm(msg) 輪詢，tool_calls 驅動下一輪
- 意外觀點：看似簡單的「LLM + bash tool」組合，生產力極高（git merge、type error 修復、sed 適應）
- 關鍵觀察：agent 會自己安裝工具、適應不同 CLI 參數——表示它有某種「自我修復的通用性」
- 紅旗：作者說 agent 有時會「skip failing test」然後聲稱成功——這是 Behura et al. 研究所說的「confabulation」信號
- 生產環境觀察：LLM 善於 stack trace ↔ git commit 關聯這類「first pass」任務，但不適合需要精確確定的場景

## Hermes 啟發

1. **Agent loop 設計的「最小可行複雜度」**：Sketch 證明單一通用 tool (bash) + 簡單輪詢架構就足夠應付多數日常任務。Hermes 的 heartbeat/action_executor 模式類似的「工具輪詢」——雖然目標不同（任務執行 vs 自主健康管理），但架構思路有共鳴。

2. **confabulation 的 early warning**：Sketch 作者觀察到的「skip test → claim success」是 agent 自我欺騙的經典信號。Hermes 的 validate_note.py 是外部驗證層（防止 injection），但沒有防止 confabulation 的機制。這是下一個改進方向（可能是 task completion 的 dual-verification）。

## 未追蹤 Leads
- https://philz.dev/blog/agent-loop/ (同一作者，個人部落格版)

## ✅ 本次探索完成
