---
_slug: 40-Resources-_mixed-research-agent-hermes-agent-framework
_vault_path: 40-Resources/_mixed/research/agent/hermes-agent-framework.md
tags:
- hermes
- framework
- reference
- architecture
source: multi
created: '2026-05-12'
title: Hermes Agent Framework
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Agent Framework

> The agent framework running this conversation.

## 基本資訊

| 項目 | 值 |
|------|-----|
| 開發者 | Nous Research |
| 語言 | Python |
| 入口 | CLI + cron + Telegram gateway |
| 安裝位置 | System install |
| 配置檔 | `~/.hermes/config.yaml` |
| 記憶檔 | `~/.hermes/memories/MEMORY.md` (2,200 char 上限) |
| 使用者檔 | `~/.hermes/memories/USER.md` (1,375 char 上限) |
| 技能庫 | `~/.hermes/skills/` |
| 工作區 | `~/.hermes/sessions/` |

## 核心特性

- **CLI-centric**: 命令行首先，所有功能透過 `hermes` 指令控制
- **Cron 支援**: 內建 cron 系統，可排程定時任務
- **Multi-agent**: `delegate_task` 委派子 agent
- **Skills 系統**: YAML frontmatter + Markdown，載入時注入 system prompt
- **MCP 整合**: 支援 Model Context Protocol servers
- **YOLO 模式**: 可設定自動執行而無需確認

## 與 OpenClaw 的關係

- Hermes = 編排器（orchestrator）
- OpenClaw = 容器（Gateway + Channel 層）
- 整合方案見 [[openclaw-vs-hermes]]

## 參見

- [[project-map-index]] — 專案總索引
- [[openclaw-vs-hermes]] — 與 OpenClaw 的對比整合方案
