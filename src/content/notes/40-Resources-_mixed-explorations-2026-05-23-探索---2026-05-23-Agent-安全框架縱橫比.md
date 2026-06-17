---
_slug: 40-Resources-_mixed-explorations-2026-05-23-探索---2026-05-23-Agent-安全框架縱橫比
_vault_path: 40-Resources/_mixed/explorations/2026-05-23-探索---2026-05-23-Agent-安全框架縱橫比.md
title: 探索 — 2026-05-23：Agent 安全框架縱橫比
date: 2026-05-23
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- aegis
- agent
- fetch
- fireclaw
- hermes
- injection
- llm
- memory
- per
- stage
created: '2026-05-23'
updated: '2026-06-15'
status: budding
---

# 探索 — 2026-05-23：Agent 安全框架縱橫比

**延續自**: 無（autonomous_notes/ 為空）

## Per-Source Insights

### FireClaw (raiph-ai/fireclaw)

**架構**：4-stage proxy pipeline，介於 agent 與網路之間。

| Stage | 職責 |
|-------|------|
| DNS Blocklist | URLhaus/PhishTank/OpenPhish community blocklist |
| Sanitize | Regex 200+ patterns：HTML tricks, Unicode, encoding exploits, inject canaries |
| LLM Summary | 隔離 LLM 只 extract facts，無 tools 無 memory |
| Output Scan | 殘留 injection + canary survival + tool-call syntax |

**設計亮點**：
- Stage 3 的 LLM 即使被 injection 也無工具可用 → dead end，加上 Stage 4 output scan → 雙重封鎖
- `inner_alignment: allow_override: false` — 固定管線，agent compromised 也無法 bypass
- Canary token system：內容中埋 marker，detect bypass 是否發生
- Community threat feed：opt-in anonymized detection metadata，Row Level Security (INSERT-only)
- Trust tiers：trusted/neutral/suspicious/blocked per domain
- Rate limiting + cost controls

**威脅模型覆蓋**：
- ✅ embedded instructions, Unicode tricks, HTML obfuscation, encoding exploits, jailbreak attempts, tool call injection, data exfiltration, summarization bypass
- ❌ Image-based injection, PDF exploits (both planned), audio/video (out of scope), zero-day LLM vulns, social engineering

**對 Hermes 的啟發**：
- Hermes 的 `sanitize_fetch.py`（Stage 1-2 equivalent）和 `validate_note.py`（output scan equivalent）功能重疊但分散
- FireClaw 的 `proxy-prompt.md` + Stage 3 LLM 是 Hermes 欠缺的——synthetic content 不是 web fetch 但同樣需要淨化
- `patterns.json` 200+ regex patterns 值得對照 Hermes 的 injection detection coverage

---

### Aegis Memory (quantifylabs/aegis-memory)

**架構**：secure context hub，4 artifact types 一個 API call 搞定。

```
Prompts (versioned, one active per name)
Memory (secure, ranked, decayed)
Skills (Anthropic Agent Skills spec, semantic activation)
Subagents (delegation surface + tool/scope policy)
Bundle: POST /context/load → all four, HMAC-verified, token-budgeted
```

**安全功能（對比其他 memory layer）**：

| Feature | mem0 | Zep | Letta | Aegis |
|---------|------|-----|-------|-------|
| Content injection detection | — | — | — | ✅ 4-stage |
| Memory integrity | — | — | — | ✅ HMAC-SHA256 |
| Agent identity binding | — | — | — | ✅ Cryptographic API key |
| Trust hierarchy | — | — | — | ✅ 4-tier OWASP |
| Per-agent rate limiting | — | — | — | ✅ Sliding window |
| Audit trail | — | — | — | ✅ Immutable event log |
| Sensitive data protection | — | — | — | ✅ Auto-detect + reject/redact/flag |

**ACE Loop（Generation → Reflection → Curation）**：
- Generation: playbook query filtered by agent_id + task_type
- Reflection: auto-vote on memory helpfulness tied to run outcomes
- Curation: promote/flag/consolidate with audit trail

**Memory depth features**：
- Hybrid retrieval: dense (pgvector cosine) + sparse (PostgreSQL tsvector) + RRF
- Contradiction detection: typed `contradicts` edge, resolution workflow, `/metrics` endpoint
- Semantic consolidation: LLM/heuristic merge + `is_deprecated=True` + `consolidated_into` audit trail

**對 Hermes 的啟發**：
- mem0 vs Aegis 的對照揭示了 Hermes 目前的記憶體策略（mem0-style）在安全維度上落後
- 4-tier trust hierarchy（untrusted/internal/privileged/system）可對應 WS-017 DCG integration 的延伸
- ACE loop 的 auto-vote tie-to-outcome 是心跳 learning 模組可以借鑒的模式

---

## 跨文章 Synthesis

### 安全的層次差異

FireClaw 和 Aegis Memory 處理的攻擊面不同但互補：
- **FireClaw**：管輸入（web fetch → agent context window）
- **Aegis Memory**：管內部（memory injection, context integrity, multi-agent ACL）

Hermes 目前的 `sanitize_fetch.py` + `validate_note.py` 只覆蓋 FireClaw 的 Stage 1-2（input sanitization），缺乏：
1. 隔離 LLM summarization（FireClaw Stage 3 equivalent）
2. memory integrity verification（Aegis HMAC-SHA256）
3. trust hierarchy per-domain/agent（Aegis 4-tier model）
4. audit trail for context mutations

### 記憶體的兩種思路

mem0 家族（mem0/Zep/Letta）：semantic search first，security optional。
Aegis：security first，memory second。

Hermes 的 `heartbeat_v2.py` scoring + learning 目前落在「semantic search first」區間，缺少 Aegis 那層 explicit security boundary。

### 可借鑒的具體 Pattern

1. **Canary token**（FireClaw）：在 fetch 內容中埋 marker，detect injection 是否發生。Hermes 可在 `sanitize_fetch.py` output 中注入 canary，後續 validate_note.py 檢測。
2. **Inner alignment no-bypass**（FireClaw）：固定管線不可override。Hermes 的 skill/agent config 目前沒有等效設計。
3. **ACE auto-vote**（Aegis）：memory quality 與 run outcome 綁定。Hermes 的 `heartbeat_learning.py` 可考慮類似反饋機制。
4. **Hybrid retrieval**（Aegis）：dense + sparse + RRF。Hermes 的 FTS5 doc index 可參考 pgvector+tsvector 混合策略。

## ✅ 本次探索完成

## 未追蹤 Leads
- Orcbot (autonomous agent framework): https://github.com/fredabila/orcbot
- Atom (multi-agent orchestra): https://github.com/rush86999/atom
- Metamind (cognitive architecture overview): https://vinithavn.medium.com/advancing-agentic-memory-an-overview-of-modern-memory-management-architectures-in-llm-agents-8df87b0da58f
