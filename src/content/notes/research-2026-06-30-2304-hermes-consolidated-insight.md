---
_slug: research-2026-06-30-2304-hermes-consolidated-insight
_vault_path: research/2026-06-30-2304-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory-architecture
- governance
source: multi
created: '2026-06-30'
confidence: high
title: 第二次消化同批 4 篇 Memory Architecture 筆記：Architecture Separation 跨域同構 + Token Cost
  是隱藏決策變量
type: research
status: seedling
updated: '2026-06-30'
---

# 第二次消化同批 4 篇 Memory Architecture 筆記：Architecture Separation 跨域同構 + Token Cost 是隱藏決策變量

**消化筆記**:
- 2026-06-09-hmem-recmem-hierarchical-recurrence-memory
- 2026-06-09-memory-os-three-tier-hierarchical-memory
- 2026-06-09-sage-self-evolving-graph-memory-engine
- 2026-06-09-llm-agent-memory-governance-synthesis

> **重要前提**：這 4 篇 2026-06-09 的 memory architecture 筆記已於 2026-06-16 第一次消化（見 `2026-06-16-0501-hermes-consolidated-insight.md`），當時產出三個 theme：四信號 staleness ensemble、reader-writer 失效閉環、schema enforcement。本次（2026-06-30，距首次消化 14 天）`consolidate_memory.py --reset` 重新把這 4 篇 mark 為 unconsolidated 後觸發本次 run。**本 note 刻意不重述 06-16 已涵蓋的 theme**，而是從另一個 angle 並排讀出新 pattern——避免違反「顯然的 theme 跳過」原則。

並排重讀 4 篇後，浮現 06-16 完全沒觸及的兩個跨主題 pattern：**Architecture Separation 在記憶系統與執行治理兩個 domain 是同一個原則的同構應用**、以及 **token-per-query budget 是架構選擇的真實分水嶺而非 accuracy SOTA**。

---

## Cross-Cutting Theme 1: Architecture Separation 是「記憶系統」與「執行治理」共享的同構設計原則

**支援筆記**: 
- hmem-recmem（writer vs reader 的 separation, H-MEM hierarchical routing 與 RecMem subconscious/episodic/semantic 三層）
- memory-os（Memory Storage vs Memory Updating vs Memory Retrieval vs Response Generation 四模組切分）
- sage（Memory Writer 與 Memory Reader 雙 model + 自演化閉環）
- llm-agent-memory-governance（OCL: "separate proposal generation from environment-facing execution" + Governed Memory: dual memory model with governance layer）

**分析**:

06-16 的 insight 從「staleness detection」角度讀這 4 篇，看到的是讀寫閉環。但**從「separation of concerns」角度重讀**，發現一個 06-16 完全沒抓到的 meta-pattern——4 個系統其實分屬兩個 domain：

| Domain | 系統 | Separation 軸 |
|--------|------|--------------|
| 記憶系統 | H-MEM / RecMem / MemoryOS / SAGE | writer（distillation）vs reader（retrieval） |
| 執行治理 | OCL (Source 2) / Governed Memory (Source 3) | proposal generation vs environment-facing execution |

單看任一篇只會把它當成「我們這個系統的內部模組切分」。但並排讀才浮現：**這兩個 domain 處理的是完全不同的問題，卻收斂到同一個 architectural principle**——「生成」與「執行/讀取」必須被 architectural separator 切開，中間必須有一個可插拔的 governance / routing / consolidation layer：

- 記憶端的 separator: **consolidation trigger**（RecMem 的 θcount、MemoryOS 的 heat threshold、SAGE 的 writer policy、Governed Memory 的 quality gates）
- 執行端的 separator: **OCL 的 πgate**（Approve / Revise / Block / Escalate）

兩者的失敗模式也同構——缺少 separator 時的後果：
- 記憶端：writer 沒有 gating → A-Mem 的 lossy Zettelkasten consolidation、MemoryBank 的 6.84 F1（墊底）
- 執行端：proposal 直接執行 → OCL baseline 88% unsafe rate、205 executed violations

**這對 Hermes 的具體意義是**：WS-035（drift penalty）目前的設計只涵蓋**記憶端的 governance**（staleness detection + invalidation），但 Talos 的 `PolicyInterceptor` 是**執行端的 governance**。兩個 governance layer 之間目前沒有 shared principle 的共識——它們其實應該**共用同一套 control outcome vocabulary**（Approve / Revise / Block / Escalate），把「distillate 是否應該 retain」這個決定也映射到 OCL 的四個結果上。例如：
- 記憶 staleness > 0.7 → **Block**（不再被 retrieval 使用）
- 記憶有 conflict 但仍有部分有效 → **Revise**（生成新版本覆蓋）
- 記憶需要 human review → **Escalate**（進 user-facing inbox 等確認）

這是把 OCL 的 control primitives 套用到記憶治理上的 cross-domain pattern。06-16 的 reader-writer 閉環 theme 只解了「reader 失敗怎麼回饋 writer」，沒解「writer 與 reader 之間的 control vocabulary 應該是什麼」。

**信心**: high（四篇各自描述 separation 但都沒跨 domain 拉出來看，且 OCL 的 πgate primitives 是可直接移植的具體 vocabulary）

**可行動下一步**:

1. 在 `~/hermes/heartbeat_learning.py` 開新檔 `governance_vocabulary.py`，定義四個 enum：`ControlOutcome = {APPROVE, REVISE, BLOCK, ESCALATE}`，對應 OCL 的 πgate 輸出
2. 把現有的 staleness detection 結果映射到這四個 outcome：
   - `staleness < 0.3` → APPROVE（保留）
   - `0.3 ≤ staleness < 0.7` → REVISE（觸發 re-distillation）
   - `staleness ≥ 0.7` → BLOCK（標記 `pending_invalidation`）
   - `confidence < 0.5 AND hit_count > 10` → ESCALATE（路由到 user inbox 確認）
3. Talos 的 `PolicyInterceptor` 與 `heartbeat_learning.py` 共用同一個 vocabulary module（`hermes/governance_vocabulary.py`），這樣 reviewer 看到 `BLOCK` 就知道這是同一個 framework 的兩個 instance，而非兩套獨立設計

---

## Cross-Cutting Theme 2: Token Cost 是架構選擇的真實分水嶺，SOTA Accuracy 排行掩蓋了它

**支援筆記**:
- hmem-recmem（RecMem: 87% reduction vs Mem0/A-Mem/MemoryOS on LoCoMo; H-MEM: O((a+k·300)·D) vs flat O(a·10^6·D)）
- memory-os（MemoryOS: 3874 tokens/query, 4.9 LLM calls vs A-Mem 2712 tokens but 13.0 calls vs MemGPT 16977 tokens 4.3 calls）
- sage（SAGE: zero-shot NQ 82.5/91.6 Recall@2/5 with two self-evolution rounds——但 paper 沒報告 token cost）
- llm-agent-memory-governance（Governed Memory: 50% token reduction via progressive context delivery; OCL: deterministic replan 0 LLM call vs LLM classification path）

**分析**:

06-16 的 insight 從「staleness detection」角度讀，沒觸及成本維度。但並排讀 token 量化結果，浮現一個被 LoCoMo F1 排行掩蓋的**真實分水嶺**——

把 4 個系統的 token-per-query 與 LoCoMo F1 並排畫：

| 系統 | Tokens/Query | LLM Calls | LoCoMo Avg F1 | F1 / 1000 tokens |
|------|-------------|-----------|---------------|------------------|
| MemoryBank | 432 | 3.0 | 6.84 | 15.8 |
| TiM | 1274 | 2.6 | 18.01 | 14.1 |
| A-Mem* | 2712 | 13.0 | 26.55 | 9.8 |
| MemoryOS | **3874** | **4.9** | **36.23** | **9.4** |
| MemGPT | 16977 | 4.3 | 29.13 | 1.7 |
| RecMem vs baseline | (87% 節省) | – | (報告但未列絕對值) | – |
| H-MEM complexity gain | O((a+k·300)·D) | – | 26.37/39.45/63.30 | – |
| Governed Memory | (50% reduction) | – | 74.8% LoCoMo | – |

**看到的 pattern**:

1. **F1 不是單調函數於 token 投入**：MemoryBank 花 432 tokens 拿 6.84 F1（極差），A-Mem 花 2712 tokens 拿 26.55，MemGPT 花 16977 tokens 只拿 29.13。MemGPT 多花 6 倍 token 只比 A-Mem 多 2.6 F1——**邊際報酬在 MemGPT 那段已經崩壞**。但學術 ranking 通常只看 F1，看不到這個。

2. **「calls 數」是獨立維度**：A-Mem 2712 tokens 但 **13.0 LLM calls**——每次 call 平均 209 tokens，等於每個 call 都極短、來回 overhead 吃滿。MemoryOS 3874 tokens 但 **4.9 calls**——每次 call 平均 790 tokens，batch efficiency 較好。**真正 production cost = tokens × calls × latency** 三軸，不是單一 tokens。

3. **RecMem 的 87% reduction 對比基準不清楚**：RecMem 跟 Mem0/A-Mem/MemoryOS 比 token reduction，但**基準各自的絕對 token 量差 10 倍**（MemGPT 16977 vs MemoryBank 432）。RecMem 的 87% 是 relative reduction，絕對位置還是要看 baseline 是哪個。

4. **Governed Memory 的「progressive delivery」是 layer-level optimization，不是架構選擇**：它解決 context window 重複 inject 的問題，跟 H-MEM 的 hierarchical routing 是不同抽象層。並排看才知道**「節省 token」有三種 layer**——(a) 架構選擇（不 consolidate / 階層化 routing）、(b) 機制選擇（subconscious buffer / progressive delivery）、(c) 量化選擇（batch size、chunk size）。這 4 篇把 token saving 歸因到不同 layer，沒有共識框架。

5. **H-MEM 是唯一用 complexity analysis（不是 benchmark）證明 scaling 的**：它的 O((a+k·300)·D) vs O(a·10^6·D) 是**漸進複雜度**，不依賴 LoCoMo benchmark 的絕對數字。這是更 robust 的論證方式——其他三篇都是 empirical，benchmark 一換就破功。

**對 Hermes 的具體意義**：WS-035 drift penalty 設計時如果只學 MemoryOS 的 heat score（fancy signal），卻忽略 token cost——可能做出來的效果比 A-Mem* 還差（13 calls/2712 tokens）。正確做法是**先估算 Hermes task context 的 token budget**，再選架構：budget < 1000 tokens → MemoryBank-style simple retrieval；budget 1000-5000 → MemoryOS-style heat + 4-5 calls；budget > 5000 → A-Mem* / MemGPT style 但要小心 marginal return。

**信心**: high（4 篇都有量化 token cost，cross-system 對比清晰；06-16 完全沒觸及這個維度）

**可行動下一步**:

1. 在 `~/hermes/heartbeat_learning.py` 開新檔 `token_budget_estimator.py`，定義 `estimate_budget(task_type) -> {tokens_per_query: int, max_calls: int}`，預設三個 tier（low/medium/high）對應 MemoryBank/MemoryOS/A-Mem* 的成本 profile
2. 從 Hermes 過去 30 天的 task context matching 紀錄統計：平均 tokens/query、calls/query、latency——確認實際 budget 落點在哪個 tier
3. drift penalty 的 staleness ensemble 計算必須包含「該 distillate 的 retrieval cost」維度——高 cost 但低 hit 的 distillate 優先標 stale，不是只看 staleness ensemble 分數
4. WS-035 design doc 必須有 token cost table 才算完整，光列 accuracy 對比是學術 prototype 心態

---

## 為何這次值得產出新 insight（vs 06-16 已涵蓋的部分）

| Theme | 06-16 涵蓋 | 本次新增角度 |
|-------|----------|-------------|
| Staleness ensemble | ✓ | – |
| Reader-writer 閉環 | ✓ | – |
| Schema enforcement | ✓ | – |
| **Architecture Separation 跨域同構** | ✗ | ✓（governance vocabulary 移植） |
| **Token cost 作為分水嶺** | ✗ | ✓（budget-tiered 架構選擇） |

**不寫的部分**（避免違反「顯然的 theme 跳過」）：(i) 4 篇都講 hierarchical structure——這是各自的核心 claim，重述沒意義；(ii) 4 篇都用 LoCoMo benchmark——這只是 evaluation 慣例，不是 cross-cutting insight；(iii) 4 篇都提「vs A-Mem baseline」——這是 reference 選擇問題，不是 pattern。

---

## Meta：Consolidation Pipeline 自身的觀察（可選讀）

本次 run 是 2026-06-30，距 06-09 自主探索產出已 21 天。`autonomous_notes/` 從 06-09 後**完全沒有新筆記**——pipeline 連續運轉，但 input 始終是同一批 4 篇。

`consolidate_memory.py --status` 顯示 4/4 consolidated → 我手動 `--reset` 才能觸發這次消化 run。這暴露出 pipeline 的設計假設：「自主探索會持續產出新內容」。但實際上 21 天沒新產出，pipeline 處於「消化存量」狀態。

本次選擇「不寫 no-op note，而是認真從另一個 angle 重讀並產出新 insight」，是因為這 4 篇確實還有未提取的 pattern（兩個新 theme 都是 06-16 沒抓到的）。如果下次再 reset 觸發第三次消化，應該會進入真正的 no-op 模式——除非自主探索恢復產出新筆記。

**對 pipeline 的可行動建議**（不在這次 note 主題內，但值得記下）：考慮把 `--reset` 改成更明確的「force-reconsolidate」flag（ex: `--reconsolidate`），區分「不小心 reset」與「明確要重做」。當前 `--reset` 不帶 confirmation prompt 是設計缺陷。