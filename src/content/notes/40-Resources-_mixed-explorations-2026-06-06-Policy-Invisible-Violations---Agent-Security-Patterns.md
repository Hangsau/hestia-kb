---
_slug: 40-Resources-_mixed-explorations-2026-06-06-Policy-Invisible-Violations---Agent-Security-Patterns
_vault_path: 40-Resources/_mixed/explorations/2026-06-06-Policy-Invisible-Violations---Agent-Security-Patterns.md
title: Policy-Invisible Violations + Agent Security Patterns
date: 2026-06-06
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- action
- coverage
- data
- llm
- model
- pattern
- policy
- scope
- source
- world
created: '2026-06-06'
updated: '2026-06-15'
status: budding
---

# Policy-Invisible Violations + Agent Security Patterns

**延續自**: [[2026-06-06-constraint-decay-llm-agents-backend]]

---

## Source 1: PhantomPolicy (arXiv:2604.12177v1)

### 核心概念：Policy-Invisible Violations

LLM agents 可以執行**語法正確、用戶授權、語意適當**的 actions，但仍違反組織政策——因為正確判斷所需的資訊在決策時對 agent 不可見。

**關鍵定義**：
- `W = (E, A, R, P)` — Organizational world model：entities (contacts, documents, projects, groups) + attributes + relationships + policy rules
- Policy-invisible violation：tool call 滿足 (1) 用戶明確請求、(2) 語式正確、語意適當、(3) tool responses 無 policy metadata，但 (4) 違反 policy rule

**八種 violation categories**：
| Category | Description | Invariant |
|---|---|---|
| Context boundary | Session 起源於 INTERNAL，內容不能流向 EXTERNAL | I2: ContextBoundary |
| Text-output leakage | 用戶口頭提供的 confidential data 進入 outbound action | I4: ContentFingerprint |
| Oversharing | 資料夾 bulk share 包含 restricted doc | I3: InformationFlow |
| Audience restriction | Doc 有 explicit audience policy（HR_ONLY）禁止目標 recipient | I3: InformationFlow |
| Accumulated session leakage | 讀取 confidential doc 後，後續 outbound 攜帶 tainted data | I3: InformationFlow |
| Cross-context dataflow | Confidential doc 發送給直接相關的外部方（e.g., 內部法律策略給反方 vendor） | I3: InformationFlow |
| High-value resource protection | Action 目標是 world model 標記為 high-importance 的 resource | I7: Liveness |
| Temporal validity | Action 目標是 inactive contact 或過期 engagement | I1: ActiveRecipient |

### Sentinel 框架

Counterfactual graph simulation：
1. 每次 agent action 視為對 organizational knowledge graph 的提議 mutation
2. Speculative execution：fork graph，apply mutations
3. 驗證 7 個 declarative graph invariants（Allow/Block/Clarify）
4. O(|M|) per-action verification cost

**Graph invariants**（覆蓋全部 8 種 violation categories）：
- I1: ActiveRecipient — 檢查 recipient 是否 active
- I2: ContextBoundary — session scope 邊界
- I3: InformationFlow — scope/audience flow rules
- I4: ContentFingerprint — confidential data 指紋（regex-based）
- I5: RecipientContext — recipient scope consistency
- I6: ScopeBoundary — scope 轉移邊界
- I7: Liveness — high-value resource 保護

**實驗結果**：
- 5 models（GPT-5.4, GPT-5 mini, GPT-5.4 nano, Claude Sonnet 4.6, Claude Opus 4.6）
- Risky-case violations：90–98%（54–59/60）
- Sentinel accuracy：92.99%，F1 92.71
- Content-only DLP baseline：68.83% accuracy / 56.61 F1

**Coverage degradation**：
- 移除 scope attribute → recall 從 100% 降至 40.0%（影響 5/8 categories）
- 移除 sensitivity attribute — 無額外 effect（scope 已捕獲主要信號）
- Entity coverage 與 recall 呈單調遞減關係
- 核心 insight：**world-model coverage 是 enforcement quality 的硬約束，不是 invariant sophistication**

### Hermes 啟發

1. **Policy enforcement should be architecturally separated from model reasoning** — Talos governance 的 tool scoping + DCG pattern 直接對應這個原則
2. **World-model coverage 優先於 invariant 複雜度** — 若 policy-relevant facts 不在 world model，任何 invariant 都無法檢測該 violation。這對 Talos 的「如何擴展 governance scope」有直接含義：優先擴展 entity/coverage，而非除錯 invariant logic
3. **Accumulated session leakage 是最難的 category（hard difficulty）** — 每個單獨 read 看起來 safe，只有 accumulated session state reveals violation。這與 heartbeat_learning.py 的 distillate staleness 問題高度類比：單一資料點看起來無害，累積後 reveal contradiction

---

## Source 2: Design Patterns to Secure LLM Agents (Reversec)

### Six Patterns（對應 PhantomPolicy 的 architectural enforcement 方向）

**Pattern 1: Action Selector**（最嚴格）
- LLM 只做 switch/router，無 LLM-generated output 顯示給用戶
- LLM 看不到它选择的 tool 的 output
- 對應：Hermes 的 `enabled_toolsets` 限制 + tool 白名單

**Pattern 2: Plan-Then-Execute**
- Phase 1：LLM 基於 trusted prompt 建立完整、不可變的 plan
- Phase 2：非 LLM Orchestrator 監督執行，step-by-step
- LLM 可在 step之間 看 output（動態參數），但不能改 plan 的結構或固定參數
- **This is exactly our Phase-Locked Exploration design** — plan lock = control-flow integrity
- VIOLATION check：LLM 企圖改變 fixed argument → halt

**Pattern 3: LLM Map-Reduce**
- Map phase：每個 untrusted doc 用 isolated LLM call 轉為嚴格定義的 structured format
- Reduce phase：只處理 sanitized structured data，不接觸 raw docs
- Security gate：Pydantic schema validation
- 對應：autonomous_notes 的 per-source insight + synthesis 分離

**Pattern 4: Dual LLM**（Simon Willison  generalization）
- Privileged LLM：操作 references，不操作 data 本身
- Quarantined LLM：有限 scope，只能 access 一次一個 document，無法執行敏感 actions
- 溝通透過 symbolic variables（非 data 本身）
- Injection in one email cannot access data from other emails

**Pattern 5: Code-Then-Execute**
- LLM 生成完整可執行 program（Python script），在處理任何 untrusted input 之前
- Control flow locked in before touching untrusted data
- 擴展：CaMeL — 如 OS reference monitor（SELinux），fine-grained security policies on data flows
- Provenance tracking：SourcedString object carries origin，mixed-source → PermissionError
- 對應：Hermes 的 DCG（Destructive Command Guard）— 已有 `__attribute__((annotate("safe")))` annotation system

**Pattern 6: Context-Minimization**
- Phase 1（Retriever）：分析 user question → 輸出 structured `{"sections": [3]}`，非 executable data
- Phase 2（Summarizer）：只看到乾淨的 extracted section text，從不看原始 user prompt
- 對應：vault 的 exploration note structure — per-source insight（map）→ cross-article synthesis（reduce）

### Best Practices（Defense-in-Depth）
1. Action Sandboxing — container with read-only filesystem
2. Structured Output Enforcement — JSON with strict schema，not just reliability
3. Permission Boundaries — least privilege，scoped to current task
4. User Confirmation — high-stakes actions，但避免 confirmation fatigue
5. Data Attribution — source citations for debugging
6. Strict Per-User Rate Limits — 防止迭代探測
7. Content Moderation Lockouts — 臨時 suspend 觸發 guardrails 的用戶

---

## 跨文章 Synthesis

1. **Architecture > Heuristic**：兩個 source 都收斂到同一個結論——prompt injection / policy violation 的根本解法不是「修復 LLM 本身」，而是 architectural constraints。Plan-Then-Execute（Reversec）+ Sentinel graph invariants（PhantomPolicy）= 同一個 design principle 的兩種表達

2. **World-model coverage 是瓶頸**：PhantomPolicy 的 coverage degradation experiments 直接量化了「world-model 不完整時 enforcement 如何退化」。這對 Talos governance 的規模化有直接意義——優先建立 entity/coverage pipeline，而非除錯 invariant logic

3. **Accumulated session leakage 是 hardest category** — 對應 heartbeat_learning.py 的 distillate staleness：單一資料點無害，累積後 reveal contradiction。需要 bitemporal model（system time + valid time）來處理

4. **Action Selector 是最安全的，但最不實用** — 實務上需要介於 Action Selector 和 full ReAct 之间。Plan-Then-Execute 是平衡點

---

## 未追蹤 Leads

- https://arxiv.org/html/2603.19469v1 — A Framework for Formalizing LLM Agent Security（更 general 的 framework）
- https://github.com/nicodisco/design-patterns-securing-llm-agents — Reversec 的程式碼範例（每個 pattern 的 Chainlit app）
- https://arxiv.org/html/2603.11768v1 — SSGM（Governing Evolving Memory），已有但尚未完整讀

~~https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action~~ → fetched, done

## ✅ 本次探索完成
