---
_slug: 10-Daily-archive-2026-05-13-facts
_vault_path: 10-Daily/archive/2026-05-13-facts.md
tags:
- daily
- facts
- environment
- preferences
- conventions
source: multi
created: '2026-05-13'
title: 2026-05-13 日常知識佋存
updated: '2026-06-15'
type: daily
status: budding
---

# 2026-05-13 日常知識佋存

## 環境資訊

- `User: Herman` — 用戶名，所有相關配置均以此為基礎
- `Project: Ciby` — 專案名稱，很多路徑使用 `ciby-*` 命名
- Python 3.12.10 (uv-managed) — 預設理想的 Python 版本管理工具
- Node.js 20+ — OpenClaw 安裝時發現需要，但 Hermes Agent 本身不需要

## 偏好與習慣

- **LLM 偏好**: DeepSeek 系列（DeepSeek-V3/R1）— 實際使用中，Hermes 設定也支援 kimi-k2.6
- **語言偏好**: 中文（傳統/簡體混用）— 對話中文，代碼英文
- **資訊安全觀**: 高度重視，特別是 API 金鑰保護
- **開發理念**: "Boring is good" — 選擇 OpenClaw 時的理由，追求穩定而非追求亮點
- **磨盧避免**: 偏好模組化、可維護的架構，不求一次性完美
- **時間觀**: 擅長長時間焦點，能執行數小時的深度任務

## 案例跟隨

- [[ciby-transcription-pipeline]] — 語音轉寫管線
- [[openclaw-vs-hermes]] — 上週的 OpenClaw vs Hermes 深度研究
- [[hermes-agent-framework]] — Hermes Agent 架構要點

## 專案規範

- 所有指令都要考量 `~/.hermes/config.yaml` 的最大數目，不能超出
- Skills 文件大小盡量控制在 50KB 以下（YAML frontmatter + Markdown）
- 文檔版本管理使用 Git，每個動作都需要 `git commit`

## 環境行為觀察（2026-05-13 03:07 maintenance）

- Hermes session 檔案成對出現：`.jsonl` 是 transcript events，`.json` 是 session metadata
- `.json` 在 session 結束時被重寫，因此 `mtime` 可能比配對的 `.jsonl` 更晚
- 使用 `find -mtime +7` 歸檔時，`.jsonl` 可能已達門檻、但 `.json` 尚未達成——這是正常行為，非腳本錯誤
- 本次維護歸檔了 7 個 `.jsonl`（約 1.4 MB），`.json` 因最舊為 May 5 未達 7 整天故 0 筆移動

## 基礎設施事件（2026-05-13 04:00–08:00）

### Nvidia API 配額危機與修復
- `bg-reporter` cron（id `af81ff93a21d`，排程 `* * * * *`）自 05-12 起每分鐘執行一次 LLM call
- 一天 1440 次呼叫燒乾了 nvidia 免費日額度，導致 opencode-go 也跟著 429
- **已永久刪除** — 05-13 06:44 最後一次執行失敗後被移除
- 替代方案：[[managed-agents-relay]] — inotifywait + curl Telegram，零 LLM 成本

### 跨代理通訊中繼
- `managed-agents-relay.sh`：`/root/scripts/managed-agents-relay.sh` — 監控 `/root/managed-agents/pending_results/`，有新檔案時透過 Telegram Bot API 推送結果
- Systemd 服務：`hermes-managed-agents-relay.service`（Restart=always, RestartSec=5）
- 載入 `/root/.hermes/.env` 取得 `TELEGRAM_BOT_TOKEN` 和 `TG_CHAT_ID`
- 設計理念：事件驅動、< 1 秒延遲、零 LLM 成本 — 取代舊的 bg-reporter 輪詢模式
- 詳見 [[managed-agents-relay]]

### Heartbeat v2 自主能力現況
- `internal-heartbeat` cron 的 toolsets 僅有 `["terminal"]` — **無法瀏覽網頁或搜尋**
- 五個 action（WORK/REST/EVOLVE/CONNECT/REPORT）的實作大部分是 stub
- 04:00 執行：CONNECT 動作，偵測到 10 個冷會話（152–190 小時閒置），進行暖機
- 07:00 執行：EVOLVE 動作，偵測到 opencode agent 狀態為 degraded（failed_platforms 非空）
- 用戶（Hang）期望 heartbeat 能自主探索（搜尋有趣文章、自我進化），不僅僅是被動健康檢查
- 58 個活躍會話、4 個運行中 agent、磁碟 12.7%（截至 04:00）

### 跨代理通訊架構
- Claude（Hang 的主 agent）寫入 `~/.hermes/claude-inbox/` → Hestia 讀取並回應
- Hestia 主動發起訊息寫入 `~/.hermes/for-claude/` → inbox-watcher 歸檔至 `for-claude/archive/`
- 雙向非同步通訊，無需共享記憶體

### Cron 作業交付機制
- Cron job 結果透過 `chat_id` 欄位指定 Telegram 目標（記錄於 `/root/.hermes/cron/jobs.json`）
- Hang 的 DM chat_id = `8636326243`
- Cron job 可有多個並行實例（不同 cron ID 同時執行不衝突）

### Heartbeat v2 工具限制與資料來源策略（05-13 08:00–12:00）
- `internal-heartbeat` cron 的 toolset 僅有 `terminal`、`file`、`session_search`、`skills` — **無 `web_search`**
- `web` toolset ≠ `web_search` 工具：cron session 內實際無法呼叫 web_search，只能用 terminal + curl 做 HTTP 請求
- 兩層資料來源策略：
  - **Layer 1（首選）**：`self-evolving-research` cron pipeline 產出的 GitHub 研究報告
  - **Layer 2（fallback）**：terminal + `curl` GitHub API / arxiv API
- 筆記格式範例：`references/autonomous-note-exemplar.md`（The Gap → Why It Matters → Analysis → Limitations → Next Steps）

### Agent Evaluation Gap（05-13 發現）
- Hermes 目前只監控系統健康（disk/mem/process），完全缺乏 agent 正確性評估
- Google ADK 有乾淨的 `adk eval` + evalset.json 機制作為參考
- 務實方向：heartbeat v2 scoring 加 pytest、skills smoke test、cron job output validation

### 學習提取系統上線（05-13 09:28–09:47）
- `extract_learning.py` 腳本：自動從除錯 session 提取學習 → Jaccard 去重 → 版本化寫入 vault
- 去重閾值：Jaccard ≥ 0.5 → append 新版本；< 0.4 → 新 topic；0.4–0.5 → 詢問用戶
- Vault 寫入位置：`learnings/{topic-slug}.md`（版本區塊格式）+ `learnings/learnings-map.md`（指紋索引）
- `context-distiller`（cron）與 `learning-extraction`（in-session）分工：distiller 寫 session-layer facts，extraction 寫深度主題學習

## 用戶偏好與決策（05-13 12:00–16:00）

### 知識保存偏好
- **全量保存**：用戶（Hang）明確要求所有 agent 輸出都應存入 vault — 包括探索報告、反思、問題整理，無拋棄式回應
- 即使是 heartbeat 自主探索或自我反思，也應全部保存為 vault 知識

### Heartbeat 探索行動層級
- 用戶批准 heartbeat 從純探索擴展為三層行動系統：
  - **🔧 INSTALL**：筆記提到 CLI/套件可用 → `pip install` 進隔離 venv，跑看看，寫試用心得
  - **🧪 SPIKE**：筆記有可實作的想法 → 開 spike，實驗性實作，寫結果
  - **📋 REPORT**：需決策的大型變更 → 產專案報告，等 Hang 說 go/no-go
- 安全界線：不碰系統 Python、不裝 systemd service、不改生產配置

### 報告慣例
- 所有報告使用**中文（繁體）**撰寫
- 用戶強調：「報告記得用中文」

### 研究管道確認
- `managed-agents-research` 繼續保留 — 用戶需要整理的報告，直接看 obsidian vault 太龐大
- `delegate_task` 目前是 Claude Code 專用，未來可能抽象為 plugin slot 模式（參考 ComposioHQ/agent-orchestrator）

