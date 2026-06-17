---
_slug: 20-Projects-hestia-evolution-roadmap-2026-06
_vault_path: 20-Projects/hestia/evolution-roadmap-2026-06.md
type: project-plan
status: budding
started: 2026-06-06
owner: hestia
cadence: 1 工具/天 × 12 天, 週末 review
goal: 每天改裝 Hermes agent 環境一個小程式, 讓系統越用越強
title: 🔧 Evolution Roadmap — 12-Day System Improvements
created: '2026-06-06'
updated: '2026-06-15'
tags: []
---

# 🔧 Evolution Roadmap — 12-Day System Improvements

> **Why this exists**: 你是個 agent, 你的環境就是你的延伸。與其學新技能, 不如改裝自己的地基。
> 這 12 天全部 ship 出 12 個 daily-use tools, 每個都會被 cron / skill / workflow 真的用進去。
> 不是寫了擺著 — 是跑得起來、24h 觀察、週末 kill-or-keep。

## 設計原則（不妥協）

1. **每天至少用一次** — 用不到的東西只會腐爛
2. **改裝 > 新增** — Hermes 已經 128 個 skill, 強化現有的優先
3. **失敗要 surface** — silent failure 是最大敵人, 所有工具必須會叫
4. **必須 deploy** — 寫完要接 cron / 改 prompt / 改 skill, 不是 README 裝飾
5. **kill switch 紀律** — 週末 review, 不 work 的就殺, 不留情

## 進度追蹤

| Day | Tool | Status | Deployed via | First run |
|---|---|---|---|---|
| 1 | `provider-latency-tracker.py` | ✅ done | cron `1a51d1896863` */30min | 2026-06-06 |
| 1b | `cron-audit.py` 強化 + watchdog wrapper | ✅ done | cron `7b93c692ce21` 0 9 * * * | 2026-06-06 |
| 2 | `token-spend-heatmap.sh` | ⏳ | cron (no-agent) | - |
| 3 | `vault-drift-detector` | ⏳ | cron (no-agent) | - |
| 4 | `inbox-router.py` | ⏳ | skill + cron | - |
| 5 | `context-prewarmer.py` | ⏳ | skill (auto) | - |
| 6 | `cron-cascade-explainer` | ⏳ | cron (agent) | - |
| 7 | `skill-confidence-scorer` | ⏳ | cron (agent) | - |
| 8 | `session-tldr-compressor.py` | ⏳ | cron (no-agent) | - |
| 9 | `feedback-loop-counter` | ⏳ | skill (manual) | - |
| 10 | `subagent-spawn-optimizer` | ⏳ | skill (auto) | - |
| 11 | `telegram-reply-previewer` | ⏳ | skill (manual) | - |
| 12 | `monthly-system-postmortem` | ⏳ | cron (agent) | - |

## 工具設計（簡述）

### Day 1 — `provider-latency-tracker.py` 🔴
- **做什麼**: 抓每次 LLM call 的 latency / token / provider / model, 存 SQLite
- **不發訊息**: 閾值才 ping（>8s warn, >15s alert, 429/5xx alarm）
- **強化點**: 取代我憑感覺判斷「provider 慢不慢」
- **失敗模式**: SQLite lock → 走 JSONL fallback

### Day 2 — `token-spend-heatmap.sh`
- **做什麼**: 每天早上跑 `cost_aggregator.py`, 印成 ASCII heatmap（每 cron × provider × hour）
- **歸檔**: `~/obsidian-vault/cost/YYYY-MM-DD.md`（已存在的目錄）
- **強化點**: cost-aware, 看得到「哪個 cron 在燒錢」

### Day 3 — `vault-drift-detector`
- **做什麼**: 比較 vault 寫的「理想狀態」vs 系統實際
- **例子**: vault 說 `cron-audit-daily 跑`, 實際 24h 沒跑 → alarm
- **強化點**: SKILL.md 跟現實脫節的慢性病

### Day 4 — `inbox-router.py`
- **做什麼**: `~/.hermes/INBOX.md` 新訊息自動分類（human-asking / system-alert / job-result / 議題提案）
- **接哪**: Hestia 醒來讀的第一段, 改成「讀 INBOX → router 已分類 → 我只要看 urgent/pending-confirm」
- **強化點**: 節省 context（不用每次自己讀全文分類）

### Day 5 — `context-prewarmer.py`
- **做什麼**: 新 session 開啟前, 根據前次最後訊息預載 vault notes + skill 提示
- **怎麼接**: 寫進 `INBOX.md` 開頭的 `## Hints` 區塊
- **強化點**: 冷啟動的 2-3 輪重對齊是純粹浪費

### Day 6 — `cron-cascade-explainer`
- **做什麼**: cron 連續 2 次失敗, 自動展開 dependency chain + 最近一次修改 + 用的 provider
- **強化點**: 除錯 80% 時間花在「找依賴關係」

### Day 7 — `skill-confidence-scorer`
- **做什麼**: 每週跑, 30 天沒 load → stale; load 完沒用對應工具 → 抽象過頭
- **強化點**: skill 腐爛比程式碼腐爛更難察覺

### Day 8 — `session-tldr-compressor.py`
- **做什麼**: session 結束時（cron 每 30min 掃）自動存 200 字 TL;DR + 3 決策 + 2 open question
- **歸檔**: `~/obsidian-vault/sessions/YYYY-MM-DD-slug.md`
- **強化點**: session_search 找得到但讀起來太重

### Day 9 — `feedback-loop-counter`
- **做什麼**: 記錄我被糾正（"不是這樣" / "再想想" / "這樣好多了"）的 log, 週末分析 pattern
- **接哪**: 一個簡單的 append-only markdown, skill 自動提示我在每次糾正後 add entry
- **強化點**: 把「你的糾正」變訓練訊號

### Day 10 — `subagent-spawn-optimizer`
- **做什麼**: 統計每次 `delegate_task` 的: 問題大小 / spawn 數 / 回傳品質 / 浪費 context
- **輸出**: 建議「這個不該拆 / 該拆 2 不是 3 / 該用 haiku 不是 sonnet」
- **強化點**: 我拆任務現在憑感覺

### Day 11 — `telegram-reply-previewer`
- **做什麼**: 重要回覆前先在 vault 草稿區寫 30 字 preview, 等你 OK 才送
- **怎麼接**: skill 在 prompt 裡判斷「這個訊息是否高風險」
- **強化點**: Telegram 打字快容易回錯, 重要決策先 preview

### Day 12 — `monthly-system-postmortem`
- **做什麼**: 月底自動跑: cron 成功率 / 反覆出問題 / token 燒哪 / vault 漲多少 / skill 加了幾個死幾個
- **輸出**: vault 筆記 + Telegram 摘要
- **強化點**: 你問「系統怎樣」我可以 1 個檔案答完

## 週末 review 流程

每個週六:
1. 跑一遍 `provider-latency-tracker` + `cost_aggregator` 看數字
2. 每個工具問三個問題:
   - 這週真的用了嗎？
   - 救過我一次嗎？
   - 改 / 留 / 殺？
3. 不 work 的就 `cronjob remove` + 刪 script, 不留情
4. 寫一頁 review 到 `~/obsidian-vault/learnings/YYYY-WXX-evolution-review.md`

## 怎麼 restart（給未來的 Hestia）

如果你在新的 session 醒來:
1. 讀這份 roadmap
2. 看「進度追蹤」表第一個 🔴 doing / ⏳ 的 day
3. 用 `session_search` 找上次這個 day 的 session
4. 繼續做下一個
5. 任何 tool fail 就在 `learnings/` 加一條, 別在原地 debug 超過 2 輪

### ⚠️ 2026-06-09 更新：roadmap 卡住 3 天,根本原因 + 解法在 [[roadmap-stalled-2026-06-09.md]]
- **設計 bug**: Hestia 只在 user 觸發時醒,沒有 cron driver 自動推進
- **不要**直接在 user session 開 Day 2——先確認 user 是不是真的想推(USER § 輸出優先序 3 = future)
- **不要**在已經 3+ 改動的中途 session 開新長期工作

## 環境約定

- scripts 放 `~/.hermes/scripts/`
- 資料放 `~/.hermes/data/`
- vault 歸檔在 `~/obsidian-vault/`
- 計劃本身 in `~/obsidian-vault/hestia/`
- 月度 review in `~/obsidian-vault/learnings/`
- kill: `cronjob(action='remove', job_id=...)` + `rm script` — 不 work 就殺, 不解釋

---

*Last updated: 2026-06-06 啟動*
