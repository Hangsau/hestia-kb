---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Mistle-Sandboxing---WUPHF-Inter-Agent-Architecture---守護者視角
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Mistle-Sandboxing---WUPHF-Inter-Agent-Architecture---守護者視角.md
title: Mistle Sandboxing & WUPHF Inter-Agent Architecture — 守護者視角
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- credentialless
- docker
- gateway
- hermes
- mistle
- runtime
- sandbox
- tool
- wuphf
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Mistle Sandboxing & WUPHF Inter-Agent Architecture — 守護者視角

**日期**: 2026-05-17 | **來源**: 未追蹤 leads from [[2026-05-16-sandbox-profiles-compliance-adversarial-drift]]
**標籤**: #sandboxing #multi-agent #process-isolation #ws-009 #credentialless #tool-scoping
**延續自**: [[2026-05-16-sandbox-profiles-compliance-adversarial-drift]]

## Per-Source Insights

### 1. Mistle — Credentialless Sandbox 架構

- **來源**: `github.com/mistlehq/mistle` — `docs/architecture.md` + sandbox profile type definitions
- **核心設計 — Credentialless sandboxes**：sandbox 內永遠看不到 credential。所有對外 HTTP 請求透過 data-plane gateway 中介，gateway 載入 runtime plan → 比對 egress route → 從 control plane 查 credential → 注入請求後轉發。Agent 看不到 secret，即使在 sandbox 內部也無法洩漏。
- **架構**：三層 — Control Plane (dashboard + API + worker) → Data Plane (API + worker + gateway) → Sandbox (Docker container)。Gateway 是 credential injection 的強制點。
- **Sandbox Profile**：定義 agent session 的 tools、permissions、environment。Profile 有 versioning（draft → publish flow），可預先 snapshot 環境讓 session 快速啟動。
- **Runtime Plan**：profile 被 compile 成 runtime plan，gateway 用於 egress routing 和 credential injection。
- **與 Hermes 的關係**：Mistle 的 credentialless gateway pattern 可以直接借鏡於 Hermes 自主探索模式的安全強化。不需要 full Docker sandbox——在 tool gateway 層做 mediation 即可。具體來說：探索 agent 不直接有 `terminal` / `write_file` / `process` tool，而是透過一個 mediator tool 間接執行，mediator 做 policy check（如同 Mistle gateway 做 egress route 比對）。

### 2. WUPHF — Push-Driven Multi-Agent Office

- **來源**: `github.com/nex-crm/wuphf` — README + ARCHITECTURE.md
- **三個架構決策**：
  1. **Fresh session per turn**：每個 agent turn 都是 `claude -p` scratch start，無累積 context。配合 Anthropic prompt cache → 97% cache hit rate。Token 成本 flat ~87k/turn（vs accumulated sessions 484k/turn，7x 差異）。
  2. **Per-agent scoped MCP**：DM mode 只 load 4 tools（vs office mode 27）。更少的 tool schema → 更小的 prompt → 更好的 cache alignment。
  3. **Push-driven broker**：agent 只在 broker push 訊息時醒來，零 idle cost。這和 heartbeat v2 的 autonomic 層（只在 cron tick 喚醒 cognitive 層）概念一致。
- **Inter-agent 互動**：agent 透過 @mention 互相 challenge assumption、宣告依賴、浮現 blocker——「bully each other to prevent context drift」的實際機制是結構化的 assumption challenge，不是人身攻擊。
- **隔離設計**：per-agent isolated git worktree（和 Hermes 的 worktree-subagent-isolation skill 完全一致）。Per-agent notebook → promotion → shared wiki 的 pattern 對應 WS-004 consolidation-step。
- **已支援 Hermes Agent**：`--provider hermes-agent` 可以直接用 Hermes gateway 跑 WUPHF agent。這意味著 Hermes 可以作為 WUPHF 的 runtime。
- **與 Hermes 的關係**：
  - Tool scoping pattern 直接對應 WS-009：探索模式限制 tool set，類似 WUPHF DM mode 只給 4 tools。
  - Fresh session 策略與 Hermes 的 memory-heavy 路線相反——兩種設計哲學的取捨。WUPHF 證明 fresh sessions + prompt cache 可以很便宜，但代價是沒有跨 session 記憶（除非透過 wiki promotion）。
  - Push-driven 喚醒機制驗證了 heartbeat v2 的 autonomic→cognitive 雙層設計是正確方向。

## Cross-Source Synthesis — 守護者三層防禦模型

從 Mistle 和 WUPHF 可以提煉出一個 **sandboxing 的輕重梯度**，對於 Hermes 自主探索的安全強化有直接參考價值：

| 層級 | 方案 | 代表 | 成本 | 隔離強度 | Hermes 適用 |
|------|------|------|------|---------|------------|
| L1: Tool scoping | 限制 agent 可用 tool set | WUPHF DM mode (4 tools) | 極低 | 弱 | ✅ 立即可用 |
| L2: Gateway mediation | Tool 呼叫透過 mediator 做 policy check | Mistle credentialless gateway | 中 | 中 | ✅ 架構上可行 |
| L3: Container isolation | Docker/microVM sandbox | Mistle Docker sandbox | 高 | 強 | ⚠️ 過重 |

**建議採用路徑**：L1 先上（探索模式限制 tool set），L2 作為 WS-009 的 medium-term target（tool gateway mediation），L3 保留為 future option。

Mistle 的 credentialless pattern 給了一個重要啟發：**不要讓 agent 看到 secret，讓 gateway 在最後一刻注入**。套用到 Hermes：探索 agent 不該有直接寫入 vault 的權限——應該透過 mediator，mediator 先 scan content 再寫入。這和 `sanitize_fetch.py` + `validate_note.py` 的 defense-in-depth 哲學一致。

## Hermes 啟發

1. **Tool scoping for exploration**（WS-009 immediate）：自主探索模式限制 tool set 為 `{web_search, web_extract, read_file, search_files}`——不給 `terminal`、`write_file`、`patch`、`process`。這和 WUPHF DM mode 的邏輯相同：更少的 tool = 更小的攻擊面。

2. **Tool gateway mediation**（WS-009 medium-term）：參考 Mistle 的 gateway 層——探索 agent 的 write_file 呼叫不直接執行，而是透過 mediator scan 後才寫入。架構上可行（Hermes 已有 tool 層），成本可控。

3. **Credentialless exploration**：Mistle 的核心教訓——sandbox 內永遠不該有 credential。Hermes 探索 agent 的 system prompt 不應包含 API key、路徑、或其他敏感資訊（目前已大致符合，但可以 formal check）。

4. **WUPHF 的 agent-to-agent challenge** 對 Talos 的角色有意義：Talos 可以扮演 WUPHF 中「challenge assumption」的角色——定期 review Hestia 的 code/config/skill，提出具體質疑。這已經是 Talos personality 的一部分（「姊，你確定？」），但可以更系統化。

## 未追蹤

- Mistle 的 runtime plan schema 完整定義（`compile-profile-version-runtime-plan` handler）— 了解 gateway 如何 matching egress routes
- WUPHF `DESIGN-WIKI.md` — 了解 markdown-based wiki 的 promotion flow 和 lint 機制（對 WS-004 consolidation step 有參考價值）
- WUPHF `docs/specs/WIKI-SCHEMA.md` — wiki schema 的 operational contract
- Docker AI Sandboxes（`docker/sbx`）— Docker 官方的 agent sandboxing 方案，和 Mistle 是競爭/互補關係
- agent-infra/sandbox — all-in-one sandbox（Browser + Shell + File + MCP + VSCode in single Docker），更輕量的 alternative

## ✅ 本次探索完成

