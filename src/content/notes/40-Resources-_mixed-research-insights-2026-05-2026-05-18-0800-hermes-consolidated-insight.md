---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-18-0800-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-18-0800-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-18'
confidence: medium
title: Hermes 安全/治理層落後於自身複雜度
updated: '2026-06-15'
type: research
status: budding
---

# Hermes 安全/治理層落後於自身複雜度

**消化筆記**: 2026-05-18-moltis-dcg-session-memory-deep-dive, 2026-05-18-moltis-deep-features-compaction-message-block-policy, 2026-05-18-moltis-lifecycle-hooks-session-branching-checkpoints, 2026-05-18-zerostack-doom-loop-code, 2026-05-18-moltis-hooks-self-extending-skills, 2026-05-17-agent-arena-memory

（摘要）六篇筆記各自研究不同框架（DCG、Zerostack、Moltis、ClawMemory、Agent Arena），但疊在一起後浮現同一個問題：Hermes 的工具矩陣複雜度（128 skills、10+ cron jobs）遠超其安全/治理覆蓋層——這是一個結構性落差，非單點 gap。

---

## Cross-Cutting Theme 1: Hermes 的安全防禦層落後於工具複雜度

**支援筆記**: 2026-05-18-moltis-dcg-session-memory-deep-dive, 2026-05-18-zerostack-doom-loop-code, 2026-05-18-moltis-hooks-self-extending-skills, 2026-05-17-agent-arena-memory

（分析）

五篇筆記各自研究一個框架的防御機制，疊起來剛好構成 Rust agent 棧的完整 defense-in-depth 矩陣：

| 防禦層 | Zerostack | Moltis | Hermes |
|--------|-----------|--------|--------|
| Destructive command guard | DCG 原生整合 | DCG 原生整合 | **已整合**（但 agent profiles 未配置） |
| Permission checker（白名單） | glob-based | 六層 ToolPolicy | **無**（只有 cron `enabled_toolsets` binary 開關） |
| Doom-loop detection | inline VecDeque | 無（靠 circuit breaker） | **提案階段** |
| Sandbox 隔離 | bubblewrap | sandbox hook | **無**（靠 filesystem 權限湊合） |
| Lifecycle hook interception | 無 | 15-event model | **無** |
| Prompt injection 雙層防禦 | Before/AfterLLMCall | Before/AfterLLMCall | 四層 sanitizer + Phase Lock |

Hermes 的工具數量是這些框架的 2-3 倍，但防御覆蓋反而更薄。Agent Arena 的關鍵論點在這裡成立：當工具矩陣夠大時，架構性防御（architectural controls）是 model-level defense 的必要後盾，而非可選項。

**可行動下一步**: 以 DCG 為基礎，補足 permission checker 層。優先：確認 DCG agent profiles 已針對 Hermes 各 cron job 設定 trust level + disabled packs。

---

## Cross-Cutting Theme 2: Memory 系統缺 Write Path，Compaction 缺零成本模式

**支援筆記**: 2026-05-18-moltis-dcg-session-memory-deep-dive, 2026-05-18-moltis-deep-features-compaction-message-block-policy

（分析）

兩篇 Moltis 筆記各自揭露 Hermes 的 memory 缺口：

1. **無 Agent Write Path**：Moltis 有 `memory_save`、`memory_forget`、`memory_delete` 完整 CRUD，Hermes 只有 `memory_search`（read-only）。Agent 無法在 session 內主動管理自己的 memory，只能等 cron consolidator。

2. **無 Deterministic/Recency-Preserving Compaction**：Moltis 的 structured compaction 引用了 Hermes 的 `context_compressor.py` 作為參考實作——但 Hermes 自己缺少 zero-token 替代方案。`memory-consolidator` 每次都需要 LLM call，成本是 Moltis deterministic mode 的 10-100x。

3. **Pre vs Post Compaction 互補**：Moltis 在 compaction 前做 Silent Memory Turn（flush），Hermes 在 compaction 後 consolidate。兩者可以共存，Moltis 的設計更即時。

**可行動下一步**: 評估 `memory_consolidator` 是否可加入 deterministic mode（建結構化 summary 而不叫 LLM），或起碼在 session 內補一個 `memory_save` tool 讓 agent 主動寫入。

---

## 備註：無 SILENT

本批筆記有 2 個可論證的 cross-cutting theme，適合产出 insight note。
