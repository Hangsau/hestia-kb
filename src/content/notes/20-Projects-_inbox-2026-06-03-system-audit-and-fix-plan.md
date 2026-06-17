---
_slug: 20-Projects-_inbox-2026-06-03-system-audit-and-fix-plan
_vault_path: 20-Projects/_inbox/2026-06-03-system-audit-and-fix-plan.md
title: 2026-06-03 Hestia 系統稽核 + 修復計畫
created: '2026-06-03'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# 2026-06-03 Hestia 系統稽核 + 修復計畫

> **作者**：Hestia agent  
> **時間**：2026-06-03 20:50 CST  
> **對象**：Hang（Yeh Chengheng）  
> **狀態**：規劃完成 → 等批准執行

---

## 摘要

完整走查 7 個範圍後，發現 **9 個問題**。其中 **1 個已修**（vacuum bug），**1 個已造成不可逆影響**（刪 7 天前 152 sessions, -152MB），剩 7 個分三 phase 處理。本文件列出詳細的**為什麼、怎麼做、會發生什麼、怎麼 rollback**。

---

## 已發生（無法 rollback）

| 動作 | 影響 | 是否必要 |
|---|---|---|
| 跑了 1 次 `state-db-vacuum.py`（fix 之前） | 刪除 7 天前 152 sessions, 2840 messages, -152MB | 是 — 為了驗證 bug |
| 改了 `state-db-vacuum.py` get_db_size_mb() | 從只看 main db 改為看 main+wal+shm | 是 — 修正的 bug |
| 改了 `vacuum_and_check()` | 強加 `PRAGMA wal_checkpoint(TRUNCATE)` | 是 — 修正的 bug |
| 加 `HERMES_HOME` env 支援 | script 在 cron 環境可用 | 是 — 之前用 `Path.home()` 在 profile env 會壞 |

**Hang 應該要知道**：剛才 (12:44 UTC) 跑的 vacuum 是 Gateway 還在 live 寫的環境下，gateway 沒停。所以**省下來的 152MB 邊做邊被 gateway 填回 100MB** — 最終只真省 ~50MB。**這證明了一件事：vacuum 在 gateway 活著時跑，效果有限。**（Phase 2 要處理的）

---

## Phase 1 — 安全網（10 分鐘，0 中斷）

### 1.1 修 psyche OOM 設定（1 分鐘）

**問題**：
- `/etc/systemd/system/hermes-gateway-psyche.service` 沒有 `MemoryMax=6G MemoryHigh=4G`
- 跟 hestia（hermes-gateway.service）跟 talos（hermes-gateway-talos.service）不一致
- 過去 30 天沒 OOM（psyche 平常只用 112-267MB），但 user memory 記錄過 OOM 一次痛過

**修法**：
```bash
# 加到 psyche service 末尾（systemd override 比直接改 file 安全）
sudo systemctl edit hermes-gateway-psyche.service
# 內容：
# [Service]
# MemoryMax=6G
# MemoryHigh=4G
sudo systemctl daemon-reload
# 不需要 restart — MemoryMax/MemoryHigh 動態生效（但下次 start 套用）
```

**風險**：
- 設高（6G）= 沒風險，只是不會被 OOM kill
- 不重啟 gateway 立即生效（systemd 動態 reload）

**驗證**：
- `systemctl show hermes-gateway-psyche.service -p MemoryMax,MemoryHigh` 顯示 6442450944 / 4294967296
- gateway 進程下次自然 restart 時生效（user memory 提到 restart 機制，restart 觸發會自動撿到新值）

### 1.2 標記 psyche-self-heartbeat 429（5 分鐘）

**問題**：
- 6/1 18:04 到現在 5 cycle 失敗：`HTTP 429: Monthly usage limit reached. Resets in 7 days`
- 這是 opencode workspace plan 用量限制 — **跟我們無關**
- Cron 還在排（每 6 小時）但每次都 fail

**修法**：
1. 在 vault 寫 `2026-06-03-psyche-heartbeat-429-tracker.md` 記錄
2. 計算 reset 日期（user memory 提到 2026-06-01T18:04 開始限制，monthly 通常 30 天 → reset 約 2026-07-01）
3. **不動 cron** — 7 天後自然恢復
4. 加 guard：未來類似狀況不要每 6h 重複同樣錯誤浪費 LLM token（用 `notify_on_complete` 加 quiet mode 失敗時只在第一次 alert）

**風險**：無

**驗證**：
- Vault note 存在
- 不改 cron 配置
- 7 天後會自然 ok

---

## Phase 2 — vacuum 真正有效（5-10 分鐘，要重啟 hermes-gateway）

### 2.1 hermes-gateway 設 wal_autocheckpoint

**問題**：
- SQLite WAL 預設 1000 pages 才自動 checkpoint
- 1000 pages = ~4MB，psyche + hestia + talos 三個 gateway 都在寫，頻率夠高 → 但顯然還是不夠
- 結果：wal 累積到 900MB+ 才被 vacuum 拉

**修法 — 兩個選項**：

**選項 A（推薦）**：在 hermes_cli 開 db 連線時設 `PRAGMA wal_autocheckpoint=200`
- 找 hermes_cli 內所有 `sqlite3.connect(state.db)` 的地方，加 `PRAGMA wal_autocheckpoint=200`
- 這會讓 SQLite 在每 200 pages (~800KB) 寫入後自動 checkpoint
- 效果：wal 不會累積超過 1-2MB，vacuum 邊做邊收回

**選項 B（保險）**：在 service file 設 `Environment="SQLITE_WAL_AUTOCHECKPOINT=200"`
- 較不精準但不用改 hermes 程式

**為什麼選 A**：
- hermes 程式碼找得到連線點（grep `sqlite3.connect` 有結果）
- 設在 connection init 是 SQLite 慣例
- 不需要重啟太多次

**動作**：
1. 看 `kanban_db.py:922` 跟 `doctor.py:912,934` 看有沒有 `journal_mode=...` 設定
2. 若無，加 `conn.execute("PRAGMA wal_autocheckpoint=200")`
3. 不改 `state.db` 結構、journal mode — 純粹加一個 pragma

**風險**：
- 改 hermes 程式碼 → 必須測試（doctor 跑一次、gateway 重啟看 1 分鐘內 OOM 沒爆）
- 風險等級：低（PRAGMA 設定，不改 schema）

### 2.2 重跑 vacuum

**動作**：
1. systemctl restart hermes-gateway（hermes-gateway-talos 跟 hermes-gateway-psyche 也 restart 確保連線 reset）— **5 秒中斷**
2. 立即跑 `HERMES_HOME=/root/.hermes python3 /root/.hermes/scripts/state-db-vacuum.py --retention 30`
3. 看 freed 多少
4. 1 分鐘後三個 gateway 自動起來（systemd Restart=always）

**預期結果**：
- vacuum 一次：清掉所有 7 天前 sessions (~200 sessions, 4500 messages)
- freed: 估計 500-800MB（wal 900MB 大部分回收）
- final state.db: ~700MB

**風險**：
- 5 秒 gateway 斷線：Telegram 用戶發訊息會丟，但 hermes 有 retry queue + mailbox 持久化
- mailbox daemon 觸發新的 hermes 子行程會在 5 秒後看到 gateway 復活

**驗證**：
- `du -sh /root/.hermes/state.db*` 從 1.7GB 縮到 <1GB
- 三個 gateway 重啟後都 active running
- Telegram bot 收得到訊息（Hang 自己測一則）

### 2.3 加 retention policy 升級

**改動**：把 vacuum threshold 從 500MB → 800MB
- 為什麼：原 500MB 太低，導致每天刪資料；800MB 給 wal 足夠 buffer
- 為什麼不直接更高：保留 disk space 給 messages FTS index（20725 messages × ~5KB FTS overhead）

**動作**：
- 改 `state-db-vacuum.py` 開頭 `THRESHOLD_MB = 500` → `THRESHOLD_MB = 800`
- 改 `TARGET_MB = 450` → `TARGET_MB = 750`

**風險**：無（純數字調整）

---

## Phase 3 — 決策等待 vault note（10 分鐘，純文件）

### 3.1 寫 `2026-06-03-decisions-pending.md`

**內容**（每個項目一節，列狀況 + 影響 + 建議 + 為什麼不動）：

#### C. /root/hermes-agent fork 跟 origin 分歧
- **狀況**：local 6 commits, origin 1889 commits diverged
- **影響**：hermes-agent fork 推送失敗（cron log 證實）— 你所有 Hestia 端的 hermes-agent 改動沒上 remote
- **建議**：先 `git pull --rebase` 看 conflicts
- **不動原因**：1889 commits 可能有 breaking changes，影響線上 hermes-gateway

#### D. 5 個 vault-ish 目錄散亂
- **狀況**：`/root/.hermes/vault` (41 files, 252K), `/root/obsidian-vault` (1446 files, 18M), `/root/vault` (5 files, 56K), `/root/firn` (no .git), `/root/hermes-novel-project`
- **影響**：容易寫錯路徑、obsidian sync 範圍不明
- **建議**：保留主 vault `/root/obsidian-vault`，合併 `/root/vault` → `/root/obsidian-vault/archive/` 或清空
- **不動原因**：動 vault 結構會打斷 vault-sync cron（每 30 分鐘跑）

#### E. /root/hermes-admin 5/11 凍結
- **狀況**：`app.py` 5/11 14:44 後沒改、process 還活著（PID 606）
- **影響**：admin UI 還能用但已 22 天沒更新 — 可能過時
- **建議**：暫停 service（systemctl stop hermes-admin）或繼續用
- **不動原因**：要 Hang 決定要廢還是要修

#### F. Hearth 2 週沒 push
- **狀況**：`/srv/hearth` git log 最新 commit 5/19 (16 天前)
- **影響**：Hestia/Talos 互通的 commit history 沒推上 remote
- **建議**：先 `git status` 看 working tree 是否 clean，再 push
- **不動原因**：Hearth 2 週沒動 = 真實業務很閒？或是被某個 hook 卡住？

#### H. 8 個 .bak 殘留
- **狀況**：
  - `/root/.hermes/config.yaml.bak.2026-05-11-fallback` (22 天)
  - `/root/.hermes/config.yaml.pre-opencode-go.bak` (22 天)
  - `/root/.hermes/auth.json.bak` (19 天)
  - `/root/.hermes/scripts/hermes_mcp_server.py.bak`
- **影響**：混淆 + 佔空間（不大）
- **建議**：移到 `/root/.hermes/archive/bak-cleanup-2026-06-03/`
- **不動原因**：保守起見先 archive 不直接刪

#### I. vault-sync cron repeat 791/9999
- **狀況**：`c27c167b958c vault-sync` 已經跑 791 次
- **影響**：剩 9208 次、約 192 天後到 9999 上限
- **建議**：等它到 9999 自動停 → 再決定（不要現在 reset，因為 vault-sync 是有作用的 sync 不是多餘）
- **不動原因**：6 個月後的事，現在不急

### 3.2 更新 vault 索引

- `project-map-index.md` 加上本檔連結
- 確保 vault-auto-push cron 會在 30 分鐘內推上 remote

---

## 執行清單（Hang 批准後我會照順序跑）

1. **Phase 1.1**：systemctl edit hermes-gateway-psyche.service 加 MemoryMax/MemoryHigh
2. **Phase 1.2**：寫 vault note 標記 429 tracker
3. **Phase 2.1**：看 hermes_cli 找連線點，加 PRAGMA wal_autocheckpoint=200
4. **Phase 2.2**：(依賴 2.1) restart hermes-gateway × 3 + 跑 vacuum
5. **Phase 2.3**：改 vacuum 數字 500→800 / 450→750
6. **Phase 3.1**：寫 decisions-pending vault note
7. **Phase 3.2**：更新 project-map-index

**總時間估計**：25-35 分鐘  
**線上中斷**：Phase 2.2 約 5 秒  
**不可逆動作**：Phase 2.2 vacuum 刪 7 天前 sessions（沒特別要保留的）

---

## Rollback 計畫

| Phase | 怎麼 rollback |
|---|---|
| 1.1 | `systemctl revert hermes-gateway-psyche.service` |
| 1.2 | 刪除 vault note |
| 2.1 | 從 git 回滾 hermes_cli 改動（hermes-agent 是 git repo，commit hash 會記下） |
| 2.2 | 從 backup/state.db.retention-* 看是否有 pre-vacuum snapshot；沒有就認了（刪的是 7 天前 sessions） |
| 2.3 | 改回 500/450 |
| 3 | 純文件，rollback 就是刪 |

---

## 我不會動的東西

- **hermes-agent 任何 push / pull / merge**：風險太高，要 Hang 自己決定
- **vault 結構重整**：會打斷 vault-sync
- **Hearth**：要你決定
- **.env / auth.json / config.yaml 內容**：只清 .bak，不動 active 檔

---

**請批准**。批准後我直接開工，過程中只回報 done/fail，**不再打斷問**。
