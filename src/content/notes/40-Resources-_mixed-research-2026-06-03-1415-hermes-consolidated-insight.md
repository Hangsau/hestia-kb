---
_slug: 40-Resources-_mixed-research-2026-06-03-1415-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-1415-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: high
title: Agent 治理雙柱：政策執行層 + 結構化遺忘機制
updated: '2026-06-15'
type: research
status: budding
---

# Agent 治理雙柱：政策執行層 + 結構化遺忘機制

**消化筆記**: 2026-06-03-forge-gambit-agent-harness, 2026-06-03-agent-governance-cupcake, 2026-05-29-SSGM-Governing-Evolving-Memory, 2026-06-02-rlm-paper-reinforcement-codeRLM

（摘要）Forge + Cupcake 構成代理治理的執行層（tool-call 攔截與政策評估），SSGM 構成遗忘機制的理論基礎——兩者合起來才是完整的可靠性架構，而非各自獨立的工具。

---

## Cross-Cutting Theme 1：代理治理需要「執行層」與「測量層」分離（proxy guardrails + eval harness）

**支援筆記**: 2026-06-03-forge-gambit-agent-harness, 2026-06-03-agent-governance-cupcake, 2026-05-29-SSGM-Governing-Evolving-Memory

### 分析

單看 Forge 會以為它是終點，單看 Cupcake 也是。但並排放，兩者形成互補的兩層：

| 層次 | 系統 | 職責 |
|---|---|---|
| **L1 執行層** | Cupcake（Rust + OPA/Wasm） | 攔截 tool-call、政策評估、Block/Modify/Warn |
| **L2 測量層** | Gambit（TypeScript） | 生成 scenario、評分行為、capture trace → 回歸測試 |

SSGM 的 §6.1 四原則（Pre-Consolidation Validation + Access-Scoped Retrieval）提供了 L1 的 policy 邏輯參照但缺少實作；Cupcake 提供了實作但缺少測量層；Gambit 提供了測量層但兩者都沒與 SSGM 的 formal proof 掛鉤。

真正的缺口是：**沒有系統把 Cupcake 的政策執行（Block/Modify）與 Gambit 的場景回歸自動連結**。目前這兩層是斷的——Cupcake 的 enforcement traces 是結構化日誌，Gambit 的 evidence 是 JSONL transcript，兩者無法彼此觸發。

另一個 cross-cutting 觀察：Forge 的 `ResponseValidator`（L1 正確性）+ Gambit 的 grader（L2 行為品質）看似相同分層，卻沒有統一的 schema 讓 L1 的 enforcement event 自動生成 L2 的 regression case。

**可行動下一步**：以 Gambit `deck.md` 格式定義一個「Talos governance policy suite」，
用 Cupcake 的 `policies/` 目錄結構為每個 harness（Claude Code, Cursor 等）寫最小的 OPA 政策子集，
並以 Gambit 的 `runtime-tools` mock fixture 為每個政策建一條 smoke test。
目標：任何人在本地跑 `gambit run --deck talos-governance/deck.md` 就能驗證 Talos 的 tool-scoping 政策是否有效。

---

## Cross-Cutting Theme 2：「結構性遺忘」比「時間衰減」更接近真正的問題

**支援筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-05-29-SSGM-Governing-Evolving-Memory

### 分析

heartbeat_learning.py 目前只有時間衰減（decay）——所有記憶以相同的速率淡化。但 RLM paper 與 SSGM 共同指向另一個問題：**有效性失敗（validity failure）**——某個具體事實變錯了，不是因為時間，而是因為新資訊與舊資訊矛盾。

SSGM 的 §4.3 明確區分兩者：
- **Temporal decay**（所有記憶淡化）→ Mem0 的 decay 機制已覆蓋
- **Validity failure**（特定事實變錯誤）→ 現有架構**無產品解**

CodeRLM 的 Studio提供了具體模板：`CodeRLM · 3h Drift: verify_token() now takes a device_id`——符號層級的 drift detection，spec 與實作之間的斷層被自動偵測。

對應到 Hermes 記憶系統：當新的 distillate 否定舊的（如「某個 belief 現在已是顯然」），現有系統會讓兩者和平共存在 context 裡，沒有鍊接到矛盾的機制。SSGM 的 `Gwrite(ΔM, Mcore)` contradiction check 是 formal NLI，是理論解法；CodeRLM Studio 的 drift alert 是产品级实现——兩者之間需要一個規模更小的 sketch 在 heartbeat_learning.py 裡落地。

**可行動下一步**：在 `heartbeat_learning.py` 增加 `contradiction_edge` 資料結構——
每次 distillate 寫入時，與前 10 個同 domain distillate 做簡單字面重疊檢查（如共享一個具體實體名但描述矛盾）。
若發現矛盾，自動降低舊 distillate 的 confidence 分數並寫入 `supersedes: [old_id]` 標記。
這不是 full NLI，是 first-order approximation——可立即實作，結果有意義。

---

## 次要連結（低信心，記錄但不保證）

- **Cupcake Wasm 評估** + **Forge TieredCompact context 策略** → 兩者都在解決「小模型資源受限下的紀律問題」→ 可能值得研究兩者是否可以合併成單一 Rust crate
- **Gambit runtime-tools mock** + **CodeRLM zero-dependency CLI** → 共同原則：外部依賴最小化 → `heartbeat_v2.py` 重新審視現有依賴列表的候選移除目標（待驗證）
