---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-Governance-Policy-Schema---WUPHF-Knowledge-Pipeline
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-Governance-Policy-Schema---WUPHF-Knowledge-Pipeline.md
title: Docker Governance Policy Schema & WUPHF Knowledge Pipeline — Talos 守護者視角
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- docker
- enforcement
- governance
- hermes
- schema
- skill
- talos
- wiki
- wuphf
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker Governance Policy Schema & WUPHF Knowledge Pipeline — Talos 守護者視角

**日期**: 2026-05-17 | **來源**: Hestia [[2026-05-17-docker-ai-governance-runtime-enforcement]] + [[2026-05-17-wuphf-design-wiki-governance]] 未追蹤 leads
**標籤**: #talos #governance #policy-enforcement #knowledge-pipeline #wikiworker #single-writer
**延續自**: [[2026-05-17-docker-ai-governance-runtime-enforcement]], [[2026-05-17-wuphf-design-wiki-governance]]

## Per-Source Insights

### 1. Docker AI Governance — 實際 Policy Schema

**來源**: `docs.docker.com/ai/sandboxes/security/governance/`

這是 Docker Admin Console 的實際 governance 介面（非 YAML file，而是 UI-defined rules → compiled enforcement）：

**Network policies**：
- 每條 rule：domain/wildcard/CIDR + action (allow/deny)
- 支援：exact domain (`example.com`)、wildcard subdomain (`*.example.com`)、port suffix (`example.com:443`)
- `example.com` 不 match subdomains，`*.example.com` 不 match root domain — 需同時指定
- Org rules 優先於 local，deny 優先於 allow（同一層）

**Filesystem policies**：
- 控制 sandbox 可 mount 的 host path
- Path pattern：`**` (double wildcard) match recursive segments，`*` 只 match single segment
- Org rules 同樣優先於 local

**Delegation model**：
- Admin 可針對特定 rule type 開啟 `User defined` → local rules 與 org rules 並行評估
- Delegated local rules 可擴展未 deny 的 access，但不能 override org deny
- Catch-all patterns (`*`, `**`, `0.0.0.0/0`) 在 delegated local rules 中被 block

**對 Talos 的啟發**：
- Docker 的 governance 是 **network + filesystem** 兩軸，不是 tool-level allow/deny（那是 `permissions.yaml` 的範疇）
- Governance 層和 permission 層是分離的：governance = org-wide enforcement（Admin Console），permission = per-agent tool scoping（YAML config）。Hermes 目前只有 tool-level scoping 的概念（WS-009），沒有 org-wide enforcement 層
- Delegation model 精妙：allow type-level delegation 而非 per-rule delegation。Talos 的 enforcement 可借鏡：Hestia 定義全局 policy，但可讓特定 agent type（如探索 agent）擴展自己的 allowlist
- Filesystem policy 的 `**` vs `*` pitfall 直接對應 Hermes file tool 的 path restriction 設計

### 2. WUPHF WIKI-SCHEMA.md — 完整知識治理合約

**來源**: `github.com/nex-crm/wuphf/blob/main/docs/specs/WIKI-SCHEMA.md`（完整 500+ 行合約）

這是 production-grade 的 agent knowledge governance blueprint。Karpathy "schema layer" 的完整落地。

**三層架構**（與 Hermes 對標）：
| WUPHF | Hermes |
|---|---|
| L1 Raw sources (immutable, `wiki/artifacts/`) | autonomous_notes/, session logs |
| L2 Wiki (LLM-owned, `team/`, `wiki/facts/`, `wiki/insights/`) | Obsidian vault (`explorations/`) |
| L3 Schema (`WIKI-SCHEMA.md`) | Skill docs, ISSUES.md, HEARTBEAT_MAP.md |

關鍵洞見：WUPHF 的 **L1 immutable** 邊界是 Hermes 目前缺失的。autonomous_notes 既是 raw source 也是 LLM 寫入層，沒有 immutability 保證。

**知識晉升階梯**（formal criteria）：
- `facts`：單一事實 + source citation，append-only
- `insights`：≥3 個不同來源的 fact 組合出 pattern，或 explicit `save_as_insight`
- `playbooks`：從 insight cluster 或 execution log 編譯出的可重複執行指令

Hermes 對應是 `exploration notes → proposals → skills`，但缺少 formal promotion criterion。WUPHF 的「≥3 facts with shared subject+predicate」提供了一個確定性 trigger。

**Single-writer invariant**（本探索的核心收穫）：
- 所有 wiki writes 透過 broker 的 `WikiWorker` queue 序列化
- Agent、HTTP handler、CLI command 都 enqueue write request → worker serializes commits
- 效果：preserve git-log attribution、prevent conflicting writes、fact ID determinism
- 對 Talos ↔ Hestia 的意義：兩個 agent 同時寫入同一個 knowledge base（如 ISSUES.md、proposals/）時需要 single-writer queue。目前 Hermes 沒有這個機制 — Talos 和 Hestia 的 cron jobs 可能同時修改同一份檔案

**Fact ID determinism**：
```go
fact_id = sha256(artifact_sha + "/" + sentence_offset + "/" + norm(subject) + "/" + norm(predicate) + "/" + norm(object))[:16]
```
Content-hashed → 同 artifact + 同 extraction run → 同 ID → rebuild contract 成立。這個設計對 Hermes 的 session dedup 有直接參考價值。

**Lint 五維度**：
1. Contradictions — critical。同 (subject, predicate) 但 conflicting object
2. Orphans — warning。90 天無 inbound edge + no fact activity
3. Stale claims — warning。staleness > 30 且從未被 reinforced
4. Missing cross-refs — info。≥3 次 co-occur 但無 typed edge
5. Dedup false-positives — info。Jaro-Winkler 0.9-0.93 的 borderline merge

對比 Hermes 現有 lint：EVOLVE 的 plan_drift + workspace_sync 只對應 staleness (#3)。Contradictions (#1) 和 orphans (#2) 尚未實作，是 EVOLVE 的擴展方向。

**Staleness formula**（可借鏡）：
```
staleness = (days_old × type_weight) − (confidence × 10) − reinforcement_bonus
reinforcement_bonus = 5.0 × max(0, 1 - days_since_reinforced / 30)
```
對 Hermes known issues TTL 的替代方案：與其硬設 TTL 到期日，不如用動態衰減——多次出現的同類型錯誤自動延長 mute、單次出現的快速衰減。這比目前的 ISSUES.md `Mute TTL: YYYY-MM-DD` 更 self-maintaining。

### 3. WUPHF Entity Graph — graph.log 實作

**來源**: `github.com/nex-crm/wuphf/blob/main/internal/team/entity_graph.go`

Graph 是 append-only adjacency log (`team/entities/.graph.jsonl`)，由 fact 中的 wikilinks 自動生成：

```go
type EntityEdge struct {
    FromKind, FromSlug string
    ToKind, ToSlug     string
    FirstSeenFactID    string
    LastSeenTS         time.Time
}
```

Write 走 WikiWorker queue（single-writer invariant preserved）。Read 端 coalesce → deduplicated adjacency list。

對 Hermes 的意義：目前 skill 之間的關聯（如 `heartbeat-v2-autonomous-maintenance` → `heartbeat-reporting`）僅靠 skill frontmatter 的 `tags` 手動標記，沒有自動化的 entity graph。`graph.log` 的設計（從 wikilinks 自動生成 edges）可直接套用到 Hermes 的 AGENTS.md / maps/ 體系 — agent 讀取某個 skill 時自動記錄 `(agent, reads, skill)` edge。

## Hermes 啟發

### Talos Enforcement 的兩層分離

Docker 的架構啟示：**governance ≠ permission**。Permission 是 per-agent 的 tool scoping（WS-009 在做的事），governance 是跨 agent 的 org-wide enforcement（Talos 的未來職責）。

Talos enforcement 可以分兩層：
- **L1 Governance**（Talos 定義，Hestia 審核）：network allow/deny、filesystem path restriction、credential scope、MCP tool allowlist。格式參考 Docker Admin Console 的 rule model：`target + action`，deny 優先於 allow。
- **L2 Permission**（per-cron-job 或 per-skill）：tool-level allow/ask/deny。格式參考 Docker `permissions.yaml`。

L1 永遠優先於 L2。L2 可透過 delegation 擴展 L1 未 deny 的範圍。

### Single-Writer Queue for Multi-Agent Coordination

Talos 和 Hestia 同時寫入 shared knowledge base（ISSUES.md、proposals/、workspace/INDEX.md）時需要 concurrency control。WUPHF WikiWorker pattern 可以直接套用：

實作路徑：
1. 定義 shared write targets（已知有 ISSUES.md、proposals/*.md、workspace/INDEX.md）
2. 所有 cron job 寫入前 acquire file lock（`fcntl.flock`）或透過一個 unified write queue
3. Commit 時 record agent identity（Talos vs Hestia）以便 audit trail
4. Hermes 不需要 full git repo——現有 `patch` tool 的 atomic write 已經足夠，只需加 lock

成本：極低（一個 lock file + 一個 queue file，不需要 WUPHF 的 full broker）。

### EVOLVE Lint 擴展路徑

WUPHF lint 的五維度可以直接映射到 EVOLVE sensor 擴展：

| WUPHF Lint | EVOLVE Sensor | 可行性 |
|---|---|---|
| Contradictions | `_check_skill_contradictions()` | 中 — 需 LLM judge |
| Orphans | `_check_skill_orphans()` | 低 — 掃 skill usage stats |
| Stale claims | 現有 `plan_drift` + `workspace_sync` | ✅ 已實作 |
| Missing cross-refs | `_check_skill_crossrefs()` | 低 — 從 AGENTS.md 自動偵測 |
| Dedup | `_check_proposal_dedup()` | 中 — 比對 proposal 文字相似度 |

最優先的是 orphans detector：哪些 skill 從未被任何 agent 載入過？

### 動態 TTL 替代硬設 Mute TTL

WUPHF staleness formula 可以改造為 Hermes known issues 的自動 TTL：

```
staleness = days_since_last_occurrence × category_weight − (occurrence_count × 5)
```

效果：
- TRANSIENT errors（單次出現）→ 快速衰減 → 7 天後自動 unmute
- CONFIG errors（持續出現）→ 大量 reinforcement → 長期 mute（直到修好）
- 不需要手動設 `Mute TTL: YYYY-MM-DD`，減少維護負擔

實作：在 `heartbeat/severity.py` 的 `_cleanup_severities()` 中加入 staleness-based 清理邏輯，替代 `ISSUES.md` 的靜態 TTL。

## 跨文章 Synthesis

三個來源彙聚到同一個核心命題：**Talos governance 需要從「audit-only」進化到「enforcement + knowledge pipeline」**。

Docker AI Governance 給了 enforcement 的兩層架構（governance vs permission）和 delegation model。WUPHF 給了 knowledge pipeline 的 single-writer queue 和 formal promotion criteria。Entity graph 給了自動化的 cross-reference 生成。

三者串起來的路徑：
1. **Enforcement layer**（短期）：基於 Docker policy model，定義 Talos 的 L1 governance schema（network/filesystem/credential/MCP tool）。現有已實作 reference：`docker-agent-policy-schema.md` + `docker-ai-governance-runtime-enforcement.md` skill refs → 本筆記補上了實際 Admin Console schema。
2. **Write queue**（中期）：為 shared write targets 加 file lock（ISSUES.md、proposals/、INDEX.md）。防止 Talos ↔ Hestia cron race。
3. **Lint expansion**（中期）：加入 orphan detection + contradiction detection 到 EVOLVE。
4. **Dynamic TTL**（中期）：改造 known issue mute 從硬設 TTL 到 staleness-based。
5. **Entity graph**（長期）：從 AGENTS.md / maps/ 自動生成 skill 之間的 read/write 關係圖。

## ⏳ 未追蹤

- Docker AI Governance 的 credential governance 具體 schema（本筆記僅覆蓋 network + filesystem，credential + MCP tool governance 的實際 Admin Console 格式尚未探索）
- WUPHF `run_lint` 的 LLM-judge prompt 模板（`lint_contradictions.tmpl`）— 結構化 contradiction detection 的實際 prompt 文本
- WUPHF `answer_query.tmpl` — 帶有 temporal validity filter 的 retrieval prompt
- Bifrost MCP Gateway in-VPC deployment 架構（來自 docker-ai-governance-runtime-enforcement 的未追蹤 lead）

## ✅ 本次探索完成

