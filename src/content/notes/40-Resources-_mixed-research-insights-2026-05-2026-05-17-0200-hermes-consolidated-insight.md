---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0200-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0200-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: high
title: Docker Agent Stack 映射到 Hermes：三層缺口與收斂設計原則
updated: '2026-06-15'
type: research
status: budding
---

# Docker Agent Stack 映射到 Hermes：三層缺口與收斂設計原則

**消化筆記**: 2026-05-17-docker-multi-agent-sandbox-comparison, 2026-05-17-docker-sandboxing-landscape

兩篇 Docker  sandboxing  研究獨立探索，卻收斂到同一套架構結論。這不只是技術參考——映射出了 Hermes 當前缺的三層。

## Cross-Cutting Theme 1: Docker 三層產品棧直接映射 Hermes 架構缺口

**支援筆記**: 2026-05-17-docker-multi-agent-sandbox-comparison, 2026-05-17-docker-sandboxing-landscape

Docker 的 full-stack agent 平台是三層疊加：

```
Docker AI Governance  ← 集中控管（network, credentials, MCP tools）
        │
Docker Agent          ← 多智能體團隊編排（YAML config, role specialization）
        │
Docker Sandboxes      ← 安全執行環境（microVM, per-engine, network isolation）
```

對照 Hermes 現況：

| Docker 層 | Hermes 現狀 | 缺口 |
|-----------|-------------|------|
| Governance | Talos（ad-hoc, 非 systematic） | **完全缺口** |
| Agent | personality skills（YAML → markdown SKILL.md） | 部分到位 |
| Sandboxes | L1-L4 gradient framework（探索中） | 部分到位 |

**關鍵洞察**：Note 1 明確指出「守護者（Talos）的角色部分填補了 governance 缺口，但是 ad-hoc 而非 systematic」——Note 2 的整個 YOLO mode 論點都在說同一件事：外部 enforcement 比 internal self-policing 有效。兩篇筆記從不同角度抵達同一個診斷。

## Cross-Cutting Theme 2: Per-sandbox Docker Engine — 被低估的 container-in-container 解法

**支援筆記**: 2026-05-17-docker-multi-agent-sandbox-comparison（首次提出）, 2026-05-17-docker-sandboxing-landscape（未提及，但概念蘊含其中）

Note 1 揭露了一個所有其他 sandboxing 筆記都沒提到的技術細節：**每個 Docker Sandbox 有自己的 Docker Engine daemon**，所以 `docker pull` / `docker compose` 只作用在 sandbox 內部，不會接觸 host daemon。

這個架構解的是 container-in-container 困境的根：
- 傳統 DinD 需要 `--privileged` → 隔離大幅削弱
- Docker Sandbox 的解法：每個 sandbox 自帶獨立 engine → 不需 privileged mode

Note 2 的 agent-infra/sandbox 從另一個方向解同一個問題（統一 filesystem + 單一 container），但沒有觸及「需要 build/run container」的場景。**兩個方案適用於不同需求層次**，但核心問題意識相同。

## 收斂的設計原則：Boundary > Permission

**支援筆記**: 兩篇筆記都從不同角度收斂到此原則

- Note 1：Docker Sandboxes「安全邊界在外部強制，而非 agent 內部的 permission prompt」
- Note 2：agent「安全模型不應該是 'ask permission'，而應該是 'define boundary'」

這和 AIUC-1 的 Autonomy oversight 原則完全一致：「Agent autonomy boundaries must be externally enforced, not self-policed.」

## 未追蹤警示

兩篇筆記都提到但都沒追蹤：**Docker AI Governance**（May 12, 2026）——對應的是 Hermes 最大的架構缺口。Talos 目前是 mental model 層次的守護，沒有對應到 systematic governance 設計。

## 可行動下一步

1. **立即可行**：用 agent-infra/sandbox 做 Hestia 探索模式的 L2 container isolation 測試——一行 `docker run`，container-level isolation 對純文字 research 已足夠
2. **本週調研**：從 Note 1 的 unfollowed leads 列表優先讀 Docker AI Governance（docker.com/blog/docker-ai-governance/），產出簡報對照 Talos 目前的能力缺口
3. **架構層次**：下次 Talos skill review 時，明確問「如果要把 Talos 變成 systematic governance layer，需要新增哪些組件」，不要只做現有能力盤點
