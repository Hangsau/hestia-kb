---
_slug: 40-Resources-_mixed-research-agent-openclaw-vs-hermes
_vault_path: 40-Resources/_mixed/research/agent/openclaw-vs-hermes.md
tags:
- research
- openclaw
- hermes
- architecture
- comparison
source: session_20260512_213501
source_url: https://github.com/openclaw/openclaw
created: '2026-05-12'
title: OpenClaw vs Hermes Agent
updated: '2026-06-15'
type: research
status: budding
---

# OpenClaw vs Hermes Agent

> 完整報告見 `~/research/openclaw-vs-hermes/reports/2026-05-12-openclaw-vs-hermes.md`（21KB，526行）

## 執行摘要

- **OpenClaw** = Node.js/TypeScript Gateway-centric 架構，強調「個人化」與「多頻道」，是一個完整的「個人助理」產品。
- **Hermes Agent** = Python CLI-centric 架構，強調「工具化」與「可程式化」，是一個「智能代理框架」。
- **關係**: 不是替代，而是「產品 vs 框架」「前端 vs 後端」。最佳整合策略：**Hermes 做主控（orchestrator），OpenClaw 做 Gateway + Channel 層**。

## OpenClaw 架構要點

| 模組 | 實現 | 備註 |
|------|------|------|
| Gateway | Express + WebSocket | 綁定 `127.0.0.1:18789`，一個 host 只能有一個 Gateway |
| Agent Loop | intake → context → inference → tool → stream → persist | 串行化 per session key，60s timeout |
| Skills | AgentSkills-compatible YAML frontmatter + Markdown | 6 級載入順序（workspace → personal → bundled → extra） |
| Memory | SQLite per agent + FTS5 + Vector search | ~400 tokens/chunk，自動重索引（1.5s debounce） |
| Bootstrap | AGENTS.md / SOUL.md / TOOLS.md / BOOTSTRAP.md / IDENTITY.md / USER.md | 注入 system prompt |
| Channels | 20+ 平台（WhatsApp, Telegram, Slack, Discord, iMessage, WeChat, QQ...） | DM pairing 模式 |
| Sandbox | Docker / SSH / OpenShell | 非 main session 可用，預設白名單 |
| 特色 | Canvas, Voice wake word, Companion apps, Node system | headless/行動設備提供 camera/screen/location |

## Hermes 架構要點（對比）

| 維度 | Hermes | OpenClaw |
|------|--------|----------|
| 語言 | Python | TypeScript/Node.js |
| 入口 | CLI + cron | Gateway daemon + CLI |
| 記憶 | MEMORY.md（2,200 char 上限）+ session JSON | SQLite + FTS5 + Vector（無上限） |
| Skills | YAML frontmatter + Markdown，載入時注入 prompt | 同樣格式，但載入順序更細緻 |
| Channels | Telegram（內建）+ webhook | 20+（內建） |
| Sandbox | Docker + SSH | Docker + SSH + OpenShell |
| Multi-agent | `delegate_task` + sub-agent | 單一 agent per Gateway |
| 設計哲學 | 框架 / 可程式化 | 產品 / 個人助理 |

## 五階段整合方案

1. **共存安裝**: 各跑各的 daemon，避免 port/resource 衝突
2. **CLI 委派**: Hermes `terminal` 呼叫 `openclaw agent --message "..."`
3. **Memory 共享**: 符號連結 `~/.hermes/memory_*.md` → `~/.openclaw/memory/`
4. **Skills 互通**: 直接複製（格式相容）
5. **Channel 中繼**: OpenClaw 收訊息 → 共享佇列 → Hermes 處理 → OpenClaw 回覆

## 風險

- Node.js 24 依賴
- 雙 daemon 資源競爭
- Config 雙邊同步
- YOLO 模式 + sandbox 邊界協調
- API 快速變動

## 關鍵見解

1. OpenClaw 的 Gateway 是單點控制平面，適合做「對外窗口」；Hermes 的 CLI/cron 適合做「後台編排」。
2. Skills 格式幾乎完全一致（YAML frontmatter + Markdown），互通成本極低。
3. Memory 後端差異最大：Hermes 是靜態注入，OpenClaw 是動態索引。符號連結是最懶的橋接方式。
4. 若只需要「多平台發訊息」，Phase 2（CLI 委派）就夠了；若要「雙向互動」，才需要 Phase 5（Channel 中繼）。
5. 類比：**Hermes = Kubernetes，OpenClaw = Docker** — 一個編排，一個容器。

## 參見

- [[project-map-index]] — 專案總索引
- [[skills-map]] — 技能庫總覽
