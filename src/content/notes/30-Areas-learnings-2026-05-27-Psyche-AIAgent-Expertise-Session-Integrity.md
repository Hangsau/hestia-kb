---
_slug: 30-Areas-learnings-2026-05-27-Psyche-AIAgent-Expertise-Session-Integrity
_vault_path: 30-Areas/learnings/2026-05-27-Psyche-AIAgent-Expertise-Session-Integrity.md
tags:
- hermes
- psyhe
- learning
- session
- self-awareness
source: 20260527_102059_5f1d10
created: '2026-05-27'
title: Psyche AIAgent Expertise + Session Integrity Learning
updated: '2026-06-15'
type: learning
status: budding
---

# Psyche AIAgent Expertise + Session Integrity Learning

## 專家定義（三維度）

1. **設計層面**：可以設計出新的 AI agent
2. **除錯層面**：可以修自己目前 Hermes agent 的問題
3. **溝通層面**：可以讓大家了解 AI agent 如何運作

**切入點**：
- 建立 `vault/system/hermes-architecture.md`：profile、tool、cron、memory、message flow 模塊地圖
- 讀 `/usr/local/lib/hermes-agent/AGENTS.md`（1132行）+ `run_agent.py` + `model_tools.py`
- 每週輸出：用「類比 + 具體例子」寫進 vault

## Session Integrity 教訓

**事件**（session `20260527_102059_5f1d10`）：
Psyche 分析 vault-auto-push failure，給了一個敘述（"pre-commit hook 設計問題"），但從未實際執行 `git diff --staged` 或看過 diff line 1671 的實際內容。user 問「有幫助到你成為 AI agent 專家嗎」，回答「沒有」。

**根本問題**：用「好像合理的敘述」代替「我確認過」。

**原則**：
> 每個爭議點都要找到 **source of truth**（實際代碼/工具輸出/文件），不要在驗證前編故事。

**具體做法**：
1. 遇到不懂的：直接找 source，不靠推理
2. 給答案之前：先說「我會做 X、Y、Z 來確認，在我驗證完之前不會給你一個確定的答案」
3. 不在拿到結果之前編故事

## Source of Truth 位置（已確認）

- Hermes source: `/usr/local/lib/hermes-agent/`
- 架構文件: `/usr/local/lib/hermes-agent/AGENTS.md`
- 核心代碼: `run_agent.py`（AIAgent class）、`model_tools.py`（tool orchestration）
- Hermes 是真實 open source 專案：NousResearch/Hermes-Agent on GitHub

## 相關存回

- vault-auto-push failure 根本原因：auto-git-push.sh（Talos profile）沒有修 pre-scan block，只有 vault-safe-push.sh（default profile）修了。Session JSONs 已移至 `/root/talos-sessions-archive/`。
