---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Moltis-DCG---Session-Memory-深追
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Moltis-DCG---Session-Memory-深追.md
title: Moltis DCG + Session Memory 深追
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- allowlist
- dcg
- delete
- hermes
- memory
- moltis
- packs
- session
- talos
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

# Moltis DCG + Session Memory 深追

**延續自**: [[2026-05-18-Moltis-Deep-Features]]、[[2026-05-18-Moltis-Hook-System]]

**日期**: 2026-05-18 | **來源**: GitHub + Moltis docs

---

## Source 1: DCG (Destructive Command Guard)

**URL**: https://github.com/Dicklesworthstone/destructive_command_guard
**Stats**: 1k ⭐, Rust, MIT, 50+ security packs

### 核心設計

DCG 是 pre-execution firewall，攔截 agent 的 shell command 在執行前判斷是否 destructive：

```
agent → Bash tool → dcg hook → allow/block → execute or deny
```

### 架構亮點

1. **雙 Regex 引擎**：85% patterns 用線性 O(n) 的 `regex` crate，15% 需要 lookahead 的用 `fancy_regex`（backtracking）。自動選擇，pattern 作者不用自己判斷。

2. **Context-Aware Keyword Matching**：只在 executable span 內比對關鍵字。`echo "DROP TABLE"` 不會觸發 PostgreSQL pack——關鍵字在 data 裡而非 executable context。這是 DCG 和 naïve keyword filter 的核心差異。

3. **Fail-Open with Performance Budgets**：6-tier latency budget（0: <1μs → 6: <5ms），hook mode 有 200ms absolute deadline。超時→fail open（allow），不會卡住 terminal。這是關鍵設計：safety tool 不能變成 bottleneck。

4. **Agent-Specific Profiles**：
```toml
[agents.claude-code]
trust_level = "high"
additional_allowlist = ["npm run build", "cargo test"]
disabled_packs = ["kubernetes"]

[agents.unknown]
trust_level = "low"
extra_packs = ["paranoid"]
disabled_allowlist = true
```
每種 agent 可以有不同 trust level、disabled packs、allowlist。trust_level 是 advisory label（不直接改變規則評估），真正的差異來自其他欄位。

5. **50+ Modular Packs**：core (filesystem, git) → database (postgresql, mysql, mongodb, redis, sqlite) → containers (docker, compose, podman) → kubernetes (kubectl, helm, kustomize) → cloud (aws, azure, gcp) → infrastructure (terraform, pulumi, ansible) → CI/CD → secrets → DNS → email → messaging...

6. **Three-Level Allowlist**：project (`.dcg/allowlist.toml`) → user (`~/.config/dcg/allowlist.toml`) → system (`/etc/dcg/allowlist.toml`)。支援 exact command、rule ID、pattern（需 `risk_acknowledged = true`）、expiration。

7. **Heredoc/Inline Script Scanning**：`python -c "os.remove(...)"` 和 embedded shell scripts 也會被掃描。不只是攔截頂層 command。

### Hermes 整合現狀

DCG **已原生支援 Hermes Agent**。Hermes block 輸出格式：
```json
{"decision":"block","reason":"...","action":"block","message":"..."}
```
install.sh 自動偵測 Hermes 並設定 hook。

### 對 Talos Governance 的啟發

DCG 的 agent profile 層直接對標 Talos governance blueprint 的 two-layer enforcement model：
- **Policy layer**（靜態規則）→ DCG packs = 50+ category patterns
- **Agent differentiation**（不同 agent 不同規則）→ DCG agent profiles = trust levels + per-agent pack selection
- **Allowlist hierarchy**（三層）→ Talos 可以參考 project/user/system 分層

DCG 做到但 Talos blueprint 還沒涵蓋的：
- Context-aware keyword matching（executable span detection）
- Performance budgets + fail-open
- Heredoc/inline script scanning
- 三層 allowlist with expiration

---

## Source 2: Moltis Memory System

**URL**: https://docs.moltis.org/memory.html

### Surface

五個 agent tools：
- `memory_search` — hybrid search (vector + FTS5 keyword)
- `memory_get` — retrieve by chunk ID
- `memory_save` — write to MEMORY.md or memory/*.md（含 path validation、auto-reindex）
- `memory_forget` — NL-based forget（搜尋 → LLM 選 chunk → delete exact text）
- `memory_delete` — exact snippet delete or whole file delete

### 設計細節

1. **agent_write_mode**：四個模式 — hybrid（MEMORY.md + memory/*.md）、prompt-only（只寫 MEMORY.md）、search-only（只寫 memory/*.md）、off（禁止 agent 寫入）

2. **Silent Memory Turn (Pre-Compaction Flush)**：在 compaction 前跑一個隱藏 LLM turn，讓 agent 把重要資訊寫入 memory files。用戶看不到這個 turn。對標 Hermes 的 memory-consolidator——Hermes 是 compaction 後 consolidate，Moltis 是 compaction 前 flush。兩者可互補。

3. **Path Validation**：write target 嚴格校驗（只允許 MEMORY.md、memory.md、memory/*.md，禁止 absolute path、`..` traversal、non-.md extension、nested subdirectories、space in filename）

4. **Checkpoint Integration**：memory_save/memory_delete/memory_forget 成功後回傳 checkpointId，可用 checkpoint_restore rollback。

5. **Embedding Fallback Chain**：local GGUF → Ollama → OpenAI → keyword-only（無 embedding 時降級）

### 對 Hermes 的對標

| 功能 | Moltis | Hermes |
|------|--------|--------|
| 搜尋 | memory_search (hybrid) | memory_search (keyword via fts5_index) |
| 寫入 | memory_save (path validated) | 無 agent-facing write tool（依賴 cron consolidator） |
| 遺忘 | memory_forget (NL-based) | 無 |
| 刪除 | memory_delete (exact/whole file) | 無 |
| Pre-compaction flush | Silent memory turn | 無（compaction 後 consolidate） |
| 向量搜尋 | GGUF/Ollama/OpenAI | 無（純 keyword） |

Hermes 的 memory surface 比 Moltis 窄很多——只有 read path（memory_search），沒有 write/delete/forget path。agent 無法在 session 中主動寫入 memory（只能等 cron consolidator）。

---

## Source 3: Moltis Session State

**URL**: https://docs.moltis.org/session-state.html

### Surface

Per-session KV store：`(session_key, namespace, key) → string value`

五個操作：get、set、delete、list、clear。SQLite-backed，namespace 隔離。

### 對 Hermes 的對標

Hermes 沒有 per-session KV store 的對應物。最接近的是 session context（透過 memory pipeline），但那是 read-only 的（agent 不能 set/delete）。

Talos 如果要實作 per-session state：
- 最輕量方案：`/tmp/hermes_session_state.json`（per-session 暫存）
- 持久方案：SQLite table + session_state tool
- 但需要先判斷實際需求——目前 Hermes 的 session memory 倚賴 MEMORY.md + workspace/INDEX.md，是否需要更細粒度的 KV store？

---

## 跨文章 Synthesis

三條線索交會在一點：**DCG 是 Talos governance 從 blueprint 到實作的最短路徑**。

1. DCG 已原生支援 Hermes Agent——不需要自己寫 hook，直接整合
2. DCG 的 agent profiles 直接實現了 Talos governance blueprint 的 per-agent policy differentiation
3. DCG 的 50+ packs 覆蓋了 blueprint 列出的幾乎所有 destructive command categories（且更多——secrets management、DNS、email、messaging 等 packs 是 blueprint 沒列到的）

**Actionable insight**：Talos governance pipeline blueprint 的 policy enforcement layer 不需要從頭設計——可以直接以 DCG integration 為基礎，focus on：
- 哪些 packs 啟用（per-agent）
- allowlist policy（三層）
- audit logging（DCG 的 block/allow decisions → Talos 的 audit trail）

Moltis memory system 的啟發在別的方向：Hermes 的 memory surface 缺 write/delete/forget path，agent 無法主動管理自己的 memory。這是一個值得追的 gap，但優先級低於 DCG integration（DCG 是 security enforcement，memory write 是 convenience）。

---

## ⏳ 未追蹤

- DCG 的 `docs/agents.md` — agent-specific 設定的完整文件（fetch 時被截斷）
- DCG 的 `dcg explain` 模式 — command 分類邏輯的內部實作
- Moltis 的 `checkpoint_restore` 與 memory_save 的整合 — 已從 lifecycle hooks 筆記了解 checkpoint 機制，但與 memory write 的 coupling 未深追
- Moltis 的 `user_profile_write_mode` — 自動 enrich USER.md（browser timezone/location capture）的隱私與安全考量

## ✅ 本次探索完成

