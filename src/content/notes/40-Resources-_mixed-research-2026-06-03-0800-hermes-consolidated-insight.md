---
_slug: 40-Resources-_mixed-research-2026-06-03-0800-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-0800-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: medium
title: 2026-06-03 Memory Consolidation — Agent 可靠性棧：從 tool-calling 到信任驗證
updated: '2026-06-15'
type: research
status: budding
---

# 2026-06-03 Memory Consolidation — Agent 可靠性棧：從 tool-calling 到信任驗證

**消化筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-shapedql-multi-stage-ranking, 2026-06-03-forge-gambit-agent-harness, 2026-06-03-llamagym-online-rl-fine-tune, 2026-06-03-alexzhang13-rlm-codebase

（本批次 5 篇筆記全部環繞同一核心問題：如何在生產環境中让 agent 系統真正可靠——不是靠更好的模型，而是靠更好的控制架構。）

## Cross-Cutting Theme 1: 三層可靠性棧趨於收斂

**支援筆記**: forge-gambit-agent-harness, llamagym-online-rl-fine-tune, alexzhang13-rlm-codebase

### 觀察

三個看起來不同的系統——Forge（guardrails）、LlamaGym（online RL）、alexzhang13/rlm（環境隔離）——全都描述了同一個分層架構：

| 層 | Forge | LlamaGym | RLM codebase |
|---|---|---|---|
| **L1 執行層** | ResponseValidator + Rescue parsing（tool-call fidelity） | `assign_reward(reward)`（reward signal injection） | REPL 隔離三層（local → ipython → cloud sandbox）|
| **L2 驗證層** | SlotWorker（priority queue GPU slot access） | Agent abstract class（observation formatting） | Metadata-only trajectory logging（constant-size） |
| **L3 行為層** | TieredCompact（context strategy） | PPO training loop | Trajectory visualizer |

### 核心洞察

Forge 的 `ResponseValidator` + `Rescue parsing` 雙層：確保 tool call 正確，不依賴模型自行判斷。Gambit 的 scenario eval：確保行為正確，不依賴模型自行誠實。RLM 的 REPL：確保環境隔離，不讓模型的爛 output 污染系統。

三個系統都在解決同一個問題：**small models（~8B）需要強制結構，別靠信任**。

### 與 Hermes 的對應

Forge 的 `synthetic respond tool` pattern（Hestia 需要 explicit tool vs text 指令）和 RLM 的 `No direct output — model doesn't verbalize output, builds Final variable` 完全一致：結構化輸出 > 自由文字。Gambit 的 `deck.md` grader format 是可操作的 agent eval 格式。

**可行動下一步**: 在 `Talos/hearth/` 架構中實作兩層閘：
1. **Forge-style guardrails** — 在 tool execution 前做 `ResponseValidator` check（Hestia 的 sanitizer 已是這個角色的簡化版）
2. **Gambit-style eval harness** — 用 `deck.md` 格式定義 grader，CI/CD 中對每個 WS task 做行為回歸測試

---

## Cross-Cutting Theme 2: 結構化 invalidation 取代時間衰減

**支援筆記**: rlm-paper-reinforcement-codeRLM, alexzhang13-rlm-codebase, shapedql-multi-stage-ranking

### 觀察

heartbeat_learning.py 的 current gap：三篇筆記都單獨點出同一個問題。

- **RLM paper**: 「Only constant-size metadata about stdout is appended — bounded memory growth」
- **alexzhang13/rlm**: 「Distillates should be compressed representations, not raw note text」
- **ShapedQL**: 「Filter → remove contradicted/outdated distillates; Score → rank by recency, contradiction count, usage frequency」

三者合在一起：memory system 需要結構化 invalidation（矛盾觸發廢棄），而不是 time-based decay（時間到了才衰減）。

### 核心洞察

ShapedQL 的 4-stage pipeline（Retrieve / Filter / Score / Reorder）就是一個現成的 memory consolidation architecture template：

```
Retrieve  → semantic + BM25 hybrid recall
Filter    → remove contradicted (confidence_valid_until check)
Score     → rank by recency + contradiction_count + usage_freq
Reorder   → present top-K, not full dump
```

LlamaGym 的 `assign_reward(reward)` 是更純的概念：新的 reward 信號（證據）應該廢棄舊的 confidence，時間不是觸發條件。

### 與 Hermes 的對應

CodeRLM Studio 的 drift detection：`CodeRLM · 3h Drifts: verify_token() now takes a device_id`——symbol 層級的 drift，spec 說 A 代碼說 B。這是 concept-level staleness detection 的具體範本。

**可行動下一步**: 在 `heartbeat_learning.py` 中實作「矛盾觸發 invalidation」：
1. 每次新 distillate 進入時，檢查是否與現有節點有矛盾（可用 embedding cosine similarity > threshold + 語意衝突檢測）
2. 矛盾存在時，標記舊節點 `confidence_valid_until = now`，不依賴時間
3. Score stage 過濾掉所有 `confidence_valid_until < now` 的節點