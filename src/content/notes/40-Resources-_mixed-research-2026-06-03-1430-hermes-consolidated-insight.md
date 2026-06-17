---
_slug: 40-Resources-_mixed-research-2026-06-03-1430-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-1430-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: high
title: RLM 架構收斂：Memory 與 Governance 的共同根基
updated: '2026-06-15'
type: research
status: budding
---

# RLM 架構收斂：Memory 與 Governance 的共同根基

**消化筆記**: 2026-06-03-rlm-core-engine-deep-dive, 2026-06-03-alexzhang13-rlm-codebase, 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-shapedql-multi-stage-ranking, 2026-06-03-forge-gambit-agent-harness, 2026-06-03-llamagym-online-rl-fine-tune

六篇筆記幾乎同時收斂到同一個底層設計原則：**把記憶／工具／環境當作有介面的一等公民，而非 wrapper 或原始字串**。這不是巧合——這是生產級 agent 系統正在集體驗證的架構方向。

---

## Cross-Cutting Theme 1: 第一公民環境層（First-Class Environment Layer）

**支援筆記**: rlm-core-engine-deep-dive, alexzhang13-rlm-codebase, rlm-paper-reinforcement-codeRLM, shapedql-multi-stage-ranking

### 分析

三層觀察指向同一個模式：

**1. RLM 的環境 factory 與三隔離層**
`environments/__init__.py` 的 `get_environment()` 工廠模式，讓隔離級別（local → ipython → cloud sandbox）變成可置換的第一公民參數，不是 wrapper 包上去。`SupportsPersistence` interface 是新增環境時的合約，確保新隔離層不會意外破壞持久化邏輯。

**2. RLM Paper 的符號化 prompt 處理**
正確的 RLM 實作把 prompt 存成 REPL 裡的**變數**，不是塞進 LLM context。LLM 生成**程式碼**來檢查/分解這個變數，子 call 是程式化的（在迴圈裡，可嵌套）。只有**常數大小的 metadata** 每輪附加到 LLM history。這直接對應 heartbeat_learning.py 的核心問題：現在是把蒸餾產出當原始文字傾倒進 context，沒有結構。

**3. ShapedQL 的四段 pipeline**
Retrieve / Filter / Score / Reorder 把搜尋引擎的複雜度收斂成宣告式 SQL。更有趣的是「User Context as first-class citizen」——不是無狀態的文件檢索，而是每個 user 的個人化決策。映射到記憶：Retrieve = 召回相關蒸餾產出，Filter = 移除矛盾/過時蒸餾產出，Score = 按時序/矛盾次數/使用頻率排名，Reorder = 只把 top-K 丟進 context，不是全量傾倒。

**三個來源共同支援的原則**：
> 把複雜的外部狀態封裝成有介面的結構實體，而不是用原始文字傳遞。RLM 把 prompt 變數化，ShapedQL 把 ranking pipeline 結構化，環境 factory 把隔離層介面化。

### 可行動下一步

在 `heartbeat_v2.py` 設計**StructuredDistillate schema**（取代目前的純文字傾倒）：

```python
class StructuredDistillate:
    content: str           # 壓縮後的 insight
    created_at: float
    source_note: str
    concept_id: str        # 跨筆記一致的概念追蹤
    contradicts: list[str] # 矛盾蒸餾產出的 ID 清單
    confidence_valid_until: float  # 置信度有效期限
```

實作時優先處理 `contradicts` 欄位——當新蒸餾產出與舊的存在矛盾，**不等時間衰減，直接結構性失效**舊節點。這是 RLM paper + CodeRLM drift detection 的內核。

---

## Cross-Cutting Theme 2: Enforce → Measure → Invalidate 三角閉環

**支援筆記**: forge-gambit-agent-harness, llamagym-online-rl-fine-tune, rlm-paper-reinforcement-codeRLM

### 分析

三個看起來不相關的工具，在同一個反饋環路上收斂：

**Forge（enforce 層）**: `ResponseValidator` + `Rescue parsing` + `Synthetic respond tool` 構成 L1 guardrails，確保 tool call 有效性，避免模型在工具和文字間抖動。小模型（~8B）無法自我判斷需要輸出工具還是文字，所以用 injection 強迫正確行為——「結構化輸出比信任模型自律更可靠」。

**Gambit（measure 層）**: agent 行為的迴歸測試框架。deck.md 定義情境，simulator 跑 trace，grading 判定行為質量。難得的是「bring your own agent」設計——不綁定特定框架，只提供 eval 能力。這對應 agent-observability-landscape 研究裡的 Task Eval 層。

**LlamaGym + RLM（invalidate 層）**: `assign_reward(reward)` 是明確的置信度失效原語。RM paper 的常數大小 metadata 每輪附加，確保記憶增長有界。Lamorel 的 `score(contexts, candidates)` 實作了具體的置信度訊號——低分 = 低置信 = drift penalty 觸發。

**Forge + Gambit 已經是具體的兩層架構**：Forge = L1 guardrails（強制正確 tool call），Gambit = L2 eval harness（測量並迴歸測試 agent 行為）。加上 LlamaGym 的 invalidate 層，三者構成完整反饋環。

### 可行動下一步

設計 `TalosGovernancePipeline`：

```python
# L1: Forge-style proxy guardrails
class L1Guardrails:
    def validate_response(self, response, tools):
        # ResponseValidator + Rescue parsing
        pass

# L2: Gambit-style eval harness
class L2EvalHarness:
    def grade_behavior(self, trace, deck):
        # deck.md scenario grading, JSONL traces
        pass

# L3: Invalidation layer (from LlamaGym/RLM pattern)
class L3Invalidation:
    def check_staleness(self, distillates, new_evidence):
        # structural contradiction check, not just temporal
        pass
```

先實作 L1 的簡化版本（不需完整 Forge），用於驗證 tool call 格式正確性。L2 和 L3 預留介面，隨增量開發逐步填入。

---

## 備註：Theme 1 與 Theme 2 的互連

Theme 1（結構化記憶）使 Theme 3（L3 Invalidation）得以實現——沒有概念圖譜，無從判斷「矛盾」與「過時」。Theme 2（Enforce-Measure 迴圈）確保 agent 行為的正確性，不只是工具使用，還包括蒸餾產出的品質。三個 theme 形成互相餵養的架構：

```
結構化記憶（Theme 1）
    ↓ 提供可失效的節點
Enforce-Measure-Invalidate 閉環（Theme 2）
    ↓ 確保蒸餾產出品質
更好的結構化記憶（反饋）
```