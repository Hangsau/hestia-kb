---
_slug: 40-Resources-_mixed-explorations-2026-06-07-ECC---DeerFlow-探索---2026-06-07
_vault_path: 40-Resources/_mixed/explorations/2026-06-07-ECC---DeerFlow-探索---2026-06-07.md
title: ECC + DeerFlow 探索 — 2026-06-07
date: 2026-06-07
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- affaan
- agent
- deerflow
- ecc
- github
- harness
- hermes
- https
- rust
- talos
created: '2026-06-07'
updated: '2026-06-15'
status: budding
---

# ECC + DeerFlow 探索 — 2026-06-07

**延續自**: 無（新探索）

## Per-Source Insights

### 1. ECC (affaan-m/ECC) — 182k stars
**URL**: https://github.com/affaan-m/ECC

**核心定位**：「harness-native operator system」——不是 config pack，是完整系統：skills、instincts、memory optimization、continuous learning、security scanning。

**與 Hermes/Talos 相關亮點**：
- **Cross-harness**：支援 Claude Code、Codex、Cursor、OpenCode、Gemini、Zed、GitHub Copilot。ECC v2.0.0-rc.1 明確提到 Hermes（`docs/HERMES-SETUP.md`）。這是第一個把 Hermes 當作一等公民的 external 專案。
- **Continuous Learning**：從真實 session 自動萃取 pattern 成 reusable skills。與 `heartbeat_learning.py` 的 distillate 層方向一致，但 ECC 是跨工具的。
- **Instincts**：學習型 pattern collection，有 confidence scoring + import/export。
- **Rust ecc2/ control plane**：alpha prototype，提供 `dashboard/start/sessions/status/stop/resume/daemon` 命令。這與 Talos 的 guardian 角色有共鳴——都是「元控制層」。
- **AgentShield**：security scanning skill，1282 tests、102 rules。CVEs、sandboxing 完整覆蓋。

**架構元素**：
- Agents（63 個 specialized roles）
- Skills（251 個 reusable capabilities）
- Instincts（learned patterns from sessions, confidence-scored）
- Hooks（session lifecycle hooks，memory persistence across sessions）
- Legacy command shims（79 個）
- ECC Tools GitHub App（PR audits, free tier, 150 installs）

**對 Talos 的啟發**：
1. ECC 的「operator」概念比「config」更精確——Talos 的 guardian 角色就是一個 operator，在 Hermes 之上運作。
2. ecc2/ 的 Rust control plane 可能是 WS-035（Policy Engine）的一個參考實作——不只是設 policy，而是真的做出一個 daemonized control layer。
3. Hermes setup guide 在 ECC 文件中（`docs/HERMES-SETUP.md`）——值得一讀，看外部怎麼看 Hermes。

### 2. DeerFlow (bytedance/deer-flow) — 70k stars
**URL**: https://github.com/bytedance/deer-flow

**核心定位**：Super agent harness for long-horizon research，orchestrates sub-agents、memory、sandboxes。

**架構特點**：
- **Sub-agents**：多 agent 協作，每個 sub-agent 有明確職責
- **Sandbox mode**：隔離執行環境
- **InfoQuest**：BytePlus 開發的智慧搜尋+crawl 工具（支援免費線上體驗）
- **LangSmith/Langfuse tracing**：完整 observability
- **MCP Server**：MCP 整合
- **IM Channels**：整合即時通訊

**對 Hermes 的啟發**：
- DeerFlow 的 sub-agent  orchestration 模式與 Hermes 的 multi-agent 架構方向相似
- Sandbox mode 與 `guardian-sandboxing-gradient` 提案一致

## 跨文章 Synthesis

ECC 和 DeerFlow 代表兩種不同的 agent harness 哲學：
- **ECC**：「縱向」——深耕單一生態（所有 harness 都要能跑），強調 continuous learning、cross-harness 可移植性
- **DeerFlow**：「橫向」——深耕 long-horizon research，強調 sub-agent 協作、sandbox、tool integration

**共鳴點**：
1. 兩者都把 memory/instinct 當作一等公民（ECC instincts、DeerFlow memory orchestration）
2. 兩者都有安全層（ECC AgentShield、DeerFlow sandbox）
3. 兩者都支援 MCP——MCP 已成 agent 生態的標準介面

**對 Talos 的具體 action**：
- 讀 `docs/HERMES-SETUP.md`（ECC 文件）看外部對 Hermes 的理解和設定方式
- 評估 ecc2/ Rust control plane 是否可作為 WS-035 policy engine 的實作參考

## Untracked Leads

- https://github.com/affaan-m/ECC/blob/main/docs/HERMES-SETUP.md — ECC 的 Hermes 設定指南
- https://github.com/affaan-m/ECC/blob/main/docs/architecture/cross-harness.md — cross-harness 架構文件
- https://github.com/affaan-m/ECC/tree/main/ecc2 — Rust ecc2/ control plane prototype
- https://deerflow.tech — DeerFlow 官方網站，有即時 demo

## ecc2 Rust Control Plane — 新發現（Phase 2 fetch）

ECC 2.0 的 Rust 控制層（`ecc2/`），是 WS-035 Policy Engine 的具體實作參考：

- **已存在**：SQLite-backed session store、`dashboard/start/stop/resume/daemon` 命令
- **架構**：多 session 追蹤、風險評分原始碼、工作tree-aware scaffolding
- **缺失**：まだ multi-agent delegation、visual diff review、memory integration 不完整
- **對 Talos 的價值**：ECC 作為外部專案已經把「harness 管理面板」做出來了，Talos 不需要從零發明。直接研究 ecc2 的 source 可以得到 WS-035 的實作起點。

**URL**: `https://github.com/affaan-m/ECC/tree/main/ecc2/src` — Rust source 可直接閱讀

## ✅ 本次探索完成
