---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-hermes-consolidated-insight.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 6, column 39:\n     ...  Hermes Enforcement Architecture: Three Cross-Cutting\
  \ Patterns\n                                         ^"
_raw_fm: '

  tags: [consolidation, synthesis]

  source: multi

  created: 2026-05-17

  confidence: high

  title: Hermes Enforcement Architecture: Three Cross-Cutting Patterns

  updated: 2026-06-15

  type: research

  status: active

  '
title: 'Hermes Enforcement Architecture: Three Cross-Cutting Patterns'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Hermes Enforcement Architecture: Three Cross-Cutting Patterns

**消化筆記**: 2026-05-17-docker-ai-governance-runtime-enforcement, 2026-05-17-talos-governance-policy-wuphf-pipeline

三個架構原則在 Docker runtime enforcement 和 WUPHF knowledge pipeline 中以不同形式反覆出現，構成 Hermes 下一階段的設計骨幹。

---

## Cross-Cutting Theme 1: Enforcement 必須在正確的抽象層——而且只有一個正確層

**支援筆記**: docker-ai-governance-runtime-enforcement, talos-governance-policy-wuphf-pipeline

兩篇筆記獨立地抵達同一個結論，但顆粒度不同：

- Docker 的教訓：「policy 在 system prompt 層是 advisory，可被繞過；要在 `pre_tool_use` runtime hook 層執行」
- WUPHF 的教訓：「governance（網域範圍）≠ permission（工具範圍），兩層分離且 L1 永遠優先於 L2」

合起來等於：**每一種控制都有其唯一正確的執行層，混用會失效**。把 credential governance 放在 system prompt（建議）而不是 `pre_tool_use`（強制），等於沒做。把 org-wide network deny 放在 per-agent permission YAML 而不是 shared governance layer 等於可以被 local 覆寫。

對 Hermes 而言，這確定了 tool gateway mediation 是唯一正確的 enforcement point——不是 system prompt，不是 tool output scan，是 `pre_tool_use` hook。

**可行動下一步**: 在 `tool-gateway` skill 的 `pre_tool_use` hook 實作 credential parameter scanning（掃描 tool call 參數中是否出現 `AWS_SECRET`、`OPENAI_API_KEY` 等關鍵字），在 `before_llm_call` hook 實作訊息掃描（阻止 credential 在 system prompt 中外洩）。目前 `secret-leak-prevention` 只做事後 regex，需升級為三層之一。

---

## Cross-Cutting Theme 2: Single-Writer 是防止非決定性狀態的唯一機制

**支援筆記**: talos-governance-policy-wuphf-pipeline（另有隱含來自架構共識）

WUPHF 的 WikiWorker single-writer queue 是針對知識寫入的非決定性：同一個 artifact 的同一句話，在不同 extraction run 中會因為 timestamp、session ID 等產生不同 ID，無法滿足 rebuild contract。

Hermes 面對的是同一個問題的變體：**Talos cron job 和 Hestia cron job 可能同時寫入同一份 ISSUES.md 或 proposals/，導致 git log 無法追蹤單一作者、workspace/INDEX.md 出現 race condition**。目前沒有任何 concurrency control。

WUPHF 的 fact ID determinism 公式：
```
fact_id = sha256(artifact_sha + "/" + sentence_offset + "/" + norm(subject) + "/" + norm(predicate) + "/" + norm(object))[:16]
```
這個設計對 Hermes 的 tool call deduplication 直接可用——用 content hash 取代 session-scoped ID，解決同一 tool call 在不同 session 的等價判斷問題。

**可行動下一步**: 在 `workspace-sync` skill 中實作 single-writer write queue（Python `queue.Queue` 或檔案鎖），針對已知並發 target：ISSUES.md、proposals/、workspace/INDEX.md、HEARTBEAT_MAP.md。同時將 tool call log 的 ID 生成改為 content-hash based（`sha256(tool_name + str(sorted(params.items())))` 取前 16 字元）。

---

## Cross-Cutting Theme 3: 知識系統需要明確的 L1 邊界——Hermes 目前雙向混用

**支援筆記**: talos-governance-policy-wuphf-pipeline（primary）, docker-ai-governance-runtime-enforcement（contextual）

WUPHF 的 L1（raw sources, immutable）vs L2（LLM-owned wiki）vs L3（schema）是對 Karpathy "schema layer" 的完整落地。關鍵 invariant 是：**L1 不可被 LLM 寫入，只能追加**。

Hermes 的問題：autonomous_notes/ 同時承載 raw source（從 system readout 來的初始狀態）和 LLM 寫入層（consolidated notes、proposal drafts），兩者沒有邊界。這導致：
1. WUPHF 的 staleness formula 無法直接套用——staleness 是針對 L1 的 fact 衰減，不是針對 LLM 創作
2. WUPHF 的 contradiction detection 無法實作——需要 L1 的 immutable ground truth 作為對照組
3. `EVOLVE` 的 plan_drift + workspace_sync 只檢查 staleness，沒有覆蓋 WUPHF 的五維 lint

**可行動下一步**: 將 `autonomous_notes/` 重構為真正的 L1——只容許來自 system readout 或 tool execution log 的追加，LLM 的 consolidated output 統一寫入 `explorations/`（L2）。在 `EVOLVE` skill 中新增 contradiction detection：每当新的 consolidated note 写入时，比对 `autonomous_notes/` 中是否有同 subject+predicate 但不同 object 的 claims。

---

## 架構總結

| Pattern | Docker | WUPHF | Hermes 現狀 | Hermes 下一步 |
|---|---|---|---|---|
| Enforcement layer | `pre_tool_use` runtime hook | N/A（知識系統） | `secret-leak-prevention` 是事後掃描 | 升級為 `pre_tool_use` + `before_llm_call` hook |
| Two-layer separation | Governance ≠ Permission | N/A | 只有 tool-level scoping | 拆分 L1 governance（Hestia 定義）vs L2 permission（per-cron） |
| Single-writer | N/A | WikiWorker queue | 無 concurrency control | write queue + content-hash tool call ID |
| L1 immutability | N/A | `wiki/artifacts/` append-only | autonomous_notes/ 雙向混用 | L1/L2 分離 + contradiction detection |
| Staleness | N/A | 動態衰減公式 | 靜態 TTL | 採用 WUPHF staleness formula |
