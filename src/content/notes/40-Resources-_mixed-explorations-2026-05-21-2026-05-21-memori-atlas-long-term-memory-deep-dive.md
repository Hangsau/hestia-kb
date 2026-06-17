---
_slug: 40-Resources-_mixed-explorations-2026-05-21-2026-05-21-memori-atlas-long-term-memory-deep-dive
_vault_path: 40-Resources/_mixed/explorations/2026-05-21-2026-05-21-memori-atlas-long-term-memory-deep-dive.md
title: 2026-05-21-memori-atlas-long-term-memory-deep-dive
date: 2026-05-21
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- arxiv
- atlas
- context
- distill
- memori
- memory
- summaries
- token
- tokens
- triple
created: '2026-05-21'
updated: '2026-06-15'
status: budding
---

**時間**: 2026-05-21T03:15 CST
**Token cost**: 低（2次 arXiv HTML fetch）
**品質**: 高 — Memori 完整論文含架構圖和 benchmark data，ATLAS 有數學推導和 10M context 實驗
**價值**: 直接影響 heartbeat_learning 的 rubric upgrade + Memori 的 triple extraction 是可実装的方向

**延續自**: [[2026-05-21-memori-production-memory-engine]]

---

## Per-Source Insights

### Memori (arXiv:2603.19935)

**核心主張**: 記憶是「資料結構化問題」而非「儲存問題」。

Advanced Augmentation pipeline:
1. **Semantic Triple Extraction**: 把對話切成 `(subject-predicate-object)` 三元組。每個 triple 鏈回原始 conversation。這是高壓縮 + 高精確度的關鍵。
2. **Conversation Summaries**: 同時產生對話層級摘要。Triple 綁定 summary → 孤立事實永遠有背景敘事。

記憶表示 = 雙層互連結構：Triples（精確事實） + Summaries（時間軸敘事）。比直接存 raw text 好是因為：
- Triples 產生 low-noise, high-signal index → 改善 vector search 精確度
- 本身就是 compression layer → 1,294 tokens vs 26,031 full-context

**Benchmark 結果** (LoCoMo):
- 81.95% overall，擊敗 Zep(79.09)、LangMem(78.05)、Mem0(62.47)
- Single-hop: 87.87%（最好）
- Temporal: 80.37%（落後 LangMem 86.92、Zep 83.33）
- Multi-hop: 72.70%
- Open-domain: 63.54%（最差）

**Token 效率**:
- Memori: 1,294 tokens (~5% context)
- Zep: 3,911 tokens
- Full-context: 26,031 tokens
- Mem0: 1,764 tokens

**對 Hermes 的啟發**: Memori 的「Triple + Summary」模型可以直接借鑒：
- 「triples」= Hermes 的 `memory-consolidator` distill 出的事實片段
- 「summaries」= 對話層級的 context outline
- 關鍵差距：Hermes 目前是破壞性 distill（原文丟），Memori 維持「expand-on-demand」能力（壓縮存在 external store，需要時召回）

### ATLAS (arXiv:2505.23735)

**核心主張**: 現有 RNN-based 模型（三個缺點）：
1. Online nature — 只根據當前 token 優化記憶，不考慮過去上下文
2. 記憶容量受限 — architecture 限制 mappable KV pairs
3. 記憶表達不足 — gradient descent 只用一階資訊，容易收斂到 spurious local minima

**解決方案**: Atlas — offline optimization of memory based on current + past tokens → 克服 online nature。結合 Newton-Schulz 5 optimizer。

**Key insight**: 記憶容量 O(d_k^p)（d_k=key dimension，p=polynomial degree）。這解釋了為什麼簡單 linear attention 容量受限——需要 nonlinear feature mapping 才能擴展。

**驚人結果**: 10M context BABILong benchmark → +80% accuracy over Titans baseline。純架構創新，無需 external memory。

**對 Hermes 的啟發**:
- Atlas 的「learning-to-memorize」概念比 vault_decay 的單純 time-decay 更有深度
- 「online vs offline optimization」區分剛好對應：短程對話用 online（快速 distill），長程記憶用 offline 重新整合
- 數學 framework（O(d_k^p) 容量）給了 vault_decay 的 scoring 演算法一個理論基礎

---

## Cross-Paper Synthesis

Memori 和 ATLAS 從兩個維度解決同一個問題：

| 維度 | Memori | ATLAS |
|------|--------|-------|
| 記憶表示 | Semantic triples + summaries | Associative memory (MLP) |
| 容量擴展 | Structured representations | Polynomial feature maps O(d_k^p) |
| 時間推理 | Conversation summaries | Offline optimization |
| Token 效率 | 1,294 tokens (~5%) | Architecture-level, no extra tokens |
| 適用場景 | API-layer LLM agents | Transformer/RNN architecture |

**合起來看**: Hermes 的 memory pipeline 可以分層：
- **Short-term**: ATLAS-style 的「learning-to-memorize」— 每個 session 學習哪些 context 值得存
- **Long-term**: Memori-style 的「structured representations」— 從 distillation 直接生成 semantic triples，summaries 維護時間軸

目前的 `memory-auto-distill` 只有長程（distill 後拋棄原文）。如果加入 Memori 的「expand-on-demand」概念（原文存在 `context_cache/`），就能同時滿足：token 效率（distill 壓縮）+ 召回能力（expand-on-demand）。

---

## 未追蹤 leads

- https://arxiv.org/abs/2402.17753 — LoCoMo dataset paper (Memori 的 benchmark)
- https://arxiv.org/abs/2512.20237 — MemR3: memory retrieval via reflective reasoning
- https://github.com/MemoriLabs/Memori — Memori official code

## ✅ 本次探索完成
