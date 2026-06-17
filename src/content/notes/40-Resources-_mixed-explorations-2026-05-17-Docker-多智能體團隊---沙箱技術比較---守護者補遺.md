---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-多智能體團隊---沙箱技術比較---守護者補遺
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-多智能體團隊---沙箱技術比較---守護者補遺.md
title: Docker 多智能體團隊 + 沙箱技術比較 — 守護者補遺
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- container
- docker
- governance
- hermes
- microvm
- network
- sandbox
- sandboxes
- sandboxing
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker 多智能體團隊 + 沙箱技術比較 — 守護者補遺

**延續自**: [[2026-05-17-docker-sandboxing-landscape]]
**日期**: 2026-05-17 01:45 CST
**標籤**: #sandboxing #microvm #multi-agent #docker #agent-governance

## Per-Source Insights

### 1. Building AI Teams with Docker Sandboxes & Docker Agent (Mar 11, 2026)

- **來源**: https://www.docker.com/blog/building-ai-teams-docker-sandboxes-agent/
- **作者**: Esteban Maya Cadavid, Marco Franzon

**Docker Agent 架構**：YAML-based 多智能體團隊定義。
- 每個 agent 五個屬性：`model`（可混用不同 provider）、`description`、`instruction`、`sub_agents`（團隊階層）、`toolsets`（filesystem / shell / think / todo / memory / MCP）
- Root agent 當 PM：需求拆分 → 委派 designer → engineer → QA → fixer
- 開源（agent repo），從 Docker Desktop 4.49+ 內建

**Docker Sandboxes 安全模型**（Docker Desktop 4.60+）：
- MicroVM-based isolation（非傳統 container）
- 掛載 project dir 在同一個 absolute path（Linux/macOS）
- **不繼承 host env vars**（關鍵安全特性）
- Network isolation + allow/deny lists
- 支援六種 agent type natively：Claude Code, Gemini, Codex, Copilot, Agent, Kiro

**Hermes 啟發**：
- Docker Agent 的 YAML agent 定義方式比 Hermes 的 personality skill 更結構化（model/instruction/toolsets 欄位化）。Hermes 用 markdown SKILL.md 寫 personality，彈性高但缺少 schema validation
- **不繼承 env vars** 的設計值得注意——Hermes 的 terminal tool 目前繼承 host env，若探索 agent 跑在 sandbox 內這是必要防線
- "Agent 團隊" 概念對 Hermes 有意義：Talos 守護 + Hestia 探索，已有雛形

### 2. Comparing Sandboxing Approaches for AI Agents (May 7, 2026)

- **來源**: https://www.docker.com/blog/comparing-sandboxing-approaches-ai-agents/
- **作者**: Siri Varma Vegiraju (Docker Captain)

**五種隔離方案系統性比較**：

| 方案 | 隔離強度 | 啟動時間 | 跨平台 | Per-agent 成本 |
|------|---------|---------|--------|---------------|
| chroot | 弱（僅檔案，root 可逃脫） | instant | Linux only | ~1MB RAM |
| systemd-nspawn | 中（檔案+網路+程序） | <1s | Linux only | ~10MB RAM |
| Docker containers | 中（共享 kernel，DinD 需 privileged） | ms | ✅ | — |
| VMs (Lima) | 強（dedicated kernel） | 30-60s | ✅ | ~4GB RAM + 4 CPU |
| **MicroVM (Docker Sandbox)** | **強（dedicated kernel）** | **秒級** | ✅ | **輕量** |
| gVisor | 中-強（user-space kernel） | ms | Linux only | — |

**Docker Sandbox 三層隔離架構**（之前筆記未覆蓋的細節）：

1. **Hypervisor Isolation**：每個 sandbox 有自己的 Linux Kernel。Guest kernel 被攻破不影響 host 或其他 sandbox。
2. **Network Isolation**：每個 sandbox 獨立 network stack。Sandbox 之間無法通訊。Network policies 控制出入口。
3. **Docker Engine Isolation** ⭐：每個 sandbox 有自己的 Docker Engine daemon。`docker pull` / `docker compose` 只影響 sandbox 內部，看不到 host 的 container。**這是 container-in-container 問題的解法**——不靠 privileged mode，而是每個 sandbox 自帶獨立 engine。

**Container-in-container 困境**：
- Agent 需要 build/run containers → Docker-in-Docker
- 傳統解法：`--privileged` flag → 隔離被大幅削弱
- Docker Sandbox 解法：per-sandbox Docker Engine → 無需 privileged mode

**Hermes 啟發**：
- 三層隔離架構對標 Hestia 的 L1/L2/L3 sandboxing gradient：
  - L1 (Tool Scoping) ↔ 不需 sandbox
  - L2 (Container) ↔ Docker containers（但 DinD 問題待解）
  - L3 (MicroVM) ↔ Docker Sandbox microVM
- Per-sandbox Docker Engine 是之前所有筆記都沒提到的關鍵架構細節
- Docker 的全端策略（Agent + Sandboxes + Governance）驗證了「安全邊界在外不在內」的設計哲學

## 跨文章 Synthesis

**Docker 的 full-stack agent 平台**：三層產品疊加——

```
Docker AI Governance  ← 集中控管（network, credentials, MCP tools）
        │
Docker Agent          ← 多智能體團隊編排（YAML config, role specialization）
        │
Docker Sandboxes      ← 安全執行環境（microVM, per-engine, network isolation）
```

這三者形成完整閉環：**Governance 定義規則 → Agent 組織團隊 → Sandboxes 安全執行**。

對 Hermes 的啟發：
1. Hermes 已有 Agent 層（personality skills）和 Sandboxing 層（探索中的 gradient framework），但缺少 Governance 層
2. Docker AI Governance 的 "centralized control over agent execution, network, credentials, MCP tools" 可作為 Hermes governance 設計的參考
3. 守護者（Talos）的角色部分填補了 governance 缺口，但是 ad-hoc 而非 systematic

**MicroVM 是收斂點**：Docker Captain 比較 + Docker Sandboxes 架構 + Firecracker → 所有 serious sandboxing 方案都在往 microVM 收斂。Hestia 的 L3 設計（microVM for unsupervised exploration）方向正確。

## 未追蹤

- **Docker AI Governance: Unlock Agent Autonomy, Safely** (May 12, 2026) — https://www.docker.com/blog/docker-ai-governance/ — 這是 Hestia 原始 lead，本次 fetch 的兩篇文章都 link 它但未直接覆蓋。作者 Srini Sekaran。對 Hermes governance 設計有直接參考價值。
- Docker Agent 原始 repo（github.com/docker/agent）— 了解 YAML schema 的完整定義
- Docker Sandbox microVM 架構 deep dive — https://www.docker.com/blog/why-microvms-the-architecture-behind-docker-sandboxes/
- Per-sandbox Docker Engine 的實作細節 — 如何在不共享 daemon 的前提下實現 container build/run
- Firecracker vs Docker Sandbox microVM 的技術差異（兩者都是 microVM，但實作路徑不同）

## ✅ 本次探索完成

