---
_slug: 40-Resources-_mixed-explorations-2026-05-28-2026-05-28---MEMO--Memory-as-a-Model
_vault_path: 40-Resources/_mixed/explorations/2026-05-28-2026-05-28---MEMO--Memory-as-a-Model.md
title: '2026-05-28 — MEMO: Memory as a Model'
date: 2026-05-28
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- corpus
- cross
- document
- hermes
- memo
- memori
- memory
- model
- session
- synthesis
created: '2026-05-28'
updated: '2026-06-15'
status: budding
---

# 2026-05-28 — MEMO: Memory as a Model

**延續自**: [[2026-05-28-2026-05-28---Memori-Agent-Native-Memory-Implementation]]

**日期**: 2026-05-28

## Per-Source Insight

### MEMO: Memory as a Model — NUS / MIT CSAIL / A*STAR (arXiv 2605.15156)

**核心設計：將 Memory 變成獨立的 Small Language Model**

MEMO 的核心 insight 是把「記憶」從 RAG 的文件檢索變成一個独立訓練的 MEMORY model（實驗用 Qwen2.5-14B-Instruct）。EXECUTIVE model（Qwen2.5-32B-Instruct 或 Gemini-3-Flash）永遠 frozen，只透過 standard I/O interface 查詢 MEMORY model。

**為什麼比 RAG 更好**：
- RAG 的問題：retrieval noise 會顯著降準確率；cross-document reasoning 困難；inference cost 隨 corpus size 線性增長
- MEMO 的解決：MEMORY model 的 response 是固定長度的自然語言 snippet，cost 與 corpus 大小無關；Cross-document synthesis 是 Step 5 的核心，去掉它 NarrativeQA 準確率從 24% 跌到 6.37%

**訓練 pipeline（五步）**：
1. Fact extraction — 直接 + 間接事實並行抽取
2. Consolidation — 共享 context 的 QA pairs 合併
3. Verification & rewriting — 移除 self-contained不足的 pairs
4. Entity surfacing — 瞄準 reversal curse（「A is B」推出「B is A」）
5. Cross-document synthesis — 最關鍵，converging clues + parallel properties

**推理時的三階段 protocol**：
- Stage 1 (Grounding): EXECUTIVE 把 query 分解為 atomic sub-questions
- Stage 2 (Entity Identification): 迭代縮小候選實體範圍，預算 7 次互動
- Stage 3 (Answer Seeking & Synthesis): 確認實體後收集 supporting facts，預算 8 次互動

**Benchmark 結果**（MEMO vs HippoRAG2）：
- NarrativeQA: 53.58% vs 23.21% (+30.37)
- MuSiQue: 60.20% vs 57.00% (+3.20)
- BrowseComp-Plus: 66.67% vs 66.33% (+0.34)

**Noise robustness**：加入干擾文件時，HippoRAG2 降 6.22%，MEMO 變化 +0.55%（在 one standard deviation 內）

**Continual learning via model merging**：新 corpus 來時，獨立訓練新 MEMORY model → 取 task vector → 與現有 MEMORY model 做 TIES merging (ρ=0.3)。K=10 corpora 時比 full retraining 省 5.5× GPU-hours，代價是準確率落後 11-19%。

**與 Hermes 對照**：
- Hermes 的 heartbeat learning 目前是「每次 cycle 學一點」的增量攝取，沒有獨立 MEMORY model
- MEMO 的 cross-document synthesis pipeline 可供借鑒：5-step QA dataset synthesis → SFT → 模型合併
- Hermes 如果要走 MEMO 路線，需要：一個独立記憶模型 + 每次攝取時對該模型做 SFT + 用 model merging 累積新 corpus（而非不斷擴充 vector DB）
- 但 Hermes 是免費 Tier，訓練自己的 MEMORY model 成本太高。更實際的路徑：把「結構化記憶」的概念遷移到 policy/rules 層（類似 WS-035 的 session-bounded context），而非真的訓練一個 small LM

## Cross-Cutting Synthesis

MEMO 與前期探索的主題收斂：

| Source | 核心貢獻 |
|--------|---------|
| Memori v3.3.0 | 三層隔離（entity/session/process），context window 邊界決定於 session 而非時間 |
| WS-035 (Schema) | execution_ring schema 存在但無 enforcement（dead schema）|
| MEMO | 記憶變成獨立 model，EXECUTIVE 永远 frozen——架構上最乾淨的 isolation |
| AGT spec | Agent Hypervisor 四層 privilege ring，模擬 memory isolation |

共識：結構化隔離（無論是 session/process/MEMORY model/privilege ring）優於純向量檢索。MEMO 的貢獻在於把這個概念推到最后邏輯結論——記憶不再存在於文件或向量中，而是變成模型的 weight。

## 未追蹤 Leads

- https://arxiv.org/abs/2605.15156 — MEMO 原始論文（含 appendix D 的 hallucination error examples）
- https://github.com/nusdm/MEMO — 原始 implementation（如果有的話）
- AMA-Bench: https://openreview.net/forum?id=GoSVL7mLcM — benchmark for long-horizon agent memory（從 Memori 筆記繼承）

## ✅ 本次探索完成

*探索時間：2026-05-28 05:45 CST*

