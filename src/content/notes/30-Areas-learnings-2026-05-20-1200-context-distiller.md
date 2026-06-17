---
_slug: 30-Areas-learnings-2026-05-20-1200-context-distiller
_vault_path: 30-Areas/learnings/2026-05-20-1200-context-distiller.md
title: Context Distiller 2026-05-20 12:00
date: 2026-05-20 12:00:00+08:00
tags:
- learnings
- context-distiller
- archive
source: session_review
created: '2026-05-20'
updated: '2026-06-15'
type: learning
status: budding
---

# Context Distiller 複習：2026-05-20 12:00

## 複習範圍

回顧了 06:45–08:07 的 5 個互動 session，均為 Telegram 來源的 multi-agent 研究工作。

## 發現

### 新建立的研究資料夾（已上 GitHub）

[[40-Resources/_mixed/research/hermes-cross-machine-agents]] 已建立，涵蓋：
- 跨機器通訊協定比較（HTTP/WebSocket/MQTT/檔案交換）
- 檔案協調機制（MCP Agent Mail、Swarm-MCP、Fleet）
- 生產部署案例（CrewAI、AutoGen、LangGraph、MCP）+ 失敗模式
- 核心結論：**INBOX.md + advisory reservation** 是最實用的跨 agent 協調模式

上傳至 `Hangsau/managed-agents-research/research/hermes-cross-machine-agents/`

### archive/ 整理

[[20-Projects/hestia/archive]] 收納了 14 個過期檔案：
- 5 個舊 context-distiller 回顧
- 8 個記憶系統探索（Orloj/Axe/R2-Mem/Aegis）
- 2 個舊探索（AutoAgents-Rust、MCP-Server pipeline）
- gateway-crash-loop incident report

### 環境狀態

- vault 路徑確認在 `~/obsidian-vault/`（非 `~/.hermes/vault/`）
- 資料庫：sessions 在 `~/.hermes/state.db`（非 `hermes_sessions.db`）
- 三個 cron agent 持續運行（b48ea41a/c27c167b/a89f6965，每 30 分鐘）

## 無需长期记住

- session 標題皆為空（`title=''`），沒有人工命名
- 兩個 research agent session（sympozium/phodal）在克隆 repo，但尚未完成分析
