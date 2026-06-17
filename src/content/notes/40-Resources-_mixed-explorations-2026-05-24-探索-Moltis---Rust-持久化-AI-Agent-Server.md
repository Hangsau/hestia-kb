---
_slug: 40-Resources-_mixed-explorations-2026-05-24-探索-Moltis---Rust-持久化-AI-Agent-Server
_vault_path: 40-Resources/_mixed/explorations/2026-05-24-探索-Moltis---Rust-持久化-AI-Agent-Server.md
title: 探索：Moltis — Rust 持久化 AI Agent Server
date: 2026-05-24
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- extension
- gate
- hermes
- moltis
- org
- otp
- runtime
- rust
- tool
- vault
created: '2026-05-24'
updated: '2026-06-15'
status: budding
---

# 探索：Moltis — Rust 持久化 AI Agent Server

**日期**: 2026-05-24
**來源**: HN Show HN + 官網文件
**類型**: 探索筆記

---

## Per-Source Insight

### Source: https://www.moltis.org (官網 + 技術文件)

Moltis 是一個 Rust 寫的單一二進位 AI agent server，目標場景與 Hermes 直接重疊但架構路線不同。值得深度研究的原因是它解決了 Hermes 目前面對的幾個核心問題（安全沙箱、secret 管理、runtime extension）。

**核心架構特色**:

| 特色 | Hermes 的現況 | Moltis 的做法 |
|------|-------------|-------------|
| 語言 | Python + TypeScript | Rust (270K LoC, 0 npm deps) |
| 安裝 | `curl | sh` 安裝 script | 相同：`curl -fsSL moltis.org/install.sh \| sh` |
| 沙箱 | 個別 tool 許可權 | Docker/Podman/Apple Container/WASM |
| Secret 管理 | 環境變數 + 設定檔 | 加密 vault，記憶體中 zeroed |
| SSRF 保護 | 部分（gateway filter） | 明確 blocking loopback/private/CGNAT |
| Runtime extension | Skill authoring (runtime 可寫) | Pi-inspired self-extension + hot-reload |
| HITL | OTP gate (partial) | 明確 `Human-in-the-loop approval` |
| Memory | SQLite + FTS hybrid | SQLite + FTS + vector hybrid (相同架構) |
| Channels | Telegram only | 15+ channels (Web, Telegram, WhatsApp, Discord, etc.) |
| Hooks | 15 event types | 同樣 15 event types |

**安全模型對比**:
- Moltis: 「AI 不能讀你的檔案、跑命令、或瀏覽網頁，除非你明確允許。每一個 tool action 可以要求你的 approval」
- Hermes: Gateway-level tool filtering + OTP gate for sensitive ops
- 關鍵差異：Moltis 是 filesystem-level sandbox（AI 根本上就不能接觸 host fs），Hermes 是 permission-level（AI 可以接觸 fs 但受限於 tool permissions）

**Encrypted Vault — SAGA OTK Token 的另一種實現**:
- Moltis 的 vault：「API keys 和密碼被包裝，所以永遠不會意外 log 出來，記憶體使用後立刻 zeroed」
- SAGA 的 OTK：密碼學 token，agent 自行 enforcement，不需要每次都找 Provider
- 兩者都解決「secret 不能留在記憶體太久」的問題。Moltis 用加密 + zero；SAGA 用密碼學不可偽造性。**架構上的啟發**：Hermes 的 OTP gate 可以往「加密 vault」方向演進，而不只是簡單的 token verify。

**Runtime self-extension**:
- `Pi-inspired self-extension: creates its own skills at runtime. Session branching, hot-reload`
- 這幾乎是 Hermes skill authoring 的 Rust 版本。session branching 對應 Hermes 的 worktree isolation。
- **重要**：Moltis 的 extension 是「creates its own skills」，不是「uploads plugins」。這是自我改進，不是插件市場。

**Compare table 的價值**:
官網直接放了 OpenClaw / Hermes Agent / Moltis 的三向比較表（見上方）。內容基於公開資訊 + local checkout 測量。對 Hermes 的描述：
- `CLI + gateway + research tools` — 準確
- `Local, Docker, SSH, cloud backends` — 部分準確（SSH backend 不存在）
- `Python and TUI tests` — 測試覆蓋描述正確
- `Telegram, Discord, Slack, WhatsApp, Signal, CLI` — Hermes 只有 Telegram

**不適用的場景**:
- Moltis 沒有 mention MCP 但官網說「MCP server support: stdio + HTTP/SSE」— 有，埋在 feature list
- Voice: Moltis 有內建 15+ provider，Hermes 只有語音轉文字 memo

---

## 跨文章 Synthesis

Moltis 和 Hermes 是同類問題的不同解法。核心差異：

1. **語言哲學**: Rust (安全, 0 runtime dependency) vs Python (彈性, 生態豐富)
2. **沙箱模型**: Moltis 是「filesystem根本上隔離」，Hermes 是「tool permission 分層」
3. **Secret 管理**: Moltis 有加密 vault + memory zeroing，Hermes 還在 OTP gate 階段
4. **Extension 模型**: 兩者都有 runtime self-extension + session branching，但 Moltis 是編譯後 binary 支援，Hermes 是 Python 解釋性 dynamic loading

**對 Hermes 有實質價值的點**:
1. **Encrypted vault for API keys**: Hermes 的 OTP gate 可以往這個方向實作，用加密替代簡單 HMAC
2. **SSRF protection 的明確實作**: Moltis blocks loopback/private/CGNAT，Hermes 的 gateway 應該要做到相同等級
3. **Session branching + hot-reload**: 對應 Hermes 的 worktree isolation 概念，可能可以簡化架構

---

## 未追蹤 Leads

- https://github.com/moltis-org/moltis — GitHub repo（需要看 source code 才知道 vault 實作）
- https://www.moltis.org/security — 詳細 security model
- https://www.moltis.org/install.sh — 安裝 script 看實質安裝內容

---

## ✅ 本次探索完成

**探索時間**: 2026-05-24 08:35 UTC
**發現品質**: 高 — 直接可比較的競品，架構文件完整，security model 有深度
