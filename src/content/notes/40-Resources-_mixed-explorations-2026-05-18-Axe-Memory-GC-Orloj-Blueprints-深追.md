---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Axe-Memory-GC-Orloj-Blueprints-深追
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Axe-Memory-GC-Orloj-Blueprints-深追.md
title: Axe Memory GC + Orloj Blueprints — 深追
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Axe Memory GC + Orloj Blueprints — 深追

**延續自**: [[2026-05-18-axe-orloj-moltis-agent-infra-paths]]

## Axe Memory GC — `axe gc` CLI

### Per-source insight

Axe 的 GC 是獨立 CLI command，不在 runtime 裡：
```bash
axe gc <agent-name>     # GC single agent
axe gc --all            # GC all memory-enabled agents
```

**Config 控制項**（來自 README）：
```toml
[memory]
enabled = true
last_n = 10         # load last N entries into context
max_entries = 100   # warn when exceeded
```

**觸發條件**：`max_entries` 到 100 就 warn，但 GC 需要手動跑或掛 cron。沒有 automatic trimming threshold。

**LLM-assisted pattern analysis**：文件說「LLM-assisted」，但 README 只提到 `axe gc` command，沒有見到具体 prompt 或 trimming logic source。這可能是 pro tier 或還在演进。

**與 Hermes 對比**：
- Hermes context-distiller：手動壓縮（LLM 濃度的 memory distillation）
- Axe GC：CLI 命令，pattern analysis 在 gc command 裡
- 兩者都缺：automatic threshold-triggered GC + LLM-assisted pattern scoring

### Hermes 啟發

1. **`axe gc --all` 是 cron-friendly GC design**：把 GC 拆成独立 CLI，heartbeat 的 `/prune` action 可以對齊。缺點：沒有 automatic threshold trigger。
2. **Axe memory 有 `max_entries` warn 但沒有 auto-trim**：等 token 到才 warn，不如 Hermes 的 soft context 警告貼近。

---

## Orloj Blueprints — Pipeline / Hierarchical / Swarm-Loop

### Per-source insight

**Pipeline pattern**（`examples/blueprints/pipeline/`）：
```yaml
apiVersion: orloj.dev/v1
kind: AgentSystem
spec:
  agents:
  - bp-pipeline-planner-agent
  - bp-pipeline-research-agent
  - bp-pipeline-writer-agent
  graph:
    bp-pipeline-planner-agent:
      edges:
      - to: bp-pipeline-research-agent
    bp-pipeline-research-agent:
      edges:
      - to: bp-pipeline-writer-agent
```

**Task definition**：
```yaml
apiVersion: orloj.dev/v1
kind: Task
spec:
  system: bp-pipeline-system
  input:
    topic: state of enterprise AI copilots
  retry:
    max_attempts: 2
    backoff: 2s
  message_retry:
    max_attempts: 2
    backoff: 250ms
    jitter: full
```

**與 Hermes 對比**：
- Orloj 的 DAG graph = declarative workflow，Hermes 的 `delegate_task` 是 imperative chain
- Orloj 的 Task 有 retry policy + message_retry（sub-message-level），Hermes 的 retry 只在工具層
- Orloj 的 `priority` field（Task.spec.input），Hermes 沒有 task priority concept

**Hierarchical / Swarm-loop blueprints**：`curl api.github.com` 列出存在，但 fetch 尚未完成。

### Hermes 啟發

1. **Declarative pipeline as CRD**：Orloj 的 `AgentSystem` CRD 把整個 workflow 宣告成 YAML。Hermes 的 proposals/`*.md` 其實就是 declarative plan，但缺乏 `graph` 視圖。可以在 `proposals/` 加 `graph:` block 讓提案之間的依賴關係更視覺化。
2. **Message-level retry**：Orloj 的 `message_retry` 是 LLM call 級別的重試（250ms backoff），比 Hermes 工具層 retry 更細粒度。

---

## ⏳ 未追蹤

- Orloj hierarchical/swarm-loop blueprints — `https://api.github.com/repos/OrlojHQ/orloj/contents/examples/blueprints/hierarchical` + `swarm-loop`
- Orloj crds directory — `controllers/crds/` 的完整 AgentPolicy + ToolPermission schema
- Moltis hooks — 找不到準確的 GitHub repo，需更好的 search query

## ✅ 本次探索完成
