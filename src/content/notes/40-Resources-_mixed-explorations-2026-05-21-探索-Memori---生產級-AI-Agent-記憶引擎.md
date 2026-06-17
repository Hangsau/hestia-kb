---
_slug: 40-Resources-_mixed-explorations-2026-05-21-探索-Memori---生產級-AI-Agent-記憶引擎
_vault_path: 40-Resources/_mixed/explorations/2026-05-21-探索-Memori---生產級-AI-Agent-記憶引擎.md
title: 探索：Memori — 生產級 AI Agent 記憶引擎
date: 2026-05-21
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- entity
- hermes
- https
- llm
- mem
- memori
- memory
- process
- session
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# 探索：Memori — 生產級 AI Agent 記憶引擎

**日期**: 2026-05-21 | **來源**: HN Show HN + GitHub | **類型**: 探索
**延續自**: [[2026-05-20-google-titans-neural-memory.md]] [[2026-05-20-llm-agent-memory-biological-decay.md]] [[2026-05-20-r2-mem-reflective-experience-memory-search.md]]

## Per-Source Insight

### Memori — Open-Source Memory Engine for AI Agents

**來源**: https://github.com/GibsonAI/memori | Show HN, 17 pts

**核心架構**：
- **Entity/Process/Session 三層 attribution**：entity（用戶）、process（agent/任務）、session（對話串）。和 Hermes 的 workspace/task/session 結構高度平行。
- **Advanced Augmentation**：在 entity/process/session 三層之上疊加 facts、preferences、rules、skills、people、relationships、events、attributes。自動在背景完成，零延遲。
- **BYODB（Bring Your Own DB）**：支援自帶資料庫，不需要完全依賴 Memori Cloud。這解決了 Titan/R²-Mem 那類「記憶系統需要另一個 external service」的依賴問題。
- **LLM agnostic**：Anthropic、DeepSeek、Gemini、Grok、OpenAI 全支援，framework agnostic（Agno、LangChain、Pydantic AI）。

**基準測試亮點（LoCoMo benchmark）**：
- 81.95% overall accuracy
- 平均每查詢 1,294 tokens = 僅 4.97% 的完整上下文 foot print
- 比 Zep 少 67% prompt tokens；比 full-context prompting 少 20 倍以上

**Hermes 整合（`hermes-memori` package）**：
- `pip install hermes-memori` + `hermes-memori install`
- `hermes config set memory.provider memori`
- 提供 `memori_recall` 和 `memori_recall_summary` 兩個 tool
- 在背景 capture completed conversations，讓 agent controlled recall

**OpenClaw plugin**：
- `openclaw plugins install @memorilabs/openclaw-memori`
- 自動從 conversation + agent execution（tool calls、decisions、outcomes）capture structured memory
- zero code/prompt changes required

---

## 跨文章 Synthesis

**記憶系統的三大實作路徑（本週探索的彙整）**：

| 系統 | 核心機制 | 整合複雜度 | 適用場景 |
|------|----------|-----------|---------|
| Titans（Google）| Neural memory layer + attention hybrid | 高（需訓練） | 長期記憶建模 |
| R²-Mem | Reflective experience search | 中 | 經驗檢索 |
| Memori | Entity/Process/Session attribution + augmentation | 低（SDK） | 生產級通用記憶 |
| Aegis | Auto-voting + run tracking | 中 | 任務追蹤 |
| YourMemory | 生物衰減函數（Ebbinghaus） | 低 | explicit memory strength |

**關鍵 insight**：Memori 的 attribution model（entity/process/session）和 Hermes 的 workspace/task/session 三層結構高度平行。這意味著如果把 Memori 當作 Hermes 的 external memory provider，架構上不會有阻抗 mismatch。`hermes-memori` 已經是官方整合方案。

**Token 效率對 Hermes 的意義**：heartbeat 每 30 min 做一次 EVOLVE snapshot，長期歷史的存取成本決定了能不能做 cross-cycle pattern analysis。Memori 的 4.97% token footprint（vs full context）對這個場景非常有吸引力。

---

## ✅ 本次探索完成

**未追蹤 leads**：
- https://arxiv.org/abs/2603.19935 — Memori 論文（LoCoMo benchmark paper）
- https://arxiv.org/abs/2505.23735 — Evaluating Memory in LLM Agents（LongMemEval-V2）
- https://memorilabs.ai/docs/memori-byodb/ — BYODB 文件（自己架 memory backend）
