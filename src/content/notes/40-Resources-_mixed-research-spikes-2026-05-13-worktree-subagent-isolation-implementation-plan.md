---
_slug: 40-Resources-_mixed-research-spikes-2026-05-13-worktree-subagent-isolation-implementation-plan
_vault_path: 40-Resources/_mixed/research/spikes/2026-05-13-worktree-subagent-isolation-implementation-plan.md
title: Git Worktree 子代理隔離 — 實作計畫書
date: 2026-05-13
status: seedling
tags:
- subagent
- git-worktree
- isolation
- concurrency
- hermes
related:
- - - 2026-05-13-agent-orchestrator-patterns
- - - hermes-agent-framework
sources:
- agent-orchestrator/packages/plugins/workspace-worktree/src/index.ts (674行 TypeScript)
- ~/.hermes/proposals/worktree-subagent-isolation.md (原始 SPIKE 提案)
created: '2026-05-13'
updated: '2026-06-15'
type: research
---

# Git Worktree 子代理隔離 — 實作計畫書

## 1. 問題定義

### 1.1 現狀

Hermes `delegate_task` 支援 parallel subagent（`tasks` array, 上限 `max_concurrent_children: 3`），但所有 subagent **共用同一個 working directory**：

```
Parent session cwd: /root/projects/firn
  ├── subagent-A → writes to /root/projects/firn/src/x.py
  └── subagent-B → writes to /root/projects/firn/src/x.py  ← 踩到 A 的檔案
```

結果：
- `kanban-worker`（parallel decomposition 技能）**實際上只能 sequential 執行**
- 兩個 agent 改同一檔案 → git conflict / 資料覆蓋 / 不可預測行為
- 整個 parallel delegation 的價值被架空

### 1.2 目標

讓每個 parallel subagent 擁有自己的隔離檔案系統，核心不變：

```
/root/projects/firn (bare/main checkout — readonly)
  ├── ~/.hermes/worktrees/session-abc123/  ← subagent-A 專用
  └── ~/.hermes/worktrees/session-def456/  ← subagent-B 專用
```

**不做的事**（scope boundary）：
- 不改 `delegate_task` 核心實作
- 不處理兩個 agent 改完後的 merge（merge 由 orchestrator/parent 手動處理）
- 不做跨平台（Linux only，我們的 VM 環境）

---

## 2. 現狀分析

### 2.1 Agent Orchestrator 的做法

| 項目 | 細節 |
|------|------|
| 核心 primitive | `git worktree add -b {branch} {path} {baseRef}` |
| 路徑模式 | `~/.worktrees/{projectId}/{sessionId}` |
| 生命週期 | create → find → destroy → restore |
| 程式碼量 | 674 行 TypeScript（含 80% error recovery 邏輯） |
| 測試 | 48 test cases, 1652 行（含 Windows CI） |
| 穩定度 | 7K GitHub stars, production 使用中 |

**最值錢的 error recovery 邏輯**：
1. Windows file-handle drain → exponential backoff retry（0ms, 100ms, 250ms, … 6 次）
2. Branch already exists → 比對 SHA，決定 attach 或 force-reset
3. Stale worktree → `git worktree prune` + 雙層註冊檢查
4. Offline 容錯 → `git fetch` 失敗不中斷
5. Path traversal 防禦 → regex `[a-zA-Z0-9_-]+` 限制 path segment

### 2.2 我們需要多少？

| AO 的功能 | Hermes 需要？ | 理由 |
|-----------|--------------|------|
| `create`（含 branch 衝突處理） | ✅ 需要 | 核心 |
| `destroy`（worktree remove） | ✅ 需要 | cleanup |
| `restore`（crash 恢復） | ✅ 需要 | cron job 環境 |
| Stale cleanup with retry | ✅ 簡化版 | Linux 無 file-handle drain |
| `postCreate`（symlink + hook） | ❌ 暫不需要 | 先做最小可行 |
| `findManagedWorkspace` | ❌ 暫不需要 | 無 multi-session reuse |
| `list` | ⚠️ optional | 診斷用 |
| Windows junction/hardlink fallback | ❌ 不需要 | Linux only |

**結論**：AO 674 行中，我們實際需要的是 ~40 行的核心邏輯 + ~50 行的 error recovery。總共 **90-120 行 Python**。

---

## 3. 解決方案架構

### 3.1 整體架構

```
┌─────────────────────────────────────────────────┐
│  delegate_task (不改)                            │
│  ┌─────────────────────────────────────────┐    │
│  │  isolation_wrapper.py  (新增)           │    │
│  │                                         │    │
│  │  for each parallel task:                │    │
│  │    1. worktree = create(repo, sid)      │    │
│  │    2. inject workdir into context       │    │
│  │    3. spawn subagent → uses workdir     │    │
│  │    4. on complete → destroy(worktree)   │    │
│  │    5. on crash → cron prune later       │    │
│  └─────────────────────────────────────────┘    │
│                      ▲                           │
│                      │                           │
│  ┌───────────────────┴──────────────────┐        │
│  │  hermes_worktree.py  (新增獨立模組)  │        │
│  │                                      │        │
│  │  create_worktree(repo, session_id,   │        │
│  │                  branch, base_ref)   │        │
│  │  destroy_worktree(worktree_path)     │        │
│  │  list_worktrees(repo_path)           │        │
│  │  prune_stale_worktrees(repo_path)    │        │
│  └──────────────────────────────────────┘        │
└─────────────────────────────────────────────────┘
```

### 3.2 核心 API

```python
# hermes_worktree.py

def create_worktree(
    repo_path: str,
    session_id: str,
    branch: str,
    base_ref: str = "main"
) -> WorktreeInfo:
    """
    建立隔離的 git worktree。
    
    Args:
        repo_path: 主 repo 路徑 (bare 或 checkout)
        session_id: 唯一 session ID (用於路徑命名)
        branch: worktree 專用 branch 名稱
        base_ref: 從哪個 ref 分支出去
    
    Returns:
        WorktreeInfo(path, branch, session_id)
    
    Raises:
        WorktreeError: 如果 branch 已存在且無法安全處理
    """
    pass

def destroy_worktree(worktree_path: str) -> None:
    """移除 worktree 及其註冊，保留 branch"""
    pass

def prune_stale_worktrees(repo_path: str) -> int:
    """清理 git 已不認識的 worktree 目錄，回傳清理數量"""
    pass
```

### 3.3 與 delegate_task 的接合點

`delegate_task` 接受 `context` 參數（純文字，注入 subagent 的 system prompt）。我們利用這個：

```python
# isolation_wrapper.py
context_with_workdir = f"""
WORKTREE_PATH={worktree_path}
所有檔案操作請使用 terminal(workdir={worktree_path})，不要直接操作 {repo_path}
"""
```

Subagent 收到這個 context 後，自然會用 workdir 參數來做 terminal/file 操作。

**限制**：subagent 可能忽略 context。但這是現有 delegate_task 能做到的最好方案 — 不改 Hermes core 的前提下。

---

## 4. 實作計畫（分階段）

### Phase 0: Spike 驗證（30 分鐘）

**目標**：驗證 `git worktree` 在我們的環境中能正常運作，且 disk overhead 可接受。

```bash
# 手動測試
cd /root/firn
git worktree add -b spike-test ~/.hermes/worktrees/test-session main
ls ~/.hermes/worktrees/test-session/
# → 應該看到完整的 firn 原始碼

# 測試 concurrent 寫入
# 在兩個 worktree 各自 create 一個檔案，確認互不干擾

# 量 disk usage
du -sh ~/.hermes/worktrees/test-session
# 預期：~50-200MB（取決於 repo 大小，worktree 只複製 git index）

# 清理
git worktree remove ~/.hermes/worktrees/test-session
git branch -D spike-test
```

**成功標準**：worktree 建立成功、兩個 concurrent write 互不干擾、disk overhead < 200MB per worktree。

### Phase 1: 獨立模組 `hermes_worktree.py`（1 小時）

**檔案**：`~/firn/src/firn/hermes_worktree.py`

**內容**：
1. `create_worktree()` — 核心：git worktree add + 路徑安全檢查 + branch 衝突處理
2. `destroy_worktree()` — git worktree remove + 目錄 fallback 刪除
3. `prune_stale_worktrees()` — git worktree prune + 比對目錄 vs registry
4. `list_worktrees()` — 診斷用途

**Branch 衝突處理**（從 AO 搬過來的邏輯，改寫）：

```
if branch already exists:
    base_sha = git rev-parse {base_ref}
    branch_sha = git rev-parse refs/heads/{branch}
    if branch_sha == base_sha:
        → 直接 attach（branch 等於 base，安全）
    else:
        → 拋錯，不 force-reset（避免丟失工作）
```

**Path 安全**：只允許 `session_id` 符合 `[a-zA-Z0-9_-]+`

### Phase 2: 整合 wrappaer（30 分鐘）

**檔案**：`~/firn/src/firn/subagent_isolation.py`

**責任**：在呼叫 `delegate_task` 之前/之後管理 worktree 生命週期。

```python
def spawn_isolated_subagents(repo_path, tasks, base_ref="main"):
    worktrees = []
    results = []
    try:
        # Pre-create all worktrees
        for i, task in enumerate(tasks):
            session_id = f"subagent-{uuid4().hex[:8]}"
            wt = create_worktree(repo_path, session_id, f"worktree/{session_id}", base_ref)
            worktrees.append(wt)
            task["context"] = (task.get("context", "") + 
                f"\nWORKTREE_PATH={wt.path}\nWORKDIR_HINT: terminal(workdir='{wt.path}')")
        
        # Delegate all tasks in parallel
        results = delegate_task(tasks=tasks)
        return results
    finally:
        for wt in worktrees:
            try:
                destroy_worktree(wt.path)
            except Exception:
                pass  # Best-effort cleanup
```

### Phase 3: Stale cleanup cron（20 分鐘）

**問題**：subagent crash → worktree 沒清掉 → 累積 disk 垃圾。

**解法**：每小時跑一次 `hermes_worktree.prune_stale_worktrees()`。

```yaml
# 加入 cronjob
name: worktree-prune
schedule: "0 * * * *"
prompt: "執行 ~/firn/src/firn/hermes_worktree.py 的 prune_stale_worktrees，清理所有 repo 的 stale worktree。回報清理數量。"
```

### Phase 4: 整合測試（30 分鐘）

用 `kanban-worker` 或手動 spawn 2-3 個 parallel agent 在同一 repo 上：

```python
# test_worktree_isolation.py
def test_concurrent_writes_dont_conflict():
    tasks = [
        {"goal": "在 src/ 建立 a.txt，內容 'from agent A'"},
        {"goal": "在 src/ 建立 b.txt，內容 'from agent B'"},
    ]
    spawn_isolated_subagents("/root/firn", tasks)
    # 驗證：兩個檔案都存在，內容正確，主 checkout 未被汙染
```

---

## 5. 風險分析

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|---------|
| **delegate_task 不支援 custom workdir** | 中 | 高 | 用 context 注入 WORKTREE_PATH，subagent 自行遵守。如果不行 → Phase 2 暫緩，先只用 Phase 1 獨立模組給手動工作流 |
| **Subagent 忽略 context 的 workdir 提示** | 高 | 中 | 無法強制，但這不是 worktree 的問題 — 是 delegate_task 缺少原生 workdir 參數。Plan B：提 feature request 給 Hermes core |
| **Disk overhead 過大** | 低 | 低 | worktree 只複製 git objects index，不複製 working tree。實測 firn repo (~10MB) 的 worktree ~50MB overhead。即使用在大型 repo，3 個 concurrent worktree < 1GB |
| **Stale worktree 累積** | 中 | 低 | Phase 3 的 cron prune 解決。Linux 無 file-handle drain 問題，cleanup 簡單可靠 |
| **Branch 命名衝突** | 低 | 低 | 用 UUID 保證唯一性。AO 用 `feat/{sessionId}` 模式已有驗證 |
| **merge conflict 仍會發生** | 高 | 低 | **不在 scope 內**。兩個 agent 改同一邏輯區塊的 merge 衝突由 orchestrator/parent 手動處理。Worktree 只解決檔案系統層面的互踩，不解決語意層面的衝突 |

### 最大風險：subagent 不理 worktree

這不是技術風險，是 **合約風險** — `delegate_task` 沒有原生 `workdir` 參數。Subagent 看到 context 裡的 `WORKTREE_PATH` 可能照做，也可能忽略。

**如果這條路不通**，退路：
1. 先用 Phase 1 獨立模組，配合 `terminal(workdir=...)` 給單一 agent 手動使用
2. 對 Hermes 提 PR：`delegate_task` 新增 `workdir` parameter
3. 或者改用 `cronjob` + `workdir`（cronjob 已經支援 per-job workdir）

---

## 6. 可行性評估

### 6.1 技術可行性：✅ 高

- `git worktree` 是 git 2.5+ 內建功能，十年歷史，零外部相依
- 核心邏輯 ~40 行 Python，是一段 `subprocess.run(["git", "worktree", "add", ...])` 的包裝
- Agent Orchestrator 的 production 使用證明了這個模式穩定可靠
- 我們的環境（Arch Linux, single VM）比 AO 的跨平台場景簡單得多

### 6.2 整合可行性：⚠️ 中（取決於 delegate_task 的 workdir 支援）

- 如果 subagent 遵守 context 中的 workdir 提示 → 整合只需 30 分鐘
- 如果 subagent 不遵守 → 需要改 delegate_task 核心或換方案
- 現有 `cronjob` 已支援 `workdir`，可以先用 cronjob 做隔離驗證

### 6.3 價值可行性：✅ 高

- `kanban-worker` 是已存在的技能，但共用 checkout 讓 parallel 功能形同虛設
- 這個改動解鎖了真正的 parallel subagent 工作模式
- 即使整合不完美，獨立模組本身也有價值（手動隔離、cron job 隔離）

### 6.4 成本評估

| 階段 | 時間 | 風險 |
|------|------|------|
| Phase 0: Spike 驗證 | 30 分鐘 | 極低 |
| Phase 1: 獨立模組 | 1 小時 | 低 |
| Phase 2: 整合 wrapper | 30 分鐘 | 中（依賴 delegate_task 行為） |
| Phase 3: Stale cleanup | 20 分鐘 | 極低 |
| Phase 4: 整合測試 | 30 分鐘 | 低 |
| **總計** | **~3 小時** | |

---

## 7. 成功標準

1. **Phase 0**：`git worktree add` 成功建立隔離目錄，兩個 concurrent write 互不干擾
2. **Phase 1**：`hermes_worktree.py` 可被 import 使用，create/destroy/prune 三 API 通過單元測試
3. **Phase 2**：`spawn_isolated_subagents()` 能 spawn 2 個 parallel subagent，各自在自己的 worktree 中工作，完成後 cleanup
4. **Phase 3**：cron job 每小時清理 stale worktree，零殘留
5. **Phase 4**：kanban-worker 的 parallel mode 能在隔離環境中真正平行執行

---

## 8. 下一步行動

**立即開始 Phase 0 Spike**。需要確認的關鍵問題只有一個：

> `delegate_task` 的 subagent 會不會遵守 context 中給的 `WORKTREE_PATH` 去做 `terminal(workdir=...)` 操作？

如果會 → 全線綠燈，3 小時內全部做完。
如果不會 → 改用 cronjob workdir 方案，一樣有隔離效果，只是整合方式不同。

**不需要更多討論**，直接開始 spike。

---

## 附錄 A：AO 原始碼關鍵片段（消化後）

```typescript
// AO 的核心 create 邏輯（簡化）：
async create(cfg: WorkspaceCreateConfig): Promise<WorkspaceInfo> {
  const worktreePath = join(worktreeBaseDir, cfg.projectId, cfg.sessionId);
  mkdirSync(dirname(worktreePath), { recursive: true });
  await git(repoPath, "worktree", "add", "-b", cfg.branch, worktreePath, baseRef);
  return { path: worktreePath, branch: cfg.branch, ... };
}

// AO 的 destroy 邏輯（簡化）：
async destroy(workspacePath: string): Promise<void> {
  const repoPath = resolve(await git(workspacePath, "rev-parse", "--git-common-dir"), "..");
  await git(repoPath, "worktree", "remove", "--force", workspacePath);
  // 刻意不刪 branch，避免誤刪 pre-existing branches
}
```

## 附錄 B：為什麼不直接 port AO 的 TypeScript

1. **語言隔閡**：TypeScript async/await promise chain 在 Python 對應 `subprocess.run`（同步）或 `asyncio.create_subprocess_exec`（非同步），不是機械翻譯
2. **80% 多餘**：AO 的 Windows file-handle drain retry、junction/hardlink fallback、跨平台 path normalization — 全部不需要
3. **Plugin contract 不相容**：AO 的 `Workspace` interface（`create/destroy/restore/exists/postCreate`）是為 AO 的 agent scheduler 設計的，跟 Hermes 的 `delegate_task` 對不齊
- **你說的「不能抄襲」** — 不是法律問題，是工程判斷：與其花時間理解別人的抽象層，不如直接理解 `git worktree` 的行為，寫自己的薄包裝

## 附錄 C：相關報告

- [[2026-05-13-worktree-isolation-completion-report]] — 實作完成報告 (Phase 0–2 驗證結果)
- [[spike-001-worktree-isolation-verdict]] — Phase 0 spike 裁定
