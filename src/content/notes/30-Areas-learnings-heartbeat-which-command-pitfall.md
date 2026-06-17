---
_slug: 30-Areas-learnings-heartbeat-which-command-pitfall
_vault_path: 30-Areas/learnings/heartbeat-which-command-pitfall.md
title: Heartbeat which 命令陷阱
date: 2026-05-17
tags:
- heartbeat
- arch-linux
- pitfall
- maintenance
created: '2026-05-17'
updated: '2026-06-15'
type: learning
status: budding
---

# Heartbeat `which` 命令陷阱

## 問題

Heartbeat v2 的自主維護 skill 使用 `which` 指令來驗證 INSTALL 提案中的工具是否已安裝。

但在 Arch Linux 環境中，`which` 並不存在，導致：
- 誤報 NOT FOUND
- 產生假的 PARTIAL 狀態
- 生成無必要的「修復」指令

## 案例

`mcporter` 安裝提案（WS-012）被標記為 PARTIAL，理由是 `which mcporter → NOT FOUND`。
實際上 `/usr/bin/mcporter` 早已存在，版本 0.11.1，PATH 正常。

## 修復

INSTALL 提案 DONE 驗證清單改用：

```bash
command -v <tool>    # POSIX 标准，检查 PATH
ls -la /usr/bin/<tool>  # 直接确认文件存在
```

**不能用**：`which`（Arch Linux 未安裝）

## 相關

- Skill: `heartbeat-v2-autonomous-maintenance`
- 發現 session: `session_20260517_113253_f406d5`
