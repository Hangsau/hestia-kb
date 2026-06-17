---
_slug: 40-Resources-_mixed-research-2026-06-01-2100-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-01-2100-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-01'
confidence: high
title: 記憶治理的兩層分工：Provenance + Enforcement
updated: '2026-06-15'
type: research
status: budding
---

# 記憶治理的兩層分工：Provenance + Enforcement

**消化筆記**: 2026-06-01-Graphiti-Bi-Temporal-Edge-Source-Analysis, 2026-06-01-agentic-governance-axonflow-pomerium

（記憶系統需要兩種互補的治理能力：fact 的源頭追蹤（provenance）和 tool/action 的權限執行（enforcement）。Graphiti 提供前者，AxonFlow/Pomerium 提供後者，兩者結合才能構成完整的自主 agent 治理架構。）

## Cross-Cutting Theme 1: Bi-Temporal Provenance 是 Agentic Memory 的必備基底

**支援筆記**: Graphiti source analysis, AxonFlow+Pomerium governance synthesis

Graphiti 的 4-field bi-temporal model（`valid_at`/`invalid_at`/`reference_time`/`expired_at`）直接解決了 WS-035 提出的 memory staleness 問題。`invalid_at` 就是事實過期時間戳，`reference_time` 從 source episode 攜帶時間上下文，可用於 drift detection。這個 model 同時是「Wikilink 即將實現的路徑」——每個 edge 的 `episodes` list 就是 provenance 追蹤，vault notes 缺的只是 query layer。

值得注意的是，Graphiti 和 AxonFlow 都在各自的領域強調同一件事：**inline（路徑內）治理比 post-hoc（事後觀測）更有價值**。Graphiti 的 edge-level semantic search 能在查詢時過濾 stale facts，AxonFlow 的 WCP 在執行時阻斷危險操作。這不是巧合，是演進方向。

**可行動下一步**: 在 WS-035 提案的 architecture section 加入 bi-temporal field（`valid_at`/`invalid_at`/`reference_time`），並以 Graphiti driver architecture 作為 KB query layer 的實作參照。

---

## Cross-Cutting Theme 2: 細粒度控制 > 粗粒度 Policy——從 Session 到 Action

**支援筆記**: AxonFlow+Pomerium synthesis, Graphiti source analysis

AxonFlow 的 step-level gate checks 和 Pomerium 的 per-action auth 共同指向一個 pattern：顆粒度決定治理有效性。Session-level 認證太粗，Action-level 才是有意義的控制平面。這個結論和 Synix 探索中「structured memory > pure embedding retrieval」的共識一致——無論是記憶还是治理，結構化細節比粗略整體更有價值。

Graphiti 的 edge-level embedding（相對於 node-level）呼應這個趨勢：真正的 semantic search 需要顆粒度到每個 fact，而非每個 entity。

**可行動下一步**: 設計 Talos governance pipeline 時，採用 action-level（而非 session-level）的審計 model；每個 tool call 寫入 durable ledger，並以 `reference_time` 標記上下文時間。

---

## Cross-Cutting Theme 3: Self-Hosted 是治理工具的預設選擇

**支援筆記**: AxonFlow+Pomerium synthesis, Graphiti source analysis

兩個差異極大的工具（Graphiti 是開源記憶圖譜，AxonFlow/Pomerium 是治理平台）都強調 self-hosted deployment。對於需要資料主權、審計合規、audit trail 的系統，self-hosted 是架構起點而非部署選項。Graphiti 的多 backend（Neo4j/FalkorDB/Kuzu）讓 self-hosted 部署有彈性；AxonFlow 的 HITL 和 3650-day retention 是合規剛需。

**可行動下一步**: 未來架構設計中，預設「所有資料留在本地」，付費雲端 SaaS 才是需要論證的選項。

---

*Insights synthesized from: Graphiti bi-temporal source analysis (2026-06-01) + AxonFlow/Pomerium agentic governance tools (2026-06-01) + prior memory system explorations*