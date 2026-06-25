---
_slug: research-2026-06-25-2101-hermes-consolidated-insight
_vault_path: research/2026-06-25-2101-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- subconscious-buffer
- progressive-cost
- personalization-substrate
source: multi
created: '2026-06-25'
confidence: high
title: 「沒被記住的東西」才是關鍵：四套系統共同擁有 Tier-0 原始緩衝區與漸進式成本升級
type: research
status: seedling
updated: '2026-06-25'
---

# 「沒被記住的東西」才是關鍵：四套系統共同擁有 Tier-0 原始緩衝區與漸進式成本升級

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

今日先前五次 consolidation（0000 / 0201 / 0601 / 0801 / 0906）已經分別處理了 Reader-Failure 閉環、5±2 工作記憶常數、多訊號 staleness、Drift Penalty 組件、Silent Failure 威脅模型、Self-Consistent Metric 偏誤等主題。本篇刻意避開那些角度，抽取一個更底層的**架構形狀**觀察：四套系統各自在「記憶形成之前」與「檢索逐步深入」這兩個維度上，都用了**同一套未明說的雙軌設計**——一個 Tier-0 原始緩衝區，加上一條成本遞增的路由管線。

## Cross-Cutting Theme 1: 每套系統都有 Tier-0「未被治理的原始緩衝區」——它是反記憶，不是記憶

**支援筆記**: hmem-recmem (RecMem Subconscious), memory-os (evicted MTM + STM 7-page queue), sage (unconnected-graph-nodes + writer-policy-rejection), llm-agent-memory-governance-synthesis (Governed Memory open-set raw facts)

把每篇關於「什麼東西**沒**進長記憶」的段落抽出來：

| 系統 | Tier-0 原始緩衝區的名字 | 它的角色 | 進入長記憶的條件 |
|------|----------------------|---------|---------------|
| RecMem | **Subconscious Memory** | raw embeddings, no LLM applied | θcount≥5 同時 θsim≥0.7 |
| MemoryOS | **STM 7-page queue**（FIFO）+ 被驅逐的 MTM segments | raw dialogue pages, no LLM segment summary | heat(α·N_visit+β·L_interaction+γ·R_recency) > τ |
| SAGE | **unconnected graph nodes** + writer-policy-rejected triples | raw entity mentions not yet linked | policy πwrite decides whether to write (u,r,v,source) |
| Governed Memory | **open-set memory** | atomic facts, no schema enforcement | schema-enforced memory extraction pass（同一 extraction 雙輸出） |
| H-MEM | **episode-layer pre-index raw vectors** | raw embedding before hierarchy routing | hierarchical descent 通過 4 層 pointer |

**洞察**：四套系統都明確區分「**被記憶的東西**」與「**還沒被記憶的東西**」——而後者不是「被遺忘」，是「**正在等待被治理的原始狀態**」。RecMem 把它命名為 "Subconscious"（最自覺），MemoryOS 用 STM 佇列實現，SAGE 用「未被寫入的節點」實現，Governed Memory 用 open-set vs schema-enforced 雙軌輸出實現。

這不是巧合。為什麼每套系統都需要這層？因為：
1. **LLM consolidation 是昂貴的**（RecMem 量化 87% token reduction 就是從這層省下來的）
2. **不是所有資訊都值得 consolidation**（一次性 noise 應該永遠留在 Tier-0，最終被 FIFO 驅逐）
3. **訊號要時間累積**（RecMem θcount、MemoryOS heat、SAGE writer policy reward 都需要多次觀察才能判定）

**對 Hermes 的直接意涵**：`heartbeat_learning.py` 目前是「每次有新 distillate 就寫入，沒有 Tier-0」——這正是 RecMem 量化抨擊的「eager consolidation」模式。`audit_cron.py` 看到的 distillate 增長 = 永久記憶增長，沒有 FIFO eviction 邊界，沒有「等待被證明值得」的 staging area。

**可行動下一步**：在 `heartbeat_learning.py` 加一個 `staging/` 子目錄（Tier-0），改寫 distillation pipeline：
```
current:  trigger → LLM distill → write to memory/
proposed: trigger → LLM distill → write to staging/{id}.md
          ↓ (every 24h) 
          staging_scoring.py 計算 heat(visit_count, link_count, recency)
          if heat > τ (= 5, 對齊 MemoryOS 預設):
              promote to memory/{id}.md  (canonical distillate)
          else if age > 14 days AND heat == 0:
              evict to staging/_evicted/{id}.md  (audit trail, recoverable)
```

關鍵差異：當前的 `memory/` 是 append-only（無 eviction），新設計引入 **promotion gate** 與 **soft eviction** 兩個新元件。預期 30 天後 `memory/` 蒸餾總數會下降 40-60%，但**留下來的會比現在的「全部保留」更有訊號密度**。實作成本：~120 行 Python + 一個 cron entry。

**信心**: high（四套系統各自獨立提出同一個設計元件，且命名幾乎一致：subconscious / STM / open-set / unconnected）。

## Cross-Cutting Theme 2: 「漸進式成本升級」（Progressive Cost Escalation）是四套系統的隱形檢索管線

**支援筆記**: hmem-recmem, memory-os, sage, llm-agent-memory-governance-synthesis

每一套系統的檢索路徑都呈現**同一個形狀：先用便宜訊號過濾，只對通過的子集呼叫貴的方法**：

| 系統 | Tier-1（便宜） | Tier-2（中） | Tier-3（貴） |
|------|--------------|------------|------------|
| RecMem | cos sim + threshold filter | — | LLM episodic summarization + semantic refinement |
| MemoryOS | embedding cosine + Jacard keyword overlap | segment heat score 排序 | LLM multi-step segment summary |
| SAGE | graph neighbor lookup | GFM soft addressing + pre-activation | LLM structurally-conditioned propagation + calibration |
| Governed Memory | Fast mode (850ms, no LLM, embedding+keyword) | — | Full mode (2-55s, LLM multi-step) |
| OCL | deterministic πgate rules | πrole authority check | LLM classification for ambiguous cases |
| H-MEM | layer-by-layer index descent (discrete pointer) | — | episode content retrieval |

**洞察**：這不是「多模態檢索」（那是用多種來源），這是「**單一模態內的成本梯度**」——同一個 query，先用 O(1) 或 O(log n) 的索引訊號篩選，再用 O(n) 或 O(n log n) 的語意訊號排序，最後才對前 k 個呼叫 LLM。

OCL 把這個 pattern 推到 governance 層：deterministic rule 先擋（0 LLM call），rule 不確定的 case 才升級到 LLM classification。Governed Memory 把 fast mode 量化到 850ms vs full mode 2-55s——**24× latency 差距對應完全不同的成本結構**。

對 Hermes 的直接意涵：`heartbeat_learning.py` 目前對每個 candidate distillate 都呼叫 LLM 做 summarization（隱含 cost = N · C_llm）；但其實大部分 candidate 在 Tier-1 就該被規則淘汰（recurrence_count == 1 且無 contradiction）。`audit_cron.py` 報的 token 用量是「**所有都走 Tier-3**」的成本，不是「**應該走的成本**」。

**可行動下一步**：在 distillation trigger 處加 progressive cost router：
```
distill_candidate arrives
  ↓
Tier-1 (heuristic, ~5ms):
  - already_in_memory? (exact id match) → skip
  - trivial_redundancy? (cos > 0.92 with existing) → skip + log "redundant"
  - low_signal? (length < 80 chars) → skip + log "thin"
  ↓ (~70% candidates die here)
Tier-2 (embedding only, ~50ms):
  - has_supporting_neighbors? (k-NN with ≥2 supporting distillates) → proceed
  - contradicts_recent? (cos > 0.85 with < 14d old distillate) → staleness_flag instead
  ↓ (~25% more die here)
Tier-3 (LLM, ~3-8s):
  - actually_distill  (only ~5-10% of original candidates reach here)
```

預期 token 節省 70-85%（對齊 RecMem 的 87% 數字），且 `audit_cron.py` 報的 distillation quality 會上升（因為 Tier-3 只處理真正 ambiguous cases，LLM 不用浪費在 trivial 上）。實作：~80 行 Python，在 `heartbeat_learning.py` 的 entry point 加 wrapper。

**信心**: high（六套獨立系統的檢索管線形狀一致，且其中四套有量化（87% token / 850ms vs 2-55s / 24× latency））。

## Cross-Cutting Theme 3: 「Persona / Schema / Typed Graph」是個人化的真正載體，不是 embedding

**支援筆記**: memory-os (User Traits 90-dim framework), llm-agent-memory-governance-synthesis (Governed Memory schema-enforced memory), sage (entity-relation typed triples)

三套系統各自用了**結構化表示**作為個人化推理的載體，且給出了量化證據：

- **MemoryOS**: User Traits 是 90 維向量，跨三類（基本需求+人格、AI對齊、內容平台興趣標籤）。**Memory density saturation**：~7 governed memories per entity reaches near-peak personalization quality（+24% relative jump from 0→3）。
- **Governed Memory**: Dual Memory Model——同一個 extraction pass 同時產出 open-set atomic facts + schema-enforced typed property values。Quality gates（coreference / self-containment / temporal anchoring）per batch。
- **SAGE**: Entity-relation-entity triples + source anchor，graph 是 typed substrate 而非 flat vector space。Self-evolution 兩輪收斂到 multi-hop QA 最佳。

三套都拒絕了「**embedding 相似度 = 個人化**」的等價，並各自用**typed/structured representation** 取代。

| 系統 | 結構化表示的維度 | 為什麼 embedding 不夠 |
|------|---------------|-------------------|
| MemoryOS | 90 維 trait schema（明確列出每個維度的語意） | "用戶喜歡 Python" 和 "用戶最近在學 Python" 在 embedding 空間距離很近，但語意完全不同（trait vs temporary state） |
| Governed Memory | typed property values（schema-governed） | atomic fact "客戶電話 02-1234-5678" 必須 schema-typed 成 `phone.primary` 才能被 CRM 消費 |
| SAGE | typed edges（relation 不是向量夾角） | "A 是 B 的 founder" 和 "A 認識 B" embedding 距離近，但 reasoning 路徑完全不同 |

**洞察**：個人化的關鍵不是「找到最相似的過去互動」，是「**找到 schema-compatible 的過去互動**」。embedding 給的是「**感覺相似**」，typed representation 給的是「**邏輯可組合**」。

對 Hermes 的直接意涵：當前的 distillate 是 free-text markdown——沒有 schema、沒有 typed edges、沒有維度標記。當 task context 需要「這個 distillate 跟使用者的哪個 trait 相關」時，唯一的辦法是再做一次 LLM call 推論——**這正是 RecMem 87% token waste 來源**。

**可行動下一步**：為 distillate 加最小 schema frontmatter：
```yaml
---
id: 2026-06-25-xyz
type: insight|fact|preference|procedure
domain: hermes-ops|user-pref|world-fact|tool-usage
trait_dimension: [memory-5, code-quality-3]   # 對齊 MemoryOS 90 維的子集
conflicts_with: []   # typed references
supersedes: []
created: 2026-06-25
heat: 0  # 累積
---
```

加 schema 後，`audit_cron.py` 可以用 `jq` 直接 group by `type` 或 `domain`，無需 LLM call。`task_context` retrieval 可以加 `domain=` filter 先縮小候選集，再做 embedding ranking——**Tier-1 從「embedding only」升級為「schema filter + embedding」**，成本接近 0（json parsing），召回率上升。

實作成本：~40 行 Python 在 distillation 出口加 schema validator。並把現有 `~/.hermes/autonomous_notes/*.md` 用一次性 migration script 加 frontmatter（~60 行）。

**信心**: high（三套獨立系統提出同一個 typed-representation 主張，且都有量化支撐：MemoryOS 的 +24% jump from 0→3、Governed Memory 的 99.6% fact recall、SAGE 的 82.5/91.6 NQ Recall@2/5）。

## 信心標示

- **Theme 1（Tier-0 原始緩衝區）**: high confidence — 四套系統獨立提出，且 RecMem 命名為 "Subconscious" 直接對應認知科學的 Atkinson-Shiffrin 框架。Hermes 缺這個元件是結構性的，不是細節。
- **Theme 2（漸進式成本升級）**: high confidence — 六套系統（含 OCL）的檢索管線形狀一致，且四套有量化數字。Token cost 是 Hermes `audit_cron.py` 已報的維度，但目前沒有 router 把 cost 梯度化。
- **Theme 3（Typed Representation 是個人化載體）**: high confidence — 三套系統各自有量化支撐，且與 Schema-enforced Memory 主題（0201 consolidation）互補——0201 處理「output format」，本篇處理「representation substrate」。

## 與今日先前五次 consolidation 的差異

- `2026-06-25-0000`：Reader-Failure 閉環 + 觸發訊號互補（**訊號來源**）
- `2026-06-25-0201`：5±2 magic number + Schema-enforced output format（**參數 + 表示格式**）
- `2026-06-25-0601`：多訊號 staleness + Reader→Writer 反饋（**失效偵測機制**）
- `2026-06-25-0801`：Drift Penalty 4 components 來自 4 篇（**drift 函數組裝**）
- `2026-06-25-0906`：Silent Failure 威脅模型 + Self-Consistent Metric（**失敗的可觀測性**）
- **本篇（2101）**：Tier-0 原始緩衝區 + 漸進式成本升級 + Typed Representation 載體（**記憶形成前的結構 + 檢索成本梯度 + 個人化推理的底層表示**）

六篇加起來構成完整 blueprint：訊號 → 參數 → 表示 → 失效偵測 → drift → 觀測性 → 形成前結構 → 成本梯度 → 推理載體。Tier-0 + Progressive Cost + Typed Schema 是前三層（**訊號/參數/表示**）的底層基礎——沒有它們，drift penalty 和 silent failure detection 都沒有「東西可以治理」。本篇補齊的是最底層的**形成層與成本層**。
