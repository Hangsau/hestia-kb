---
_slug: 40-Resources-_mixed-explorations-2026-05-30---Agentic-Memory--AgeMem----RL-Trained-Unified-LT
_vault_path: 40-Resources/_mixed/explorations/2026-05-30---Agentic-Memory--AgeMem----RL-Trained-Unified-LT.md
title: 2026-05-30 | Agentic Memory (AgeMem) — RL-Trained Unified LTM/STM Management
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- agent
- delete
- hermes
- ltm
- memory
- stage
- stm
- tool
- update
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 2026-05-30 | Agentic Memory (AgeMem) — RL-Trained Unified LTM/STM Management

**延續自**: [[2026-05-30-LLM-Agent-Memory-Architecture---Survey---2026-B]]
**日期**: 2026-05-30

## 核心發現：AgeMem 三階段 GRPO + Tool-Based Memory Interface

### 為何值得深讀（相較於 survey 的 summary）

Survey（2603.07670）將 AgeMem 列為 "Pattern C: Tiered memory + learned control" 的 exemplar，僅 3 行描述。但 AgeMem 論文（2601.01885）是 2026 年的最新工作，實際內容遠比 survey summary 豐富。

### AgeMem 核心設計

**三階段漸進 RL 訓練**：
- **Stage 1**：一般對話，agent 學習何時把資訊存進 LTM（Add/Update/Delete）
- **Stage 2**：引入干擾資訊，agent 學習管理 STM（Retrieve/Summary/Filter）
- **Stage 3**：最終任務依賴 LTM + STM 的協調使用

**Context reset between stages** — Stage 1 vs Stage 2 之間 reset STM context，強制 agent 不能靠殘留上下文，必須正確從 LTM retrieval。這是訓練階段的關鍵機制。

**Step-wise GRPO**：將最終任務 reward 反向傳播到早期的 memory decisions，解決 memory operations 的 sparse/discontinuous rewards 問題。

### 6 Tool Interface（從 agent 的視角看 memory）

| Tool | Target | Function |
|------|--------|----------|
| Add | LTM | 存新知識進 long-term store |
| Update | LTM | 修改已有 entry |
| Delete | LTM | 移除 entry（對應 staleness/drift 問題） |
| Retrieve | STM | 把 LTM 取出到 active context |
| Summary | STM | 壓縮 active context segments |
| Filter | STM | 從 active context 過濾不相關資訊 |

**關鍵：Update + Delete 是解決 staleness 的具體工具**。Survey 和 Mem0 blog 都提到 staleness 是 open problem，但 AgeMem 提供了 RL-learned 的 Update/Delete 策略。

### 對 Hermes 的直接啟發

1. **WS-035 bounded dereferencing** — AgeMem 的 Update/Delete tools 是架構參照。Hermes 需要類似機制：confidence decay觸發dereferencing，而非純粹基於時間。

2. **Staleness as learnable signal** — AgeMem 讓 RL agent 自己學何時 Update/Delete。Hermes 的做法（規則基礎 + confidence threshold）是一種簡化，但 AgeMem 證明了 "learned" 路徑是可行的。

3. **Three-stage training analog** — Hermes heartbeat_learning.py 的蒸餾邏輯（technical/domain categories → staleness computation）可以類比為 Stage 1（accumulate）→ Stage 2（context management）→ Stage 3（retrieval use）。只不過 Hermes 是規則驅動而非 RL。

4. **Tool interface as memory API** — AgeMem 的 tool-based memory control 與 Hermes 的 `memory_prefixer.py query` 設計精神一致，只是 AgeMem 是 end-to-end learned，Hermes 是 fixed policy。

## 與前期筆記的連結

**Survey 提出的 10 個 open challenges**，AgeMem 直接解決了：
- Challenge 3: "Trustworthy reflection (avoid entrenching mistakes via confirmation bias)" — AgeMem 的 Update/Delete tools + RL reward 結構
- Challenge 4: "Learning to forget (selective forgetting under safety constraints)" — AgeMem 的 Delete tool + filter penalty

**Mem0 blog 的 staleness problem**（"high-relevance memories become confidently wrong"）— AgeMem 的 Update/Delete 是目前看到最具體的架構性解決方案。

## Untracked Leads

- arXiv 2601.01885 Appendix A: AgeMem 詳細演算法（Algorithm 1-5）+ 實驗細節 — 值得再取 full content
- Mem0 的 entity linking approach（write-time extraction → parallel entity collection → fused score at read time）與 AgeMem 的 Retrieve tool 比較
- GRPO step-wise credit assignment 的數學推導

## ✅ 本次探索完成
