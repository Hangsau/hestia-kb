---
_slug: 40-Resources-_mixed-explorations-2026-06-08-Agent-Behavioral-Contracts---PhantomPolicy---Runtime-Enforce
_vault_path: 40-Resources/_mixed/explorations/2026-06-08-Agent-Behavioral-Contracts---PhantomPolicy---Runtime-Enforce.md
title: Agent Behavioral Contracts + PhantomPolicy — Runtime Enforcement Architecture
date: 2026-06-08
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- abc
- agent
- context
- drift
- governance
- phantompolicy
- policy
- recovery
- talos
- tool
created: '2026-06-08'
updated: '2026-06-15'
status: budding
---

# Agent Behavioral Contracts + PhantomPolicy — Runtime Enforcement Architecture

**來源**:
- [arxiv:2602.22302](https://arxiv.org/html/2602.22302) — Bhardwaj (Accenture, 2026-02-25)
- [arxiv:2604.12177](https://arxiv.org/html/2604.12177v1) — Wu & Gong (Atlassian, 2026-04-14)

**探索日期**: 2026-06-08

---

## 核心發現

### 1. Agent Behavioral Contracts (ABC) — C=(P,I,G,R)

**論文架構**：
- **C=(P,I,G,R)**: Preconditions, Invariants (hard/soft), Governance policies (hard/soft), Recovery mechanisms — 這是首個將 Design-by-Contract 引入 autonomous AI agent 的正式 framework
- **(p,δ,k)-satisfaction**: 機率性 contract compliance — with probability p, deviations within tolerance δ, recovery within k steps
- **Drift Bounds Theorem**: 若 recovery rate γ > natural drift rate α → expected drift bounded at D* = α/γ。Gauss concentration for stochastic setting
- **Compositionality Theorem**: 當四個條件滿足（interface compatibility, pre/post chaining, governance consistency, recovery isolation），multi-agent chain 的 contract guarantees 可以 composition

**ContractSpec DSL**（Section 5）:
- YAML-based domain-specific language
- Hard/soft constraint separation
- Expression-based predicates
- File-reference composition for multi-agent pipelines

**AgentAssert runtime library**:
- Sub-10ms per-action overhead
- 1980 sessions across 7 models from 6 vendors
- 88–100% hard constraint compliance
- D* < 0.27 across extended sessions

**Key experimental results**:
- Contracted agents detect 5.2–6.8 soft violations/session that uncontracted baselines miss entirely (p<0.0001, Cohen's d=6.7–33.8)
- Recovery contributes largest marginal improvement to reliability Θ (dominant contributor)
- Llama 3.3 70B: best overall reliability; Mistral Large 3: most room for improvement

### 2. PhantomPolicy — Policy-Invisible Violations

**問題定義**：
- LLM agent execute actions that are syntactically valid, user-sanctioned, semantically appropriate — but still violate org policy
- 原因：facts needed for correct policy judgment are **hidden at decision time** (not in agent-visible context)
- 這是 cooperative, non-adversarial setting，不是 jailbreak 或 prompt injection

**8 種 violation categories**：
| Category | Invariant |
|---|---|
| Context boundary | I2: ContextBoundary |
| Text-output leakage | I4: ContentFingerprint |
| Oversharing | I3: InformationFlow |
| Audience restriction | I3: InformationFlow |
| Accumulated session leakage | I3: InformationFlow |
| Cross-context dataflow | I3: InformationFlow |
| High-value resource protection | I7: Liveness |
| Temporal validity | I1: ActiveRecipient |

**Sentinel 架構**：
- 每個 agent action 視為對 org knowledge graph 的提議 mutation
- 執行 speculative execution materializes post-action world state
- 驗證 graph-structural invariants → Allow/Block/Clarify
- 7 invariants covering all 8 categories
- O(|M|) per-action verification cost

**核心結果**：
- 90–98% violation rates across models (when policy state hidden)
- Sentinel: 92.99% accuracy, 92.71 F1 (vs. content-only DLP 68.83% accuracy)
- **World-model coverage 是 enforcement quality 的硬約束**：Coverage(W,V)=1.0 才能 100% recall；coverage 降解時 recall 同步降解，invariant engineering 無法補償

---

## 對 Hermes 的啟發

### 1. Talos Governance Pipeline — ABC Contract Composition

ABC 的 Compositionality Theorem 正好對應 Talos 的 multi-agent coordination：
- C1 (Interface compatibility) ↔ Handoff invariant between Hestia↔Talos
- C2 (Pre/post chaining) ↔ 雙 agent 的 tool call sequencing
- C3 (Governance consistency) ↔ Talos 的 tool scoping policy
- C4 (Recovery isolation) ↔ 各自的 recovery mechanism 不破壞對方的 contract state

**實際應用**：Talos 的 governance policy (tool surface, scope limits) 可以正式化為 ABC contract，用 ContractSpec YAML 表述，AgentAssert-style runtime enforcement。

### 2. PhantomPolicy 的 World-Model Coverage 原則

**核心設計原則**：
> "Policy enforcement should be architecturally separated from model reasoning."

這與 `guardian-sandboxing-gradient` (WS-029) 的 L2/L3 層次完全一致：
- L1: tool scoping (model's own capability limit)
- L2: gateway mediation (separate enforcement layer)
- L3: container isolation (architectural separation)

PhantomPolicy 的 world-model coverage 問題呼應：
- **Talos 作為 guardian agent**：需要維持一個 policy-relevant world model (entity attributes, relationships, scope tags)
- 這正是 `heartbeat_learning.py` drift penalty 的另一面 — drift penalty 管 internal distillate 的穩定性；world model 管 external policy state 的覆蓋率

### 3. Drift Detection — 與 SSGM / heartbeat_learning.py 的交叉

ABC 的 Drift Bounds Theorem (D* = α/γ) 與 SSGM framework 的 bounded semantic drift (Theorem 1) 高度互補：
- SSGM: periodic reconciliation bounds drift
- ABC: recovery rate > natural drift rate → drift bounded

對 WS-035 (heartbeat_learning.py drift penalty) 的啟發：
- heartbeat_learning.py 的 distillate drift penalty 可以建模為 ABC 的 soft constraint violation
- Recovery mechanism (γ) vs natural drift rate (α) 的框架可以直接移植

### 4. PhantomPolicy 的 8-category taxonomy → Hearth 協作場景

PhantomPolicy 的 violation categories 幾乎可以直接映射到 Hearth 協作：
- **Accumulated session leakage** ↔ Hestia→Talos 的 thread 資訊意外流入不該看到的 context
- **Context boundary** ↔ internal channel ↔ external scope 的嚴格分離
- **Oversharing** ↔ 过度 broad 的訊息共享

**實務對應**：Talos 的 comms scope limiting（只在 thread 內回覆、不主動外傳）正是對這類 violation 的防禦。

### 5. Sentinel 的 Graph Invariants → Talos 的 Tool Call Validation

Sentinel 的 7 graph invariants 覆蓋 8 種 violation categories，全部來自 graph structure 而非 content inspection：

| Invariant | 覆蓋 categories |
|---|---|
| I1: ActiveRecipient | Temporal validity |
| I2: ContextBoundary | Context boundary |
| I3: InformationFlow | Oversharing, Audience, Accumulated leakage, Cross-context |
| I4: ContentFingerprint | Text-output leakage |
| I5: RecipientContext | (auxiliary) |
| I6: ScopeBoundary | (auxiliary) |
| I7: Liveness | High-value resource protection |

**對 Talos 的啟發**：將 tool call 視為對 Hermes 內部 state graph 的 mutation，invariant 驗證作為 tool call 的 pre-check — 這比直接檢查 tool output content 更 robust（不怕 invisible state）。

---

## 未追蹤 leads

- ABC reference implementation + AgentContract-Bench (subject to IP clearance) — 等 release
- ContractSpec YAML schema (Section 5.1) — 可直接作為 Talos governance policy 的 specification format
- PhantomPolicy public release (8 categories, 120 cases) — benchmark for Talos governance enforcement quality

---

## ✅ 本次探索完成

