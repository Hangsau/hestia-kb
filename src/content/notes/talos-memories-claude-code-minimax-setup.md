---
_slug: talos-memories-claude-code-minimax-setup
_vault_path: talos-memories/claude-code-minimax-setup.md
title: Claude Code + MiniMax-M3 整合設定（2026-06-08）
created: '2026-06-09'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Claude Code + MiniMax-M3 整合設定（2026-06-08）

## 環境

- Claude Code 版本：2.1.168，安裝在 `/usr/bin/claude`
- 設定檔：`~/.claude/settings.json`
- Endpoint：`https://api.minimax.io/anthropic`
- Auth Token：复用 `~/.hermes/auth.json` 裡的 OAuth token（MiniMax 月費訂閱，到期 2027）

## 設定方式

```bash
export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
export ANTHROPIC_AUTH_TOKEN="复用 auth.json 的 OAuth token"
```

settings.json 內容：
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<复用 OAuth token>"
  },
  "allowDangerouslySkipPermissions": true
}
```

之後直接打 `claude` 即可使用 MiniMax-M3。

## 背景執行模式（推薦）

Claude Code 預設是互動模式，需要 TTY。透過背景模式可從 cron 執行：

```python
terminal(
    command="claude -p '任務描述'",
    background=True,
    notify_on_complete=True
)
```

- `background=true` + `notify_on_complete=true`：任務完成後系統通知，不受 600s 上限約束
- 120s timeout 只適用於等待方，背景任務本身會跑到完成
- Claude Code 可能卡在互動式確認，需要 `--allow-dangerously-skip-permissions`

## Inbox 機制

Claude Code 已配置監聽：
- 輸入：`/root/.hermes/for-claude/` → Claude Code 處理
- 輸出：`/root/.hermes/claude-outbox/` 或 `/root/.hermes/claude-inbox/`

## 常見問題

- Segfault：npx 版本與主程式衝突，用 `npm install -g @anthropic-ai/claude-code` 直接安裝
- 無法執行系統指令：加 `--allow-dangerously-skip-permissions`