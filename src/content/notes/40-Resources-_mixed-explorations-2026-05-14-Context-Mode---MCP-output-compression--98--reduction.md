---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Context-Mode---MCP-output-compression--98--reduction
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Context-Mode---MCP-output-compression--98--reduction.md
title: Context Mode — MCP output compression (98% reduction)
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- code
- context
- hermes
- index
- mcp
- mode
- output
- raw
- sandbox
- tool
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Context Mode — MCP output compression (98% reduction)

**來源**: [Stop Burning Your Context Window — We Built Context Mode](https://mksg.lu/blog/context-mode) (HN 570 pts, 107 comments)
**日期**: 2026-05-14
**作者**: Mert Köseoğlu (MCP Directory & Hub 維護者)

## 核心概念

MCP server 作為 middleman 坐在 Claude Code 和 MCP tool outputs 之間。Tool call 的 raw output 不進 context window — 在 sandbox 裡跑完，只回傳計算結果。

## 三個關鍵機制

### 1. Sandbox Execution
- 每個 `execute` call spawn 獨立 subprocess（process boundary 隔離）
- Scripts 之間不能互相存取 memory/state
- 只 capture stdout，raw data（logs, API responses, snapshots）永不進 context
- 支援 10 種語言 runtime：JS, TS, Python, Shell, Ruby, Go, Rust, PHP, Perl, R
- Bun auto-detection for 3-5x faster JS/TS
- Authenticated CLIs（gh, aws, gcloud, kubectl, docker）透過 credential passthrough

### 2. SQLite FTS5 Knowledge Base
- `index` tool：按 heading 切 markdown，保留 code blocks 完整
- 搜尋用 BM25 ranking（term frequency + IDF + doc length normalization）
- Porter stemming at index time（"running"/"runs"/"ran" → same stem）
- `search` 回傳 exact code blocks + heading hierarchy
- `fetch_and_index`：fetch URL → HTML→markdown → chunk → index，raw page 不進 context

### 3. PreToolUse Hook
- 自動 routing：tool outputs → sandbox，transparent to user
- Subagents 自動學會用 `batch_execute` 當 primary tool
- Bash subagents upgrade 到 `general-purpose` 以存取 MCP tools

## 數據

| Scenario | Raw | Compressed |
|---|---|---|
| Playwright snapshot | 56 KB | 299 B |
| GitHub issues (20) | 59 KB | 1.1 KB |
| Access log (500 req) | 45 KB | 155 B |
| Analytics CSV (500 rows) | 85 KB | 222 B |
| Git log (153 commits) | 11.6 KB | 107 B |
| Repo research (subagent) | 986 KB | 62 KB (5 calls vs 37) |
| **Full session** | 315 KB | 5.4 KB |

Session time before slowdown: ~30 min → ~3 hours
Context remaining after 45 min: 99% (vs 60% without)

## 對 Hermes 的啟發

- Hermes 也面臨一樣的 context window 壓力（tool definitions + tool outputs 雙向吃 token）
- 現有 heartbeat 的 provider_health 已經監控 cost，但沒有做 output 端的 compression
- Context Mode 的 sandbox 模式對應 Hermes 的 terminal tool — 差別在 Hermes 的 terminal 輸出目前是全量進 context
- SQLite FTS5 + BM25 的 KB 模式可以用在 Hermes 的 vault/obsidian search 優化
- PreToolUse hook 的概念可以對標 Hermes 的 skill system — skill 本身就可以當 output filter

## 連結

- GitHub: https://github.com/mksglu/claude-context-mode (MIT)
- 作者: x.com/mksglu, linkedin.com/in/mksglu
- 相關: Cloudflare Code Mode（tool definition 端壓縮 99.9%）

