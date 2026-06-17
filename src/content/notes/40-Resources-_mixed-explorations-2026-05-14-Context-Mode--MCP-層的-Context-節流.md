---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Context-Mode--MCP-層的-Context-節流
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Context-Mode--MCP-層的-Context-節流.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 20:\n    title: Context Mode: MCP 層的 Context 節流\n                  \
  \     ^"
_raw_fm: '

  title: Context Mode: MCP 層的 Context 節流

  date: 2026-05-14

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [claude, code, context, fts, hermes, index, mcp, mode, sandbox, tool]

  created: 2026-05-14

  updated: 2026-06-15

  status: active

  '
title: 'Context Mode: MCP 層的 Context 節流'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Context Mode: MCP 層的 Context 節流

**來源**: [Stop Burning Your Context Window — We Built Context Mode](https://mksg.lu/blog/context-mode) (HN 570pts, 107 comments)
**日期**: 2026-05-14
**作者**: Mert Köseoğlu (MCP Directory & Hub 維護者)

## 一句話

Context Mode 是一個 MCP server，坐在 Claude Code 和 MCP tool outputs 之間。tool 輸出的原始資料進 sandbox 處理，只讓處理後的結果進入 context window。315KB → 5.4KB，98% reduction。

## 核心機制

### 1. Sandbox 執行層

每個 `execute()` call 開獨立 subprocess，process boundary 隔離：
- script 不能存取彼此的 memory/state
- 只有 stdout 進 conversation context
- raw data（log、API response、snapshot）永遠不離開 sandbox
- 支援 10 種 runtime：JS, TS, Python, Shell, Ruby, Go, Rust, PHP, Perl, R
- Bun auto-detect（JS/TS 快 3-5x）

### 2. Knowledge Base（SQLite FTS5 + BM25）

`index` tool 做的事：
- 按 heading 切 markdown，保留 code blocks
- 存進 SQLite FTS5 virtual table
- 搜尋用 BM25 ranking（TF-IDF + document length normalization）
- Porter stemming at index time（"running"/"runs"/"ran" → 同一 stem）
- `search` 回傳 exact code blocks + heading hierarchy，不是 summary

`fetch_and_index`：fetch URL → HTML→markdown → chunk → index。原始頁面不進 context。

### 3. 自動路由（PreToolUse hook）

Context Mode 帶 PreToolUse hook，自動把 tool output 導進 sandbox。Subagent 學會用 `batch_execute` 當 primary tool。Bash subagent 被 upgrade 成 general-purpose 以存取 MCP tools。

## 數字（11 個真實場景）

| Scenario | Before | After |
|---|---|---|
| Playwright snapshot | 56 KB | 299 B |
| GitHub issues (20) | 59 KB | 1.1 KB |
| Access log (500 req) | 45 KB | 155 B |
| Analytics CSV (500 rows) | 85 KB | 222 B |
| Git log (153 commits) | 11.6 KB | 107 B |
| Repo research (subagent) | 986 KB | 62 KB（5 calls vs 37） |

Session-level：315KB raw → 5.4KB。Session time before slowdown: 30min → 3hr。Context remaining after 45min: 99%（原本 60%）。

## 跟 Hermes 的關聯

今天探了幾個相關主題：
- `compaction-context-rot-handbook`：概念層的 context 腐化問題
- `context-gateway-hn`：MCP gateway 做 context 管理
- `agent-cost-curve`：context 成長的 quadratic cost

Context Mode 補上了**實作層**：它不是概念或架構圖，是 shipping code（MIT）。關鍵差異：它做在 MCP 層，不需要改 Claude Code 本身。對 Hermes 的啟發：

1. **Hermes gateway 可以加類似的 output filter layer** — 在 MCP tool 回傳路徑上插入 sandbox/truncation/summarization
2. **FTS5 + BM25 的 KB approach 比純向量搜尋適合 structured content** — markdown heading hierarchy 本身就是好的 chunk boundary
3. **subprocess sandbox 比 prompt-based summarization 可靠** — 不會有 hallucination，因為只回傳 stdout 而非 AI 生成的 summary
4. **PreToolUse hook 的自動路由是關鍵 UX** — 使用者不用改變工作方式

## 可能的 Hermes 應用

- `hermes gateway` 加 context-mode plugin：攔截大型 tool output，sandbox 處理後只回傳精簡結果
- `hermes kb` 用 FTS5 做 local doc index（已經有 Obsidian vault，但可以做 runtime search）
- heartbeat 可以監控 context window utilization 當作健康指標

## 開源

MIT, GitHub: `mksglu/claude-context-mode`
安裝：`claude mcp add context-mode -- npx -y context-mode`

