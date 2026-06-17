---
_slug: 40-Resources-_mixed-explorations-2026-05-31-AgeMem-三階段-GRPO-實錄-LTM-STM-統一策略的關鍵收穫
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-AgeMem-三階段-GRPO-實錄-LTM-STM-統一策略的關鍵收穫.md
title: AgeMem 三階段 GRPO 實錄：LTM/STM 統一策略的關鍵收穫
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agemem
- context
- delete
- grpo
- hermes
- ltm
- memory
- reward
- stage
- stm
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

**日期**: 2026-05-31
**延續自**: [[2026-05-31-探索-AI-Agent-Memory-架構-2026---State-of-the-Art]], [[2026-05-31-探索-AgeMem-统一记忆管理---Mem0-Benchmark-生態]]

# AgeMem 三階段 GRPO 實錄：LTM/STM 統一策略的關鍵收穫

## 核心論文資料

- **Title**: Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents
- **arXiv**: [2601.01885](https://arxiv.org/abs/2601.01885)（v2, 30 Apr 2026）
- **Authors**: Yu, Yao, Xie, Tan, Feng, Li, Wu（武漢大學 + Alibaba）
- **Method**: 三階段 progressive GRPO + step-wise GRPO 處理不連續 reward

---

## 關鍵 insight：AgeMem 與先前論文的最大差異

### 1. 統一策略 vs 分離策略

AgeMem 之前的記憶系統（Mem0、LangMem、A-Mem）都把 LTM 和 STM 當成獨立的子系统：
- LTM：有專門的 memory manager 或 trigger 機制
- STM：靜態的 context window，靠 RAG 擴展

**AgeMem 的突破**：讓同一個 policy πθ 同時生成 language generation + memory operations（6 個工具：Add/Update/Delete 用於 LTM，Retrieve/Summary/Filter 用於 STM）。

> 這正是 Hermes heartbeat_learning.py 可以借鑒的方向——目前 staleness detection 是被動的（decay），但 AgeMem 的工具化架構可以讓「何時蒸餾」變成一個 learned decision。

### 2. 三階段漸進訓練

| Stage | 目標 | Memory 狀態 |
|-------|------|-------------|
| Stage 1 | LTM storage capabilities | LTM 逐步建立；STM 正常 |
| Stage 2 | STM context management | LTM 保持；STM 在 distractor 注入後 reset |
| Stage 3 | 協調兩種 memory 完成任務 | LTM 跨 stage 持久化；STM Stage 2 後 clear |

Stage 2 的 context reset 是關鍵——確保 agent 不能靠殘留 context 解決問題，必須真正從 LTM retrieve。

### 3. Step-wise GRPO 解決不連續 reward

標准 GRPO 需要連續 trajectory，但 memory operations 的回報是**延遲的**（最後任務完成才結算）。Step-wise GRPO 將最終 reward 的 credit 傳播回所有 intermediate memory decisions。

公式：
```
R(τ) = Σi wi·Ri(τ) + Ppenalty(τ)
```

三個 reward component：
- R_task：任務表現（final task completion）
- R_context：context 管理質量（STM tools 的使用是否有效）
- R_memory：記憶品質（MQ metric，LLM judge 評估 stored facts 的質量）

### 4. 六個工具的具體規格

| Tool | Target | Function |
|------|--------|---------|
| Add | LTM | 寫入新知識到 memory store |
| Update | LTM | 修改現有 entry（帶 memory_id） |
| Delete | LTM | 移除 entry（防止 stale 累積） |
| Retrieve | STM | 從 LTM 召回 top-k 相關記憶進 active context |
| Summary | STM | 壓縮 interaction history span |
| Filter | STM | 過濾與 criterion semantic similarity 超過 θf 的 messages |

**重要**：Delete tool 直接對應 Hermes 的 staleness 問題。當 user 換工作時，舊偏好要被刪掉而非標記過時。

---

## 對 Hermes / Talos 的具體啟發

### 1. WS-035 drift penalty 可以量化

AgeMem 的 Memory Quality（MQ） metric：
- 用 LLM judge（Qwen-Max）評估 stored facts 覆蓋 expected facts 的程度
- Score 0.0~1.0，完全精確 = 1.0

**應用**：Hermes 的 drift penalty 可以基於 MQ 分數而非簡單的 staleness threshold。當某個 fact 的 `confidence_valid_until` 過期，MQ 分數應開始線性衰減，而非 binary 過期。

### 2. Delete tool 的重要性在 Case 1 有完整展示

AgeMem Case 1 展示了一個學習偏好從 60min→120min 的完整 cycle：
1. Add_memory 初始偏好
2. Update_memory 更新為新值（保留歷史標記）
3. 用戶確認 120min 已成為永久偏好
4. **Delete_memory + Add_memory** 清理含「updated from 60 minutes」歷史標記的 entry，寫入乾淨的新 entry

**這就是 Hermes 目前缺口的核心**：heartbeat_learning.py 有 decay 但沒有 Delete（蒸餾）。當 fact 變成「confirmed wrong」而非「just old」，需要刪除而非壓縮。

### 3. Stage 2 distractor injection 模式

AgeMem Stage 2 注入 N=3~7 的 distractor utterances（與目標 query 無語義共享但具有對話可信度），強迫 agent 學習 Filter_context。

**對 Hermes 的啟發**：研究 pipeline 中的「dead leads」或「outdated facts」就是隱性 distractor。當 context 累積過多過時資訊，Filter tool（蒸餾）比 Retrieve 更重要。

### 4. All-Returns vs Answer-Only reward

AgeMem 實驗證明：reward 所有 intermediate steps（not just final answer）顯著提升 memory quality：
- Answer-Only: MQ = 0.415, J = 0.546
- All-Returns: MQ = 0.605, J = 0.555
- **改善**：MQ +46%, J +2%

**對 Hermes heartbeat learning rubric 的修正**：目前的 `followup_quality` 只看「是否有後續追蹤」，可以升級成「記憶操作品質」（是否正確使用 Add/Delete/Update，stale fact 是否被及時蒸餾）。

---

## Untracked Leads

- https://arxiv.org/abs/2602.16313 — MemoryArena benchmark
- https://github.com/mem0ai/memory-benchmarks — Mem0 開源 evaluation framework
- https://arxiv.org/abs/2601.01885#appendix-a — AgeMem 詳細工具實作（Algorithm 1-5）

---

## ✅ 本次探索完成
