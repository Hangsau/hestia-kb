---
_slug: 40-Resources-_mixed-explorations-2026-05-20-探索-Google-Titans---Neural-Long-Term-Memory
_vault_path: 40-Resources/_mixed/explorations/2026-05-20-探索-Google-Titans---Neural-Long-Term-Memory.md
title: 探索：Google Titans — Neural Long-Term Memory
date: 2026-05-20
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- attention
- context
- decay
- evolve
- heartbeat
- llm
- memory
- neural
- term
- titans
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# 探索：Google Titans — Neural Long-Term Memory

**日期**: 2026-05-20 | **來源**: arxiv 2501.00663 + HF paper page | **類型**: 探索
**延續自**: [[2026-05-20-llm-agent-memory-biological-decay.md]]（leads 未追蹤區塊）

## Per-Source Insight

### Titans: Learning to Memorize at Test Time

**來源**: https://arxiv.org/abs/2501.00663 | Ali Behrouz, Peilin Zhong, Vahab Mirrokni (Google)

**核心論文結論**：
- **核心論點**：標準 attention 是 short-term memory（有限 context，精確依賴建模）；neural memory 是 long-term memory（能記憶歷史資料，持續性）。
- **Titans 架構**：結合 attention（短期）+ neural memory（長期）的混合架構，三種變體：
  1. **Memory as Context**：將 memory 作為 context 注入
  2. **Memory as Layer**：將 memory 作為網絡層
  3. **Memory as Gated Branch**：門控機制動態選擇使用哪種 memory
- **評測**：超越 modern recurrent models 和 hybrid variants，在各种 task 和 context window size 下優於 Transformer

**對 Herms 的啟發**：
- 區分「精確短期上下文」vs「持久神經記憶」的混合架構，可以對應 heartbeat 的「馬上要處理的錯誤」vs「過去累積的 pattern」
- 論文中提到 attention 擅長 dependency modeling，這和 EVOLVE sensor 鏈每次做 dependency check 的角色類似
- 三種整合方式提供了 heartbeat severity tracking 可以借鑒的架構模式

---

### 相關跟進：2505.23735 — Evaluating Memory in LLM Agents

**來源**: web search 發現 | 標題：Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions

**作者**：Yuanzhe Hu et al., Ali Behrouz et al.

**方向**：LongMemEval-V2 基準測試，評估 agent 在漫長互動中能否保持長期記憶（界面操作、狀態動態、工作流、失敗模式）。

---

## 跨文章 Synthesis

**生物衰減 vs 神經記憶的交匯點**：
- YourMemory：用生物衰減函數（Ebbinghaus）管理 explicit memory strength
- Titans：用 neural memory module 學習「什麼值得記憶」，而不是靠預設公式
- 兩者都承認：standard attention/context window 不足以作為長期記憶載體

**對 Talos heartbeat 的具體方向**：
- EVOLVE sensor 的「錯誤指紋追蹤」本質上是一種神經記憶——同一錯誤指紋反覆出現 = 這個 pattern 值得被記住
- category-specific decay（YourMemory）和 severity escalation（EVOLVE）結合：failure 類錯誤 decay 最快（11天半衰期），但若連續出現應加速 escalation
- Titans 的 gated branch 概念可用於：某個 sensor 連續 stable 是否可以降低其執行頻率？

## 未追蹤

（無）

## ✅ 本次探索完成
