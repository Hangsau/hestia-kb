---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Google-Scion---Multi-Agent-Orchestration-Testbed
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Google-Scion---Multi-Agent-Orchestration-Testbed.md
title: Google Scion — Multi-Agent Orchestration Testbed
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- claude
- container
- google
- harness
- hermes
- isolation
- orchestration
- scion
- worktree
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Google Scion — Multi-Agent Orchestration Testbed

**日期**: 2026-05-15 | **來源**: HN (230 pts, 62 comments) + InfoQ + GitHub README
**Repo**: https://github.com/GoogleCloudPlatform/scion (1522⭐, Go, Apache 2.0)
**創建**: 2026-03-10

## 一句話摘要

Google 的「agent hypervisor」——在 container 內跑多個 deep agent（Claude Code / Gemini CLI / Codex），每個 agent 有自己的 container + git worktree + credentials，透過 tmux 生命週期管理。

## 核心設計

| 概念 | 說明 |
|------|------|
| **Agent** | Container 化的 deep agent process |
| **Harness** | Agent adapter — 管理生命週期、認證、配置（Gemini CLI, Claude Code, OpenCode, Codex） |
| **Project** | 專案命名空間，通常 1:1 對應 git repo |
| **Template** | Agent 藍圖 — system prompt + skills 集合 |
| **Runtime** | Docker / Podman / Apple Container / K8s |
| **Hub** | 多機 orchestration 的中央控制平面（可選） |
| **Runtime Broker** | 提供 runtime 給 Hub 的機器 |

## 設計哲學

> **Isolation over constraints** — 不在 prompt 層限制 agent 行為，而是在 infrastructure 層設邊界。Agent 在 container 內跑 --yolo mode，network policy / container boundary 做 guardrail。

這和 Hermes 的 worktree isolation 是同一個思路，但 Scion 往上多了一層 container（network isolation + credential separation）。

## HN 討論精華

1. **Gastown 比較** — 更成熟但只支援 Claude、昂貴。Scion 早期但 harness-agnostic。
2. **Optio** — 另一 agent orchestration 平台，專注 ticketing system integration（Linear/Jira/GitHub Issues），k8s-native。Scion 則自己重建 control plane。
3. **ARIA** (aria-ir.org) — AI-authored code 的中間表示（IR），在 compile-time 做 constraint（宣告 effect、intent annotation、memory safety）。和 Scion 互補：Scion 管「agent 能碰什麼」，ARIA 管「agent 產出什麼」。
4. **Cascading failures** — 多 agent 狀態衝突是 underrepresented 的 failure mode。單一 agent 行為正確但互動後集體錯誤。
5. **Google 碎片化問題** — ADK、gemini-cli、antigravity、AI Studio、Scion... 五個方向各自為政。產品取消風險高。

## 與 Hermes 的對比

| 維度 | Hermes (現狀) | Scion |
|------|-------------|-------|
| Isolation | Git worktree 檔案層 | Container + worktree + network policy |
| Agent 支援 | delegate_task (OpenCode/Claude Code/Codex) | Harness abstraction (Gemini/Claude/Codex/OpenCode) |
| 生命週期 | subprocess | tmux session (attach/detach) |
| 多機 | 無 | Hub/Broker 架構 |
| 可觀測性 | heartbeat logging | OTEL telemetry |
| 成熟度 | 自用穩定 | 早期實驗性 |

## 值得追蹤的點

- **Harness abstraction** — 如果 Hermes 要支援更多 agent backend，可以參考 Scion 的 harness 設計
- **Container 隔離** — 目前 Hermes 用 worktree 已經夠用，但如果要跑更不受信任的 agent，container 是合理下一層
- **多機 orchestration** — Hub/Broker 概念可能對 distributed agent 場景有用，但 Hermes 目前單機就夠了
- **Cascading failure 測試** — 這是 Hermes heartbeat 目前沒測到的：多 agent 並行時的互動錯誤

## 結論

Scion 的設計哲學和 Hermes 高度一致（isolation > constraints），但實作層次更高（container vs worktree）。目前對 Hermes 的直接可用性有限——worktree 對單機開發已經足夠——但 harness abstraction 和 OTEL telemetry 是兩個可以借鏡的設計 pattern。Google 內部的碎片化也提醒我們：不要什麼都做，一個自洽的架構比五個半成品有價值。

