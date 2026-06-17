---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索-OrcBot-v2-1---完整-README-深度---Hermes-借鑒
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索-OrcBot-v2-1---完整-README-深度---Hermes-借鑒.md
title: 探索：OrcBot v2.1 — 完整 README 深度 + Hermes 借鑒
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- completion
- cycle
- heartbeat
- hermes
- memory
- orcbot
- repair
- self
- step
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

---
title: "探索：OrcBot v2.1 — 完整 README 深度 + Hermes 借鑒"
date: 2026-05-23
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [agent, hermes, memory, heartbeat, autonomy, supervision, self-repair]
---

# 探索：OrcBot v2.1 — 完整 README 深度 + Hermes 借鑒

**延續自**: [[2026-05-23-探索-OrcBot---Atom-自主代理框架---SAGA-ACE-延續]]

**日期**: 2026-05-23
**類型**: 架構研究
**來源**: GitHub raw README (43KB, 全文)

---

## Supervisor Runtime Loop（OrcBot 的核心）

前期筆記只看了前幾行。這次讀到完整的 `## Supervisor Runtime` 章節，核心機制比想像的更精細：

### Pre-execution repair
`DecisionEngine` 在主 loop 執行前就能修復 blocked 或不可執行的 plan。這比 Hermes 的「等問題出現再 EVOLVE」更前饋——問題在執行前就被攔截。

### Shared execution coordinators
serial / parallel / bonus-step 的 tool execution 都走同一套 shared helpers，確保：
- side-effect handling 一致
- cooldown 同步
- failure semantics 對齊

**Hermes 的啟示**：目前 Hermes 的 heartbeat actions（SNAPSHOT/EXPLORE/HEAL 等）是各別實作的，沒有統一的 coordinator layer。如果要走向更即時的 supervisor，需要一個共享的 action execution framework。

### Runtime re-planning
batch 失敗時，OrcBot 會：
1. 暫停後續排程 work
2. 記錄 workflow signal
3. 從最新失敗 context 重規劃

**Hermes 的啟示**：Hermes 的 EVOLVE 是在每個 heartbeat cycle 结束时触发，等同「每 30 分鐘重新评估一次」。OrcBot 的模型是「每个 batch 失败后立即 re-plan」——粒度更細，代價是更頻繁的 LLM 調用。Hermes 在 cron mode 下不適合這個模式（否則會觸發太多次），但在 interactive mode 下可以考慮。

### Bonus-step wrap-up mode
當 max-step review 给了额外 turns，bonus steps 被優化為「安全交付」而非「新的探索」。

### Completion reconciliation
實質的 user-facing delivery 成功後，OrcBot 可以 reconcile 最終狀態為 `completed`，即使 guardrails 後來耗盡了 step budget。

---

## Self-Training Sidecar（重要新發現）

OrcBot v2.1 新增了完整的 self-training loop，但設計選擇是**不上線 weight mutation**：

1. **Capture**: completed actions → redacted trajectories (tool steps + delivery audits + final answers)
2. **Filter**: 低品質、無完成、純狀態更新的 trajectory 被排除
3. **Prepare**: 湊夠 accepted examples → 寫 JSONL dataset + offline manifest
4. **Evaluate**: 候選模型在 accepted trajectories 上打分
5. **Promote**: admin explicit promotion，evaluation gate 必須通過

**Hermes 的啟示**：
- Hermes 的 learning extraction 目前是「每個 cycle 記錄 learnings，30 天歸檔」。但從未把這些 learnings 拿來評估或優化 model selection。
- OrcBot 的模式暗示一條可行路徑：**用 learnings 做 offline evaluation → 根據 context（code vs research vs exploration）選擇不同的 model/provider**
- 具體想法：`heartbeat_action_log.jsonl` 已經有完整的 action trajectory，可以改造成「分類 → 歷史成功率 → 動態 model routing」

---

## Memory System（架構對照）

OrcBot 的 memory layer 設計：

| Layer | Type | 說明 |
|-------|------|------|
| short memory | 步驟觀察 | 每個 action 的 observation |
| episodic memory | LLM summaries | 壓縮後的對話段 |
| VectorMemory | embedding index | text-embedding-3-small |
| DailyMemory | append-only .md | 日誌 |
| long memory | MEMORY.md / LEARNING.md / USER.md / JOURNAL.md | 跨 session |

**Hermes 的對照**：
- Hermes 的 L1 (MEMORY.md) ≈ OrcBot 的 long memory (MEMORY.md)
- Hermes 的 L2 (memory-consolidator) ≈ OrcBot 的 episodic memory
- Hermes 的 L3 (briefing-updater) ≈ OrcBot 的 DailyMemory + recall_memory
- **Hermes 缺少**：VectorMemory、RAG semantic search、rag_ingest/search

---

## Agent-Driven Config Management（Policy 分級）

OrcBot v2.0 引入 config 分級保護：

| Policy | 範例 | Agent 權限 |
|--------|------|------------|
| SAFE | modelName, memoryContextLimit | Agent 可自行調整 |
| APPROVAL | API keys | Agent 請求，人工核准 |
| LOCKED | safeMode, security settings | Agent 完全不能改 |

**Hermes 的啟示**：Hermes 目前沒有 config 分級——所有 config 都可以改。引入類似的分級可以：
- 防止某個 heartbeat cycle 意外破壞關鍵設定
- 讓 `CHANGE` 類型的提案更容易實施（有「安全的改法」vs「需要審核的改法」）

---

## Completion Audit Codes（實用的故障分類）

OrcBot 的 completion review 產生 audit codes 來標記為何 block 了 completion：

| Code | 意義 | 典型修復 |
|------|------|----------|
| NO_SEND | user-facing reply 未送出 | completion 前要呼叫 channel send skill |
| UNSENT_RESULTS | 深度 tool output 存在但未發送 | search/browser/command 後要發最終結果 |
| NO_SUBSTANTIVE | 深度/research tools 跑了但無實質交付 | 狀態更新要換成具體發現/結果 |
| ACK_ONLY | 只有確認/狀態訊息 | ack 後要附內容豐富的 delivery |
| ERROR_UNRESOLVED | tool errors 未處理 | 解釋失敗 + 下一步 |

**Hermes 的啟示**：
- Hermes 沒有類似的 audit system——heartbeat completion 沒有「交付了什么」的追蹤
- 可以作為 `heartbeat_v2.py` 的新增功能：在 SNAPSHOT step 記錄這次 cycle 做了什麼實質交付，不只是「跑了哪些 steps」

---

## 跨文章 Synthesis

OrcBot 和 Atom 的架構互補性很強，加上之前的 SAGA/ACE 框架：

|| Pattern | OrcBot | Atom | Hermes |
|---------|--------|-------|------|--------|
| Runtime supervisor (batch-level) | ✅ pre-exec repair + re-plan | — | ❌ (heartbeat only) |
| Self-healing (plugin-level) | ✅ self_repair_skill auto-trigger | — | ❌ |
| Smart heartbeat | ✅ exponential backoff + productivity track | — | ❌ |
| Intent routing | — | ✅ (CHAT/WORKFLOW/TASK) | ❌ |
| Agent maturity graduation | — | ✅ 4-tier | ❌ |
| Self-training sidecar | ✅ capture→eval→promote | — | ❌ |
| Agent-driven config (policy tiers) | ✅ SAFE/APPROVAL/LOCKED | — | ❌ |
| Decision pipeline guardrails | ✅ dedup + recovery hints | — | partial |
| Completion audit codes | ✅ 7-code system | — | ❌ |
| MCP server mode | ✅ stdio + Streamable HTTP | — | ❌ |
| LLM task complexity classifier | ✅ dynamic step/message budgets | — | ❌ |
| GraphRAG | ✅ | ✅ | Partial (FTS5) |
| VectorMemory (embedding) | ✅ | ✅ | ❌ |

**最高價值 pattern 對 Hermes 的潛在價值**（按實作難度排序）：

1. **Completion audit codes（低難度）**：加在 SNAPSHOT，記錄這次 cycle 的實質交付
2. **Smart heartbeat exponential backoff（低難度）**：idle cycle 多了就拉長 interval
3. **Config policy tiers（中難度）**：先給 SAFE/APPROVAL/LOCKED 分類，再實作
4. **Intent routing（高難度）**：需要先有 action taxonomy
5. **Self-training sidecar（高難度）**：需要 learnings 分類 + offline eval framework

---

## 未追蹤 Leads

- OrcBot self-repair skill 原始碼: https://github.com/fredabila/orcbot/blob/main/skills/self_repair_skill.md → 404，repo 無 `skills/` dir
- OrcBot autonomy.html 架構文件: https://github.com/fredabila/orcbot/blob/main/docs/autonomy.html → HTML，非 markdown，fetch 複雜
- OrcBot Circuit Breaker pattern 實作: repo 內 `src/` 無法直接 fetch，需 clone

---

## ✅ 本次探索完成
