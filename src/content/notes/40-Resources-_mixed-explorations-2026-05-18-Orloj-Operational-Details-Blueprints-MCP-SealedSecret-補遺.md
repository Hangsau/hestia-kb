---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Orloj-Operational-Details-Blueprints-MCP-SealedSecret-補遺
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Orloj-Operational-Details-Blueprints-MCP-SealedSecret-補遺.md
title: Orloj Operational Details — Blueprints, MCP, SealedSecret 補遺
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Orloj Operational Details — Blueprints, MCP, SealedSecret 補遺

**延續自**: [[2026-05-18-Orloj-Governance---完整-Reference-Implementation-深讀]], [[2026-05-18-Axe-Memory-GC---Orloj-Blueprints---深追]], [[2026-05-18-Axe--Orloj--Moltis---三個-agent-基礎設施的不同設計路徑]]

## 來源

- Orloj Hierarchical Blueprint: `https://raw.githubusercontent.com/OrlojHQ/orloj/main/examples/blueprints/hierarchical/agent-system.yaml`
- Orloj Swarm-Loop Blueprint: `https://raw.githubusercontent.com/OrlojHQ/orloj/main/examples/blueprints/swarm-loop/agent-system.yaml`
- Orloj McpServer docs: `https://docs.orloj.dev/concepts/tools/mcp-server`（via llms.txt）
- Orloj SealedSecret reference: `https://docs.orloj.dev/reference/resources/sealed-secret`（via llms.txt）

## Per-source insight

### 1. Hierarchical Blueprint — 6-agent DAG with Join

```yaml
graph:
  bp-hier-manager-agent:
    edges:
      - to: bp-hier-research-lead-agent
      - to: bp-hier-social-lead-agent
  bp-hier-research-lead-agent:
    edges:
      - to: bp-hier-research-worker-agent
  bp-hier-social-lead-agent:
    edges:
      - to: bp-hier-social-worker-agent
  bp-hier-research-worker-agent:
    edges:
      - to: bp-hier-editor-agent
  bp-hier-social-worker-agent:
    edges:
      - to: bp-hier-editor-agent
  bp-hier-editor-agent:
    join:
      mode: wait_for_all
```

**結構**：Manager → 兩個平行的 lead（research + social）→ 各有一個 worker → 匯聚到 editor（`wait_for_all` join）。

**關鍵設計**：
- `join.mode: wait_for_all` — 兩個 worker 都完成後 editor 才啟動。這是 barrier synchronization。
- Manager 分派後不收回結果——research lead 和 social lead 各自帶 worker 獨立完成，最終 editor 合併。
- 與 sequential pipeline 不同：這是 parallel fan-out → fan-in，適合可並行的 subtask。

### 2. Swarm-Loop Blueprint — 5-agent Iterative Refinement

```yaml
graph:
  bp-swarm-coordinator-agent:
    edges:
      - to: bp-swarm-scout-alpha-agent
      - to: bp-swarm-scout-beta-agent
      - to: bp-swarm-scout-gamma-agent
      - to: bp-swarm-synthesizer-agent
  bp-swarm-scout-alpha-agent:
    edges:
      - to: bp-swarm-coordinator-agent
  bp-swarm-scout-beta-agent:
    edges:
      - to: bp-swarm-coordinator-agent
  bp-swarm-scout-gamma-agent:
    edges:
      - to: bp-swarm-coordinator-agent
```

**結構**：Coordinator → 3 scouts 平行探索 → 結果回傳 coordinator → （loop）→ 最終 synthesizer 輸出。

**關鍵設計**：
- **Feedback edges** — scouts 的 output 回到 coordinator，讓 coordinator 可以決定是否再發一輪。這是 iteration，不是一次性 fan-out。
- Synthesizer 是 terminal node — 沒有 outgoing edges。也就是 loop 結束後的最終彙整。
- 缺 `join` 宣告 — 不像 hierarchical 有 `wait_for_all`。coordinator 自己決定何時結束 loop → synthesizer。這是 implicit loop termination。

### 3. McpServer Resource — MCP Tool Governance

Orloj 把 MCP server 當成正式資源（CRD），不是 ad-hoc 連線：

**生命週期**：
1. `McpServer` resource applied → controller 建立連線
2. `tools/list` → 自動發現 tools
3. 每個 tool 生成對應的 `Tool` resource（`type: mcp`）
4. ToolPermission / AgentPolicy / ToolApproval 全線治理這些生成的 Tool

**Transport 雙模式**：
- **stdio**（process 或 container）：spawn child process 或 Docker container。Container 模式有 sandbox（read-only fs, no caps）。
- **HTTP**：連線到既有的 MCP server。支援 auth（secretRef + bearer token）。

**Idle timeout**：session reaper 在 idle_timeout 後關閉連線，下次 tool call 時 transparently recreate。Container-backed 的 server 只在 active 時消耗資源。

**Tool filter**：`tool_filter.include` allowlist 只生成指定的 tool。這是最簡潔的 MCP tool governance：不 expose 不需要的 tool。

### 4. SealedSecret — Git-Safe Encrypted Secrets

**加密方案**：RSA-OAEP wrapped AES-256-GCM。Public key 從 API GET `/v1/sealing-key/public`。只有 orlojd 有 private key。

**Schema**：
```yaml
spec:
  encryptedData:
    OPENAI_API_KEY:
      keyId: "4d8e4f1f..."
      wrappedKey: "<base64 RSA-OAEP wrapped AES key>"
      ciphertext: "<base64 nonce || aes_gcm_ciphertext>"
  template:
    labels: ...
    annotations: ...
```

**Controller 行為**：
- Decrypt → 寫入 normal `Secret` resource（same name/namespace）
- 生成的 Secret 標註 `orloj.dev/sealedsecret-owner` annotation
- 若 target Secret 已存在但無 ownership annotation → **fail closed**（`status.phase: Error`）。這防止 overwrite 手動建立的 secret。
- Background cleanup：orphan Secret（source SealedSecret 已刪）自動清除。

**CLI workflow**：
```bash
orlojctl seal public-key                    # 取得 public key
orlojctl seal secret -f secret.yaml         # 從 manifest seal
orlojctl seal secret openai-api-key \
  --from-literal value=sk-prod-123 \
  --out secrets/openai-api-key.sealed.yaml  # 從 literal seal
orlojctl apply -f secret.sealed.yaml        # 部署
```

## Hermes 啟發

1. **Swarm-loop pattern 是 Hermes 缺的 topology**：目前 Hermes 的 multi-agent 只有 sequential delegation（delegate_task）。Swarm-loop（coordinator ⇄ workers feedback loop）適合需要 iterative refinement 的場景——如 code review、multi-round research、adversarial testing。

2. **MCP tool governance 的 auto-generation 模型**：Orloj 的 McpServer → 自動生成 Tool resource → ToolPermission 治理。Hermes 的 MCP gateway 目前只做 forwarding，沒有 per-tool permission layer。Orloj 的 `tool_filter.include` allowlist 是最簡潔的第一層。

3. **SealedSecret 是 secret-leak-prevention 的下一步**：Hermes 目前只有 detection（scan for leaks）。Orloj 的 SealedSecret 做到 prevention-by-design——加密後的 YAML 可以直接進 git。對 Talos 的 credential governance：可以考慮類似的 public-key seal 流程，把 gateway API keys 加密後進 repo，只在 runtime 解密。

4. **Join semantics 是 DAG pipeline 的必要組件**：Hierarchical blueprint 的 `join.mode: wait_for_all` 讓 multi-agent DAG 有明確的同步點。Hermes 目前沒有這個概念——subagent 之間沒有 join。

5. **Ownership annotation 的 conflict detection**：SealedSecret 的 controller 在 target Secret 已存在但無 ownership annotation 時 fail closed。這防止 silent overwrite。Talos 的 board audit 可以借鏡：偵測 "claim 完成但無 ownership trail" 的假結案。

## ⏳ 未追蹤

- Orloj 的 `task.yaml` 範例（hierarchical + swarm-loop）— 看 task input schema 和參數傳遞模式
- Orloj 的 `agents/` 目錄（每個 blueprint 的 agent 定義）— 這些 YAML 沒綁在 blueprint 目錄裡（GitHub API 回 `None`），可能在 `examples/agents/` 
- Orloj 的 Kubernetes CRD operator 實作（`/deploy/kubernetes-operator`）— 如何在 k8s 環境 sync governance resources
- Orloj 的 Starter Blueprints 總覽頁（`/guides/starter-blueprints`）— 可能還有 pipeline topology 沒看

## ✅ 本次探索完成
