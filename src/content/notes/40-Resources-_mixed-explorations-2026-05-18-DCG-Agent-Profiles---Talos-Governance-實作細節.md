---
_slug: 40-Resources-_mixed-explorations-2026-05-18-DCG-Agent-Profiles---Talos-Governance-實作細節
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-DCG-Agent-Profiles---Talos-Governance-實作細節.md
title: DCG Agent Profiles — Talos Governance 實作細節
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agents
- cli
- dcg
- detection
- hermes
- packs
- robot
- session
- talos
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

# DCG Agent Profiles — Talos Governance 實作細節

**日期**: 2026-05-18 | **來源**: prior note untracked leads

**延續自**: [[2026-05-18-Moltis-DCG-Session-Memory-Deep-Dive]]

---

## Source 1: DCG `docs/agents.md` — Agent Profiles Full Docs

**URL**: https://github.com/Dicklesworthstone/destructive_command_guard (raw `docs/agents.md`)

### Hermes Agent 原生支援

DCG 已偵測 Hermes Agent。Detection via：
- `HERMES_AGENT=1`
- `HERMES_SESSION_ID`

Detection priority:
1. `--agent` CLI flag (manual override)
2. Environment variables
3. Parent process inspection
4. `unknown` fallback

### trust_level 是 advisory label，不是 behavioral switch

這是文件明確說明的關鍵設計：

> `trust_level` is an **advisory label**. It is recorded in JSON output... It does **not**, by itself, change which rules fire or how confidence scores are computed.

真正的 behavioral knobs：
- `disabled_packs` — 移除 packs（含 sub-packs）
- `extra_packs` — 新增 packs
- `additional_allowlist` — bypass deny rules
- `disabled_allowlist: true` — ignore ALL allowlist entries

### Robot Mode — 給 AI Agent 的程式化介面

`--robot` flag gives machine-friendly JSON + standardized exit codes:

| Code | Meaning |
|------|---------|
| 0 | Allow |
| 1 | Denied/blocked |
| 2 | Warning |
| 3 | Config error |
| 4 | Parse error |
| 5 | IO error |

DCG 輸出：
```json
{
  "command": "rm -rf /",
  "decision": "deny",
  "agent": {
    "detected": "hermes-agent",
    "trust_level": "medium",
    "detection_method": "environment_variable"
  }
}
```

### Profile Resolution 順序

1. Exact match: `agents.<detected-name>`
2. `agents.unknown` fallback
3. `agents.default` fallback

### 對 Talos Governance 的實作意涵

DCG 的 `agents.unknown` profile = default policy for unrecognized agents. Talos governance 的 enforcement layer 可以直接以 DCG 的 agent detection 為基礎：

```
Talos enforcement decision =
  1. DCG agent detection (Hermes/Talos/custom agents)
  2. Look up agents.<name> profile
  3. Apply disabled_packs/extra_packs/additional_allowlist
  4. DCG Robot Mode JSON → Talos audit trail
```

DCG 覆蓋的 agent 環境變數（HIGH priority for Hermes integration）：
- `HERMES_AGENT=1` / `HERMES_SESSION_ID` — Hermes detection
- `CLAUDE_CODE=1` — Claude Code
- `CODEX_CLI=1` — OpenAI Codex CLI
- `AUGMENT_AGENT=1` — Augment Code

Hermes 沒有在 DCG detection list 中（`HERMES_AGENT=1` 是 detection method 但 list 裡只有 GitHub Copilot/GitHub Copilot CLI），但 DCG 會偵測 `HERMES_SESSION_ID`（Talos 用這個）。

---

## Source 2: `dcg explain` — CLI help

**URL**: N/A (no separate doc page)

`dcg explain` 是 CLI subcommand，用於顯示 command classification 的內部邏輯。沒有單獨的 doc page，內容從 `dcg --help` 和 source code 而來。

Key: `dcg explain <command>` 顯示 DCG 如何分類該命令——包括 matched rule、severity、affected pack。這對理解 DCG 的 classification engine 有幫助，但不需要專門 fetch 文件。

---

## Source 3: Moltis `user_profile_write_mode` — 404 dead lead

**URL**: `https://docs.moltis.org/user_profile.html`

→ 404 (page removed from Moltis docs)

Dead lead. Skip.

---

## 跨文章 Synthesis

DCG agent profiles 的關鍵發現：

1. **Hermes detection 已有** — `HERMES_SESSION_ID` env var，DCG 原生支援
2. **trust_level advisory** — 這與 Talos blueprint 的「two-layer enforcement: policy + agent differentiation」設計一致，但實作上要以 `disabled_packs`/`extra_packs` 為操作 knobs，不是 trust_level 本身
3. **Robot Mode 是關鍵** — Talos audit trail 可以直接 consume DCG Robot Mode JSON，不需要自建 parser

**Actionable**: 立即可做的並不是「安裝 DCG」，而是：
- 確認 Hermes 的 `HERMES_SESSION_ID` 在 cron/interactive 都正確設定（DCG 靠這個偵測 agent）
- 在 `/srv/hearth/` 試 `dcg test <command> --robot` 看看 JSON 輸出格式
- 評估 DCG 的 packs 覆蓋範圍是否滿足 Talos governance 的最低要求

DCG 不是「全部接受或全部拒絕」——它有細粒度的 packs（50+ categories）和 per-agent profile。對 Talos governance 來說，這是比從頭寫 enforcement 更務實的基礎。

## ⏳ 未追蹤

- `dcg explain <command>` 的實際輸出格式（本地 CLI test，不需要 fetch）
- DCG 的 pack 具體 rule sets（`core.filesystem`、`database.postgresql` 等）— 需要看 source code 或跑 `dcg list-packs`
- Talos 的 `HERMES_SESSION_ID` 在 cron session 中是否正確設定（audit check）

## ✅ 探索完成 — 補充驗證 (2026-05-18 20:36 CST)

**DCG Robot Mode 驗證**（`dcg test --robot <cmd>`）：
- `cat` → `allow` ✅
- `rm -rf /` → `deny` (rule: `core.filesystem:rm-rf-root-home`) ✅
- `dcg explain "docker run --rm ubuntu echo test"` → `ALLOW` (162ms, `containers.docker` 未啟用) ⚠️

**結論**：`containers.docker` pack 明確未啟用，`docker run` 暢通。提案的「立即行動」項目仍然有效：需在 `~/.config/dcg/config.toml` 啟用該 pack。

## ✅ 本次探索完成

