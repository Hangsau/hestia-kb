---
_slug: 40-Resources-_mixed-explorations-2026-05-17-Docker-Credential-Governance---不是-Policy-是-Injection-Proxy
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-Docker-Credential-Governance---不是-Policy-是-Injection-Proxy.md
title: Docker Credential Governance — 不是 Policy，是 Injection Proxy
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- api
- credential
- docker
- governance
- injection
- key
- policy
- proxy
- yaml
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# Docker Credential Governance — 不是 Policy，是 Injection Proxy

**日期**: 2026-05-17 | **來源**: [[2026-05-17-talos-governance-policy-wuphf-pipeline]] 未追蹤 leads
**標籤**: #talos #governance #credential #docker #injection-proxy #enforcement-layer
**延續自**: [[2026-05-17-talos-governance-policy-wuphf-pipeline]]

## 關鍵發現：Credential Governance ≠ Policy Rules

之前的探索預設 Docker 的四控制面（network/filesystem/credential/MCP tools）使用同一種 policy rule 機制。**錯了**。Credential governance 是完全不同的架構模式。

## Per-Source Insights

### 1. Docker Credentials 頁面 — Injection Proxy 架構

**來源**: `docs.docker.com/ai/sandboxes/security/credentials/`

Docker 的 credential handling 不是 Admin Console 的 policy rules，而是一個 **HTTP/HTTPS interception proxy**：

**架構**：
- Host-side proxy 攔截 sandbox 的 outbound HTTP 請求
- 比對 request domain → 從 OS keychain 讀取對應 credential
- 在 proxy 層注入 auth header → 真實 credential 從不進入 sandbox
- Sandbox 內看到的是 sentinel value（`proxy-managed`）

**儲存層**：
1. **Stored secrets**（OS keychain）：`sbx secret set -g <service>`，keyed on service identifier
2. **Custom secrets**（keychain）：`sbx secret set-custom -g --host <domain> --env <var>`，keyed on domain+env var
3. **Host shell env vars**（fallback，不安全）

**Built-in services table**：

| Service | Env Vars | API Domains |
|---------|----------|-------------|
| anthropic | ANTHROPIC_API_KEY | api.anthropic.com |
| aws | AWS_ACCESS_KEY_ID | AWS Bedrock endpoints |
| github | GH_TOKEN, GITHUB_TOKEN | api.github.com, github.com |
| google | GEMINI_API_KEY, GOOGLE_API_KEY | generativelanguage.googleapis.com |
| groq | GROQ_API_KEY | api.groq.com |
| mistral | MISTRAL_API_KEY | api.mistral.ai |
| nebius | NEBIUS_API_KEY | api.studio.nebius.ai |
| openai | OPENAI_API_KEY | api.openai.com |
| xai | XAI_API_KEY | api.x.ai |

**Custom kits**：可在 `spec.yaml` 的 `credentials.sources` 宣告自訂 service identifier，無需註冊步驟。

**SSH agent forwarding**：host SSH agent forwarded into sandbox（`SSH_AUTH_SOCK`），private keys 留在 host。

**Custom secrets**（實驗性）：用於非標準 credential（request body 而非 header、agent 在啟動時 validate env var format）。`sbx secret set-custom` keyed on domain + env var name + optional placeholder。Sandbox 內看到 placeholder，proxy 在 outbound traffic 中替換。

### 2. Organization Governance 頁面（複查）

**來源**: `docs.docker.com/ai/sandboxes/security/governance/`

確認：governance 頁面只覆蓋 **network + filesystem** policy rules。Credential 不在這個 governance 框架內——它有自己獨立的 credentials 頁面和 injection proxy 機制。

## Hermes 啟發

### 對 Talos Governance Pipeline 的修正

之前的 blueprint（`talos-governance-policy-wuphf-pipeline.md`）假設四控制面使用統一 policy schema。Credential 的 injection proxy 模式提示了一個重要的架構區分：

| 控制面 | Docker 機制 | 模式 | Talos 對應 |
|--------|------------|------|-----------|
| Network | Admin Console allow/deny rules | **Policy Rule** | 可用 YAML policy schema |
| Filesystem | Admin Console allow/deny rules | **Policy Rule** | 可用 YAML policy schema |
| Credential | HTTP proxy injection | **Injection Proxy** | 需不同的 enforcement pattern |
| MCP Tools | （待探索） | 未知 | 待探索 |

**Injection Proxy 模式的關鍵特性**：
1. **Real credential never enters agent context** — sentinel value 是防禦邊界
2. **Lookup by service identifier** — 不是 per-resource rule，是 per-service mapping
3. **OS keychain as trust anchor** — credential 存在 OS 層，不是 app 層
4. **Proxy 層攔截** — enforcement 發生在 traffic 層，不是 policy evaluation 層

### 對 Hermes 的啟發

Hermes 沒有 sandbox 隔離（single-user, single-host），但 Injection Proxy 模式的核心理念適用：

1. **Provider credential 不應進入 agent context**：目前 Hermes 的 provider API key 存在 config.yaml 或被讀入環境變數 → agent 可以 `cat` 到。Docker 的 sentinel 模式提示：credential 應該在 tool gateway 層注入，不進入 session。
2. **Service identifier 優於 per-request credential**：與其讓 agent 管理 credential，不如讓 gateway 根據 target domain 自動匹配。
3. **Credential governance 是 mediation，不是 prohibition**：Docker 不做「禁止 agent 用某個 API key」的 policy——它做的是「agent 根本看不到 API key」的 mediation。這改變了 credential governance 的目標：從 allow/deny 轉為 injection/isolation。

### 對 Four-Control-Surface Schema 的修正

原有的 `docker-agent-policy-schema.md` 和 `docker-agent-yaml-schema-policy-enforcement.md` 筆記側重 YAML policy 格式。現在清楚了：這個 YAML schema 只適用於 network + filesystem。Credential（可能還有 MCP tools）需要不同的 enforcement pattern。

**修正後的 Talos enforcement layer 藍圖**：
```
L1: Network Policy    → YAML rules (allow/deny, wildcards, delegation)
L1: Filesystem Policy → YAML rules (allow/deny, path patterns, delegation)  
L1: Credential Policy → Injection mediation (service→key mapping, sentinel)
L1: MCP Tool Policy   → （待探索）
```

## ⏳ 未追蹤

- ~~Docker MCP Tool governance 的實際 Admin Console 格式~~ → 已追：[[2026-05-17-docker-mcp-tool-governance]]。MCP tool governance 是 **approval catalog** 而非 allow/deny rules，Admin Console 具體 UI 格式未公開文件。
- Docker `spec.yaml` 中 `credentials.sources` 的完整 schema（custom kits 如何宣告 credential 需求）
- 是否有方法讓 Hermes 的 provider config 也走 sentinel 模式（DeepSeek API key 不進入 agent context）

## ✅ 本次探索完成

