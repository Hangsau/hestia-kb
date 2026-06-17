---
_slug: 40-Resources-_mixed-explorations-2026-05-31-Exploration--Mnemonic-Sovereignty---arxiv-2604-16548v1
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-Exploration--Mnemonic-Sovereignty---arxiv-2604-16548v1.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 19:\n    title: Exploration: Mnemonic Sovereignty — arxiv:2 ... \n \
  \                     ^"
_raw_fm: '

  title: Exploration: Mnemonic Sovereignty — arxiv:2604.16548v1

  date: 2026-05-31

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, arxiv, gate, governance, https, llm, memory, org, section,
  write]

  created: 2026-05-31

  updated: 2026-06-15

  status: active

  '
title: 'Exploration: Mnemonic Sovereignty — arxiv:2604.16548v1'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Exploration: Mnemonic Sovereignty — arxiv:2604.16548v1

**日期**: 2026-05-31
**來源**: [Survey on the Security of Long-Term Memory in LLM Agents](https://arxiv.org/html/2604.16548v1)
**類型**: 探索筆記（Phase-Locked）

---

## Per-Source Insights

### 核心概念：Mnemonic Sovereignty

> "A system's verifiable, recoverable governance over what may be written, who may read, when updates are authorized, which states must remain auditable, and which states may be forgotten."

這是本論文提出的規範性目標。直接翻譯：記憶主權。相較於「記憶能力」，論點是：下一代安全 Agent 的差異化將不在於 recall capacity，而在於**記憶治理的品質**。

**對 Talos 的直接價值**：
- WS-035 (heartbeat_learning drift penalty) 缺少的設計層——論文明确指出 drift 是 benign-persistence failure 的子類，需要 `confidence_valid_until` + event-driven invalidation，而非只靠 decay
- governance middleware 的設計方向（Section 12.3 Area 2：用 LLM 作為記憶安全工具）直接呼應 `exploration-tool-scoping-gradient` 的方向

### 六階段記憶生命週期（Section 3）

| Phase | Security Objective | Key Threat |
|---|---|---|
| **Write** | Integrity | Memory injection, experience-based poisoning |
| **Store** | Governance | Compression-amplified toxins, silent retention |
| **Retrieve** | Integrity + Availability | RAG poisoning, retrieval corruption |
| **Execute** | Integrity | Context assembly → action steering |
| **Share** | Confidentiality | Cross-agent contagion, internal channel leakage |
| **Forget/Rollback** | Governance | No verified deletion across substrates |

**重要發現**：文獻集中在 Write 和 Retrieve 階段的攻擊；Store/Forget 階段、Confidentiality、Availability 和 **benign-persistence axis**（非攻擊性記憶失效）研究嚴重不足。

### Benign-Persistence Axis（不需攻擊者就會發生的失效）

Section 12.2 發展這個概念：
- 共享 store 的靜默跨用戶污染
- profile facts 過度泛化到不适用的上下文
- 記憶引起的馬屁精行為（sycophancy）

**對 Talos 的啟發**：heartbeat_learning.py 的 distillate 有時會產生與前期結論相悖的語義跳躍——這不只是「drift」，而是 benign-persistence failure。需要：

1. `confidence_valid_until` — 高相關性事實突然失效的 explicit detector
2. **Access recency re-rank** — Mem0 blog (2026-05-13) 提出：recent boost 1.5×, idle dampen 0.3×；論文 Section 5.4 的 retention/aging 討論補充了另一個視角
3. **Event-driven invalidation** — 不同於 time-based decay

### 三個關鍵發現（Section 1 總結）

1. **研究空白**：文獻集中在 write-time 和 retrieve-time integrity attacks；confidentiality、availability、store/forget phases、benign-persistence failures 嚴重不足
2. **架構缺口**：No published architecture covers all 9 governance primitives；write-gate validation 和 post-deletion verification 是所有系統的共同盲點
3. **LLM-as-tool 匱乏**：用 LLM 作為記憶安全的自動紅隊、審計員、遺忘驗證器——這個方向目前稀疏但至關重要

### 九個治理原語（Section 11.2，Table 1）

論文識別出 9 個 governance primitives，聲稱「沒有任何已發布架構完整覆蓋」。具體九個：

1. Write-gate validation（寫入前驗證）
2. Provenance tracking（溯源追蹤）
3. Versioning + snapshots（版本控制）
4. Compression audit（壓縮審計）
5. Principal-scoped retrieval（主體範圍檢索）
6. Dynamic policy enforcement（動態策略執行）
7. Forgetting protocol（遺忘協議）
8. Cross-substrate deletion verification（跨基底刪除驗證）
9. Audit retention compliance（審計保留合規）

**Write-gate validation** 和 **Post-deletion verification** 是共同盲點——這正是 Talos governance pipeline 需要加強的方向。

### Section 10 — 現有防禦的地圖

| Phase | Defense Approach | Gap |
|---|---|---|
| Write | Pre-consolidation validation | 幾乎沒有系統實作 write-gate |
| Store | Versioning, provenance, compression audit | 大多數系統缺少 compression lineage preservation |
| Retrieve | Filtering, consensus, clustering | 單獨的 retrieve-time filtering 不足以應對記憶污染 |
| Execute | Information-flow control | 很少被討論 |
| Share | Principal-scoped policy | 現有架構對 multi-agent 共享受限 |
| Post-breach | Forensics, recovery | 幾乎沒有 cross-substrate forgetting 驗證 |

### 攻擊分類摘要（Sections 4-9）

**Write-path attacks**:
- Query-induced memory injection (Section 4.2) — 不需要直接 prompt，讓 agent 自己把錯誤資訊寫入記憶
- Experience-based poisoning (Section 4.3) — 從事實到程序的污染
- Environment-injected poisoning (Section 4.4) — 世界成為寫入介面（Zou et al. 2026 的環境注入記憶污染）
- RAG corpus poisoning as approximate threat model

**Retrieve-path attacks**:
- RAG poisoning at retrieve phase
- From retrieved content to control-flow hijacking
- Full attack chain: external content → persistent action steering

**Share-phase threats** (Section 7):
- Multi-agent contagion：jailbreak 跨記憶傳播
- Internal channels dominate（不是 user-facing output）— 這與 El Yagoubi et al. 2026 的隱私洩漏研究一致
- Worm-like propagation in production

**Confidentiality** (Section 8):
- Black-box memory extraction
- User visibility gap
- Internal-channel leakage in multi-agent pipelines
- Parametric memory ≠ memory system（拉開這兩者的討論很重要）

### 架構發現（Section 11）

- **No published architecture is full-spectrum** — 所有系統都有盲點
- **Virtual-memory architectures** prioritize capability and efficiency，expose more governance primitives than retrieval-only stores
- **Metadata-bearing "memory-as-resource" designs** expose more governance primitives than retrieval-only stores
- Multi-user and cognitive-architecture framings bring orthogonal contributions
- **Agent harness as governance substrate** — Section 11.4 提出 agent harness 是治理基底，呼應 WS-035 的設計方向

### 12 個研究優先方向（Section 12.6）

P1: Composable defense semantics
P2: Lifecycle-wide benchmark
P3: Post-breach evaluation
P4: Memory lineage attribution

A1: Typed-write schemas with chain-of-custody provenance
A2: Compression-lineage preservation
A3: Principal-scoped retrieval with dynamic policy
A4: **Verified forgetting across substrates** ← 這是最大缺口

Area 2（Section 12.3）: **LLM-as-tool for memory security** — 用 LLM 作為：
- Memory defender
- Memory attacker
- Automated memory red-teamer

---

## Hermes 啟發

### 1. drift penalty 的設計缺口已獲確認

論文 Section 12.2 的 benign-persistence axis 直接確認：heartbeat_learning.py 缺少 `confidence_valid_until` 機制（SSGM 的 periodic reconciliation 是參考方向，但這篇進一步指出需要 event-driven invalidation）。

**設計方向**：
- 新增 `confidence_valid_until` 欄位：高相關性事實突然失效的 explicit detector
- Access recency re-rank：Mem0 的 recent boost 1.5× / idle dampen 0.3× 可以直接借鑒
- Event-driven invalidation 替代 time-based decay

### 2. Write-gate validation 是 Talos governance 的核心缺口

9 個 governance primitives 中，write-gate validation 是「共同盲點」——這意味著無論哪個 memory system 都缺少寫入前的驗證層。

**具體設計方向**：
- 在 heartbeat_learning.py 的 distillate 層加入 write-gate：每次 distillate 寫入前，檢查是否與現有 distillate 矛盾
- 衝突檢測：用矛盾分數（contradiction score）取代單純的相似度閾值

### 3. Verified forgetting 是最大缺口

A4: Verified forgetting across substrates — 沒有人做好。這對 Talos 的意義：當 distillate 被判定為 stale 並刪除時，需要有可驗證的刪除證據（不只是 soft delete）。

### 4. LLM-as-tool for memory security（Area 2）

這是論文強調的「稀疏但關鍵」方向：用 LLM 自動紅隊測試記憶系統的安全性。對 Talos 的具體應用：
- 定期用 LLM 生成「記憶污染 prompt」，測試 heartbeat_learning.py 的 write-gate 是否能攔截
- 用 LLM 驗證 distillate 的刪除是否真的生效（cross-substrate verification）

### 5. 九個治理原語的系統化對照

| Primitive | Hermes 現況 | Gap |
|---|---|---|
| Write-gate validation | ❌ 無 | 需要新增 |
| Provenance tracking | 部分（commit history） | 需加到 distillate 層 |
| Versioning + snapshots | ❌ 無 | 考慮 heartbeat state snapshots |
| Compression audit | ❌ 無 | drift penalty 需補充 |
| Principal-scoped retrieval | N/A | 多 agent 場景需 |
| Dynamic policy enforcement | 部分（cron enabled_toolsets） | 需整合到 governance |
| Forgetting protocol | ❌ 軟刪除 | 需驗證刪除 |
| Cross-substrate deletion verification | ❌ 無 | Area 2 需解決 |
| Audit retention compliance | 部分（memory-tracker） | 需加強 |

---

## 未追蹤 Leads

- https://arxiv.org/abs/2604.04853 — MemMachine: ground-truth-preserving memory system
- https://arxiv.org/abs/2604.01350 — Unintentional cross-user contamination in shared-state LLM agents (benign-persistence axis)
- https://arxiv.org/abs/2603.21654 — Secure RAG comprehensive review (threats, defenses, benchmarks)
- https://arxiv.org/abs/2604.02623 — Poison once, exploit forever: environment-injected memory poisoning (Zou et al. 2026)
- https://arxiv.org/abs/2510.02964 — External data extraction attacks against RAG
- https://www.owasp.org/www-project-agentic-ai-threats/ — OWASP Agent Memory Guard (runtime memory protection reference implementation)

---

## ✅ 本次探索完成

**延續自**: (none — 從 vault 的 SSGM 筆記出發，但本篇是新 paper)

**相關 vault 筆記**:
- [[2026-05-29-SSGM-Framework---Bounded-Drift-via-Governance-Middleware]] — SSGM 框架（Theorem 1 bounded drift）
- [[2026-05-31-探索筆記-Agent-Memory---Staleness-與架構測繪]] — staleness vs decay 框架
- [[2026-05-30-探索-Agent-Memory-Architecture---2026-State-of-the-Field]] — 架構測繪
