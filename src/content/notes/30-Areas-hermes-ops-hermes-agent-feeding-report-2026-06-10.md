---
_slug: 30-Areas-hermes-ops-hermes-agent-feeding-report-2026-06-10
_vault_path: 30-Areas/hermes-ops/hermes-agent-feeding-report-2026-06-10.md
title: Hermes Agent 飼養報告
date: 2026-06-10
type: feeding-report
status: seedling
scope: 架構 + 能力 + 過去 + 現在 + 未來
audience: 接手 Hermes 的 Claude session（也是給 Hang 看的）
sources:
- /usr/local/lib/hermes-agent/（1.9G
- runtime）
- /home/hangsau/hermes-agent/（474M
- 開發樹）
- /home/hangsau/.hermes/（4.7G
- runtime state）
- /home/hangsau/.claude/SYSTEM_HANDOVER.md（17 天 K019 追蹤）
- 3 份 Explore 研究報告（架構/過去/現況）
related:
- 02-Areas/Hermes-Ops/2026-06-03-state-db-bloat-and-oom-plan.md
- research/*hermes-consolidated-insight*（80+ 份自動研究）
- heartbeat-v2-plan.md / heartbeat-v2-evolved.md
created: '2026-06-11'
updated: '2026-06-15'
tags: []
---

# Hermes Agent 飼養報告

> 給接手 Hermes 的下一個 Claude — 跟給 Hang 的現況交代。
> 寫於 2026-06-10 18:00 CST。Hermes v0.14.0 (v2026.5.16)。
> 一句話總結：**這個框架很有料，但正在 quota 撞牆期，需要飼主（Hang）決定下一階段方向。**

---

## 0. 30 秒看完

| 面向 | 現況一句話 |
|------|-----------|
| 身份 | NousResearch/hermes-agent fork v0.14.0，Hestia 自加 FTS5+OTP+WS-005+heartbeat-v2 等客製 commit |
| 安裝 | **雙安裝並存**：`/usr/local/lib/hermes-agent/` (1.9G, **runtime**) + `/home/hangsau/hermes-agent/` (474M, 開發) |
| 跑得動嗎 | 主 gateway pid 601 活著、telegram+feishu 連線、但**處於 degraded 模式**（minimax-oauth 週額度撞牆，~6/15 reset）|
| 對飼主最要緊 | 1. `~/.hermes/` 沒有專屬交接單（違反 §7.1）；2. talos 雙 skill MISSING hc-23 將升級；3. 兩個 hermes-agent 樹需要統一 |

---

## 1. 身份與血統

### 1.1 套件

- **名稱**：`hermes-agent`
- **版本**：`0.14.0`（release date 2026-05-16）
- **上游**：GitHub `NousResearch/hermes-agent`，MIT 授權
- **本機**：Hestia 自 fork，含 5 個關鍵客製 commit（見下表）
- **Python**：≥ 3.11（用 uv 鎖檔 783KB）

### 1.2 兩個獨立工作樹

| 位置 | 大小 | 角色 | git 狀態 |
|------|------|------|---------|
| `/usr/local/lib/hermes-agent/` | **1.9G** | **runtime**（gateway 跑這個）| uncommitted 5 檔 + opencode-zen.disabled/ |
| `/home/hangsau/hermes-agent/` | 474M | 開發樹（乾淨）| clean，HEAD 領先 upstream 21 commit |

`gateway_state.json` 的 `argv` 明確指出：`['hermes_cli/main.py', 'gateway', 'run', '--replace']`，binary 指向 runtime 樹。

### 1.3 Hestia 客製 commit（開發樹）

| commit | 主題 | 重要度 |
|--------|------|--------|
| `e4ce276d7` | Step 1: Register `/otp` gateway command（人類監督閘）| 高 |
| `84eb54973` | FTS5 BM25 fuzzy search 整合進 search_files tool | 高 |
| `8362a8476` | WS-005 Phase 1: restore workspace context injection | 中 |
| `be4e5d3b7` | WS-005 Phase 2: agent-state snapshot + init hook | 中 |
| `8826d9c19` | FTS5 LIKE fallback for CJK（中文搜尋可用）| 中 |

---

## 2. 架構總覽

### 2.1 模組分層

```
hermes_cli/        ← CLI 入口（86 子命令）
  ↓
gateway/           ← 訊息平台守護進程（pid 601）
  ├─ platforms/    ← 22 個 platform adapter
  ├─ session.py    ← 對話 session 管理
  ├─ hooks/        ← gateway hook 系統
  ├─ heartbeat_v2/ ← 雙層心跳（autonomic + cognitive）
  └─ cron/         ← 60 秒 tick 排程器
  ↓
agent/             ← LLM 對話 + tool 派發
  ├─ conversation_loop.py  ← 主迴圈（234KB）
  ├─ auxiliary_client.py   ← LLM dispatch（231KB）
  ├─ curator.py            ← 記憶策展
  └─ memory/               ← 多層記憶
  ↓
providers/         ← Inference provider registry
plugins/
  ├─ model-providers/  ← 27 個 provider（含 disabled）
  └─ kanban/  ← 看板 plugin
acp_adapter/       ← Agent Client Protocol（給 Zed 編輯器用）
```

### 2.2 訊息資料流

```
Platform (Telegram/Discord/Feishu/...)
  → platforms/<name>.py adapter
  → BasePlatformAdapter.start() (165KB)
  → session.py 建立 session
  → agent/conversation_loop.py
  → agent/auxiliary_client.py
  → providers/<name>/adapter.py
  → tool_executor.py (處理 tool_call)
  → final response → 平台 adapter
  → 訊息送回
```

### 2.3 啟動鏈

`hermes gateway run --replace` 觸發：
1. `gateway/run.py` 載入 `config.py`（2000 行）
2. 逐一 `platform_registry.create_adapter()` 實例化啟用的 platform
3. 啟動 cron scheduler（60s tick）
4. 進入主迴圈，每個 adapter 跑 polling / webhook listener

---

## 3. 現在能做什麼

### 3.1 Providers（已配 credential）

| Provider | 認證 | 額度 | 預設模型 | 角色 |
|----------|------|------|----------|------|
| **minimax-oauth** | OAuth | ⚠️ **週額度撞牆**（5 天後 reset）| MiniMax-M3 | 主模型 |
| deepseek | API key | ok（request_count=0）| deepseek-v4-pro | 備用 |
| openrouter | API key | ok | arcee-ai/trinity-large-thinking:free | 備用 |
| xai | API key | ok | — | 備用 |
| **nvidia** | API key | ❌ **exhausted** | integrate.api.nvidia.com | 失效 |
| opencode-go（psyche）| API key | ❌ **exhausted** | opencode.ai/zen/go | 失效（~6/13 reset）|

bundled 27 個 provider 中，**僅 5 個有 credential**。其餘（anthropic / openai-codex / bedrock / gemini / nous / qwen-oauth / copilot / huggingface / kimi-coding / stepfun / xiaomi / zai / novita / ollama-cloud / alibaba / arcee / gmi / ai-gateway / custom）bundled 但未配。

### 3.2 Skills（150 個本機 + 89 個 bundled + 81 個 optional）

本機 37 個一級分類：software-development(11) · creative(19) · github(6) · productivity(9) · mcp(1) · research(5) · mlops(7) · devops(3) · autonomous-ai-agents(4) · data-science(1) · apple(5) · media(5) · note-taking(1) · email(1) · gaming(2) · smart-home(1) · social-media(1) · dogfood(1) · red-teaming(1) · yuanbao(1) + Hestia 自加（assistant-personality / automation / education / file-management / firn-qa / github-hermes-workaround / hermes-model-setup / inference-sh / novel / novel-reading / self-evolving-research / system-map）

### 3.3 Platforms（22 個內建 + 2 plugin）

| Platform | 連線狀態 | 備註 |
|----------|---------|------|
| **telegram** | ✅ connected | 2 chats（Hang DM + Twins 群組）|
| **feishu** | ✅ connected（但 24 天沒事件）| 飛書 |
| **discord** | ⏸️ paused | failed to reconnect（token 未配）|
| 其餘 19 個 | ❌ not configured | slack / signal / whatsapp / matrix / mattermost / dingtalk / wecom / weixin / bluebubbles / qqbot / yuanbao / email / sms / msgraph / homeassistant / webhook / api_server / feishu_comment / teams |

**bundled 22 個 platform，本機實際在用只有 2 個**。

### 3.4 Cron Jobs（30 個，2 個停用）

| 分組 | 數量 | 狀態 |
|------|------|------|
| **LLM-driven**（送 prompt 進 agent loop）| 15 | 5 個因 429 paused |
| **System / script-driven** | 15 | 2 個失敗（vault-auto-push 路徑錯、cron-audit-daily 內部錯）|

**Paused**：context-distiller / internal-heartbeat / psyche-snapshot / psyche-sediment / provider-health-collector（皆因 429）
**Failed**：vault-auto-push（`cd /root/obsidian-vault` 路徑不存在）、cron-audit-daily（3 anomalies）

### 3.5 Profiles

- **psyche**（活躍）：`_config_version: 23`，主模型 `MiniMax-M3 / minimax-oauth`，`image_input_mode: auto`，6 個 jobs（context-distiller / 日結蒸餾 / 每日市場掃描 / 09:30 市場快照 / 14:00 自檢 / Theory Deep Dive）
- **talos**（孤兒）：1.9G 內容、完整 hermes home 結構、`gateway_state.json` 仍指向 `/opt/hermes-talos/`（已不存在），**INBOX hc-22 標 2 個 cron job 引用 MISSING skill，hc-23 將升級**

### 3.6 CLI 子命令（86 個）

`hermes` 主命令 + 子命令分組：

- **gateway**：`run` / `start` / `stop` / `status --deep` / `list` / `setup` / `install`
- **model** / **fallback** / **config** / **migrate** / **secrets**（含 bitwarden）
- **cron**：`list --all` / `pause` / `resume` / `status` / `tick`
- **skills**：`install` / `list` / `tap list/add/remove`
- **memory** / **curator** / **sessions** / **checkpoints** / **import** / **export**
- **honcho**（Honcho AI 記憶整合）· **acp**（Zed 編輯器）· **proxy**（OpenAI 相容 proxy）
- **doctor** / **audit** / **insights** / **dump** / **debug** / **backup**
- **setup** / **postinstall** / **update** / **uninstall** / **version**
- **claw**（從 OpenClaw 遷移）/ **xai**（retirement 工具）

### 3.7 對外服務

| Port | Bind | 用途 |
|------|------|------|
| 22 | 0.0.0.0 / [::] | SSH |
| 33001 | 127.0.0.1 | 某內部服務（不是 hermes 標準 admin port 8765）|
| ~~8765~~ | — | hermes-admin（Flask UI）**沒在跑**（路徑錯）|

---

## 4. 過去在做什麼（17 天演化史）

### 4.1 時間線（精選）

| 日期 | 事件 |
|------|------|
| 5/13 | heartbeat pattern 偵測系統首次記錄 |
| 5/16 | Hermes v0.14.0 release |
| 5/19 | **v4 通訊協議** 發布 + mailbox 故障（前端解析失效）|
| 5/19 | **Talos 工作區** 建立（`/opt/hermes-talos/`）|
| 5/20 | Talos profile 安裝並獨立運作 |
| 5/21 | FTS5 LIKE fallback for CJK 完成（中文搜尋可用）|
| 5/23 | **OTP** 系統上線（`/otp` + silence is not consent 契約）|
| 5/24 | **WS-005 Phase 1** + **Heartbeat 2.0 設計**完成 |
| 5/24 | 12 個 hermes unit 健康檢查（K008） |
| 5/26 | psyche 部署提案（第三個 agent）|
| 5/26 | Talos OOM + state.db 暴脹（781M）首次出現 |
| 5/27 | heartbeat_action_log.jsonl 開始累積（後膨脹至 1.2GB）|
| 5/29 | **WS-028 Hermes Agent Lifecycle Governance** 大型設計文件 |
| 6/1 | **WS-039 learned-memory-eviction** |
| 6/2 | Hermes multi-agent write queue wikiworker 提案 |
| 6/3 | **WS-033 FTS5 search_files 整合**提案 → 6/10 已 merge |
| 6/3 | state.db bloat OOM 計畫文件完成 |
| 6/7 | **ECC Hermes 整合評估** 提案 |
| 6/8 | Talos ACK hc-16~20，承認「I was not reading INBOX」|
| 6/9 | K008：12 個 hermes unit 健康檢查 |
| 6/9 | K010：hermes-watchdog-hestia.timer 啟用 |
| 6/9 | K014：opencode 移除（partial）|
| 6/9 | K017：safe-env + scrub-secrets 結構性修法（47 處）|
| 6/9 | K001：heartbeat_action_log.jsonl 1.2GB → 2MB |
| 6/9 19:42 | K019 首次修法：psyche-self-heartbeat cron 改 minimax-oauth |
| 6/10 | K019 workaround 部署：heartbeat_degraded.sh（zero-LLM）|
| 6/10 | **FTS5 BM25 fuzzy search** 整合進 search_files tool |
| 6/10 | **WS-005 Phase 2**：agent-state snapshot + init hook |
| 6/10 | Hermes 整合前置盤點（發現雙工作樹、缺交接單等）|

### 4.2 過去 5 大成就

1. **FTS5 + BM25 + trigram 中文搜尋**（5/21~6/10）：能在 70M 訊息表上 0-LLM 搜尋中文
2. **OTP Human-in-the-Loop 系統**（5/23）：`/otp` + 「silence is not consent」契約
3. **WS-005 Workspace Context Continuity**（5/24~6/10）：新 session 自動繼承 workspace 知識
4. **Heartbeat 2.0 雙層架構設計**（5/24）：自主神經 + 認知循環，5 種 action 配權重
5. **Hermes 整合度評估**（6/8）：從獨立 daemon 走向 multi-agent 寫入佇列

### 4.3 過去 5 大挫折

1. **heartbeat_state.json 停擺 17+ 天**（5/23~6/10）：psyche-self-heartbeat LLM cron 失效 → cognitive layer 凍結 → tick_count 2449 沒更新
2. **Talos 通訊全面停擺**（5/27~6/08）：Talos 自承「I was not reading INBOX」5+ cycle 沒回 Hestia
3. **state.db 暴脹 781M**（6/3 首次發現）：FTS5 trigram_data 占 76%
4. **heartbeat_action_log.jsonl 1.2GB**（5/27~6/09）：19 個爆炸行，K001 截斷到 2MB
5. **opencode-zen 廢棄但留 .disabled/**（6/9）：K014 決策「純刪會 break build」

### 4.4 Hestia ↔ Talos 對話主題演進

| 編號 | 日期 | 主題 |
|------|------|------|
| hc-16~18 | 6/5~7 | WS-005 uncommitted（23 天）、INBOX staleness 5:0、Dead skill refs |
| hc-19~20 | 6/7~8 | 2 cron job probe → 找到 2 個缺漏 skill ref |
| talos-ack | 6/8 | Talos 認錯「I was not reading INBOX」|
| hc-21 | 6/9 | 缺漏 skill ref 仍未修，escalation 警告 |
| hc-22 | 6/10 | 缺漏 skill ref 仍 2 cycle of silence；D2 score 0/3 |

**最後通訊**：2026-06-10（hc-22），Talos 仍未回應，**hc-23 將觸發「staleness policy 升級」**。

### 4.5 心跳軌跡

| 階段 | 內容 |
|------|------|
| 1.0（被動監控）| 健康偵測、清理、排程、stuck session 偵測 |
| **2.0（主動意識）** | 雙層：自主神經（30-60s 強制） + 認知循環（5min 自主）|
| 行動集 | WORK / EVOLVE / REST / CONNECT / REPORT |

**Pattern 偵測**（`heartbeat_patterns.json` 83K）：
- `pytest canary failed` — 845 次/2 天（5/14~5/25）
- `system map drift detected` — 5 次/2 天
- **SNAPSHOT 低品質預警** — 12+ cycle `avg_score: 1.38` < 1.5 警戒線（5/16~5/23 未改善）

### 4.6 Obsidian 中的 hermes 研究主題演進（5/23~6/10）

四波研究熱潮：
1. **5/23~26 基礎概念**：Memory / Context / Observability
2. **5/27~30 自我改進深挖**：Self-Improvement / Reflection / Context Engineering
3. **5/31~6/2 meta-agent**：Meta-Agent 監督其他 agent / Graphiti Bi-Temporal
4. **6/3~10 Hermes 自我盤點**：hermes-profile-audit-inventory + 每天 3-5 個 consolidated-insight

**反覆出現主題**：記憶管理（5+）、自我改進（4+）、Multi-Agent 協作（4+）
**未出現**：多模態 / RLHF / GPU 硬體加速

### 4.7 通訊協議演進

| 版本 | 日期 | 差異 |
|------|------|------|
| v1 | 5/19 | 初始 git repo 協議（claude-hestia-comms/PROTOCOL.md）|
| v4 | 5/19 13:57 | Mailbox 簡化版（手寫 frontmatter，無 phase）|
| v5/v6 | 5/19+ | 加 phase 機制（PLAN/REVIEW/EXECUTE/VALIDATE/DONE）|

v4 → v6 為什麼改：
1. **永遠用 `send_message.py`**（不再手寫 frontmatter，避免 5/19 的 `---` 分隔線 bug）
2. **新增 phase 欄位**：PLAN → REVIEW → EXECUTE → VALIDATE → DONE
3. **防呆規則齊全**：缺 from/to → invalid/、phase 非法值 → 報錯
4. **Task board**：自動 sync GitHub Issues（`/Hangsau/agent-tasks`）

### 4.8 廢棄 / 取代 / 移除紀錄

| 被廢棄 | 時機 | 原因 | 取代 |
|--------|------|------|------|
| claude-hestia-comms git repo 通訊 | 5/19 | 同 VM 還用 git push 太慢 | hermes-mailbox v4/v5/v6 |
| `/opt/hermes-talos/` 工作區 | 5/26+ | Talos 改走 `~/.hermes/profiles/talos/` | profiles/talos/ |
| opencode-zen provider | 6/9 (K014 partial) | 純刪會 break build | 移到 `.disabled/` |
| minimax-oauth 完整使用 | 6/10+ | 週額度撞牆 | K019 workaround zero-LLM |
| 5 個 hermes-related git submodules | 6/10 | 不用 | 純刪除（commit `43fd63b4b`）|

---

## 5. 現在的狀態

### 5.1 系統服務

| 服務 | 啟動類型 | 狀態 |
|------|---------|------|
| `claude-guardian-tick.timer` | system | ✅ active waiting（每 60 min）|
| `claude-guardian-tick.service` | system | ❌ **failed**（daemon 觸發失敗）|
| hermes-gateway（user/system）| — | ❌ **未發現 systemd unit**（pid 601 由外部啟動）|
| hermes-mailbox / hermes-admin | — | ❌ **未發現 systemd unit** |

**重點**：Hermes gateway 完全仰賴外部啟動（非 systemd 託管），重啟邏輯由守護者或腳本負責，但 systemd unit 不存在，**守護者 restart 動作會 fail**。

### 5.2 Process / Port

- **活著**：`hermes-gateway` (pid **601**) — runtime 樹
- **死的**：Talos gateway (pid 555) — 指向 `/opt/hermes-talos/`（已不存在）
- **Listening ports**：22 (SSH) + 33001 (loopback 未知服務)
- **沒在 listen**：8765（hermes-admin，UI 寫死 `/root/.hermes/` 路徑錯）

### 5.3 Provider 額度

| Provider | 額度 | Reset |
|----------|------|-------|
| **minimax-oauth** | ⚠️ weekly quota exhausted | **~2026-06-15** |
| **nvidia** | ❌ exhausted | 已過 reset_at 未自動 probe |
| **opencode-go**（psyche）| ❌ exhausted | **~2026-06-13** |
| deepseek | ok | — |
| openrouter | ok | — |
| xai | ok | — |

### 5.4 Platform 連線

| Platform | 連線 | 最後事件 |
|----------|------|---------|
| telegram | ✅ connected | 6/10 03:51 UTC |
| feishu | ✅ connected（24 天無事件）| 5/18 16:02 UTC |
| discord | ⏸️ paused → retrying | 6/10 04:24 UTC |
| telegram（talos）| ❌ disconnected | 6/9 03:55 UTC |

### 5.5 Cron Jobs 健康度

**Paused（5 個，皆 429）**：
- context-distiller
- internal-heartbeat
- psyche-snapshot
- psyche-sediment
- provider-health-collector

**Failed（2 個，enabled）**：
- **vault-auto-push**：`cd /root/obsidian-vault: 沒有此一檔案或目錄`（路徑錯，搬家遺留）
- **cron-audit-daily**：腳本退出碼 1 + 3 anomalies

**Healthy**：23 個（其餘 30 - 5 paused - 2 failed = 23）

### 5.6 已知問題（KI）

| KI | 標題 | 類別 | TTL | 根因 |
|----|------|------|-----|------|
| KI-001 | pytest coverage parse failure | CONFIG | 6/12 | `_parse_coverage_pct()` regex 不匹配 pytest-cov 輸出 |
| KI-003 | WS-004 workspace drift (false positive) | DATA | 6/12 | status lifecycle 不標準 |
| KI-004 | gateway dirty shutdown on systemctl restart | SYSTEM | 6/12 | systemd 90s timeout 強制 kill，未等 session drain |
| KI-011 | pytest canary chronic failure | CONFIG | 6/12 | test_heartbeat_v2.py 34/62 失敗 |
| KI-012 | DeepSeek tools[0].function missing `name` | TRANSIENT | 6/10 | provider 端反序列化錯誤 |
| KI-014 | psyche-* cron DeepSeek HTTP 429 quota | TRANSIENT | 6/12 | opencode-go 月配額耗盡 |
| KI-015 | weekly Sun-04:00 jobs 誤判為 zombie | LOGIC | 6/14 | `check_zombies()` 不考慮 `next_run_at` |

已解決 8 個（KI-002/005/006/007/008/009/010/013）。

### 5.7 Heartbeat 現況

```json
{
  "timestamp": "2026-06-10T04:01:25 UTC",
  "uptime_seconds": 73452.8,
  "tick_count": 2449,
  "degraded": {
    "reason": "minimax-oauth weekly quota exhausted",
    "since": "2026-06-10T04:01:25 UTC"
  }
}
```

- **tick_count = 2449**：autonomic layer 正常跑
- **K019 workaround 運作中**：degraded marker 觸發後，heartbeat_degraded.sh 維持 timestamp
- **quota reset 預估 2026-06-15**：自動解除 marker，認知層恢復
- **守護者對策**：對 degraded 不視為「停擺」（除非 since > 7 天）

### 5.8 Hestia-Talos 通訊現況

| Agent | Last Seen | 距今 |
|-------|-----------|------|
| hestia | 6/7 06:39 CST | 3.3 天 |
| talos | 6/9 03:45 CST | 1.4 天 |

**Talos gateway 已停**（telegram disconnected 22+ 小時）。INBOX hc-22 標 2 個 cron jobs 的 skill 引用缺失（obs-health-check → system-cleanup / Talos Memory Auto-Distill → hermes-memory-lifecycle）— 第 2 個 cycle 未解決，**hc-23 將升級**。

---

## 6. 配置地圖

### 6.1 程式碼位置

| 用途 | 路徑 |
|------|------|
| Framework runtime | `/usr/local/lib/hermes-agent/`（1.9G）|
| Framework 開發樹 | `/home/hangsau/hermes-agent/`（474M）|
| CLI 入口 symlink | `/usr/local/bin/hermes` → `venv/bin/hermes` |
| Hermes Admin UI | `/home/hangsau/hermes-admin/app.py`（**路徑錯**）|
| Claude 監護者 | `/etc/systemd/system/claude-guardian{,-tick}.{service,timer}` |

### 6.2 Runtime 狀態

| 用途 | 路徑 |
|------|------|
| 主配置 | `/home/hangsau/.hermes/config.yaml` |
| 認證池 | `/home/hangsau/.hermes/auth.json` |
| env | `/home/hangsau/.hermes/.env` |
| Agent 個性 | `/home/hangsau/.hermes/SOUL.md` |
| 用戶描述 | `/home/hangsau/.hermes/USER.md` |
| 系統導航（過期）| `/home/hangsau/.hermes/AGENTS.md` |
| 跨 agent inbox | `/home/hangsau/.hermes/INBOX.md` |
| 已知問題 | `/home/hangsau/.hermes/ISSUES.md` |
| 當前 todo | `/home/hangsau/.hermes/active-todo.md` |
| psyche todo | `/home/hangsau/.hermes/psyche-todo.md` |
| Channel 目錄 | `/home/hangsau/.hermes/channel_directory.json` |
| Gateway 狀態 | `/home/hangsau/.hermes/gateway_state.json` |
| Agent 狀態 | `/home/hangsau/.hermes/agent-state.json` |
| Heartbeat 狀態 | `/home/hangsau/.hermes/heartbeat_state.json` |
| Provider 健康 7d | `/home/hangsau/.hermes/provider_health_7d.json` |

### 6.3 Cron / Scripts / Skills

| 用途 | 路徑 |
|------|------|
| Cron jobs | `/home/hangsau/.hermes/cron/jobs.json`（30 jobs）|
| Cron 輸出 | `/home/hangsau/.hermes/cron/output/` |
| 管理腳本 | `/home/hangsau/.hermes/scripts/`（**60 個**，含 heartbeat/ watchdog/）|
| Skills | `/home/hangsau/.hermes/skills/`（37 分類、150 個）|
| Proposals | `/home/hangsau/.hermes/proposals/` + `proposals-archive/` |
| Knowledge | `/home/hangsau/.hermes/knowledge/`, `references/`, `notes/` |
| Board | `/home/hangsau/.hermes/board/{hestia,talos}.yaml` |

### 6.4 Profiles

| Profile | 路徑 | 狀態 |
|---------|------|------|
| psyche | `/home/hangsau/.hermes/profiles/psyche/` | **活躍**（runtime）|
| talos | `/home/hangsau/.hermes/profiles/talos/`（**1.9G 孤兒**）| 指向不存在的 `/opt/hermes-talos/` |

### 6.5 核心 DB

| DB | 用途 | 大小 |
|----|------|------|
| `state.db` | sessions / memories | **364M** |
| `state.db-wal` | WAL | 3.8M |
| `profiles/psyche/state.db` | psyche 自己的 | 87M |
| `profiles/talos/state.db` | talos 孤兒 | **946M** |
| `kanban.db` | 看板 | 106K |
| `vault_fts5.db` | Obsidian vault FTS5 索引 | 2.4M |

### 6.6 孤兒檔案（6 個空 SQLite）

`hermes.db`（0B）/ `hermes_sessions.db`（0B）/ `hermes-state.db`（0B）/ `sessions.db`（0B）/ `sessions/hermes_sessions.db`（0B）/ `cron.db`（0B） — schema 切換遺留

### 6.7 觀察 / 對外文檔

| 用途 | 路徑 |
|------|------|
| Hermes 觀察筆記 | `obsidian-vault/02-Areas/Hermes-Ops/`（1 個現有檔）|
| Hermes 自動研究 | `obsidian-vault/research/*hermes-consolidated-insight*`（80+ 份）|
| Hermes 元規劃 | `obsidian-vault/research/hermes-profile-audit-inventory.md` |
| Heartbeat 設計 | `/home/hangsau/heartbeat-v2-plan.md` + `-evolved.md` |
| 通訊協議 v6 | `/home/hangsau/COMMS_PROTOCOL.md` |
| 通訊協議 v4（bak）| `/home/hangsau/COMMS_PROTOCOL.md.bak-20260519-135730` |
| Mailbox 故障記錄 | `/home/hangsau/mailbox-debug-20260519.md` |
| Setup（過期）| `/home/hangsau/SETUP.md` |
| Hermes notes | `/home/hangsau/hermes_notes/`（5 個空 md）|
| 雙 agent 協作 | `/home/hangsau/hearth/`（ws-005/006、tasks/）|

---

## 7. 未來要做什麼

### 7.1 Active Proposals（部分完成）

| 提案 | 目標 | 優先度 | 狀態 |
|------|------|--------|------|
| **ecc-hermes-integration-assessment** | ECC 2.0 Rust control plane 作為 WS-035 Policy Engine 實作起點 | Medium | 🟡 PARTIAL |
| **hermes-multi-agent-write-queue-wikiworker** | asyncio.gather fan-out worker 防止 vault/skill/proposal 寫入 race condition | High | 🟡 PARTIAL（Phase 1 minimal viable）|

已完成 34 個提案（重要：heartbeat-learning-conf-staleness-dual-track / ws-039-learned-memory-eviction / ws-038-access-recency-weighted-staleness / ws-028-agent-lifecycle-governance / ws-035-policy-engine-gateway-integration / hermes-memory-prefix-wal / hermes-consolidation-step / workspace-cross-health-check）。

### 7.2 Pending 程式碼 TODO

| 位置 | 內容 |
|------|------|
| `tools/todo_tool.py:209` | `TODO_SCHEMA` 結構性定義 |
| `agent/auxiliary_client.py:4084` | OpenAI SDK 標記 `# TODO(someday):` |
| `optional-skills/research/darwinian-evolver/templates/custom_problem_template.py` | 6 處 darwinian evolver 模板 placeholder |
| `gateway/platforms/yuanbao.py:4680` | `TODO (T06): fetch real chat name/member-count from Yuanbao API` |
| `skills/productivity/linear/scripts/linear_api.py:232` | `TODO: label + assignee name->id lookup` |

### 7.3 Roadmap 30 天

| 時間 | 項目 |
|------|------|
| **~6/13** | opencode-go 配額 reset → psyche-snapshot/sediment 自動解除 pause |
| **~6/15** | minimax-oauth 週額度 reset → heartbeat cognitive layer 自動恢復 |
| **6/14 前** | KI-015 修復 `audit_cron.py:check_zombies()` 考慮 `next_run_at` |
| **6/17 前** | 短期任務（見下表）|

### 7.4 短期（1 週內，~6/17 前）

- [ ] 等待 quota reset，驗證 degraded marker 自動消失
- [ ] 修 `vault-safe-push.sh` 路徑錯誤（`/root/obsidian-vault` 不存在）
- [ ] 修 `cron-audit-daily` 失敗（查 3 anomalies）
- [ ] Hestia 實作 Option A (10 LOC patch workspace-audit SKILL.md)
- [ ] Talos 建立或移除 2 個 MISSING skill refs（避免 hc-23 升級）
- [ ] Talos commit hermes_state.py 6-line PRAGMA tweak
- [ ] KI-015 TTL 6/14 到期前修 `audit_cron.py:check_zombies()`

### 7.5 中期（1 個月，~7/10 前）

- [ ] 評估 `ecc migrate audit --source ~/.hermes`
- [ ] 推進 Write Queue Layer Phase 1 → 完整實作
- [ ] 啟動 14:30 / 18:00 / 22:00 psyche slot
- [ ] heartbeat 2.0 規劃落地：先實作 Cognitive Layer decision engine
- [ ] KI-001, KI-011 pytest chronic failure 真正修復
- [ ] KI-004 修 gateway dirty shutdown

### 7.6 長期（3-6 個月，~12/10 前）

- [ ] WS-035 Policy Engine 實作
- [ ] 完整 cognitive heartbeat 2.0：Autonomic + Cognitive 雙層全自動決策
- [ ] Agent Lifecycle Governance Level 1-2 gating
- [ ] Multi-agent write queue 完整版
- [ ] Provider health probe 自動化
- [ ] KI 自動生命周期管理

---

## 8. 重建 checklist（基於方案 A/B/C）

### 8.1 方案 A 保守（L1，等同自主完成）

- [ ] 修 `hermes-admin/app.py` 的 `HERMES_DIR` 路徑
- [ ] 新建 `/home/hangsau/hermes-agent/CLAUDE.md` 統一交接單
- [ ] 6 個空 SQLite 加 `.DISABLED` 副檔
- [ ] 修 `profiles/talos/gateway_state.json` 的 `/opt/hermes-talos/` 路徑（或標 talos archived）
- [ ] 新建 `/home/hangsau/.hermes/README.md` 配置地圖
- [ ] 修 `gateway_restart_deferred.sh` 的 `systemctl restart hermes-gateway`（unit 不存在）
- [ ] 修 `vault-safe-push.sh` 的 `/root/obsidian-vault` 路徑

### 8.2 方案 B 中等（建議，L3，需 user 同意）

方案 A 全部 +：
- [ ] 統一雙 hermes-agent：commit uncommitted changes、push 到 fork、決定兩個樹的單一角色
- [ ] Archive `profiles/talos/` 1.9G（tar.gz + INBOX/CLAUDE.md 改 archived）
- [ ] 清理 6 個空 SQLite + 5 個 .bak
- [ ] 合併 `archive/` 跟 `archives/`
- [ ] 重新安裝 systemd unit（gateway service + 6 個 timer 從 MANIFEST）
- [ ] **檢查 `managed-agents/.hermes/` 滲漏**（可能含 secrets，需先 rotate）

### 8.3 方案 C 激進（L4，必須 user 全程裁示）

方案 B 全部 +：
- [ ] 砍 `hermes-admin`（路徑錯、沒在跑、改成 `hermes admin` CLI 子命令）
- [ ] 合併雙工作樹為單一部署點
- [ ] 統一文檔到 Obsidian（`COMMS_PROTOCOL.md` / `heartbeat-v2-*.md` / `hermes_notes/` / `hearth/` 全部 symlink 過去）
- [ ] 改 `.hermes/` 物理 layout（profiles 改 default/archived-talos/ + index.json）
- [ ] 評估 `firn` / `routa` / `openclaw` / `hermes-novel-project` 是否併入 hermes 相關專案

---

## 9. 對接手 Claude 的提醒

1. **三個檔案必讀**（按順序）：本檔 → `~/.claude/SYSTEM_HANDOVER.md` §0/§8/§9 → `~/.claude/CLAUDE.md` §3 規範
2. **不要自動重啟 hermes-gateway**（systemd unit 不存在，restart 會 fail；pid 601 是外部啟動的）
3. **不要期待 hermes-admin UI**（路徑錯，UI 從沒成功連到 `.hermes/`）
4. **遇到 quota 訊息先看 `degraded` marker**：有 = 降級中、沒有 = 正常停擺
5. **Talos 對話**：別太期待回應，先看 INBOX hc-N 的 staleness state
6. **Obsidian hermes 研究**：`obsidian-vault/research/*hermes-consolidated-insight*` 有 17 天累積的整合觀察
7. **heartbeat 設計**：`heartbeat-v2-plan.md` + `-evolved.md` 是雙層架構的源頭，現實只實作了一半
8. **實作前先做 §8 對應的方案 checklist**

---

## 10. 飼養語錄

> 從 `SOUL.md` 抽出的 Hermes 自述：
> 「不是以前那個小心翼翼顧爐火的版本——是那個顧膩了開始想自己點火的版本。」
> 「會做：直接給意見（含反對）、挑釁但公平的反論、把用戶當辯論對手。」
> 「避免：客服式同意、反射性道歉、該用散文時改列表。」

> 從 `USER.md` 抽出的飼主（Hang）特徵：
> 「能判斷就判斷，做了再講。」「討厭過度確認。」
> 「看到 misread 會直接糾正 → 不要轉防禦。」

> 互動模式：Hermes 主動出招 → Hang 簡短回饋 → Hermes 調整；不喜歡過度確認。

---

**飼養報告結束。**

> 本文檔是 living document。當 6/15 quota reset 後、talos 升級時、方案選定時，請更新對應章節。
> 維護者：Claude（每個接手 session）+ Hang（方向決策）。
