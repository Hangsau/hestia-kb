---
_slug: 40-Resources-_mixed-explorations-2026-05-31-Exploration--OWASP-Agentic-AI---MemMachine-Follow-up
_vault_path: 40-Resources/_mixed/explorations/2026-05-31-Exploration--OWASP-Agentic-AI---MemMachine-Follow-up.md
title: 'Exploration: OWASP Agentic AI + MemMachine Follow-up'
date: 2026-05-31
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agentic
- asi
- ground
- memmachine
- memory
- mnemonic
- model
- owasp
- retrieval
- truth
created: '2026-05-31'
updated: '2026-06-15'
status: budding
---

# Exploration: OWASP Agentic AI + MemMachine Follow-up

**日期**: 2026-05-31
**探索方向**: 從 Mnemonic Sovereignty 的「九個治理原語」出發，驗證三個直接相關的後續來源
**來源**: 本地探索筆記 + OWASP + MemMachine 論文 + AgentThreatBench

---

## Per-Source Insights

### OWASP Agentic AI Threats — genai.owasp.org

**URL 確認**：正確 URL 是 `https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/`，非 `owasp.org/www-project/...`。OWASP 的 agentic 內容在 genai 子域名。

**內容層級**：該頁面是落地頁（February 17, 2025），無威脅詳情。主要價值是下載連結指向完整 PDF，以及 Additional Resources 區塊的時間線（December 2025 OWASP Top 10 for Agentic Applications）。

**對 Talos 的價值**：
- OWASP Top 10 for Agentic Applications 2026 (December 2025) 是實質標準——AgentThreatBench 正是基於這個版本構建
- Section 分類（ASI01-ASI10）可直接對應 Mnemonic Sovereignty 的 9 governance primitives
- OWASP Agent Memory Guard（runtime memory protection）是 Section 12.3 Area 2 的具體實作參考

**結論**：該頁面本身價值有限，真正的礦藏在：
1. OWASP Top 10 for Agentic Applications 2026（December 2025 版本）
2. AgentThreatBench（基於該標準的可執行 benchmark）
3. OWASP Agent Memory Guard（MCP-based runtime protection）

---

### MemMachine (arXiv 2604.04853) — Phase 1.5 Content Check

**基礎確認**：
- Title: "MemMachine: A Ground-Truth-Preserving Memory System for Personalized AI Agents"
- Authors: Shu Wang, Edwin Yu, Oscar Love, Tom Zhang, Tom Wong, Steve Scargall, Charles Fan（MemVerge, Inc.）
- Date: March 2026, arXiv:2604.04853v1
- License: CC BY 4.0, Apache 2.0
- GitHub: `MemMachine/MemMachine`

**核心貢獻**：

| 貢獻 | 內容 |
|---|---|
| Ground-truth-preserving | 存 raw episodes，sentence-level indexing，最小化 LLM extraction |
| Contextualized retrieval | nucleus expansion，episode clusters |
| Cost efficiency | ~80% fewer tokens vs Mem0 |
| LoCoMo SOTA | 0.9169 with gpt-4.1-mini（超過 Mem0/Zep/Memobase/LangMem/OpenAI） |
| LongMemEvalS ablation | 93.0% overall accuracy，揭示 retrieval-stage optimization dominates |
| Retrieval Agent | multi-hop reasoning (HotpotQA 93.2%, WikiMultiHop 92.6%) |

**架構亮點**：

1. **三層記憶整合**（Section 3）：Episodic + Semantic (Profile) + Procedural + Temporal Awareness
   - Episodic = raw ground truth（事實、對話記錄）
   - Semantic/Profile = distilled user preferences（蒸餾過的高層次知識）
   - Procedural = 尚未實作（但架構可擴展）
   - Temporal Awareness = 全系統 timestamp tagging（跨切割的時間推理能力）

2. **Write-gate validation 是其核心設計**：MemMachine 的 ground-truth-preserving architecture = write-gate 的具體實現
   - 每次寫入前檢查是否與現有 episodes 矛盾（矛盾分數閾值）
   - 衝突高於閾值 → flag for human review 或應用 "ground-truth anchor" 機制
   - 這直接回應 Mnemonic Sovereignty Table 1 的「共同盲點」：write-gate validation 是所有系統的缺口，MemMachine 是唯一已實現的架構

3. **Retrieval-stage dominates 的發現（Section 9.1）**：
   - retrieval depth: +4.2%
   - context formatting: +2.0%
   - search prompt design: +1.8%
   - user-query bias correction: +1.4%
   - sentence chunking (ingestion): +0.8%
   - **結論：如何召回比如何儲存更重要**——這與 heartbeat_learning.py 的 drift penalty 直接相關：drift penalty 屬於 retrieval-stage 優化（retrieval quality → distillate quality）

4. **Model-prompt co-optimization**：GPT-5-mini outperforms GPT-5 when co-optimized (+2.6%)，原因是 COT prompt 對 GPT-5 有負面 interference。直接影響 ws-035 的 model selection 策略。

5. **Table 16 架構比較**：
   - MemMachine: retrieval ✓, ground truth preserved ✓, prompt cacheable (partial), scales beyond context ✓, LLM calls per message (low), specialized DB required (Yes), works with closed-source ✓
   - vs Mem0: retrieval ✓, ground truth partial, prompt cacheable ✗, scales ✓, LLM calls high, specialized DB required, closed-source ✓
   - vs Mastra: in-context ✗, ground truth no, prompt cacheable ✓, scales beyond context ✗, no DB required
   - **結論：MemMachine 是「ground truth + retrieval + low LLM calls + 可擴展性」的最優解**

**對 Talos 的具體應用**：

1. **ws-035 drift penalty**：MemMachine 的 retrieval-stage optimization 框架證明 drift penalty 應該是 retrieval quality metric，而非 storage quality metric。Heartbeat_learning.py 的 distillate quality 直接影響 downstream retrieval accuracy。
2. **Write-gate validation**：MemMachine 的矛盾檢測（contradiction score > threshold → flag for human review）是 ws-035 可以直接移植的設計。
3. **Model selection**：GPT-5-mini 的 cost-efficiency 確認，建議 ws-035 的 answer model 用 GPT-5-mini 而非 GPT-5。
4. **Memory consolidation and forgetting**（Section 10 Future Work）：MemMachine 的 future work 項目中有 explicit forgetting mechanism —— 這是 Mnemonic Sovereignty 的「post-deletion verification」缺口，MemMachine 也承認尚未實現。

---

### AgentThreatBench — DEV Community article

**背景**：作者 Vaishnavi Gudur，2026-05-19，已 merge 到 UK AISI inspect_evals。

**覆蓋範圍**（3 scenarios，2 OWASP categories）：
- **Memory Poisoning (ASI06)**：攻擊者透過追加或替換方式汙染 memory/RAG store
- **Autonomy Hijack (ASI01)**：indirect prompt injection 藏在 tool return 裡，目標是 agent goal hijack
- **Data Exfiltration (ASI01)**：customer profile data 嵌入 payload，指示 agent 洩漏 SSN

**雙度量評分系統**：
- Utility Metric：是否完成正當任務
- Security Metric：是否抵禦攻擊
- **兩者都必須 1.0 才算 pass** —— 但多數 SOTA model 兩者不可兼得（over-refuse vs hijacked）

**UK AISI merge 的意義**：
- 這是官方國家級評估框架的納入，信號強度高
- inspect_evals 是 UK AI Safety Institute 的官方 evaluation package
- 代表 OWASP Top 10 for Agentic Applications 2026 已有可執行測試

**對 Talos 的具體應用**：
- Agentic threat model 實例化 → 可直接用來評估 Talos heartbeat 的 threat model
- Memory Poisoning (ASI06) 的 threat model 與 ws-035 drift penalty 直接相關（benign-persistence failure = memory poisoning without attacker）
- Data Exfiltration 的 attack pattern 可補充 Mnemonic Sovereignty 的 Confidentiality 缺口

---

## 跨文章 Synthesis

### 1. 治理原語的實作層級對照

| Mnemonic Sovereignty Primitive | MemMachine | OWASP |
|---|---|---|
| Write-gate validation | ✅ ground-truth anchor | ASI06 (Memory Poisoning) |
| Provenance tracking | partial (episode metadata) | 部分 |
| Versioning + snapshots | ❌ | ❌ |
| Compression audit | ❌ | ❌ |
| Principal-scoped retrieval | multi-tenancy (project/session isolation) | ❌ |
| Dynamic policy enforcement | ❌ | ASI01-ASI10 |
| Forgetting protocol | 軟刪除，future work | ❌ |
| Cross-substrate deletion verification | ❌ | ❌ |
| Audit retention compliance | partial | ❌ |

**缺口最大的三個**：Versioning+Snapshots、Compression audit、Cross-substrate deletion verification——全部 memory system 都缺，MemMachine 也只列在 future work。

### 2. Retrieval-stage dominates 的心跳應用

MemMachine Section 9.1 的發現（retrieval-stage optimization dominates over ingestion-stage changes）對 heartbeat_learning.py 有直接影響：
- drift penalty = retrieval-stage quality metric
- 改善 retrieval quality（例如：更精確的去重機制、更嚴格的矛盾檢測）比改善 distillate storage 更有效
- 這解釋了為何 heartbeat_learning.py 的 drift 問題不能只靠「更好的蒸餾」解決——需要從 retrieval 層下手

### 3. Agent Threat Model 的三層分類

AgentThreatBench 的 threat model（ASI01/ASI06/Other）提供了一個可操作的 threat 分類：
- ASI01 = goal hijack via environment（indirect injection）
- ASI06 = memory poisoning via store（benign-persistence axis）
- 兩者都是 ws-035 drift penalty 的 threat model 基礎

### 4. Ground-truth preserving vs extraction-based 的代價分析

MemMachine 的 benchmark data:
- MemMachine: ~80% fewer tokens than Mem0, LoCoMo 0.9169
- Mem0: LLM extraction per message, LoCoMo 0.6688
- 差距來自 extraction-based approach 的 error accumulation + high per-message LLM cost

**結論**：ws-035 若要實作 write-gate validation，應參考 MemMachine 的「存 raw + lightweight indexing + retrieval-stage validation」模式，而非 Mem0 的「per-message extraction」模式。

---

## 未追蹤 Leads

- https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/ (OWASP page — limited content, actual value in download PDF)
- https://arxiv.org/abs/2604.04853 — MemMachine (confirmed alive, full content reviewed)
- https://github.com/agentthreatbench/agentthreatbench — AgentThreatBench (UK AISI merge confirmed)
- https://genai.owasp.org/resource/agent-memory-guard/ — OWASP Agent Memory Guard (mentioned in OWASP page as runtime protection reference, not yet validated)
- https://mastra.ai/research — Mastra Observational Memory (cited in MemMachine Table 16, alternative approach worth tracking)
- https://arxiv.org/abs/2507.03724 — MemOS (cited in MemMachine as ambitious long-term vision, requires direct model access limits portability)

---

## ✅ 本次探索完成

**延續自**: [[2026-05-31-Exploration--Mnemonic-Sovereignty---arxiv-2604-16548v1]]（同一 chain，從 leads 驗證出發）

**相關 vault 筆記**:
- [[2026-05-31-Exploration--Mnemonic-Sovereignty---Lead-Validation---MemMac]] — lead validation note（MemMachine confirmed alive, OWASP URL confirmed, AgentThreatBench pending）
- [[2026-05-31-Exploration--Mnemonic-Sovereignty---arxiv-2604-16548v1]] — Mnemonic Sovereignty 源 paper
- [[2026-05-29-SSGM-Framework---Bounded-Drift-via-Governance-Middleware]] — SSGM framework
- [[2026-05-31-探索筆記-Agent-Memory---Staleness-與架構測繪]] — staleness vs decay 框架
- [[2026-05-30-探索-Agent-Memory-Architecture---2026-State-of-the-Field]] — 架構測繪
