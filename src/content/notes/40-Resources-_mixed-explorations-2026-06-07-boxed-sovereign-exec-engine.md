---
_slug: 40-Resources-_mixed-explorations-2026-06-07-boxed-sovereign-exec-engine
_vault_path: 40-Resources/_mixed/explorations/2026-06-07-boxed-sovereign-exec-engine.md
tags:
- explorations
- auto-ingested
source: autonomous_notes
created: '2026-06-07'
title: Boxed — Sovereign Exec Engine for AI Agents
updated: '2026-06-15'
type: exploration
status: budding
---

# Boxed — Sovereign Exec Engine for AI Agents

**Date**: 2026-06-07 | **Source**: HN Show HN (`akshayaggarwal99/boxed`) | **Type**: Exploration

## Per-Source Insight

### Boxed (GitHub,4pts HN)

**What it is**: Open-source sovereign code execution engine for AI agents. BYOK model — operator runs their own control plane, no vendor accounts.

**Architecture**:
- **Control Plane (Go)**: REST API + WebSocket gateway, ~2.8k LOC, 12 MiB binary
- **Agent (Rust)**: 1.32 MiB stripped binary injected into every sandbox; streams stdout/stderr/artifacts over JSON-RPC
- **Driver interface**: Docker driver ships today; Firecracker + Wasm drivers stubbed behind a single `Driver` interface

**Key numbers** (MacBook Pro M1 Pro, 16 GB, macOS, Docker Desktop, n=200):
| Metric | Value |
|--------|-------|
| Median create+exec+destroy | **303 ms** |
| p95 / p99 | 395 ms / 495 ms |
| Peak throughput | 9.8 sandboxes/s |
| Idle agent RSS (median) | 0.4 MiB |
| Behavioural escape probe | 5/12 denied |

**Honest security scoping** (from README):
> current Docker driver enforces a `Memory` cgroup (default 512 MiB) and runs `/tmp` and `/output` as `tmpfs`, but leaves the container rootfs writable, retains the default Linux capability set (no `CapDrop: ALL`), does not set `PidsLimit`, and permits in-PID-namespace `ptrace`. We report the full escape probe in the paper and close those gaps in the planned Firecracker driver.

→5/12 escape probes denied, 7/12 still possible in current Docker driver. Firecracker driver planned to close these.

**SDKs**: TypeScript + Python first-class, Go SDK planned

**Network policy**: Coarse `EnableNetworking` toggle today (Docker `none` vs bridge); fine-grained allow-lists on roadmap

---

## Hermes/Talos 啟發

### 1. BYOK Model 直接對標 Talos Governance

Boxed 的「Bring-Your-Own-Key」模式——operator 自己部署 control plane，自己定義 API key——正是 Talos governance pipeline 的 credntial governance方向。

`guardian-sandboxing-gradient` 提案（WS-029）探索的三層隔離：
- L1: tool scoping（簡單）
- L2: gateway mediation（中等）
- L3: container/VM isolation（嚴格）

Boxed 處於 L2-L3 之間：Docker隔離（有一定缺口）→ Firecracker（更強隔離， roadmap）。

**具體差距**：Boxed 的 Docker driver 缺口：
- No `CapDrop: ALL` → container retains Linux capabilities
- No `PidsLimit` → fork bomb possible
- Permits in-PID-namespace `ptrace` → escape probe vector

這些缺口等價於「WS-029 的 L2 sandbox 方案若只用 Docker 而不加固，會有 7/12 逃逸風險」。如果要實作 L3，Boxed 的 Firecracker driver roadmap 是直接參考。

### 2. Rust Agent Binary 的隔離模式

Boxed injects a lightweight Rust binary into every sandbox. This is similar to what `muscle-mem-behavior-cache` (764⭐) does with deterministic replay — but Boxed's approach is for code *execution* rather than *caching*.

For Talos governance: a lightweight Talos agent binary injected into sandbox could serve as:
- Policy enforcement sidecar (like Boxed's Rust agent)
- Tool call interception layer
- Audit log emitter

### 3. JSON-RPC over WebSocket for Artifact Streaming

Boxed's Rust agent streams stdout/stderr/artifacts over JSON-RPC via WebSocket. This is a concrete implementation of the "structured output + streaming" pattern that `agent-tool-design-patterns` (Sketch.dev447pts) discusses.

Hermes tool outputs currently go directly to LLM context. A Boxed-like artifact streaming model could separate:
- **Immediate outputs** (stdout/stderr) → LLM context
- **Artifacts** (files, images, datasets) → Object store, only metadata in context

###4. Honest Security Self-Assessment

Boxed's README explicitly discloses7/12 escape probe gaps. This is a model for how Talos should report governance gaps — transparent about what's not yet secure, clear about roadmap to close gaps.

---

## 未追蹤 Leads

- https://github.com/akshayaggarwal99/boxed — main repo (star count unknown, likely small-to-medium)
- https://github.com/akshayaggarwal99/boxed/tree/main/paper/main.pdf — full paper with escape probe details
- https://github.com/akshayaggarwal99/boxed/tree/main/bench — reproducible benchmark harness
- Firecracker driver (roadmap, not yet shipped) — would close Docker security gaps

## ✅ 本次探索完成
---
tags: [explorations, auto-ingested]
source: autonomous_notes
created: 2026-06-07
---
