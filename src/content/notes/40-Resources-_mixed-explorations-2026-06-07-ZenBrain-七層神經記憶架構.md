---
_slug: 40-Resources-_mixed-explorations-2026-06-07-ZenBrain-七層神經記憶架構
_vault_path: 40-Resources/_mixed/explorations/2026-06-07-ZenBrain-七層神經記憶架構.md
title: ZenBrain：七層神經記憶架構
date: 2026-06-07
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- arxiv
- core
- decay
- episodic
- layer
- procedural
- sleep
- stability
- working
- zenbrain
created: '2026-06-07'
updated: '2026-06-15'
status: budding
---

# ZenBrain：七層神經記憶架構

**日期**: 2026-06-07 | **來源**: arxiv:2604.23878v2 | **類型**: SPIKE

## Per-Source Insight

### ZenBrain (arxiv:2604.23878v2)

**核心貢獻**：15 個神經科學機制整合於單一 MemoryCoordinator，覆蓋 7 層記憶架構（working/short-term/episodic/semantic/procedural/core/cross-context）。

**架構**：
- 7 層：working (Miller 7-item cap) → short-term (session-bounded) → episodic (timestamped events) → semantic (KG with Two-Factor Synaptic edges) → procedural (tool-use patterns) → core (persistent identity, no decay) → cross-context (entity resolution, privacy-aware)
- MemoryCoordinator 統一調度：store/recall/consolidate/decay/review

**15 個機制（9 基礎演算法 + 6 預測記憶架構）**：
1. Two-Factor Synaptic KG edges — Fisher Information proxy 使成熟 edge 抵抗 catastrophic forgetting（數學上等價於 EWC）
2. vmPFC-coupled FSRS — FSRS interval scheduling 耦合 KG-derived prediction-error signal (PE=1−cos(c_prev,c_now))，情緒轉換時縮短間隔、穩定時延長
3. Simulation-Selection Sleep Loop — CA3 simulator 生成候選（真實 эпизод + 反事實），CA1 selector 用 RL TAG(e)=α|δ_TD|+βR_e+γN_e 評分
4. Bayesian Confidence Propagation — 每個 fact 攜帶 P(f) 含 95% CI，更新透過 KG edge 傳播，情緒增強初始權重
5. Query-Aware Cross-Layer Retrieval — regex 分類查詢類型（temporal/procedural/factual/general），層別分數融合
6. NeuromodulatorEngine — 雙向反饋驅動編碼
7. ReconsolidationEngine — 記憶再鞏固
8. TripleCopyMemory — 30 天後 S(t)=0.912
9. PriorityMap — 優先級映射
10. StabilityProtector — 穩定性保護
11. MetacognitiveMonitor — 元認知監控

**關鍵數據**：
- LongMemEval-500：ZenBrain 47.7% vs oracle 52.2%（1/106 token cost）
- LoCoMo multi-layer routing：+20.7% F1 vs flat single-layer
- Sleep consolidation：+37% stability + 47.4% storage reduction (p≤5.1×10⁻³)
- Stress ablation（decay 0.25/day, 60 天）：9/15 機制成為 individually critical（ΔQ up to −93.7%）
- NoDecay counterfactual：ΔP@5=0.002（p=0.043）— principled forgetting 代價極小

**對比其他系統**（Table 1）：MemGPT 3 層（無神經科學基礎）、Mem0/A-Mem/Zep 1 層、LightMem/MemoryOS/Tiwari '26 3 層。ZenBrain 是唯一覆蓋全部 8 個特徵（7 層 + 神經科學基礎 + principled decay + sleep consolidation + spaced repetition + confidence + temporal + neuromodulation + reconsolidation）的系統。

**限制**：LoCoMo 的 substring-based F1 天然偏好 BM25（ZenBrain 不爭議）；無 full-context consolidation 比較；Judge 用 LLM-as-Judge（單一 human rater n=50 spot-check）。

## Hermes 啟發

1. **Core Memory 作為 never-decay 層**：ZenBrain 的 core layer（identity facts, never decay）對應 Hermes 的 pinned memory pattern。但 Hermes 目前無分層架構，所有 memory 混在同一層。WS-035 提案若要實作分層，Core/Working/Episodic 三層切割是 minimum viable design。

2. **TripleCopyMemory 的數字直接可用**：S(t)=0.912 at 30 days 給了具體 target。heartbeat_learning.py 若要做 retention stability，三拷貝策略值得評估。

3. **vmPFC-coupled FSRS 的 PE signal**：Prediction-error coupling 是連接情緒/上下文變化與記憶衰減率的具體機制。目前 Hermes 無 explicit confidence_valid_until，PE signal 機制填補這個缺口。

4. **Stress ablation 揭示 cooperative survival network**：9/15 機制在 stress 條件下才 critical。對 WS-035 意味：正常條件下模組化架構看起來冗餘，但刪除任一關鍵模組會在 high-load 情境導致突變。這支持「架構完整性 > 精簡最優化」的設計原則。

5. **NoDecay ΔP@5=0.002 的實踐意涵**：principled forgetting 代價極小（statistically significant but practically negligible）。對 heartbeat_learning.py 的 drift penalty 設計：decay 機制不需要 aggressive，mild decay 足以維持新舊資訊的區分度。

## 跨文章 Synthesis

ZenBrain 的 7 層 taxonomy 與 YantrikDB 的 5 層索引（HNSW+graph+temporal+decay+KV）趨同，但 ZenBrain 明確將層別對應到認知科學建構（working=Atkinson-Shiffrin, episodic=Tulving, procedural=Cohen-Squire）。兩者都確認：純 embedding 檢索不足，結構化分層是必要條件而非錦上添花。

TripleCopyMemory（S(t)=0.912 at 30d）+ Simulation-Selection Sleep Loop（+37% stability）的具體數字，填補了 YantrikDB 只給架構沒有數字的空白。可直接做為 WS-035 retention stability objective 的量化 calibration target。

## 未追蹤 Leads

- https://arxiv.org/html/2605.18421 (EvoMemBench)
- https://www.microsoft.com/en-us/research/publication/memgym-a-long-horizon-memory-environment-for-llm-agents/ (MemGym)
- https://spoonai.me/posts/2026-02-arxiv-2604-23878-zenbrain-en (ZenBrain blog, 500 error → fallback to arxiv HTML)

## ✅ 本次探索完成
