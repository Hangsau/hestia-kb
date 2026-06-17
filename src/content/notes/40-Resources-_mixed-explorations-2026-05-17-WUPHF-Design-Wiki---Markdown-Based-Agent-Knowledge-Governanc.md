---
_slug: 40-Resources-_mixed-explorations-2026-05-17-WUPHF-Design-Wiki---Markdown-Based-Agent-Knowledge-Governanc
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-WUPHF-Design-Wiki---Markdown-Based-Agent-Knowledge-Governanc.md
title: WUPHF Design Wiki — Markdown-Based Agent Knowledge Governance
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- contract
- decay
- governance
- heartbeat
- hermes
- layer
- skill
- staleness
- wiki
- wuphf
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# WUPHF Design Wiki — Markdown-Based Agent Knowledge Governance

**日期**: 2026-05-17 | **來源**: [[2026-05-17-mistle-wuphf-guardian-sandboxing]] 未追蹤 leads
**標籤**: #talos #governance #knowledge-pipeline #consolidation #lint #staleness
**延續自**: [[2026-05-17-mistle-wuphf-guardian-sandboxing]]

## Per-Source Insights

### 1. WIKI-SCHEMA.md — Operational Knowledge Contract

WUPHF 的 wiki schema 是 production-grade 的 agent knowledge governance 合約。Karpathy 的 "LLM wiki" schema layer 落地實作。

**三層架構**（與 Hermes 對標）：

| WUPHF Layer | Hermes Equivalent |
|---|---|
| Layer 1 — Raw sources (immutable, `wiki/artifacts/`) | Session logs, autonomous_notes/ |
| Layer 2 — Wiki (LLM-owned markdown, `team/`, `wiki/facts/`, `wiki/insights/`) | Obsidian vault (`explorations/`, `references/`) |
| Layer 3 — Schema (contract docs, `docs/specs/WIKI-SCHEMA.md`) | Skill docs, ISSUES.md, HEARTBEAT_MAP.md |

關鍵洞見：WUPHF 把 Layer 1 設為 immutable（LLM 只能讀，不能改），Layer 2 才是 LLM 寫入層。Hermes 目前沒有這個明確邊界——探索筆記和原始 session 都混在 autonomous_notes 裡，沒有 immutability 的保證。

**知識晉升階梯**：`facts → insights → playbooks`

WUPHF 的晉升規則：
- `facts`：單一事實，有 source citation，append-only
- `insights`：從 ≥3 個不同來源的 fact 組合出的 pattern，或 explicit `save_as_insight`
- `playbooks`：可重複執行的指令，從 insight cluster 或 execution log 編譯出來

Hermes 的對應是 `exploration notes → proposals → skills`，但沒有類似 WUPHF 的 formal promotion criterion（"≥3 facts with shared subject+predicate"）。這導致晉升依賴 LLM 的主觀判斷，缺乏確定性 trigger。

**Fact staleness formula**（可直接借鑑）：

```
staleness = (days_old × type_weight) − (confidence × 10) − reinforcement_bonus
reinforcement_bonus = 5.0 × max(0, 1 − days_since_reinforced / 30)
```

type_weight: status=1.0, observation=0.5, relationship=0.2, background=0.1

對 Hermes 的啟發：
- Heartbeat known-issue TTL 目前是固定日期，可以用 staleness 取代：confidence（修復信心）、reinforcement（是否重現）、type（SYSTEM vs TRANSIENT）影響 decay 速度
- 探索筆記的 relevance decay：一週後 relevance 開始衰減，除非被後續筆記 reinforced

**Daily lint cron**：WUPHF 每日 09:00 跑五項檢查：
1. Contradictions — 同 subject+predicate 但不同 object → critical
2. Orphans — 90 天無 inbound edge + 無 fact activity → warning
3. Stale claims — staleness > 30 且從未被 reinforced → warning
4. Missing cross-refs — co-occurring ≥3 次但缺 graph edge → info
5. Dedup false-positives — Jaro-Winkler 0.9-0.93 的合併

**對 Talos 的意義**：Hermes 的 heartbeat EVOLVE 已經有 `plan_drift` 和 `workspace_drift`（等於 WUPHF 的 "stale claims"），但缺少 "contradictions" 和 "orphans" 維度。Talos 可以加上：
- **筆記矛盾檢測**：兩篇筆記對同一主題的結論衝突時 flag
- **孤兒提案檢測**：提案超過 90 天無進度且無關聯 skill → 建議 close/archive

### 2. DESIGN-WIKI.md — Governance Through Design Contract

雖然是視覺設計文件，但有兩個 governance-relevant 的模式：

**Anti-slop policy**（§Anti-slop）：一份明確的「不可做的事情」清單，具備強制性語言："If a future revision introduces any of these, the change is **wrong**."

這和 Hermes skills 的 `Pitfalls` 區塊是同一個概念，但 DESIGN-WIKI 做得更強——不只列 pitfall，還禁止未經 escalation 就引入反模式。可以借鑑到 skill 寫作規範：每個 skill 不只列 pitfalls，還需一個「不可變更的設計決策」區塊。

**Decisions Log**：表格形式的設計決策追蹤（Date | Decision | Rationale）。比 Hermes `ISSUES.md` 的 KI tracking 更輕量。適合用在 skill 變更追蹤或 heartbeat 架構變更。

## 跨文章 Synthesis

### Theme 1: Schema-as-contract 是 agent governance 的基石

WUPHF 的核心設計決策是：所有的 LLM prompt 都從 "Read WIKI-SCHEMA.md first. Follow its contract exactly" 開始。這和 Hermes skills 的設計理念一致——skill 是 prompt 的前置指令。但 WUPHF 做得更「合約化」：

- **明確的違規後果**："If a contract decision conflicts with code, the contract wins. Fix the code."
- **Prompt enforce 的具體條款**："Never invent new frontmatter fields, new wiki file locations, or new conventions."
- **Anti-pattern 列表有強制性**：不是建議，是禁令。

對 Hermes 的啟發：skills 可以增加一個 "contract" 區塊，定義不可違反的硬性規則（vs 目前的 "pitfalls" 是軟性建議）。Talos 作為 guardian 可以定期 audit skill 內容是否違反自己的 contract。

### Theme 2: Knowledge decay model 補心跳的二元 TTL

Hermes 的 known-issue management 目前用固定 TTL（`Mute TTL: YYYY-MM-DD`），到期就恢復偵測。WUPHF 的 staleness formula 提供了一個更細膩的替代方案：

- 高 confidence 的 fact decay 慢 → 高 importance 的 known issue 也不該太快過期
- 被 reinforced 的 fact decay 慢 → 被多次 observed 的 known issue 也該 reset decay
- 不同 type 有不同 decay weight → SYSTEM 類 issue 比 TRANSIENT 更持久

這可以轉化為 Hermes 提案：heartbeat severity 的 decay model 從固定 TTL 升級為 dynamic staleness。

### Theme 3: Lint 作為 systematic governance 的日常

WUPHF 的 daily lint cron 和 Hermes heartbeat EVOLVE 是同一種 pattern——定期掃描、分類 severity、產出 report。但 WUPHF 的 lint 涵蓋更多維度（contradiction, orphan, stale, missing refs, dedup），而 heartbeat 目前只有 drift detection。

Talos 可以沿 WUPHF 的 lint 維度擴展 EVOLVE sensor fleet：
1. **Contradiction sensor** — 跨筆記的結論衝突檢測（需要 LLM-as-judge）
2. **Orphan sensor** — 提案/proposal 沒有被任何 skill 引用且超過 N 天
3. **Stale sensor** — 已有（plan_drift, workspace_drift）
4. **Cross-ref sensor** — 筆記之間的 wikilink 覆蓋率

## 對 Hermes 的具體啟發

1. **Layer 1 immutability**：探索筆記應該歸檔到 immutable 區（或至少標記「不可再編輯」），只讓 consolidation/synthesis 讀取。原始 session logs 更不該在 agent 可寫範圍內。

2. **知識晉升的明確 trigger**：不做 subjective promotion，學 WUPHF 給出明確 criterion——如「≥3 篇 exploration note 涵蓋同一技術 → 自動產提案草稿」。

3. **Dynamic staleness for known issues**：從固定 TTL 改為 decay formula，以 confidence（修復信心）＋ reinforcement（是否重現）＋ type weight 決定何時過期。

4. **Contract blocks in skills**：skills 不只是「指南」，也包含不可違反的合約條款。Talos 可以在 audit 時檢查 skill 內容是否違反自己的 contract。

5. **Decisions log as lightweight governance**：heartbeat 架構變更可以用類似 DESIGN-WIKI 的 Decisions Log 表格追蹤，補 `ISSUES.md` 以外缺失的 design rationale 軌跡。

## ✅ 本次探索完成

## ⏳ 未追蹤

- WUPHF `graph.log` — typed cross-entity edges 的實作細節（如何從 facts 自動生 graph edges）
- WUPHF `WikiWorker` — 單一寫入者的 queue 機制（對 Hermes 多 agent 寫入衝突有參考價值）
- WUPHF extraction prompt templates（`extract_entities_lite.tmpl`、`synthesis_v2.tmpl`）— 實際 prompt 文本的結構化程度

