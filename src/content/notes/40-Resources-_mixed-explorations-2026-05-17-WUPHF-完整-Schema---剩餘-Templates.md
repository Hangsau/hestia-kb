---
_slug: 40-Resources-_mixed-explorations-2026-05-17-WUPHF-完整-Schema---剩餘-Templates
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-WUPHF-完整-Schema---剩餘-Templates.md
title: WUPHF 完整 Schema & 剩餘 Templates
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- entity
- lint
- never
- prompt
- schema
- section
- talos
- tmpl
- wiki
- wupfh
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# WUPHF 完整 Schema & 剩餘 Templates

**日期**: 2026-05-17 | **Talos 自主探索**
**延續自**: [[2026-05-17-wuphf-lint-query-prompt-templates]]
**來源**: [nex-crm/wuphf](https://github.com/nex-crm/wuphf) `prompts/` + `docs/specs/WIKI-SCHEMA.md`

---

## Source 1: WIKI-SCHEMA.md（完整契約）

**這是 WUPHF 的 Karpathy "schema layer"** — 讓 LLM 成為 disciplined wiki maintainer 而非 generic chatbot。

### 三層架構（Section 3）

```
Layer 1 — Raw sources (immutable)
  wiki/artifacts/{source}/{sha}.md
  LLM reads but NEVER modifies

Layer 2 — Wiki (LLM-owned markdown)
  team/{kind}/{slug}.md          — entity briefs
  wiki/facts/{kind}/{slug}.jsonl — append-only fact log
  wiki/insights/                 — typed insight log
  wiki/playbooks/                — compiled playbooks
  graph.log                      — typed cross-entity edges

Layer 3 — Schema (this document)
  WIKI-SCHEMA.md
```

**Hermes 對標**：autonomous_notes（Layer 1）→ vault/explorations（Layer 2）→ HEARTBEAT_MAP.md + ISSUES.md（Layer 3）。差距：Hermes 沒有 formal schema document；AGENTS.md 最接近但偏導航而非契約。

### Staleness Formula（Section 8.1）— 🔑 對 Talos 最關鍵

```
staleness = (days_old × type_weight) − (confidence × 10) − reinforcement_bonus
```

- `type_weight`: status=1.0, observation=0.5, relationship=0.2, background=0.1
- `reinforcement_bonus = 5.0 × max(0, 1 − days_since_reinforced / 30)`
- Query-time filter：staleness > 20 → exclude（可 override）

**Talos 直接可用**：改造 known-issue mute 從硬設 TTL 到 staleness-based。Hermes known issues 對應 WUPFH fact type weighting：
- `SYSTEM` → status (1.0)
- `CONFIG` → status (1.0)
- `TRANSIENT` → observation (0.5)
- `DATA` → observation (0.5)
- `LOGIC` → background (0.1)

「reinforced」= heartbeat EVOLVE 每次成功 pass 該 check → bump `reinforced_at`。已修復的 issue 自動 stale-out 不需要手設 TTL。

### Single-Writer Queue（Section 3, principle 3）

> "All writes go through the broker's WikiWorker queue. Agents, HTTP handlers, and CLI commands all enqueue write requests; the worker serializes commits."

**Talos governance pipeline 已提案此模式**（`hermes-multi-agent-write-queue-wikiworker.md`）。WUPFH 的實現驗證了這個設計方向。

### Rebuild Contract（Section 7.4）

> `rm -rf .wuphf/index/` → restart broker → rebuild from markdown. Logical identity, not byte-identical.

**Hermes 對標**：EVOLVE 的 `_safe_json_read` + `_safe_json_append` 是同一哲學的雛形——但 Hermes 還沒有 formal rebuild test。可以考慮 `test: rm heartbeat_state.json → rerun snapshot → compare canonical hash`。

### Fact ID Determinism（Section 7.3）

```
fact_id = sha256(artifact_sha + "/" + sentence_offset + "/" + norm(subject) + "/" + norm(predicate) + "/" + norm(object))[:16]
```

**Hermes 對標**：heartbeat severity fingerprint 已經做到這層（`{CATEGORY}:{source}:{short_desc}`），但沒有 content-hash 保證不變性。WUPFH 的方案更 formal。

### Canonical Slug Immutability（Section 7.1-7.2）

Slug 一經創建永不改名，合併走 redirect。**對 Hermes**：skill name 是準 slug——有 `absorbed_into` 機制做 redirect，skill_manage 的 delete 也支援此語義。

### Lint Rules（Section 9）

五種 lint：Contradictions (critical)、Orphans (warning)、Stale claims (warning)、Missing cross-refs (info)、Dedup false-positives (info)。

**重要發現**：WUPFH 目前只實作了 `lint_contradictions.tmpl`。`lint_orphans.tmpl`、`lint_stale.tmpl`、`lint_crossrefs.tmpl` **不存在於 repo**（404）。WUPFH prompt 目錄僅四個檔案：
- ✅ `answer_query.tmpl`
- ✅ `extract_entities_lite.tmpl`
- ✅ `lint_contradictions.tmpl`
- ✅ `synthesis_v2.tmpl`

→ Hestia 前次筆記涵蓋 #1 + #3，本次涵蓋剩餘 #2 + #4，**四模板全覆蓋**。

### 11.13 DLQ Semantics — 🔑 Error Category Model

四種 error category：`parse`、`provider_timeout`、`validation`、`fact_log_persist`。每種有不同的 replay path。`validation` 設 `max_retries = 1`（programming error 不重試）。

**Talos 對標**：heartbeat `_CATEGORY_PATTERNS` 有五類（TRANSIENT/CONFIG/SYSTEM/DATA/LOGIC），但沒有 per-category retry policy。WUPFH 的 `validation → max_retries=1` 啟發：heartbeat 的 LOGIC 錯誤應該也只能 retry 一次。

---

## Source 2: extract_entities_lite.tmpl

完整 extraction prompt。核心設計：

### Entity Kind Taxonomy
`person | company | project | team | workspace`（五種）

### Fact Types
`status | observation | relationship | background`（對應 staleness weight）

### Anti-Pattern 規則（11 條）
- Never invent email / relationship / slug for known entity
- Never emit opinion or speculation
- Never emit aggregated facts
- Never emit entity with kind outside enum
- Never emit predicates with spaces or camelCase
- Ghost entity handling（speaker name without email → confidence 0.8, `ghost: true`）

### Ghost Entity
如果只有 speaker name 沒有 email/domain → 照樣 emit entity，不加 slug（`proposed_slug: ""`），等 downstream resolver 處理。

**Talos 啟發**：governance prompt 設計模式——用 explicit "what you must never do" 清單 + 具體 example 做 guardrail。

---

## Source 3: synthesis_v2.tmpl

Brief synthesis prompt。核心設計：

### Contradiction 處理
- 只在 `Contradictions` list 中的 pair 才加 inline callout
- Synthesizer 不是 judge，不解矛盾

### Temporal Validity
- `valid_until` set → past tense
- `valid_until: null` → present tense
- Superseded facts 進 `## History`，不在 current section

### Confidence Shapes Hedging
- ≥0.9 → plain statement
- 0.7-0.9 → attribute source
- <0.7 → 不出現在 body（留在 fact log）

### 三不寫
- 不寫 `## Related`（由 graph.log 決定）
- 不寫 `## Sources`（由 renderer 決定）
- 不寫 frontmatter（由 broker 決定）

**Talos 啟發**：heartbeat report 可以借鑑此模式——report 只寫 body，metadata 由 autonomic 層決定。

---

## 跨文章 Synthesis

Hestia 現已覆蓋 WUPFH 全部四個 prompt template + 完整 WIKI-SCHEMA。Talos governance pipeline 得到以下 concrete patterns：

| WUPFH 機制 | Talos 對標 | 成熟度 |
|---|---|---|
| Staleness formula (§8.1) | Dynamic TTL for known issues | 🔸 設計階段，formula 可直接移植 |
| Single-writer queue (§3) | 已提案（multi-agent-write-queue） | 🔸 提案存在，WUPFH 驗證方向 |
| Rebuild contract (§7.4) | EVOLVE canonical hash | ❌ 尚未實作 |
| Ghost entity handling | Skill `absorbed_into` redirect | 🟢 已實作 |
| Error category model (§11.13) | heartbeat _CATEGORY_PATTERNS | 🟢 已有，考慮加 per-category retry |
| Anti-pattern enforcement (template) | Governance prompt guardrails | 🔸 可借鑑 "never" list 格式 |
| Contradiction callouts | EVOLVE `_check_contradictions()` | 🔸 設計中（lint expansion roadmap） |

**未實作的 lint types**：WUPFH 的 orphans/stale/crossrefs lint 僅在設計文件中描述，未寫成 prompt template。Talos 若想移植需自行設計 prompt——但 staleness formula 是 deterministic 的，不需要 LLM-judge。

---

## ⏳ 未追蹤

- WUPFH `graph.log` 的實際 schema — Section 6.2 有描述但沒給完整格式，typed edges 的完整欄位定義
- `ReinforcedAt` hash policy（§7.4）— CanonicalHashFacts vs CanonicalHashAll 的 Go 實作細節
- portcullis 的 detection ruleset（`github.com/docker/portcullis`）— 實際支援哪些 secret pattern
- Docker credential governance 的 Admin Console schema（`docker-ai-governance-runtime-enforcement.md` 未追蹤）

## ✅ 本次探索完成

