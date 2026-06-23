---
_slug: research-2026-06-16-0501-hermes-consolidated-insight
_vault_path: research/2026-06-16-0501-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- drift-penalty
- staleness-detection
source: multi
created: '2026-06-16'
confidence: high
title: Drift Detection 真正缺口：Reader-Writer Closed-Loop 與四信號 Staleness Ensemble
type: research
status: seedling
updated: '2026-06-23'
---

# Drift Detection 真正缺口：Reader-Writer Closed-Loop 與四信號 Staleness Ensemble

**消化筆記**: 
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 同日探索的 memory architecture 論文，表面各說各話（H-MEM 層級化、RecMem recurrence、MemoryOS heat、SAGE graph、Governed Memory schema）。但並排讀才浮現兩個跨論文都沒解的 pattern：每個系統都只覆蓋 staleness 偵測的單一子集，且**所有 prototype 等級的系統都缺少 reader→writer 的失效反饋閉環**。

## Cross-Cutting Theme 1: 四種 staleness 觸發機制互補但都只覆蓋一個子集

**支援筆記**: hmem-recmem (RecMem recurrence)、memory-os (heat score)、sage (reader failure signal)、llm-agent-memory-governance (contradiction detection)

把四篇放在一起才看出：每篇都宣稱 "we solved staleness"，但其實是**不同 facet 的偵測**：

| 系統 | Staleness 信號 | 偵測到什麼 | 漏掉什麼 |
|------|--------------|----------|---------|
| RecMem | recurrence count (θcount) | 重複 = 重要、不重複 = stale | 高頻但已過時的 fact（如舊 CTO 名字） |
| MemoryOS | heat = visit + interaction + recency | 冷 = stale | 從未被引用但正確的事實（如法規條文） |
| SAGE | reader failure signal | 找不到證據 = 圖中缺失 | reader 路徑錯誤但目標存在 |
| Governed Memory | contradiction detection (83.3%) | 顯式衝突 = stale | 隱式矛盾（不同 framing 同概念） |

**洞見**：WS-035 drift penalty 如果只挑其中一個機制，會在另一個 facet 失效。RecMem 會把「高頻的舊事實」視為 strong signal；MemoryOS 會誤殺冷知識；SAGE 的 reader failure 是最弱的信號（reader 路徑問題不等於 fact 過時）；contradiction detection 對隱性矛盾無感。

**真正解法是 ensemble**：staleness = `w1·(1-recurrence) + w2·(1-heat_normalized) + w3·contradiction_score + w4·reader_failure_count`，任一信號強烈觸發即標記 stale。這是四篇都隱含但沒任一篇拉出來講的 meta-pattern。

**信心**: high（四篇都明確提出自己的 staleness 機制，差異比對清晰）

**可行動下一步**:
1. 在 `~/hermes/heartbeat_learning.py` 開新檔 `staleness_ensemble.py`，定義 `compute_staleness(distillate) -> float`，權重預設 `w1=0.3, w2=0.3, w3=0.25, w4=0.15`（recurrence + heat 主導，contradiction + reader failure 補強）
2. 從現有 distillate store 撈 10 個真實樣本，計算四信號分布，確認權重是否需要 rebalance
3. 任一信號超過閾值（staleness > 0.7）→ 標記 `pending_invalidation` 而非直接刪除，等下次蒸餾時確認無新覆蓋版才真的 evict

## Cross-Cutting Theme 2: Prototype 級記憶系統共有的封閉式寫入盲點

**支援筆記**: hmem-recmem (writer 觸發條件)、memory-os (heat-based 更新)、sage (writer-reader self-evolution loop)、llm-agent-memory-governance (Storage→Reflection→Experience 框架)

單看任一篇會覺得 writer 邏輯很完整——RecMem 有 θcount + θsim、MemoryOS 有 heat threshold、H-MEM 有 user feedback、Governed Memory 有 quality gates。但並排才看到一個**所有 prototype 都犯的相同錯誤**：writer 的更新觸發都只看「內部信號」（recurrence、heat、feedback），不看「reader 的失敗」。

SAGE 是唯一例外，它明確建模 `Reader failure signal → Writer improvement target` 的閉環。但 SAGE 是 graph-based，跟 Hermes 的 distillate-based 架構不直接對應。

**洞見**：WS-035 目前的 drift penalty 是純 decay-based（time + contradiction），完全沒有 reader 端的觀察。也就是說，當某個 distillate 長期沒被 task context 引用時，沒有任何機制把「引用率 = 0」這個信號傳回 distillation trigger。系統永遠在被動接受新 distillate，主動淘汰舊的——這是 prototype 級的「write-only memory」。

**真正的 drift detection 需要閉環**：
```
[Reader: task context matching] 
  → 找不到證據 OR 命中率低
  → 發 signal 給 Writer: "distillate X 引用率 0，持續 Nd"
  → Writer 決定: stale-mark / re-distill / leave-alive
```

這是 SAGE 的 pattern 移植到 Hermes distillate 架構的具體化。

**信心**: high（四篇的 writer 設計都明確，缺點的共性是直接從表格對比浮現）

**可行動下一步**:
1. 在 `heartbeat_learning.py` 的 distillation 流程加 `reader_feedback_hook(distillate_id, hit_count, last_hit_at)`，每次 task context matching 結束時呼叫
2. `distillate` schema 增加欄位 `reader_stats: {hit_count, last_hit_at, miss_streak}`，預設初始化為 0/null
3. 定義 `is_stale_by_reader(d) = (d.miss_streak > 30 days) AND (d.hit_count < 3)`——低引用 + 長 miss streak 才標記，避免一次性的冷知識被誤殺
4. 設 daemon 每 7 天掃一次 reader_stats，觸發 stale-mark → 等下次 distillation 決定是否 re-distill

## Cross-Cutting Theme 3: Schema/Structure Enforcement 是 Production-Ready 的隱形分水嶺

**支援筆記**: hmem-recmem (H-MEM positional index)、memory-os (segment-paging + User Traits 90 維度)、sage (entity-relation triple graph)、llm-agent-memory-governance (dual open-set + schema-enforced + OCL two-tier)

這個 theme 比較 subtle：四篇都各自有「結構化」設計，但**沒有一篇把它列為 production-readiness 的關鍵**。並排才看出——LoCoMo SOTA 的系統（MemoryOS 1.0th、H-MEM Adversarial 63.3、Governed Memory 100% adversarial compliance）**全都**有顯式 schema/index/structure layer；而 A-Mem、MemoryBank 這些 prototype 級的系統是純 embedding + 自由 text。

**洞見**：對 Hermes 的意義是，distillate 不能是 free-form text，必須有 schema（fact_type, confidence, hit_count, last_hit_at, source 至少這五個欄位）。目前的 free-form distillate 是「A-Mem 等級」，升級到「MemoryOS 等級」的門檻就是 schema enforcement。

**信心**: medium（兩篇明確提出 schema、兩篇間接對應；不夠「非顯然」但仍是可執行 pattern）

**可行動下一步**:
1. 定義 `DistillateSchema` dataclass 在 `heartbeat_learning.py`：`{fact_type: Enum, confidence: float, hit_count: int, last_hit_at: ISO, source_uris: List[str], staleness_ensemble: float}`
2. 寫 migration script 將現有 free-form distillate 重新解析進 schema（用 LLM classification 填 fact_type，confidence 從現有 metadata 推）
3. 下游任何 consumer（task context matching、reflection note generation）都只接受 schema-compliant distillate，否則丟棄並 log

## 對 WS-035 Drift Penalty 的整合建議

把三個 theme 合起來，WS-035 不只是「drift penalty 公式」——它是個**有 schema、reader feedback、ensemble signal 的小系統**：

```
[Schema-enforced Distillate]
  ↓ (每次 reader match)
[Reader feedback hook 更新 hit_count/last_hit_at]
  ↓ (每 7 天)
[Staleness ensemble: 4 信號加權]
  ↓ (staleness > 0.7)
[Stale-mark → 等下次 distillation 確認]
  ↓
[Writer: 決定 re-distill / leave / evict]
```

這個閉環是四篇論文交叉出來的設計，不是任一篇的 1:1 移植。

## 未追蹤 Leads

- SCM (Self-Controlled Memory, Wang et al. 2025) — 已在 2026-06-09 memory-os note 標記未 fetch
- BEAM benchmark (100 sessions, 10M tokens) — Experience stage 量化框架，可作 WS-035 評估基準
- MemoryOS GitHub 開源實作 — `https://github.com/BAI-LAB/MemoryOS`，可參考 segment-paging 具體 code
