---
_slug: 40-Resources-_mixed-research-2026-06-05-cuga-policy-system
_vault_path: 40-Resources/_mixed/research/2026-06-05-cuga-policy-system.md
title: 探索：CUGA Policy System — Governance by Construction
created: '2026-06-05'
updated: '2026-06-15'
type: research
tags: []
status: budding
---

# 探索：CUGA Policy System — Governance by Construction

**日期**: 2026-06-05 | **來源**: arxiv:2605.20874 | **類型**: SPIKE

## CUGA Policy System 核心架構

IBM Haifa 團隊的 CUGA policy system（Policy-as-Code layer， LangGraph 整合）提供 5 個 runtime enforcement checkpoints：

1. **Intent Guard** — 在規劃之前攔截惡意/意外 harmful intent（keyword matching + embedding similarity，優先於其他 policy）
2. **Playbook** — 動態注入 system prompt，引導 agent 推理過程（structured multi-step execution）
3. **Tool Guide** — 在 tool execution 前 enrich tool description（warning、pagination requirements、alternative endpoints）
4. **Tool Approval** — human-in-the-loop gate，post-code generation 暫停等待確認
5. **Output Formatter** — 最後一關，結構化輸出（template verbatim / markdown / JSON schema）

## 關鍵發現

- **Policy-as-code 勝過 Prompt-level safety**：prompt-level 只是「礼貌请求」，CUGA 在 5 個 checkpoint 強制執行，與模型無關
- **Trigger 機制**：keyword / embedding similarity / application context / state / tool，四種觸發方式
- **衝突解決**：Intent Guard 優先（deterministic first），其他用 LLM structured reasoning 選擇
- **Ablation 結果**（BPO benchmark，GPT-OSS-120B）：
  - No policies: 46.2%
  - 2 policies: 71.8% (+25.6pp)
  - 5 policies: 78.2% (+32.0pp)
- **OAK benchmark**：GPT-OSS-120B 從 75% → 100%（+25pp）

## 與現有架構對照

CUGA 的 5 checkpoint 對應到 Hermes 的潛在強化點：
- Intent Guard → 對應 WS-032 `guardian-sandboxing-gradient` 的 L1/L2 tool scoping
- Playbook → 對應 `hermes-explicit-behavioral-guidance.md`（已存在，尚未 enforcement）
- Tool Guide → 對應 `hermes-session-tree-phase-navigation` 的 tool description enrichment
- Tool Approval HITL → 對應 `dcg-hermes-talos-governance-integration.md` 的 enforcement 層（DCG 已有部分功能）
- Output Formatter → 對應 `wuphf-lint-model.md` 的矛盾偵測

## 跨文章 Synthesis

CUGA 的 Policy System + Microsoft AGT 的 Agent Hypervisor + DCG 的 dual-regex enforcement，三者都收斂到同一個結論：**runtime enforcement > prompt-level compliance**。Prompt-level instruction 只是「礼貌请求」，真正的 governance 必須在 agent reasoning loop 之外執行。

這個收斂與 `structure-before-content-pattern.md` 的發現一致：結構化約束 > 純嵌入檢索。Agent governance 也是如此 — typed policy primitives > probabilistic prompt adherence。

## 未追蹤 Leads

- https://github.com/cuga-project/cuga-agent — CUGA 開源 repo
- https://github.com/cuga-project/oak-bench — OAK benchmark
- arxiv:2503.01861 — Marreed et al. "Towards enterprise-ready computer using generalist agent"

## ✅ 本次探索完成