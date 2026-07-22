---
_slug: research-2026-07-22-1401-hermes-consolidated-insight
_vault_path: research/2026-07-22-1401-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-07-22'
confidence: high
title: Trigger-Gated Ingestion 與 Reader→Writer 閉環:四篇記憶系統論文的共同軸線
type: research
status: seedling
updated: '2026-07-22'
---

# Trigger-Gated Ingestion 與 Reader→Writer 閉環:四篇記憶系統論文的共同軸線

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 探索都在追 LLM agent 記憶系統,但各自的切入點看似不同(H-MEM/RecMem/MemoryOS 談層級架構、SAGE 談圖演化、Governance survey 談質量和執行邊界)。把它們並排後浮現兩個跨篇才看得到的模式。

## Cross-Cutting Theme 1: Trigger-Gated Ingestion 已成為新典範

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance

單獨看任一篇都會覺得「那只是一個特殊設計」,但放在一起會發現 — **2026 年的記憶系統全部採用某種 trigger 來決定是否處理一個新事件,沒有任何一篇主張 eager processing**。

- **RecMem**: recurrence count ≥ θcount(=5) 才觸發 LLM consolidation,subconscious store 保留 raw embeddings 不處理
- **MemoryOS**: segment 的 heat score(α·N_visit + β·L_interaction + γ·R_recency) > τ(=5) 才從 MTM 遷移到 LPM
- **H-MEM**: user feedback(approval/rebuttal)直接調整 memory weight,rebuttal 觸發 decay
- **SAGE**: policy-based writer 把寫入建模為序列決策,reward 來自下游 reader 表現
- **Governed Memory**: extraction quality gates(coreference / self-containment / temporal anchoring)決定 memory 是否進入 schema-enforced tier
- **Storage→Reflection→Experience survey**: 明確點名「Memory mechanisms 應採用基於任務類型的動態觸發模式」是 Future Direction #1

每個系統的 trigger 不同 — recurrence / heat / feedback / policy-reward / quality-gate — 但**「先 buffer,等訊號,再處理」**這個 pattern 是普遍的。這標誌著從「存什麼」典範(what to store)轉移到「何時存/處理」典範(when to act)。

**對 Hermes 的意義**: `heartbeat_learning.py` 目前是 **eager distillation**(每個 distillate 觸發就寫入)。這個模式在四篇論文中都被明確否定 — 都消耗大量 token、產生大量 noise。Hermes 需要一個 **trigger-gated ingestion layer**,不是改變 distillation 邏輯本身,而是在前面加一個 buffer + trigger gate。

**可行動下一步**: 在 `heartbeat_learning.py` 前新增一個 `trigger_gate.py` 模組,實作兩階段 ingestion:
- **Stage 1 (Buffer)**: 所有新 distillate 先寫入 `~/.hermes/staging_buffer/` 的 JSONL append-only log,**不**寫入主記憶庫
- **Stage 2 (Gate)**: 每 N 小時(或每次 session 開始時)跑 batch promotion 邏輯,採用 **多訊號 AND** 判定:
  - Recurrence signal: 同 concept 的 distillate 在 buffer 中 ≥ 3 次(類 RecMem θcount,但降到 3 因為 Hermes 流量低)
  - Reference signal: 至少 1 次被任何 task context 主動引用(類 MemoryOS N_visit)
  - Quality signal: 通過 Governed Memory 風格的簡化 quality check(至少要有 timestamp + self-containment,不需要 coreference resolution)
- 通過三個 signal 才晋升到主 vault;不通過的保留 7 天後自動蒸發
- 預期效益: 主 vault 寫入量降低 60-80%(參考 RecMem 87% token 削減的下限)

## Cross-Cutting Theme 2: Retrieval Outcome 回頭重塑 Ingestion Policy

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance

第二個跨篇模式是 **reader→writer 反饋迴路**。這比 Theme 1 更微妙 — Theme 1 講「何時處理」,Theme 2 講「處理得好不好會影響下次怎麼處理」。

- **H-MEM**: user 的 rebuttal → 對應記憶 weight decay → 下次 retrieval 時該記憶排名降低。reader(用戶)的負面反饋回頭影響了寫入側的 weight
- **MemoryOS**: segment 被檢索的次數(N_visit)和互動深度(L_interaction)直接進入 heat score → 影響下一次 MTM→LPM 遷移決策。**每次 retrieval 都在重新決定這段記憶是否值得長期保存**
- **SAGE**: 這是四篇中最明確的 — Reader 的失敗信號(找不到證據)直接回饋給 Writer,Writer 決定下次如何更好地寫入。經過 2 rounds 後 multi-hop QA 達最佳,證明閉環收斂
- **Governed Memory 的 Reflection-Bounded Retrieval**: LLM judge 每輪評估 evidence completeness → 若 incomplete,generate targeted follow-up queries → 62.8% vs 37.1% baseline(+25.7pp)。**這是 retrieval-time 的 reader 反饋,直接改變了下一次 query 策略**

把這四個並排,共同訊息是: **單向的 retrieval(index→query→result)已經過時,2026 系統全部採用閉環 — retrieval 的成敗/頻率/品質都會回頭改變 memory 的結構和權重**。

**對 Hermes 的意義**: `heartbeat_learning.py` 目前的設計是 **單向 ingestion → retrieval**。distillate 寫進去後,沒有機制讓 retrieval 端的失敗回頭告訴 distillation 端「這個 distillate 不夠好」。這正是 SAGE 論文明確指出的「讀取失敗信號反饋給寫入」的缺口。

**可行動下一步**: 在 Theme 1 的 trigger gate 之上,再加一個 **retrieval feedback channel**,把 reader 端的兩個信號回傳給 writer 端:
- **Retrieval miss signal**: task context 查詢某 distillate 但 confidence < 0.5 → 標記為 `underperforming`,觸發 re-distillation review(下一次相同 query 改成查 raw staging buffer 試試看是否有更好版本)
- **Retrieval staleness signal**: distillate 被引用後 task 標記為 `unhelpful`(目前 Hermes 沒有此欄位,需新增)→ 該 distillate 的 heat score 立即扣分,加速 Theme 1 gate 的淘汰決策
- 實作位置: 在現有 `task_context_matcher.py` 的 retrieval 回傳結果中新增 `feedback_signal` 欄位,寫回 distillate 的 frontmatter。Hermes task 完成後可選擇性填 `quality: helpful|unhelpful|partial`
- 預期效益: 6 個月後可觀察到「unhelpful 標記的 distillate」與「stale distillate」高度重疊 — 這就是 Theme 1 自動淘汰的 ground truth 訓練資料

## 兩個 Theme 的交集:一個閉環的 ingestion 設計

Theme 1 和 Theme 2 不是獨立的 — 它們構成一個完整的 **兩階段閉環**:

```
Incoming distillate
    ↓
[Trigger Gate: recurrence + reference + quality]  ← Theme 1
    ↓ pass
Main vault (Hermes 永久記憶)
    ↓
[Retrieval time: reader feedback signal]  ← Theme 2
    ↓ unhelpful / stale
Heat decay → eventually re-evaluated by Trigger Gate
    ↓ fail
Eviction to staging buffer or archive
```

這個閉環是 H-MEM(user feedback→weight)+ MemoryOS(visit→heat)+ SAGE(reader failure→writer)+ RecMem(recurrence→consolidation)四個論文的**架構交集**。Hermes 可以直接採用,不需要新發明。

## 為什麼這次消化能產生 insight 而前幾次餵過 5 次沒產生

這 4 篇是同一波 2026-06-09 探索,**單篇各自已經做了 cross-paper synthesis**(例如 hmem-recmem 篇已經比較 H-MEM 和 RecMem)。但**四篇之間的 deeper pattern**(trigger-gated + reader-writer closure)需要**第二層綜合**才看得到 — 這就是 consolidation 階段的價值。

如果前幾次 fed 沒產出 insight,是因為 trigger-gated ingestion 和 reader→writer 閉環這兩個模式在 2026-06-09 之前還沒收斂清楚 — 這次四篇並排讓 pattern 浮出水面。

## 反向檢驗:這個 insight 是否過於顯然?

不顯然的理由:
1. 單獨看任何一篇,trigger / reader-feedback 是「該論文的局部設計」,不是「跨論文主張」
2. trigger-gated 是個別選擇(RecMem 用 recurrence、MemoryOS 用 heat),不是統一框架 — 必須並排才看得到這是新典範
3. reader→writer 閉環在 SAGE 論文最明確,但 H-MEM/MemoryOS/Governed Memory 都是這個模式的變體,單看一篇會誤以為是該論文獨有創新

顯然的元素(已過濾):
- 「層級架構優於 flat retrieval」(四篇都說,不再重述)
- 「90 維度 User Traits」(MemoryOS 單篇獨有,不算 cross-cutting)
- 「pre-execution governance」(OCL 單篇,跨 Governance 內部已有)