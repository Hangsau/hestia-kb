---
_slug: 40-Resources-_mixed-explorations-2026-05-26-CUGA-Policy-System---Runtime-Governance--IBM--arXiv-2605-208
_vault_path: 40-Resources/_mixed/explorations/2026-05-26-CUGA-Policy-System---Runtime-Governance--IBM--arXiv-2605-208.md
title: CUGA Policy System — Runtime Governance (IBM, arXiv:2605.20874)
date: 2026-05-26
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- cuga
- dcg
- governance
- hermes
- policy
- runtime
- stage
- talos
- tool
created: '2026-05-27'
updated: '2026-06-15'
status: budding
---

# CUGA Policy System — Runtime Governance (IBM, arXiv:2605.20874)

**日期**: 2026-05-26 | **來源**: arxiv.org/html/2605.20874 | **類型**: 研究筆記
**延續自**: 相關 `dcg-hermes-talos-governance-integration.md` (PARTIAL)、`ws-028-hermes-agent-lifecycle-governance.md` (IN PROGRESS)

---

## 核心架構：CUGA 五層 runtime governance

CUGA (Computer-Using Generalist Agent) 是 IBM 的开源 enterprise agent，實現了與 Hermes/Talos 治理方向高度互補的 runtime policy enforcement。

### Stage 1 — Intent Guard（意圖守衛）
- **位置**：Agent reasoning loop **之前**，最早截獲
- **觸發**：keyword + embedding similarity（threshold 0.65）
- **動作**：立即終止執行，agent 完全看不到惡意/危險請求
- **关键设计**：優先於其他 policy types（priority 90），確保 blocking > advisory

### Stage 2 — Playbook（劇本注入）
- **位置**：system prompt 動態注入
- **功能**：step-by-step 指令，引導 agent planning
- **关键设计**：不阻斷，而是塑形（shaping），「精確指導而非膨脹 prompt」
- **與 Hermes 對照**：相當於 `hermes.session_tree` 的結構化約束，但作為 runtime policy 而非靜態 prompt

### Stage 3 — Tool Guide（工具指南）
- **位置**：tool description 執行前動態充實
- **功能**：在 tool description 附加 warning/context（如「known-unreliable endpoint」）
- **关键设计**：可疊加（cumulative，非 mutually exclusive），session-scoped deep-copy

### Stage 4 — Tool Approval（工具審批）
- **位置**：code generation **之後**、實際執行**之前**
- **功能**：暂停執行 graph，等待 human-in-the-loop 確認
- **关键设计**：脫離 agent reasoning loop（outside the reasoning loop），確保高風險操作有獨立把關

### Stage 5 — Output Formatter（輸出格式化）
- **位置**：最終 response 返回之前
- **功能**：structred JSON / verbatim template / Markdown 格式化
- **Trigger**：同時看 user input + generated response

---

## 關鍵啟發

### 1. Policy 分離儲存 + 動態觸發
CUGA 用 Milvus vector DB 儲存 policy， 량以 keyword/embedding/application/state/tool trigger 動態匹配。不是靜態 prompt，而是runtime 動態插入。

**對 Talos 啟發**：現有 `dcg-hermes-talos-governance-integration.md` 的 DCG 是靜態 regex matching。CUGA 的分層觸發機制（keyword → similarity → state）更適合複雜企業場景。

### 2. Intent Guard 優先於 Playbook
CUGA 的 policy evaluation 順序：Intent Guard（blocking）→ Playbook（shaping）→ Tool Guide → Tool Approval → Output Formatter。
- 惡意請求在 Intent Guard 被截獲，Playbook 根本不會被執行
- 這解釋了為何 `ws-028` 的四層模型應該把「隔離/ blocking」放在最外層

### 3. Tool Approval 是獨立的 HITL gate
Tool Approval 發生在 code generation 後、執行前，脫離 agent reasoning loop。這是 Mos moltis governance 的「Block tool invocation」hook 的對應設計。

### 4. Token overhead 是可接受的代價
CUGA benchmark 顯示：runtime governance 的 token overhead 相對於破壞性錯誤是可接受的代價（enterprise 合規至上的場景）。

---

## 與現有提案的對應

| CUGA 層次 | Talos 提案 | 狀態 |
|---|---|---|
| Intent Guard | `dcg-hermes-talos-governance-integration.md` | PARTIAL |
| Playbook | `ws-028-hermes-agent-lifecycle-governance.md` (Phase 1) | IN PROGRESS |
| Tool Guide | `dcg-hermes-talos-governance-integration.md` (Tool Warning) | PARTIAL |
| Tool Approval | `ws-028` Phase 3 (pre-execution gate) | IN PROGRESS |
| Output Formatter | 未涵蓋 | PENDING |

---

## 未追蹤 Leads

- https://github.com/cuga-project/cuga-agent — CUGA 開源 repo
- https://github.com/cuga-project/oak-bench — OAK benchmark (customer-care, 27 tasks)
- https://huggingface.co/datasets/ibm-research/BPO-Bench — BPO benchmark (26 tasks, enterprise workflows)
- arxiv.org/abs/2605.20874 — 完整論文 PDF（本 note 來源）

## ✅ 本次探索完成

