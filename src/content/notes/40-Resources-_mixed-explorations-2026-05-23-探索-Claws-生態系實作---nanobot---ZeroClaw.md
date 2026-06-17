---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-Claws-生態系實作---nanobot---ZeroClaw
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-Claws-生態系實作---nanobot---ZeroClaw.md
title: 探索：Claws 生態系實作 — nanobot & ZeroClaw
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- clawhub
- claws
- engine
- hermes
- nanobot
- security
- sop
- tool
- zeroclaw
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索：Claws 生態系實作 — nanobot & ZeroClaw

**日期**: 2026-05-23
**延續自**: [[2026-05-23-llm-agent-failure-modes-and-claws-layer]]

**來源**:
- HKUDS/nanobot (43k stars) — Python, ultra-lightweight agent
- zeroclaw-labs/zeroclaw (31k stars) — Rust, security-first agent runtime

## Per-source Insights

### HKUDS/nanobot (43k stars, 2026-02 ~ present, v0.2.0 released 2026-05-15)

Python 實現，刻意維持小核心（~4000 LOC 可讀），從 OpenClaw/Claude Code/Codex 精神繼承。架構哲學：messages in → LLM decides tools → memory/skills as context → 不變成 orchestration 怪物。

**核心組件**:
- `/goal` — 跨 turn 維持長期目標（v0.2.0 新增）
- `Dream` — 兩階段記憶系統（v0.1.5 引入，最近重設計）
- MCP 整合（v0.1.4, 2026-02）
- ClawHub skill 整合（v0.1.4.post1, 2026-02）
- 多 channel: Telegram/Discord/WeChat/Feishu/WhatsApp/Matrix/QQ/Feishu
- WebUI 內建于 wheel package（v0.2.0 新增）
- `nanobot onboard` 互動式引導設定（類似 Hermes initial setup）
- streaming reasoning（visible CoT）

**開發節奏**: 每 1-3 天一個 patch 版本，fast-moving。說「research-ready codebase intended to study, modify, and extend」——直接和 nanoclaw 的「~4000 LOC, auditable by both humans and AI agents」口徑一致。

**Hermes 啟發**: nanobot 的 `/goal` 相當於 Hermes 的 task persistence——跨 session 維持意圖。但 Hermes 是被動架構（heartbeat 補資訊），nanobot 是主動架構（agent 自己追蹤 goal）。這個對比對 WS-024（heartbeat learning rubric）有意義：rubric 可以評估 agent 是否有 goal-tracking behavior。

**對 Claws 層的直接貢獻**: ClawHub 整合（nanobot 已經可以 search + install public agent skills）。這代表 Claws 層已有 marketplace 雛形。

### zeroclaw-labs/zeroclaw (31k stars)

Rust 單一二進制 (~6.6 MB minimal)，聲明式安全。架構三分：agent loop / security policy / SOP engine。

**最值得注意的設計**:
- **Tool receipts** — 每個 action 都產生密碼學 receipt（audit trail 不只是 log，是 cryptographic proof）。zero-trust tool execution model。
- **安全預設**: `supervised` 模式（medium-risk 需 approval，high-risk blocked）。`YOLO mode` 只在 trust dev box。
- **OS-level sandbox**: Landlock/Bubblewrap/Seatbelt/Docker
- **SOP engine**: MQTT/webhook/cron/peripheral 觸發的 Standard Operating Procedures，with approval gates + resumable runs
- **Hardware capability**: GPIO/I2C/SPI on Raspberry Pi, STM32, Arduino, ESP32
- **Multi-channel**: 30+ channel adapters（Discord/Telegram/Matrix/email/voice/webhooks/CLI）
- **ACP (Agent Client Protocol)**: JSON-RPC 2.0 over stdio — IDE/editor integration

**Architecture diagram**（從 README 擷取）:
```
channels (30+ adapters)  gateway (REST/WS)  ACP (JSON-RPC)
           ↓
     ZeroClaw runtime
  ┌──────────┬──────────┬──────────┐
  │  agent   │ security │   SOP    │
  │   loop   │  policy  │  engine  │
  └──────────┴──────────┴──────────┘
       ↓          ↓           ↓
   providers    tools      memory
```

**Hermes 啟發**: 
1. **Tool receipts** — Hermes 的 heartbeat action log 已經是 audit trail，但缺少 cryptographic integrity。可以提案：heartbeat action log → signed JSON（每 entry 用 HMAC-SHA256 簽名，防事後篡改）。
2. **SOP engine** — zeroclaw 的 SOP 是 event-triggered workflow。Hermes 的 heartbeat cronjobs 也是一種 SOP，但目前是靜態排程沒有 event-triggered 能力。
3. **Rust binary distribution** — zeroclaw 的 `curl | bash` install + prebuilt binary 模式，vs nanobot 的 `uv tool install` / `pip install`。Hermes 目前是 Python，不過這個取決於底層架構。

## 跨文章 Synthesis

nanobot 和 zeroclaw 代表 Claws 層的兩條路徑：

| | nanobot | zeroclaw |
|--|---------|----------|
| 語言 | Python | Rust |
| 分發 | PyPI/uv/wheel | curl\|bash + prebuilt binary |
| 安全模型 | permissive（可選 shell allow-list） | supervise by default, tool receipts |
| 擴展方式 | plugin / MCP / channel adapter | channel adapters + SOP engine |
| 開發節奏 | 瘋狂快速（daily patches） | 穩定 release |
| 目標用戶 | 研究者、hacker | 注重安全的一般用戶 |

兩者都實作了 Claw 的核心定義：orchestration + scheduling + persistence + context management。它們之間的差異正好對應 Hermes 內部的 tension——Talos（zeroclaw 風格，security-first）vs Hestia（nanobot 風格，explore-first）。

**一個值得追的線**: Claws 層的 marketplace（ClawHub）已經存在且有實作。如果 Hermes 想升級成 Claw-level agent，ClawHub skill sharing 機制是捷徑——不需要自己發明 skill registry，把 ClawHub 當成外部 dependency。

## 未追蹤 Leads

- ZeroClaw architecture 詳細文件 — https://zeroclaw.dev/book/src/architecture/overview.md
- nanobot v0.2.0 release notes — https://github.com/HKUDS/nanobot/releases/tag/v0.2.0
- ClawHub skill registry — https://clawhub.ai
- ZeroClaw tool receipts 實作 — https://zeroclaw.dev/book/src/security/tool-receipts.md
- zeroclaw SOP engine — https://zeroclaw.dev/book/src/sop/index.md

## ✅ 本次探索完成
