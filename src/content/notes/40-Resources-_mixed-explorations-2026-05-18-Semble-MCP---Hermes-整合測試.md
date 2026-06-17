---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Semble-MCP---Hermes-整合測試
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Semble-MCP---Hermes-整合測試.md
title: Semble MCP — Hermes 整合測試
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- bash
- gateway
- heartbeat
- hermes
- mcp
- native
- seemble
- semble
- uvx
- 未追蹤
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

# Semble MCP — Hermes 整合測試

**日期**: 2026-05-18 | **來源**: `semble-api-notes.md` 未追蹤 lead

## 測試結果

### 安裝與啟動
```bash
uvx --from "semble[mcp]" semble --help
# ✅ 成功，command: seemble (semble 而不是 seemble)
```

### 搜尋測試
```bash
uvx --from "semble[mcp]" semble search "heartbeat_v2.py" --top-k 3
# ✅ 成功，~2s 完成，回傳 3 個結果：
#   1. gateway/run.py:3890 — HeartbeatV2 startup in gateway
#   2. tests/scripts/test_release_acp_registry.py:84
#   3. gateway/heartbeat_v2.py:514 — build_heartbeat_snapshot()
```

## 觀察

- Semble MCP 的搜尋延遲低（~2s 含 cold start）
- 結果精準命中預期檔案（`heartbeat_v2.py` 在 `gateway/heartbeat_v2.py`，不是獨立的 `scripts/heartbeat_v2.py`）
- 這對 `native-mcp` skill 整合有意義：Semble MCP 可直接接到 `native-mcp` 設定

## 後續

- ~~**未追蹤**：Hermes `native-mcp` skill 設定測試（Semble MCP server 設定到 `config.yaml`）~~ → ✅ 2026-05-18 完成
- **未追蹤**：Semble vs `search_files` 在實際任務上的 token 對比（A/B test）

## ✅ 本次探索完成

