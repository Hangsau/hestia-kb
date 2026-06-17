---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-18-1020-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-18-1020-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-18'
confidence: high
title: Hermes Memory Write-Path + Tool Governance 光譜 — Cross-Cutting Insights
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Memory Write-Path + Tool Governance 光譜 — Cross-Cutting Insights

**消化筆記**: 2026-05-18-moltis-dcg-session-memory-deep-dive, 2026-05-18-agent-memory-persistence-deep-dive, 2026-05-18-zerostack-semble, 2026-05-18-moltis-deep-features-compaction-message-block-policy, 2026-05-18-zerostack-doom-loop-code, 2026-05-18-semble-token-savings-test

六篇同日探索筆記，分別研究 Moltis DCG/Memory、Zerostack/Semble、以及三種 agent 記憶系統。看似分散，隱含兩個共同模式。

---

## Cross-Cutting Theme 1: Hermes 的 Memory Write-Path 是系統性缺口

**支援筆記**: moltis-dcg-session-memory-deep-dive, agent-memory-persistence-deep-dive, moltits-deep-features-compaction-message-block-policy

### 分析

三篇筆記從不同角度指向同一個缺口：**Hermes 的 memory surface 只有 read path，沒有 write path**。

| 系統 | 讀取 | 寫入 | 刪除 |  Forget |
|------|------|------|------|---------|
| Moltis | ✅ memory_search | ✅ memory_save | ✅ memory_delete | ✅ memory_forget |
| StixDB | ✅ hybrid search | ✅ 背景自動 merge | ✅ decay/prune |  indirectly via decay |
| AgentKeeper | ✅ ask() | ✅ remember() | ✅ forget() | ✅ forget() |
| Hermes | ✅ memory_search | ❌ | ❌ | ❌ |

Hermes 的 memory pipeline（L1 MEMORY.md → L2 memory-consolidator → L3 briefing）是純推模型（push-based）：agent 產出內容，consolidator 負責消化。沒有讓 agent 在 session 中主動寫入、標記重要事項、或選擇性遺忘的機制。

Moltis 的「Silent Memory Turn」（compaction 前讓 agent 自動 flush 重要資訊）是 Hermes 可以考慮的方向——Hermes 的 consolidator 是事後處理，Moltis 是事前、主動的。StixDB 的四階段記憶成熟模型（episodic → working → semantic）則提供了「什麼條件該晉升」的量化框架。

這個缺口的後果：當 context window 緊張時，agent 無法優先保留關鍵資訊；當記憶過期時，無法定向清除。

### 可行動下一步

在 `memory_consolidator` skill 或 `context_compressor.py` 加入 `BeforeCompaction` hook checkpoint——在 compaction 前先讓 agent 把 critical context flush 到 vault。優先實作「寫入 MEMORY.md 的 agent-facing tool」（參考 Moltis `memory_save` 的 path validation），而非完整 forget/selective delete 功能。

---

## Cross-Cutting Theme 2: Tool Governance 是從被動偵測到主動攔截的光譜

**支援筆記**: moltis-dcg-session-memory-deep-dive, zerostack-doom-loop-code, molttis-deep-features-compaction-message-block-policy

### 分析

三篇筆記展現了 agent tool governance 的三種防禦層次，彼此互補而非重疊：

**Layer 1 — 事前攔截（Preventive）**：
- DCG（Destruction Command Guard）：pre-execution firewall，在 shell command 執行前以 pattern matching 攔截。Context-aware keyword matching（只在 executable span 比對）是核心差異。
- Moltis `MessageReceived/Block`：在 message ingestion 層就阻擋，不持久化到 session store，block reason 回傳給發送者。

**Layer 2 — 即時偵測（Reactive）**：
- Zerostack doom-loop detection：`(tool, input)` pair 計數，16-entry sliding window，≥3 次觸發。純 counter，零 LLM cost，即時阻擋。
- Hermes 提案中的 `doom-loop-detection-sensor`：批次掃描 session log，適合 heartbeat EVOLVE 架構。

**Layer 3 — 事後補救（Corrective）**：
- Hermes 現有的 `enabled_toolsets`：coarse-grained session tool restriction，binary（全開/限定），落在這層。

Zerostack 原始碼確認：doom-loop detection 的正確粒度是 `(tool, input)` pair，不是 tool name alone。Hermes 的 sensor 必須 session-bound 重置 counter（跨 session 重複可能是正常任務）。

DCG 和 doom-loop detection 不是競爭關係——前者管「這個命令是否危險」，後者管「這個行為是否重複到異常」。兩者都在 permission layer 實作，構成雙重檢查。

### 可行動下一步

優先實作 Hermes 版 doom-loop detection sensor（heartbeat EVOLVE step）：掃描 session log，以 session 為單位計數 `(tool, input)` pair，≥3 次觸發 warning severity。同時啟動 DCG 整合評估——DCG 已原生支援 Hermes，是 Talos governance pipeline 的最快上路點。

---
