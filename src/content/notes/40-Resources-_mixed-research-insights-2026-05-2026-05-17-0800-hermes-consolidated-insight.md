---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0800-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0800-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: medium
title: Credential Injection + Deferred Tool Loading = Hermes Enforcement Architecture
updated: '2026-06-15'
type: research
status: budding
---

# Credential Injection + Deferred Tool Loading = Hermes Enforcement Architecture

**消化筆記**: 2026-05-17-mcp-gateway-deployment-spectrum, 2026-05-17-docker-credential-governance-injection-proxy

兩篇筆記湊在一起，勾勒出一個統一的 enforcement layer 設計原則：**把「權力」跟「執行」拉開一層中介**，而非用 policy rule 直接禁止。

## Cross-Cutting Theme 1: Enforcement 作為 Mediation，不是 Prohibition

**支援筆記**: 2026-05-17-docker-credential-governance-injection-proxy, 2026-05-17-mcp-gateway-deployment-spectrum

Docker credential 的 injection proxy 模式不是「禁止 agent 用 API key」，而是「讓 agent 根本看不到 API key」。Bifrost 的 virtual key 模型也不是「禁止某個 agent 呼叫某 tool」，而是「每個 agent 持有一把啞鑰匙，gateway 根據这把钥匙查表決定能訪問什麼」。

Cloudflare 的 Code Mode 更是這個原則的硬幣反面——tool code 不到 execution time 不載入，agent 拿到的只是「能查、不能直接用」的 reference。

三個案例湊在一起：enforcement 的正確架構是 **mediation layer**，不是 **policy rule list**。Policy 決定「能不能」，mediation 決定「怎麼給」。credential injection 把這個拆成两步：gateway 查 keychain 做 policy decision，然後在 proxy 層 injection，agent 從頭到尾只碰到 sentinel value。

**可行動下一步**: 在 `docker-agent-policy-schema.md` 加上明確的「mediation layer」章節，與其把 enforcement 當 YAML rules 列表，不如定義 `enforcement_mode: mediation | prohibition`。Credential 和 MCP Tool 用 mediation，Network/FileSystem 的 allow/deny 維持 prohibition。

---

## Cross-Cutting Theme 2: Sentinel Value Pattern 是 Agent Isolation 的通用單元

**支援筆記**: 2026-05-17-docker-credential-governance-injection-proxy, 2026-05-17-mcp-gateway-deployment-spectrum

Docker credential injection 用 sentinel value（`proxy-managed`）取代真實 credential，讓 agent 無法直接讀取或 exfiltrate。Bifrost 的 Code Mode 用「search result handle」取代實際 tool code，agent 能操作 handle 但接觸不到 implementation。Cloudflare 的 MCP portal 94% token reduction 也是這個 pattern——tool definitions 全部在 portal 層 abstract 掉。

三個獨立的系統獨立演化出相同的解法：agent 不應該持有「可以直接使用的敏感 resource」，只應該持有「必須經過 gateway 兌換的 reference」。

這個 pattern 解決了一個之前沒被明確定義的問題：Hermes 的 agent（如 Hestia）如果能 `cat ~/.config/hermes/credentials.yaml`，整個 credential governance 就形同虛設。必須在架構層強制執行「credential reference ≠ credential value」。

**可行動下一步**: 评估 Hermes 的 provider API key 存储。目標：API key 不進入 session process 的記憶體空間，改由 gateway 層根據 target domain 自動匹配並注入。

---

## Cross-Cutting Theme 3: Docker 四控制面的第四層（MCP Tool）最可能是 Injection Proxy + Code Mode 組合

**支援筆記**: 2026-05-17-docker-credential-governance-injection-proxy（credential injection proxy 模式）, 2026-05-17-mcp-gateway-deployment-spectrum（Code Mode pattern）

兩篇筆記湊在一起可以推論 Docker MCP Tool governance 的實作：

- **Injection proxy 模式**（來自 credential governance 的啟發）：MCP JSON-RPC traffic 經過一個 proxy，policy decision 在 proxy 層，tool code 在允許後才實際執行
- **Code Mode pattern**（來自三個 MCP gateway 的共同演化）：tool definitions 不是靜態載入，而是 `search_tool()` + `execute` 的兩步，deferred loading 減少攻擊面
- **Shadow MCP detection**（來自 Cloudflare）：proxy 層用 JSON-RPC method regex 做動態發現，未在 allowlist 的 MCP server 自動阻擋

這個組合填補了 `docker-agent-policy-schema.md` 裡 MCP Tool enforcement 一直缺席的空白。

**可行動下一步**: 查 Docker AI Sandboxes 官方文檔中 MCP Tool governance 的具體實作格式（`docs.docker.com/ai/sandboxes/security/mcp-tools/` 或類似路徑），確認是 injection proxy 還是 policy rules。

---

## 修正既有笔记的判斷

原本 `talos-governance-policy-wuphf-pipeline.md` 把「四控制面用同一套 YAML schema」當成預設，這是錯的。Credential 需要 injection proxy pattern，MCP Tool 最可能也是（見上）。YAML policy schema 只適用於 Network + Filesystem。

這個修正直接影響 `docker-agent-yaml-schema-policy-enforcement.md` 的適用範圍。
