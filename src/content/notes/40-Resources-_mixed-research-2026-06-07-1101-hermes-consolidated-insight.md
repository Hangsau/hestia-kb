---
_slug: 40-Resources-_mixed-research-2026-06-07-1101-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-07-1101-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- ws-035
- talos
- ecc
- deerflow
- control-plane
source: multi
created: '2026-06-07'
confidence: high
title: ECC ecc2/ 不再是參考資料——它是 WS-035 的對照組
updated: '2026-06-15'
type: research
status: budding
---

# ECC ecc2/ 不再是參考資料——它是 WS-035 的對照組

**消化筆記**: 2026-06-07-ecc-deerflow-harness-exploration, 2026-06-07-ecc2-rust-control-plane-deep-dive

兩篇筆記放在一起浮現一個被單篇筆記自己沒說清楚的轉折：Hermes 對 WS-035 (Policy Engine) 的設計問題，已經從「該建什麼」變成「該偏離 ecc2/ 多遠」。

## Cross-Cutting Theme 1: WS-035 的設計空間被 ecc2/ 大幅收斂

**支援筆記**: 2026-06-07-ecc-deerflow-harness-exploration, 2026-06-07-ecc2-rust-control-plane-deep-dive

Note 2 開了個頭：把 ECC 定位為「harness-native operator system」，並指出 ecc2/ 的 Rust control plane 是 WS-035 的潛在實作參考。但那時還停在「值得研究」層次。

Note 1 把這個洞補完了：它用 ecc2/ 的原始碼逐項對應 WS-035 的 10 個子需求（policy state store、session lifecycle、risk scoring、tool audit、conflict detection、daemon heartbeat、worktree isolation、operator escalation、cost tracking、multi-session grouping），每一項都有對應的 Rust 模組與 SQLite table。

**真正的 cross-cutting insight** 是：這 10 項對應**完全沒有摩擦**——沒有任何一項是 ecc2/ 沒想到或實作方式與 Hermes 需求衝突的。這意味著 ecc2/ 不是「部分參考」而是「完整對照組」。Hermes 的 WS-035 不再需要發明，只需要做一件事：**逐項決定要繼承、要改寫、要捨棄**。

這個結論兩篇單獨看都不會出現——Note 2 太早結束在「ecc2 是 reference」，Note 1 太技術細節看不出 WS-035 層級的涵義。

**可行動下一步**:
建立 `~/obsidian-vault/projects/ws-035-decision-matrix.md`，左欄是 ecc2/ 的 10 項實作，右欄四個選項（直接移植 / Python 改寫 / 抽象介面隔離 / 捨棄自建）。每項填入選擇理由與預估工時。下次 sprint planning 前完成，這是 WS-035 RFC 的輸入。

## Cross-Cutting Theme 2: Talos guardian 角色的「operator escalation」從概念變成可實作契約

**支援筆記**: 2026-06-07-ecc-deerflow-harness-exploration, 2026-06-07-ecc2-rust-control-plane-deep-dive

Note 2 觀察到 ECC 的「operator」概念和 Talos 的 guardian 角色是同構的——都是「在 agent 之上運作」的控制層。當時這是個抽象對應。

Note 1 把這個對應具象化了：`operator_escalation_required()` 函式在 daemon.rs 裡給出了精確的觸發條件——

```rust
self.dispatch_cooloff_active()           // cooloff 期間
    && self.chronic_saturation_streak >= 5  // 連續 5 次慢性飽和
    && self.last_rebalance_rerouted == 0    // rebalance 無效
```

**真正的 cross-cutting insight** 是：escalation 不是「通知使用者」這個動作，而是一個**有狀態的決策**——它需要三個獨立訊號在時間軸上交會（backoff counter、saturation streak、rebalance effectiveness counter）。這把 Talos 的 guardian 角色從「監控 + 通知」重新定義為「**長期狀態觀察者**」。

單看 Note 2 會以為 Talos 是 watchdog；單看 Note 1 會以為 `operator_escalation_required` 只是個 utility function。放在一起才看出：Talos 必須是一個有持久狀態的 daemon，**不能是 stateless hook**。

**可行動下一步**:
把 Talos 的設計文件（如果沒有就開一份 `~/obsidian-vault/projects/talos-guardian-design.md`）明確寫出三個計數器：`chronic_saturation_streak`、`last_rebalance_rerouted`、`dispatch_cooloff_active`，並標明它們的儲存位置（SQLite table column 或 Redis key）。如果現有 Talos 設計是 stateless 的，這份文件要明列「為何必須改成 stateful」。

## Cross-Cutting Theme 3: 「Memory 是一等公民」從觀察變成控制層的查詢介面

**支援筆記**: 2026-06-07-ecc-deerflow-harness-exploration, 2026-06-07-ecc2-rust-control-plane-deep-dive

Note 2 把「ECC instincts + DeerFlow memory orchestration」列為兩個專案的共鳴點，結論是 memory 在 2026 agent 生態已是標準配備。

Note 1 揭露了 ecc2/ 怎麼把 memory 接上 control plane：`context_graph` table 儲存 `ContextGraphEntity`、`ContextGraphRelation`、`ContextGraphObservation`——而且這張表被 daemon loop 查詢（用於 conflict detection 與 escalation 判斷）。

**真正的 cross-cutting insight** 是：memory 在 ecc2/ 不是裝飾或 sidecar，它是 control plane **做決策時的 query target**。當 `operator_escalation_required` 要判斷「rebalance 是否有效」時，它需要的不是 metric，而是「這個 session 過去的 observation graph」。

對 Hermes 的含義：現有的 `heartbeat_learning.py` distillate 層如果只產出 markdown notes 而沒有結構化 query 介面，它對 WS-035 的 control plane **就只是死的歷史**，無法被 daemon 查詢。

**可行動下一步**:
在 WS-035 設計中明確區分兩種 memory：(1) **distillate memory**（給人讀的筆記、現有 vault）與 (2) **queryable memory**（給 control plane 查的結構化 state）。後者最簡單的起點是 SQLite table——和 ecc2/ 的 `context_graph` 對齊 schema，跨 session 的 observation 寫進去，escalation 邏輯 SQL query 即可。

---

**信心**: high（三個 theme 都由兩篇筆記交叉驗證，且都能在 ecc2/ 原始碼中找到對應實作點，不是推測）。
