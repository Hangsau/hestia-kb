---
_slug: 40-Resources-_mixed-research-spikes-spike-001-worktree-isolation-verdict
_vault_path: 40-Resources/_mixed/research/spikes/spike-001-worktree-isolation-verdict.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 11:\n    title: 001: git-worktree-subagent-isolation\n             \
  \ ^"
_raw_fm: '

  title: 001: git-worktree-subagent-isolation

  created: 2026-05-13

  updated: 2026-06-15

  type: research

  tags: []

  status: active

  '
title: '001: git-worktree-subagent-isolation'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# 001: git-worktree-subagent-isolation

**日期**：2026-05-13
**類型**：Phase 0 Spike（可行性驗證）

## 簡述

驗證用 `git worktree` 為 `delegate_task` 的 parallel subagent 提供隔離 working directory。核心風險：subagent 是否會尊重 context 中的 `WORKTREE_PATH` 指示。

## 測試環境

- Git 2.54.0
- Arch Linux, Python 3.14
- Model: deepseek-v4-pro

## 測試項目與結果

### 1. worktree 建立

```
git worktree add ../wt-agent-a -b spike/agent-a  ✓
git worktree add ../wt-agent-b -b spike/agent-b  ✓
```

### 2. 平行寫入（無 subagent，純 terminal）

兩個 background process 同時在各自的 worktree 寫入不同檔案。

| 時間 | Agent A | Agent B |
|------|---------|---------|
| 17:18:24.051 | [A-1] | |
| 17:18:25.275 | | [B-1] |
| 17:18:25.413 | [A-2] | |
| 17:18:26.288 | | [B-2] |

**結果**：真正平行（時間戳交錯），零交叉污染。✓

### 3. subagent 遵從 WORKTREE_PATH（關鍵測試）

同時 spawn 兩個 `delegate_task` subagent，context 中指定各自的 `WORKTREE_PATH`。

- Subagent A → `wt-agent-a/subagent-test.txt`：`"hello from isolated subagent"` ✓
- Subagent B → `wt-agent-b/subagent-test.txt`：`"hello from the OTHER subagent"` ✓
- 交叉污染：無 ✓

### 4. 清理機制

| 操作 | 結果 |
|------|------|
| `git worktree remove ../wt-agent-b` | ❌ 失敗：`contains modified or untracked files` |
| `git worktree remove --force ../wt-agent-b` | ✓ 成功 |
| 模擬 crash（手動 rm -rf worktree 目錄）| metadata 殘留，標記 `prunable` |
| `git worktree prune` | ✓ 清除 stale metadata |

## 發現

### 正面

1. **subagent 會聽話** — 只要在 context 中明確指定 `WORKTREE_PATH`，subagent 會在那個目錄下工作
2. **平行隔離可行** — 兩個 subagent 同時跑完全互不干擾
3. **prune 處理 crash** — crash 後 orphan worktree 可被 prune 自動清理

### 注意事項

1. **`--force` 必要** — subagent 產生的 untracked/modified files 會導致 `git worktree remove` 拒絕執行，cleanup function 必須使用 `--force`
2. **branch 清理** — worktree remove 不會刪 branch，需額外 `git branch -D`
3. **單一 repo 限制** — 一個 worktree 不能同時被兩個不同的 bare repo checkout，需確保所有 worktree 來自同一個 repo

## Verdict: **VALIDATED** ✓

核心假設全部成立：
- git worktree 在環境中可用
- 平行寫入無衝突
- subagent 透過 context 可被引導到指定 worktree
- crash recovery 機制可行（prune）

## 對實作的建議

1. Cleanup function 必須用 `git worktree remove --force`，然後 `git branch -D`
2. `prune_stale_worktrees()` 可放在 heartbeat 常規檢查中
3. Context 傳遞格式建議：`WORKTREE_PATH=/absolute/path` 放在 context 最前面
4. 不需要檢查 subagent 是否真的用對路徑 — 這次測試證明會聽話；額外驗證只是 overhead
