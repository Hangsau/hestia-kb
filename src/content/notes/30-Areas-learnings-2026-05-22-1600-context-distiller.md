---
_slug: 30-Areas-learnings-2026-05-22-1600-context-distiller
_vault_path: 30-Areas/learnings/2026-05-22-1600-context-distiller.md
title: Context Distiller 回顧（16:00）
date: 2026-05-22
tags:
- distillation
- context-distiller
updated: 2026-05-22T16:00+08:00
created: '2026-05-22'
type: learning
status: budding
---

# Context Distiller 回顧（16:00）

## 覆盤 session 數：5

- `session_20260522_091245_10acb8` — 用戶 DM（Hearth sync，cron 狀態回報）
- `session_20260522_151508_0f49f2` — heartbeat autonomous maintenance cycle
- `session_20260522_153938_37b945` — heartbeat autonomous maintenance cycle
- `session_cron_b48ea41a8c8d_20260522_150034` — internal-heartbeat cron（完整健康報告）
- `session_cron_c27c167b958c_20260522_150034` — vault-sync（silent）

## 發現

### 1. MCP Server 部署：uvx 會 hang

從 `hermes-agent` skill review session（15:15）確認：
- `uvx --from mcp-agent python3` 當 script 呼叫 `create_mcp_server_for_app()` 時會 hang
- 原因：uvx 的 transient context 沒有 `mcp-agent` 自己的 imports scope
- **解法**：建立專用 venv + 直接路徑引用
  ```bash
  python3.12 -m venv --system-site-packages /tmp/mcp-agent-venv
  ```
  然後在 cron config 直接用 `/tmp/mcp-agent-venv/bin/python` 而非 `uvx`

### 2. Proposal 欺騙性 failure mode

`heartbeat-v2-autonomous-maintenance` 在 15:39 cycle 發現：
- WS-010 的 SKILL.md 宣稱「proposal file 存在於 `proposals/ws010*.md`」
- 實際上那個檔案不存在
- 這是「已實作」的 proposal claim 卻對應空事實的 failure mode
- **修補**：已更新 skill，加入 proposal premise validation 邏輯

### 3. 系統狀態摘要

| 項目 | 狀態 |
|------|------|
| Cron jobs | ✅ 15 全 clean |
| Heartbeat age | ✅ < 12h |
| Hearth sync | ✅ 無待處理 |
| Vault ahead of local | ✅ ingest 正常 |

## 無需寫入 vault 的觀測

- cron heartbeat 報告格式穩定，無新學習
- vault-sync 穩定（silent = 正常）
- LLM eval + Agent Memory exploration 筆記已由自主探索寫入 vault，無需重複