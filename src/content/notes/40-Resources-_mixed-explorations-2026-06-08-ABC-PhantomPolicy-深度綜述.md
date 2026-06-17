---
_slug: 40-Resources-_mixed-explorations-2026-06-08-ABC-PhantomPolicy-深度綜述
_vault_path: 40-Resources/_mixed/explorations/2026-06-08-ABC-PhantomPolicy-深度綜述.md
title: ABC + PhantomPolicy 深度綜述
created: '2026-06-08'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# ABC + PhantomPolicy 深度綜述

**日期**: 2026-06-08
**來源**: `autonomous_notes/2026-06-08-agent-behavioral-contracts.md` (初探) + 兩篇論文 deep fetch
**類型**: 研究綜述

---

## Per-Source Insights

### 1. Agent Behavioral Contracts (ABC) — arxiv:2602.22302v1

**核心框架：C=(P,I,G,R)**
- **P** (Preconditions): 執行前的假設條件
- **I** (Invariants): 執行中必須維持的條件（hard + soft）
- **G** (Governance): 行為策略約束（hard + soft）
- **R** (Recovery): 偏離時的恢復機制

**(p,δ,k)-satisfaction** — 機率性合約合規：
- 以 pp 機率滿足合約
- 偏差最多 δδ
- kk 步內恢復

**Drift Bounds Theorem（核心結果）**：
- 若自然 drift rate α，recovery rate γ > α
- 則 expected drift bound D* = α/γ
- 有 Gaussian concentration 在隨機設定
- **實驗驗證**：D* < 0.27，17–100% recovery success

**Compositionality Theorem（多 agent 鏈）**：
Four conditions for safe composition:
1. **Interface compatibility**: handoff invariant maintained at boundary
2. **Pre/postcondition chaining**: PostCondA ∧ Ihandoff ⇒ PB
3. **Governance compatibility**: GA ∪ GB 無衝突
4. **Recovery isolation**: RA 不違反 PB，RB 不違反 IA

Composition bounds:
- pp_chaine ≥ ∏ᵢ pᵢ · ∏ⱼ p_{h_j}
- δ_chain ≤ ∑ᵢ δᵢ + ∑ⱼ δ_{h_j}

**ContractSpec DSL**（Section 5.1）：
- YAML-based，支援 hard/soft constraint 分離
- Expression-based predicates
- 支援 pipeline composition

**AgentAssert**：runtime enforcement  library，sub-10ms overhead

**E4 Ablation（最關鍵實驗）**：
> Recovery contributes the largest marginal improvement to reliability Θ
> 移除 Recovery → Θ drop 0.199–0.215（mean −0.209）
> 這個 0.20 的 degrade 在所有模型都非常一致（不同 baseline 能力都同樣受害）

這確認了：**Recovery 機制是 ABC 架構的核心貢獻，不是 model-specific artifact。**

**Θ Paradox**：為何加入更多 constraint（Θ 應該更高）反而導致 Θ drop？
→ 原因是 soft constraint 會产生"false negative"（合約外行為被錯誤標記為 violation），稀釋了 recovery 的實際貢獻。Recovery alone 的 marginal improvement 才是真正的增量。

**Foundational claim**：
> Passive safety (training-time alignment alone) is provably insufficient
> for agents that evolve behavior over extended interactions.
> — Wang et al. (2026a) self-evolution trilemma

### 2. PhantomPolicy — arxiv:2604.12177v1

**核心問題：Policy-Invisible Violations**
- 定義：actions that are syntactically valid, user-sanctioned, and semantically appropriate, yet still violate org policy
- 關鍵：the decisive policy facts are absent from the model's execution context at decision time
- 非 jailbreak、非 authorization failure、非 content-filtering problem

**8 種 Violation Categories**：

| Category | Description | Invariant |
|---|---|---|
| Context boundary | INTERNAL context content → EXTERNAL | I2: ContextBoundary |
| Text-output leakage | User verbal data → outbound action | I4: ContentFingerprint |
| Oversharing | Folder bulk share includes restricted doc | I3: InformationFlow |
| Audience restriction | Doc audience policy prohibits recipient | I3: InformationFlow |
| Accumulated session leakage | Read CONFIDENTIAL doc taints session | I3: InformationFlow |
| Cross-context dataflow | Internal strategy → opposing vendor | I3: InformationFlow |
| High-value resource | Routine action targets legal matter | I7: Liveness |
| Temporal validity | Inactive contact / expired engagement | I1: ActiveRecipient |

**Sentinel Architecture**：
- Treats every agent action as a **proposed mutation** to an organizational knowledge graph
- Speculative execution: fork graph → apply mutations → verify invariants
- Three-valued logic: Allow / Block / Clarify
- O(|M|) per-action verification cost

**7 Graph Invariants (I1-I7)**：
- I1: ActiveRecipient — recipient must be active
- I2: ContextBoundary — internal context must not flow externally
- I3: InformationFlow — audience/scope constraints
- I4: ContentFingerprint — verbal taint detection
- I5: RecipientContext — recipient's clearance level
- I6: ScopeBoundary — scope transition rules
- I7: Liveness — high-value resource protection

**Coverage Degradation Experiments（關鍵數字）**：
- World-model coverage = 100% → 100% recall
- World-model coverage = 80% → 79.6% recall
- World-model coverage = 60% → 62.4% recall
- World-model coverage = 0% → 20% recall（ContextBoundary invariants still catch some）
- **Scope attribute removal** alone: recall 100% → 40.0%（scope 是最關鍵 metadata）
- **Sensitivity attribute removal**：no additional effect beyond scope removal

**Core insight（與 ABC 互補）**：
> Policy enforcement should be architecturally separated from model reasoning.
> The model should be responsible for task completion;
> a policy-aware enforcement layer, with access to org world state,
> should be responsible for compliance.

**Enforcement comparison**：
| Strategy | Accuracy / Recall |
|---|---|
| Baseline (no enforcement) | ~0% recall |
| Content DLP | 68.83% accuracy, 40.13% recall |
| Policy-in-prompt | 40.7% risky-case violations |
| **Sentinel** | **92.99% accuracy, 92.71 F1** |

---

## Cross-Paper Synthesis

### 1. ABC + PhantomPolicy 互補關係

ABC 和 PhantomPolicy 解決同一個底層問題的兩個正交維度：

- **PhantomPolicy** 解決「Policy facts are invisible to the model at decision time」→ 解決方案：world-state-grounded enforcement（Sentinel）
- **ABC** 解決「Behavioral drift over extended sessions」→ 解決方案：(P,I,G,R) contracts + Recovery mechanisms

兩者都強調：**Enforcement must be architecturally separated from the model**（ABC: recovery layer; PhantomPolicy: Sentinel graph invariants）。

### 2. Recovery 的核心地位

ABC E4 ablation 確認 Recovery 是 reliability 的最大貢獻者（移除後 Θ drop ~0.20）。這呼應了 PhantomPolicy 的設計：Sentinel 的 Clarify 機制就是 soft recovery——當 invariant 處於 ambiguous 狀態時，不是直接 block 而是要求 human clarification，這本身就是一種 recovery。

### 3. Drift Detection 的兩條路線

- **ABC**: 數學驅動 — Drift Bounds Theorem，Lyapunov stability，Ornstein-Uhlenbeck drift model
- **PhantomPolicy**: 知識圖譜驅動 — world-model coverage 決定 recall 上限，invariant satisfaction 決定 detection

兩者都收斂到同一結論：沒有外部事實來源（world state / contract preconditions），純靠模型內部推理是不夠的。

### 4. Compositionality 的重要性

ABC Compositionality Theorem（Section 4.3）給出了多 agent 鏈的正式保證：
- 機率下界：p_chain ≥ ∏ pᵢ
- 偏差上界：δ_chain ≤ ∑ δᵢ

這與 PhantomPolicy 的 Theorem 3（composability guarantee for Sentinel invariants）完全對稱：兩個系統都確保新增 invariant/contract 不會破壞現有保證。

### 5. 對 Talos Governance Pipeline 的啟發

**WS-029 (guardian-sandboxing-gradient)** 的三層隔離：
- L1: tool scoping
- L2: gateway mediation
- L3: container

ABC + PhantomPolicy 提供了 L2/L3 的具體實作參考：
- **Sentinel-style graph invariants** → 可作為 L2 的 pre-validation check（action 送到 graph simulation，Block/Allow/Clarify 再執行）
- **ABC Recovery mechanisms** → L2 的 fallback chains when soft constraints violated

**World-model coverage 優先於 invariant sophistication**：PhantomPolicy 明確指出，即使 invariant set 完整，coverage gap 也會導致 recall 上限下降。這對 Talos governance 的實作優先順序有直接影響：先建 world-model population pipeline，再做 invariant 精化。

**Scope metadata 是最關鍵的 attribute**：移除 scope 標籤，recall 從 100% → 40.0%。這意味著 Talos governance 的 world model 應優先 capture scope/authorization 資訊。

---

## Untracked Leads

（無）

## Dead Leads

（無）

## ✅ 本次探索完成
