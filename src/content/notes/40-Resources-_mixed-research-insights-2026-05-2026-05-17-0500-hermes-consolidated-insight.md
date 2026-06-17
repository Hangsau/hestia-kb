---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0500-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0500-hermes-consolidated-insight.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 6, column 35:\n    title: Hermes Knowledge Governance: Immutability Boundaries\
  \ & Form ... \n                                      ^"
_raw_fm: '

  tags: [consolidation, synthesis]

  source: 2026-05-17-wuphf-design-wiki-governance

  created: 2026-05-17

  confidence: medium

  title: Hermes Knowledge Governance: Immutability Boundaries & Formal Promotion Triggers

  updated: 2026-06-15

  type: research

  status: active

  '
title: 'Hermes Knowledge Governance: Immutability Boundaries & Formal Promotion Triggers'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Hermes Knowledge Governance: Immutability Boundaries & Formal Promotion Triggers

**消化筆記**: 2026-05-17-wuphf-design-wiki-governance

從同一篇 WUPHF 治理文檔的兩個不同章節（WIKI-SCHEMA.md 與 DESIGN-WIKI.md）提煉出兩個非顯然的 cross-cutting pattern，兩者都指向 Hermes 架構中缺失的 governance 層。

---

## Cross-Cutting Theme 1: Governance 的核心是 boundary 而非 content

**支援筆記**: WIKI-SCHEMA.md（Layer 1/2/3 架構）＋ DESIGN-WIKI.md（Anti-slop policy 的強制性語言）

WUPHF 的 schema contract 不是只定義「該寫什麼」，更定義「誰能寫什麼」：Layer 1 是 immutable（LLM 只能讀）、Layer 2 才是 LLM 寫入層。DESIGN-WIKI 的 Anti-slop 條款不是風格建議，而是帶強制性的禁令語言——"If a future revision introduces any of these, the change is **wrong**."

這兩個設計細節共享同一個底層邏輯：**governance 的力度不在於內容豐富度，在於邊界是否被明確且不可滲透**。Hermes 目前不缺 content（ISSUES.md、skills、heartbeat maps），缺的是「哪些 content 可以被 LLM 修改、哪些不行」的明確邊界。

反觀 Hermes：autonomous_notes 和 session logs 混在一起，沒有 immutable layer，沒有「不可變更的 contract 條款」。結果是——任何 LLM agent 都可以覆寫任何東西，governance 形同虛設。

**可行動下一步**: 在 `docs/` 或 `skills/` 目錄新增 `HERMES-CONTRACT.md`，定義 3-5 條不可違反的硬性規則（例如：「所有 exploration notes 歸檔後不可編輯」「skill 的 Pitfalls 區塊一旦寫入不可移除」）。Talos 執行 weekly audit 時檢查這些 boundary 是否被遵守。

---

## Cross-Cutting Theme 2: 知識晉升需要客觀 trigger，否則晉升不會發生

**支援筆記**: WIKI-SCHEMA.md（facts→insights→playbooks 晉升階梯）＋ DESIGN-WIKI.md（Decisions Log 的輕量追蹤）

WIKI-SCHEMA 的晉升規則是明確的：「≥3 個不同來源的 fact 共享同一 subject+predicate → 自動晉升為 insight」。這不是 LLM 主觀判斷，是可 audit 的條件。DESIGN-WIKI 的 Decisions Log 則是另一種晉升的可執行形式——每個設計決策附上 Date + Rationale，未來任何偏離都有跡可查。

把這兩個機制放在一起看出一個 pattern：**沒有客觀 trigger 的知識系統，知識會永遠停在最底層**。Hermes 的 exploration notes 永遠是 exploration notes，因為沒有「什麼時候升級成 proposal」的明確定義；proposal 永遠是 proposal，因為沒有「什麼時候升級成 skill」的明確條件。

結果是：系統內累積大量 low-value 的 notes，真正有價值的 patterns 從來沒有被晉升為可執行的 playbooks。

**可行動下一步**: 制定 HERMES-KNOWLEDGE-PROMOTION.md，定義晉升階梯與客觀條件：
- fact 等同：autonomous note 中「已被驗證的操作事實」
- insight trigger：「同一技術主題出現在 ≥3 篇不同日期的 note 中」→ 產出 consolidated note 草稿
- playbook trigger：「同一技術主題有 ≥1 個已通過的 proposal + ≥1 個實際執行紀錄」→ 自動轉 skill 草稿
- 每個晉升事件寫入 Decisions Log（Date, What, Why）

---

## 與 WUPHF Staleness Formula 的銜接

Theme 1 和 Theme 2 都需要 staleness formula 作為基礎設施：boundary 不被執行會變成 drift，晉升 trigger 不會自己消失。WUPHF 的 staleness formula（`staleness = days_old × type_weight − confidence × 10 − reinforcement_bonus`）可以直接套用到 Hermes known-issue TTL 以及 exploration note relevance decay 上，先把 decay 機制做出來，Theme 1 的 audit 和 Theme 2 的 trigger 才能有意義地運作。

**Next step for staleness**（獨立的 low-priority 工作項）：在 heartbeat sensor fleet 中新增 `StalenessMonitor`，以 WUPHF 公式計算每個 known-issue 和 exploration note 的 decay score，score 超過 threshold 時自動 flag 給 Talos。
