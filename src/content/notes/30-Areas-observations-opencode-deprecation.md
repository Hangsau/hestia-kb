---
_slug: 30-Areas-observations-opencode-deprecation
_vault_path: 30-Areas/observations/opencode-deprecation.md
title: OpenCode 訂閱取消後的遷移（2026-06-08）
created: '2026-06-09'
updated: '2026-06-15'
type: observation
tags: []
status: budding
---

# OpenCode 訂閱取消後的遷移（2026-06-08）

## 時間線

1. Psyche 的 auxiliary（title_generation、compression、curator 等）全部指向 `opencode-go/deepseek-v4-flash`
2. OpenCode Monthly quota 耗盡（HTTP 429），導致所有 auxiliary call 失敗
3. 使用者取消訂閱（`opencode-go` provider 不再需要）

## 遷移項目

Psyche config.yaml 中移除：
- 7 個 auxiliary 的 `provider: opencode-go` → 改為 `minimax-oauth`
- `web_extract` auxiliary 的 `opencode-go` model reference
- `fallback_providers` 中的 `opencode-go`
- `providers` section 中的 `opencode-go` 定義

Talos 的 config 原本就已是 `minimax-oauth`，不受影響。

## 驗證

```bash
grep -r "opencode" ~/.hermes/profiles/psyche/config.yaml  # 0 matches
```