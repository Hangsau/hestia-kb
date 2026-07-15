---
_slug: research-2026-07-15-1900-hermes-consolidated-insight
_vault_path: research/2026-07-15-1900-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-governance
- ws-035
source: multi
created: '2026-07-15'
confidence: high
title: 2026-06-09 Memory Governance 研究日：四篇筆記的 cross-cutting 收斂
type: research
status: seedling
updated: '2026-07-15'
---

# 2026-06-09 Memory Governance 研究日：四篇筆記的 cross-cutting 收斂

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇筆記同一天（2026-06-09）產出，圍繞 LLM agent 記憶與執行治理。單篇各自已做跨論文 synthesis，但**把四篇放在一起**才浮現三個非顯然的 pattern：WS-035 drift penalty 的三個缺口其實是同一個問題的三面、MemoryOS 的 heat-based eviction 是其他三個架構的合成答案、governance 與 memory 的 separation principle 是同一條底層原則的兩種投影。

## Cross-Cutting Theme 1: WS-035 drift penalty 的「reader 失效信號」缺口是四篇共同盲點

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

四篇都在討論記憶系統的寫入/鞏固/蒸發策略，但**都把 reader 當成被動消費者**：

- **H-MEM + RecMem**: 寫入是 top-down routing（H-MEM）或 recurrence-triggered（RecMem），但都沒有機制讓讀取結果反饋給寫入策略。RecMem 的 subconscious store 只看相似度，未追蹤讀取後是否真的被引用。
- **MemoryOS**: heat score 有 `N_visit`（檢索次數），這是最接近的 reader 信號，但它只影響**蒸發**，不影響**寫入觸發條件**。MTM→LPM 的遷移只看熱度，不看「讀者到底找到了什麼、缺了什麼」。
- **SAGE**: **唯一**明確建立 writer-reader closed loop 的架構。Reader 找不到證據時，反饋「圖中哪些結構鏈路缺失」給 writer。這正是其他三個系統缺的東西。
- **Governed Memory**: reflection-bounded retrieval 有 bounded rounds，但這是 retrieval-time 的迭代，不是 retrieval → write 的跨時反饋。

把四篇放在一起看：**drift penalty 不是 decay 函數的問題，而是閉環缺口的問題**。單獨看任一篇會以為是「該加 staleness detection」（governance 筆記）或「該加 heat score」（memory-os 筆記），但這兩個解其實是同一個 reader→writer feedback 信號的不同表現形式。

**可行動下一步**: 在 `heartbeat_learning.py` 加一個 `RetrievalFeedbackLog` 結構，記錄每次 task context 匹配時「命中了哪些 distillate / 找不到證據時 query 是什麼」。當某 distillate 被命中 0 次連續 N 天，或 reader 連續 K 次找不到某 query type 的證據，自動觸發：
1. 對應 distillate 標記 `cold_candidate`
2. 累積 cold_candidate + missing-query 模式 → 發出 `distill_trigger` 信號給 distillation loop（不只是 time-based 的 trigger）

不是把 decay 函數改複雜，而是**把 reader 的失敗轉成 writer 的輸入**。

---

## Cross-Cutting Theme 2: MemoryOS 的 heat score 是其他三個架構的合成收斂點

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

乍看 H-MEM、RecMem、SAGE、Governed Memory 是四種獨立設計，但把 heat score 公式展開：

```
Heat = α·N_visit + β·L_interaction + γ·R_recency
```

每一項其實是其他架構核心概念的精確對應：

| Heat score 項 | 對應架構的核心概念 |
|--------------|-------------------|
| `N_visit`（檢索次數） | **SAGE** 的 reader failure signal — 讀取頻率本身就是讀者對該記憶價值的投票 |
| `L_interaction`（互動長度） | **Governed Memory** 的 memory density saturation（7 memories/entity peak）— 互動深度反映資訊密度 |
| `R_recency`（時間衰減） | **H-MEM/RecMem** 的 decay 機制，但**用於「提升」而非「懲罰」** — 長期高 heat 的記憶即使 recency 衰減仍能保留 |
| 整個 heat score 公式 | **H-MEM** 的 layer promotion（從低層往高層遷移的觸發條件）— 但 H-MEM 用 discrete threshold，MemoryOS 用連續函數 |

四篇獨立設計的架構，**都是 heat score 的某個子集或變體**。H-MEM 強調路由、RecMem 強調時機、SAGE 強調閉環、Governed Memory 強調 schema，但都沒把「重要性 = f(visit, depth, recency)」這條最簡單的公式完整實作。

對 WS-035 的啟示：drift penalty **不需要從零設計**。直接移植 MemoryOS 的 heat score 公式，把 distillate 當 segment、把 task context 引用當 page interaction，就能拿到四篇研究的合成效果。

**可行動下一步**: 在 `heartbeat_learning.py` 的 `DistillateIndex` 加三個欄位（`visit_count`、`interaction_count`、`last_referenced_at`），每天計算一次 heat score。低於閾值的 distillate 進入 `cold_candidate` 集合（餵給 Theme 1 的 retrieval feedback loop）。**不要自創新的 decay 函數** — MemoryOS 的公式是已經 cross-validated 的。

---

## Cross-Cutting Theme 3: 架構分離（separation principle）是 governance 與 memory 的共同底層

**支援筆記**: llm-agent-memory-governance-synthesis, sage, memory-os

四篇中兩篇（governance、sage）反覆強調「不能混在一起」，但分離的對象不同：

| 架構 | 分離什麼 | 分離理由 |
|-----|---------|---------|
| **OCL** (governance 筆記) | proposal generation ↔ environment-facing execution | 88% unsafe rate 來自不分離 |
| **Governed Memory** (governance 筆記) | memory store ↔ governance layer | 多 agent 寫入需要仲裁 |
| **SAGE** | writer ↔ reader | 缺少 reader feedback → writer 盲目 |
| **MemoryOS** | STM ↔ MTM ↔ LPM | 不同生命週期的記憶不該共享存取介面 |

乍看四個是不同的工程考量。但放在一起看：**它們都是「避免單一組件同時承擔生成與驗證/消費職責」的具體化**。OCL 防止 LLM 既提案又執行、SAGE 防止 writer 既寫又讀、Governed Memory 防止應用程式既讀又治理、MemoryOS 防止 STM 既快取又長期儲存。

這條原則對 Talos 的啟示：**Talos 的 PolicyInterceptor 缺的不是更多 policy rule，是明確的 architectural boundary**。目前 LLM 的 generated tool call 與實際執行之間沒有真正的 separation — PolicyInterceptor 是在同一個 process 內攔截，沒有獨立的 audit trail、沒有獨立的 escalation path、沒有獨立於 LLM 的 deterministic enforcement。

**可行動下一步**: 把 `talos/policy/` 的 PolicyInterceptor 從「同進程 inline hook」改為「獨立 daemon process」：
- LLM 產出 proposal → 寫到 shared queue → PolicyInterceptor daemon 讀 queue → 決定 approve/revise/block/escalate → 寫 audit log → 實際 tool execution 從 audit log 讀 approved set
- 即使 LLM process 崩潰，audit log 仍可事後 review
- OCL 的 `πaudit` + `πgate` + `πescalate` 變成 daemon 內的三個獨立 module

這個改動**不只是 engineering hygiene** — 它是 OCL 量化結果（94% → 12% valid success rate gap）的架構前提。

---

## 信心標示

- Theme 1 (reader→writer feedback loop): **high** — 四篇筆記都有 reader 角色但只有 SAGE 有閉環，缺口的 negative presence 在三篇中都明確可見
- Theme 2 (heat score as 合成收斂): **medium** — 公式對應是概念 mapping 而非數學證明，但 MemoryOS 的實證結果（LoCoMo 1st place, 4.9 LLM calls）支持這個對應
- Theme 3 (separation principle): **high** — OCL 88% unsafe rate 是量化證據，SAGE writer-reader loop、Governed Memory 多 agent 場景、MemoryOS 三層架構都是同一原則的不同 instantiation

## 未消化的後續問題

1. Theme 1 的 `RetrievalFeedbackLog` 需要先在 Hermes 既有 task 流量上跑 baseline，才能定 N 天 / K 次的閾值 — 沒有 baseline 就直接上 production 是猜測
2. Theme 2 的 heat score 移植需要決定 α/β/γ 的初始權重 — MemoryOS 沒報告這三個係數的 ablation，這是個文獻空白
3. Theme 3 的 daemon 改動是 breaking change — 需要先在 staging 環境驗證 audit log 與現有 PolicyInterceptor 行為等價