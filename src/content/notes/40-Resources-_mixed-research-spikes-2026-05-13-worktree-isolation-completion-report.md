---
_slug: 40-Resources-_mixed-research-spikes-2026-05-13-worktree-isolation-completion-report
_vault_path: 40-Resources/_mixed/research/spikes/2026-05-13-worktree-isolation-completion-report.md
title: Git Worktree 子代理隔離 — 實作完成報告
date: 2026-05-13
status: seedling
tags:
- subagent
- git-worktree
- isolation
- concurrency
- hermes
- implementation
related:
- - - 2026-05-13-worktree-subagent-isolation-implementation-plan
- - - spike-001-worktree-isolation-verdict
created: '2026-05-13'
updated: '2026-06-15'
type: research
---

# Git Worktree 子代理隔離 — 實作完成報告

## 摘要

完成 Hermes `delegate_task` parallel subagent 的檔案系統隔離方案，使用 `git worktree` 給每個 subagent 獨立的 working directory，解決共用 checkout 的檔案互踩問題。全部四個階段完成，通過端對端測試。

## 問題回顧

`delegate_task` 可以平行 spawn 最多 3 個 subagent，但它們共用同一個 working directory。兩個 agent 改同一檔案 → 衝突/覆蓋。結果 `kanban-worker` 的 parallel mode 形同虛設。

## 解法

```
main repo (readonly)
  ├── ~/.hermes/worktrees/session-0 → subagent A 專用
  └── ~/.hermes/worktrees/session-1 → subagent B 專用
```

`git worktree`（git 2.5+ 內建）可以在同一個 repo 上建立多個獨立 checkout。每個 subagent 拿到自己的沙盒，真正並行。

## 實作成果

### Phase 0: Spike 驗證 ✓

| 測試 | 結果 |
|------|------|
| `git worktree add` | 正常建立（git 2.54.0） |
| 平行寫入（純 terminal） | 時間戳交錯，零污染 |
| **subagent 尊重 WORKTREE_PATH** | 兩個 subagent 各自在自己的 worktree 工作 |
| 交叉污染 | 無 |
| crash 恢復（prune） | 成功清除 stale metadata |

### Phase 1: `hermes_worktree.py` ✓

**檔案**：`~/firn/src/firn/hermes_worktree.py`（~200 行）

核心 API：
- `create_worktree(repo, session_id, branch, base_ref)` → WorktreeInfo
- `destroy_worktree(path)` — 強制清除含 untracked files
- `prune_stale_worktrees(repo)` → int — crash 殘留清理
- `list_worktrees(repo)` → 診斷
- `ensure_pristine(repo)` → 清空所有 worktree（測試用）

全部 4 個單元測試通過。

### Phase 2: `subagent_isolation.py` ✓

**檔案**：`~/firn/src/firn/subagent_isolation.py`（~200 行）

工作流三步驟：
1. `prepare_isolated_tasks(repo, tasks, session_id)` — 建立 worktree，注入 `WORKTREE_PATH`
2. `delegate_task(tasks=modified_tasks)` — spawn subagent
3. `cleanup_session(session_id)` — 清除 worktree

端對端測試：兩個 parallel subagent 同時在 firn repo 上工作，零交叉污染，cleanup 完全清除。

### Phase 3: 自動維護 ✓

Cron job `worktree-prune`（job_id: dab9401ac8d8）
- 排程：每小時 `0 * * * *`
- 任務：對 firn repo 執行 `prune_stale_worktrees()`
- 只清理 git metadata，不碰檔案

### Phase 4: 文件 ✓

- 技能文件：`autonomous-ai-agents/worktree-subagent-isolation`
- Spike verdict：`obsidian-vault/research/spike-001-worktree-isolation-verdict.md`
- 本報告：`obsidian-vault/research/2026-05-13-worktree-isolation-completion-report.md`
- GitHub 摘要：`managed-agents-research/reports/2026-05-13-worktree-isolation-plan.md`

## 使用方式（給未來 session）

見 `worktree-subagent-isolation` 技能，核心三步驟：

```bash
# 1. Prepare
cd ~/firn && python3 -c "
import sys; sys.path.insert(0, 'src')
from firn.subagent_isolation import prepare_isolated_tasks
modified = prepare_isolated_tasks('/root/firn', tasks, 'my-session')
print(modified)  # → 餵給 delegate_task
"

# 2. delegate_task(tasks=<modified>)

# 3. Cleanup
cd ~/firn && python3 -c "
import sys; sys.path.insert(0, 'src')
from firn.subagent_isolation import cleanup_session
cleanup_session('my-session')
"
```

## 技術決策記錄

1. **不 port Agent Orchestrator**：674 行 TypeScript，80% 處理 Windows edge case，不適用
2. **自研 Python 版**：~200 行（含 CLI），核心 ~40 行
3. **不改 Hermes core**：透過 `context` 傳遞 `WORKTREE_PATH`，subagent 自行遵守
4. **不處理 merge**：檔案系統隔離，語意層衝突仍由 orchestrator 手動處理

## 已知限制

- Subagent 需自行遵守 `WORKTREE_PATH`（無強制機制，但實測會遵守）
- 每個 worktree ~50-200MB disk overhead
- Session 未 cleanup 會殘留 worktree（cron prune 補救）
- Linux only

## 成功標準驗證

| 標準 | 狀態 |
|------|------|
| `git worktree add` 成功建立隔離目錄 | ✓ |
| 兩個 concurrent write 互不干擾 | ✓ |
| `hermes_worktree.py` create/destroy/prune API 通過測試 | ✓ |
| 兩個 parallel subagent 真正並行、零交叉污染 | ✓ |
| Cron job 每小時清理 stale worktree | ✓ |
