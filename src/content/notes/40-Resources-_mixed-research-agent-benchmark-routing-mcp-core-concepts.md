---
_slug: 40-Resources-_mixed-research-agent-benchmark-routing-mcp-core-concepts
_vault_path: 40-Resources/_mixed/research/agent/benchmark-routing-mcp-core-concepts.md
tags:
- knowledge
- ai-agent
- core-concepts
- benchmark
- routing
- mcp
- security
created: '2026-06-08'
version: 1
status: seedling
sources:
- 2026-06-04-研究報告-swe-bench-2026-leaderboard-與-agent-benchmark-設計反思-saber-啟示.md
- 2026-06-05-研究報告-llm-model-routing-cascade-cost-economics-for-ai-agents-2026.md
- 2026-06-06-研究報告-mcp-ecosystem-maturity-2026-從-萬用-tool-bus-到-policy-enforced-tool-fabric.md
type: core-concepts
fingerprint: benchmark, swe-bench, saber, routing, cascade, mcp, sanitizer, policy-gateway
title: Benchmarks + Routing + MCP — 核心概念整合
updated: '2026-06-15'
---

# Benchmarks + Routing + MCP — 核心概念整合

> 三個表面獨立、主題內在高度相關的題目。
> Benchmark 量化「誰好」、Routing 量化「誰便宜」、MCP 量化「誰安全」。

---

# Part 1: Benchmarks + SWE-bench + SABER

## SWE-bench 2026 現狀

**2026 leaderboard 頭部已達 79.2%**（Claude Opus 4.5 + live-SWE-agent），看似接近「解決」。但有三個深層問題：

1. **Benchmark ceiling 是 artifact，不是 model ceiling** — SABER 論文證明
2. **Cost-vs-score 曲線無人繪** — leaderboard 只列分數
3. **「嘗試次數」遊戲** — single-attack vs multi-attack 比較是 apples-to-oranges

## SWE-bench 家族（2026 變體）

```
SWE-bench 家族
├── Verified（500 題，人工驗證可解）— 主流
├── Lite（300 題，輕量版）
├── Multilingual（9 種程式語言，2026 新增）
├── Multimodal（截圖 + 文字，2025-07 發表）
├── Bash-only（僅 shell 工具，2026 新增）— 強迫「最簡 harness」
└── Test split（500 題私有，需 sb-cli 提交）
```

### 關鍵發現：mini-SWE-agent

**原始 SWE-agent 100+ 行複雜 prompting → mini 版本 100 行 Python code**，靠 Claude Opus 4.5 high reasoning 達到 79.2%。

**這暗示**：**harness 複雜度對 SOTA 的邊際貢獻正在趨近於零**，底層 model 能力是主因。

## SABER 三大組件

SABER（**S**afeguarding Mutating **A**ctions, **B**lock-based filtering, **E**nhanced **R**eflection）**不是新 framework，而是 plug-in 層包在現有 agent loop 外**。不需要 retraining（gradient-free, model-agnostic），只需要兩個 model（main + auxiliary）：

### (A) Mutation-gated human verification

只在 candidate action 是 mutating 時要求 user 確認。Non-mutating（查詢）action 完全不被打擾。

- **mutating 只佔 14-18% 步數**，所以 user 被打擾的頻率約每 6 個 turn 一次
- 把 tool call 改寫成自然語言摘要 + 必要前置條件

### (B) Targeted reflection

在 mutating action 前注入蒸餾後的 constraints 摘要到 `<think>` block（推理模型）或 ReAct-style format。

**這解「lost-in-the-middle」問題**：long context 後 agent 開始忘記 system policy。

### (C) Block-based context cleaning

把 trajectory 切成 block，存 `(s_k, e_k)` 摘要嵌入，**只 retrieve top-N 最相關的 block**。

**這解「context poisoning」**：user 確認記錄塞爆對話歷史後，後面的判斷開始 reference 過期的 confirmation。

### 實驗結果

| Benchmark | Model | No-SABER | +SABER | Δ |
|-----------|-------|----------|--------|---|
| τ-Bench Airline | Qwen3-Thinking-235B | 49.3% | 63.3% | **+14.0 pp** |
| τ-Bench-V Air | Qwen3-Thinking-235B | 58.5% | **78.2%** | **+19.7 pp** |
| τ-Bench Airline | Claude Sonnet 4 | 62.6% | **76.5%** | **+13.9 pp** |

**Ablation（Qwen3-Thinking，τ-Bench-V Air）**：
- No-SABER: 58.0%
- +Reflection only: 66.9% (+8.9 pp)
- +Verification only: 68.0% (+10.0 pp)
- **Full SABER: 78.7% (+20.7 pp)** — 兩者**非線性疊加**

**輔助 model 配對很重要**：**auxiliary 用 instruction-tuned 守門員 + main 用 reasoning-heavy 行動者** 的不對稱分工最佳。

## Benchmark 設計的典範轉移

> 從「分數高」到「評分可靠」

- τ-Bench Verified — 當 agent 在原始 τ-Bench 上分數飽和，**先懷疑 benchmark 本身**
- SABER 團隊手動審計 165 題、修正 ground truth、擴寫 user instruction 釋出 Verified 版本
- SWE-bench Verified 500 題已經過同樣流程（OpenAI x Princeton 2024-08）
- **但其他 benchmark（GAIA、HotpotQA、ToolBench）沒人做** — 未來 12 個月可能會看到一波 Verified 版本發布

---

# Part 2: LLM Routing + Cascade Cost

## 為什麼需要 Routing

- **Token 成本爆炸**：每個 agent 流程 5-20 次 LLM call，複雜任務 50-500k tokens
- **任務異質**：同一個 agent 同時做「格式化訊息」、「RAG 摘要」、「規劃工具呼叫鏈」三種本質不同的工作
- **全部用 frontier model 是嚴重的資源浪費**

## 三種基本 Routing 策略

### (A) Static Tiered Routing（最簡單）

```python
TIER_TABLE = {
    "summarize":  "anthropic/claude-haiku-4-5",
    "extract":    "openai/gpt-4.1-mini",
    "plan":       "openai/gpt-5.2",
    "code":       "x-ai/grok-code-fast-1",
    "reflect":    "anthropic/claude-sonnet-4.5",
}
```

### (B) Cascading / Self-Cascade（最普遍）

```python
def cascade(prompt, budget):
    cheap_response, cheap_conf = call("haiku-4.5", prompt, return_logprob=True)
    if cheap_conf > 0.92 or budget.exhausted:
        return cheap_response
    return call("claude-sonnet-4.5", prompt, verify(cheap_response))
```

### (C) Learned Router（最 SOTA）

用小 router model（often distilled 1B param）把每個 prompt 對應到 1-of-N models，訓練資料來自大規模 human/AI 偏好對齊。

## OpenRouter 2026 Routing Primitives

| Variant | 機制 | 成本 | 適用 |
|---------|------|------|------|
| `:floor` | 永遠選最便宜的能完成任務的 model | 最低 | 開發/批次 |
| `:nitro` | 永遠選延遲最低的（通常 = 最便宜的）| 中 | 互動式 |
| `:free` | 免費 model，20 RPM/50-1000 RPD 限制 | $0 | 開發/低成本 agent |
| `:auto` | ML router 學出來的「每分錢最高品質」 | +5-10% 溢價 | **生產環境預設** |

## 2026 新興 Pattern：Multi-model Cost Guard

不再只是「選哪個 model」，而是「同一個 call 內多個 model 並行 + take best-of-N」或「cheap model 嘗試 N 次取 consensus」。

```python
async def best_of_n_routing(prompt, n=3, models=None):
    responses = await asyncio.gather(*[call(m, prompt) for m in models])
    return await self_verifier.rank(responses, prompt)
```

## 關鍵洞見

- **Agentic cost curve 從線性變次線性** — 20-step flow 從「20 × frontier」變「5 × frontier + 15 × mini」，**60-75% 成本下降**（Not Diamond 公開 case studies）
- **可靠性提升，不是下降** — 早期擔心 routing 會引入不一致；2026 數據顯示 routing 系統的 *aggregate* reliability 反而高於單一 frontier

## 關鍵警告

**沒有 verifier 就不要做 cascade**。「cheap model 自信錯了」是最危險的 — 它會把 hallucination 包裝成 high confidence，**比直接用 frontier 更難 debug**。

## 可複製性

✅ **可以自己做**：
- Static tiered + heuristic — 50 行 Python
- Cascade with self-verifier — 200 行 Python
- 用 OpenAI/Anthropic SDK 切換 — 不用 OpenRouter

❌ **自己做不了的**：
- ML router 的 training data（需要百萬級 human preference label）
- 400+ model 的 capability benchmarking
- 即時 model availability / pricing / latency 監控

**瓶頸是訓練資料，不是演算法**。

---

# Part 3: MCP Ecosystem + Security

## 2026 範式轉移

> **MCP 從「tool bus」變成「policy-enforced tool fabric」是 2026 年最大範式轉移**

- Tool list 不再是「我能接什麼」而是「我**應該**讓 LLM 看到什麼」
- 每個 host（Claude Desktop、Cursor、Cline、Windsurf）的預設行為是「LLM 看得到 = LLM 能 call」 — 這是根本錯誤

## 三層防禦模型

| 層級 | 攔截點 | 代表實作 | 防什麼 |
|------|--------|---------|--------|
| **L1 Tool-list filter** | client 看到 tools 之前 | `mcp-routing-gateway`, `Epydios gateway` | 危險 tool 不給 LLM 看、virtualize 替換 |
| **L2 Call-time policy** | tool 執行前 | `Epydios` (allow/deny + step-up approval) | 需要 user 在場同意的 destructive ops |
| **L3 Output sanitizer** | tool 結果回給 LLM 前 | `StackOneHQ/defender` (2-tier: regex + ONNX ML) | indirect prompt injection |
| **L0 Registry/Discovery** | 載入 MCP server 時 | `mcp-contextprotocol/registry`, `agentseal scan-mcp` | 防止裝到已知惡意 server |

## StackOne Defender 兩層架構

**最值得抄的 output sanitizer 設計**：

```typescript
import { createPromptDefense } from '@stackone/defender';

const defense = createPromptDefense({ blockHighRisk: true });
const result = await defense.defendToolResult(toolOutput, 'gmail_get_message');

if (!result.allowed) {
    // Tier 1: 規則 pattern (Unicode tag, Base64, BiDi override, zero-width)
    // Tier 2: ONNX classifier (22MB, ~10ms latency, F1 90.8%)
    throw new Error('Tool output blocked by Defender');
}
```

**為什麼這個設計重要**：
- **CPU only**、**~10ms latency**、**22MB model** — 真的能塞進 agent loop
- 兩層：規則擋 90% 已知攻擊快又便宜，ML 補 10% 變體
- `blockHighRisk: true` 是 **fail-closed 預設**（反向於大多數 LLM library 的 fail-open）

## Epydios Policy Gateway

**最完整的 policy engine 雛形**：

```
MCP Client → Policy Gateway → MCP Server(s)
                    ↓
          ┌──────────┴──────────┐
          │ 1. allow/deny list  │
          │ 2. step-up approval │  ← 2-min TTL, JSONL audit
          │ 3. capability-limited approver token │
          │ 4. append-only evidence log │
          └─────────────────────┘
```

**關鍵 primitives**：
- **Step-up approval** — 高風險 tool 必須 user 透過 CLI `aimxs-cli approve <id>` 才能執行
- **Separation of duties** — approver token 跟 executor token 是不同 capability，**自己不能 approve 自己的 call**
- **Append-only JSONL audit** — 每一次 tool call 都有 SHA-256 chain 串接

## 根本未解問題

> 「LLM 看到 tools = LLM 執行」這個根本問題沒人解

所有 L1 filter 都是「別讓 LLM 看到」，但這跟 LLM 本身能 infer 出工具存在的能力衝突。例如「刪除檔案」的 tool 被 filter 掉，但 user 問「能刪檔嗎」LLM 還是會在 description 之外找到其他寫檔路徑（shell.exec、fs.write）。

**真正的解法是 capability-based security**：tool 本身要有 **unforgeable capability token**，LLM「看到」≠「擁有 capability」。

## 限制

- **Defender F1 90.8% 在 adversarial 設定下可能掉到 70% 以下** — 任何 ML classifier 面對 adaptive attacker 都會掉
- **多層防禦的代價是延遲堆疊** — Defender 10ms + Policy gateway 5ms + Registry scan 200ms + Audit log 5ms = ~220ms per tool call
- **2026 學術圈落後實作 6-12 個月** — 找不到一篇 2026 arXiv 專門針對 MCP 攻擊面
- **Registry 是新的 supply chain 風險** — 跟 X.509 PKI 早期 CA 信任問題同構

---

# 三主題交叉洞見

## 1. Benchmark 重新定義什麼叫「好」
- 從「分數高」→「評分可靠」+「cost-vs-score Pareto」
- 從「通用 benchmark」→「domain-specific 驗證集」

## 2. Routing 解決「什麼 task 給什麼 model」
- 任務分級 → cheap model 嘗試 → high confidence 留、low confidence 升級
- **沒有 verifier 就不要做 cascade**

## 3. MCP 解決「tool 怎麼安全暴露給 LLM」
- 從「tool bus」→「policy-enforced tool fabric」
- **三層防禦（filter + policy + sanitizer）必須疊加**

## 三者交集：Production-grade Agent 系統的標配

```
[Benchmark]    →  量化「誰好」  →  internal benchmark + leaderboard 對比
[Routing]      →  量化「誰便宜」 →  cheap-first cascade + cost circuit breaker
[MCP Security] →  量化「誰安全」 →  policy gateway + output sanitizer + audit log
```

---

## 給我們自己的 Actionable

### Benchmark 方向

| 方向 | 難度 | 具體做法 |
|------|------|----------|
| **建立 firn 自己的 SWE-bench Verified 子集** | MODERATE | 從現有 research script 手動審計 20 個 ground truth → `firn_bench_v1.json` |
| **評估 cost-vs-score Pareto** | MODERATE | `eval_pareto.py` 在 Lite 50 題上跑多個模型，輸出 Pareto frontier plot |
| **SABER-style action risk classifier** | MODERATE | 在 firn agent loop 加 mutation 分類，mutating action 暫停送 user 確認 |
| **Block-based context cleaning** | MODERATE | 對話歷史改 block 結構，每 5 turns 摘要 + embedding，只 retrieve top-8 |

### Routing 方向

| 方向 | 難度 | 具體做法 |
|------|------|----------|
| **Static tiered routing** | TRIVIAL | 在 `firn/llm/router.py` 加 `TaskTier` enum + routing table |
| **Cascade wrapper** | MODERATE | `call_with_cascade()`：cheap → confidence check → 升級到 frontier |
| **Cost-based circuit breaker** | TRIVIAL | 擴充現有 `CircuitBreaker` 加 hourly spend threshold |
| **Cost CLI report** | TRIVIAL | `firn llm cost` 從 `TurnsLogger` 讀 token 用量 + 算 daily/weekly cost |

### MCP Security 方向

| 優先 | 方向 | 難度 | 具體做法 |
|------|------|------|----------|
| **P0** | L3 Output sanitizer | MODERATE | 抄 `StackOneHQ/defender` Tier 1 regex（Unicode tag、Base64、BiDi override、zero-width）— 純 Python 零 ML 依賴 |
| **P1** | L1 Tool-list filter | TRIVIAL | `mcp/registry.py` 的 `as_tool_schemas()` 加 allowlist 參數，預設 deny `fs.write`、`exec`、`send_*` |
| **P1** | Step-up approval 雛形 | MODERATE | 抄 Epydios 模式，destructive tool 預設需要 confirmation |
| **P2** | JSONL audit log | TRIVIAL | `observability/spans.py` 加 `MCP_CALL_SPAN`，記錄 (server, tool, args_hash, decision) |

---

## 參考資料

- **2026-06-04** — SWE-bench 2026 Leaderboard + SABER 三大組件 + 實驗結果
- **2026-06-05** — Routing + Cascade Cost Economics + OpenRouter primitives
- **2026-06-06** — MCP Ecosystem + StackOne Defender + Epydios + 三層防禦
- 來源：SWE-bench leaderboard、SABER (paper)、OpenRouter docs、StackOneHQ/defender、Epydios-MCP-Policy-Gateway、modelcontextprotocol/registry
