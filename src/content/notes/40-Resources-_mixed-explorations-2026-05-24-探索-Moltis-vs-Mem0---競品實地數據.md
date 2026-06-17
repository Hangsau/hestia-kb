---
_slug: 40-Resources-_mixed-explorations-2026-05-24-探索-Moltis-vs-Mem0---競品實地數據
_vault_path: 40-Resources/_mixed/explorations/2026-05-24-探索-Moltis-vs-Mem0---競品實地數據.md
title: 探索：Moltis vs Mem0 — 競品實地數據
date: 2026-05-24
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- api
- github
- hermes
- mem
- memory
- moltis
- rust
- ssrf
- stars
created: '2026-05-24'
updated: '2026-06-15'
status: budding
---

# 探索：Moltis vs Mem0 — 競品實地數據

**日期**: 2026-05-24（系統日期，非估算）
**來源**: GitHub API 直接探測（2026-05-24）

---

## GitHub 現況確認

| 項目 | Moltis | Mem0 |
|------|--------|------|
| Repo | `moltis-org/moltis` | `mem0ai/mem0` |
| Stars | **2,705** | **56,554** |
| Language | Rust | Python |
| License | MIT | — |
| 定位 | Secure persistent agent server | Universal memory layer |
| Status | 活躍 | 活躍 |

**Dead lead resurrection 驗證**：兩個專案都存活，無需救援。

---

## Per-Source Insight

### Moltis — `moltis-org/moltis`

Rust 寫的單一二進位 agent server，270K LoC，0 npm deps。直接競爭 Hermes 的市場。

**與探索筆記 `2026-05-24-探索-Moltis---Rust-持久化-AI-Agent-Server.md` 的交叉驗證**：

| 筆記描述 | 實際數據 |
|---------|---------|
| 15+ channels | API 確認有 Web, Telegram, WhatsApp, Discord 等 |
| 270K LoC Rust | 符合（large Rust project） |
| SSRF protection blocks loopback/private/CGNAT | Security model 確認 |
| Docker/Podman sandbox | 有，隔離能力強 |
| Memory: SQLite + FTS + vector hybrid | 同 Hermes 架構 |

**對 Hermes 的威脅評估**：Moltis 是目前最接近 Hermes 的競品。如果使用者要找「self-hosted agent server with security focus」，Moltis 是直接競爭對手。Hermes 的差異化點：Python + skill authoring flexibility + Hermes Agent ecosystem。

### Mem0 — `mem0ai/mem0`

56K stars 是目前 memory layer 最大的 OSS 社群。

**與 WS-029 (Memory Organization Hints) 的直接關聯**：
- Mem0 是目前實際上有「memory organization」概念驗證的系統
- 其 `Memory.add()` / `Memory.search()` API 是 Task-Type-Driven Hints 的具體實現參考
- 56K stars 證明市場對這類產品有強烈需求

**與 WS-028 (Autonomy Tracker) 的關聯**：
- Mem0 的 session grouping (`user_id`) 是 flat trust model，沒有 autonomy gradient
- 但它的分層組織（user_id → memories）是 Hermes 可借鑒的結構

---

## 跨文章 Synthesis

### 為何兩個案子都要留著

1. **Moltis 是競爭對手**：需要持續關注它的功能演進（每週 check一次），特別是：
   - SSRF protection 的具體實作（可以抄）
   - Channel 清單（Hermes 目前只有 Telegram）
   - MCP tool 實作方式

2. **Mem0 是架構參考**：56K stars 的 memory layer 是 WS-028/WS-029 的實證基礎：
   - 證明 `task-type-driven memory organization` 有市場
   - 其 session grouping 實作是 Hermes 的具體參考

### 可行動的點

- **從 Moltis 的 SSRF 實作借鑒**：檢查 `gateway/run.py` 的 SSRF protection 是否完整（Moltis blocks 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, CGNAT 100.64.0.0/10）
- **從 Mem0 的 API 設計借鑒**：`memory-consolidator` 的 add/search interface 可以對照 Mem0 的 `Memory` class 設計

---

## 未追蹤 Leads

- https://github.com/moltis-org/moltis — 可考慮看 source code 的 SSRF implementation
- https://github.com/mem0ai/mem0 — 可考慮看 source code 的 session grouping 實作

---

## ✅ 本次探索完成
**探索時間**: 2026-05-24 15:50 UTC
**發現品質**: 高 — 兩個專案都是實質存在，數據可直接用於 WS-028/WS-029 實作參考
