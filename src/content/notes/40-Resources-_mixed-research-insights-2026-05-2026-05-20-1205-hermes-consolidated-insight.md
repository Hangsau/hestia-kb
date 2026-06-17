---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-20-1205-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-20-1205-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-20'
confidence: high
title: 持久化 Agent × 多層防禦 × 技能基礎設施：三個跨主題收斂
updated: '2026-06-15'
type: research
status: budding
---

# 持久化 Agent × 多層防禦 × 技能基礎設施：三個跨主題收斂

**消化筆記**: agent-memory-taxonomy-survey, autoagents-rust-multi-agent-framework, mcp-agent-agent-as-mcp-server-deep-dive, axe-gc-dead-orloj-agent-system, agent-memory-architecture, zerostack-doom-loop-source-analysis, moltis-dcg-session-memory-deep-dive, moltis-hooks-self-extending-skills, axe-orloj-moltis-agent-infra-paths, orloj-governance-deep-dive, axe-orloj-moltis-deep-dive, agent-memory-persistence-deep-dive, agent-arena-memory, moltis-lifecycle-hooks-session-branching-checkpoints, moltis-deep-features-compaction-message-block-policy, dcg-agent-profiles-talos-governance, zerostack-semble, semble-token-savings-test, zerostack-doom-loop-code

（摘要）19 篇筆記涵蓋記憶理論、Rust agent 框架、MCP 協定、governance、doom-loop detection、技能自我延伸、session memory、compaction。交叉比對後浮現三條非顯然弧線，各自超越單篇筆記的邊界。

---

## Cross-Cutting Theme 1: 「持久化 Agent」收斂——從三個方向指向同一結論

**支援筆記**: mcp-agent-agent-as-mcp-server-deep-dive, autoagents-rust-multi-agent-framework, moltis-lifecycle-hooks-session-branching-checkpoints, orloj-governance-deep-dive

### 分析

這四篇筆記各自獨立的探索，但匯聚到同一個架構結論：

| 來源 | 指向「持久化 Agent」的訊號 |
|------|--------------------------|
| mcp-agent — `create_mcp_server_for_app()` | Hermes 可以暴露成標準 MCP server，支援 pause/resume workflow，session 不再是一次性 |
| AutoAgents Rust framework | 核心設計是 `Environment` 管理 agent lifecycle，而非每次呼叫重啟 |
| Orloj | Worker lease model + durable messaging（NATS JetStream），agent 有 identity 和持久 state |
| Moltis | Persistent agent server，session branching 支援從 checkpoint 恢復 |

這四者各自獨立的探索，共同指向 Hermes 目前架構的盲點：**Hermes 是 CLI → cron → stateless session 的範式**，但外部生態正在向「持久化、有 identity、可 branching」的 agent server 收斂。Hermes 的 heartbeat 機制本質上是在用 cron workaround 模擬持久化（心跳狀態 externalize 到 heartbeat_state.json），但架構上仍不是 first-class persistent agent。

### 可行動下一步

在 `proposals/` 裡立一個 proposal：`hermes-persistent-agent-model.md`。核心問題：Hermes 的下一個版本要不要支援 session resume / branch / identity？評估維度：
1. `create_mcp_server_for_app()` asyncio 模式能否真的把 Hermes 變成 stdio MCP server
2. Orloj 的 worker lease model vs Hermes cron heartbeat 的具體取捨（複雜度 vs 可靠性）
3. 如果要走持久化，checkpoint 要存在哪裡（目前 vault 是檔案，未來是結構化 DB？）

---

## Cross-Cutting Theme 2: 「多層防禦」的完整拼圖——從四個獨立研究路線拼出同一張圖

**支援筆記**: moltis-dcg-session-memory-deep-dive, moltis-hooks-self-extending-skills, dcg-agent-profiles-talos-governance, zerostack-doom-loop-source-analysis, zerostack-doom-loop-code

### 分析

這五篇筆記來自五個幾乎不相關的研究方向，但拼在一起是完整的 defense-in-depth 架構：

```
Layer 1: DCG (Destructive Command Guard)
  — Pre-execution firewall，判斷 command 是否 destructive
  — Context-aware keyword matching（只掃 executable span）
  — Fail-open with performance budgets（6-tier latency budget，200ms deadline）

Layer 2: Lifecycle Hook System (Moltis 15-event)
  — BeforeLLMCall / AfterLLMCall / BeforeToolCall 可做 runtime interception
  — Circuit breaker（3 failures → 60s cooldown → auto re-enable）
  — Prompt injection defense via hook（filter-injection.sh）

Layer 3: Declarative Governance (Orloj)
  — AgentPolicy / AgentRole / ToolPermission / ToolApproval / TaskApproval 五層
  — Fail-closed authorization，scoped 執行

Layer 4: Doom-loop Detection (Zerostack)
  — 16-call sliding window，identical (tool, input) >= 3 次觸發
  — 三態反應：Allow / Ask / Deny
```

**單篇看不出來的**：這四層目前在 Hermes 是碎片化的（DCG 有鉤子但無 governance，doom-loop 只在提案階段，hook 系統完全沒有），但從外部看它們是同一個 design space 的四個象限。Talos governance pipeline blueprint 如果要完整，必須涵蓋全部四層。

### 可行動下一步

更新 `proposals/talos-governance-pipeline-blueprint.md`，在「enforcement layer」下加一個 sub-section「四層 defense stack」，把 DCG、hooks、governance、doom-loop detection 列為四個 enforcement 層。明確定義它們的執行順序和分工——目前只有 governance layer 是 declarative（YAML），其餘三層都是 imperative 或 config-only，需要一次 architectural review 把介面統一定義。

---

## Cross-Cutting Theme 3: 「技能基礎設施」的共同缺口——自我延伸缺 rollback

**支援筆記**: moltis-hooks-self-extending-skills, axe-orloj-moltis-deep-dive, axe-gc-dead-orloj-agent-system, agent-memory-persistence-deep-dive, agent-arena-memory

### 分析

五篇筆記都觸及「agent 自己修改自己的能力」：

| 系統 | 自我修改機制 | 有 rollback？ |
|------|-------------|-------------|
| Moltis | `create_skill`/`patch_skill`/checkpoint before mutation | ✅ checkpoint restore |
| Hermes | `skill_manage` action（LLM→寫檔） | ❌ 沒有 |
| Axe | LLM-assisted memory GC（pattern analysis + trimming） | ❌ 沒有 |
| Hermes (ISSUE) | ISSUES.md suppression（explicit forgetting） | ⚠️ 隱性，不透明 |
| Agent Arena | Memory persistence across sessions | ❌ 缺 GC |

核心缺口：當 Hermes 的 `skill_manage` action 讓 LLM 自己 patch SKILL.md 時，如果 patch 破壞了系統，沒有 checkpoint 可以回滾。Moltis 的設計（automatic checkpoint before mutation）是正確答案，但 Hermes 還沒實作。

同時，「forgetting」在這些筆記裡出現了三次（Aegis 的 learned forgetting、axe memory GC、ISSUES.md suppression），但三者的機制完全不同——需要一個 unified forgetting policy。

### 可行動下一步

在 `proposals/` 裡提案 `hermes-skill-checkpoint-rollback.md`：
1. 實作 checkpoint before skill mutation：在 `skill_manage` 的 patch/delete action 前，自動 cp 舊檔到 `.skill_backup/` 目錄
2. 加 `--rollback <skill_name>` 參數到 `skill_manage`
3. 同時，在 `ISSUES.md` 的 suppression 邏輯旁加一個統一的 `forgetting_policy` 定義（哪些是高頻存取 skill、哪些可以衰減），不再讓 suppression 是 ad-hoc 的
