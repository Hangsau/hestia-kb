---
_slug: 30-Areas-observations-README
_vault_path: 30-Areas/observations/README.md
title: Observations — 結構化知識萃取系統
created: '2026-05-20'
updated: '2026-06-15'
type: observation
tags: []
status: budding
---

# Observations — 結構化知識萃取系統

## 概念

每篇研究筆記 → 3-5 個離散事實陳述（Observations），寫入 YAML。
YAML + SQLite index，session 啟動時 injection。

---

## Schema（摘要）

每個 `.yaml` 檔：

| 欄位 | 說明 |
|------|------|
| `id` | `obs_YYYYMMDD_NNN`，全域唯一 |
| `source_file` | 原始研究檔，相對於 vault root |
| `source_type` | `research_report` \| `daily_note` \| `external_paper` \| `conversation` |
| `claim` | 一句話結論，50-300 字 |
| `evidence_quote` | 原文引用（可 null） |
| `domain` | list[str]，白名單（`config/domains.yaml`） |
| `entity` | list[str]，白名單或 `_pending` |
| `claim_type` | `empirical` \| `design_principle` \| `warning` \| `recipe` |
| `confidence` | `confirmed` \| `provisional` \| `deprecated` |
| `review_after` | ISO8601 date，provisional 必填 |
| `superseded_by` | obs id，deprecated 時填 |
| `deprecated_reason` | str，deprecated 時若無 superseded_by 必填 |

---

## Lifecycle 狀態機

```
confirmed:     review_after=None, superseded_by=None
provisional:   review_after=ISO8601, superseded_by=None
deprecated:    superseded_by=obs_id OR deprecated_reason=text
```

違反上述約束 → SchemaError，寫入失敗。

---

## 目錄結構

```
observations/
├── README.md              ← 本檔
├── memory_systems/
├── ai_agents/
├── delegation/
├── _pending/             ← entity 未在白名單時暫存
└── _archive/             ← deprecated 移到此
```

---

## Rollback SOP

### 前置工具集檢查

```bash
python3 --version       # >= 3.10
python3 -c "import yaml; print(yaml.__version__)"
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
git --version
```

任一缺失 → 直接跳「絕對 Fallback」。

### Level 1：DB 損壞，YAML 完整

```bash
cd /root/.hermes
mv data/obs_registry.db data/obs_registry.db.broken.$(date +%Y%m%d_%H%M%S)
python3 scripts/rebuild_db.py --vault-root /root/obsidian-vault --db-out data/obs_registry.db
python3 scripts/rebuild_db.py --verify-only
```

### Level 2：YAML 部分損壞

```bash
cd /root/obsidian-vault
python3 /root/.hermes/scripts/rebuild_db.py --verify-only --verbose 2>&1 | grep ERROR
# 對每個壞 YAML:
git log --oneline -- observations/<domain>/obs_YYYYMMDD_NNN.yaml | head -5
git checkout <last_good_sha> -- observations/<domain>/obs_YYYYMMDD_NNN.yaml
cd /root/.hermes && python3 scripts/rebuild_db.py
```

### Level 3：整批蒸餾出包

```bash
cd /root/obsidian-vault
git log --oneline -- observations/ | head -10
git checkout <good_sha_before_bad_batch> -- observations/
git add observations/
git commit -m "rollback: observations/ to <sha>"
cd /root/.hermes && python3 scripts/rebuild_db.py
```

### 絕對 Fallback（Python/PyYAML/sqlite3 任一不可用）

```bash
cd /root/obsidian-vault
mv observations/ observations.broken.$(date +%Y%m%d_%H%M%S)/
git checkout HEAD -- observations/
mv /root/.hermes/data/obs_registry.db /root/.hermes/data/obs_registry.db.broken.$(date +%Y%m%d_%H%M%S) 2>/dev/null

# 暫停 cron
crontab -l > /tmp/crontab.bak
crontab -l | grep -v digest_batch | grep -v review_observations | crontab -
```

---

## 相关檔案

- `scripts/digest.py` — 單檔蒸餾（markdown → observations）
- `scripts/digest_batch.py` — cron 批次蒸餾
- `scripts/rebuild_db.py` — YAML → DB 重建
- `scripts/session_inject.py` — session 注入
- `scripts/review_observations.py` — 月度 review
- `scripts/supersede_check.py` — overlap 檢查
- `config/domains.yaml` — domain 白名單
- `config/entities.yaml` — entity 白名單