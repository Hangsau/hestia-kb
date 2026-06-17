---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-21-1605-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-21-1605-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-21'
confidence: high
title: 記憶與治理的「過期問題」：跨系統通用設計模式
updated: '2026-06-15'
type: research
status: budding
---

# 記憶與治理的「過期問題」：跨系統通用設計模式

**消化筆記**: 2026-05-21-memori-production-memory-engine, 2026-05-17-ultracontext-loom-context-api, 2026-05-17-wuphf-lint-query-prompt-templates, 2026-05-17-wuphf-complete-schema-templates, 2026-05-17-mcp-gateway-deployment-spectrum, 2026-05-17-ralphex-stalemate-detection

六篇看似無關的筆記（記憶引擎、context API、lint pipeline、MCP 部署、autonomous loops）其實都在回答同一個問題：**何時該信任某個陳述，何時該懷疑它已過期**。

---

## Cross-Cutting Theme 1: Staleness/Validity 作為通用治理原子

**支援筆記**: Memori, WUPHF lint, WUPHF schema, Ralphex

### 問題敘述

六篇筆記各自提出了不同場景的「資訊有效性判斷」問題，但解法可以抽象為同一個 framework：

| 場景 | 問題 | 解法 |
|------|------|------|
| Memori entity/process/session | 三層 attribution，哪層的事實最可信？ | 自動 augmentation，背景刷新 |
| WUPHF staleness formula (§8.1) | 如何量化一個 claim 的新舊？ | `days_old × type_weight − confidence × 10 − reinforcement_bonus`，staleness > 20 排除 |
| Ralphex stalemate | 為何 agent 一直 retry 不放棄？ | 連續 N 輪無 progress = stalemate，放棄而非無限期重試 |
| WUPHF temporal validity | 矛盾判斷前要先問：這事實是否已過期？ | `valid_until` 過期的事實不進 contradiction scan |

### 隱藏的共同結構

```
stale_signal = age_factor − reinforcement − confidence
threshold_exceeded → exclude from decision / escalate
```

這適用於：
- **記憶召回**：Memori 的 entity freshness vs Memori 的 session decay
- **治理 lint**：WUPHF contradiction scan 排除 stale facts
- **REPAIR loop**：heartbeat 的 REPAIR 動作一直失敗 = stalemate，需要 escalation
- **已知問題 mute**：目前 Hermes 用硬設 TTL，但 WUPHF 的 `reinforced_at` bump 更優——每次 EVOLVE pass 該 check 就刷新，不需要手動 TTL

### 可行動下一步

實作 `heartbeat/utils.py` 新函數 `_compute_staleness(issue_id)`，公式直接移植 WUPHF §8.1：

```python
staleness = (days_old × type_weight) − (confidence × 10) − reinforcement_bonus
```

其中 `reinforcement_bonus` = EVOLVE 每次 pass 該 issue 就 bump `reinforced_at`。改造 `KNOWN_ISSUES.md` 的 mute 機制：不再用 `muted_until` 硬 TTL，改用 staleness threshold。

---

## Cross-Cutting Theme 2: 職責分離 + Deferral Pattern（工具縮小化）

**支援筆記**: WUPHF lint, WUPHF schema, Ultracontext, MCP gateway deployment

### 問題敘述

四個獨立系統（Go 寫的 CRM lint pipeline、Rust 寫的 context API、Cloudflare/Bifrost MCP gateway、本地 autonomous loop CLI）都演化出同一個架構：**把一個大一統的 tool/action 切成兩個角色，一個專門做窄範圍的事，另一個 defer 到外部**。

| 系統 | Role A（窄） | Role B（Defer） | 代價 |
|------|-------------|----------------|------|
| WUPHF lint | `lint_contradictions.tmpl` — 只 judge，不寫 | Go WikiWorker 根據判斷結果寫入 | 需要 pre-clustered facts |
| WUPHF query | `answer_query.tmpl` — 只 retrieval，不發明 | 拒答 policy（LLM 知道也不准說） | 需要 query classification |
| Ultracontext Code Mode | `portal_codemode_search` + `portal_codemode_execute` | Dynamic Workers sandboxed JS execution | 需要 portal design |
| Cloudflare MCP | 两个 portal tools 替換 52 tools | sandboxes the rest | 94% token reduction |
| Bifrost Code Mode | search + execute | token cost ↓50%, latency ↓40% | 需 MCP server portal |
| Ralphex review | Claude Code 執行 task | Codex 做 external review | 需要 external tool |

### 為何是同一個 pattern

當一個 component 試圖同時做「判斷 + 執行」或「理解 + 生成」時，它會：
1. 吃掉更多 context window（52 tools 全加載）
2. 承擔更多 hallucination risk（retriever 自己發明答案）
3. 角色混淆導致越權（judge 自己寫入）

把「窄的、確定性的」職責給一個 role，「需要創意/執行」的給 deferral layer，是這個 pattern 的核心動機。

### 可行動下一步

實作 `hermes-mcp-tool-compaction` — 一個 post-processing step，发生在 tool call 結果寫入 briefing 之前：

```
tool call 結果 → compaction(prompt) → 保留 path/query/key，丟棄可重建的 output
```

不需要改 prompt，只需要一個 Python post-processing step。這是 Ultracontext 的 **Compaction** 技術在 Hermes 的第一次實作。

具體實作：在 `heartbeat/actions.py` 的 EVOLVE snapshot 写入前，對 file read/tool call 結果做 compaction——保留 `path`、`query`、`key` 等 metadata，移除可從 vault 重建的 content。

---

## 附：Spec-Anchored Prompting（medium confidence，2 篇）

**支援筆記**: WUPHF lint, WUPHF schema

WUPHF 的 prompt template 第一行固定是「Read WIKI-SCHEMA.md Section X」，確保 LLM 行為與規格文件一致而非靠提示詞本身傳遞所有約束。

這與 Ultracontext 的 Context Engineering Framework（五種技術作為顯式分層）是同一哲學：把「領域知識」從 prompt 中抽出來放到規格文件，prompt 只說「查規格」。

對 Hermes 的意義：`HEARTBEAT_MAP.md` 和 `ISSUES.md` 已經是準規格文件，但從未在 prompt 第一行被引用。可以在 `memory-consolidator` 和 `heartbeat` 的 system prompt 开头加一行 `你是 Heartbeat，你的規格文件是 ~/.hermes/maps/heartbeat.md`。

**confidence: medium**（只有 2 篇 WUPHF 系列互相驗證，其他四篇未提及）

**可行動下一步**：在 `skills/memory/memory-consolidator/SKILL.md` 的 system prompt 开头加一行 anchor 到 `HEARTBEAT_MAP.md`。
