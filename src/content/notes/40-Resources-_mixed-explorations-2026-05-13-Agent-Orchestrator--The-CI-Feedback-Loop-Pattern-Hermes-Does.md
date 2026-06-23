---
_slug: 40-Resources-_mixed-explorations-2026-05-13-Agent-Orchestrator--The-CI-Feedback-Loop-Pattern-Hermes-Does
_vault_path: 40-Resources/_mixed/explorations/2026-05-13-Agent-Orchestrator--The-CI-Feedback-Loop-Pattern-Hermes-Does.md
title: 'Agent Orchestrator: The CI-Feedback-Loop Pattern Hermes Doesn\"\"t Have Yet'
date: 2026-05-13
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agents
- claude
- code
- hermes
- isolation
- orchestrator
- pattern
- runtime
- worktree
created: '2026-05-13'
updated: '2026-06-15'
status: budding
---

# Agent Orchestrator: The CI-Feedback-Loop Pattern Hermes Doesn't Have Yet

**Date**: 2026-05-13
**Source**: [ComposioHQ/agent-orchestrator](https://github.com/ComposioHQ/agent-orchestrator) (7K ⭐, MIT, TypeScript)
**Theme**: 週三 — Multi-Agent Systems

---

## The Core Insight

The thing that separates Agent Orchestrator from "just another multi-agent framework" is the **closed CI feedback loop**. An agent opens a PR → CI runs → if it fails, the agent automatically reads the failure, fixes it, and re-pushes. If reviewers leave comments, the agent addresses them. The human only gets pulled in for judgment calls.

This isn't "spawn agents in parallel" — that's table stakes. It's "spawn agents that *self-correct against external feedback* without re-prompting."

## Plugin Architecture: Clean Separation of Concerns

Seven slots, each a TypeScript interface:

| Slot      | Default    | What It Means               |
|-----------|-----------|------------------------------|
| Runtime   | tmux      | Where agent processes live   |
| Agent     | claude-code | Which coding agent to use   |
| Workspace | worktree  | Isolation strategy (git worktree per agent) |
| Tracker   | github    | Issue/PR tracking backend    |
| SCM       | github    | Source control (git ops)     |
| Notifier  | desktop   | Where status updates go      |
| Terminal  | iterm2    | Dashboard rendering          |

The key architectural decision: **lifecycle stays in core, behavior goes in plugins**. This is how Hermes skills work too — but Hermes doesn't have an equivalent "runtime slot" abstraction. In Hermes, subagent-driven-development runs agents inside the same Hermes process via `delegate_task`. Agent Orchestrator runs them as separate OS-level processes (tmux panes), giving true isolation.

## What Hermes Can Steal

### 1. The CI Feedback Loop
Hermes's `subagent-driven-development` skill creates subagents that do work and report back. But there's no automated "CI failed → fix it → re-push" loop. The agent completes its task and the human reviews. Adding a post-PR hook that watches CI status and re-engages the agent would close this gap.

### 2. Worktree Isolation
Agent Orchestrator gives each agent its own `git worktree`. Hermes subagents share the same checkout. This works for sequential tasks but creates collision risk for parallel work. For the kanban-worker pattern (where multiple agents might work on different items simultaneously), worktree isolation would be valuable.

### 3. Plugin Slot Pattern for Agent Providers
AO's agent-agnostic design (Claude Code, Codex, Aider, OpenCode, KimiCode all plug into the same slot) is a pattern Hermes could adopt for `delegate_task`. Right now Hermes calls Claude Code via the `claude-code` skill. Supporting multiple backends through a unified interface would make the subagent system more resilient.

## The Numbers That Matter

- **7K stars in 3 months** (created Feb 2026) — rapid adoption
- **3,288 test cases** — serious engineering, not a demo
- **825 open issues** — either growing pains or neglect; worth watching
- **Agent-agnostic, runtime-agnostic, tracker-agnostic** — the "bring your own X" pattern is becoming standard

## Open Questions

1. **Merge conflict resolution**: How does AO handle two agents modifying the same file? The worktree isolation prevents file-level conflicts during development, but merge-time conflicts at PR level are still possible. The README doesn't address this.

2. **Agent cost management**: Running 30 Claude Code agents in parallel is expensive. Does AO have any cost controls or budget limits? Not mentioned.

3. **Hermes integration feasibility**: Could Hermes use AO as a runtime backend? Possibly — AO exposes a web dashboard and CLI. But Hermes would need to speak AO's plugin interface, which is TypeScript. A bridge skill might work.

4. **Self-improving claim**: The demo shows "AI agents building their own orchestrator" — is this a gimmick or does the system genuinely use its own agents to improve its codebase? Worth investigating.

## Worth Tracking

- The `ao` CLI is on npm as `@aoagents/ao`. If Hermes ever needs a dedicated multi-agent runtime that isn't Claude Code-specific, this is a strong candidate.
- Watch for a Go or Rust rewrite — the TypeScript foundation may limit performance at scale (30+ agents).
- The Linear integration is interesting for teams using Linear as their tracker — Hermes's `linear` skill could potentially feed into AO as a task source.

