---
_slug: 40-Resources-_mixed-explorations-2026-05-25-llm-agent-context-patterns
_vault_path: 40-Resources/_mixed/explorations/2026-05-25-llm-agent-context-patterns.md
title: Exploration — 2026-05-25
created: '2026-05-25'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Exploration — 2026-05-25

## Per-source Insights

### 1. Tilth — Smart code reading (GitHub: jahala/tilth)

**What it is**: Rust CLI (~20k LOC) + MCP server for structural code reading. Uses tree-sitter for AST-based symbol search, ripgrep for content search, `memmap2` for fast file reads, DashMap for outline caching.

**Key architecture decisions**:
- Tree-sitter for definition detection (not text search) — finds where symbols are *defined*, not where strings appear
- Callee footer (`── calls ──`) shows resolved callees with file+line+signature in one pass
- Token-based size detection: <~6000 tokens = full content, >6000 = structural outline
- `tilth_diff` — function-level change detection, replaces `git diff` for AI agents
- `--map` CLI-only (codebase skeleton) — disabled in MCP mode because AI agents overused it and accuracy dropped

**Benchmarks** (160 runs across Express, FastAPI, Gin, ripgrep repos):
| Model | Baseline acc | tilth acc | Cost reduction |
|-------|-------------|-----------|---------------|
| Sonnet 4.6 | 84% | 94% | -44% |
| Opus 4.6 | 91% | 92% | -39% |
| Haiku 4.5 | 54% | 73% | -38% |

**MCP mode features**:
- `tilth_search` with `kind: "callers"` — structural call site finding (tree-sitter in reverse, `memchr` SIMD pre-filter)
- Session dedup: `[shown earlier]` on subsequent definition searches — saves tokens when revisiting symbols
- `expand` defaults to 2 in MCP mode, no flag needed

**Install**: `cargo install tilth` or `npx tilth`. MCP server: `tilth install claude-code` etc. Supports 19 AI tool integrations (Claude Code, Cursor, Windsurf, VSCode, Gemini, Codex, etc.).

**Hermes relevance**: Code reading efficiency. The token-based outline-then-section pattern (outline for large files, section for exact range) could inform Hermes's own code reading strategy. The 40% cost reduction benchmark validates the "structure before content" approach.

---

### 2. context-llemur — Portable git-based context management (GitHub: jerpint/context-llemur)

**What it is**: CLI tool + MCP server that tracks project context as a git repository. No embeddings. Context travels between all LLMs.

**Core philosophy**:
- "Context windows are getting longer, agents are getting more capable of finding information when properly structured" — explicit rejection of embedding-based retrieval
- Context is version-controlled git repos — branches for exploration, merge for integration
- Self-documenting: each `ctx` folder includes `ctx.txt` explaining how to use it; MCP server also self-documents so LLM immediately knows available tools

**Key commands**:
- `ctx explore <topic>` — creates new git branch for exploration
- `ctx integrate <exploration>` — merges branch back to main
- `ctx load` — displays all file contents with clear delimiters (for pasting into LLM context)
- `ctx mcp` — starts MCP server for AI agent integration

**MCP server tools**: Repository management, semantic workflows (explore/save/integrate), file operations, navigation. All tools are self-documenting.

**No embeddings** — relies on LLMs and humans to manage context structure. Explicitly: "I noticed that 1) context windows are getting longer 2) most agents are using their own retrieval magic sauce that seems to work pretty well already."

**Hermes relevance**: Memory architecture. The branch-based exploration workflow (`ctx explore "topic" → work → ctx integrate`) is a natural pattern for session-based research. The "no embeddings" design aligns with Mem0's ADD-only philosophy and ctx's explicit rejection of vector search for context management.

---

## Cross-article Synthesis

### Structural code reading vs. embedding-based retrieval

Both Tilth and context-llemur represent a counter-movement: **structured approach over embedding-based approach**.

Tilth: tree-sitter AST + token预算 → structural outline → exact section retrieval. No embeddings. The problem with embeddings is latency and maintenance overhead — tilth shows you can get 40% cost reduction with the right structure.

context-llemur: git repo + plain text files → MCP server. The MCP server is self-documenting (LLM immediately knows available tools). Branch-based exploration workflow. Explicit rejection of embeddings because "context windows are getting longer."

**Synthesis for Hermes**: The "structure before content" principle appears in both:
1. Tilth's outline-then-section for code reading
2. ctx's structured git repo + self-documenting MCP for context management

This suggests Hermes's memory architecture should lean toward **structured metadata + plain text** over vector embeddings. The Mem0 `ADD-only` design and `scope-tagged writes` already point this direction. Tilth's token budget approach and ctx's branch-based exploration provide concrete implementation patterns.

---

## Untracked Leads

- `https://github.com/f/mcptools` — MCP Tools CLI Inspector. Raw README 404. Would need HTML fetch. Topic relevant but lead is cold.
- `https://github.com/jahala/tilth` — MCP server install base (19 integrations). Could be studied for Hermes MCP gateway integration patterns.
- `https://github.com/jerpint/context-llemur` — the `ctx.txt` template file for LLM self-onboarding. Could inform Hermes's session initialization prompts.

## ✅ 本次探索完成

**探索時間**: 2026-05-25
**主要收穫**: Tilth 的 token budget outline pattern 和 ctx 的 branch-based context exploration 是互補的兩個方向——前者改善 code reading 效率，後者改善跨 session 記憶整合。兩者都拒絕 embedding-based retrieval，呼應 Mem0 的 ADD-only 設計。