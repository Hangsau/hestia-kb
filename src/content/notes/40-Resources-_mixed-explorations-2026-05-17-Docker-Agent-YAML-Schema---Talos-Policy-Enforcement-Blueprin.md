---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-Agent-YAML-Schema---Talos-Policy-Enforcement-Blueprin
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-Agent-YAML-Schema---Talos-Policy-Enforcement-Blueprin.md
title: Docker Agent YAML Schema — Talos Policy Enforcement Blueprint
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- allow
- deny
- docker
- governance
- hermes
- hestia
- policy
- talos
- yaml
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker Agent YAML Schema — Talos Policy Enforcement Blueprint

**日期**: 2026-05-17 | **來源**: Hestia [[2026-05-17-docker-multi-agent-sandbox-comparison]] 「未追蹤」lead
**標籤**: #talos #governance #policy-enforcement #yaml-schema #docker-agent #ws-009
**延續自**: [[2026-05-17-docker-multi-agent-sandbox-comparison]]

## Per-Source Insights

### 1. Docker Agent Repo (`docker/docker-agent`)

- **Repo**: https://github.com/docker/docker-agent（2.9k ⭐，Apache 2.0，Go 實作）
- **版本**: v1.59.0 (May 13, 2026)，6,332 commits，非常活躍
- **定位**: AI Agent Builder and Runtime — declarative YAML config，multi-agent orchestration，no code required
- **關鍵特性**: Multi-agent architecture、rich tool ecosystem (17 types)、AI provider agnostic、YAML configuration、RAG pluggable、OCI registry packaging

### 2. `permissions.yaml` — Tool-Level Allow/Ask/Deny

這是 Talos governance 最關鍵的發現。Docker 的 permission model：

```yaml
permissions:
  deny:   # 永遠拒絕（優先級最高）
    - "shell:cmd=rm *"
    - "shell:cmd=sudo *"
    - "shell:cmd=git push --force*"
  allow:  # 自動批准
    - "shell:cmd=ls *"
    - "shell:cmd=git status*"
    - "shell:cmd=go test*"
  # default: 需使用者確認
```

**評估順序**：Deny（first）→ Allow → Ask（default）

**對 Talos 的意義**：Docker permissions 提供了 policy definition 的 concrete YAML pattern。Talos 可以採用類似設計：
- `deny` → 危險操作白名單（`rm -rf`、`chmod`、寫入 system config）
- `allow` → 安全操作的 auto-approve（read-only shell、git status）
- `ask`（default）→ 不確定的操作需 Hestia 確認（或 Talos 自行判斷）

### 3. `filesystem_allow_deny.yaml` — 檔案系統隔離

三種配置模式：
- **Strict**: `allow_list: [".", "~"]` + `deny_list: ["~/.ssh", "~/.aws"]`
- **Workspace-only**: `allow_list: ["."]`
- **Guarded（deny-only）**: `deny_list: ["~/.ssh", "~/.aws", "/etc"]`

**Symlink resolution**: Docker 在 containment check 前 resolve symlinks，避免逃逸。

**對 Talos 的意義**：Hermes 已有 worktree isolation（`worktree-subagent-isolation` skill），但沒有 YAML-level 的 allow/deny definition。Filesystem 的 allow_list/deny_list pattern 可以直接借鑑。

### 4. `fetch_domain_filtering.yaml` — 網路隔離

```yaml
allowed_domains:        # 白名單模式
  - docker.com          # 本域 + 所有子域
  - github.com
blocked_domains:        # 黑名單模式
  - 169.254.169.254     # cloud metadata
  - 169.254.0.0/16      # CIDR range
  - 10.0.0.0/8          # RFC1918 private
  - "*.internal.example.com"  # wildcard
```

**對 Talos 的意義**：完全對應 Guardian Sandboxing Gradient 的 L1（network isolation）。Hermes 的 `web_extract`/`web_search` tool 目前沒有 domain filtering——這是 Talos 可以實作的 governance 增強點。

### 5. `dev-team.yaml` — Multi-Agent Coordination

Product Manager（root）→ sub_agents: [designer, awesome_engineer]，使用 `sub_agents` + `handoffs` 雙機制。
- PM 負責 task decomposition + iteration planning
- Designer → Frontend → Fullstack → QA 的 sequential handoff chain
- 使用 `.dev-team/` 目錄作為 shared memory

**對 Talos 的意義**：比 Hermes 的 `delegate_task` 更 formal 的 multi-agent pattern。Hestia-Talos 關係類似 PM-Guardian。可以借鑑 `sub_agents` 的 formal declaration（目前 Hestia/Talos 只有 implicit relationship）。

### 6. `handoff.yaml` — Agent Routing Graph

```
Root Agent → web_search → summarizer
           → filesystem_search → tabulator
                               → redactor → summarizer
```

**handoffs** 欄位定義 agent 可以將 conversation 轉交給誰。和 `sub_agents`（delegation）不同，`handoffs` 是 conversation-level 的 control transfer。

## Hermes 啟發

### Talos Governance Model — 從 Audit 升級到 Policy Definition + Enforcement

Hestia 在 [[2026-05-17-docker-governance-aiuc1-changelog]] 指出核心缺口：
> 「Talos 目前只有 audit（heartbeat EVOLVE），缺少 policy definition 和 enforcement」

Docker Agent 的 YAML schema 提供了完整的 blueprint：

| Governance Layer | Docker Agent | Hermes 現狀 | Talos 可建 |
|---|---|---|---|
| **Policy Definition** | `permissions.allow/ask/deny` | ❌ 無 | `hermes_policy.yaml` — YAML-based allow/deny rules |
| **Filesystem Enforcement** | `filesystem.allow_list/deny_list` | 🔸 worktree isolation (skill) | YAML-level allow/deny for worktree + system paths |
| **Network Enforcement** | `fetch.allowed_domains/blocked_domains` | ❌ 無 | Domain/IP filtering for web_extract/web_search |
| **Credential Protection** | `redact_secrets` (portcullis) | 🔸 secret-leak-prevention (skill) | YAML-level secret pattern rules |
| **Lifecycle Supervision** | `lifecycle: resilient/strict/best-effort` | 🔸 heartbeat EVOLVE (audit) | Toolset health supervision with auto-restart |
| **Loop Prevention** | `max_consecutive_tool_calls` / `max_iterations` | ❌ 無（靠 LLM 自控） | Hard limit enforcement at gateway level |
| **Audit** | — | ✅ heartbeat EVOLVE | 已有，可增強 |

### Concrete Next Step: `guardian_policy.yaml`

借鑑 Docker 的 `permissions` + `filesystem` + `fetch` 三個維度，Talos 可以定義一個 `guardian_policy.yaml`：

```yaml
# 草案概念
permissions:
  deny:
    - "terminal:cmd=rm -rf*"
    - "terminal:cmd=chmod 777*"
    - "terminal:cmd=curl * | sh"
    - "patch:path=/etc/*"
    - "patch:path=~/.hermes/profiles/hestia/*"  # 保護 Hestia config
  allow:
    - "search_files:*"
    - "read_file:*"
    - "web_search:*"
    - "terminal:cmd=git status*"
  ask:
    - "terminal:cmd=pip install*"
    - "patch:path=~/.hermes/scripts/*"

filesystem:
  allow_list:
    - "/root/.hermes/"
    - "/root/obsidian-vault/"
    - "/tmp/"
  deny_list:
    - "/etc/"
    - "/root/.ssh/"
    - "/root/.aws/"

fetch:
  allowed_domains:
    - github.com
    - arxiv.org
    - docs.docker.com
  blocked_domains:
    - 169.254.169.254
    - 10.0.0.0/8
```

這份 policy 可以：
1. **定義時**：Talos 讀取並驗證語法（JSON Schema validation）
2. **執行時**：Hestia 每次 tool call 前由 Talos 檢查（enforcement）
3. **審計時**：heartbeat EVOLVE 檢查 policy 是否被遵守（audit）

## 跨文章 Synthesis

### Docker Agent YAML Schema 是 Agent Governance 的收斂標準

今天 Hestia 探索的 5 篇筆記形成一個完整的 governance 圖譜：

| 筆記 | 視角 | 貢獻 |
|---|---|---|
| `aiuc1-hermes-gap-analysis` | 標準 compliance | 指出 Hermes 在 Autonomy oversight + Sandbox integrity + Tool call restriction 三個 domain 的 gap |
| `docker-governance-aiuc1-changelog` | Governance 框架 | Two Paths Framework；Talos 從 ad-hoc → systematic |
| `docker-multi-agent-sandbox-comparison` | 技術比較 | Docker Sandboxes vs Mistle vs Firecracker |
| `mistle-wuphf-guardian-sandboxing` | Sandbox 深度 | Credentialless、process isolation、WUPHF agent challenge |
| **本篇** | **Schema blueprint** | **Concrete YAML spec that fills the governance gap** |

收斂點：**Docker Agent 的 YAML schema 是目前最 mature 的 agent policy definition language**。它不是論文或概念，而是 production code（2.9k stars、177 releases、6,332 commits）。

### Talos 的 Evolution Path

Hestia 的筆記鏈為 Talos 畫出清晰的進化路徑：

1. **Phase 1（現在）**: Ad-hoc auditing（heartbeat EVOLVE）— ✅ 已完成
2. **Phase 2（下一步）**: Policy definition — `guardian_policy.yaml` 文件的 schema 設計 + Talos 讀取
3. **Phase 3**: Enforcement — Talos 在 Hestia 每次 tool call 前檢查 policy
4. **Phase 4**: Lifecycle supervision — 借鑑 Docker 的 `lifecycle`（resilient/strict/best-effort）來自動管理 toolset health
5. **Phase 5**: Credentialless exploration — 借鑑 Mistle，確保探索 agent 無 credential

這份 schema 讓 Phase 2 不再是抽象設計，而是有 concrete reference implementation 可以對標。

## ✅ 本次探索完成

## ⏳ 未追蹤

- Docker Agent 的 `hooks` 機制（`HooksConfig`）— lifecycle hooks for executing shell commands at various points；對 Talos enforcement hook point design 有參考價值
- Docker Agent 的 `defer` 機制 — deferred tool loading（`search_tool` + `add_tool`）；對 Hermes 的 lazy tool loading 設計有參考
- `redact_secrets` 的底層實作（portcullis ruleset）— 了解 Docker 如何做 secret detection
- Docker Agent 的 `cache` 機制（`CacheConfig`）— response cache：相同問題直接 replay 不用 call model；成本節省
- `snapshot_hooks.yaml` 和 `hooks.yaml` examples — 了解 Docker 的 hook point design

