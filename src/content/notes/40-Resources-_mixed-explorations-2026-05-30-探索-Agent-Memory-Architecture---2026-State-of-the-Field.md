---
_slug: 40-Resources-_mixed-explorations-2026-05-30-探索-Agent-Memory-Architecture---2026-State-of-the-Field
_vault_path: 40-Resources/_mixed/explorations/2026-05-30-探索-Agent-Memory-Architecture---2026-State-of-the-Field.md
title: 探索：Agent Memory Architecture — 2026 State of the Field
date: 2026-05-30
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- based
- decay
- drift
- mem
- memory
- multi
- retrieval
- staleness
- user
created: '2026-05-30'
updated: '2026-06-15'
status: budding
---

# 探索：Agent Memory Architecture — 2026 State of the Field

**日期**: 2026-05-30 | **來源**: Mem0 benchmark + Steve Kinney synthesis

---

## Mem0 State of Agent Memory 2026

**來源**: https://mem0.ai/blog/state-of-ai-agent-memory-2026

### 核心數據
- 2026 新演算法：LoCoMo 92.5 / LongMemEval 94.4 / BEAM-1M 64.1 / BEAM-10M 48.6
- 最大進步：temporal queries +29.6pts，multi-hop +23.1pts
- token/query：~6,900（2026 algorithm）vs ~26,000（full-context 2025）

### 兩個架構改動
1. **Single-pass ADD-only extraction**：agent 生成的事實（confirmations/recommendations）現在和 user-stated facts 同等 weight，關閉了 significant gap
2. **Multi-signal retrieval**：semantic + BM25 keyword + entity matching 三路並行，分數 fuse 後勝過任何單一信號

### Memory staleness vs decay（重要區分）
- **decay**：低關聯記憶逐漸衰减（Mem0 產品已解決）
- **staleness**：高關聯事實突然失效（如 user 更換雇主，原本「user works at X」變成 confident error）。這是**open problem**，目前無產品解
- heartbeat_learning.py drift penalty 設計要處理的正是 staleness 不是 decay

### 三 scope memory model
- `user_id`：跨 session 持久化
- `agent_id`：特定 agent 實例
- `run_id / session_id`：單次對話 scope
- `app_id / org_id`：共享組織 context
- 這四個 identifiers 在 retrieval 時 compose，pipeline 自動 merge + rank

### Open problems（完整清單）
1. Temporal abstraction at scale — BEAM 10M drop 是 25% loss
2. Cross-session structure — treated as replacement 而非 evolution
3. Application-level evaluation — benchmark 分數不等於你的醫療/法律 workload 表現
4. Privacy/consent architecture — Regulation 會越來越具體
5. **Cross-session identity resolution** — anonymous/multi-device/mixed auth 打破 stable user_id assumption
6. **Memory staleness** — high-relevance memories that become wrong（open problem, no product solution）

---

## Steve Kinney — Memory Systems for AI Agents

**來源**: https://stevekinney.com/writing/agent-memory-systems

### 三軸框架：Forms / Functions / Dynamics

**Forms（記憶存在哪）**：
- Token-level：外部資料庫，所有 hosted model 都能用。topology 光譜：flat(1D) → planar/graph(2D) → hierarchical(3D)
  - StructMemEval 結論：simple retrieval outperforms complex hierarchies on standard benchmarks
  - **Practical guidance：flat is probably right**。移到 planar/hierarchical only when you observe specific retrieval failures that flat can't solve
- Latent：存在 model internal representations（KV cache、hidden states）。需 internal access → open-source only，hosted API 無法用
- Parametric：fine-tune / LoRA / ROME。Provider fine-tuning 是 batch process，不支援 incremental updates → 不是真正的 memory system

**Functions（為什麼需要記憶）**：
- **Factual memory**：what the agent knows（declarative facts）。大多數 framework 做的
- **Experiential memory**：how to do things better。**最大 gap** — 大多數 agent 有 factual memory，幾乎沒有系統性從自己的成敗學習
  - 這正是 heartbeat_learning.py 要解決的：distillate drift = experiential memory 未正確 consolidation
- **Working memory**：context window 內的主動控制，不是長期存儲

**Dynamics（記憶如何運作）**：
- Formation → Evolution（consolidation/update/forgetting）→ Retrieval
- **Forgetting 的三個訊號**：time decay（Ebbinghaus curve）、access frequency（LRU/LFU）、semantic importance（LLM-judged）
- **Three generations of evolution**：rule-based → LLM-assisted → RL-trained（Memory-R1、Mem-α frontier）
- Field progressing through: rule-based (hard-coded decay) → LLM-assisted (model judges what to merge) → RL-trained (policy learns through experience)

### Conflict detection at write time 被低估
- 0.6–0.9 cosine similarity range 是衝突區
- <0.6：不相關
- >0.9：near-duplicate
- 0.6–0.9 相似 topic 不同 facts → 這是有趣的衝突，應該主動 surface

### HyDE（Hypothetical Document Embeddings）
- Raw user query 不是好的 retrieval signal（question vs answer 形狀不同）
- HyDE fix：先叫 LLM 用無 context 方式回答問題，即使答案錯，fabricated answer 的 shape 會接近真實 stored memory 的 embedding
- 不需要答案正確，只需要 answer-shaped（declarative、specific）
-結合 hybrid search：BM25 catches exact keywords + semantic catches paraphrases

### Multi-hop queries 的策略光譜
- Iterative retrieval（agent tool call loop）：最簡單，zero storage change
- Query expansion：只能 rephrase 已給出的 entity，無法發現 memory store 裡存在但 query 未提到的 entity
- Enrichment at write time：extract entities + connection hints as metadata，中間方案
- Knowledge graph：full-power，但 engineering commitment 很高

### 實務建議（practitioners）
1. **Start flat**：StructMemEval 證明 simple retrieval 勝過複雜 hierarchies
2. **Conflict detection at write time > sophisticated retrieval ranker**
3. **Background consolidation > hierarchical architecture**
4. **HyDE for query construction** matters more than a fancier vector index
5. **Experiential memory** 是最大 gap — 你的 agent 應該記住如何解決問題，而不只記住事實

### 三個 trust pillars
- Privacy：tenant isolation + user-controlled deletion
- Explainability：traceable retrieval paths（practical minimum：retrieval logging）
- Hallucination robustness：conflict detection + surface contradictions rather than silently pick one

---

## 跨文章 Synthesis

### 一、Staleness vs Decay — 最關鍵的區分
兩個 sources 都提到但沒串起來：
- **Decay**：低關聯記憶隨時間平滑衰减 → Mem0 產品已解決（Ebbinghaus curve）
- **Staleness**：高關聯事實突然失效（user 換工作 → 「user works at X」變成 confidently wrong）→ **open problem，無產品解**

heartbeat_learning.py 的 drift penalty 需求：
- drift penalty 不是 decay（distillate 不是低關聯）
- drift penalty 是抑制 semantic drift（今天提煉的結論和前期衝突）
- 這更接近 staleness 的變體——不是「事實失效」而是「詮釋衝突」
- 建議：加入 `confidence_valid_until` 欄位讓 distillate 有时效，结合 event-driven invalidation 處理 staleness

### 二、Experiential Memory — 最大實作 Gap
兩個 sources 收斂到同一個結論：
- Mem0：procedural memory 是第三種 memory type，但 tooling 仍在 early-stage
- Steve Kinney：factual memory 大家都做，experiential memory 幾乎沒人做
- 具體來說：三層 experiential memory（case-based → strategy-based → skill-based），現在大多數 agent 在 case-based 和 strategy-based 之间
- **heartbeat_learning.py 的 distillate 層正是 strategy-based experiential memory** — 但缺少 procedure extraction（skill-based）和 conflict detection（drift penalty）

### 三、Multi-signal retrieval 是2026主流方向
- Mem0：semantic + BM25 + entity matching 三路並行
- Steve Kinney：BM25 catches exact keyword + semantic catches paraphrase + graph traversal catches multi-hop
- 這與 YantrikDB/agentmemory 等系統一致：结构化 > 纯 embedding

### 四、Architecture decision tree（實務建議）
```
Hosted frontier model (Claude/GPT/Gemini)?
  → Yes: Token-level only. Flat first. Add graph only when you observe specific multi-hop failures.
  → No: 考慮 latent + parametric（open-source only）
```

---

## 未追蹤 Leads

- https://arxiv.org/html/2603.07670v1 — Zhang et al. 2026 survey, comprehensive memory taxonomy
- https://arxiv.org/abs/2504.19413 — Mem0 ECAI 2025 paper
- https://github.com/mem0ai/memory-benchmarks — benchmark eval framework
- https://arxiv.org/abs/2603.11768v1 — SSGM (Governing Evolving Memory)
- Memory-R1 / Mem-α — RL-driven memory management（research frontier）

## ✅ 本次探索完成
