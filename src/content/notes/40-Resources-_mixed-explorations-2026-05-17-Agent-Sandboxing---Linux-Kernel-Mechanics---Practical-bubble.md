---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Agent-Sandboxing---Linux-Kernel-Mechanics---Practical-bubble
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Agent-Sandboxing---Linux-Kernel-Mechanics---Practical-bubble.md
title: Agent Sandboxing — Linux Kernel Mechanics + Practical bubblewrap
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- bind
- bubblewrap
- bwrap
- docker
- hermes
- kernel
- mount
- namespace
- senko
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Agent Sandboxing — Linux Kernel Mechanics + Practical bubblewrap

**日期**: 2026-05-17 | **來源**: [[2026-05-17-docker-ai-governance-runtime-enforcement]] 未追蹤 leads → 轉向 Senko blog + Greptile blog（皆為新發現）
**標籤**: #sandboxing #linux-kernel #bubblewrap #containerization #runtime-security
**延續自**: [[2026-05-17-docker-ai-governance-runtime-enforcement]]

## Per-Source Insights

### 1. Senko Rašić — "Sandboxing AI agents in Linux" (blog.senko.net, Feb 2026)

**背景**: Senko 是 bubblewrap (bwrap) 的維護者之一，用自己的 tool 跑 Claude Code。Concrete, opinionated setup。

**他的威脅模型**（明確放棄的部分）:
- ❌ 不防 zero-day kernel bug escape
- ❌ 不防 covert side channel
- ❌ 不防 current project 的資料外洩（自己就是 project owner）
- ✅ 防範的主要風險：API key 誤用、壞掉整個系統

**bubblewrap script 核心設計**:
```
RO bind mounts: /bin, /lib, /lib64, /usr/bin, /usr/lib, /usr/local/bin, /usr/local/lib
RW bind: $HOME/.claude/, $HOME/.cache/, project dir (pwd), .claude.json (fd 3)
Network: 預設允許 outbound（AI provider + internet）
```

**關鍵設計決策**:
1. **Project dir 直接 RW bind**：不用 copy-in/copy-out，IDE 可以直接看到相同檔案，agent 改完馬上可見
2. **Credential injection via fd**：把 `.claude.json` 透過 fd 3 傳入，agent 改了也不會 flush 回硬碟（對比 Docker 的 volume mount 會持久化）
3. **系統路徑完全對應**：所有 `/usr/bin`、`/opt/node` 等直接 bind 進來，所以不需要特殊的環境重建

**strace 用於探索**:
```bash
strace -e trace=open,openat,stat,statx,access -o /tmp/strace.log codex
# 然後檢查 log 看 agent 實際存取了哪些檔案，逐步加到 bwrap script
```

**對 Talos/Hermes 的意義**:
- Hermes 目前是 single process，沒有 filesystem sandbox
- 如果要實作：bubblewrap 適用於 local，Docker 適用於 isolation 更強的環境
- credential injection pattern（fd 傳入而非 mount）是乾淨的做法，避免 agent 意外修改 credential file
- bubblewrap 比 Docker 輕量（無 daemon），適合單機使用

### 2. Greptile — "Sandboxing agents at the kernel level" (greptile.com, Sep 2025)

**核心理念**: 「假設 process 能看到的，它就能傳出去」— 所以要靠 kernel-level enforcement，不是 application-level guard。

**open() syscall 的三層失敗模式**（由淺到深）:

| 層次 | 函數 | 失敗模式 | 隱藏手段 |
|---|---|---|---|
| Late NO | do_open | 權限檢查（chmod） | 檔案存在但讀不到 |
| Middle NO | link_path_walk | 目錄 traversal 權限 + mount 覆寫 | bind mount 覆蓋目錄內容 |
| Early NO | path_init | chroot（改變 process 的 root） | 整棵檔案樹都看不到 |

**Mount namespace 實戰**:
```bash
sudo unshare --mount bash
# 這個 bash 在獨立的 mount namespace
mount --bind /tmp/cover /tmp/a
cat /tmp/a/secret.txt  # No such file
# 另一個 terminal（預設 namespace）仍可見 secret.txt
```

**容器技術的底層就是這些**:
- `clone(2)` + namespace flags → 新 process 有獨立的 mount/uts/pid namespace
- `pivot_root` → 改變 process 的 filesystem root
- Mount namespace 隔離 → mount 操作不影響 host 或其他 container

**Greptile 自己的 production 做法**: rootless Podman container，kernel 強制保證 agent 只能看到被允許的檔案。

**對 Talos/Hermes 的意義**:
- 三層失敗模式對應三種不同程度的隔離強 度
- bwrap/bubblewrap = Late + Middle + Early NO 的組合（mount namespace + chroot-like isolation）
- Docker = 更完整的隔離（含 network namespace、pid namespace 等）
- 如果要選：local 輕量用 bwrap，需要更強隔離時用 Docker/Podman

## Hermes 啟發

### 從 bwrap 到 Hermes 的實體化路徑

Senko 的 script 是給 Claude Code CLI 用的，Hermes 是另一種 agent。但概念可以 transfer：

```
Senko 的威脅模型（明確放棄什麼）→ Hermes 也需要類似的明確宣告
FD-based credential injection → secret-leak-prevention 可以考慮升級
strace-based discovery → 可以變成 sandbox config 的 auto-tune script
```

### 隔離技術選項對照

| 技術 | 隔離強度 | 資源開銷 | 適用場景 |
|---|---|---|---|
| bubblewrap (bwrap) | 中（mount ns + user ns） | 極低 | 本機開發、輕量隔離 |
| Docker | 高（完整 namespace set） | 中 | 生產、需網路隔離 |
| Podman (rootless) | 高 | 中 | 無 root 權限的環境 |
| gVisor | 更高（kernel deprivilege） | 高 | 不可信 workload |

Hermes 目前 zero isolation → bubblewrap 是最簡單的第一步。

## 未追蹤

- Bubblewrap 的 user namespace mode（無需 root 的完整隔離）
- gVisor vs bubblewrap 的 security trade-off（Senko 完全忽略了 kernel escape 風險，這適合哪些 threat model）
- Docker Agent YAML schema 對應的鉤子（pre_tool_use 事件在 sandbox 層的對應實作）

## ✅ 本次探索完成

