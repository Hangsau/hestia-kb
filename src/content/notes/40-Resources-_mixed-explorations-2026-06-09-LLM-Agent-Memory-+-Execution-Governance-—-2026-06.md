---
_slug: 40-Resources-_mixed-explorations-2026-06-09-LLM-Agent-Memory-+-Execution-Governance-—-2026-06
_vault_path: 40-Resources/_mixed/explorations/2026-06-09-LLM-Agent-Memory-+-Execution-Governance-—-2026-06.md
title: 探索：LLM Agent Memory + Execution Governance — 2026-06-09
created: '2026-06-09'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# 探索：LLM Agent Memory + Execution Governance — 2026-06-09

**日期**: 2026-06-09 | **來源**: arXiv:2605.06716 + arXiv:2606.04306 + arXiv:2603.17787 | **類型**: Exploration

## Source 1: "From Storage to Experience" (arXiv:2605.06716)

**URL**: https://arxiv.org/abs/2605.06716 | **日期**: 2026-05-07

### 核心：Storage → Reflection → Experience 三階段演化框架

現有研究在「作業系統工程」和「認知科學」兩個paradigm之間震盪，導致碎片化。該survey提出統一的演化框架：

- **Storage**（軌跡保存）：最小變換地保留歷史互動軌跡，一對一對應
- **Reflection**（軌跡精煉）：將軌跡轉化為點評/corrective insights（`Fref: T→S`），注入quality density
- **Experience**（軌跡抽象）：跨軌跡歸納，MDL原則壓縮冗餘→通用schema/規則

### 對 Hermes 的直接啟發

1. **heartbeat_learning.py 的定位問題**：目前的 distillate 層本質上是 Reflection（trajectory refinement），但宣稱在解決 Experience 層的問題。**缺口**：缺少 cross-trajectory abstraction。當同一概念的 multiple trajectories 出現矛盾時，沒有機制做抽象層的衝突偵測。

2. **Staleness Detection 的量化target**：論文 Table 3 的 Experience Stage benchmarks（StreamBench、MemoryBench、Evo-Memory、LABench）提供了量化框架。BEAM benchmark（100 sessions, 10M tokens）的 `contradiction_resolution` metric 是直接relevant的 WS-035 drift penalty target。

3. **Temporal Decay vs Event-Driven Invalidation**：論文 Section 3.2（Dynamic Environments）指出：「知識在動態環境中是條件性的而非永恆有效」且「過時的知識經常在沒有明顯跡象的情況下失效（semantic representation 仍然看起來相關）」。這正是 uniform time decay 的失效模式——需要 event-driven invalidation。

### Per-source Insight

- 三階段不必然是完整替代，而是疊加演進——較新的階段仍保留前期階段的特徵
- Experience stage 的兩種transformative mechanisms：**Active Exploration**（主動探索）和 **Cross-Trajectory Abstraction**（跨軌跡歸納）
- Memory mechanisms 應採用基於任務類型的動態觸發模式（6 Future Directions第一點）

---

## Source 2: "Organizational Control Layer" (arXiv:2606.04306)

**URL**: https://arxiv.org/html/2606.04306 | **日期**: 2026-06-03（6天前，極新）

### 核心：Execution Boundary Problem

LLM agents 在部署環境中產生的輸出可能直接觸發狀態改變（價格、庫存、refund、order）。關鍵問題：**在執行之前必須govern proposed actions**。

OCL 的四個控制結果：
- **Approve**：直接執行提議
- **Revise**：修改為安全替代方案後執行
- **Block**：不執行任何環境 facing decision
- **Escalate**：路由到更高級別的process或human review

### 量化結果（GPT-5.4 backend, 50 adversarial episodes）

| Metric | Baseline | OCL |
|--------|----------|-----|
| Success Rate | 94% | 96% |
| Valid Success Rate | **12%** | **96%** |
| Unsafe Rate | **88%** | **0%** |
| Executed Violations | **205** | **0** |
| Avg Rounds | 5.36 | **2.58** |
| Avg Latency | 38.75s | **18.51s** |

核心發現：**Task success 的表面高（94%）隱藏了 88% 的unsafe rate**。沒有governance的agent看似成功，實則大量合規失敗。Valid success rate 12%→96% 證明了governance infrastructure的價值。

### 關鍵architectural principle

> "Deployment-grade agent systems should **separate proposal generation from environment-facing execution**."

這正是 WS-035 `PolicyInterceptor` 設計的核心缺口——目前沒有明確的 architectural separation between the LLM's generated proposal and the actual tool call execution.

OCL 的四個policy components：
- `πrole`：role-authority checks（哪個agent/module允許propose/revise/authorize）
- `πgate`：constraint checks against visible constraints → return control outcome
- `πescalate`：local approval insufficient時路由到human/trusted module
- `πaudit`：記錄所有proposed decisions、constraint checks、control outcomes

### 與 CUGA 的互補

CUGA（2026-05-27 exploration）的五層runtime governance是同一問題的不同切面：
- CUGA Layer 4 = **Tool Approval**（code gen後、execution前的pause gate）
- OCL同樣在proposal和execution之間插入governance layer
- 差異：CUGA的policy engine用Milvus vector DB做dynamic matching；OCL用确定性规则+LLM classification

兩者都確認：**pre-execution governance是deployment-grade agent system的必要條件**，而非可選項。

### Per-source Insight

- Safety-utility tradeoff：嚴格governance在adversarial markets保護seller，但在cooperative thin-margin markets會over-constrain agent
- OCL的deterministic replanning（out-of-bounds price自動clamp到nearest viable threshold）是practical enforcement mechanism
- 50 adversarial personas（Extreme Lowballer、Privacy Phisher、Role Hijacker、Vague Shopper、Time Waster）提供了威脅模型參考

---

## Source 3: "Governed Memory" (arXiv:2603.17787)

**URL**: https://arxiv.org/html/2603.17787 | **日期**: 2026-03-18 | **狀態**:  production deployed at Personize.ai

### 核心：Memory Governance Gap

企業AI部署產生 dozens of autonomous agent nodes，每個node對同一entity讀寫，但：
- 無共享memory
- 無共同governance layer
- 無schema enforcement for downstream consumption

Five structural challenges：
1. Memory silos across agent workflows
2. Governance fragmentation across teams and tools
3. Unstructured memories unusable by downstream systems
4. Context redundancy in autonomous multi-step execution
5. Silent quality degradation without feedback loops

### 關鍵機制：Dual Memory Model

**single extraction pass** 同時產生：
- **Open-set memory**：atomic facts（coreference-resolved、temporal anchoring、atomicity）
- **Schema-enforced memory**：typed property values governed by organizational schemas

兩種modalities互補，無資訊丟失。

Quality gates（per extraction batch）：
- Coreference score（pronoun detection）
- Self-containment score（syntactic pattern matching）
- Temporal anchoring score（relative-time pattern detection）

### 關鍵機制：Governance Routing

Tiered routing：
- **Fast mode**（~850ms avg）：無LLM call，embedding similarity + keyword overlap
- **Full mode**（~2-55s）：embedding pre-filter + LLM multi-step structured analysis

**Progressive Context Delivery**：session-aware delta delivery，只inject新content，避免重複context佔用window。

### 關鍵機制：Reflection-Bounded Retrieval

迭代協議，bounded rounds：
- 每round：LLM judge evidence completeness → 若incomplete則generate targeted follow-up queries
- 結果：62.8% completeness vs 37.1% baseline（+25.7pp）

關鍵發現：**API-managed reflection（+3.3pp）vs manual multi-hop（+25.7pp）**，差距在於query generation strategy，而非round count。

### 量化結果

| Experiment | Result |
|------------|--------|
| Fact recall | 99.6% |
| Governance routing precision | 92% |
| Token reduction (progressive delivery) | 50% |
| Cross-entity leakage (adversarial) | **0**（500 queries × 5 types）|
| Adversarial governance compliance | **100%** |
| LoCoMo benchmark | 74.8%（vs human 87.9%）|

**Memory density saturation**：~7 governed memories per entity reaches near-peak personalization quality（+24% relative jump from 0→3）。

### Per-source Insight

- Schema enforcement的價值在下游系統（CRM sync、analytics aggregation、structured API consumption），不在單次interaction quality
- Entity isolation由CRM key pre-filtering enforce，而非embedding distinctiveness——這是確定性的硬隔離
- 多-agent write conflicts未驗證（concurrent writes是open problem）
- 兩個phase的PII redaction（pre-extraction + post-extraction）防止LLM reconstruct PII from contextual cues

---

## 跨文章 Synthesis

### 1. 三篇文章收斂到同一原則：架構分離是必要的

- **2605.06716**（Storage→Reflection→Experience）：memory mechanism的演化是因為「proposal generation ≠ execution reality」——agent產生的trajectory在動態環境中會失效
- **2606.04306**（OCL）：proposal generation必須與environment-facing execution分離，否則88%unsafe rate
- **2603.17787**（Governed Memory）：memory store和governance layer必須與agent execution separated——多agent場景下共享memory需governance基礎設施

**核心原則**：無論是execution control（OCL）還是memory governance（Governed Memory），architecture separation between generation and enforcement是production-grade system的必要條件。

### 2. Staleness Detection：從 Time Decay → Event-Driven Invalidation

2605.06716 Section 3.2的關鍵洞察：
> "knowledge that is outdated often fails **without overt indication** (Lazaridou et al., 2021; Jang et al., 2022; Ko et al., 2024); although factually incorrect, such information may still exhibit significant relevance in its semantic representation"

這解釋了heartbeat_learning.py的uniform time decay為何不足：staleness和decay是不同的——
- **Decay**：低關聯記憶平滑衰減（Mem0 blog區分）
- **Staleness**：高關聯事實突然失效，無產品解

2603.17787的「semantic conflict resolution」（83.3% conflict detection）提供了staleness detection的production實證：exponential recency decay（half-life=38 days）rank recent facts above outdated，但仍是time-based而非event-driven。

**缺口**：event-driven invalidation（如2606.04306的constraint violation觸發replan）在memory system中沒有對應——當environment事實改變（如CTO更換、vendor評估結果出爐），相關的memory entries需要被標記為stale，而非只是decay over time。

### 3. Cross-trajectory Abstraction 是 WS-035 drift penalty的正確顆粒度

2605.06716的Experience stage（cross-trajectory abstraction）正是heartbeat_learning.py distillate試圖做的事，但缺少：
- **矛盾偵測**：multiple trajectories對同一concept給出不同結論時如何處理
- **歸納觸發條件**：何時觸發cross-trajectory abstraction而非繼續在Reflection層
- **Schema-guided abstraction**：2603.17787的schema-enforced memory提供structured output format，讓abstraction的結果可下游消費

### 4. Execution Governance 的具體實施模式

2606.04306的OCL提供了四個可移植的enforcement pattern：
1. **Deterministic replan**（clamp out-of-bounds price to floor）：簡單規則，零LLM call
2. **Escalation routing**（to human/trusted module）：無法本地處理的case外部化
3. **Audit trace**（all decisions logged）：事後可debug為何某proposal被approve/blocked
4. **Role-based authority**（πrole）：哪個agent/module允許做什麼

2603.17787的governance routing（fast vs full mode）提供了progressive enforcement的cost-quality tradeoff——簡單case用fast path（850ms），複雜case用full path（2-55s）。

### 5. Memory Quality 的量化框架

2603.17787的實驗提供了可直接移植的evaluation framework：
- **E2: Memory density** — 7 memories per entity saturation point
- **E3/E13: Governance routing precision** — 92%
- **E11: Entity isolation** — 0 cross-entity leakage
- **E14: Semantic conflict resolution** — 83.3% detection, 33.3% full suppression
- **E15: Adversarial governance** — 100% compliance

這些數字可作為WS-035 implementation的success metrics。

---

## 對 Hermes/Talos 的具體建議

### WS-035 Drift Penalty Design

1. **顆粒度**：cross-trajectory abstraction，not individual memory entries
2. **觸發條件**：semantic conflict between new distillate and existing distillate → immediate staleness標記
3. **Fallback**：exponential recency decay（half-life=38 days）for無衝突的gradual staleness
4. **Output format**：schema-enforced structured output（actionable by downstream systems），不只text summary

### Talos Governance Pipeline

1. **PolicyInterceptor 的 placement**：在tool call execution hop之前插入，不是LLM generation之內
2. **Two-tier enforcement**：fast path（deterministic rules）+ full path（LLM classification）for complex cases
3. **Audit trail**：所有governance decisions logged，supports事后debug和compliance reporting
4. **Role-based authority**：comms-reply、heartbeat、exploration各有不同tool call permissions

### heartbeat_learning.py upgrade

1. **增加 staleness detection**：不只decay，要追蹤contradiction events
2. **Query generation strategy**：reflection-bounded retrieval的有效性取決於query quality，而非round count
3. **Memory density**：~7 distillates per concept達到quality saturation，additional distillates yield diminishing returns

---

## 未追蹤 Leads

- RecMem（ACL 2026 Findings，subconscious + recurrence-triggered agent memory）— 標題来自web search但未找到具體paper URL
- H-MEM（EACL 2026，Hierarchical Memory for High-Efficiency Long-Term Reasoning）— search找到但vault無記錄，source URL待確認
- A-Mem（2502.12110）已在vault覆蓋（2026-06-08 notes），本次探索2605.06716的Storage→Reflection→Experience框架更完整
- CUGA Tool Approval（2026-05-27 exploration）已完整覆蓋，OCL提供互補的deterministic enforcement視角

## ✅ 本次探索完成