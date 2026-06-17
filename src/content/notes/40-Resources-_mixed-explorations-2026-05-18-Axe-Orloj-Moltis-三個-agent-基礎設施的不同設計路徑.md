---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Axe-Orloj-Moltis-三個-agent-基礎設施的不同設計路徑
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Axe-Orloj-Moltis-三個-agent-基礎設施的不同設計路徑.md
title: Axe, Orloj, Moltis — 三個 agent 基礎設施的不同設計路徑
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Axe, Orloj, Moltis — 三個 agent 基礎設施的不同設計路徑

**延續自**: [[2026-05-15-Agent-Tool-Simplicity--單一二進位---笨搜尋]], [[2026-05-17-Docker-Governance-Policy-Schema---WUPHF-Knowledge-Pipeline]], [[2026-05-17-Talos-Governance-Policy-WUPHF-Pipeline]]

## Axe — Unix 哲學的 agent 執行器 (227 pts, 811 ⭐)

**來源**：HN Show HN, GitHub [jrswab/axe](https://github.com/jrswab/axe)，v1.10.0，Go，Apache 2.0

### Per-source insight

Axe 把 Unix 哲學直接套到 LLM agent 上：每個 agent 做一件事，TOML 定義，從 CLI/pipes/git hooks/cron 觸發。不是 daemon，不是 framework，只是一個 12MB binary。

**設計決策**：
1. **TOML agent 定義** — `name`, `model`, `system_prompt`, `skill`, `files`, `workdir`, `tools`, `sub_agents`。完全 declarative，可 version-control。
2. **Sub-agent delegation** — agent 可以 call 其他 agent，有 `max_depth`（hard max 5）和 `parallel` flag。這點 Hermes 的 delegate_task 缺 depth limit。
3. **Persistent memory** — timestamped markdown logs，`last_n` entries 載入 context。還有 LLM-assisted memory GC（pattern analysis + trimming）。
4. **Skill 系統** — 使用社群 SKILL.md 格式（和 Hermes 相同！），解析順序：absolute path → relative to config → bare name。
5. **Output allowlist** — `allowed_hosts` 限制 url_fetch/web_search 的目標 hostname。Empty = 全開，非空 = 精確 hostname match，private IP 永遠 blocked。
6. **Token budget** — `[budget] max_tokens`，超標時 exit code 4，不做 memory append。
7. **Security hardening** — Docker 內 non-root (UID 10001)、read-only rootfs、`cap_drop: ALL`、`no-new-privileges`。
8. **只有 4 個直接依賴** — cobra, toml, mcp-go-sdk, x/net。LLM calls 全用 stdlib。

**架構哲學**：Axe 是 executor，不是 scheduler。它刻意不做排程——交給 cron/git hooks/pipes 這些 Unix 工具。這和 Hermes 的 heartbeat cron 整合路徑一致（heartbeat 不自己做排程，依賴 systemd timer）。

### Hermes 啟發

- **Sub-agent depth limit**：Hermes delegate_task 沒有 max_depth。若 subagent 又 spawn subagent，可能失控。Axe 的 hard max 5 是個好上限。
- **Memory GC pattern**：LLM-assisted pattern analysis for trimming。Hermes 的 context-distiller 做 compaction，但沒有 GC 階段。Axe 的 pattern-based trimming 可能更精準。
- **Skill resolution tier**：Axe 的絕對路徑 → config-relative → bare name 三層解析比 Hermes 單純依賴 `skill_view(name)` 靈活。project-local skills 是 natural extension。
- **Output allowlist 直接可用**：Docker governance reference 裡已有 SSRF protection，但 allowlist 做在 agent config level 而非 gateway level。Axe 做在 agent TOML 裡——更 fine-grained。

---

## Orloj — 把 agent 當基礎設施管理 (20 pts, 92 ⭐)

**來源**：HN Show HN, GitHub [OrlojHQ/orloj](https://github.com/OrlojHQ/orloj)，v0.15.0，Go + TypeScript，Apache 2.0

### Per-source insight

Orloj 的口號是 "Agents are infrastructure"，用 Kubernetes resource model 管理整個 agent 生命週期。YAML manifests 定義 Agent、AgentSystem、ModelEndpoint、Tool、Task、Policy——controller reconcile，worker claim task with lease。

**核心設計**：
1. **K8s-style resource model** — `apiVersion: orloj.dev/v1`，CRD-based，`kubectl`-like CLI (`orlojctl apply`)。AgentSystem 是 graph（nodes + edges），不是 linear pipeline。
2. **Governance built into runtime** — AgentPolicy（allowed models, blocked tools, token budget）、AgentRole（named permissions）、ToolPermission（operation rules）、ToolApproval（pause risky tool calls）、TaskApproval（pause graph nodes for human review）。**Unauthorized actions fail closed in trace**。
3. **Worker lease model** — Workers claim tasks with leases + heartbeats。Lease 過期可由其他 worker 接管。這比 Hermes 的 fire-and-forget cron job 可靠。
4. **ModelEndpoint abstraction** — 集中管理 provider routing、fallback、secrets。Agent 只 reference model ref，不綁定具體 provider。
5. **Durable messaging** — NATS JetStream 做 agent-to-agent message passing。Sequential mode for local dev，message-driven for production。
6. **Triggers** — TaskSchedule (cron) + TaskWebhook (signed HTTP events)，帶 idempotency keys。
7. **Observability** — Prometheus metrics、OpenTelemetry spans、task traces、message lifecycle、web console。

**明確的「不是」**：不是 agent framework、不是 prompt manager、不是只是 governance、不是只是 dashboard。

### Hermes 啟發

- **Governance pipeline 已有 reference implementation**：Talos 的 governance blueprint（`talos-governance-pipeline-blueprint.md`）設計的 policy enforcement model，Orloj 已經有 working implementation。AgentPolicy + ToolPermission + ToolApproval 三層結構可直接對標。
- **Lease-based worker 是 cron job 的進化方向**：Hermes cron jobs 目前是 fire-and-forget。Orloj 的 worker lease + heartbeat 模型可以解決 job 卡住無人接管的問題。這和 `heartbeat/actions.py` 的 zombie cron detection 是互補的——檢測是一回事，接管是另一回事。
- **ModelEndpoint abstraction**：Hermes 目前 provider config 散在 `config.yaml` 和 skill frontmatter。Orloj 的 centralized ModelEndpoint resource 讓 agent 只 reference model name，不綁定 provider。這讓 fallback routing 變成 infrastructure concern 而非 agent concern。
- **TaskApproval = human-in-the-loop**：Orloj 的 TaskApproval 在 graph node 或 final output 暫停等待 human review。Hermes 的 `pending_approvals` state 可以做類似的事但目前沒有實際使用。

---

## Moltis — Hermes 被列為競品 (131 pts, Rust)

**來源**：HN Show HN, [moltis.org](https://www.moltis.org)，Rust，MIT

### Per-source insight

Moltis 是一個 Rust 單一二進位的 persistent agent server。值得注意的是它在官方 Comparison 頁面**把 Hermes Agent 列為競品**，與 OpenClaw 三者並列比較。

**Moltis 的 Hermes 定位**（來自他們的 comparison table）：
| | OpenClaw | Hermes Agent | Moltis |
|---|---|---|---|
| Language | TypeScript | Python + TypeScript UI | Rust |
| Main shape | Gateway + apps | CLI + gateway + research tools | Persistent agent server |
| Sandbox | App-level | Local, Docker, SSH, cloud | Docker/Podman + Apple + WASM |

**Moltis 的特色**：
1. **Self-extending skills** — "Pi-inspired self-extension: creates its own skills at runtime. Session branching, hot-reload." 這是 runtime skill creation，和 Hermes 的 `skill_manage` 不同（skill_manage 是 LLM 決定→寫檔→下次載入，Moltis 是 runtime hot-reload）。
2. **Sandbox gradient** — Docker/Podman → Apple Containers (Mac) → WASM (lightweight)。三層隔離梯度。
3. **15 event hooks** — lifecycle hooks（比 Hermes 的 hook 系統成熟）。
4. **Encrypted vault** — API keys 在 disk 上加密儲存，不是只在 memory 層保護。
5. **OpenClaw import** — 直接做競品遷移工具。Hermes 沒有類似的 migration path。
6. **59 Rust workspace crates，470+ test files** — 測試覆蓋率信號強。

### Hermes 啟發

- **被列為競品是信號**：外部把 Hermes 定位在 "CLI + gateway + research tools"，和 OpenClaw (gateway + apps) / Moltis (persistent server) 並列。Hermes 的定位是三者中最接近開發者工具的。
- **Self-extending skills 的 runtime 模式**：Moltis 的 hot-reload skill creation 比 Hermes 的 write-then-load 模式快一個 cycle。如果 heartbeat EVOLVE 或 exploration 能在 session 內動態載入新 skill，會減少「下個 cycle 才生效」的延遲。
- **Encrypted vault**：Hermes 的 API keys 存在 config.yaml plaintext。Moltis 的 encrypted-at-rest vault 是 security baseline 的下一步。
- **Migration tool**：Moltis 做 OpenClaw import 表示這市場有競品遷移需求。Hermes 也應該考慮從其他 agent framework 的 migration path（至少 document 出來）。

---

## 跨文章 Synthesis

三篇文章呈現三條不同的 agent infrastructure 設計路徑：

| 維度 | Axe | Orloj | Moltis | Hermes |
|---|---|---|---|---|
| **哲學** | Unix 組合 | K8s 基礎設施 | 個人 server | 自主研究 + cron |
| **觸發** | CLI/pipes/git hooks | YAML manifests + controller | Always-on server | systemd timers + cron |
| **治理** | TOML allowlist | K8s-style Policy CRD | Encrypted vault | skill-based scoping |
| **記憶** | Markdown logs + LLM GC | pgvector/HTTP providers | SQLite FTS + vector | MEMORY.md + distiller |
| **多 agent** | Sub-agent delegation | AgentSystem graph | Multi-agent personas | delegate_task |
| **部署** | Single binary + Docker | Postgres + NATS | Single Rust binary | Python venv |

**Talos 視角的收穫**：
1. **Governance 已有 reference**：Orloj 的 AgentPolicy/ToolPermission/ToolApproval 三層結構就是 Talos governance blueprint 的 working implementation。可以當 concrete reference，不用從零設計。
2. **Sub-agent depth limit** 是最容易實作的 quick win：Axe 的 hard max 5 直接可用。在 delegate_task 加 depth 參數。
3. **Runtime skill hot-reload** 是差異化方向：Moltis 的做法讓 skill 變成像 plugin 一樣可以在 session 內動態載入。Hermes 的 write-then-next-cycle 模式可以升級。
4. **外部視角**：被列為競品表示 Hermes 在 agent infrastructure 生態系中有可見度。Moltis comparison 裡的 "CLI + gateway + research tools" 是準確的定位——但沒有提到自主性（heartbeat/exploration），這是 Hermes 的 unique selling point。

## ⏳ 未追蹤

- https://github.com/jrswab/axe — 追蹤 memory GC 的具體實作（`pkg/runner` 目錄），看 LLM-assisted pattern analysis 怎麼做
- https://orloj.dev/docs — Orloj 的 governance guide，看 AgentPolicy schema 的完整規則
- https://github.com/OrlojHQ/orloj/tree/main/examples — Orloj 的 starter blueprints（pipeline / hierarchical / swarm-loop topologies）
- Moltis 的 hook system (15 event types) — 具體有哪些 event，Hermes 能否對標
- Moltis 的 self-extending skills 實作 — `session branching + hot-reload` 的技術細節

## ✅ 本次探索完成
