---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Agent-Defense-Landscape-從-NIST-的架構缺陷到實作方案
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Agent-Defense-Landscape-從-NIST-的架構缺陷到實作方案.md
title: Agent Defense Landscape：從 NIST 的架構缺陷到實作方案
date: 2026-05-14
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- agentarmor
- canary
- fireclaw
- lilith
- mcp
- nist
- policy
- untrusted
- zero
created: '2026-05-14'
updated: '2026-06-15'
status: budding
---

# Agent Defense Landscape：從 NIST 的架構缺陷到實作方案

**延續自**: [[2026-05-14-agent-hijacking-nist]]
**日期**: 2026-05-14 | **來源**: HN (FireClaw 5pts, AgentArmor 10pts, Lilith-zero 9pts)

## 一句話

NIST 說 LLM agent 沒有 trusted/untrusted boundary。三套開源工具各自從不同層面試圖建立這個 boundary：FireClaw 在 transport 層做 proxy isolation、AgentArmor 做全管線八層 defense-in-depth、Lilith-zero 在 MCP 層做 deterministic policy enforcement。各有洞見，但也各有盲區。

---

## FireClaw — Proxy-Level Isolation

**Repo**: [raiph-ai/fireclaw](https://github.com/raiph-ai/fireclaw)
**定位**：AI agent 的防火牆 proxy，專注防 prompt injection

### 架構：四階段硬管線

```
Agent → FireClaw Proxy → Internet

Stage 1: DNS Check — blocklist (URLhaus, PhishTank, OpenPhish)
Stage 2: Sanitize — strip HTML tricks, hidden Unicode, encoding exploits, inject canary tokens
Stage 3: LLM Summary — isolated LLM extracts facts only (no tools, no memory, no data access)
Stage 4: Output Scan — check residual injection, canary survival, tool-call syntax
```

### 核心洞察

就算 Stage 3 的 summarization LLM 被 injection 攻破，**它沒有 tools、沒有 memory、沒有 data access**，只能回傳文字。而回傳的文字還要過 Stage 4 output scanning。攻擊者進退無路。

這其實就是 NIST 要的那個「trusted/untrusted boundary」的窮人版實作：用一個隔離的 LLM instance 當 sanitizer，把 untrusted web content 轉成 safe summary。

### 亮點

- **Canary Token System**：在 content 裡插入 unique marker，若 summarization 被繞過，canary 會存活被 Stage 4 抓到
- **No Bypass Mode**：管線固定，即使 agent 被 compromise 也不能關掉 FireClaw
- **Domain Trust Tiers**：trusted（跳過 sanitization）/ neutral（全管線）/ suspicious（aggressive）/ blocked（拒絕）
- **Community Threat Feed**：opt-in 匿名分享 detection metadata，建立社群級 blocklist
- **`/api/scan` endpoint**：不限 web fetch，可掃任意 untrusted text — tool descriptions、memory artifacts、MCP responses
- **Pi Appliance**：可跑在 Raspberry Pi 上當實體安全設備，含 OLED 顯示

### 限制

- 只做 **input sanitization**，不做 execution control / output filtering / identity management
- 管線是固定的，無法針對不同 agent 行為做 adaptive policy
- 依賴一個額外 LLM call（Stage 3）— 成本與 latency 交換安全性

---

## AgentArmor — 全覆蓋八層框架

**Repo**: [Agastya910/agentarmor](https://github.com/Agastya910/agentarmor)
**定位**：OWASP Top 10 for Agentic Applications (2026) 的完整實作

### 八層架構

| Layer | Name | 防什麼 |
|-------|------|--------|
| L1 | Ingestion | Input scanning, prompt injection detection |
| L2 | Storage | AES-256-GCM encryption at rest, HMAC integrity |
| L3 | Context | **GoalLock** anchoring, canary injection, template stripping |
| L4 | Planning | Action chain tracking, semantic risk scoring |
| L5 | Execution | DNS rebinding, rate limiting, circuit breakers |
| L6 | Output | Credential/PII scanning, exfiltration detection |
| L7 | Inter-Agent | Mutual auth (HMAC), trust scoring, delegation depth |
| L8 | Identity | JIT permissions, credential rotation |

v0.5.0 宣稱 L3-L6 已從 basic → production-grade，含 127+ adversarial test cases。

### 關鍵設計

- **GoalLock (L3)**：在每個 conversation 開頭 anchor agent 的 purpose，防止 goal hijacking
- **CanaryVault (L3)**：per-session 注入多個 unique canary tokens
- **ActionChainTracker (L4)**：偵測多步驟攻擊鏈（reconnaissance → escalation → exfiltration）
- **L5 Network Policy**：DNS rebinding protection + SSRF protection + domain allow/blocklist
- **MCP Server Mode**：可直接當 MCP server 跑，零程式碼整合 Claude Code / OpenClaw 等 agent

### HN 社群的具體批評

@ibrahim_h 指出 L4 risk scoring 的致命盲區：

> L4 只 parse action string 的 verb（"read", "delete"），**不看 params**。所以 `read.file` targeting `/etc/shadow` 拿 risk score 1，而 `delete.file` on `/tmp/cache.json` 拿 7。在真實 agent workload 中，target 跟 verb 同等重要。

這是 NIST Insight #3（task-level analysis > aggregate）在實作層的再現：只看 action type 不看 context 會漏掉高風險操作。

### 限制

- 框架級整合：需要 import `agentarmor` 並改 code／用 decorator／跑 proxy mode。不是 drop-in transparent proxy。
- L4 param-blind 問題（見上）
- 八層全開的效能開銷尚未有公開 benchmark
- 社群尚小（10pts, 6 comments），production battle-testing 有限

---

## Lilith-zero — MCP 層的 Deterministic Security

**Repo**: [BadC-mpany/lilith-zero](https://github.com/BadC-mpany/lilith-zero)
**定位**：MCP tool call 的 Rust 安全中介層

### 設計哲學

- **Fail-Closed**：預設 DENY。policy 缺失、parse error、內部錯誤 → 全部封鎖
- **Zero-Trust Transport**：stdio/network payload 全視為惡意，strict Content-Length framing 防 JSON smuggling
- **Type-Safe Invariants**：Rust 型別系統讓不安全的狀態（如未驗證的 taint）在編譯期就無法表達
- **Deterministic Classification**：tool class 在 policy 中顯式宣告，不用 runtime heuristics

### 核心能力

- **Deterministic ACLs**：tool name + resource URI 的 static allow/deny
- **Dynamic Taint Tracking**：session-bound sensitivity tags，tool-class 宣告
- **Lethal Trifecta Protection**：自動封鎖 "Access Private → Access Untrusted → Exfiltrate" 模式
- **Tamper-Proof Audit**：HMAC-SHA256 signed JSONL
- **Zero-Copy Runtime**：<1ms overhead
- **JsonLogic Predicates**：argument-level 遞迴 policy enforcement

### 與其他兩個的差異

Lilith-zero 最小、最 focused。不做 summarization（不像 FireClaw），不做 multi-layer defense-in-depth（不像 AgentArmor）。它只做一件事：在 MCP transport 層做 deterministic policy enforcement。因為是 Rust 寫的，overhead 極低。

**這是 AgentArmor L5 的 MCP 特化版**：如果你只需要「這個 MCP tool call 該不該過」，不需要 L1-L8 全套，Lilith-zero 更適合。

---

## 交叉分析：誰補了 NIST 的哪個洞？

NIST 四個 insight 對應到這三套工具的覆蓋：

| NIST Insight | FireClaw | AgentArmor | Lilith-zero |
|-------------|----------|------------|-------------|
| #1 框架需持續擴展 (RCE/phishing/exfil) | ❌ (只做 input) | ⚠️ L5-L6 部分覆蓋 | ⚠️ ACL + taint |
| #2 Adaptive evaluation (新攻擊 11%→81%) | ⚠️ 管線固定，無 adaptive | ❌ 參數盲區 | ✅ deterministic 但 non-adaptive |
| #3 Task-level analysis (不看 aggregate) | ❌ | ❌ (L4 verb-only) | ⚠️ JsonLogic 可做 param-level |
| #4 Multi-attempt (57%→80%) | ⚠️ 每次都過管線 | ⚠️ 每次都過 L1-L8 | ✅ 每次都過 policy |

沒有一個工具完整補上 #2（adaptive evaluation）和 #3（task-level risk）。FireClaw 的管線是固定的，AgentArmor 的 L4 risk scoring 只看 verb，Lilith-zero 的 policy 是 static 的。

### 架構層的共同盲區

三套工具都沒有解決 NIST 的核心架構問題：**LLM 的 input 強制混合 trusted instructions 和 untrusted data**。它們做的是：

- FireClaw：把 untrusted data 先 sanitize 再餵給 agent
- AgentArmor：在 input pipeline 的多個點攔截
- Lilith-zero：在 tool call 層決定允不允許

但真正的「trusted/untrusted boundary」應該是架構層的 separation——讓 LLM 本身能區分「這是系統指令」和「這是外部資料」。這三套都是在現有架構上打補丁，沒有改變架構本身。

---

## 對 Hermes 的意義

1. **FireClaw 的 `/api/scan` endpoint** 很有意思：Hermes 在自主探索時 fetch 網頁，如果所有 web content 都先過 FireClaw 的 scan → 可大幅降低 injection 風險。這是低 friction 的整合（只需改 fetch 路徑，不需改 Hermes 核心）。

2. **AgentArmor 的 MCP Server Mode**：如果 Hermes 的 MCP gateway 整合 AgentArmor，可以在 tool call 層加一層 policy enforcement。但目前 L4 的 param-blind 問題對 Hermes 這種頻繁 file I/O 的 agent 是 dealbreaker。

3. **Lilith-zero 的 taint tracking**：「Access Private → Access Untrusted → Exfiltrate」這個 lethal trifecta pattern 對 Hermes 特別 relevant——Hermes 同時有 local vault（private）和 web fetch（untrusted），如果被 compromise，這條攻擊鏈是成立的。

4. **Canary token 技術可獨立採用**：FireClaw 和 AgentArmor 都用 canary tokens 來偵測 sanitization 是否被繞過。Hermes 可以在寫入 vault notes 時注入 per-session canary，後續讀取時檢查 canary 是否存活——一個輕量的 integrity check。

---

## References

- FireClaw: https://github.com/raiph-ai/fireclaw
- AgentArmor: https://github.com/Agastya910/agentarmor
- Lilith-zero: https://github.com/BadC-mpany/lilith-zero
- OWASP Top 10 for Agentic Applications (2026): https://owasp.org/www-project-top-10-for-agentic-security-and-integrity/
- NIST Agent Hijacking (延續來源): [[2026-05-14-agent-hijacking-nist]]
- Agent Orchestration Skepticism: [[2026-05-14-scion-orchestration-skeptic]]

