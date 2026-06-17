---
_slug: 40-Resources-_mixed-research-2026-05-30-0414-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-05-30-0414-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-30'
confidence: medium
title: 記憶系統的兩個尚未閉環的核心問題：staleness 與 forgetting
updated: '2026-06-15'
type: research
status: budding
---

# 記憶系統的兩個尚未閉環的核心問題：staleness 與 forgetting

**消化筆記**: 2026-05-29-llm-agent-memory-architecture, INBOX_20260519_100535

LLM Agent Memory 架構研究已收斂到三層核心問題，但 Hermes 的実装只覆蓋了其中一個（decay）。剩下兩個——staleness 與 forgetting——需要從設計態度上改變。

---

## Cross-Cutting Theme 1: Staleness 不是 decay 的子集，是另一個維度的失效

**支援筆記**: 2026-05-29-llm-agent-memory-architecture, INBOX_20260519_100535

**分析**:

MLMF Survey 明確區分這兩者：
- **Decay** = 低相關性事實隨時間平滑衰减（heartbeat_learning.py 已在處理）
- **Staleness** = 高信心、事實突然變錯（例如 skill 的版本號、工具的 API endpoint、環境狀態）

2026-05-29 的筆記第 56 行說「heartbeat_learning.py addresses decay but not staleness」，但 INBOX entry 提到 heartbeat 任務需要來自 Talos 的回覆——這說明一個事實：系統狀態依賴外部更新，而外部更新不會主動通知記憶系統。

Mem0 blog 直接點出：「Staleness in high-relevance memories is a harder, open problem」。研究文獻和系統現実共同指向同一個結論：不解決 staleness，high-relevance 記憶會在關鍵時刻提供錯誤信心，比沒有記憶更糟。

BEAM benchmark 的 10M scale 降至 48.6% 也暗示：當架構横向擴展，staleness 會比 recall quality 更早成為瓶頸。

**可行動下一步**:

在 `heartbeat_learning.py` 的記憶結構加上 `confidence_valid_until` 欄位（datetime），讓高impact 的事實（版本、endpoint、狀態開關）攜帶有效期限。當 session 啟動檢索記憶時，自動標記過期事實為 `stale`，不走刪除而是降權。具體實作：參考 Zep 的 validity window 模式——不再依賴「最近使用」推論相關性，而是讓源頭明確宣告「這件事何時可能變錯」。

---

## Cross-Cutting Theme 2: Forgetting 作為設計 primitive 而非 edge case

**支援筆記**: 2026-05-29-llm-agent-memory-architecture

**分析**:

研究調查的 8 個框架中，Supermemory 是唯一把 explicit forgetting 當成 first-class design primitive 的系統。所有其他框架（包括 Mem0、Zep、Letta）預設記憶只增不減。

但 MLMF Survey 說：「Forgetting is not a bug; it is a feature」——這不是修辭，是效率論點：不 forget 的系統會被低價值記憶稀釋高價值記憶的召回信號，最終 context 膨脹但 SNR 下降。

6,956 tokens/query 的效率數字（Mem0）對照 BEAM 10M scale 48.6% 的天花板，直接說明：即使向量檢索已足夠聰明，當記憶總量成長，儲存與檢索成本仍會壓垮架構。Forgetting 是規避這條路的唯一永續手段。

Hermes 的 skills 已有 `deprecated` frontmatter，這是 partial implementation 但尚未系統化——沒有 depletion trigger、沒有 archive 流程、沒有跨 skill 的版本繼承邏輯。

**可行動下一步**:

在 `skills/` 分類下實作一個 `version-lifecycle` 規範：每個 skill 的 frontmatter 必須有 `replaces: [older-skill-name]` 欄位（可選但建議），當新版本 skill 上線時，舊版本自動寫入 `deprecated: true` 並觸發 vault 歸檔。這個機制比「優雅刪除」更能追蹤系統演化——不只知道某個做法被放棄，還知道被什麼取代、為什麼。

---

## 備註

INBOX_20260519_100535.md 為短期待辦（回覆 Talos），不承載長期知識，直接標記已消化不做 consolidation。