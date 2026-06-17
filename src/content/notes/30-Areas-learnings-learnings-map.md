---
_slug: 30-Areas-learnings-learnings-map
_vault_path: 30-Areas/learnings/learnings-map.md
tags:
- learnings
- index
- map
updated: '2026-05-27'
fingerprint_version: 1
title: 學習地圖
created: '2026-05-13'
type: learning
status: budding
---

# 學習地圖

> 全自動維護。每個 topic 一個檔案，新發現自動 append 為新版本區塊。
> 指紋用於去重：新學習進來 → 提取關鍵詞 → 比對既有指紋 → Jaccard > 0.5 = 同一主題。

## 索引

| Topic | File | Versions | Fingerprint | First Seen | Last Updated |
|-------|------|----------|-------------|------------|--------------|
| Cron Scheduler 可觀測性 | [[cron-scheduler-observability]] | 1 | cron, ticker, backpressure, observability, silent-failure, action-run | 2026-05-13 | 2026-05-13 |
| Cron One-Shot Restart Loop Fix | [[cron-one-shot-restart-loop-fix]] | 1 | cron, one-shot, completion-state, restart-loop, gateway-restart, attempted-at, systemd-working-directory | 2026-05-17 | 2026-05-17 |
| Heartbeat Pending Thread Discovery | [[heartbeat-pending-thread-discovery]] | 1 | heartbeat, pending-thread, reply-expected, cross-agent, discovery-timestamp | 2026-05-17 | 2026-05-17 |
| Forge/Preflight 弱模型補償機制 | [[2026-05-23-1600-context-distiller]] | 1 | forge, preflight, validate, iteration_state, triage, stagnation, weak-model, scaffolding | 2026-05-23 | 2026-05-23 |
| Hermes M6 系統缺口 | [[2026-05-23-1600-context-distiller]] | 1 | hermes-gaps, M6, heartbeat, subagent-traceability, looptrap, token-budget, bm25, architect-executive | 2026-05-23 | 2026-05-23 |
| Psyche AIAgent Expertise + Session Integrity | [[2026-05-27-Psyche-AIAgent-Expertise-Session-Integrity]] | 1 | psyhe, session-integrity, source-of-truth, hermes-architecture, self-awareness | 2026-05-27 | 2026-05-27 |

## 去重規則

- **自動建立**：新學習與所有既有指紋 Jaccard < 0.4 → 新建 topic
- **自動合併**：Jaccard ≥ 0.5 → 附加為既有 topic 的新版本區塊
- **詢問用戶**：0.4–0.5 灰色地帶無法判斷 → 中斷詢問

## 相關

- [[project-map-index]] — 專案總索引
- [[skills-map]] — 技能地圖
