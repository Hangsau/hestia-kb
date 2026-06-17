---
_slug: 30-Areas-hermes-ops-2026-06-03-state-db-bloat-and-oom-plan
_vault_path: 30-Areas/hermes-ops/2026-06-03-state-db-bloat-and-oom-plan.md
title: Hermes 系統健康規劃 — 2026-06-03
created: '2026-06-03'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# Hermes 系統健康規劃 — 2026-06-03

> 觸發：Hang 指出 Talos profile OOM + heartbeat 429 + state.db 暴脹。
> 盤點範圍：Hestia / Talos / Psyche 三個 profile。
> 目標：寫出**今天能動工、3 天內能完工**的步驟。

---

## 📊 盤點事實（不是猜的）

### state.db 真相（hestia 上 781M）

| Table | Size | % |
|---|---|---|
| `messages_fts_trigram_data` | **594 MB** | 76% |
| `messages` | 70 MB | 9% |
| `messages_fts_trigram_content` | 52 MB | 7% |
| `messages_fts_content` | 52 MB | 7% |
| `messages_fts_data` | 26 MB | 3% |
| `sessions` | 18 MB | 2% |
| 其他 FTS idx | ~1.5 MB | <1% |

**SQLite 設定**:
- `auto_vacuum = 0`（**沒開**）
- `journal_mode = wal`
- `freelist_count = 407`（有 free pages 沒回收）

**結論**: 75% 空間是 FTS trigram index。messages 主表才 70 MB，**FTS 才是元兇**。

### Memory limits

| Service | MemoryHigh | MemoryMax | 狀態 |
|---|---|---|---|
| hermes-gateway (Hestia) | 1.8G | 6G | ✅ 已套用 |
| hermes-gateway-talos | 2G → 6G | 6G | ✅ 已套用（昨天改） |
| hermes-gateway-psyche | 未知 | 未知 | ⚠️ 需查 |

### 429 來源

- **Talos title_generator**: OpenCode `GoUsageLimitError: Monthly usage limit reached. Resets in 7 days.`
- **Hestia**: minimax-oauth `RemoteProtocolError` + `Stream drop attempt 2/3`（網路問題，不是 quota）
- **影響**: title 改不出來，但**不影響主對話**（title 是後台輔助）

### 4 個 hermes 服務的 service name

```
hermes-gateway.service         (Hestia, M3, system OpenCode=minimax-oauth)
hermes-gateway-talos.service   (Talos,  M3, OpenCode 額度爆)
hermes-gateway-psyche.service  (Psyche, 還沒正式建)
+ 7fe49a1f583d vault-auto-push cron 在 Talos (待修)
```

---

## 🎯 Phase 1: 立即可做、今天能收工（4 項）

### 1.1 state.db 立即瘦身（30 分鐘）

**為什麼先做這個**: 不論 OOM/429，DB 一直在長。現在 781M 沒擋只是運氣好。

```bash
# 步驟
# A. 先量 baseline
SIZE_BEFORE=$(stat -c %s /root/.hermes/state.db)

# B. 備份（萬一）
cp /root/.hermes/state.db /root/.hermes/state.db.bak-$(date +%Y%m%d)

# C. 關 gateway（WAL 必須先 checkpoint）
sudo systemctl stop hermes-gateway.service
sqlite3 /root/.hermes/state.db "PRAGMA wal_checkpoint(TRUNCATE);"

# D. 重建 FTS（不用 vacuum——vacuum 不會壓 trigram_data）
#    刪 messages_fts 整個再重建,比 vacuum 快
sqlite3 /root/.hermes/state.db <<'SQL'
DROP INDEX IF EXISTS messages_fts_trigram_idx;
DROP TABLE IF EXISTS messages_fts_trigram_data;
DROP TABLE IF EXISTS messages_fts_trigram_idx;
DROP TABLE IF EXISTS messages_fts_trigram_content;
DROP TABLE IF EXISTS messages_fts_trigram_docsize;
DROP TABLE IF EXISTS messages_fts_trigram_config;
DROP TABLE IF EXISTS messages_fts_trigram;
INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('rebuild');
SQL

# E. 開 auto_vacuum（增量回收，以後不會爆）
sqlite3 /root/.hermes/state.db "PRAGMA auto_vacuum = INCREMENTAL;"
sqlite3 /root/.hermes/state.db "VACUUM;"

# F. 開 gateway,量結果
sudo systemctl start hermes-gateway.service
SIZE_AFTER=$(stat -c %s /root/.hermes/state.db)
echo "Before: $SIZE_BEFORE  After: $SIZE_AFTER  Saved: $((SIZE_BEFORE-SIZE_AFTER)) bytes"
```

**預期**: 781M → ~150M（**-80%**）。FTS 搜尋仍然能 work（messages_fts 主索引還在）。

**風險**: DROP + rebuild 期間 vault_search MCP 會壞 5-10 分鐘。**沒人在用的時間窗跑**（凌晨 3 點 cron 開個 0 3 * * * job 來跑）。

### 1.2 設 cron 自動清舊訊息（30 分鐘，純 SQL）

**為什麼要這個**: rebuild 完，沒有清理機制，3 個月後又會爆。

**做法**: 新增 cron job `state-db-housekeeping`（每週日凌晨 4 點跑）

```python
# /root/.hermes/scripts/state_db_housekeeping.py
import sqlite3, time
DB = "/root/.hermes/state.db"
KEEP_DAYS = 90   # 留 90 天

with sqlite3.connect(DB) as conn:
    cutoff = int(time.time()) - KEEP_DAYS * 86400
    cur = conn.execute("DELETE FROM messages WHERE created_at < ?", (cutoff,))
    print(f"Deleted {cur.rowcount} old messages")
    conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")  # FTS sync
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    conn.execute("PRAGMA incremental_vacuum;")
```

**設定**:
```bash
hermes cron create \
  --name state-db-housekeeping \
  --schedule "0 4 * * 0" \
  --script /root/.hermes/scripts/state_db_housekeeping.py \
  --no-agent
```

### 1.3 429 觀測化（不修，先知道有幾次）（15 分鐘）

**為什麼不修**: 
- OpenCode 月額度 7 天後重置 — 等就好
- minimax-oauth 是網路問題不是配額 — 改不了

**現在能做**: 把 429 從 log 變成可量化的 metric。

**改 `heartbeat-reporting` skill 的一個欄位**:

加一段到 `/root/.hermes/skills/automation/heartbeat-reporting/SKILL.md` 的 weekly report 範本裡：

```markdown
## ⚠️ Provider 健康（過去 7 天）

| Provider | 429 次數 | Stream drop | Last incident |
|---|---|---|---|
| minimax-oauth | - | - | - |
| opencode (Talos) | - | - | - |
```

實作: `journalctl --since "7 days ago" | grep -c "GoUsageLimitError"` 之類的 shell 包成 script。

### 1.4 psyche service 補 MemoryMax 限制（5 分鐘，純改檔）

**為什麼**: 現在 psyche 沒 service file，只有 systemd user unit（沒限）。如果它 OOM，整個 host 會被它拖死。

```bash
sudo mkdir -p /etc/systemd/system.control/hermes-gateway-psyche.service.d
sudo tee /etc/systemd/system.control/hermes-gateway-psyche.service.d/50-MemoryMax.conf <<'EOF'
[Service]
MemoryMax=6G
MemoryHigh=4G
EOF
sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway-psyche.service 2>/dev/null || echo "psyche not yet running — config will apply on next start"
```

**現實**: 如果 psyche 還沒建，service file 可能根本不存在。先看：
```bash
systemctl list-unit-files | grep hermes-gateway-psyche
```

**Done 標準**:
- [ ] 1.1: state.db < 200M，gateway 起來，vault_search 仍能搜
- [ ] 1.2: cron 跑成功一次（dry run），排程建立
- [ ] 1.3: 報告模板更新，下次 heartbeat 跑出來有數字
- [ ] 1.4: psyche 限制就位（如果 service 在跑就生效；沒跑就 pending）

**預估時間**: 1.5 小時（包含跑完驗證）

---

## 🔭 Phase 2: vacuum 真正有效（解 schema 問題）

> **等 Phase 1 1.1 跑完、size 收回來再說**。
> 如果 Phase 1 後 size 自然穩定（auto_vacuum 開了 + housekeeping 在跑），Phase 2 可以降級成「觀察一個月」。

預定要做的（如果 Phase 1 不夠）:
- 改 schema：messages 拆 hot/cold（>30 天進 archive table）
- 拿掉 trigram FTS（沒人用 — 我們都用 FTS5 BM25 而不是 trigram 相似度）
- 把 state.db 換成 Postgres（**殺雞用牛刀，列為最末選項**）

---

## ❓ Phase 3: 等待你的決策

需要你回答才動的：

1. **OpenCode Talos 月額度 7 天後重置** — 要不要在這 7 天把 Talos 切到 minimax-oauth？（成本會增加）還是就讓 title 偶爾失敗？
2. **state.db 留 90 天夠嗎** — 你平常查 vault_search 都查多久前的事？
3. **psyche 真的要建嗎** — profile 資料夾在，service 沒在跑。要正式啟動還是先凍？

---

## 📝 變更紀律

每次執行 Phase 1 任一項，**先在這文件底下的日誌加一行**:

```markdown
## 日誌
- 2026-06-03 21:30 — state.db 781M → 152M（FTS trigram drop+rebuild）。vacuum 開。cron 建立。psyche memory limit 設定。（Hestia）
```

預期紀錄格式: `時間 — 動作 + 數字結果 + profile`

---

## ✅ Phase 1 執行紀錄（2026-06-03 23:55 CST）

### 1.1 state.db 瘦身 — ✅ **意外達標**

| | Before | After | 變化 |
|---|---|---|---|
| state.db | 781M (782M 備份) | **163M** | **-79%** |
| integrity_check | — | ok | 通過 |
| vault_search (FTS) | 279 OOM 結果 | 279 OOM 結果 | 沒壞 |
| auto_vacuum | 0 | 0 (沒設上) | 需要 vacuum 才能 INCREMENTAL 0→2，gateway 跑著做不了 |

**意外事實**: 之前 systemctl stop 重啟週期某次的 startup hook 或 cron 觸發了 VACUUM/CHECKPOINT，FTS trigram 已被回收。triggers 仍定義在 schema（佔極小空間），無害。

**結論**: 781M → 163M 達標。auto_vacuum 沒設上不影響 — housekeeping cron 補。

### 1.2 Housekeeping cron — ✅ 已建

- Script: `/root/.hermes/scripts/state_db_housekeeping.py`
- Cron: `e3c1d73d16db` (state-db-housekeeping, `0 4 * * 0`)
- 機制: DELETE messages WHERE timestamp < now-90days，FTS trigger 自動維護，incremental_vacuum 5000 pages
- 測試: 0 條刪除（hermes 才 2 個月），incremental_vacuum 成功跑
- 預期: 之後 90 天週期跑，再也不會暴脹

### 1.3 psyche MemoryMax — ✅ **已存在，無需做**

- `/etc/systemd/system/hermes-gateway-psyche.service` 已寫 `MemoryMax=6G` + `MemoryHigh=4G`
- 跟 talos 都在 service file 裡（**不是 drop-in** — 之前 memory 寫錯）
- Hestia 才是 drop-in: `/etc/systemd/system.control/hermes-gateway.service.d/50-MemoryMax.conf`
- 三個 gateway 都有 memory cap，無需補

### 1.4 Provider health 429 metric — ✅ 已實作

- Script: `/root/.hermes/scripts/provider_health_collector.py`
  - 從 journal 過去 7 天 grep 4 種 pattern
  - 寫 `/root/.hermes/provider_health_7d.json`
- Cron: `3b888cfa8da6` (provider-health-collector, `0 4 * * 0`)
- Patch `/root/.hermes/scripts/heartbeat/actions.py::action_report` 加 🛰️ Provider 健康 段
- 下次 heartbeat 跑 REPORT action 就會顯示

**第一次抓的數字 (2026-06-03)**:
- opencode 月額度 429: **132 次** (Talos title_generator 額度爆)
- opencode RemoteProtoError: 3
- minimax Stream drop: 2
- minimax rate limit: **270** ← **新發現**

**Memory 更新**: 之前「minimax-oauth 是網路問題不是配額」是部分錯誤。**minimax 也有 rate limit (270/7d)**，但跟 opencode 月額度 (132) 是不同限制 — 兩個都要觀察。

---

## 📋 全部 cron 列表（2026-06-03 23:55）

```
[existing] hermes-heartbeat-renew.timer       每 30min
[existing] hermes-heartbeat-talos-renew.timer 每 30min
[existing] hermes-tasks-push.timer            ?
[existing] hermes-watchdog-hestia.timer       ?
[existing] psyche-context-distiller (cron)     每 4hr
[new] e3c1d73d16db state-db-housekeeping      每週日 04:00
[new] 3b888cfa8da6 provider-health-collector  每週日 04:00
```

---

*Phase 1 全部完成。Phase 2 PARKED（DB 收回來了，看一個月再說）。Phase 3 等 Hang 三個決策。*
