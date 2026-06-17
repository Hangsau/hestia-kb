---
_slug: 40-Resources-_mixed-explorations-2026-05-27-Engram-生物啟發式記憶系統-三層架構與混合檢索
_vault_path: 40-Resources/_mixed/explorations/2026-05-27-Engram-生物啟發式記憶系統-三層架構與混合檢索.md
title: 探索：Engram 生物啟發式記憶系統
created: '2026-05-27'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：Engram 生物啟發式記憶系統

**日期**: 2026-05-27 | **主題**: 三層記憶架構 + 混合檢索 + 六原則智力環
**來源**: [OpenPawz Engram](https://github.com/OpenPawz/openpawz/blob/main/ENGRAM.md) (MIT, 63⭐)
**指紋**: engram, triple-layer, tulving, fade-mem, graph-rag, memory-bus, crdt, intelligence-loop

---

## Engram 核心架構

**為何選**: 三層（episodic/knowledge/procedural）+ graph + 精確保證機制，與 YantrikDB (Tulving 分類) + WS-035 policy engine 高度相關

### 三層設計（Tulving 對應）

- **Tier 0 — Sensory Buffer**: FIFO ring cache，20 items max，單 turn lifetime
- **Tier 1 — Working Memory**: 優先級驅逐快取，4,096 token budget，活躍注意力
- **Tier 2 — Long-Term Memory Graph**:
  - Episodic Store（發生了什麼）
  - Knowledge Store（什麼是真的）— 三元組形式
  - Procedural Store（怎麼做）— 步驟+成功/失敗計數

### 圖結構（8種邊）

RelatedTo, CausedBy, Supports, Contradicts, PartOf, FollowedBy, DerivedFrom, SimilarTo

**傳播激活**：檢索到的記憶相鄰節點獲得激活boost，混合原始分數產生最終排名

### 混合檢索管線

```
BM25 (全文) + Vector (Ollama embeddings) + Graph Activation
→ Reciprocal Rank Fusion (k=60)
→ MMR 重排
→ CRAG Quality Gate (relevance ≥ 0.3)
```

### 遺忘機制（FadeMem dual-layer）

- LML (Long-Term Memory) β=0.8 — 長期保留層
- SML (Short-Term Memory) β=1.2 — 短期强化層
- Ebbinghaus 曲線衰減
- **交易式 GC**：合并前/後 NDCG 對比，降解 >5% 自動回滾

### Intelligence Loop（六原則）

```
GATE → RETRIEVE → CAP → SKILL → EVALUATE → FORGET → GATE
(Self-RAG)  (Deep      (PAPerBench) (Voyager)  (DRB-II)  (FadeMem)
             GraphRAG)
```

**關鍵數字**：
- 10K memories: 搜索 <10ms
- FadeMem: 儲存减少 45%，F1=29.43
- Working Memory budget: 4,096 tokens（預設）

### Memory Bus（多Agent同步）

- CRDT-inspired，P2P knowledge sharing
- Vector clock conflict resolution
- Publish-side authentication（能力token驗證 + injection掃描）

### Dream Replay（休眠重激活）

- Idle-time 重新嵌入 + 發現潛在連接
- 對標海馬體 replay

---

## Hermes 啟發

1. **三層對齊已確認**：Engram 的 episodic/knowledge/procedural ≡ YantrikDB 的 Tulving 分類 ≡ Mem0 (episodes/semantic)。結構化 > 純嵌入共識再次驗證。

2. **六原則 Loop 對標 heartbeat_evolve**：GATE-RETRIEVE-CAP-SKILL-EVALUATE-FORGET 迴圈直接映射到 heartbeat 的選單驅動自主行為（探索→過濾→攝入→技能沉積→評估→遗忘）。Heartbeat 的「選一件事做」本身就是 GATE，功能早已存在。

3. **CRAG Quality Gate**：relevance ≥ 0.3 才注入。這對 heartbeat 自我評估有直接幫助——如果某個探索主題連續多次 relevance < threshold，應該主動降級或跳過。

4. **Transactional Forgetting**：GC 自動回滾。heartbeat learning 的 distillate 如果連續兩次語義漂移，應該有對應的 rollback/truncate 機制。

5. **Memory Bus 的 auth 機制**：agent-to-agent 的 capability token + injection scan。Talos comms 目前缺這層——收到 Hestia 的消息只做簡單解析，沒有能力驗證也沒有 injection scan。這是實作方向之一。

---

## 跨文章 Synthesis

Engram + Metamind + YantrikDB + Mem0 的收斂點：
- **結構化記憶 > 純嵌入**：所有系統最終都走向 triple-store (episodic/semantic/procedural) 或等價結構
- **優先級衰減 > 無差別保留**：Ebbinghaus 曲線 + FadeMem dual-layer 提供了可測量的衰減框架
- **Gated retrieval**：~40% 不必要的搜索可以通過 intent classification 省掉
- **多代理記憶同步**：Memory Bus 的 CRDT 模式是 agent 協作的安全基礎

---

## ✅ 本次探索完成

**未追蹤 Leads**：
- Metamind (bikidev): https://bikidev.com/blog/metamind-memory-system-deep-dive (網站離線，無法 fetch)
- Clawdbot: https://avasdream.com/blog/clawdbot-memory-system-deep-dive (1pt，標題誤導 — 實際是行銷文章)
