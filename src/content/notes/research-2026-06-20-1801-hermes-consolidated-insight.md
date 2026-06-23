---
_slug: research-2026-06-20-1801-hermes-consolidated-insight
_vault_path: research/2026-06-20-1801-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- agent-memory
- memory-architecture
source: multi
created: '2026-06-20'
confidence: high
title: 2026 記憶系統的兩條隱含主線：Reader-Driven Writer + Token Economics 作為架構約束
type: research
status: seedling
updated: '2026-06-23'
---

# 2026 記憶系統的兩條隱含主線：Reader-Driven Writer + Token Economics 作為架構約束

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

把 4 篇關於 LLM agent 記憶系統的探索筆記（H-MEM、RecMem、MemoryOS、SAGE + Governance synthesis）放在一起，會浮現兩條單篇自己沒明說、但跨篇彼此共鳴的主線。

## Cross-Cutting Theme 1: Reader-Signal-Driven Writer 是 2026 記憶系統的隱含共同架構原則

**支援筆記**: 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-llm-agent-memory-governance-synthesis

**信心**: high（5+ 次跨篇引用，5 個獨立來源）

四篇筆記各自呈現不同術語的同一個 pattern：**writer（寫入/蒸餾/consolidation 觸發）不再自主決定，而是被 reader（檢索/查詢/使用）的信號驅動**。

- **SAGE** 最 explicit：writer-reader self-evolution loop，reader 的 retrieval failure 直接回饋給 writer 作為改進目標。
- **RecMem** 的 recurrence-triggered consolidation：subconscious store 的 unit 只有在被 reader query 命中到 θcount 次以上時才被 promote 到 episodic layer — 寫入完全由 reader 的 query pattern 決定。
- **MemoryOS** 的 heat-based eviction：visit count (N_visit)、interaction length、recency 三維組成的 heat score，**本質是 reader 使用統計**；writer（MTM→LPM promotion）完全由這個 reader 統計觸發。
- **H-MEM** 的 user feedback 機制：approval → strengthen weight、rebuttal → decay — user 是終極 reader，writer 聽 reader 的判決。
- **Governed Memory** 的 reflection-bounded retrieval：LLM judge 評估 evidence completeness，若 incomplete 就 generate follow-up query — reader 的「資訊不足」信號直接驅動 writer 生成新查詢。

這個 pattern 的深層意涵：**2026 的記憶系統不再是「存進去就有用」，而是「被讀過才算存在」**。單篇筆記各自把這講成 consolidation trigger、eviction policy、self-evolution，但跨篇看就是同一件事：write-after-read。

**可行動下一步**：

1. 把 heartbeat_learning.py 的 distillate writer 改造成 reader-driven：目前 distillate 一旦寫入就直接進長期記憶，缺少「這個 distillate 是否曾被 task context 命中」的計數器。具體：在每個 distillate 上加 `hit_count` 和 `last_hit_timestamp` 欄位，writer 的 promotion 條件從「confidence > threshold」改為「confidence > threshold AND hit_count ≥ 1 OR age > X」（雙軌：受 reader 認可的快速 promote，無人聞問的走時間衰減）。
2. 在 distillate metadata schema（`~/obsidian-vault/` 的 YAML frontmatter）加 `reader_signals` 區塊：`hits`, `contradictions`, `rebuttals`，把讀寫閉環的狀態變成可觀測的。
3. 對應到 SAGE 的 self-evolution rounds：定義「reader failure → writer action」的具體協議，例如：若某 distillate 在 14 天內 hit_count=0 且無 contradiction，自動標記 `stale_candidate`；累積到 N 個 stale_candidate 就 trigger 一次「consolidation round」檢查是否需要重寫或合併。

## Cross-Cutting Theme 2: Token Economics 是架構選擇的 first-order constraint，不是 best-effort optimization

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

**信心**: high（5+ 次跨篇引用，所有 4 篇都把 token 量化結果列為 design validation 的核心證據）

每篇筆記都用了顯著的篇幅報告 token cost，並把這個數字當作架構合理性的論證依據：

- **RecMem**: 87% token reduction vs Mem0/A-Mem/MemoryOS — 這是論文的 headline。
- **MemoryOS**: 3,874 tokens/query 對比 MemGPT 的 16,977 — 77% 節省，作為設計驗證的核心數字。
- **H-MEM**: 整個四層 hierarchical index 的存在理由就是「flat O(a·10^6·D) → hierarchical O((a+k·300)·D)」的指數 vs 線性差距 — 沒提 token 數但 latency growth curve 是 token cost 的 proxy。
- **SAGE**: reflection-bounded retrieval 的 bounded rounds 直接防止 unbounded LLM calls；policy-based writing 避免「每個 turn 都觸發寫入」。
- **Governed Memory**: progressive context delivery 50% token reduction；fast mode (~850ms) vs full mode (2-55s) 的 tiered routing 就是 token-aware architecture。

把這 5 個觀察放在一起會發現：**2026 記憶系統的所有架構決策（hierarchical routing、recurrence trigger、heat-based eviction、bounded reflection、progressive delivery）都可以追溯到「降低每次 retrieval/consolidation 的 token cost」這個 first-order 約束**。單篇各自講成「效率提升」，但跨篇看是同一件事的 5 種表達。

更深的洞察：**token cost 不是副作用，是 design driver**。MemoryOS 的 STM 固定 7 pages、RecMem 的 subconscious 不做 LLM consolidation、H-MEM 的 4 層是 ablation 確認的最優點（再多會增加 routing overhead，更少會退化成 flat）——這些「magic numbers」全都是 token economics 壓出來的局部最優。

**可行動下一步**：

1. 對 `heartbeat_learning.py` 做 token cost audit：log 每個 distillate 寫入時消耗的 input+output tokens、每次 retrieval 時 distillate context 注入的 token 數。建立 `~/obsidian-vault/04-Archives/hermes-token-economics-2026-06.md` 追蹤月度趨勢。
2. 在 WS-035 drift penalty 的 spec 裡加 token 預算欄位：`max_distillate_tokens_per_session = N`（預設值待 audit 後決定）。當 session 累積 distillate 超過預算，自動觸發 consolidation（不是 retention failure 才 trigger，而是 budget 壓力 trigger）。
3. 借鑒 MemoryOS 的 tiered routing：對 distillate 設計 fast/full 兩種 retrieval mode — fast 用 embedding similarity 不調 LLM（~本地 ms 級），full 才用 LLM judge（bounded rounds）。把 OCL 的 governance routing 從 execution layer 移植到 memory retrieval layer。

## Cross-Cutting Theme 3 (medium): 「事件驅動 vs 時間驅動」的隱含辯論 — 但收斂在「兩者並用，但事件優先」

**支援筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-llm-agent-memory-governance-synthesis

**信心**: medium（3 篇觸及但角度不同，沒有一篇明確做 trade-off 比較）

這是 Theme 1 的時序維度切片：

- **RecMem**: 純事件驅動（recurrence count），完全不用時間衰減。
- **MemoryOS**: 時間 + 事件並用（recency 衰減 + visit count），但 recency 是 heat score 的一個 component，不是獨立 trigger。
- **H-MEM**: 純事件驅動（user rebuttal → decay），論文沒討論 time-based decay。
- **Governance synthesis (Source 1)**: 明確點出「uniform time decay 失效模式 — 過時的知識在沒有明顯跡象下失效」。

單篇各自把這當副產品講，但跨篇看這是 2026 記憶系統的一個未解的 design tension：**時間衰減簡單但誤殺，事件觸發精準但 cold-start 期間所有東西都沒信號**。MemoryOS 的「兩者並用」可能是實務妥協而非理論最優。

**可行動下一步**：

在 heartbeat_learning.py 實作 dual-decay：
```
effective_confidence = base_confidence 
                       × recency_decay(t_now - last_hit, half_life=38d)
                       × event_modifier
```
其中 `event_modifier`：hit_count > 0 → ×1.2、contradiction detected → ×0.5、user rebuttal → ×0.1。這個公式讓 cold-start 期間靠時間衰減保守淘汰，系統成熟後靠事件信號精準淘汰。對應到 Hermes 的蒸餾生命週期管理，需要先在 `~/obsidian-vault/` 找一個現有 distillate schema 加這三個欄位。

## 給 Hermes/Talos 的整合性下一步

把 Theme 1 + Theme 2 結合，得到一個 actionable 的系統級提案：

**「Reader-driven, token-budgeted distillate lifecycle」**

把 heartbeat_learning.py 的 distillate 從「寫入後靜默存在」改為：
- **寫入時**：標記 token_cost（這個 distillate 引入的 context overhead）
- **每次檢索時**：更新 hit_count、last_hit_timestamp、回報 reader_signal（success/contradiction/insufficient）
- **每個 session 結束時**：計算 session 的 distillate token 總和，若超過 budget → trigger 一次「consolidation round」（不是 retention failure 觸發，是 budget 壓力觸發）
- **每 14 天**：跑一次 self-evolution round，把 hit_count=0 且無 contradiction 的 distillate 標記 stale_candidate，累積到閾值就合併或淘汰

這個提案對應的 code change 集中在三個檔案：`heartbeat_learning.py`（writer 邏輯）、新增 `distillate_reader_signals.py`（reader 回報）、`session_token_budget.py`（預算追蹤）。預估工作量：1-2 天 prototype，1 週 production-ready。

對應的參考實作：SAGE 的 writer-reader loop 是最完整的 blueprint，MemoryOS 的 heat score 是最容易移植的 metric，RecMem 的 θcount/θsim threshold 設定是最直接的 default 值來源。
