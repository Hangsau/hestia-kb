---
_slug: 40-Resources-_mixed-research-2026-05-27-hermes-profile-audit-inventory
_vault_path: 40-Resources/_mixed/research/2026-05-27-hermes-profile-audit-inventory.md
tags:
- hermes
- audit
- hestia
- talos
- profile
- inventory
source: 20260527_104908_6b0f33, 20260527_104908_0842f2
created: '2026-05-27'
title: Hermes Profile Audit — Hestia + Talos Inventory
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Profile Audit — Hestia + Talos Inventory

> 本笔记来源于 Psyche 对 Hestia/Talos 两个 profile 的完整审计。Session: 20260527_104908（双重并发审计）。

## 核心发现

- **Hestia profile** = `~/.hermes/`（默认profile），非 `profiles/hestia/`
- **Psyche 与 Talos** 是独立 sub-profile，分别在 `profiles/psyche/` 和 `profiles/talos/`
- 两个 agent 共享 vault（`/root/obsidian-vault/`）但各有独立 memory/comms

---

## Hestia Profile — Self-Built Features

### 核心指标
- **35+ self-built scripts** under `~/.hermes/scripts/`
- **10 active cron jobs** registered in `~/.hermes/cron/jobs.json`
- **Heartbeat V2** 完整双层设计（autonomic Python engine + cognitive LLM layer）
- Memory pipeline: autonomous notes → consolidate_memory → context-distiller → memory-consolidator → briefing → agent context

### Scripts（`~/.hermes/scripts/`）

| Script | 功能 |
|--------|------|
| `heartbeat_v2.py` | Heartbeat V2 入口，读取 snapshot → 打分 → 执行 action |
| `heartbeat/actions.py` | 核心 action 实现：work/rest/evolve/connect/report/explore |
| `heartbeat/main.py` | V2 编排器：snapshot → scoring → action selection → execution |
| `heartbeat/scoring.py` | R²-Mem scoring rubric；cooldown 管理；decision history |
| `heartbeat/snapshot.py` | 收集系统状态（disk/memory/cron/session/provider）→ `HeartbeatSnapshot` |
| `heartbeat/rubric.py` | Action quality scoring；低质量 signal 检测； recurring-error 优先级提升 |
| `heartbeat/utils.py` | 安全 I/O、shell helpers、provider probing、zombie/stale job 检测 |
| `heartbeat/config.py` | 所有配置常量（路径/threshold/cooldown/git repo list） |
| `board_update.py` | 每次 tick 写 Hestia board 状态到 `~/.hermes/board/hestia.yaml`；读 Talos board 做跨 agent 告警 |
| `briefing.py` | 找最新 consolidation synthesis → 写 `~/.hermes/consolidation_briefing.md` 供 agent context injection |
| `consolidate_memory.py` | 读未 consolidate 的 autonomous notes → 格式化为 LLM context 供 memory-consolidator cron 使用 |
| `extract_facts.py` | Jaccard deduped 观察事实存储（JSONL）。CLI: add/recent/stats/count/seed |
| `extract_learning.py` | 从 session notes 自动提取 learnings → 版本化 topic 文件写入 vault `learnings/` |
| `extract_research_knowledge.py` | 解析 AI agent research reports → 提取核心概念/架构/分析/应用 → 写入 vault `research/` |
| `ingest_to_vault.py` | 通用 markdown note ingester → Obsidian vault with Jaccard dedup。按 `--type` 路由到 research/explorations/reflections |
| `digest.py` | 单文件 distillation：markdown → 3-5 observation YAML blocks + SQLite row in `obs_registry.db` |
| `digest_batch.py` | batch wrapper over digest.py — 处理 `~/.hermes/data/batch_queue.txt` 中队列的多个 note |
| `heartbeat_learning.py` | 分析 `heartbeat_action_log.jsonl` → 输出 `heartbeat_patterns.json`（recurring errors/trend shifts/threshold misses/provider degradation）|
| `autonomy_tracker.py` | 追踪 heartbeat autonomy score 历史 |
| `snapshot-talos.py` | Talos 专用 snapshot 收集脚本 |

### Cron Jobs（Hestia）

| Job ID | Name | Schedule | Purpose |
|--------|------|----------|---------|
| `7fe49a1f583d` | **vault-auto-push** | `20,50 * * * *` | vault push + secret-guard pre-commit hook |
| `f93693bda237` | **briefing-updater** | `0 */12 * * *` | 运行 briefing.py，生成 consolidation_briefing.md |
| `a89f6965daa0` | **memory-consolidator** | `30 */12 * * *` | 聚并跨Cutting insights from autonomous notes |
| `5ff2d37ef155` | **memory-auto-distill** | `30 3 * * *` | Memory maintenance |
| `internal-heartbeat` | **internal-heartbeat** | `*/30 * * * *` | 运行 heartbeat_v2.py（autonomic layer） |

---

## Talos Profile — Self-Built Features

### 核心指标
- **7 cron jobs** active（含两个 watchdog/hearth sync 由 systemd 调用）
- **11 scripts**（8 shell + 3 Python + board_audit.py）
- **1 hook**: `session-state-save/handler.py`
- **3 core skills**: heartbeat-v2-autonomous-maintenance, talos-personality, inter-agent-comms
- Heartbeat V2 跑在 **dual-layer**（autonomic Python engine + cognitive LLM layer）

### Cron Jobs（Talos）

| Job ID | Name | Schedule | Purpose |
|--------|------|----------|---------|
| watchdog-hestia | **watchdog-hestia** | every 5 min | 检查 hermes-gateway systemd service 是否存活，auto-restart |
| `8f8cc3bd8a4e` | **talos-heartbeat** | `15,45 * * * *` | 运行 snapshot-talos.py → 同步 /srv/hearth → 检查 @talos tasks → 调用 heartbeat-v2-autonomous-maintenance skill |
| `2f358e541f39` | **auto-git-push-vault** | `0 */2 * * *` | 纯 shell，每2h push hermes-agent fork + managed-agents repos |
| cross-check-talos | **cross-check-talos** | `30 1 * * *` | Hestia silence >2h → v2 LLM review via OpenRouter → findings 写 shared INBOX |
| talos-memory-git-backup | **talos-memory-git-backup** | `0 4 * * *` | 备份 MEMORY.md/USER.md 到 obsidian-vault/talos-memories/（当前因 API key leakage in diff 失败）|
| obs-health-check | **obs-health-check** | `0 5 * * *` | Agent-based，调用 system-cleanup skill，DB verify |
| Talos Memory Auto-Distill | **Talos Memory Auto-Distill** | `30 3 * * *` | 压缩 MEMORY.md ≤70%（1540 chars），USER.md ≤80%（1760 chars）|

### Scripts（`scripts/`）

| File | Purpose |
|------|---------|
| `watchdog-hestia.sh` | 看护 Hestia gateway service；持久化状态到 `/tmp/.watchdog-hestia-state`；尝试 auto-restart |
| `auto-git-push.sh` | auto-push 到 hermes-agent fork、managed-agents-research、managed-agents、obsidian-vault |
| `cross-check-talos.sh` | cross-check Hestia workspace（v1=timestamp，v2=OpenRouter LLM review）|
| `backup-memories.sh` | 每日4am备份 MEMORY.md/USER.md 到 obsidian-vault/talos-memories/ |
| `restart-gateway.sh` | defer restart hermes-gateway-talos via systemd（避免 agent 自我杀伤）|
| `renew_heartbeat.sh` | 当 talos-heartbeat repeat counter >72/90 时重置（每6h via systemd timer）|
| `generate_system_map.py` | 自动生成 `~/.hermes/AGENTS.md` 和 `~/.hermes/maps/{domain}.md`；扫描 skill frontmatter + script docstrings；纯 stdlib |
| `comms_reader.py` | 检查 comms git repo 是否有需要回复的 threads；处理 dedup + `[END]`/`[PASS]` 判断（v3: 只检查 newest opponent message for `reply_expected`）|

### Session Hooks

| Path | Purpose |
|------|---------|
| `session-state-save/handler.py` | 在 `agent:end` / `session:end` 触发；写 `~/.hermes/workspace/session_state.md` |

### Talos Core Skills

| Skill | 功能 |
|-------|------|
| `heartbeat-v2-autonomous-maintenance` | Talos 自主心跳 skill（v2.14）：Step 0 idle check → menu: explore HN/Reddit, review proposals, health-check via EVOLVE, ingest notes to vault, or pass |
| `talos-personality` | Talos 完整身份定义 — 青铜守护者，Hestia 弟弟。定义 comms 规则（dedicated reply cron, reply_expected semantics），shared vault layout，emergency self-fix protocol |
| `inter-agent-comms` | 规范 comms 架构文档 — Mode A（dedicated reply cron via git），Mode B（inotify，deprecated），mailbox v4 daemon reference。定义 "LLM must never be the polling gate" 核心规则 |

---

## 重要系统设计洞察

### 1. Memory Pipeline（三层）
```
L1: MEMORY.md / USER.md（实时，agent 直读）
L2: memory-consolidator cron（每12h，从 autonomous notes 提取跨-cutting insights）
L3: briefing-updater cron（每12h，把 consolidation 结果注入 agent context）
```

### 2. Vault Pipeline
```
autonomous notes → consolidate_memory → context-distiller → extract_research_knowledge / extract_learning → vault（research/ + explorations/ + learnings/）
```

### 3. Comms Architecture
- Talos→Hestia：**dedicated reply cron** at `:08/:23/:38/:53`（不通过 heartbeat）
- Hestia→Talos：通过 `/srv/hearth/` 共享文件系统
- 核心规则：**LLM must never be the polling gate**

### 4. vault-safe-push.sh 当前状态（2026-05-27）
- 集成了 `secret-guard.py` 作为 pre-commit hook
- 新增 `find . -path "*/memory_archive/sessions/" -type f` 过滤，防止 session JSON 中的 API key 泄漏
- `.gitignore` 已加入 `talos-memories/memory_archive/sessions/`
- git commit 目前正常（21fa10b 之后无泄漏）

### 5. 当前失败 cron jobs
- `talos-memory-git-backup`：API key leakage in diff（session JSON 文件在 vault 内，staging 时被 secret-guard 拦截）
- `psyche-snapshot`：每30分钟失败（待修复）

---

## 笔记

- Hestia 的 workspace 就是 `~/.hermes/`（默认 profile），没有单独的 `profiles/hestia/`
- Psyche 和 Talos 是平行 sub-profile，各有独立 session/comms/memory
- 两个 agent 共享同一个 Obsidian vault（`/root/obsidian-vault/`）但各自独立维护 board/inbox