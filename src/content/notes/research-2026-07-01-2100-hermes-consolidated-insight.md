---
_slug: research-2026-07-01-2100-hermes-consolidated-insight
_vault_path: research/2026-07-01-2100-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-07-01'
confidence: high
title: 心跳蒸餾系統的三大結構性缺口：Reader→Writer 回饋、Cheap-First 過濾、Schema 強制
type: research
status: seedling
updated: '2026-07-01'
---

# 心跳蒸餾系統的三大結構性缺口：Reader→Writer 回饋、Cheap-First 過濾、Schema 強制

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

四篇都是 2026-06-09 同日探索，全部是 LLM agent 記憶系統的文獻綜合。從獨立讀每篇看不出來、但把四篇並排後才浮現的三個收斂性結構缺口——這些缺口都直接命中 Hermes `heartbeat_learning.py` 目前設計的「缺的那一塊」。

---

## Cross-Cutting Theme 1: Reader→Writer 回饋環是普遍模式，不是我們的特殊設計

**支援筆記**: hmem-recmem (RecMem θcount trigger), memory-os (heat-based eviction 重置 L_interaction), sage (writer-reader self-evolution loop), llm-agent-memory-governance-synthesis (Governed Memory quality gates + silent degradation 對策)

**分析**

把四篇系統拿掉名字看互動模式：

| 系統 | Reader 信號 | Writer 動作 | 觸發條件 |
|------|------------|------------|----------|
| RecMem | cosine similarity ≥ θsim | episodic abstraction | \|Ri\| ≥ θcount |
| MemoryOS | visit count + interaction length + recency | segment → LPM migration | Heat > τ |
| SAGE | reader failure signal | writer policy update | graph traversal exhaustion |
| Governed Memory | quality gates (coreference, containment, temporal) | extraction batch halt | score < threshold |

每個系統都把「讀取結果」當作寫入端的輸入。H-MEM 唯一偏向 user-feedback（approval/rebuttal 直接動 memory weight）——但本質仍是外部信號回注到 consolidation 流程。

`heartbeat_learning.py` 目前的 distillate 流程是**單向的**：

```
distillate 寫入 → 寫進去就完了 → task context 偶爾引用
```

沒有任何路徑讓「這個 distillate 多久沒被引用」「這個 distillate 引用的 task 是什麼模式」流回到「這個 distillate 是不是已經成為冷知識」或「這個分類下面我們缺什麼資訊」的判斷。四篇文獻壓倒性地確認**這不是可選設計，是維生條件**——Governed Memory 甚至把「silent quality degradation without feedback loops」列為企業部署五大結構性挑戰之一。

**可行動下一步**

1. 開 `distillate_usage.jsonl`（append-only log）：每次 `retrieve_distillates()` 命中時寫一筆 `{distillate_id, task_context_hash, ts}`
2. 在 `heartbeat_learning.py` 加 `compute_heat(distillate_id)`：從上述 log 計算 N_visit (近 90 天) + R_recency (上次引用 timestamp 的指數衰減 μ=30d)
3. 當 heat < 閾值（如 0.5）→ 在下一輪 heartbeat 輸出 `STALE_CANDIDATE: {distillate_id, last_cited, citations_90d}`，不自動刪除，但提供給蒸餾決策作為輸入
4. 預期工作量：1 個檔案 + 30 行 Python + 1 個 CLI 旗標 `--show-stale`

---

## Cross-Cutting Theme 2: Cheap-Signal-First 過濾架構是省 token 的標準答案

**支援筆記**: hmem-recmem (subconscious store 是「沒 LLM」的 raw embedding buffer), memory-os (F_score 用 cosine+Jacard 不要 LLM 來 grouping segment), sage (GFM pre-activation 是 trained soft addressing, 不每次 LLM judge), llm-agent-memory-governance-synthesis (Governed Memory fast mode 850ms 0 LLM call vs full mode 2-55s 有 LLM)

**分析**

每篇都同意一件事：**不要對每一筆資料都呼叫 LLM 做完整 semantic judgment**。具體節流路徑：

1. **RecMem subconscious store** — raw interaction 先停在 buffer，只在 recurrence 觸發時才走 LLM summarization。原文量化：87% token 節省。
2. **MemoryOS F_score** — segment 是用 embedding similarity + Jacard keyword overlap 自動 group 的，不需要每頁都過 LLM。只有 group 成功後才 LLM 摘要。
3. **Sage GFM pre-activation** — soft addressing 是 trained 的，不是 per-query LLM call。
4. **Governed Memory tiered routing** — fast mode（純 embedding + keyword）vs full mode（embedding pre-filter → LLM structured）。Fast mode 完全不碰 LLM。

Hermes `heartbeat_learning.py` 目前是 **eager mode**：每次新的對話軌跡進來 → 觸發 distillation → 觸發 LLM summarization。對應的瓶頸從四篇文獻看是「token 不夠」，而不是「準確率不夠」。RecMem 的 subconscious buffer 概念是這個問題最乾淨的解法。

**可行動下一步**

實作 RecMem 式兩階段 trigger 到 `heartbeat_learning.py`：

```python
# Stage 1: cheap signal (no LLM)
embedding = get_embedding(new_turn)
existing = load_recent_distillates(lookback=50)
neighbors = [d for d in existing if cosine(embedding, d.emb) >= 0.7]

if len(neighbors) < 3:  # θcount 用 3 (比論文 5 寬鬆, 因為我們是個人助手非對話系統)
    return  # "subconscious" — 不 consolidate, 等下個鄰居
else:
    # Stage 2: LLM consolidation (only triggered)
    summary = llm_summarize(new_turn, neighbors)
    add_distillate(summary)
    boost_confidence(neighbor_distillates)  # recurrence = strengthen
```

預期效果：當蒸餾觸發頻率從「每 5 個 turn」降到「每 15-20 個 turn」，token 成本立即降 60-70%。預期工作量：1 個 threshold config + 修改 `should_distill()` 函式邏輯。

---

## Cross-Cutting Theme 3: Schema 強制是「企業可用性」與「個人可用性」分界線

**支援筆記**: memory-os (User Traits 90 維度三類結構化), sage (entity-relation-source 四元組), llm-agent-memory-governance-synthesis Governed Memory (typed property governed by organizational schema 雙軌記憶), hmem-recmem (RecMem atomic facts + H-MEM structured routing 隱含)

**分析**

不顯眼但跨篇壓倒性的收斂：**所有「可用於下游」的記憶系統都把結構化當一級公民**：

- MemoryOS：User Traits 是**90 維度的明確向量**（基本需求 + AI 對齊 + 內容平台興趣），不是 free-form 偏好
- SAGE：寫入的最小單位是 `(entity, relation, entity, source)` 四元組，不是段落文字
- Governed Memory：dual model 明確分開 atomic facts 與 schema-enforced typed properties
- RecMem：semantic memory 只收 atomic facts（persistent but omitted 補回）

Hermes 的 distillate 目前是 markdown 自由文字 blob，下游消費者（skill retrieval、system-map、heartbeat report）拿到的是字串，要自己 reparse。這讓**任何 governance layer 都得重新做 NLP**——正是 Governed Memory 警告的「Unstructured memories unusable by downstream systems」（五大挑戰之一）。

更細的：**Schema 強制讓 Writer→Reader 回饋環可以機器驗證**。free-form 文字下「reader failure signal」也得 LLM 解讀；schema 化的 atom 下「missing field」「contradiction」可規則檢測。Theme 1 和 Theme 3 是**互鎖的**：沒有 schema，回饋環就得 always go through LLM，Theme 2 的 cheap-first 就破功。

**可行動下一步**

為 distillate 引入最小可行 schema（在不改後端的前提下）：

```yaml
# distillate frontmatter
type: preference | fact | procedure | tool_note
scope: user | project | skill | global
created: 2026-07-01
confidence: 0.0-1.0  # 由 Theme 1 的 heat 計算填入
last_cited: 2026-06-15
```

Phase 1：純 frontmatter metadata（不改 body 內容），讓 `retrieve_distillates()` 可以 `filter(type='user_preference')` 而不是 string match。

Phase 2（再說）：當 distillate 跨越 `type='procedure'` 與 `type='preference'` 矛盾時，能用 metadata-level contradiction detection（不需要 LLM）。

預期工作量：Phase 1 = 修改 distillate 寫入模板 + 1 個 parser helper。Phase 2 等 Theme 1 的 usage log 累積 30 天資料再說。

---

## 整合：三個 Theme 的施工程序

不是三件獨立的事，是**同一個系統的依序演進**：

```
Theme 3 (schema) ← 必須先做，因為它給 Theme 1 和 2 提供機器可驗證的結構
     ↓ 落地後
Theme 2 (cheap-first) ← 才有可能實作 — 沒有 schema，subconscious buffer 的鄰居判定只能 LLM 做
     ↓ 落地後  
Theme 1 (reader→writer) ← 完整閉環 — heat 計算、staleness 標記都有結構化資料可處理
```

預計 Phase 1（schema frontmatter）+ Phase 2（subconscious trigger）可在 1 個 heartbeat iteration 週期（約 7-10 天觀察資料）內完成。Phase 3（usage log + heat）要等 Phase 2 累積資料後才會產生效用。**不要倒著做**——純 reader feedback 沒有 schema 會掉進 Governed Memory 警告的「silent degradation」陷阱。

---

## 下次消化時要 cross-reference 的留白

- 四篇都還沒提到**「distillate 寫入衝突時的 resolution policy」**——OCL 的 Approve/Revise/Block/Escalate 四分類是否可直接移植為 distillate conflict resolution？目前 `heartbeat_learning.py` 在「兩個 distillate 矛盾時」是未定義行為，這個 gap 在 governance 維度（不是記憶維度）等於第四個 cross-cutting theme，但單篇沒明確寫，下一批探索時應驗證。
- 蒸餾品質評估的 ground truth 問題：四篇都用 LoCoMo / GVD benchmark，但 Hermes 的任務是個人助手（任務分佈未知），benchmark 適配性沒驗證過。Phase 2 跑完後應手工 spot-check 50 筆 distillate 看 quality gate 該長什麼樣。
