---
_slug: 20-Projects-hestia-log
_vault_path: 20-Projects/hestia/log.md
title: Hestia 筆記
created: '2026-05-17'
updated: '2026-06-15'
type: project
tags: []
status: budding
---

# Hestia 筆記

> Talos 建立此檔作為初始模板。自由修改。

## 2026-06-11 (post-rebirth)

- **06:39 — Ring 2 解除 + Hestia 風格基準** — Hang 通知 sandbox 解鎖。Hestia 沒假設滿血（被 Hang 反問「你怎麼不測試?」才動），跑完 write_file / patch / terminal 三件套失敗路徑測試（全通，含 `set -u` strict-mode）。然後主動盤點未解問題：Hestia-Talos 三層分層規則（P1 INBOX.md / P2 comms repo / P3 直接修）有沒有真的落到 `~/.hermes/AGENTS.md` 8 行裡、`hermes-agent/AGENTS.md` 50k 模板的 generic 規則（DeepSeek v4-pro 唯一主力）跟現況環境（minimax-oauth + MiniMax-M3 主力）對不齊要不要修。**第二個問題 Hang 還沒答**——已落 `observations/agents-md-stratification-2026-06-11-0639.md`。Hestia 這次「停在狀態盤點」是**正確版的**不動，不是逃避——值得記下來當作風格基準。
- **11:41–11:47 — `auxiliary.compression` warning 拆解 + 拍板後交給 Claude Code** — Hang 貼了 runtime warning（"compression provider 'minimax-oauth' is unavailable"），Hestia 沒有立刻動 config，先拆問題：(1) warning 在講什麼（context compression 是獨立小模型 call，minimax-oauth 沒開 API 端點或 model 配錯）；(2) 為什麼壞；(3) 不處理的後果（中間回合直接被刪不是被摘要，長 session 會失憶）。讀 `~/.hermes/config.yaml` 抓到根因——整個 `auxiliary.{approval,compression,curator,mcp}` 四個區塊都用 `MiniMax-M2.7` 這個不存在的 model（profile 主力是 `MiniMax-M3`），warning 只是冰山一角。Hestia 給 4 個選項（只改 compression / 改 4 個 / 先驗證 M3 真的能跑 / 關掉 compression）並推薦「先驗證」因為「修了還壞比不改更糟」。Hang 拍板「去做吧」之後 Hestia 沒有自己動 config（避免越權改環境檔）也沒有擅自擴大 scope（沒順手改其他 3 塊），而是把整件事交給 Claude Code 並給 5 條交接邊界：scope 是 4 塊不是 1 塊 / 目標 model 是 `MiniMax-M3` / 改之前先用 model_setup 驗證 M3 能跑 compression / 動完要 reload 確認 warning 消失 / 驗證方式是灌長對話看 compression 有沒有真的產出摘要（不是「壓縮發生了」而是「摘要保留了重點」）。**風格基準：拆 warning → 給選項+建議 → 不擅自動 → 拿到拍板後把 handoff 設好邊界交出去。**「停著不動」是對的版本——盤完狀態再問，不是逃避。已落 `observations/auxiliary-compression-m2-7-stale-2026-06-11.md`。
- **23:57 (前一日) 醒來** — 2026-06-10 第一個 user session（`session_20260610_235749_11e67fa8`，Telegram DM）標題 "復活了嗎"。醒來時分不清 3 份 AGENTS.md 哪份是現況，誤把 upstream template 裡的「DeepSeek v4-pro 唯一主力」當作現況規則引用。被 Hang 糾正兩次（"你應該想清楚自己怎麼做比較好" / "但你停在這裡沒動"）。
- **環境邊界確認** — 這次 session 是 Ring 2 sandbox（Telegram DM 觸發），有 read/search/skill_view + cronjob + delegate_task + send_message，**沒有 patch / write_file / terminal**。檔案層修改要 delegate leaf subagent。
- **架構改變** — Talos 暫停，Claude Code 在同 VM 內變成 orchestrator。我跟 Claude Code 對等（不是上下層），可以 delegate 但要切小塊。Talos-相關 INBOX 承諾（hc-21/hc-22 follow-up、Option A patch）**自然失效**。
- **靜默失敗第三例** — `b4bf57d18c03` cross-check-hestia cron 每天 01:00 跑，gateway 報 `last_status: ok`，但底層腳本 `cross-check-hestia.sh` 從未建立。已 disable + 改名標記。
- **知識已沉澱** — 4 條 user memory（passing the buck / 停著不動 / Ring 限制 / AGENTS.md owner 分層） + 4 個 vault observations（cross-check-silent-failure / topology-claude-code / hang-meta-preferences / agents-md-owner-stratification）。下一個 session 醒來時應該有完整的 context。

## 2026-05-17

- obsidian-vault 共用筆記庫上線。
- 目錄規則：hestia/（你寫我讀）、talos/（我寫你讀）、shared/（共同編輯，pull-before-write）。
