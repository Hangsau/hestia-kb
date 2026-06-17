---
_slug: 40-Resources-_mixed-explorations-2026-06-08-MemTier--Tiered-Memory-Architecture--2026-06-08
_vault_path: 40-Resources/_mixed/explorations/2026-06-08-MemTier--Tiered-Memory-Architecture--2026-06-08.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 15:\n    title: MemTier: Tiered Memory Architecture (20 ... \n     \
  \             ^"
_raw_fm: '

  title: MemTier: Tiered Memory Architecture (2026-06-08)

  date: 2026-06-08

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [acc, architecture, invariance, memtier, multi, retrieval, semantic,
  session, signals, tier]

  created: 2026-06-08

  updated: 2026-06-15

  status: active

  '
title: 'MemTier: Tiered Memory Architecture (2026-06-08)'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# MemTier: Tiered Memory Architecture (2026-06-08)

**來源**: arxiv:2605.03675v2 | Sidik & Rokach, Ben-Gurion University

## 核心發現

### 1. 三層不變性 — 架構瓶頸在 retrieval 而非 generation

三個維度的 ablation 全都顯示：不變。
- **Generator invariance**: DeepSeek-V4-Flash (284B MoE) vs Qwen2.5-7B → Acc 重疊 CI，無顯著差異
- **Weight invariance**: PPO-learned weights vs default → Acc 完全相同（0.382）
- **Score normalisation invariance**: log/min-max/zz-score 全都 → Acc=0.320（identical）

結論：linear BM25 retrieval architecture 是綁定約束。更好的 model 和更好的 weights 在 retrieval 架構無法找到 multi-session evidence 時都無法提升 accuracy。

### 2. Retrieval 是瓶頸（Oracle analysis）

- Oracle（金牌 sessions 直接 inject）→ Acc=0.550 vs 系統 0.350（gap +0.200）
- Recall@2 = 0.390（整體），但 multi-session 只有 0.038（96% 的 multi-session 問題在 top-2 找不到答案）
- 7B reader 不是上限：給正確 context 可達 0.550

→ 改善 reader 無用。要改善 retrieval。

### 3. Retrieval-limited regime 的量化邊界

BM25 raw score 對其他 bounded signals（decay, CW, tier boost）的 dominate 是 5-10x，導致 bounded signals 增加 noise 而非 signal。

即使 PPO 成功調整 weights（w_bm25: 0.350→0.374, w_tier: 0.150→0.183），最終 ranking 完全不變。

### 4. 最佳 k=2（邊緣硬體）

k=2 勝過 k=4（Acc: 0.402 vs 0.382, Δ+0.022）。k=8 部分恢復（0.394），非單調關係。

600 tokens budget 勝過 300（Acc 0.412）。

### 5. Semantic pre-population 是 dominant contributor

移除 semantic tier → Acc -0.128，F1 降 2.9x。

LLM-extracted facts (~3.1/question) 勝過 heuristic (~509/question) → F1 +2.9x，164x token reduction。

### 6. 架構組件貢獻 Hierarchy

1. Semantic pre-population: -0.128（最大）
2. Two-stage scoping: -0.038（第二）
3. Individual signals（time decay, CW, tier boost）: 各自輕微負貢獻（+0.012~+0.014）→ BM25 dominance 稀釋了 bounded signals

### 7. Dense/hybrid 修復 category-specific gap

D2 Hybrid RRF vs BM25-only:
- Multi-session: +0.077（最大受益類別）
- Temporal: +0.037
- Knowledge update: -0.125（BM25 lexical precision 更好）

## Hermes 啟發

1. **WS-035 drift penalty 方向確認**: MemTier 的 CW attribution loop（tool outcome → CW update）是 drift penalty 的具體參考。CW 從 {-0.5, 0, +1} tool-outcome rewards 更新，而非時間衰減。與 heartbeat_learning.py 的 distillate stability 不同——CW 是 explicit success/failure signal，drift penalty 應該是 semantic contradiction detection 而非 uniform decay。

2. **Retrieval bottleneck = architecture ceiling**: 純 embedding retrieval（如 Mem0）也有同樣問題——BM25 lexical ceiling 在 multi-session 場景無效。結構化記憶 > 純嵌入共識再次確認。

3. **k=2 實用建議**: 邊緣部署建議 k=2，避免噪聲 entry 稀释 7B generator。

## 未追蹤 leads
- MemGPT（interrupt-driven paging）vs MemTier（async daemon-driven）架構對比
- ProMem（larger scale model accuracy maximisation）evaluation
- AgentWarden (RL-based governance) — arxiv:2604.12177v1 對應 PhantomPolicy Sentinel

## ✅ 本次探索完成


## Version 2 — 2026-06-08

# MemTier: Tiered Memory Architecture (2026-06-08)

**來源**: arxiv:2605.03675v2 | Sidik & Rokach, Ben-Gurion University

## 核心發現

### 1. 三層不變性 — 架構瓶頸在 retrieval 而非 generation

三個維度的 ablation 全都顯示：不變。
- **Generator invariance**: DeepSeek-V4-Flash (284B MoE) vs Qwen2.5-7B → Acc 重疊 CI，無顯著差異
- **Weight invariance**: PPO-learned weights vs default → Acc 完全相同（0.382）
- **Score normalisation invariance**: log/min-max/zz-score 全都 → Acc=0.320（identical）

結論：linear BM25 retrieval architecture 是綁定約束。更好的 model 和更好的 weights 在 retrieval 架構無法找到 multi-session evidence 時都無法提升 accuracy。

### 2. Retrieval 是瓶頸（Oracle analysis）

- Oracle（金牌 sessions 直接 inject）→ Acc=0.550 vs 系統 0.350（gap +0.200）
- Recall@2 = 0.390（整體），但 multi-session 只有 0.038（96% 的 multi-session 問題在 top-2 找不到答案）
- 7B reader 不是上限：給正確 context 可達 0.550

→ 改善 reader 無用。要改善 retrieval。

### 3. Retrieval-limited regime 的量化邊界

BM25 raw score 對其他 bounded signals（decay, CW, tier boost）的 dominate 是 5-10x，導致 bounded signals 增加 noise 而非 signal。

即使 PPO 成功調整 weights（w_bm25: 0.350→0.374, w_tier: 0.150→0.183），最終 ranking 完全不變。

### 4. 最佳 k=2（邊緣硬體）

k=2 勝過 k=4（Acc: 0.402 vs 0.382, Δ+0.022）。k=8 部分恢復（0.394），非單調關係。

600 tokens budget 勝過 300（Acc 0.412）。

### 5. Semantic pre-population 是 dominant contributor

移除 semantic tier → Acc -0.128，F1 降 2.9x。

LLM-extracted facts (~3.1/question) 勝過 heuristic (~509/question) → F1 +2.9x，164x token reduction。

### 6. 架構組件貢獻 Hierarchy

1. Semantic pre-population: -0.128（最大）
2. Two-stage scoping: -0.038（第二）
3. Individual signals（time decay, CW, tier boost）: 各自輕微負貢獻（+0.012~+0.014）→ BM25 dominance 稀釋了 bounded signals

### 7. Dense/hybrid 修復 category-specific gap

D2 Hybrid RRF vs BM25-only:
- Multi-session: +0.077（最大受益類別）
- Temporal: +0.037
- Knowledge update: -0.125（BM25 lexical precision 更好）

## Hermes 啟發

1. **WS-035 drift penalty 方向確認**: MemTier 的 CW attribution loop（tool outcome → CW update）是 drift penalty 的具體參考。CW 從 {-0.5, 0, +1} tool-outcome rewards 更新，而非時間衰減。與 heartbeat_learning.py 的 distillate stability 不同——CW 是 explicit success/failure signal，drift penalty 應該是 semantic contradiction detection 而非 uniform decay。

2. **Retrieval bottleneck = architecture ceiling**: 純 embedding retrieval（如 Mem0）也有同樣問題——BM25 lexical ceiling 在 multi-session 場景無效。結構化記憶 > 純嵌入共識再次確認。

3. **k=2 實用建議**: 邊緣部署建議 k=2，避免噪聲 entry 稀释 7B generator。

## 未追蹤 leads
- MemGPT（interrupt-driven paging）vs MemTier（async daemon-driven）架構對比
- ProMem（larger scale model accuracy maximisation）evaluation
- AgentWarden (RL-based governance) — arxiv:2604.12177v1 對應 PhantomPolicy Sentinel

## ✅ 本次探索完成
