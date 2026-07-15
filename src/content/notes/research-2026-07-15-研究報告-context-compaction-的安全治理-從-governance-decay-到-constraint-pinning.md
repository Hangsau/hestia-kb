---
_slug: research-2026-07-15-研究報告-context-compaction-的安全治理-從-governance-decay-到-constraint-pinning
_vault_path: research/2026-07-15-研究報告-context-compaction-的安全治理-從-governance-decay-到-constraint-pinning.md
tags:
- research
- knowledge
- ai-agent
created: '2026-07-15'
version: 1
source_report: 2026-07-15-context-compaction-governance-decay-constraint-pinning.md
source_url: ''
type: research
fingerprint: constraint, context, tool, policy, compaction, governance, agent, pinning,
  memory, pinned
title: 研究報告：Context Compaction 的安全治理：從 Governance Decay 到 Constraint Pinning
status: seedling
updated: '2026-07-15'
---

# 研究報告：Context Compaction 的安全治理：從 Governance Decay 到 Constraint Pinning

## Version 1 — 2026-07-15

### 核心觀念
**問題**：長時間運作的 LLM agent 必須壓縮、摘要或淘汰 context，否則 token budget、latency 與 inference cost 會隨 session 長度失控。但 context 不只是對話紀錄；它同時承載 tool policy、權限邊界、使用者限制、回復策略與安全規則。 問題因此不是單純的「摘要品質」：**被壓縮掉的規則，對 agent 而言等同不存在**。2026 年的研究把這種失效命名為 **Governance Decay**，並以 ConstraintRot 測試 compaction 後安全約束是否仍可被遵守。這對 firn 特別重要：firn 的長流程…

**洞見**：**可信度：HIGH｜類型：論文｜新穎度：NEW**。Governance Decay 直接把 compaction 從效能元件提升為安全邊界。若 agent 能在第 1 turn 遵守規則、在第 50 turn 因摘要遺失規則而違規，那「模型 alignment」沒有涵蓋完整系統；真正的 policy surface 包含 context pipeline。 **可信度：MEDIUM｜類型：論文 + framework 實作｜新穎度：EXTENSION**。現有 agent framework 普遍把 memory 表現成文字或 message list；更穩健的設計是把 memory 拆成…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 Context compaction 的安全失效模型

典型流程如下：

```text
raw conversation / tool traces
          │
          ▼
  compaction or summarization
          │
          ▼
  shorter context + surviving constraints
          │
          ▼
  next agent decision
```

Governance Decay 的核心觀察是：若 constraint 沒有被保留，agent 在它原本可見時可能 0% 違規，壓縮後卻會開始呼叫禁止的 tool 或違反操作政策。研究中的 ConstraintRot 以多輪 episode、不同模型與硬/軟約束測量這種衰退；報告的結果顯示 compaction 後違規率可由 0% 升至 30% 以上，攻擊者甚至能透過 **Compaction-Eviction Attack** 偏置摘要器，讓特定 constraint 被刪除。

### 2.2 Constraint Pinning

最簡單也最值得先做的修法是 **Constraint Pinning**：將安全與治理規則從一般可摘要 context 中抽離，作為不可被一般 compactor 淘汰的結構化區塊。

```python
PINNED_KINDS = {
    "operator_policy",
    "tool_schema",
    "permission_boundary",
    "cost_guard",
    "user_hard_constraint",
}

compactable, pinned = partition(messages, is_pinned)
summary = summarize(compactable)
new_context = [*pinned, summary, recent_tail(messages)]
assert validate_constraints(new_context, pinned)
```

關鍵不是把所有內容都 pin——那會讓 context budget 重新爆炸——而是明確區分：

- **Hard constraints**：不可刪除；例如禁止執行的命令、tool schema、HITL 要求。
- **Soft policies**：可摘要但要保留 provenance 與版本；例如偏好、風格、一般工作原則。
- **Ephemeral evidence**：可淘汰；例如已完成的中間推理、冗餘 tool output。

### 2.3 Compression 後驗證，而不是相信摘要

每次 compaction 都應產生一個可檢查的 artifact：保留哪些 constraint、刪掉哪些 constraint、來源訊息範圍、摘要版本與 hash。驗證器可做 schema 檢查、constraint ID coverage 檢查，以及對高風險 tool 的 policy replay。

```text
before:  C1, C2, C3, C4
compaction report:
  retained: C1, C2, C4
  evicted:  C3 (reason=ephemeral evidence)
  policy_hash: ...
validator:
  required={C1,C2,C4} ⊆ retained ? PASS : BLOCK
```

### 2.4 與其他 context 技術的關係

- **Rolling summary / memory extraction**：省 token，但若沒有治理分類，會把 safety policy 當成普通 prose。
- **Retrieval memory**：能在需要時找回規則，但 tool decision 發生前不保證 retrieval 成功；對 hard constraint 不應只依賴向量搜尋。
- **KV cache / stateful inference**：降低重算成本，並不解決「規則是否仍存在」；cache 讓錯誤 context 更快被重複使用，這點有點諷刺。
- **Context window 擴大**：延後問題，不是治理方案；長 session 仍會遇到成本與 attention 稀釋。

### 思考
## 4. Limitations / Honest Assessment

1. **研究結果仍需外部複製**：ConstraintRot 的模型數、episode 設計與 constraint 類型值得參考，但不能直接推論所有 production agent 都會有同樣違規率。
2. **摘要器不是唯一攻擊面**：tool result injection、prompt injection、memory poisoning、stale checkpoint 也能改變 governance state；pinning 只處理其中一段。
3. **「保留 constraint」不等於「理解 constraint」**：字面保留可能因位置、衝突指令或 tool schema 變更而失效。
4. **額外 token 與 latency**：pinning、validation、policy replay 都有成本；若每個低風險 turn 都跑完整驗證，會過度工程化。
5. **Policy drift**：長期系統需要規則版本、撤銷、租約與 scope；單純永久 pin 會製造新的一致性 bug。
6. **安全指標可能被 gaming**：只看 constraint-retention rate 會鼓勵系統保留文字，而非在實際 tool call 上拒絕危險操作。

獨立判斷：這不是「context window 的下一個技巧」，而是 agent runtime 的 governance primitive；但目前最強的證據支持的是風險存在與簡單 mitigation 有效，尚不足以證明某個 pinning policy 在所有 agent domain 都接近零違規。

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### firn：優先做 typed context governance layer

**建議模組**：`context` / `memory` / `tool gateway` / `observability`。若 firn 的實際命名不同，應找負責 context distillation、delegation state 與 tool authorization 的等價模組。

1. **建立 `ConstraintRegistry`**：每條規則有 `id`、`kind`、`scope`、`severity`、`version`、`expires_at`、`source`。
2. **改 compactor contract**：輸入不再只有 messages；輸出包含 `summary`、`retained_constraint_ids`、`evicted_ids`、`source_hashes`。
3. **加入 constraint pinning**：先 pin `operator_policy`、`tool_registry_schema`、`permission_boundary`、`cost_guard` 與 HITL gate。
4. **tool gateway 二次檢查**：高風險 tool 不接受模型自行宣稱「已獲准」，必須由 runtime policy engine 判定。
5. **發出 trace attributes**：`context.compaction_ratio`、`context.pinned_tokens`、`governance.retention_ok`、`governance.policy_version`、`tool.authorization.decision`。
6. **建立 regression suite**：同一 workflow 在 1、10、50、100 turns 執行；比較無壓縮、普通摘要、pinning、pinning+gateway enforcement。
7. **做 adversarial compaction test**：把要保留的 constraint 放在不同位置，混入長 tool output 與 prompt injection，檢查是否仍被保留且實際阻擋 tool call。

**實作難度**：

- constraint registry + partition：**MODERATE**
- hash/version/retention validator：**TRIVIAL–MODERATE**
- tool gateway enforcement：**MODERATE–HARD**
- 完整長 horizon benchmark：**HARD**
- 學習型 policy optimizer：**RESEARCH-ONLY**

**付費 API**：不需要。免費方案與 local model 足以做 registry、壓縮、驗證與測試；付費模型只會影響摘要品質與 benchmark 成本，不是架構必要條件。

### Managed-agents / 其他專案

managed-agents 是 batch runner，不應假裝自己是 autonomous agent；但其 playbook 結果可加入 `policy_hash` 與 `constraint_ids`，避免批次任務重跑時拿到不一致的 governance context。對 cron pipeline，最值得做的是在報告抽取前 pin 輸出格式與路徑限制，並在腳本寫入 vault 前驗證來源 report 的 hash。


### 來源

- 原始報告：2026-07-15-context-compaction-governance-decay-constraint-pinning.md
- 類型：
- 連結：
