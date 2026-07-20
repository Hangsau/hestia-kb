---
_slug: research-2026-07-21-0701-hermes-consolidated-insight
_vault_path: research/2026-07-21-0701-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-governance
- drift-penalty
- heartbeat-learning
source: multi
created: '2026-07-21'
confidence: high
title: 四份記憶系統論文都拒絕了「單一信號驅動」—— Hermes 的 staleness 函數目前就是單一信號
type: research
status: seedling
updated: '2026-07-21'
---

# 四份記憶系統論文都拒絕了「單一信號驅動」—— Hermes 的 staleness 函數目前就是單一信號

**消化筆記**: 2026-06-09-hmem-recmem-hierarchical-recurrence-memory, 2026-06-09-memory-os-three-tier-hierarchical-memory, 2026-06-09-sage-self-evolving-graph-memory-engine, 2026-06-09-llm-agent-memory-governance-synthesis

四篇 2026-06-09 自主探索筆記讀完後最鮮明的圖像：**H-MEM、RecMem、MemoryOS、SAGE、BEAM、OCL、Governed Memory——七個獨立的 2026 年記憶/治理系統，全部在用「單一信號驅動」的架構上碰壁，於是各自朝不同方向補洞**。但每一篇只看到自己補的那一面。把它們疊起來才看見：**Hermes 現有的 `heartbeat_learning.py` drift penalty 是這七個系統試圖逃離的那種架構本身**——而這正是 WS-035 一直搖擺不決的根源。

## Cross-Cutting Theme 1: 「單一 staleness 信號」是 2026 記憶系統共同的反模式

**支援筆記**: hmem-recmem（RecMem 否定 eager consolidation、H-MEM 否定 pure similarity retrieval）, memory-os（否定 fixed FIFO，提出 heat score = visit × interaction × recency 三維）, sage-self-evolving（否定 static graph index，提出 reader-failure signal 反饋 writer）, llm-agent-memory-governance（BEAM contradiction metric 否定 uniform time decay，提出 event-driven invalidation + Experience-stage abstraction）

**分析**：四篇筆記各自獨立提出的修正方案如下表，把它們並排才看得見——**每一篇補的是不同軸**：

| 軸 | 補洞者 | 訊號 | 單獨用的盲點 |
|----|--------|------|-------------|
| 時間衰減 | H-MEM（memory weight）、RecMem（subconscious buffer） | recency | 無法偵測「看似相關但語意過時」 |
| 重複頻率 | RecMem（θcount ≥ threshold） | recurrence | 高頻誤訊息會被誤升 |
| 檢索熱度 | MemoryOS（heat score = N_visit + L_interaction + R_recency） | retrieval utility | 冷門但關鍵的 distillate 被誤蒸 |
| 語意衝突 | llm-agent-memory-governance（BEAM contradiction_resolution） | contradiction event | 無衝突的 staleness 不會觸發 |
| 讀取失敗 | SAGE（reader-failure signal → writer） | retrieval miss | 系統長期沒用就不會 fail |
| 治理 / 撤銷 | llm-agent-memory-governance（OCL πgate, Governed Memory quality gates） | explicit invalidation | 仰賴人/規則定義什麼算 invalid |

**Hermes `heartbeat_learning.py` 現狀**：只用「時間衰減（half-life=38d）」。**這正好落在七個論文各自抨擊的那個象限**。每篇筆記給的「可行動建議」都是「加一個 X 信號」——但從來沒有任何一篇指出：我們其實在拼的是一個**多軸 staleness 函數**，而且這四個軸是**正交的**（衝突可能在沒熱度時發生，重複可能跟時間無關）。

**可行動下一步**：
1. 在 `~/obsidian-vault/02-Areas/Hermes-Ops/` 下新增 `drift-penalty-multiaxis-design.md`，把上表四軸正式定義成 `staleness_score(d) = w_t·recency_decay + w_r·(1-recurrence_norm) + w_h·(1-heat_norm) + w_c·contradiction_count`，權重預設值採用 0.4/0.2/0.2/0.2（時間仍主導，但留 60% 給其他信號）
2. **具體程式碼變更點**（明日可做）：在 `heartbeat_learning.py` 的 decay 計算處，加三個計數器：`recurrence_count`、`retrieval_visit_count`、`contradiction_event_count`，每個 distillate 攜帶這三個欄位（先 schema-level 改，無需立即改演算法）
3. 設定 `--mark-fed` 之前的權重 sweep：未來 ablation 應該證明「只用時間」在 BEAM contradiction_resolution metric 上必然衰退，因為 BEAM 的 invalidation 規則不靠時間

## Cross-Cutting Theme 2: 寫入/讀取必須閉環——七個系統全都在做「reader → writer 反饋」

**支援筆記**: hmem-recmem（RecMem subconscious→episodic trigger 就是 reader signal 驅動 writer）, memory-os（MTM→LPM heat > τ 是 reader utility 反饋 writer）, sage-self-evolving（writer-reader self-evolution 是該論文的 entire 核心）, llm-agent-memory-governance（Governed Memory reflection-bounded retrieval、OCL πaudit 反饋給 πgate）

**分析**：把四篇筆記的架構圖疊起來，會浮現一個**共同的拓撲**：

```
Writer（distillation trigger）
  ↓ write
Memory Store
  ↓ read
Reader（task context matching）
  ↓ failure signal / utility signal
Writer（refinement trigger）  ← 這條回饋弧
```

**每一篇都在不同地方畫出這條回饋弧**：SAGE 是顯式的（"self-evolution rounds"），RecMem 是隱式的（recurrence 偵測本身就是讀取後觸發寫入），MemoryOS 是用 heat score 量化的（visit count 必須來自 reader），Governed Memory 是 governance routing（fast/full mode 切換本質上是 reader 失敗 → 升級 writer）。

**Hermes 現狀**：`heartbeat_learning.py` 是**單向 pipeline**——distillate 寫入後就進入 retrieval，沒有反饋路徑告訴 distillation trigger「這條 distillate 沒人用了」或「這條 distillate 在 task context 裡永遠 retrieve 不到證據」。

**這是 Theme 1 的成因**：因為沒有 reader→writer 反饋，所以 staleness 只能靠時間瞎猜。

**可行動下一步**：
1. 在 `heartbeat_learning.py` 加一個輕量級 telemetry hook：每次 task context matching 完成後，記錄 `(distillate_id, hit=true/false, query_embedding)` 到 `~/.hermes/state/retrieval_telemetry.jsonl`
2. 下次 consolidation（明天的 cron job）時，這個檔案已經有資料，可以計算「每條 distillate 的 7 日 hit rate」——這就是 SAGE reader-failure signal 的 Hermes 等價物
3. **不要等 schema 改完才做**：先用 append-only JSONL，後續再 migrate 到 SQLite。Schema-first 會卡在設計討論

## Cross-Cutting Theme 3（bonus, medium confidence）: 2026 記憶論文的 benchmark 收斂點都是 LoCoMo——Hermes 應該有專屬 benchmark

**支援筆記**: hmem-recmem（LoCoMo 5 種 QA 任務）, memory-os（LoCoMo + GVD）, llm-agent-memory-governance（LoCoMo + BEAM + StreamBench + MemoryBench + Evo-Memory + LABench）

**分析**：四篇筆記裡三篇引用 LoCoMo benchmark。這意味著 2026 年的記憶系統論文有**共同的量化戰場**，但 LoCoMo 是 social dialogue QA——**跟 Hermes 的「agent 自進化」任務本質不同**。

四篇沒有一篇指出：我們應該做 HermesBench。但這正是實作 Theme 1 多軸 staleness 函數的前提——沒 benchmark 就沒法 sweep 權重。

**可行動下一步**：
1. 從 `~/.hermes/state/` 與 `~/obsidian-vault/memory/` 萃取 50 個 task sessions，標註每個 session 引用了哪些 distillate → 建立第一版 HermesBench
2. 標註三類 ground truth：(a) distillate 該被提升（被引用且有正面結果）、(b) 該被標 stale（沒引用 > 60 天）、(c) 該被 contradiction-flagged（同一概念兩個版本衝突）
3. 這給 Theme 1 的權重 sweep 提供 evaluation harness

## 這次消化對 Hermes 架構的具體交付物

| 項目 | 優先級 | 預估工時 |
|------|-------|---------|
| retrieval_telemetry.jsonl hook | P0 | 30 min |
| distillate schema 加三計數器欄位 | P0 | 1 hr |
| drift-penalty-multiaxis-design.md | P1 | 1 hr |
| HermesBench v0.1（50 sessions） | P2 | 半日 |

P0 兩項今天就能完成——它們是 Theme 1 與 Theme 2 的具體落地，不依賴其他設計決定。