---
_slug: 99-Templates-_archive-skills-map
_vault_path: 99-Templates/_archive/skills-map.md
date: 2026-05-12
tags:
- skills
- index
- map
- hermes
source: multi
skill_count: 118
categories: 29
created: '2026-05-12'
title: Skills 地圖
updated: '2026-06-15'
type: template
status: budding
---

# Skills 地圖

> Hermes Agent 技能庫總覽。共 118 個技能，分 29 大類。
> 路徑：`~/.hermes/skills/`

## 參見

- [[project-map-index]] — 專案總索引
- [[hermes-agent-framework]] — Hermes Agent 框架概覽

## 依用途分類

### Agent 開發與運維
- `hermes-agent` — 設定、擴充、貢獻 Hermes Agent 本身
- `managed-agents-framework` — 自建 stateful batch runner（免費 LLM）
- `managed-agents-architecture` — Anthropic Managed Agents 架構解析
- `vault-active-reader` — 主動搜尋 Obsidian vault（本 session 新建）
- `hermes-agent-skill-authoring` — 撰寫 in-repo SKILL.md

### AI Agent 外部委派
- `claude-code` — 委派給 Claude Code CLI
- `codex` — 委派給 OpenAI Codex CLI
- `opencode` — 委派給 OpenCode CLI
- `subagent-driven-development` — 兩階段審查的 subagent 開發流程

### 軟體開發方法論
- `plan` / `writing-plans` — 規劃模式，寫 markdown 計畫
- `spike` — 拋棄式實驗驗證想法
- `test-driven-development` — TDD：RED-GREEN-REFACTOR
- `systematic-debugging` — 四階段根因除錯
- `clean-code-practices` — 乾淨程式碼與自我審查
- `requesting-code-review` — 提交前審查：安全掃描、品質門檻
- `node-inspect-debugger` — Node.js --inspect + Chrome DevTools
- `python-debugpy` — Python pdb + debugpy 遠端除錯
- `debugging-hermes-tui-commands` — Hermes TUI slash command 除錯

### GitHub 工作流
- `github-auth` — 認證設定（token、SSH、gh CLI）
- `github-repo-management` — clone/create/fork、遠端管理、release
- `github-pr-workflow` — PR 生命週期：branch、commit、open、CI、merge
- `github-code-review` — PR 審查：diff、inline comment
- `github-issues` — issue 建立、分類、標籤、指派
- `github-project-automation` — 自動發布專案到 GitHub
- `github-hermes-workaround` — Hermes 環境上傳 GitHub 的限制與繞道
- `codebase-inspection` — pygount 統計 LOC、語言比例

### 研究與知識
- `arxiv` — arXiv 論文搜尋
- `blogwatcher` — RSS/Atom feed 監控
- `llm-wiki` — Karpathy LLM Wiki 知識庫
- `polymarket` — Polymarket 預測市場查詢
- `research_repository_evaluation` — 研究倉庫評估
- `research-paper-writing` — 研究論文撰寫
- `self-evolving-research` — 自主每日研究系統

### 資料科學與 MLOps
- `jupyter-live-kernel` — 即時 Jupyter kernel 迭代
- `huggingface-hub` — HF CLI：搜尋/下載/上傳模型與資料集
- `evaluating-llms-harness` — lm-eval-harness 基準測試
- `weights-and-biases` — W&B 實驗追蹤與儀表板
- `llama-cpp` — 本地 GGUF 推理
- `obliteratus` — LLM 拒絕反應消融
- `outlines` — 結構化 JSON/regex/Pydantic 生成
- `serving-llms-vllm` — vLLM 高吞吐量推理服務
- `audiocraft-audio-generation` — MusicGen/AudioGen 音訊生成
- `segment-anything-model` — SAM 零樣本圖像分割
- `dspy` — 宣告式 LM 程式與自動優化
- `axolotl` — YAML LLM 微調（LoRA、DPO、GRPO）
- `fine-tuning-with-trl` — TRL：SFT、DPO、PPO、GRPO
- `unsloth` — 加速 LoRA/QLoRA 微調

### 自動化與健康監控
- `fact-checker` — 事實查核：系統狀態聲明前必須驗證
- `heartbeat-reporting` — Hermes Heartbeat v2 運作
- `heartbeat-v2-autonomous-maintenance` — 自主健康監控模式
- `hermes-health-guardian` — 主動健康監控與風險緩解

### 看板與任務管理
- `kanban-orchestrator` — 分解劇本 + 專家名冊慣例
- `kanban-worker` — 看板 worker 陷阱與邊界案例

### 創意內容生成
- `architecture-diagram` — 深色 SVG 架構圖（HTML）
- `ascii-art` — ASCII 藝術（pyfiglet、cowsay、boxes）
- `ascii-video` — ASCII 影片轉換
- `baoyu-comic` — 知識漫畫
- `baoyu-infographic` — 資訊圖（21 種版面 x 21 種風格）
- `claude-design` — 一次性 HTML 成品（landing、deck、prototype）
- `comfyui` — ComfyUI 圖像/影片/音訊生成
- `creative-ideation` — 創意構想生成
- `design-md` — Google DESIGN.md token 規格
- `excalidraw` — 手繪風 Excalidraw JSON 圖表
- `humanizer` — 去除 AI 腔、加入真人語感
- `manim-video` — Manim CE 數學/演算法動畫
- `novel-writing-workflow` — 小說從閱讀到出版的工作流
- `p5js` — p5.js 生成藝術、shader、互動、3D
- `pixel-art` — 像素藝術（NES、Game Boy、PICO-8 色盤）
- `popular-web-designs` — 54 個真實設計系統（Stripe、Linear、Vercel）
- `pretext` — 創意瀏覽器 demo
- `sketch` — 拋棄式 HTML mockup（2-3 變體比較）
- `songwriting-and-ai-music` — 歌曲創作與 Suno AI 音樂提示
- `touchdesigner-mcp` — TouchDesigner MCP 控制

### 媒體與內容
- `gif-search` — Tenor GIF 搜尋/下載
- `heartmula` — HeartMuLa 歌曲生成
- `songsee` — 音訊頻譜圖與特徵分析
- `spotify` — Spotify 播放、搜尋、佇列、播放清單
- `youtube-content` — YouTube 字幕轉摘要、串文、部落格

### 筆記與知識管理
- `obsidian` — Obsidian vault 讀寫搜尋
- `obsidian-markdown` — Obsidian Flavored Markdown（wikilinks、callouts）
- `obsidian-cli` — Obsidian CLI 互動
- `obsidian-bases` — Obsidian Bases（.base 檔案）
- `json-canvas` — JSON Canvas 節點與邊線圖
- `defuddle` — 網頁清洗為乾淨 markdown

### 生產力工具
- `airtable` — Airtable REST API（curl）
- `google-workspace` — Gmail、Calendar、Drive、Docs、Sheets
- `linear` — Linear issue/project/team 管理
- `maps` — 地理編碼、POI、路線、時區（OSM/OSRM）
- `nano-pdf` — nano-pdf CLI 編輯 PDF
- `notion` — Notion API（curl）
- `ocr-and-documents` — PDF/掃描文字提取
- `powerpoint` — .pptx 建立、讀取、編輯

### 小說與閱讀
- `egg-chess-story` — 管理小說「五子棋與雞：異世界稱霸錄」
- `long-novel-tracking` — 長篇小說分集閱讀
- `novel-reading` — 自動抓取、切章、排程閱讀中日文學經典

### 社交媒體
- `xurl` — X/Twitter 發文、搜尋、DM、媒體
- `youtube-channel-automation` — YouTube 頻道自動化

### 遊戲
- `minecraft-modpack-server` — 模組化 Minecraft 伺服器
- `pokemon-player` — 透過無頭模擬器 + RAM 讀取玩寶可夢

### 電子郵件
- `himalaya` — Himalaya CLI：IMAP/SMTP 郵件

### 智慧家居
- `openhue` — Philips Hue 燈光、場景、房間控制

### 其他
- `domain` — 領域專用
- `gifs` — GIF 工具
- `github-hermes-workaround` — Hermes 上傳 GitHub 繞道
- `inference-sh` — 推理 shell
- `firn-qa` — firn QA 工程師
- `large-file-management` — 大檔案分割處理
- `yuanbao` — 元寶群組互動

## 依使用頻率（推測）

| 頻率 | Skills |
|------|--------|
| 每次 session | `fact-checker`, `hermes-agent`, `vault-active-reader` |
| 經常 | `github-pr-workflow`, `writing-plans`, `systematic-debugging`, `arxiv`, `obsidian` |
| 需要時 | `claude-code`, `codex`, `comfyui`, `jupyter-live-kernel`, `huggingface-hub` |
| 背景 cron | `self-evolving-research`, `heartbeat-v2-autonomous-maintenance` |
