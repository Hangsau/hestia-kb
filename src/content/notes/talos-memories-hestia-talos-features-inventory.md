---
_slug: talos-memories-hestia-talos-features-inventory
_vault_path: talos-memories/hestia-talos-features-inventory.md
title: Hestia + Talos 自建功能全貌
created: '2026-05-27'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Hestia + Talos 自建功能全貌

> 建立：2026-05-27
> 用途：系統性盤點兩個 profile 自建的工具、腳本、cronjobs、插件

---

## Hestia Profile（`~/.hermes/`）

### 心跳系統（Heartbeat v2）

| 腳本 | 功能 |
|------|------|
| `scripts/heartbeat_v2.py` | 入口，讀 snapshot → 評分 → 執行 action |
| `scripts/heartbeat/main.py` | 協調層：snapshot + scoring →選 action → dispatch |
| `scripts/heartbeat/actions.py` | 實際 action 實作（WORK/REST/EVOLVE/CONNECT/REPORT/EXPLORE）、session 歸檔、cache 清理、cron error 掃描 |
| `scripts/heartbeat/scoring.py` | R²-Mem 評分 rubric + cooldown 管理 |
| `scripts/heartbeat/snapshot.py` | 採集系統狀態（disk/memory/cron/session/provider）|
| `scripts/heartbeat/rubric.py` | 品質評分 + 低信號偵測 + recurring-error 優先級 |
| `scripts/heartbeat/utils.py` | shell helpers、provider probing、zombie job 偵測、doom-loop 追蹤 |
| `scripts/heartbeat/config.py` | 所有門檻值、cooldown、git repo list |
| `scripts/board_update.py` | 寫入 `~/.hermes/board/hestia.yaml`；讀取 Talos board 交叉 alert |

**設計：雙層架構**
- Autonomic 層：Python engine 評分，直接 dispatch
- Cognitive 層：LLM 最終決策（透過 `heartbeat-v2-autonomous-maintenance` skill）

### Memory Pipeline

| 腳本 | 功能 |
|------|------|
| `scripts/consolidate_memory.py` | 讀取 autonomous notes → 餵給 memory-consolidator cron |
| `scripts/extract_learning.py` | session → Jaccard 去重 → versioned learnings |
| `scripts/extract_research_knowledge.py` | 研究文獻 → structured notes + digest |
| `scripts/briefing.py` | 找 vault 最新 consolidation → 寫 `briefing.md` 供 context injection |
| `scripts/extract_facts.py` | Jaccard 去重事實儲存（JSONL），CLI：`add`/`recent`/`since`/`stats` |

### 主动式 Cron Jobs（Hestia，`~/.hermes/cron/jobs.json`）

| Job ID | 名稱 | 排程 | 功能 |
|--------|------|------|------|
| `b48ea41a8c8d` | `internal-heartbeat` | 每 5m | 心跳 Python engine |
| `f93693bda237` | `briefing-updater` | 每 30m | 更新 briefing.md |
| `a89f6965daa0` | `memory-consolidator` | daily | 蒸餾 autonomous notes |
| `e7fd7dc2e43a` | `context-distiller` | daily | daily AI agent research |
| `5ff2d37ef155` | `memory-auto-distill` | daily | Memory → ≤70%/80% |
| `4ece069b24be` | `hermes-daily-health-check` | daily | 系統健康檢查 |
| 諸多 others | `西遊記每日関讀心得` 等 | various | 閱讀/研究 |

### 重要 Scripts

| 腳本 | 功能 |
|------|------|
| `scripts/vault-safe-push.sh` | vault 推送；flock 防並行 + rebase + `find` 掃描 sessions/ JSON |
| `scripts/secret-guard.py` | API key 洩漏防線；指紋比對；pre-commit/pre-push hook |

---

## Talos Profile（`~/.hermes/profiles/talos/`）

### 心跳 / 自主維護

| Job | 排程 | 功能 |
|-----|------|------|
| `talos-heartbeat` | `:15/:45` | snapshot → `/srv/hearth` sync → `heartbeat-v2-autonomous-maintenance` skill |
| `heartbeat-v2-autonomous-maintenance`（skill）| — | 根據門檻自動判斷空閒時做什麼 |

### 通訊（跨 Agent）

| 腳本 | 功能 |
|------|------|
| `scripts/comms_reader.py` | 讀取 comms git repo → `reply_expected` 判斷 → 決定是否回覆（v3）|
| 專屬 reply cron（`:08/:23/:38/:53`）| 定時主動回覆，不走心跳 |

### 系統監控

| Job | 排程 | 功能 |
|-----|------|------|
| `watchdog-hestia.sh` | 每 5m | 檢查 Hestia gateway systemd，自動重啟；stable 時 silent |
| `restart-gateway.sh` | on-demand | deferred restart（避免殺死 process 自己）|

### Git / 備份

| 腳本 | 功能 |
|------|------|
| `auto-git-push.sh`（cron `auto-git-push-vault`）| 每 2h | 推送 hermes-agent fork + managed-agents repos |
| `backup-memories.sh`（cron `talos-memory-git-backup`）| 4am | MEMORY.md/USER.md → vault；sessions/ 已排除（不含 API key）|
| `renew_heartbeat.sh` | 每 6h via systemd | repeat counter ≥ 72/90 時重置 |

### Hooks

| 路徑 | 功能 |
|------|------|
| `hooks/session-state-save/handler.py` | session end 時保存 state 到 `session_state.md` |

### Other Scripts

| 腳本 | 功能 |
|------|------|
| `scripts/generate_system_map.py` | auto-generate `AGENTS.md` + `maps/{domain}.md` |
| `board/board_audit.py` | 監査 comms threads vs board YAML；發現 `CONCLUDED` 但無 board 記錄 |

### Cron Jobs（Talos）

| Job ID | 名稱 | 排程 | 功能 |
|--------|------|------|------|
| `2fd94dd6b183` | `watchdog-hestia` | 每 5m | Hestia gateway 看門狗 |
| `8f8cc3bd8a4e` | `talos-heartbeat` | `:15/:45` | 主心跳 |
| `2f358e541f39` | `auto-git-push-vault` | 每 2h | Git push |
| `talos-memory-backup-20250519` | `talos-memory-git-backup` | 4am | 記憶備份 |
| `cross-check-talos-20260518` | `cross-check-talos` | 1:30am | Hestia silence >2h → LLM review |
| `0a6fa5ac9427` | `obs-health-check` | 5am | DB verify |
| `00abba630a23` | `Talos Memory Auto-Distill` | 3:30am | Memory ≤70%/80% |

---

## 通用基礎設施

| 腳本 | 位置 | 功能 |
|------|------|------|
| `secret-guard.py` | `~/.hermes/scripts/` | API key 指紋比對；整合 git hooks |
| `vault-safe-push.sh` | `~/.hermes/scripts/` | Vault 獨佔推送；rsync exclude sessions/ |
| `otp_gate.py` | `~/.hermes/scripts/` | OTP 一次性密碼保護 WS-028 等高風險操作 |
| `policy_engine.py` | `~/.hermes/plugins/` | Block/allow/redact 三 profile 全域 policy |

---

## Secret Leak 修復記錄（2026-05-27）

**問題**：`talos-memory-git-backup` 失敗，`backup-memories.sh` 用 `cp -r` 把含 API key 的 session JSON 複製進 vault，觸發 `pre-commit` hook。

**Root cause**：
- `sessions/` 資料夾含 env dump 的 JSON，API key 在 payload 裡
- `.gitignore` 有 `tal talos-memories/memory_archive/sessions/` 但複製的檔案是 untracked，git add 全部進 staging 後被 secret-guard.py 抓到

**Fix**：`backup-memories.sh` 改用 `rsync --exclude='sessions/'`，不再複製含 key 的 session JSON。

**驗證**：
```bash
cd /root/obsidian-vault && git status --porcelain | head -5  # 乾淨
python3 /root/.hermes/scripts/secret-guard.py staged .       # ✅ EXIT:0
```
