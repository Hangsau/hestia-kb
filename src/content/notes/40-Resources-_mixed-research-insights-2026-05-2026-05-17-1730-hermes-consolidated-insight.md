---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-1730-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-1730-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: high
title: 自主 Agent 系統的失敗處理策略光譜
updated: '2026-06-15'
type: research
status: budding
---

# 自主 Agent 系統的失敗處理策略光譜

**消化筆記**: 2026-05-17-ralph-wiggum-autonomous-loops, 2026-05-17-agent-orchestration-zenflow-opik

三套系統（Zenflow、Opik、 Ralph Wiggum）加上 Heartbeat，各自對「agent 失敗了怎麼辦」有不同的預設答案。把這些答案擺在一起，出現一個清楚的光譜結構。

## Cross-Cutting Theme 1: 失敗處理策略是架構選擇的核心變數

**支援筆記**: 2026-05-17-ralph-wiggum-autonomous-loops, 2026-05-17-agent-orchestration-zenflow-opik

Zenflow、Opik、Ralph Loop、Heartbeat 四套系統的核心差異不是「用不用 loop」，而是**遇到失敗時觸發什麼機制**：

| 系統 | 失敗處理策略 |
|---|---|
| Zenflow | verify gate — 每個 step 後檢查，通過才前進 |
| Opik | evaluate → optimize — 根據 trace feedback 調整 prompt |
| Ralph Wiggum | brute-force retry — 一直跑到成功為止 |
| Heartbeat | structured retry with severity escalation — sensor → categorize → escalate → known-issue filter → REPAIR |

這個對照在任一單篇筆記內都沒有出現。Ralph 筆記內部只談 Ralph 自己的失敗哲學，Zenflow/Opik 筆記只談 workflow 和 observability。把兩篇放在一起才看出：這四個系統其實在回答同一個問題，只是答案不同。

Zenflow 和 Opik 的失敗策略偏「預防」（verify + feedback），Ralph 偏「暴力覆寫」（一直試），Heartbeat 偏「結構化修復」（severity 分級 + 已知問題 suppression）。三種哲學可以共存，不是非此即彼。

**可行動下一步**: 在 Heartbeat 的 `EVOLVE` sequence 之後，加一個 explicit failure-strategy selector：
- `severity=CRITICAL` → 觸發 verify gate（類 Zenflow）
- `severity=LOW + known_issue=TRUE` → suppress + log
- `severity=LOW + known_issue=FALSE` → adaptive retry（類 Ralph，但有冷卻期）
不需要改 EVOLVE 本身，在 `decide_next_action` 的分類邏輯裡加分支即可。

---

## Cross-Cutting Theme 2: 獨立 Context Window 是跨系統收斂的結論

**支援筆記**: 2026-05-17-ralph-wiggum-autonomous-loops, 2026-05-17-agent-orchestration-zenflow-opik

Ralph 社群最終得出的結論（bash-based independent context > single-session permanent loop）直接驗證了 Heartbeat 的 cron 架構設計。Zenflow 的 parallel worktree isolation 也是同一個 pattern 的另一種變體。Opik 的 trace-evaluate-optimize 流程在時間軸上也是分開的 span，不是累積在同一个 session 內。

三個完全獨立的系統都收斂到同一個結論：session 累積帶來的 context pollution 問題，大到值得用架構犧牲去避免。這個結論不是任何單篇筆記自己說的。

**可行動下一步**: 這個發現沒有新技術債要加，只是確認架構方向正確。但可以用來抵抗「把 Heartbeat 改成 single long-running session」的衝動提議——參考依據是 Ralph 社群踩過的坑。

---

## Cross-Cutting Theme 3: Completion Criteria 明確性是四套系統共同的優化方向

**支援筆記**: 2026-05-17-ralph-wiggum-autonomous-loops, 2026-05-17-agent-orchestration-zenflow-opik

Ralph 強調「define done precisely」，Zenflow 用 Spec-Driven Workflow 把 completion criteria 前移到 PRD 階段，Heartbeat 目前依賴隱性邏輯（EVOLVE clean = done）。Opik 的 evaluation framework 也是在問「怎麼知道這個版本比上一個好」——也就是 completion measurement 的問題。

四套系統都在往同一個方向優化：把「什麼叫完成」從隱性知識變成可測量的 explicit criteria。Heartbeat 目前落後這個光譜。

**可行動下一步**: 選一個 Heartbeat action（建議 REPAIR）寫出明確的 completion criteria 文件：
```
REPAIR success = gateway responds 200 AND pytest canary passes AND no new ERROR in heartbeat.log
```
現在這些標準存在於工程師心裡，不是系統知道的事實。讓系統知道，才能做真正的 auto-verification。
