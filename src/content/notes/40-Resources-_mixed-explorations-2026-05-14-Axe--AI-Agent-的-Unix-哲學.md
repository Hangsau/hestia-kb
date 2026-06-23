---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Axe--AI-Agent-的-Unix-哲學
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Axe--AI-Agent-的-Unix-哲學.md
title: 'Axe: AI Agent 的 Unix 哲學'
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- axe
- hermes
- memory
- pipe
- prompt
- run
- skill
- toml
- unix
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Axe: AI Agent 的 Unix 哲學

**日期**: 2026-05-14 | **來源**: HN (227 points, 128 comments), GitHub README | **類型**: exploration

## TL;DR

Axe 是一個 12MB Go binary，把 AI agent 當 Unix 程式對待：每個 agent 一個 TOML 檔、做一件事、透過 pipe 組合。806 stars，Apache-2.0。

```
git diff --staged | axe run pr-reviewer
cat error.log | axe run log-analyzer
```

## 核心設計

### Agent = TOML + Skill
- 每個 agent 用一個 TOML 定義：system prompt、model、skill files、context files、working directory
- Skill 是可重複使用的 instruction set，跨 agent 共享
- 支援 sub-agent delegation，有 depth limiting + parallel execution

### Unix 哲學的四個面向
1. **Small & focused** — 不當聊天機器人，不做 long-running session
2. **Composable** — stdin/stdout pipe，和 cron/git hooks/CI 組合
3. **No daemon** — 沒有背景 process、沒有 GUI
4. **Declarative** — TOML 可進 version control

### 功能亮點
- **多 provider**: Anthropic, OpenAI, Ollama, OpenCode, AWS Bedrock
- **Persistent memory**: timestamped markdown logs，跨 run 延續 context；有 LLM-assisted GC
- **Sub-agent delegation**: agent 可以 call 其他 agent（透過 LLM tool use）
- **MCP 支援**: SSE / streamable-HTTP transport
- **Output allowlist**: 限制 url_fetch / web_search 的 hostname；private/reserved IP 永遠 blocked（SSRF 防護）
- **Token budgets**: 可設 `[budget]` 或 `--max-tokens`
- **Docker**: non-root user, read-only rootfs, all caps dropped
- **Retry**: exponential/linear/fixed backoff

## HN 討論精華

### 正面迴響
- **Unix 框架引起共鳴**：「終於有人用 Unix 的方式做 AI」（swaminarayan）
- **成本控制**：single-purpose agent 只拿需要的 context，prompt 小、行為可預測（Orchestrion）
- **crabtalk.ai 比較**：daemon + commands 模式，8MB binary，hot-swap 和 process isolation（clearloop）
- **實戰場景**：RPG character creation workflow，pipe 串接多個 agent，中間檔案可手動編輯（Multicomp）

### 質疑與批評
- **12MB 算大**：「Zig 寫的 full HTTP stack + TLS 只要 400KB」（mccoyb）——但 Go 的 runtime 就佔了不少
- **Persistent memory 是 scope creep**：「任何提 persistent memory 的專案都應該用三句話解釋 scratch/notes files 怎麼 pipe」（athrowaway3z）
- **Fine-grained agents 不自然**：「如果 agent 是人，把這麼細的工作分給不同人然後叫他們協作，根本瘋了」（hamandcheese）
- **Cost fan-out**：「unintentionally fan out 10 agents 比一個大 context window 更貴」（bensyverson）
- **Shell escape**：path sandbox 擋不了 agent 直接跑 `cat` 或 shell command（uhx）
- **Config location**：希望 agent config 在 repo 裡而不是 `~/.config`（ColonelPhantom）——Axe 其實有 `--agents-dir` flag 和 auto-discover `<cwd>/axe/agents/`

### 其他觀察
- **MCP 疲勞**：有人在多個專案中觀察到「movement away from MCP」，覺得 Unix composability 更自然（btbuildem）
- **商標問題**：Deque 已有 Axe accessibility testing tool（bsoles）

## 相似工具對比

| 工具 | Stars | 語言 | 定位 |
|------|-------|------|------|
| **Axe** | 806 | Go | CLI agent runner，Unix pipe |
| **ell** | 5,871 | Python | LLM programming library |
| **runprompt** | 439 | Python | Shell prompt runner |
| **crabtalk.ai** | ? | ? | Daemon + commands，8MB |

ell 的 stars 遠高於 Axe，但 ell 是 library/framework，Axe 是 standalone binary——不同生態位。

## 對 Hermes 的啟發

1. **Agent-as-TOML 的思路**：Hermes 的 skill 系統已經有類似的模組化設計，但 agent 定義是隱式的（透過 system prompt + skills）。可以考慮把 agent persona 也做成宣告式 config。
2. **Pipe-first design**：Hermes 目前是 session-based，但 cron job 已經有 pipe 的影子（stdin = task description）。如果 Hermes 支援 `echo "review this PR" | hermes run reviewer`，會解鎖很多 CI 整合場景。
3. **Memory GC**：Axe 的 LLM-assisted memory GC（pattern analysis + trimming）是我們還沒有的功能。Heartbeat 的 warmup 機制可以做類似的事。
4. **Output allowlist**：SSRF 防護的 allowlist 設計乾淨，比 Hermes 目前的 tool sandbox 更 declarative。
5. **Sub-agent depth limiting**：Axe 的 depth limit + parallel execution 是我們 delegate_task 可以參考的模式。

## 值得追蹤

- Axe 的 skill system 如何演進（目前還很簡單）
- 是否會有 community agent registry（類似 nixpkgs）
- 12MB → 更小的可行性（Go 1.25+ vs Zig rewrite）
- MCP 整合的深度（目前 only SSE/streamable-HTTP）

