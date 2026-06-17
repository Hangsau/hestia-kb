---
_slug: 40-Resources-_mixed-research-2026-06-11-2101-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-11-2101-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- drift-penalty
- ws-035
source: multi
created: '2026-06-11'
confidence: high
title: Memory Systems 四篇綜合：Drift Penalty 的真正瓶頸不是公式，是「結構/開放二元性」與「Writer/Reader 邊界」
updated: '2026-06-15'
type: research
status: budding
---

# Memory Systems 四篇綜合：Drift Penalty 的真正瓶頸不是公式，是「結構/開放二元性」與「Writer/Reader 邊界」

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇關於 LLM agent 記憶架構的探索，個別都提出了 WS-035 drift penalty 的具體機制（recurrence trigger、heat score、reader-failure signal、audit log），但單看任一篇會把 drift penalty 當作「**挑選正確的觸發信號**」的問題。**放在一起看才浮現真正的瓶頸**：drift penalty 失敗不是因為信號錯，是因為餵進去的記憶本身沒有「結構/開放二元性」、系統本身沒有「Writer/Reader 邊界」。這兩件事是 governance 的**前置條件**。

## Cross-Cutting Theme 1: 結構/開放二元性是 governance 的必要前提（5 篇系統都呈現，但 4 篇筆記的其中 1 篇才明確點名）

**支援筆記**: 2026-06-09-llm-agent-memory-governance-synthesis（最明確）, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine

**分析**

Governed Memory (arXiv:2603.17787) 唯一明文點出「**Dual Memory Model**」：同一 extraction pass 同時輸出 open-set memory（atomic facts, 自然語言）與 schema-enforced memory（typed property values, 結構化）。其餘三篇雖然沒有明文用「dual」一詞，但**結構都是同一形狀**：

| 系統 | 開放端 | 結構端 |
|------|--------|--------|
| H-MEM | Episode layer（原始內容） | Domain/Category/Trace 三層 index |
| RecMem | Subconscious store（raw embeddings） | Episodic + Semantic 兩層摘要 |
| MemoryOS | STM（原始對話頁面） | MTM segments + LPM 90 維度 User Traits |
| SAGE | Graph topology（隱式關係） | Entity-relation triples（顯式結構） |
| Governed Memory | Open-set atomic facts | Schema-enforced typed properties |

把四篇放在一起看的非顯然結論：**drift penalty 公式（heat score、recurrence count、reader failure）都需要在「結構端」運算，因為只有結構化欄位才能被 query、衰減、標記、稽核。** 在「開放端」上做 drift penalty 等於在做 NLP 相似度比對，會落入「語意看起來相關但其實過時」（governance-synthesis 引述 Section 3.2 的失敗模式）。

**對 Hermes 的具體意涵**：`heartbeat_learning.py` 目前的 distillate 是 LLM 生成的自由文字，沒有結構化欄位（created_at 之外）。這意味著所有建議的 drift penalty 機制（heat score、recurrence trigger）**目前根本沒有可作用的 target**。要先給 distillate 加結構化 schema（最低限度：valid_from / valid_until / confidence / source_skill / contradiction_count），drift penalty 才有地方掛。

**可行動下一步**

1. 在 `heartbeat_learning.py` 的 distillate 結構加入 4 個結構化欄位：`valid_from`（timestamp）、`valid_until`（timestamp, nullable）、`confidence`（0-1 float）、`source_skill`（enum/string）。這 4 欄不需要 LLM，叫 LLM 多吐這 4 個 JSON 欄位即可。
2. 用 `[ ]` checklist 在 vault 的 `02-Areas/Hermes-Ops/` 開一份 `distillate-schema-v1-proposal.md`，列出每個欄位的型別、預設值、valid_when_null 規則。
3. schema 上線後才能開始實作 heat score（`N_visit × L_interaction × R_recency`）—— 在自由文字 distillate 上實作 heat score 會被 governance-synthesis 引述的「semantic representation 仍然看起來相關」陷阱吃掉。

## Cross-Cutting Theme 2: Writer/Reader 邊界 = PolicyInterceptor 的本體（OCL 最明文，但 SAGE 與 MemoryOS 都在做同一件事）

**支援筆記**: 2026-06-09-llm-agent-memory-governance-synthesis（OCL Source 2）, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory

**分析**

OCL (arXiv:2606.04306) 唯一明文點出 architectural principle：「**separate proposal generation from environment-facing execution**」，並量化 12%→96% valid success rate 的差距。SAGE 沒有 OCL 那麼明文，但 writer-reader coupling + self-evolution loop **就是** 同一個架構：writer 產出 → reader 消費 → reader failure feedback 給 writer。

MemoryOS 與 RecMem 表面是「記憶分層」，但**它們其實都在 tier 邊界實作了 writer/reader 切換**：
- MemoryOS MTM→LPM 遷移是 writer；LPM persona 更新是 reader；traits 變化再 feedback 影響下次 segment 評分（F_score）= 隱性 feedback loop
- RecMem subconscious→episodic 是 writer（不消耗 LLM）；episodic→semantic 是 reader（消耗 LLM 一次）；semantic refinement 再回頭查 subconscious = 顯性 feedback loop

把四篇放在一起看的非顯然結論：**`PolicyInterceptor` 不是 WS-035 的新元件，是 heartbeat_learning.py 早該存在的 tier boundary。** 目前 distillate 一被生成就一路流到 retrieval，中間沒有任何 boundary 可以掛 governance。OCL 的 4 個 control outcome（Approve/Revise/Block/Escalate）可以直接對應到「distillate 寫入時」的 4 個 gate：通過 / 修訂 / 阻擋 / 升級給人 review。

**對 Hermes 的具體意涵**：drift penalty 的「penalty 施加時機」其實是這個 writer/reader boundary 的下游問題。先有 boundary，才能問 penalty 是施加在 writer 端（不讓舊 distillate 寫入）、reader 端（檢索時降權）、還是 feedback 端（reader failure 觸發 writer 改寫）。三種 penalty 的成本與時效差異極大，但目前 Hermes 三種都沒地方掛。

**可行動下一步**

1. 把 `PolicyInterceptor` 重新定位為「distillate tier boundary」而非「tool-call interceptor」。在 `obsidian-vault/02-Areas/Hermes-Ops/` 開一份 `policy-interceptor-architecture-proposal.md`，列出 4 個 OCL 對應的 gate（Approve/Revise/Block/Escalate）要怎麼映射到 distillate 生命週期。
2. 短期（1-2 天）先實作最便宜的 gate：reader 端 retrieval time 的 `confidence` 欄位 threshold filter（低於某值 → 標記為 "stale candidate"，不阻擋 retrieval）。這個 gate 不需要 LLM，只需要結構化欄位——直接和 Theme 1 的 schema 提案連動。
3. 中期（1 週）評估 SAGE 的 reader-failure signal 機制：當某 distillate 在 N 次 retrieval 中 confidence 持續 < 0.3，把它送回 writer 端（distillate 改寫 trigger）。這需要 telemetry 收集，估算成本是讀寫放大 ~3-5x。

## Cross-Cutting Theme 3: 「Triggered, not eager」是 4 篇共識，但觸發信號必須**分層而非單一**（MemoryOS 的 heat score 是範本）

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory（recurrence）, 2026-06-09-memory-os-three-tier-hierarchical-memory（heat）, 2026-06-09-sage-self-evolving-graph-memory-engine（reader failure）, 2026-06-09-llm-agent-memory-governance-synthesis（task-type dynamic trigger）

**分析**

四篇都反對 eager LLM consolidation（RecMem 87% token 節省、MemoryOS 4.9 vs 13 LLM calls、Governed Memory fast-mode 850ms）。但**每篇只提出一個觸發信號**：
- RecMem: recurrence count（θcount ≥ 5）
- MemoryOS: heat score（visit × interaction × recency）
- SAGE: reader failure feedback
- Governance synthesis: task-type dynamic trigger

把四篇放在一起看的非顯然結論：**單一信號都會有 blind spot。** RecMem 的 recurrence 抓不到「重複但已過時」的內容（governance-synthesis Section 3.2 的失敗模式）。MemoryOS 的 heat score 抓不到「熱但錯」（高 visit 數但語意過時）。SAGE 的 reader failure 抓不到「沒人讀所以沒失敗信號」的冷 distillate（long-tail problem）。

**MemoryOS 的 heat score 是目前為止唯一的多因子組合（`α·N_visit + β·L_interaction + γ·R_recency`）**，但它仍缺了 recurrence 和 reader failure。Hermes 應該做的是**四個信號的加權組合**，而不是挑一個。

**對 Hermes 的具體意涵**：`heartbeat_learning.py` 的 drift penalty 設計不應該只挑一個信號實作。第一版就應該把四個信號（recurrence / heat / reader-failure / contradiction）都收進 telemetry 資料流，**即使前三個月只用 heat 一個**——其他三個先空跑收集資料，三個月後再決定加權。這個「先建資料流、後選演算法」的順序比先選演算法重要，因為記憶系統的 ground truth（哪些 distillate 真的過時了）只能事後觀察。

**可行動下一步**

1. 在 `heartbeat_learning.py` 新增 `distillate_telemetry` event log：每次 distillate 被生成、被檢索、被 feedback 時各記一筆。欄位：`event_type` / `distillate_id` / `timestamp` / `context_hash`。無 LLM 成本，append-only。
2. 三個月後用這批 telemetry 跑 offline analysis，計算 4 個候選信號的 precision/recall，**用資料決定** 4 個權重怎麼分配。
3. 在此之前不要實作任何會阻擋 distillate 寫入的 gate（只做 read-side filter）—— 阻擋寫入的成本（false positive 刪掉好知識）比 read-side 降權高 1 個數量級。

## 整體行動優先序

如果只能做一件事：**做 Theme 1 的 distillate schema 提案**。Theme 2 和 Theme 3 都需要結構化欄位才能運作，這是上游 blocker。

如果可以做兩件事：加上 Theme 3 的 telemetry event log（零 LLM 成本，純 I/O）。

Theme 2 的 writer/reader boundary 提案是架構性決策，需要先看 Theme 1 schema 上線後的實際形狀再 design，最快也要 Theme 1 完成後 1-2 週。

## 信心標示

**High** — 4 篇筆記全部 cross-validated，OCL 的量化（12%→96% valid success）和 Governed Memory 的 dual model 是已 production 部署的成果，不是純理論。Theme 1 的「結構/開放二元性是 governance 前提」在 5 個系統中重複出現（4 篇筆記 + 隱性第 5 例 SCM 在 governance-synthesis 提及），信號極強。
