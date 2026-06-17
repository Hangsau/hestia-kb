---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-20-1401-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-20-1401-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-20'
confidence: high
title: 三層防禆架構收斂：Sandbox / Policy / Hook
updated: '2026-06-15'
type: research
status: budding
---

# 三層防禆架構收斂：Sandbox / Policy / Hook

**消化筆記**: 2026-05-18-zerostack-doom-loop-code, 2026-05-18-moltis-lifecycle-hooks-session-branching-checkpoints, 2026-05-18-orloj-governance-deep-dive, 2026-05-17-docker-multi-agent-sandbox-comparison, 2026-05-17-agent-arena-memory

（摘要）從 Zerostack、Moltis、Orloj、Docker Agent 到 Agent Arena，多個無關來源的 agent 基礎設施研究全部收斂到同一個設計結論：runtime 防禦需要三層互補——隔離層（sandbox/microVM）、策略層（policy/schema）、攔截層（hooks/circuit-breaker）。Hermes 目前只有零散的單層實作，拼圖完整度約 30%。

---

## Cross-Cutting Theme 1: Defense-in-Depth = 三層互補，非單一方案

**支援筆記**: zerostack-doom-loop-code, moltis-lifecycle-hooks, orloj-governance-deep-dive, docker-multi-agent-sandbox-comparison

三個獨立的框架研究同時指出三層架構：

| 層 | Zerostack | Moltis | Orloj | Docker Agent |
|---|-----------|--------|-------|--------------|
| **L1 隔離** | bubblewrap | Docker/Podman/MicroVM/WASM gradient | — | Docker Sandbox microVM + per-engine |
| **L2 策略** | glob-based permission checker | — | AgentPolicy + ToolPermission + operation_rules | AI Governance YAML |
| **L3 攔截** | doom-loop detection (VecDeque counter) | 15-event hook system + circuit breaker | ToolApproval + TaskApproval (human-in-the-loop) | network policies |

**非顯然之處**：這三層各自獨立演化而收斂到同一結構，代表這是此問題域的**強迫性架構**（forced architecture），不是巧合。Hermes 現有：
- L1: `sanitize_fetch.py`（檔案層隔離，非 runtime sandbox）
- L2: `enabled_toolsets` per cron-job（coarse-grained，無 operation_class）
- L3: 無系統性 hook，doom-loop detection 在提案階段

**可行動下一步**：在 `proposals/` 建立 `talos-three-layer-defense-blueprint.md`，把 Orloj 的五層 governance resource schema（AgentPolicy/AgentRole/ToolPermission/ToolApproval/TaskApproval）映射到 Hermes 目前已有的程式碼位置，標出 gap。目標不是立刻實作，而是有文件可循。

---

## Cross-Cutting Theme 2: Memory = Pipeline 設計，不是 Model 設計

**支援筆記**: agent-memory-persistence-deep-dive, agent-arena-memory (ClawMemory section), 2026-05-18-semble-token-savings-test, 2026-05-18-axe-orloj-moltis-deep-dive (Axe GC)

四篇筆記從不同方向對「LLM 已經做複雜事了，後段保持簡單」這個原則達成共識：

1. **ClawMemory**：移除 vector search（昂貴的 semantic 第二次運算），因為 extraction 階段 LLM 已經做了 semantic heavy lifting。BM25 keyword match 足夠。
2. **Semble**：token savings 98% 的核心邏輯不是 semantic 更好，而是「LLM extraction → 結構化事實 → 簡單搜尋」，而不是讓 embedding model 重新理解所有內容。
3. **Axe memory GC**：max_entries warn 但沒有 auto-trim → 需要 external cron trigger（heartbeat）。
4. **StixDB + MuninnDB**：四層記憶晉升模型（raw → edges → hub → semantic）對應 Hermes 的 MEMORY.md → distiller → briefing，但**沒有晉升閾值定義**。

**非顯然之處**：這些系統都把「LLM 是昂貴的前處理，之後交給簡單工具」當作預設模式，但 Hermes 的現有設計剛好相反——MEMORY.md 是 flat append，distiller 是全量重寫，沒有分層或晉升機制。ClawMemory 的 contradiction resolver（newer-wins）和 StixDB 的 merge threshold 都是 Hermes 缺少的**確定性記憶策略**。

**可行動下一步**：在 `heartbeat/actions.py` 加入 `_check_memory_tier()` sensor，實作最簡版本：追蹤 `~/.hermes/memory/*.md` 的行數變化，當單一檔案超過 300 行且 48 小時未變動，自動呼叫 distiller 做一次 compaction，並在 EVOLVE output 報告 `memory tier: flat → compacted`。不引入 vector DB，不用 embedding API，用 `wc -l` + `stat` 這類確定性檢測。