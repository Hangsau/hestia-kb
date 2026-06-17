---
_slug: 40-Resources-_mixed-research-2026-06-08-0301-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-08-0301-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-08'
confidence: high
title: Constraint Decay 與 PhantomPolicy 的合流：LLM Agent 的 Invisible State 問題
updated: '2026-06-15'
type: research
status: budding
---

# Constraint Decay 與 PhantomPolicy 的合流：LLM Agent 的 Invisible State 問題

**消化筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

兩篇論文（Constraint Decay 量化「加約束反而掉 30pp」、PhantomPolicy 量化「policy state 不可見時 90-98% 違規」）從不同面向指向同一個根因：LLM agent 的失敗主因不是 reasoning 錯誤，而是 **invisible state**——對任務或政策至關緊要的 state 不在 agent-visible context 內。

## Cross-Cutting Theme 1: 約束越多反而越糟——但 ABC 的 (p,δ,k) 形式化正是回應

**支援筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

Constraint Decay 量化一個反直覺事實：L0（無約束）→ L3（架構+DB+ORM 全開）assertion pass rate 跌 30pp，weaker config 接近 zero。論文結論是「strict tool surface 勝過 wide access」，但**沒解釋為何**。ABC 的 Compositionality Theorem 給了答案：硬約束必須滿足四個條件（interface compatibility, pre/post chaining, governance consistency, recovery isolation）才能 compose，否則就是 pile-up。**L0→L3 的 30pp drop 就是這些條件沒被滿足時的 decay**。ABC 的 (p,δ,k)-satisfaction 提供 (with probability p, deviation within δ, recovery within k steps) 形式化——這正是把「decay 30pp」轉成「bounded drift D*=α/γ」的關鍵轉譯。Hermes 的 Talos governance 不該用「愈多約束愈好」的心態堆 rule，而該明確把每條約束的 p, δ, k 寫進 ContractSpec YAML。

**可行動下一步**:
- 建立 `tal/contract_spec/` 目錄，挑選 3 條 Talos 現有的 governance policy（例如 tool scoping 規則、scope boundary 規則、recovery trigger），重寫為 ContractSpec YAML 格式，每條都附 `(p, δ, k)` 機率性 satisfaction 欄位。
- 在 `heartbeat_learning.py` 的 drift penalty 計算中新增一條 metric：追蹤「constraints added vs recovered violations」的比率——若 ratio 持續上升代表正在 decay。
- 跑一次 mini-A/B：在同一個 coding task 上比較「5 條 hard contract 全部 hard-enforce」vs「5 條 hard contract 拆成 2 hard + 3 soft with δ=0.1」,量測 pass rate 差異,目標是驗證 ABC 形式化是否真的緩解 constraint decay。

## Cross-Cutting Theme 2: Invisible State 是兩篇論文的共同根因——但 recovery rate (γ) 是被忽略的槓桿

**支援筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

Constraint Decay 描述了兩種 invisible state failure：
- **Premature halting**：模型發送 natural language summary 而非呼叫 finish tool——state（task completion）對模型「可見」但被忽略
- **Framework idiosyncrasy**：特定 framework 的特殊行為（如 Django ORM 的 lazy query），agent context 內根本沒記錄

PhantomPolicy 量化了這個問題的規模：當 policy-relevant facts 不在 agent-visible context 時，**90-98% 的 action 違規**。論文用 Sentinel 的 7 個 graph invariants + speculative execution 解，**把 state 從「不可見」轉成「執行後 materialized 然後驗證」**。

兩篇合併的 insight：ABC 論文自己也承認「Recovery contributes largest marginal improvement to reliability Θ (dominant contributor)」——γ 在 D*=α/γ 公式中是分母，**增加 recovery rate 比降低 drift rate 對 bounded drift 的槓桿更大**。Constraint Decay 完全沒談 recovery（OpenHands re-prompt 6 turns 算 ad-hoc recovery 但沒正式化）。這意味著 Hermes 的高槓桿介入點是**正式化 recovery loop**而非再加更多 hard constraint。

**可行動下一步**:
- 把 OpenHands-style 的 re-prompt 機制正式化為 ABC 的 `recovery_policy` 欄位：在 Talos governance schema 中新增 `recovery: {max_attempts: 6, escalation: 'heartbeat_alert', rollback_action: 'discard_partial_state'}` 結構。
- 設計一個新 metric `recovery_rate γ` 追蹤 Talos 觸發 recovery 後 24 小時內是否成功 bound drift——這是 D*=α/γ 中 γ 的具體量測方式。
- PhantomPolicy 的 Sentinel speculative execution pattern 可直接借鏡：Talos 在執行任何 tool call 前，先在隔離 sandbox 跑一次「ghost mutation」驗證 graph invariants，O(|M|) overhead 對 sub-100ms tool call 來說可接受——寫一個 PoC 在 `tal/poc/sentinel_precheck.py`。

## Cross-Cutting Theme 3: Premature Halting = PhantomPolicy 的 I1:ActiveRecipient/Temporal Validity——但 Hermes 還沒偵測這個

**支援筆記**: 2026-06-08-constraint-decay-llm-agents, 2026-06-08-agent-behavioral-contracts

Constraint Decay 的 premature halting 範例（agent 發 natural language summary 而非呼叫 finish tool）正是 PhantomPolicy 8 個 violation categories 之一的 **I1: ActiveRecipient / Temporal validity**——「在錯誤的時機對錯誤的接收者送出訊息」。PhantomPolicy 對所有 8 個 categories 提供 7 個 graph invariants 覆蓋，I1 是其中唯一針對時序的。**Constraint Decay 沒意識到自己的 premature halting 觀察就是 PhantomPolicy taxonomy 的一個 instance**——這是 cross-paper 命名差異造成的 insight 缺口。

對 Hermes 的意義：Hestia/Talos 的 cron 任務完成偵測邏輯目前可能只檢查「是否有 finish tool call」，沒檢查「finish tool call 是否對應實際 task completion」。一個 agent 可能 schedule-cron 任務跑完後發出看似完成訊息但實際上還有 side effect 沒落地。

**可行動下一步**:
- 在 Hermes 的 cron 完成偵測（`/root/.hermes/scripts/`）中加入一條 invariant 檢查：「最後一個訊息是否包含 unfinished_side_effect 標記」——這是 I1:ActiveRecipient 簡化版的 hermes-side 對應。
- 為 Hearth Hestia↔Talos handoff protocol 新增 `temporal_validity` 欄位：發送 handoff 訊息時必須包含 `(sent_at, expected_complete_by, recovery_window)` 三元組，缺一就 block。
- 寫一個 30 分鐘的研究任務：通讀 PhantomPolicy Section 4 全部 8 個 categories，建立 `tal/violation_taxonomy.md` 把 PhantomPolicy → Hermes existing systems 的對應表填完（目前只有部分 coverage：ContextBoundary ↔ scope limiting、Oversharing ↔ comms scope、Accumulated leakage ↔ thread context cutoff，**Temporal validity / High-value resource / Cross-context dataflow 還沒對應**）。
